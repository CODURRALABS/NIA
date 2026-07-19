# NIA v0.7.0 (v2026.4.3)

**Release Date:** April 3, 2026

> The resilience release — pluggable memory providers, credential pool rotation, Camofox anti-detection browser, inline diff previews, gateway hardening across race conditions and approval routing, and deep security fixes across 168 PRs and 46 resolved issues.

---

## ✨ Highlights

- **Pluggable Memory Provider Interface** — Memory is now an extensible plugin system. Third-party memory backends (Honcho, vector stores, custom DBs) implement a simple provider ABC and register via the plugin system. Built-in memory is the default provider. Honcho integration restored to full parity as the reference plugin with profile-scoped host/peer resolution. ([#4623](Local Sovereign Environment/pull/4623), [#4616](Local Sovereign Environment/pull/4616), [#4355](Local Sovereign Environment/pull/4355))

- **Same-Provider Credential Pools** — Configure multiple API keys for the same provider with automatic rotation. Thread-safe `least_used` strategy distributes load across keys, and 401 failures trigger automatic rotation to the next credential. Set up via the setup wizard or `credential_pool` config. ([#4188](Local Sovereign Environment/pull/4188), [#4300](Local Sovereign Environment/pull/4300), [#4361](Local Sovereign Environment/pull/4361))

- **Camofox Anti-Detection Browser Backend** — New local browser backend using Camoufox for stealth browsing. Persistent sessions with VNC URL discovery for visual debugging, configurable SSRF bypass for local backends, auto-install via `nia tools`. ([#4008](Local Sovereign Environment/pull/4008), [#4419](Local Sovereign Environment/pull/4419), [#4292](Local Sovereign Environment/pull/4292))

- **Inline Diff Previews** — File write and patch operations now show inline diffs in the tool activity feed, giving you visual confirmation of what changed before the agent moves on. ([#4411](Local Sovereign Environment/pull/4411), [#4423](Local Sovereign Environment/pull/4423))

- **API Server Session Continuity & Tool Streaming** — The API server (Open WebUI integration) now streams tool progress events in real-time and supports `X-NIA-Session-Id` headers for persistent sessions across requests. Sessions persist to the shared SessionDB. ([#4092](Local Sovereign Environment/pull/4092), [#4478](Local Sovereign Environment/pull/4478), [#4802](Local Sovereign Environment/pull/4802))

- **ACP: Client-Provided MCP Servers** — Editor integrations (VS Code, Zed, JetBrains) can now register their own MCP servers, which NIA picks up as additional agent tools. Your editor's MCP ecosystem flows directly into the agent. ([#4705](Local Sovereign Environment/pull/4705))

- **Gateway Hardening** — Major stability pass across race conditions, photo media delivery, flood control, stuck sessions, approval routing, and compression death spirals. The gateway is substantially more reliable in production. ([#4727](Local Sovereign Environment/pull/4727), [#4750](Local Sovereign Environment/pull/4750), [#4798](Local Sovereign Environment/pull/4798), [#4557](Local Sovereign Environment/pull/4557))

- **Security: Secret Exfiltration Blocking** — Browser URLs and LLM responses are now scanned for secret patterns, blocking exfiltration attempts via URL encoding, base64, or prompt injection. Credential directory protections expanded to `.docker`, `.azure`, `.config/gh`. Execute_code sandbox output is redacted. ([#4483](Local Sovereign Environment/pull/4483), [#4360](Local Sovereign Environment/pull/4360), [#4305](Local Sovereign Environment/pull/4305), [#4327](Local Sovereign Environment/pull/4327))

---

## 🏗️ Core Agent & Architecture

### Provider & Model Support
- **Same-provider credential pools** — configure multiple API keys with automatic `least_used` rotation and 401 failover ([#4188](Local Sovereign Environment/pull/4188), [#4300](Local Sovereign Environment/pull/4300))
- **Credential pool preserved through smart routing** — pool state survives fallback provider switches and defers eager fallback on 429 ([#4361](Local Sovereign Environment/pull/4361))
- **Per-turn primary runtime restoration** — after fallback provider use, the agent automatically restores the primary provider on the next turn with transport recovery ([#4624](Local Sovereign Environment/pull/4624))
- **`developer` role for GPT-5 and Codex models** — uses OpenAI's recommended system message role for newer models ([#4498](Local Sovereign Environment/pull/4498))
- **Google model operational guidance** — Gemini and Gemma models get provider-specific prompting guidance ([#4641](Local Sovereign Environment/pull/4641))
- **Anthropic long-context tier 429 handling** — automatically reduces context to 200k when hitting tier limits ([#4747](Local Sovereign Environment/pull/4747))
- **URL-based auth for third-party Anthropic endpoints** + CI test fixes ([#4148](Local Sovereign Environment/pull/4148))
- **Bearer auth for MiniMax Anthropic endpoints** ([#4028](Local Sovereign Environment/pull/4028))
- **Fireworks context length detection** ([#4158](Local Sovereign Environment/pull/4158))
- **Standard DashScope international endpoint** for Alibaba provider ([#4133](Local Sovereign Environment/pull/4133), closes [#3912](Local Sovereign Environment/issues/3912))
- **Custom providers context_length** honored in hygiene compression ([#4085](Local Sovereign Environment/pull/4085))
- **Non-sk-ant keys** treated as regular API keys, not OAuth tokens ([#4093](Local Sovereign Environment/pull/4093))
- **Claude-sonnet-4.6** added to OpenRouter and Nous model lists ([#4157](Local Sovereign Environment/pull/4157))
- **Qwen 3.6 Plus Preview** added to model lists ([#4376](Local Sovereign Environment/pull/4376))
- **MiniMax M2.7** added to nia model picker and OpenCode ([#4208](Local Sovereign Environment/pull/4208))
- **Auto-detect models from server probe** in custom endpoint setup ([#4218](Local Sovereign Environment/pull/4218))
- **Config.yaml single source of truth** for endpoint URLs — no more env var vs config.yaml conflicts ([#4165](Local Sovereign Environment/pull/4165))
- **Setup wizard no longer overwrites** custom endpoint config ([#4180](Local Sovereign Environment/pull/4180), closes [#4172](Local Sovereign Environment/issues/4172))
- **Unified setup wizard provider selection** with `nia model` — single code path for both flows ([#4200](Local Sovereign Environment/pull/4200))
- **Root-level provider config** no longer overrides `model.provider` ([#4329](Local Sovereign Environment/pull/4329))
- **Rate-limit pairing rejection messages** to prevent spam ([#4081](Local Sovereign Environment/pull/4081))

### Agent Loop & Conversation
- **Preserve Anthropic thinking block signatures** across tool-use turns ([#4626](Local Sovereign Environment/pull/4626))
- **Classify think-only empty responses** before retrying — prevents infinite retry loops on models that produce thinking blocks without content ([#4645](Local Sovereign Environment/pull/4645))
- **Prevent compression death spiral** from API disconnects — stops the loop where compression triggers, fails, compresses again ([#4750](Local Sovereign Environment/pull/4750), closes [#2153](Local Sovereign Environment/issues/2153))
- **Persist compressed context** to gateway session after mid-run compression ([#4095](Local Sovereign Environment/pull/4095))
- **Context-exceeded error messages** now include actionable guidance ([#4155](Local Sovereign Environment/pull/4155), closes [#4061](Local Sovereign Environment/issues/4061))
- **Strip orphaned think/reasoning tags** from user-facing responses ([#4311](Local Sovereign Environment/pull/4311), closes [#4285](Local Sovereign Environment/issues/4285))
- **Harden Codex responses preflight** and stream error handling ([#4313](Local Sovereign Environment/pull/4313))
- **Deterministic call_id fallbacks** instead of random UUIDs for prompt cache consistency ([#3991](Local Sovereign Environment/pull/3991))
- **Context pressure warning spam** prevented after compression ([#4012](Local Sovereign Environment/pull/4012))
- **AsyncOpenAI created lazily** in trajectory compressor to avoid closed event loop errors ([#4013](Local Sovereign Environment/pull/4013))

### Memory & Sessions
- **Pluggable memory provider interface** — ABC-based plugin system for custom memory backends with profile isolation ([#4623](Local Sovereign Environment/pull/4623))
- **Honcho full integration parity** restored as reference memory provider plugin ([#4355](Local Sovereign Environment/pull/4355)) — @erosika
- **Honcho profile-scoped** host and peer resolution ([#4616](Local Sovereign Environment/pull/4616))
- **Memory flush state persisted** to prevent redundant re-flushes on gateway restart ([#4481](Local Sovereign Environment/pull/4481))
- **Memory provider tools** routed through sequential execution path ([#4803](Local Sovereign Environment/pull/4803))
- **Honcho config** written to instance-local path for profile isolation ([#4037](Local Sovereign Environment/pull/4037))
- **API server sessions** persist to shared SessionDB ([#4802](Local Sovereign Environment/pull/4802))
- **Token usage persisted** for non-CLI sessions ([#4627](Local Sovereign Environment/pull/4627))
- **Quote dotted terms in FTS5 queries** — fixes session search for terms containing dots ([#4549](Local Sovereign Environment/pull/4549))

---

## 📱 Messaging Platforms (Gateway)

### Gateway Core
- **Race condition fixes** — photo media loss, flood control, stuck sessions, and STT config issues resolved in one hardening pass ([#4727](Local Sovereign Environment/pull/4727))
- **Approval routing through running-agent guard** — `/approve` and `/deny` now route correctly when the agent is blocked waiting for approval instead of being swallowed as interrupts ([#4798](Local Sovereign Environment/pull/4798), [#4557](Local Sovereign Environment/pull/4557), closes [#4542](Local Sovereign Environment/issues/4542))
- **Resume agent after /approve** — tool result is no longer lost when executing blocked commands ([#4418](Local Sovereign Environment/pull/4418))
- **DM thread sessions seeded** with parent transcript to preserve context ([#4559](Local Sovereign Environment/pull/4559))
- **Skill-aware slash commands** — gateway dynamically registers installed skills as slash commands with paginated `/commands` list and Telegram 100-command cap ([#3934](Local Sovereign Environment/pull/3934), [#4005](Local Sovereign Environment/pull/4005), [#4006](Local Sovereign Environment/pull/4006), [#4010](Local Sovereign Environment/pull/4010), [#4023](Local Sovereign Environment/pull/4023))
- **Per-platform disabled skills** respected in Telegram menu and gateway dispatch ([#4799](Local Sovereign Environment/pull/4799))
- **Remove user-facing compression warnings** — cleaner message flow ([#4139](Local Sovereign Environment/pull/4139))
- **`-v/-q` flags wired to stderr logging** for gateway service ([#4474](Local Sovereign Environment/pull/4474))
- **NIA_HOME remapped** to target user in system service unit ([#4456](Local Sovereign Environment/pull/4456))
- **Honor default for invalid bool-like config values** ([#4029](Local Sovereign Environment/pull/4029))
- **setsid instead of systemd-run** for `/update` command to avoid systemd permission issues ([#4104](Local Sovereign Environment/pull/4104), closes [#4017](Local Sovereign Environment/issues/4017))
- **'Initializing agent...'** shown on first message for better UX ([#4086](Local Sovereign Environment/pull/4086))
- **Allow running gateway service as root** for LXC/container environments ([#4732](Local Sovereign Environment/pull/4732))

### Telegram
- **32-char limit on command names** with collision avoidance ([#4211](Local Sovereign Environment/pull/4211))
- **Priority order enforced** in menu — core > plugins > skills ([#4023](Local Sovereign Environment/pull/4023))
- **Capped at 50 commands** — API rejects above ~60 ([#4006](Local Sovereign Environment/pull/4006))
- **Skip empty/whitespace text** to prevent 400 errors ([#4388](Local Sovereign Environment/pull/4388))
- **E2E gateway tests** added ([#4497](Local Sovereign Environment/pull/4497)) — @pefontana

### Discord
- **Button-based approval UI** — register `/approve` and `/deny` slash commands with interactive button prompts ([#4800](Local Sovereign Environment/pull/4800))
- **Configurable reactions** — `discord.reactions` config option to disable message processing reactions ([#4199](Local Sovereign Environment/pull/4199))
- **Skip reactions and auto-threading** for unauthorized users ([#4387](Local Sovereign Environment/pull/4387))

### Slack
- **Reply in thread** — `slack.reply_in_thread` config option for threaded responses ([#4643](Local Sovereign Environment/pull/4643), closes [#2662](Local Sovereign Environment/issues/2662))

### WhatsApp
- **Enforce require_mention in group chats** ([#4730](Local Sovereign Environment/pull/4730))

### Webhook
- **Platform support fixes** — skip home channel prompt, disable tool progress for webhook adapters ([#4660](Local Sovereign Environment/pull/4660))

### Matrix
- **E2EE decryption hardening** — request missing keys, auto-trust devices, retry buffered events ([#4083](Local Sovereign Environment/pull/4083))

---

## 🖥️ CLI & User Experience

### New Slash Commands
- **`/yolo`** — toggle dangerous command approvals on/off for the session ([#3990](Local Sovereign Environment/pull/3990))
- **`/btw`** — ephemeral side questions that don't affect the main conversation context ([#4161](Local Sovereign Environment/pull/4161))
- **`/profile`** — show active profile info without leaving the chat session ([#4027](Local Sovereign Environment/pull/4027))

### Interactive CLI
- **Inline diff previews** for write and patch operations in the tool activity feed ([#4411](Local Sovereign Environment/pull/4411), [#4423](Local Sovereign Environment/pull/4423))
- **TUI pinned to bottom** on startup — no more large blank spaces between response and input ([#4412](Local Sovereign Environment/pull/4412), [#4359](Local Sovereign Environment/pull/4359), closes [#4398](Local Sovereign Environment/issues/4398), [#4421](Local Sovereign Environment/issues/4421))
- **`/history` and `/resume`** now surface recent sessions directly instead of requiring search ([#4728](Local Sovereign Environment/pull/4728))
- **Cache tokens shown** in `/insights` overview so total adds up ([#4428](Local Sovereign Environment/pull/4428))
- **`--max-turns` CLI flag** for `nia chat` to limit agent iterations ([#4314](Local Sovereign Environment/pull/4314))
- **Detect dragged file paths** instead of treating them as slash commands ([#4533](Local Sovereign Environment/pull/4533)) — @rolme
- **Allow empty strings and falsy values** in `config set` ([#4310](Local Sovereign Environment/pull/4310), closes [#4277](Local Sovereign Environment/issues/4277))
- **Voice mode in WSL** when PulseAudio bridge is configured ([#4317](Local Sovereign Environment/pull/4317))
- **Respect `NO_COLOR` env var** and `TERM=dumb` for accessibility ([#4079](Local Sovereign Environment/pull/4079), closes [#4066](Local Sovereign Environment/issues/4066)) — @SHL0MS
- **Correct shell reload instruction** for macOS/zsh users ([#4025](Local Sovereign Environment/pull/4025))
- **Zero exit code** on successful quiet mode queries ([#4613](Local Sovereign Environment/pull/4613), closes [#4601](Local Sovereign Environment/issues/4601)) — @devorun
- **on_session_end hook fires** on interrupted exits ([#4159](Local Sovereign Environment/pull/4159))
- **Profile list display** reads `model.default` key correctly ([#4160](Local Sovereign Environment/pull/4160))
- **Browser and TTS** shown in reconfigure menu ([#4041](Local Sovereign Environment/pull/4041))
- **Web backend priority** detection simplified ([#4036](Local Sovereign Environment/pull/4036))

### Setup & Configuration
- **Allowed_users preserved** during setup and quiet unconfigured provider warnings ([#4551](Local Sovereign Environment/pull/4551)) — @kshitijk4poor
- **Save API key to model config** for custom endpoints ([#4202](Local Sovereign Environment/pull/4202), closes [#4182](Local Sovereign Environment/issues/4182))
- **Claude Code credentials gated** behind explicit NIA config in wizard trigger ([#4210](Local Sovereign Environment/pull/4210))
- **Atomic writes in save_config_value** to prevent config loss on interrupt ([#4298](Local Sovereign Environment/pull/4298), [#4320](Local Sovereign Environment/pull/4320))
- **Scopes field written** to Claude Code credentials on token refresh ([#4126](Local Sovereign Environment/pull/4126))

### Update System
- **Fork detection and upstream sync** in `nia update` ([#4744](Local Sovereign Environment/pull/4744))
- **Preserve working optional extras** when one extra fails during update ([#4550](Local Sovereign Environment/pull/4550))
- **Handle conflicted git index** during nia update ([#4735](Local Sovereign Environment/pull/4735))
- **Avoid launchd restart race** on macOS ([#4736](Local Sovereign Environment/pull/4736))
- **Missing subprocess.run() timeouts** added to doctor and status commands ([#4009](Local Sovereign Environment/pull/4009))

---

## 🔧 Tool System

### Browser
- **Camofox anti-detection browser backend** — local stealth browsing with auto-install via `nia tools` ([#4008](Local Sovereign Environment/pull/4008))
- **Persistent Camofox sessions** with VNC URL discovery for visual debugging ([#4419](Local Sovereign Environment/pull/4419))
- **Skip SSRF check for local backends** (Camofox, headless Chromium) ([#4292](Local Sovereign Environment/pull/4292))
- **Configurable SSRF check** via `browser.allow_private_urls` ([#4198](Local Sovereign Environment/pull/4198)) — @nils010485
- **CAMOFOX_PORT=9377** added to Docker commands ([#4340](Local Sovereign Environment/pull/4340))

### File Operations
- **Inline diff previews** on write and patch actions ([#4411](Local Sovereign Environment/pull/4411), [#4423](Local Sovereign Environment/pull/4423))
- **Stale file detection** on write and patch — warns when file was modified externally since last read ([#4345](Local Sovereign Environment/pull/4345))
- **Staleness timestamp refreshed** after writes ([#4390](Local Sovereign Environment/pull/4390))
- **Size guard, dedup, and device blocking** on read_file ([#4315](Local Sovereign Environment/pull/4315))

### MCP
- **Stability fix pack** — reload timeout, shutdown cleanup, event loop handler, OAuth non-blocking ([#4757](Local Sovereign Environment/pull/4757), closes [#4462](Local Sovereign Environment/issues/4462), [#2537](Local Sovereign Environment/issues/2537))

### ACP (Editor Integration)
- **Client-provided MCP servers** registered as agent tools — editors pass their MCP servers to NIA ([#4705](Local Sovereign Environment/pull/4705))

### Skills System
- **Size limits for agent writes** and **fuzzy matching for skill patch** — prevents oversized skill writes and improves edit reliability ([#4414](Local Sovereign Environment/pull/4414))
- **Validate hub bundle paths** before install — blocks path traversal in skill bundles ([#3986](Local Sovereign Environment/pull/3986))
- **Unified nia-agent and nia-agent-setup** into single skill ([#4332](Local Sovereign Environment/pull/4332))
- **Skill metadata type check** in extract_skill_conditions ([#4479](Local Sovereign Environment/pull/4479))

### New/Updated Skills
- **research-paper-writing** — full end-to-end research pipeline (replaced ml-paper-writing) ([#4654](Local Sovereign Environment/pull/4654)) — @SHL0MS
- **ascii-video** — text readability techniques and external layout oracle ([#4054](Local Sovereign Environment/pull/4054)) — @SHL0MS
- **youtube-transcript** updated for youtube-transcript-api v1.x ([#4455](Local Sovereign Environment/pull/4455)) — @el-analista
- **Skills browse and search page** added to documentation site ([#4500](Local Sovereign Environment/pull/4500)) — @IAvecilla

---

## 🔒 Security & Reliability

### Security Hardening
- **Block secret exfiltration** via browser URLs and LLM responses — scans for secret patterns in URL encoding, base64, and prompt injection vectors ([#4483](Local Sovereign Environment/pull/4483))
- **Redact secrets from execute_code sandbox output** ([#4360](Local Sovereign Environment/pull/4360))
- **Protect `.docker`, `.azure`, `.config/gh` credential directories** from read/write via file tools and terminal ([#4305](Local Sovereign Environment/pull/4305), [#4327](Local Sovereign Environment/pull/4327)) — @memosr
- **GitHub OAuth token patterns** added to redaction + snapshot redact flag ([#4295](Local Sovereign Environment/pull/4295))
- **Reject private and loopback IPs** in Telegram DoH fallback ([#4129](Local Sovereign Environment/pull/4129))
- **Reject path traversal** in credential file registration ([#4316](Local Sovereign Environment/pull/4316))
- **Validate tar archive member paths** on profile import — blocks zip-slip attacks ([#4318](Local Sovereign Environment/pull/4318))
- **Exclude auth.json and .env** from profile exports ([#4475](Local Sovereign Environment/pull/4475))

### Reliability
- **Prevent compression death spiral** from API disconnects ([#4750](Local Sovereign Environment/pull/4750), closes [#2153](Local Sovereign Environment/issues/2153))
- **Handle `is_closed` as method** in OpenAI SDK — prevents false positive client closure detection ([#4416](Local Sovereign Environment/pull/4416), closes [#4377](Local Sovereign Environment/issues/4377))
- **Exclude matrix from [all] extras** — python-olm is upstream-broken, prevents install failures ([#4615](Local Sovereign Environment/pull/4615), closes [#4178](Local Sovereign Environment/issues/4178))
- **OpenCode model routing** repaired ([#4508](Local Sovereign Environment/pull/4508))
- **Docker container image** optimized ([#4034](Local Sovereign Environment/pull/4034)) — @bcross

### Windows & Cross-Platform
- **Voice mode in WSL** with PulseAudio bridge ([#4317](Local Sovereign Environment/pull/4317))
- **Homebrew packaging** preparation ([#4099](Local Sovereign Environment/pull/4099))
- **CI fork conditionals** to prevent workflow failures on forks ([#4107](Local Sovereign Environment/pull/4107))

---

## 🐛 Notable Bug Fixes

- **Gateway approval blocked agent thread** — approval now blocks the agent thread like CLI does, preventing tool result loss ([#4557](Local Sovereign Environment/pull/4557), closes [#4542](Local Sovereign Environment/issues/4542))
- **Compression death spiral** from API disconnects — detected and halted instead of looping ([#4750](Local Sovereign Environment/pull/4750), closes [#2153](Local Sovereign Environment/issues/2153))
- **Anthropic thinking blocks lost** across tool-use turns ([#4626](Local Sovereign Environment/pull/4626))
- **Profile model config ignored** with `-p` flag — model.model now promoted to model.default correctly ([#4160](Local Sovereign Environment/pull/4160), closes [#4486](Local Sovereign Environment/issues/4486))
- **CLI blank space** between response and input area ([#4412](Local Sovereign Environment/pull/4412), [#4359](Local Sovereign Environment/pull/4359), closes [#4398](Local Sovereign Environment/issues/4398))
- **Dragged file paths** treated as slash commands instead of file references ([#4533](Local Sovereign Environment/pull/4533)) — @rolme
- **Orphaned `</think>` tags** leaking into user-facing responses ([#4311](Local Sovereign Environment/pull/4311), closes [#4285](Local Sovereign Environment/issues/4285))
- **OpenAI SDK `is_closed`** is a method not property — false positive client closure ([#4416](Local Sovereign Environment/pull/4416), closes [#4377](Local Sovereign Environment/issues/4377))
- **MCP OAuth server** could block NIA startup instead of degrading gracefully ([#4757](Local Sovereign Environment/pull/4757), closes [#4462](Local Sovereign Environment/issues/4462))
- **MCP event loop closed** on shutdown with HTTP servers ([#4757](Local Sovereign Environment/pull/4757), closes [#2537](Local Sovereign Environment/issues/2537))
- **Alibaba provider** hardcoded to wrong endpoint ([#4133](Local Sovereign Environment/pull/4133), closes [#3912](Local Sovereign Environment/issues/3912))
- **Slack reply_in_thread** missing config option ([#4643](Local Sovereign Environment/pull/4643), closes [#2662](Local Sovereign Environment/issues/2662))
- **Quiet mode exit code** — successful `-q` queries no longer exit nonzero ([#4613](Local Sovereign Environment/pull/4613), closes [#4601](Local Sovereign Environment/issues/4601))
- **Mobile sidebar** shows only close button due to backdrop-filter issue in docs site ([#4207](Local Sovereign Environment/pull/4207)) — @xsmyile
- **Config restore reverted** by stale-branch squash merge — `_config_version` fixed ([#4440](Local Sovereign Environment/pull/4440))

---

## 🧪 Testing

- **Telegram gateway E2E tests** — full integration test suite for the Telegram adapter ([#4497](Local Sovereign Environment/pull/4497)) — @pefontana
- **11 real test failures fixed** plus sys.modules cascade poisoner resolved ([#4570](Local Sovereign Environment/pull/4570))
- **7 CI failures resolved** across hooks, plugins, and skill tests ([#3936](Local Sovereign Environment/pull/3936))
- **Codex 401 refresh tests** updated for CI compatibility ([#4166](Local Sovereign Environment/pull/4166))
- **Stale OPENAI_BASE_URL test** fixed ([#4217](Local Sovereign Environment/pull/4217))

---

## 📚 Documentation

- **Comprehensive documentation audit** — 9 HIGH and 20+ MEDIUM gaps fixed across 21 files ([#4087](Local Sovereign Environment/pull/4087))
- **Site navigation restructured** — features and platforms promoted to top-level ([#4116](Local Sovereign Environment/pull/4116))
- **Tool progress streaming** documented for API server and Open WebUI ([#4138](Local Sovereign Environment/pull/4138))
- **Telegram webhook mode** documentation ([#4089](Local Sovereign Environment/pull/4089))
- **Local LLM provider guides** — comprehensive setup guides with context length warnings ([#4294](Local Sovereign Environment/pull/4294))
- **WhatsApp allowlist behavior** clarified with `WHATSAPP_ALLOW_ALL_USERS` documentation ([#4293](Local Sovereign Environment/pull/4293))
- **Slack configuration options** — new config section in Slack docs ([#4644](Local Sovereign Environment/pull/4644))
- **Terminal backends section** expanded + docs build fixes ([#4016](Local Sovereign Environment/pull/4016))
- **Adding-providers guide** updated for unified setup flow ([#4201](Local Sovereign Environment/pull/4201))
- **ACP Zed config** fixed ([#4743](Local Sovereign Environment/pull/4743))
- **Community FAQ** entries for common workflows and troubleshooting ([#4797](Local Sovereign Environment/pull/4797))
- **Skills browse and search page** on docs site ([#4500](Local Sovereign Environment/pull/4500)) — @IAvecilla

---

## 👥 Contributors

### Core
- **@teknium1** — 135 commits across all subsystems

### Top Community Contributors
- **@kshitijk4poor** — 13 commits: preserve allowed_users during setup ([#4551](Local Sovereign Environment/pull/4551)), and various fixes
- **@erosika** — 12 commits: Honcho full integration parity restored as memory provider plugin ([#4355](Local Sovereign Environment/pull/4355))
- **@pefontana** — 9 commits: Telegram gateway E2E test suite ([#4497](Local Sovereign Environment/pull/4497))
- **@bcross** — 5 commits: Docker container image optimization ([#4034](Local Sovereign Environment/pull/4034))
- **@SHL0MS** — 4 commits: NO_COLOR/TERM=dumb support ([#4079](Local Sovereign Environment/pull/4079)), ascii-video skill updates ([#4054](Local Sovereign Environment/pull/4054)), research-paper-writing skill ([#4654](Local Sovereign Environment/pull/4654))

### All Contributors
@0xbyt4, @arasovic, @Bartok9, @bcross, @binhnt92, @camden-lowrance, @curtitoo, @Dakota, @Dave Tist, @Dean Kerr, @devorun, @dieutx, @Dilee, @el-analista, @erosika, @Gutslabs, @IAvecilla, @Jack, @Johannnnn506, @kshitijk4poor, @Laura Batalha, @Leegenux, @Lume, @MacroAnarchy, @maymuneth, @memosr, @NexVeridian, @Nick, @nils010485, @pefontana, @Penov, @rolme, @SHL0MS, @txchen, @xsmyile

### Issues Resolved from Community
@acsezen ([#2537](Local Sovereign Environment/issues/2537)), @arasovic ([#4285](Local Sovereign Environment/issues/4285)), @camden-lowrance ([#4462](Local Sovereign Environment/issues/4462)), @devorun ([#4601](Local Sovereign Environment/issues/4601)), @eloklam ([#4486](Local Sovereign Environment/issues/4486)), @HenkDz ([#3719](Local Sovereign Environment/issues/3719)), @hypotyposis ([#2153](Local Sovereign Environment/issues/2153)), @kazamak ([#4178](Local Sovereign Environment/issues/4178)), @lstep ([#4366](Local Sovereign Environment/issues/4366)), @Mark-Lok ([#4542](Local Sovereign Environment/issues/4542)), @NoJster ([#4421](Local Sovereign Environment/issues/4421)), @patp ([#2662](Local Sovereign Environment/issues/2662)), @pr0n ([#4601](Local Sovereign Environment/issues/4601)), @saulmc ([#4377](Local Sovereign Environment/issues/4377)), @SHL0MS ([#4060](Local Sovereign Environment/issues/4060), [#4061](Local Sovereign Environment/issues/4061), [#4066](Local Sovereign Environment/issues/4066), [#4172](Local Sovereign Environment/issues/4172), [#4277](Local Sovereign Environment/issues/4277)), @Z-Mackintosh ([#4398](Local Sovereign Environment/issues/4398))

---

**Full Changelog**: [v2026.3.30...v2026.4.3](Local Sovereign Environment/compare/v2026.3.30...v2026.4.3)
