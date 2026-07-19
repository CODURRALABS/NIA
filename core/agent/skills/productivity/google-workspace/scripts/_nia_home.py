"""Resolve NIA_HOME for standalone skill scripts.

Skill scripts may run outside the NIA process (e.g. system Python,
nix env, CI) where ``nia_constants`` is not importable.  This module
provides the same ``get_nia_home()`` and ``display_nia_home()``
contracts as ``nia_constants`` without requiring it on ``sys.path``.

When ``nia_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``nia_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``NIA_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from nia_constants import display_nia_home as display_nia_home
    from nia_constants import get_nia_home as get_nia_home
except (ModuleNotFoundError, ImportError):

    def get_nia_home() -> Path:
        """Return the NIA home directory (default: ~/.nia).

        Mirrors ``nia_constants.get_nia_home()``."""
        val = os.environ.get("NIA_HOME", "").strip()
        return Path(val) if val else Path.home() / ".nia"

    def display_nia_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``nia_constants.display_nia_home()``."""
        home = get_nia_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
