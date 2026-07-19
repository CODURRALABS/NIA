# NIA v0.9.0 (v2026.4.13)

**Release Date:** April 13, 2026
**Since v0.8.0:** 487 commits · 269 merged PRs · 167 resolved issues · 493 files changed · 63,281 insertions · 24 contributors

> The everywhere release — NIA goes mobile with Termux/Android, adds iMessage and WeChat, ships Fast Mode for OpenAI and Anthropic, introduces background process monitoring, launches a local web dashboard for managing your agent, and delivers the deepest security hardening pass yet across 16 supported platforms.

---

## ✨ Highlights

- **Local Web Dashboard** — A new browser-based dashboard for managing your NIA locally. Configure settings, monitor sessions, browse skills, and manage your gateway — all from a clean web interface without touching config files or the terminal. The easiest way to get started with NIA.

- **Fast Mode (`/fast`)** — Priority processing for OpenAI and Anthropic models. Toggle `/fast` to route through priority queues for significantly lower latency on supported models (GPT-5.4, Codex, Claude). Expands across all OpenAI Priority Processing models and Anthropic's fast tier. ([#6875](Local Sovereign Environment/pull/6875), [#6960](Local Sovereign Environment/pull/6960), [#7037](Local Sovereign Environment/pull/7037))

- **iMessage via BlueBubbles** — Full iMessage integration through BlueBubbles, bringing NIA to Apple's messaging ecosystem. Auto-webhook registration, setup wizard integration, and crash resilience. ([#6437](Local Sovereign Environment/pull/6437), [#6460](Local Sovereign Environment/pull/6460), [#6494](Local Sovereign Environment/pull/6494))

