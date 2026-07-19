# Langfuse Observability Plugin

This plugin ships bundled with NIA but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

Pick one:

```bash
# Interactive: walks you through credentials + SDK install + enable
nia tools  # → Langfuse Observability

# Manual
pip install langfuse
nia plugins enable observability/langfuse
```

## Required credentials

Set these in `~/.nia/.env` (or via `nia tools`):

```bash
NIA_LANGFUSE_PUBLIC_KEY=pk-lf-...
NIA_LANGFUSE_SECRET_KEY=sk-lf-...
NIA_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
nia plugins list                 # observability/langfuse should show "enabled"
nia chat -q "hello"              # then check Langfuse for a "NIA turn" trace
```

## Optional tuning

```bash
NIA_LANGFUSE_ENV=production       # environment tag
NIA_LANGFUSE_RELEASE=v1.0.0       # release tag
NIA_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
NIA_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
NIA_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
nia plugins disable observability/langfuse
```
