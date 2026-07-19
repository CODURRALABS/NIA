#!/bin/bash
# Docker/Podman entrypoint: bootstrap config files into the mounted volume, then run nia.
set -e

NIA_HOME="${NIA_HOME:-/opt/data}"
INSTALL_DIR="/opt/nia"

# --- Privilege dropping via gosu ---
# When started as root (the default for Docker, or fakeroot in rootless Podman),
# optionally remap the nia user/group to match host-side ownership, fix volume
# permissions, then re-exec as nia.
if [ "$(id -u)" = "0" ]; then
    if [ -n "$NIA_UID" ] && [ "$NIA_UID" != "$(id -u nia)" ]; then
        echo "Changing nia UID to $NIA_UID"
        usermod -u "$NIA_UID" nia
    fi

    if [ -n "$NIA_GID" ] && [ "$NIA_GID" != "$(id -g nia)" ]; then
        echo "Changing nia GID to $NIA_GID"
        # -o allows non-unique GID (e.g. macOS GID 20 "staff" may already exist
        # as "dialout" in the Debian-based container image)
        groupmod -o -g "$NIA_GID" nia 2>/dev/null || true
    fi

    # Fix ownership of the data volume. When NIA_UID remaps the nia user,
    # files created by previous runs (under the old UID) become inaccessible.
    # Always chown -R when UID was remapped; otherwise only if top-level is wrong.
    actual_nia_uid=$(id -u nia)
    needs_chown=false
    if [ -n "$NIA_UID" ] && [ "$NIA_UID" != "10000" ]; then
        needs_chown=true
    elif [ "$(stat -c %u "$NIA_HOME" 2>/dev/null)" != "$actual_nia_uid" ]; then
        needs_chown=true
    fi
    if [ "$needs_chown" = true ]; then
        echo "Fixing ownership of $NIA_HOME to nia ($actual_nia_uid)"
        # In rootless Podman the container's "root" is mapped to an unprivileged
        # host UID — chown will fail.  That's fine: the volume is already owned
        # by the mapped user on the host side.
        chown -R nia:nia "$NIA_HOME" 2>/dev/null || \
            echo "Warning: chown failed (rootless container?) — continuing anyway"
    fi

    # Ensure config.yaml is readable by the nia runtime user even if it was
    # edited on the host after initial ownership setup. Must run here (as root)
    # rather than after the gosu drop, otherwise a non-root caller like
    # `docker run -u $(id -u):$(id -g)` hits "Operation not permitted" (#15865).
    if [ -f "$NIA_HOME/config.yaml" ]; then
        chown nia:nia "$NIA_HOME/config.yaml" 2>/dev/null || true
        chmod 640 "$NIA_HOME/config.yaml" 2>/dev/null || true
    fi

    echo "Dropping root privileges"
    exec gosu nia "$0" "$@"
fi

# --- Running as nia from here ---
source "${INSTALL_DIR}/.venv/bin/activate"

# Create essential directory structure.  Cache and platform directories
# (cache/images, cache/audio, platforms/whatsapp, etc.) are created on
# demand by the application — don't pre-create them here so new installs
# get the consolidated layout from get_nia_dir().
# The "home/" subdirectory is a per-profile HOME for subprocesses (git,
# ssh, gh, npm …).  Without it those tools write to /root which is
# ephemeral and shared across profiles.  See issue #4426.
mkdir -p "$NIA_HOME"/{cron,sessions,logs,hooks,memories,skills,skins,plans,workspace,home}

# .env
if [ ! -f "$NIA_HOME/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$NIA_HOME/.env"
fi

# config.yaml
if [ ! -f "$NIA_HOME/config.yaml" ]; then
    cp "$INSTALL_DIR/cli-config.yaml.example" "$NIA_HOME/config.yaml"
fi

# SOUL.md
if [ ! -f "$NIA_HOME/SOUL.md" ]; then
    cp "$INSTALL_DIR/docker/SOUL.md" "$NIA_HOME/SOUL.md"
fi

# Sync bundled skills (manifest-based so user edits are preserved)
if [ -d "$INSTALL_DIR/skills" ]; then
    python3 "$INSTALL_DIR/tools/skills_sync.py"
fi

# Optionally start `nia dashboard` as a side-process.
#
# Toggled by NIA_DASHBOARD=1 (also accepts "true"/"yes", case-insensitive).
# Host/port/TUI can be overridden via:
#   NIA_DASHBOARD_HOST  (default 0.0.0.0 — exposed outside the container)
#   NIA_DASHBOARD_PORT  (default 9119, matches `nia dashboard` default)
#   NIA_DASHBOARD_TUI   (already honored by `nia dashboard` itself)
#
# The dashboard is a long-lived server.  We background it *before* the final
# `exec nia "$@"` so the user's chosen foreground command (chat, gateway,
# sleep infinity, …) remains PID-of-interest for the container runtime.  When
# the container stops the whole process tree is torn down, so no explicit
# cleanup is needed.
case "${NIA_DASHBOARD:-}" in
    1|true|TRUE|True|yes|YES|Yes)
        dash_host="${NIA_DASHBOARD_HOST:-0.0.0.0}"
        dash_port="${NIA_DASHBOARD_PORT:-9119}"
        dash_args=(--host "$dash_host" --port "$dash_port" --no-open)
        # Binding to anything other than localhost requires --insecure — the
        # dashboard refuses otherwise because it exposes API keys.  Inside a
        # container this is the expected deployment (host reaches it via
        # published port), so opt in automatically.
        if [ "$dash_host" != "127.0.0.1" ] && [ "$dash_host" != "localhost" ]; then
            dash_args+=(--insecure)
        fi
        echo "Starting nia dashboard on ${dash_host}:${dash_port} (background)"
        # Prefix dashboard output so it's distinguishable from the main
        # process in `docker logs`.  stdbuf keeps the pipe line-buffered.
        (
            stdbuf -oL -eL nia dashboard "${dash_args[@]}" 2>&1 \
                | sed -u 's/^/[dashboard] /'
        ) &
        ;;
esac

# Final exec: two supported invocation patterns.
#
#   docker run <image>                 -> exec `nia` with no args (legacy default)
#   docker run <image> chat -q "..."   -> exec `nia chat -q "..."` (legacy wrap)
#   docker run <image> sleep infinity  -> exec `sleep infinity` directly
#   docker run <image> bash            -> exec `bash` directly
#
# If the first positional arg resolves to an executable on PATH, we assume the
# caller wants to run it directly (needed by the launcher which runs long-lived
# `sleep infinity` sandbox containers — see tools/environments/docker.py).
# Otherwise we treat the args as a nia subcommand and wrap with `nia`,
# preserving the documented `docker run <image> <subcommand>` behavior.
if [ $# -gt 0 ] && command -v "$1" >/dev/null 2>&1; then
    exec "$@"
fi
exec nia "$@"