- **WeChat (Weixin) & WeCom Callback Mode** — Native WeChat support via iLink Bot API and a new WeCom callback-mode adapter for self-built enterprise apps. Streaming cursor, media uploads, markdown link handling, and atomic state persistence. NIA now covers the Chinese messaging ecosystem end-to-end. ([#7166](Local Sovereign Environment/pull/7166), [#7943](Local Sovereign Environment/pull/7943))

- **Termux / Android Support** — Run NIA natively on Android via Termux. Adapted install paths, TUI optimizations for mobile screens, voice backend support, and the `/image` command work on-device. ([#6834](Local Sovereign Environment/pull/6834))

- **Background Process Monitoring (`watch_patterns`)** — Set patterns to watch for in background process output and get notified in real-time when they match. Monitor for errors, wait for specific events ("listening on port"), or watch build logs — all without polling. ([#7635](Local Sovereign Environment/pull/7635))

- **Native xAI & Xiaomi MiMo Providers** — First-class provider support for xAI (Grok) and Xiaomi MiMo, with direct API access, model catalogs, and setup wizard integration. Plus Qwen OAuth with portal request support. ([#7372](Local Sovereign Environment/pull/7372), [#7855](Local Sovereign Environment/pull/7855))

- **Pluggable Context Engine** — Context management is now a pluggable slot via `nia plugins`. Swap in custom context engines that control what the agent sees each turn — filtering, summarization, or domain-specific context injection. ([#7464](Local Sovereign Environment/pull/7464))

- **Unified Proxy Support** — SOCKS proxy, `DISCORD_PROXY`, and system proxy auto-detection across all gateway platforms. NIA behind corporate firewalls just works. ([#6814](Local Sovereign Environment/pull/6814))

- **Comprehensive Security Hardening** — Path traversal protection in checkpoint manager, shell injection neutralization in sandbox writes, SSRF redirect guards in Slack image uploads, Twilio webhook signature validation (SMS RCE fix), API server auth enforcement, git argument injection prevention, and approval button authorization. ([#7933](Local Sovereign Environment/pull/7933), [#7944](Local Sovereign Environment/pull/7944), [#7940](Local Sovereign Environment/pull/7940), [#7151](Local Sovereign Environment/pull/7151), [#7156](Local Sovereign Environment/pull/7156))

- **`nia backup` & `nia import`** — Full backup and restore of your NIA configuration, sessions, skills, and memory. Migrate between machines or create snapshots before major changes. ([#7997](Local Sovereign Environment/pull/7997))

- **16 Supported Platforms** — With BlueBubbles (iMessage) and WeChat joining Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, SMS, DingTalk, Feishu, WeCom, Mattermost, Home Assistant, and Webhooks, NIA now runs on 16 messaging platforms out of the box.

- **`/debug` & `nia debug share`** — New debugging toolkit: `/debug` slash command across all platforms for quick diagnostics, plus `nia debug share` to upload a full debug report to a pastebin for easy sharing when troubleshooting. ([#8681](Local Sovereign Environment/pull/8681))

---

## 🏗️ Core Agent & Architecture

### Provider & Model Support
- **Native xAI (Grok) provider** with direct API access and model catalog ([#7372](Local Sovereign Environment/pull/7372))
- **Xiaomi MiMo as first-class provider** — setup wizard, model catalog, empty response recovery ([#7855](Local Sovereign Environment/pull/7855))
- **Qwen OAuth provider** with portal request support ([#6282](Local Sovereign Environment/pull/6282))
- **Fast Mode** — `/fast` toggle for OpenAI Priority Processing + Anthropic fast tier ([#6875](Local Sovereign Environment/pull/6875), [#6960](Local Sovereign Environment/pull/6960), [#7037](Local Sovereign Environment/pull/7037))
- **Structured API error classification** for smart failover decisions ([#6514](Local Sovereign Environment/pull/6514))
- **Rate limit header capture** shown in `/usage` ([#6541](Local Sovereign Environment/pull/6541))
- **API server model name** derived from profile name ([#6857](Local Sovereign Environment/pull/6857))
- **Custom providers** now included in `/model` listings and resolution ([#7088](Local Sovereign Environment/pull/7088))
- **Fallback provider activation** on repeated empty responses with user-visible status ([#7505](Local Sovereign Environment/pull/7505))
- **OpenRouter variant tags** (`:free`, `:extended`, `:fast`) preserved during model switch ([#6383](Local Sovereign Environment/pull/6383))
- **Credential exhaustion TTL** reduced from 24 hours to 1 hour ([#6504](Local Sovereign Environment/pull/6504))
- **OAuth credential lifecycle** hardening — stale pool keys, auth.json sync, Codex CLI race fixes ([#6874](Local Sovereign Environment/pull/6874))
- Empty response recovery for reasoning models (MiMo, Qwen, GLM) ([#8609](Local Sovereign Environment/pull/8609))
- MiniMax context lengths, thinking guard, endpoint corrections ([#6082](Local Sovereign Environment/pull/6082), [#7126](Local Sovereign Environment/pull/7126))
- Z.AI endpoint auto-detect via probe and cache ([#5763](Local Sovereign Environment/pull/5763))

### Agent Loop & Conversation
- **Pluggable context engine slot** via `nia plugins` ([#7464](Local Sovereign Environment/pull/7464))
- **Background process monitoring** — `watch_patterns` for real-time output alerts ([#7635](Local Sovereign Environment/pull/7635))
- **Improved context compression** — higher limits, tool tracking, degradation warnings, token-budget tail protection ([#6395](Local Sovereign Environment/pull/6395), [#6453](Local Sovereign Environment/pull/6453))
- **`/compress <focus>`** — guided compression with a focus topic ([#8017](Local Sovereign Environment/pull/8017))
- **Tiered context pressure warnings** with gateway dedup ([#6411](Local Sovereign Environment/pull/6411))
- **Staged inactivity warning** before timeout escalation ([#6387](Local Sovereign Environment/pull/6387))
- **Prevent agent from stopping mid-task** — compression floor, budget overhaul, activity tracking ([#7983](Local Sovereign Environment/pull/7983))
- **Propagate child activity to parent** during `delegate_task` ([#7295](Local Sovereign Environment/pull/7295))
- **Truncated streaming tool call detection** before execution ([#6847](Local Sovereign Environment/pull/6847))
- Empty response retry (3 attempts with nudge) ([#6488](Local Sovereign Environment/pull/6488))
- Adaptive streaming backoff + cursor strip to prevent message truncation ([#7683](Local Sovereign Environment/pull/7683))
- Compression uses live session model instead of stale persisted config ([#8258](Local Sovereign Environment/pull/8258))
- Strip `<thought>` tags from Gemma 4 responses ([#8562](Local Sovereign Environment/pull/8562))
- Prevent `<think>` in prose from suppressing response output ([#6968](Local Sovereign Environment/pull/6968))
- Turn-exit diagnostic logging to agent loop ([#6549](Local Sovereign Environment/pull/6549))
- Scope tool interrupt signal per-thread to prevent cross-session leaks ([#7930](Local Sovereign Environment/pull/7930))

### Memory & Sessions
- **Hindsight memory plugin** — feature parity, setup wizard, config improvements — @nicoloboschi ([#6428](Local Sovereign Environment/pull/6428))
- **Honcho** — opt-in `initOnSessionStart` for tools mode — @Kathie-yu ([#6995](Local Sovereign Environment/pull/6995))
- Orphan children instead of cascade-deleting in prune/delete ([#6513](Local Sovereign Environment/pull/6513))
- Doctor command only checks the active memory provider ([#6285](Local Sovereign Environment/pull/6285))

---

## 📱 Messaging Platforms (Gateway)

### New Platforms
- **BlueBubbles (iMessage)** — full adapter with auto-webhook registration, setup wizard, and crash resilience ([#6437](Local Sovereign Environment/pull/6437), [#6460](Local Sovereign Environment/pull/6460), [#6494](Local Sovereign Environment/pull/6494), [#7107](Local Sovereign Environment/pull/7107))
- **Weixin (WeChat)** — native support via iLink Bot API with streaming, media uploads, markdown links ([#7166](Local Sovereign Environment/pull/7166), [#8665](Local Sovereign Environment/pull/8665))
- **WeCom Callback Mode** — self-built enterprise app adapter with atomic state persistence ([#7943](Local Sovereign Environment/pull/7943), [#7928](Local Sovereign Environment/pull/7928))

### Discord
- **Allowed channels whitelist** config — @jarvis-phw ([#7044](Local Sovereign Environment/pull/7044))
- **Forum channel topic inheritance** in thread sessions — @nia-agent-dhabibi ([#6377](Local Sovereign Environment/pull/6377))
- **DISCORD_REPLY_TO_MODE** setting ([#6333](Local Sovereign Environment/pull/6333))
- Accept `.log` attachments, raise document size limit — @kira-ariaki ([#6467](Local Sovereign Environment/pull/6467))
- Decouple readiness from slash sync ([#8016](Local Sovereign Environment/pull/8016))

### Slack
- **Consolidated Slack improvements** — 7 community PRs salvaged into one ([#6809](Local Sovereign Environment/pull/6809))
- Handle assistant thread lifecycle events ([#6433](Local Sovereign Environment/pull/6433))

### Matrix
- **Migrated from matrix-nio to mautrix-python** ([#7518](Local Sovereign Environment/pull/7518))
- SQLite crypto store replacing pickle (fixes E2EE decryption) — @alt-glitch ([#7981](Local Sovereign Environment/pull/7981))
- Cross-signing recovery key verification for E2EE migration ([#8282](Local Sovereign Environment/pull/8282))
- DM mention threads + group chat events for Feishu ([#7423](Local Sovereign Environment/pull/7423))

### Gateway Core
- **Unified proxy support** — SOCKS, DISCORD_PROXY, multi-platform with macOS auto-detection ([#6814](Local Sovereign Environment/pull/6814))
- **Inbound text batching** for Discord, Matrix, WeCom + adaptive delay ([#6979](Local Sovereign Environment/pull/6979))
- **Surface natural mid-turn assistant messages** in chat platforms ([#7978](Local Sovereign Environment/pull/7978))
- **WSL-aware gateway** with smart systemd detection ([#7510](Local Sovereign Environment/pull/7510))
- **All missing platforms added to setup wizard** ([#7949](Local Sovereign Environment/pull/7949))
- **Per-platform `tool_progress` overrides** ([#6348](Local Sovereign Environment/pull/6348))
- **Configurable 'still working' notification interval** ([#8572](Local Sovereign Environment/pull/8572))
- `/model` switch persists across messages ([#7081](Local Sovereign Environment/pull/7081))
- `/usage` shows rate limits, cost, and token details between turns ([#7038](Local Sovereign Environment/pull/7038))
- Drain in-flight work before restart ([#7503](Local Sovereign Environment/pull/7503))
- Don't evict cached agent on failed runs — prevents MCP restart loop ([#7539](Local Sovereign Environment/pull/7539))
- Replace `os.environ` session state with `contextvars` ([#7454](Local Sovereign Environment/pull/7454))
- Derive channel directory platforms from enum instead of hardcoded list ([#7450](Local Sovereign Environment/pull/7450))
- Validate image downloads before caching (cross-platform) ([#7125](Local Sovereign Environment/pull/7125))
- Cross-platform webhook delivery for all platforms ([#7095](Local Sovereign Environment/pull/7095))
- Cron Discord thread_id delivery support ([#7106](Local Sovereign Environment/pull/7106))
- Feishu QR-based bot onboarding ([#8570](Local Sovereign Environment/pull/8570))
- Gateway status scoped to active profile ([#7951](Local Sovereign Environment/pull/7951))
- Prevent background process notifications from triggering false pairing requests ([#6434](Local Sovereign Environment/pull/6434))

---

## 🖥️ CLI & User Experience

### Interactive CLI
- **Termux / Android support** — adapted install paths, TUI, voice, `/image` ([#6834](Local Sovereign Environment/pull/6834))
- **Native `/model` picker modal** for provider → model selection ([#8003](Local Sovereign Environment/pull/8003))
- **Live per-tool elapsed timer** restored in TUI spinner ([#7359](Local Sovereign Environment/pull/7359))
- **Stacked tool progress scrollback** in TUI ([#8201](Local Sovereign Environment/pull/8201))
- **Random tips on new session start** (CLI + gateway, 279 tips) ([#8225](Local Sovereign Environment/pull/8225), [#8237](Local Sovereign Environment/pull/8237))
- **`nia dump`** — copy-pasteable setup summary for debugging ([#6550](Local Sovereign Environment/pull/6550))
- **`nia backup` / `nia import`** — full config backup and restore ([#7997](Local Sovereign Environment/pull/7997))
- **WSL environment hint** in system prompt ([#8285](Local Sovereign Environment/pull/8285))
- **Profile creation UX** — seed SOUL.md + credential warning ([#8553](Local Sovereign Environment/pull/8553))
- Shell-aware sudo detection, empty password support ([#6517](Local Sovereign Environment/pull/6517))
- Flush stdin after curses/terminal menus to prevent escape sequence leakage ([#7167](Local Sovereign Environment/pull/7167))
- Handle broken stdin in prompt_toolkit startup ([#8560](Local Sovereign Environment/pull/8560))

### Setup & Configuration
- **Per-platform display verbosity** configuration ([#8006](Local Sovereign Environment/pull/8006))
- **Component-separated logging** with session context and filtering ([#7991](Local Sovereign Environment/pull/7991))
- **`network.force_ipv4`** config to fix IPv6 timeout issues ([#8196](Local Sovereign Environment/pull/8196))
- **Standardize message whitespace and JSON formatting** ([#7988](Local Sovereign Environment/pull/7988))
- **Rebrand OpenClaw → NIA** during migration ([#8210](Local Sovereign Environment/pull/8210))
- Config.yaml takes priority over env vars for auxiliary settings ([#7889](Local Sovereign Environment/pull/7889))
- Harden setup provider flows + live OpenRouter catalog refresh ([#7078](Local Sovereign Environment/pull/7078))
- Normalize reasoning effort ordering across all surfaces ([#6804](Local Sovereign Environment/pull/6804))
- Remove dead `LLM_MODEL` env var + migration to clear stale entries ([#6543](Local Sovereign Environment/pull/6543))
- Remove `/prompt` slash command — prefix expansion footgun ([#6752](Local Sovereign Environment/pull/6752))
- `NIA_HOME_MODE` env var to override permissions — @ygd58 ([#6993](Local Sovereign Environment/pull/6993))
- Fall back to default model when model config is empty ([#8303](Local Sovereign Environment/pull/8303))
- Warn when compression model context is too small ([#7894](Local Sovereign Environment/pull/7894))

---

## 🔧 Tool System

### Environments & Execution
- **Unified spawn-per-call execution layer** for environments ([#6343](Local Sovereign Environment/pull/6343))
- **Unified file sync** with mtime tracking, deletion, and transactional state ([#7087](Local Sovereign Environment/pull/7087))
- **Persistent sandbox envs** survive between turns ([#6412](Local Sovereign Environment/pull/6412))
- **Bulk file sync** via tar pipe for SSH/Modal backends — @alt-glitch ([#8014](Local Sovereign Environment/pull/8014))
- **Daytona** — bulk upload, config bridge, silent disk cap ([#7538](Local Sovereign Environment/pull/7538))
- Foreground timeout cap to prevent session deadlocks ([#7082](Local Sovereign Environment/pull/7082))
- Guard invalid command values ([#6417](Local Sovereign Environment/pull/6417))

### MCP
- **`nia mcp add --env` and `--preset`** support ([#7970](Local Sovereign Environment/pull/7970))
- Combine `content` and `structuredContent` when both present ([#7118](Local Sovereign Environment/pull/7118))
- MCP tool name deconfliction fixes ([#7654](Local Sovereign Environment/pull/7654))

### Browser
- Browser hardening — dead code removal, caching, scroll perf, security, thread safety ([#7354](Local Sovereign Environment/pull/7354))
- `/browser connect` auto-launch uses dedicated Chrome profile dir ([#6821](Local Sovereign Environment/pull/6821))
- Reap orphaned browser sessions on startup ([#7931](Local Sovereign Environment/pull/7931))

### Voice & Vision
- **Voxtral TTS provider** (Mistral AI) ([#7653](Local Sovereign Environment/pull/7653))
- **TTS speed support** for Edge TTS, OpenAI TTS, MiniMax ([#8666](Local Sovereign Environment/pull/8666))
- **Vision auto-resize** for oversized images, raise limit to 20 MB, retry-on-failure ([#7883](Local Sovereign Environment/pull/7883), [#7902](Local Sovereign Environment/pull/7902))
- STT provider-model mismatch fix (whisper-1 vs faster-whisper) ([#7113](Local Sovereign Environment/pull/7113))

### Other Tools
- **`nia dump`** command for setup summary ([#6550](Local Sovereign Environment/pull/6550))
- TODO store enforces ID uniqueness during replace operations ([#7986](Local Sovereign Environment/pull/7986))
- List all available toolsets in `delegate_task` schema description ([#8231](Local Sovereign Environment/pull/8231))
- API server: tool progress as custom SSE event to prevent model corruption ([#7500](Local Sovereign Environment/pull/7500))
- API server: share one Docker container across all conversations ([#7127](Local Sovereign Environment/pull/7127))

---

## 🧩 Skills Ecosystem

- **Centralized skills index + tree cache** — eliminates rate-limit failures on install ([#8575](Local Sovereign Environment/pull/8575))
- **More aggressive skill loading instructions** in system prompt (v3) ([#8209](Local Sovereign Environment/pull/8209), [#8286](Local Sovereign Environment/pull/8286))
- **Google Workspace skill** migrated to GWS CLI backend ([#6788](Local Sovereign Environment/pull/6788))
- **Creative divergence strategies** skill — @SHL0MS ([#6882](Local Sovereign Environment/pull/6882))
- **Creative ideation** — constraint-driven project generation — @SHL0MS ([#7555](Local Sovereign Environment/pull/7555))
- Parallelize skills browse/search to prevent hanging ([#7301](Local Sovereign Environment/pull/7301))
- Read name from SKILL.md frontmatter in skills_sync ([#7623](Local Sovereign Environment/pull/7623))

---

## 🔒 Security & Reliability

### Security Hardening
- **Twilio webhook signature validation** — SMS RCE fix ([#7933](Local Sovereign Environment/pull/7933))
- **Shell injection neutralization** in `_write_to_sandbox` via path quoting ([#7940](Local Sovereign Environment/pull/7940))
- **Git argument injection** and path traversal prevention in checkpoint manager ([#7944](Local Sovereign Environment/pull/7944))
- **SSRF redirect bypass** in Slack image uploads + base.py cache helpers ([#7151](Local Sovereign Environment/pull/7151))
- **Path traversal, credential gate, DANGEROUS_PATTERNS gaps** ([#7156](Local Sovereign Environment/pull/7156))
- **API bind guard** — enforce `API_SERVER_KEY` for non-loopback binding ([#7455](Local Sovereign Environment/pull/7455))
- **Approval button authorization** — require auth for session continuation — @Cafexss ([#6930](Local Sovereign Environment/pull/6930))
- Path boundary enforcement in skill manager operations ([#7156](Local Sovereign Environment/pull/7156))
- DingTalk/API webhook URL origin validation, header injection rejection ([#7455](Local Sovereign Environment/pull/7455))

### Reliability
- **Contextual error diagnostics** for invalid API responses ([#8565](Local Sovereign Environment/pull/8565))
- **Prevent 400 format errors** from triggering compression loop on Codex ([#6751](Local Sovereign Environment/pull/6751))
- **Don't halve context_length** on output-cap-too-large errors — @KUSH42 ([#6664](Local Sovereign Environment/pull/6664))
- **Recover primary client** on OpenAI transport errors ([#7108](Local Sovereign Environment/pull/7108))
- **Credential pool rotation** on billing-classified 400s ([#7112](Local Sovereign Environment/pull/7112))
- **Auto-increase stream read timeout** for local LLM providers ([#6967](Local Sovereign Environment/pull/6967))
- **Fall back to default certs** when CA bundle path doesn't exist ([#7352](Local Sovereign Environment/pull/7352))
- **Disambiguate usage-limit patterns** in error classifier — @sprmn24 ([#6836](Local Sovereign Environment/pull/6836))
- Harden cron script timeout and provider recovery ([#7079](Local Sovereign Environment/pull/7079))
- Gateway interrupt detection resilient to monitor task failures ([#8208](Local Sovereign Environment/pull/8208))
- Prevent unwanted session auto-reset after graceful gateway restarts ([#8299](Local Sovereign Environment/pull/8299))
- Prevent duplicate update prompt spam in gateway watcher ([#8343](Local Sovereign Environment/pull/8343))
- Deduplicate reasoning items in Responses API input ([#7946](Local Sovereign Environment/pull/7946))

### Infrastructure
- **Multi-arch Docker image** — amd64 + arm64 ([#6124](Local Sovereign Environment/pull/6124))
- **Docker runs as non-root user** with virtualenv — @benbarclay contributing ([#8226](Local Sovereign Environment/pull/8226))
- **Use `uv`** for Docker dependency resolution to fix resolution-too-deep ([#6965](Local Sovereign Environment/pull/6965))
- **Container-aware Nix CLI** — auto-route into managed container — @alt-glitch ([#7543](Local Sovereign Environment/pull/7543))
- **Nix shared-state permission model** for interactive CLI users — @alt-glitch ([#6796](Local Sovereign Environment/pull/6796))
- **Per-profile subprocess HOME isolation** ([#7357](Local Sovereign Environment/pull/7357))
- Profile paths fixed in Docker — profiles go to mounted volume ([#7170](Local Sovereign Environment/pull/7170))
- Docker container gateway pathway hardened ([#8614](Local Sovereign Environment/pull/8614))
- Enable unbuffered stdout for live Docker logs ([#6749](Local Sovereign Environment/pull/6749))
- Install procps in Docker image — @HiddenPuppy ([#7032](Local Sovereign Environment/pull/7032))
- Shallow git clone for faster installation — @sosyz ([#8396](Local Sovereign Environment/pull/8396))
- `nia update` always reset on stash conflict ([#7010](Local Sovereign Environment/pull/7010))
- Write update exit code before gateway restart (cgroup kill race) ([#8288](Local Sovereign Environment/pull/8288))
- Nix: `setupSecrets` optional, tirith runtime dep — @devorun, @ethernet8023 ([#6261](Local Sovereign Environment/pull/6261), [#6721](Local Sovereign Environment/pull/6721))
- launchd stop uses `bootout` so `KeepAlive` doesn't respawn ([#7119](Local Sovereign Environment/pull/7119))

---

## 🐛 Notable Bug Fixes

- Fix: `/model` switch not persisting across gateway messages ([#7081](Local Sovereign Environment/pull/7081))
- Fix: session-scoped gateway model overrides ignored — @Hygaard ([#7662](Local Sovereign Environment/pull/7662))
- Fix: compaction model context length ignoring config — 3 related issues ([#8258](Local Sovereign Environment/pull/8258), [#8107](Local Sovereign Environment/pull/8107))
- Fix: OpenCode.ai context window resolved to 128K instead of 1M ([#6472](Local Sovereign Environment/pull/6472))
- Fix: Codex fallback auth-store lookup — @cherifya ([#6462](Local Sovereign Environment/pull/6462))
- Fix: duplicate completion notifications when process killed ([#7124](Local Sovereign Environment/pull/7124))
- Fix: agent daemon thread prevents orphan CLI processes on tab close ([#8557](Local Sovereign Environment/pull/8557))
- Fix: stale image attachment on text paste and voice input ([#7077](Local Sovereign Environment/pull/7077))
- Fix: DM thread session seeding causing cross-thread contamination ([#7084](Local Sovereign Environment/pull/7084))
- Fix: OpenClaw migration shows dry-run preview before executing ([#6769](Local Sovereign Environment/pull/6769))
- Fix: auth errors misclassified as retryable — @kuishou68 ([#7027](Local Sovereign Environment/pull/7027))
- Fix: Copilot-Integration-Id header missing ([#7083](Local Sovereign Environment/pull/7083))
- Fix: ACP session capabilities — @luyao618 ([#6985](Local Sovereign Environment/pull/6985))
- Fix: ACP PromptResponse usage from top-level fields ([#7086](Local Sovereign Environment/pull/7086))
- Fix: several failing/flaky tests on main — @dsocolobsky ([#6777](Local Sovereign Environment/pull/6777))
- Fix: backup marker filenames — @sprmn24 ([#8600](Local Sovereign Environment/pull/8600))
- Fix: `NoneType` in fast_mode check — @0xbyt4 ([#7350](Local Sovereign Environment/pull/7350))
- Fix: missing imports in uninstall.py — @JiayuuWang ([#7034](Local Sovereign Environment/pull/7034))

---

## 📚 Documentation

- Platform adapter developer guide + WeCom Callback docs ([#7969](Local Sovereign Environment/pull/7969))
- Cron troubleshooting guide ([#7122](Local Sovereign Environment/pull/7122))
- Streaming timeout auto-detection for local LLMs ([#6990](Local Sovereign Environment/pull/6990))
- Tool-use enforcement documentation expanded ([#7984](Local Sovereign Environment/pull/7984))
- BlueBubbles pairing instructions ([#6548](Local Sovereign Environment/pull/6548))
- Telegram proxy support section ([#6348](Local Sovereign Environment/pull/6348))
- `nia dump` and `nia logs` CLI reference ([#6552](Local Sovereign Environment/pull/6552))
- `tool_progress_overrides` configuration reference ([#6364](Local Sovereign Environment/pull/6364))
- Compression model context length warning docs ([#7879](Local Sovereign Environment/pull/7879))

---

## 👥 Contributors

**269 merged PRs** from **24 contributors** across **487 commits**.

### Community Contributors
- **@alt-glitch** (6 PRs) — Nix container-aware CLI, shared-state permissions, Matrix SQLite crypto store, bulk SSH/Modal file sync, Matrix mautrix compat
- **@SHL0MS** (2 PRs) — Creative divergence strategies skill, creative ideation skill
- **@sprmn24** (2 PRs) — Error classifier disambiguation, backup marker fix
- **@nicoloboschi** — Hindsight memory plugin feature parity
- **@Hygaard** — Session-scoped gateway model override fix
- **@jarvis-phw** — Discord allowed_channels whitelist
- **@Kathie-yu** — Honcho initOnSessionStart for tools mode
- **@nia-agent-dhabibi** — Discord forum channel topic inheritance
- **@kira-ariaki** — Discord .log attachments and size limit
- **@cherifya** — Codex fallback auth-store lookup
- **@Cafexss** — Security: auth for session continuation
- **@KUSH42** — Compaction context_length fix
- **@kuishou68** — Auth error retryable classification fix
- **@luyao618** — ACP session capabilities
- **@ygd58** — NIA_HOME_MODE env var override
- **@0xbyt4** — Fast mode NoneType fix
- **@JiayuuWang** — CLI uninstall import fix
- **@HiddenPuppy** — Docker procps installation
- **@dsocolobsky** — Test suite fixes
- **@bobashopcashier** (1 PR) — Graceful gateway drain before restart (salvaged into #7503 from #7290)
- **@benbarclay** — Docker image tag simplification
- **@sosyz** — Shallow git clone for faster install
- **@devorun** — Nix setupSecrets optional
- **@ethernet8023** — Nix tirith runtime dep

---

**Full Changelog**: [v2026.4.8...v2026.4.13](Local Sovereign Environment/compare/v2026.4.8...v2026.4.13)
