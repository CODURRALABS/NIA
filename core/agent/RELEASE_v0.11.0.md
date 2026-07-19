# NIA v0.11.0 (v2026.4.23)

**Release Date:** April 23, 2026
**Since v0.9.0:** 1,556 commits · 761 merged PRs · 1,314 files changed · 224,174 insertions · 29 community contributors (290 including co-authors)

> The Interface release — a full React/Ink rewrite of the interactive CLI, a pluggable transport architecture underneath every provider, native AWS Bedrock support, five new inference paths, a 17th messaging platform (QQBot), a dramatically expanded plugin surface, and GPT-5.5 via Codex OAuth.

This release also folds in all the highlights deferred from v0.10.0 (which shipped only the Nous Tool Gateway) — so it covers roughly two weeks of work across the whole stack.

---

## ✨ Highlights

- **New Ink-based TUI** — `nia --tui` is now a full React/Ink rewrite of the interactive CLI, with a Python JSON-RPC backend (`tui_gateway`). Sticky composer, live streaming with OSC-52 clipboard support, stable picker keys, status bar with per-turn stopwatch and git branch, `/clear` confirm, light-theme preset, and a subagent spawn observability overlay. ~310 commits to `ui-tui/` + `tui_gateway/`. (@OutThisLife + Teknium)

- **Transport ABC + Native AWS Bedrock** — Format conversion and HTTP transport were extracted from `run_agent.py` into a pluggable `agent/transports/` layer. `AnthropicTransport`, `ChatCompletionsTransport`, `ResponsesApiTransport`, and `BedrockTransport` each own their own format conversion and API shape. Native AWS Bedrock support via the Converse API ships on top of the new abstraction. ([#10549](Local Sovereign Environment/pull/10549), [#13347](Local Sovereign Environment/pull/13347), [#13366](Local Sovereign Environment/pull/13366), [#13430](Local Sovereign Environment/pull/13430), [#13805](Local Sovereign Environment/pull/13805), [#13814](Local Sovereign Environment/pull/13814) — @kshitijk4poor + Teknium)

- **Five new inference paths** — Native NVIDIA NIM ([#11774](Local Sovereign Environment/pull/11774)), Arcee AI ([#9276](Local Sovereign Environment/pull/9276)), Step Plan ([#13893](Local Sovereign Environment/pull/13893)), Google Gemini CLI OAuth ([#11270](Local Sovereign Environment/pull/11270)), and Vercel ai-gateway with pricing + dynamic discovery ([#13223](Local Sovereign Environment/pull/13223) — @jerilynzheng). Plus Gemini routed through the native AI Studio API for better performance ([#12674](Local Sovereign Environment/pull/12674)).

- **GPT-5.5 over Codex OAuth** — OpenAI's new GPT-5.5 reasoning model is now available through your ChatGPT Codex OAuth, with live model discovery wired into the model picker so new OpenAI releases show up without catalog updates. ([#14720](Local Sovereign Environment/pull/14720))

- **QQBot — 17th supported platform** — Native QQBot adapter via QQ Official API v2, with QR scan-to-configure setup wizard, streaming cursor, emoji reactions, and DM/group policy gating that matches WeCom/Weixin parity. ([#9364](Local Sovereign Environment/pull/9364), [#11831](Local Sovereign Environment/pull/11831))

- **Plugin surface expanded** — Plugins can now register slash commands (`register_command`), dispatch tools directly (`dispatch_tool`), block tool execution from hooks (`pre_tool_call` can veto), rewrite tool results (`transform_tool_result`), transform terminal output (`transform_terminal_output`), ship image_gen backends, and add custom dashboard tabs. The bundled disk-cleanup plugin is opt-in by default as a reference implementation. ([#9377](Local Sovereign Environment/pull/9377), [#10626](Local Sovereign Environment/pull/10626), [#10763](Local Sovereign Environment/pull/10763), [#10951](Local Sovereign Environment/pull/10951), [#12929](Local Sovereign Environment/pull/12929), [#12944](Local Sovereign Environment/pull/12944), [#12972](Local Sovereign Environment/pull/12972), [#13799](Local Sovereign Environment/pull/13799), [#14175](Local Sovereign Environment/pull/14175))

- **`/steer` — mid-run agent nudges** — `/steer <prompt>` injects a note that the running agent sees after its next tool call, without interrupting the turn or breaking prompt cache. For when you want to course-correct an agent in-flight. ([#12116](Local Sovereign Environment/pull/12116))

- **Shell hooks** — Wire any shell script as a NIA lifecycle hook (pre_tool_call, post_tool_call, on_session_start, etc.) without writing a Python plugin. ([#13296](Local Sovereign Environment/pull/13296))

- **Webhook direct-delivery mode** — Webhook subscriptions can now forward payloads straight to a platform chat without going through the agent — zero-LLM push notifications for alerting, uptime checks, and event streams. ([#12473](Local Sovereign Environment/pull/12473))

- **Smarter delegation** — Subagents now have an explicit `orchestrator` role that can spawn their own workers, with configurable `max_spawn_depth` (default flat). Concurrent sibling subagents share filesystem state through a file-coordination layer so they don't clobber each other's edits. ([#13691](Local Sovereign Environment/pull/13691), [#13718](Local Sovereign Environment/pull/13718))

- **Auxiliary models — configurable UI + main-model-first** — `nia model` has a dedicated "Configure auxiliary models" screen for per-task overrides (compression, vision, session_search, title_generation). `auto` routing now defaults to the main model for side tasks across all users (previously aggregator users were silently routed to a cheap provider-side default). ([#11891](Local Sovereign Environment/pull/11891), [#11900](Local Sovereign Environment/pull/11900))

- **Dashboard plugin system + live theme switching** — The web dashboard is now extensible. Third-party plugins can add custom tabs, widgets, and views without forking. Paired with a live-switching theme system — themes now control colors, fonts, layout, and density — so users can hot-swap the dashboard look without a reload. Same theming discipline the CLI has, now on the web. ([#10951](Local Sovereign Environment/pull/10951), [#10687](Local Sovereign Environment/pull/10687), [#14725](Local Sovereign Environment/pull/14725))

- **Dashboard polish** — i18n (English + Chinese), react-router sidebar layout, mobile-responsive, Vercel deployment, real per-session API call tracking, and one-click update + gateway restart buttons. ([#9228](Local Sovereign Environment/pull/9228), [#9370](Local Sovereign Environment/pull/9370), [#9453](Local Sovereign Environment/pull/9453), [#10686](Local Sovereign Environment/pull/10686), [#13526](Local Sovereign Environment/pull/13526), [#14004](Local Sovereign Environment/pull/14004) — @austinpickett + @DeployFaith + Teknium)

---

## 🏗️ Core Agent & Architecture

### Transport Layer (NEW)
- **Transport ABC** abstracts format conversion and HTTP transport from `run_agent.py` into `agent/transports/` ([#13347](Local Sovereign Environment/pull/13347))
- **AnthropicTransport** — Anthropic Messages API path ([#13366](Local Sovereign Environment/pull/13366), @kshitijk4poor)
- **ChatCompletionsTransport** — default path for OpenAI-compatible providers ([#13805](Local Sovereign Environment/pull/13805))
- **ResponsesApiTransport** — OpenAI Responses API + Codex build_kwargs wiring ([#13430](Local Sovereign Environment/pull/13430), @kshitijk4poor)
- **BedrockTransport** — AWS Bedrock Converse API transport ([#13814](Local Sovereign Environment/pull/13814))

### Provider & Model Support
- **Native AWS Bedrock provider** via Converse API ([#10549](Local Sovereign Environment/pull/10549))
- **NVIDIA NIM native provider** (salvage of #11703) ([#11774](Local Sovereign Environment/pull/11774))
- **Arcee AI direct provider** ([#9276](Local Sovereign Environment/pull/9276))
- **Step Plan provider** (salvage #6005) ([#13893](Local Sovereign Environment/pull/13893), @kshitijk4poor)
- **Google Gemini CLI OAuth** inference provider ([#11270](Local Sovereign Environment/pull/11270))
- **Vercel ai-gateway** with pricing, attribution, and dynamic discovery ([#13223](Local Sovereign Environment/pull/13223), @jerilynzheng)
- **GPT-5.5 over Codex OAuth** with live model discovery in the picker ([#14720](Local Sovereign Environment/pull/14720))
- **Gemini routed through native AI Studio API** ([#12674](Local Sovereign Environment/pull/12674))
- **xAI Grok upgraded to Responses API** ([#10783](Local Sovereign Environment/pull/10783))
- **Ollama improvements** — Cloud provider support, GLM continuation, `think=false` control, surrogate sanitization, `/v1` hint ([#10782](Local Sovereign Environment/pull/10782))
- **Kimi K2.6** across OpenRouter, Nous Portal, native Kimi, and HuggingFace ([#13148](Local Sovereign Environment/pull/13148), [#13152](Local Sovereign Environment/pull/13152), [#13169](Local Sovereign Environment/pull/13169))
- **Kimi K2.5** promoted to first position in all model suggestion lists ([#11745](Local Sovereign Environment/pull/11745), @kshitijk4poor)
- **Xiaomi MiMo v2.5-pro + v2.5** on OpenRouter, Nous Portal, and native ([#14184](Local Sovereign Environment/pull/14184), [#14635](Local Sovereign Environment/pull/14635), @kshitijk4poor)
- **GLM-5V-Turbo** for coding plan ([#9907](Local Sovereign Environment/pull/9907))
- **Claude Opus 4.7** in Nous Portal catalog ([#11398](Local Sovereign Environment/pull/11398))
- **OpenRouter elephant-alpha** in curated lists ([#9378](Local Sovereign Environment/pull/9378))
- **OpenCode-Go** — Kimi K2.6 and Qwen3.5/3.6 Plus in curated catalog ([#13429](Local Sovereign Environment/pull/13429))
- **minimax/minimax-m2.5:free** in OpenRouter catalog ([#13836](Local Sovereign Environment/pull/13836))
- **`/model` merges models.dev entries** for lesser-loved providers ([#14221](Local Sovereign Environment/pull/14221))
- **Per-provider + per-model `request_timeout_seconds`** config ([#12652](Local Sovereign Environment/pull/12652))
- **Configurable API retry count** via `agent.api_max_retries` ([#14730](Local Sovereign Environment/pull/14730))
- **ctx_size context length key** for Lemonade server (salvage #8536) ([#14215](Local Sovereign Environment/pull/14215))
- **Custom provider display name prompt** ([#9420](Local Sovereign Environment/pull/9420))
- **Recommendation badges** on tool provider selection ([#9929](Local Sovereign Environment/pull/9929))
- Fix: correct GPT-5 family context lengths in fallback defaults ([#9309](Local Sovereign Environment/pull/9309))
- Fix: clamp `minimal` reasoning effort to `low` on Responses API ([#9429](Local Sovereign Environment/pull/9429))
- Fix: strip reasoning item IDs from Responses API input when `store=False` ([#10217](Local Sovereign Environment/pull/10217))
- Fix: OpenViking correct account default + commit session on `/new` and compress ([#10463](Local Sovereign Environment/pull/10463))
- Fix: Kimi `/coding` thinking block survival + empty reasoning_content + block ordering (multiple PRs)
- Fix: don't send Anthropic thinking to api.kimi.com/coding ([#13826](Local Sovereign Environment/pull/13826))
- Fix: send `max_tokens`, `reasoning_effort`, and `thinking` for Kimi/Moonshot
- Fix: stream reasoning content through OpenAI-compatible providers that emit it

### Agent Loop & Conversation
- **`/steer <prompt>`** — mid-run agent nudges after next tool call ([#12116](Local Sovereign Environment/pull/12116))
- **Orchestrator role + configurable spawn depth** for `delegate_task` (default flat) ([#13691](Local Sovereign Environment/pull/13691))
- **Cross-agent file state coordination** for concurrent subagents ([#13718](Local Sovereign Environment/pull/13718))
- **Compressor smart collapse, dedup, anti-thrashing**, template upgrade, hardening ([#10088](Local Sovereign Environment/pull/10088))
- **Compression summaries respect the conversation's language** ([#12556](Local Sovereign Environment/pull/12556))
- **Compression model falls back to main model** on permanent 503/404 ([#10093](Local Sovereign Environment/pull/10093))
- **Auto-continue interrupted agent work** after gateway restart ([#9934](Local Sovereign Environment/pull/9934))
- **Activity heartbeats** prevent false gateway inactivity timeouts ([#10501](Local Sovereign Environment/pull/10501))
- **Auxiliary models UI** — dedicated screen for per-task overrides ([#11891](Local Sovereign Environment/pull/11891))
- **Auxiliary auto routing defaults to main model** for all users ([#11900](Local Sovereign Environment/pull/11900))
- **PLATFORM_HINTS for Matrix, Mattermost, Feishu** ([#14428](Local Sovereign Environment/pull/14428), @alt-glitch)
- Fix: reset retry counters after compression; stop poisoning conversation history ([#10055](Local Sovereign Environment/pull/10055))
- Fix: break compression-exhaustion infinite loop and auto-reset session ([#10063](Local Sovereign Environment/pull/10063))
- Fix: stale agent timeout, uv venv detection, empty response after tools ([#10065](Local Sovereign Environment/pull/10065))
- Fix: prevent premature loop exit when weak models return empty after substantive tool calls ([#10472](Local Sovereign Environment/pull/10472))
- Fix: preserve pre-start terminal interrupts ([#10504](Local Sovereign Environment/pull/10504))
- Fix: improve interrupt responsiveness during concurrent tool execution ([#10935](Local Sovereign Environment/pull/10935))
- Fix: word-wrap spinner, interruptable agent join, and delegate_task interrupt ([#10940](Local Sovereign Environment/pull/10940))
- Fix: `/stop` no longer resets the session ([#9224](Local Sovereign Environment/pull/9224))
- Fix: honor interrupts during MCP tool waits ([#9382](Local Sovereign Environment/pull/9382), @helix4u)
- Fix: break stuck session resume loops after repeated restarts ([#9941](Local Sovereign Environment/pull/9941))
- Fix: empty response nudge crash + placeholder leak to cron targets ([#11021](Local Sovereign Environment/pull/11021))
- Fix: streaming cursor sanitization to prevent message truncation (multiple PRs)
- Fix: resolve `context_length` for plugin context engines ([#9238](Local Sovereign Environment/pull/9238))

### Session & Memory
- **Auto-prune old sessions + VACUUM state.db** at startup ([#13861](Local Sovereign Environment/pull/13861))
- **Honcho overhaul** — context injection, 5-tool surface, cost safety, session isolation ([#10619](Local Sovereign Environment/pull/10619))
- **Hindsight richer session-scoped retain metadata** (salvage of #6290) ([#13987](Local Sovereign Environment/pull/13987))
- Fix: deduplicate memory provider tools to prevent 400 on strict providers ([#10511](Local Sovereign Environment/pull/10511))
- Fix: discover user-installed memory providers from `$NIA_HOME/plugins/` ([#10529](Local Sovereign Environment/pull/10529))
- Fix: add `on_memory_write` bridge to sequential tool execution path ([#10507](Local Sovereign Environment/pull/10507))
- Fix: preserve `session_id` across `previous_response_id` chains in `/v1/responses` ([#10059](Local Sovereign Environment/pull/10059))

---

## 🖥️ New Ink-based TUI

A full React/Ink rewrite of the interactive CLI — invoked via `nia --tui` or `NIA_TUI=1`. Shipped across ~310 commits to `ui-tui/` and `tui_gateway/`.

### TUI Foundations
- New TUI based on Ink + Python JSON-RPC backend
- Prettier + ESLint + vitest tooling for `ui-tui/`
- Entry split between `src/entry.tsx` (TTY gate) and `src/app.tsx` (state machine)
- Persistent `_SlashWorker` subprocess for slash command dispatch

### UX & Features
- **Stable picker keys, /clear confirm, light-theme preset** ([#12312](Local Sovereign Environment/pull/12312), @OutThisLife)
- **Git branch in status bar** cwd label ([#12305](Local Sovereign Environment/pull/12305), @OutThisLife)
- **Per-turn elapsed stopwatch in FaceTicker + done-in sys line** ([#13105](Local Sovereign Environment/pull/13105), @OutThisLife)
- **Subagent spawn observability overlay** ([#14045](Local Sovereign Environment/pull/14045), @OutThisLife)
- **Per-prompt elapsed stopwatch in status bar** ([#12948](Local Sovereign Environment/pull/12948))
- Sticky composer that freezes during scroll
- OSC-52 clipboard support for copy across SSH sessions
- Virtualized history rendering for performance
- Slash command autocomplete via `complete.slash` RPC
- Path autocomplete via `complete.path` RPC
- Dozens of resize/ghosting/sticky-prompt fixes landed through the week

### Structural Refactors
- Decomposed `app.tsx` into `app/event-handler`, `app/slash-handler`, `app/stores`, `app/hooks` ([#14640](Local Sovereign Environment/pull/14640) and surrounding)
- Component split: `branding.tsx`, `markdown.tsx`, `prompts.tsx`, `sessionPicker.tsx`, `messageLine.tsx`, `thinking.tsx`, `maskedPrompt.tsx`
- Hook split: `useCompletion`, `useInputHistory`, `useQueue`, `useVirtualHistory`

---

## 📱 Messaging Platforms (Gateway)

### New Platforms
- **QQBot (17th platform)** — QQ Official API v2 adapter with QR setup, streaming, package split ([#9364](Local Sovereign Environment/pull/9364), [#11831](Local Sovereign Environment/pull/11831))

### Telegram
- **Dedicated `TELEGRAM_PROXY` env var + config.yaml proxy support** (closes #9414, #6530, #9074, #7786) ([#10681](Local Sovereign Environment/pull/10681))
- **`ignored_threads` config** for Telegram groups ([#9530](Local Sovereign Environment/pull/9530))
- **Config option to disable link previews** (closes #8728) ([#10610](Local Sovereign Environment/pull/10610))
- **Auto-wrap markdown tables** in code blocks ([#11794](Local Sovereign Environment/pull/11794))
- Fix: prevent duplicate replies when stream task is cancelled ([#9319](Local Sovereign Environment/pull/9319))
- Fix: prevent streaming cursor (▉) from appearing as standalone messages ([#9538](Local Sovereign Environment/pull/9538))
- Fix: retry transient tool sends + cold-boot budget ([#10947](Local Sovereign Environment/pull/10947))
- Fix: Markdown special char escaping in `send_exec_approval`
- Fix: parentheses in URLs during MarkdownV2 link conversion
- Fix: Unicode dash normalization in model switch (closes iOS smart-punctuation issue)
- Many platform hint / streaming / session-key fixes

### Discord
- **Forum channel support** (salvage of #10145 + media + polish) ([#11920](Local Sovereign Environment/pull/11920))
- **`DISCORD_ALLOWED_ROLES`** for role-based access control ([#11608](Local Sovereign Environment/pull/11608))
- **Config option to disable slash commands** (salvage #13130) ([#14315](Local Sovereign Environment/pull/14315))
- **Native `send_animation`** for inline GIF playback ([#10283](Local Sovereign Environment/pull/10283))
- **`send_message` Discord media attachments** ([#10246](Local Sovereign Environment/pull/10246))
- **`/skill` command group** with category subcommands ([#9909](Local Sovereign Environment/pull/9909))
- **Extract reply text from message references** ([#9781](Local Sovereign Environment/pull/9781))

### Feishu
- **Intelligent reply on document comments** with 3-tier access control ([#11898](Local Sovereign Environment/pull/11898))
- **Show processing state via reactions** on user messages ([#12927](Local Sovereign Environment/pull/12927))
- **Preserve @mention context for agent consumption** (salvage #13874) ([#14167](Local Sovereign Environment/pull/14167))

### DingTalk
- **`require_mention` + `allowed_users` gating** (parity with Slack/Telegram/Discord) ([#11564](Local Sovereign Environment/pull/11564))
- **QR-code device-flow authorization** for setup wizard ([#11574](Local Sovereign Environment/pull/11574))
- **AI Cards streaming, emoji reactions, and media handling** (salvage of #10985) ([#11910](Local Sovereign Environment/pull/11910))

### WhatsApp
- **`send_voice`** — native audio message delivery ([#13002](Local Sovereign Environment/pull/13002))
- **`dm_policy` and `group_policy`** parity with WeCom/Weixin/QQ adapters ([#13151](Local Sovereign Environment/pull/13151))

### WeCom / Weixin
- **WeCom QR-scan bot creation + interactive setup wizard** (salvage #13923) ([#13961](Local Sovereign Environment/pull/13961))

### Signal
- **Media delivery support** via `send_message` ([#13178](Local Sovereign Environment/pull/13178))

### Slack
- **Per-thread sessions for DMs by default** ([#10987](Local Sovereign Environment/pull/10987))

### BlueBubbles (iMessage)
- Group chat session separation, webhook registration & auth fixes ([#9806](Local Sovereign Environment/pull/9806))

### Gateway Core
- **Gateway proxy mode** — forward messages to a remote API server ([#9787](Local Sovereign Environment/pull/9787))
- **Per-channel ephemeral prompts** (Discord, Telegram, Slack, Mattermost) ([#10564](Local Sovereign Environment/pull/10564))
- **Surface plugin slash commands** natively on all platforms + decision-capable command hook ([#14175](Local Sovereign Environment/pull/14175))
- **Support document/archive extensions in MEDIA: tag extraction** (salvage #8255) ([#14307](Local Sovereign Environment/pull/14307))
- **Recognize `.pdf` in MEDIA: tag extraction** ([#13683](Local Sovereign Environment/pull/13683))
- **`--all` flag for `gateway start` and `restart`** ([#10043](Local Sovereign Environment/pull/10043))
- **Notify active sessions on gateway shutdown** + update health check ([#9850](Local Sovereign Environment/pull/9850))
- **Block agent from self-destructing the gateway** via terminal (closes #6666) ([#9895](Local Sovereign Environment/pull/9895))
- Fix: suppress duplicate replies on interrupt and streaming flood control ([#10235](Local Sovereign Environment/pull/10235))
- Fix: close temporary agents after one-off tasks ([#11028](Local Sovereign Environment/pull/11028), @kshitijk4poor)
- Fix: busy-session ack when user messages during active agent run ([#10068](Local Sovereign Environment/pull/10068))
- Fix: route watch-pattern notifications to the originating session ([#10460](Local Sovereign Environment/pull/10460))
- Fix: preserve notify context in executor threads ([#10921](Local Sovereign Environment/pull/10921), @kshitijk4poor)
- Fix: avoid duplicate replies after interrupted long tasks ([#11018](Local Sovereign Environment/pull/11018))
- Fix: unlink stale PID + lock files on cleanup
- Fix: force-unlink stale PID file after `--replace` takeover

---

## 🔧 Tool System

### Plugin Surface (major expansion)
- **`register_command()`** — plugins can now add slash commands ([#10626](Local Sovereign Environment/pull/10626))
- **`dispatch_tool()`** — plugins can invoke tools from their code ([#10763](Local Sovereign Environment/pull/10763))
- **`pre_tool_call` blocking** — plugins can veto tool execution ([#9377](Local Sovereign Environment/pull/9377))
- **`transform_tool_result`** — plugins rewrite tool results generically ([#12972](Local Sovereign Environment/pull/12972))
- **`transform_terminal_output`** — plugins rewrite terminal tool output ([#12929](Local Sovereign Environment/pull/12929))
- **Namespaced skill registration** for plugin skill bundles ([#9786](Local Sovereign Environment/pull/9786))
- **Opt-in-by-default + bundled disk-cleanup plugin** (salvage #12212) ([#12944](Local Sovereign Environment/pull/12944))
- **Pluggable `image_gen` backends + OpenAI provider** ([#13799](Local Sovereign Environment/pull/13799))
- **`openai-codex` image_gen plugin** (gpt-image-2 via Codex OAuth) ([#14317](Local Sovereign Environment/pull/14317))
- **Shell hooks** — wire shell scripts as hook callbacks ([#13296](Local Sovereign Environment/pull/13296))

### Browser
- **`browser_cdp` raw DevTools Protocol passthrough** ([#12369](Local Sovereign Environment/pull/12369))
- Camofox hardening + connection stability across the window

### Execute Code
- **Project/strict execution modes** (default: project) ([#11971](Local Sovereign Environment/pull/11971))

### Image Generation
- **Multi-model FAL support** with picker in `nia tools` ([#11265](Local Sovereign Environment/pull/11265))
- **Recraft V3 → V4 Pro, Nano Banana → Pro upgrades** ([#11406](Local Sovereign Environment/pull/11406))
- **GPT Image 2** in FAL catalog ([#13677](Local Sovereign Environment/pull/13677))
- **xAI image generation provider** (grok-imagine-image) ([#14765](Local Sovereign Environment/pull/14765))

### TTS / STT / Voice
- **Google Gemini TTS provider** ([#11229](Local Sovereign Environment/pull/11229))
- **xAI Grok STT provider** ([#14473](Local Sovereign Environment/pull/14473))
- **xAI TTS** (shipped with Responses API upgrade) ([#10783](Local Sovereign Environment/pull/10783))
- **KittenTTS local provider** (salvage of #2109) ([#13395](Local Sovereign Environment/pull/13395))
- **CLI record beep toggle** ([#13247](Local Sovereign Environment/pull/13247), @helix4u)

### Webhook / Cron
- **Webhook direct-delivery mode** — zero-LLM push notifications ([#12473](Local Sovereign Environment/pull/12473))
- **Cron `wakeAgent` gate** — scripts can skip the agent entirely ([#12373](Local Sovereign Environment/pull/12373))
- **Cron per-job `enabled_toolsets`** — cap token overhead + cost per job ([#14767](Local Sovereign Environment/pull/14767))

### Delegate
- **Orchestrator role** + configurable spawn depth (default flat) ([#13691](Local Sovereign Environment/pull/13691))
- **Cross-agent file state coordination** ([#13718](Local Sovereign Environment/pull/13718))

### File / Patch
- **`patch` — "did you mean?" feedback** when patch fails to match ([#13435](Local Sovereign Environment/pull/13435))

### API Server
- **Stream `/v1/responses` SSE tool events** (salvage #9779) ([#10049](Local Sovereign Environment/pull/10049))
- **Inline image inputs** on `/v1/chat/completions` and `/v1/responses` ([#12969](Local Sovereign Environment/pull/12969))

### Docker / Podman
- **Entry-level Podman support** — `find_docker()` + rootless entrypoint ([#10066](Local Sovereign Environment/pull/10066))
- **Add docker-cli to Docker image** (salvage #10096) ([#14232](Local Sovereign Environment/pull/14232))
- **File-sync back to host on teardown** (salvage of #8189 + hardening) ([#11291](Local Sovereign Environment/pull/11291))

### MCP
- 12 MCP improvements across the window (status, timeout handling, tool-call forwarding, etc.)

---

## 🧩 Skills Ecosystem

### Skill System
- **Namespaced skill registration** for plugin bundles ([#9786](Local Sovereign Environment/pull/9786))
- **`nia skills reset`** to un-stick bundled skills ([#11468](Local Sovereign Environment/pull/11468))
- **Skills guard opt-in** — `config.skills.guard_agent_created` (default off) ([#14557](Local Sovereign Environment/pull/14557))
- **Bundled skill scripts runnable out of the box** ([#13384](Local Sovereign Environment/pull/13384))
- **`xitter` replaced with `xurl`** — the official X API CLI ([#12303](Local Sovereign Environment/pull/12303))
- **MiniMax-AI/cli as default skill tap** (salvage #7501) ([#14493](Local Sovereign Environment/pull/14493))
- **Fuzzy `@` file completions + mtime sorting** ([#9467](Local Sovereign Environment/pull/9467))

### New Skills
- **concept-diagrams** (salvage of #11045, @v1k22) ([#11363](Local Sovereign Environment/pull/11363))
- **architecture-diagram** (Cocoon AI port) ([#9906](Local Sovereign Environment/pull/9906))
- **pixel-art** with hardware palettes and video animation ([#12663](Local Sovereign Environment/pull/12663), [#12725](Local Sovereign Environment/pull/12725))
- **baoyu-comic** ([#13257](Local Sovereign Environment/pull/13257), @JimLiu)
- **baoyu-infographic** — 21 layouts × 21 styles (salvage #9901) ([#12254](Local Sovereign Environment/pull/12254))
- **page-agent** — embed Alibaba's in-page GUI agent in your webapp ([#13976](Local Sovereign Environment/pull/13976))
- **fitness-nutrition** optional skill + optional env var support ([#9355](Local Sovereign Environment/pull/9355))
- **drug-discovery** — ChEMBL, PubChem, OpenFDA, ADMET ([#9443](Local Sovereign Environment/pull/9443))
- **touchdesigner-mcp** (salvage of #10081) ([#12298](Local Sovereign Environment/pull/12298))
- **adversarial-ux-test** optional skill (salvage of #2494, @omnissiah-comelse) ([#13425](Local Sovereign Environment/pull/13425))
- **maps** — added `guest_house`, `camp_site`, and dual-key bakery lookup ([#13398](Local Sovereign Environment/pull/13398))
- **llm-wiki** — port provenance markers, source hashing, and quality signals ([#13700](Local Sovereign Environment/pull/13700))

---

## 📊 Web Dashboard

- **i18n (English + Chinese) language switcher** ([#9453](Local Sovereign Environment/pull/9453))
- **Live-switching theme system** ([#10687](Local Sovereign Environment/pull/10687))
- **Dashboard plugin system** — extend the web UI with custom tabs ([#10951](Local Sovereign Environment/pull/10951))
- **react-router, sidebar layout, sticky header, dropdown component** ([#9370](Local Sovereign Environment/pull/9370), @austinpickett)
- **Responsive for mobile** ([#9228](Local Sovereign Environment/pull/9228), @DeployFaith)
- **Vercel deployment** ([#10686](Local Sovereign Environment/pull/10686), [#11061](Local Sovereign Environment/pull/11061), @austinpickett)
- **Context window config support** ([#9357](Local Sovereign Environment/pull/9357))
- **HTTP health probe for cross-container gateway detection** ([#9894](Local Sovereign Environment/pull/9894))
- **Update + restart gateway buttons** ([#13526](Local Sovereign Environment/pull/13526), @austinpickett)
- **Real API call count per session** (salvages #10140) ([#14004](Local Sovereign Environment/pull/14004))

---

## 🖱️ CLI & User Experience

- **Dynamic shell completion for bash, zsh, and fish** ([#9785](Local Sovereign Environment/pull/9785))
- **Light-mode skins + skin-aware completion menus** ([#9461](Local Sovereign Environment/pull/9461))
- **Numbered keyboard shortcuts** on approval and clarify prompts ([#13416](Local Sovereign Environment/pull/13416))
- **Markdown stripping, compact multiline previews, external editor** ([#12934](Local Sovereign Environment/pull/12934))
- **`--ignore-user-config` and `--ignore-rules` flags** (port codex#18646) ([#14277](Local Sovereign Environment/pull/14277))
- **Account limits section in `/usage`** ([#13428](Local Sovereign Environment/pull/13428))
- **Doctor: Command Installation check** for `nia` bin symlink ([#10112](Local Sovereign Environment/pull/10112))
- **ESC cancels secret/sudo prompts**, clearer skip messaging ([#9902](Local Sovereign Environment/pull/9902))
- Fix: agent-facing text uses `display_nia_home()` instead of hardcoded `~/.nia` ([#10285](Local Sovereign Environment/pull/10285))
- Fix: enforce `config.yaml` as sole CWD source + deprecate `.env` CWD vars + add `nia memory reset` ([#11029](Local Sovereign Environment/pull/11029))

---

## 🔒 Security & Reliability

- **Global toggle to allow private/internal URL resolution** ([#14166](Local Sovereign Environment/pull/14166))
- **Block agent from self-destructing the gateway** via terminal (closes #6666) ([#9895](Local Sovereign Environment/pull/9895))
- **Telegram callback authorization** on update prompts ([#10536](Local Sovereign Environment/pull/10536))
- **SECURITY.md** added ([#10532](Local Sovereign Environment/pull/10532), @I3eg1nner)
- **Warn about legacy nia.service units** during `nia update` ([#11918](Local Sovereign Environment/pull/11918))
- **Complete ASCII-locale UnicodeEncodeError recovery** for `api_messages`/`reasoning_content` (closes #6843) ([#10537](Local Sovereign Environment/pull/10537))
- **Prevent stale `os.environ` leak** after `clear_session_vars` ([#10527](Local Sovereign Environment/pull/10527))
- **Prevent agent hang when backgrounding processes** via terminal tool ([#10584](Local Sovereign Environment/pull/10584))
- Many smaller session-resume, interrupt, streaming, and memory-race fixes throughout the window

---

## 🐛 Notable Bug Fixes

The `fix:` category in this window covers 482 PRs. Highlights:

- Streaming cursor artifacts filtered from Matrix, Telegram, WhatsApp, Discord (multiple PRs)
- `<think>` and `<thought>` blocks filtered from gateway stream consumers ([#9408](Local Sovereign Environment/pull/9408))
- Gateway display.streaming root-config override regression ([#9799](Local Sovereign Environment/pull/9799))
- Context `session_search` coerces limit to int (prevents TypeError) ([#10522](Local Sovereign Environment/pull/10522))
- Memory tool stays available when `fcntl` is unavailable (Windows) ([#9783](Local Sovereign Environment/pull/9783))
- Trajectory compressor credentials load from `NIA_HOME/.env` ([#9632](Local Sovereign Environment/pull/9632), @Dusk1e)
- `@_context_completions` no longer crashes on `@` mention ([#9683](Local Sovereign Environment/pull/9683), @kshitijk4poor)
- Group session `user_id` no longer treated as `thread_id` in shutdown notifications ([#10546](Local Sovereign Environment/pull/10546))
- Telegram `platform_hint` — markdown is supported (closes #8261) ([#10612](Local Sovereign Environment/pull/10612))
- Doctor checks for Kimi China credentials fixed
- Streaming: don't suppress final response when commentary message is sent ([#10540](Local Sovereign Environment/pull/10540))
- Rapid Telegram follow-ups no longer get cut off

---

## 🧪 Testing & CI

- **Contributor attribution CI check** on PRs ([#9376](Local Sovereign Environment/pull/9376))
- Hermetic test parity (`scripts/run_tests.sh`) held across this window
- Test count stabilized post-Transport refactor; CI matrix held green through the transport rollout

---

## 📚 Documentation

- Atropos + wandb links in user guide
- ACP / VS Code / Zed / JetBrains integration docs refresh
- Webhook subscription docs updated for direct-delivery mode
- Plugin author guide expanded for new hooks (`register_command`, `dispatch_tool`, `transform_tool_result`)
- Transport layer developer guide added
- Website removed Discussions link from README

---

## 👥 Contributors

### Core
- **@teknium1** (Teknium)

### Top Community Contributors (by merged PR count)
- **@kshitijk4poor** — 49 PRs · Transport refactor (AnthropicTransport, ResponsesApiTransport), Step Plan provider, Xiaomi MiMo v2.5 support, numerous gateway fixes, promoted Kimi K2.5, @ mention crash fix
- **@OutThisLife** (Brooklyn) — 31 PRs · TUI polish, git branch in status bar, per-turn stopwatch, stable picker keys, `/clear` confirm, light-theme preset, subagent spawn observability overlay
- **@helix4u** — 11 PRs · Voice CLI record beep, MCP tool interrupt handling, assorted stability fixes
- **@austinpickett** — 8 PRs · Dashboard react-router + sidebar + sticky header + dropdown, Vercel deployment, update + restart buttons
- **@alt-glitch** — 8 PRs · PLATFORM_HINTS for Matrix/Mattermost/Feishu, Matrix fixes
- **@ethernet8023** — 3 PRs
- **@benbarclay** — 3 PRs
- **@Aslaaen** — 2 PRs

### Also contributing
@jerilynzheng (ai-gateway pricing), @JimLiu (baoyu-comic skill), @Dusk1e (trajectory compressor credentials), @DeployFaith (mobile-responsive dashboard), @LeonSGP43, @v1k22 (concept-diagrams), @omnissiah-comelse (adversarial-ux-test), @coekfung (Telegram MarkdownV2 expandable blockquotes), @liftaris (TUI provider resolution), @arihantsethia (skill analytics dashboard), @topcheer + @xing8star (QQBot foundation), @kovyrin, @I3eg1nner (SECURITY.md), @PeterBerthelsen, @lengxii, @priveperfumes, @sjz-ks, @cuyua9, @Disaster-Terminator, @leozeli, @LehaoLin, @trevthefoolish, @loongfay, @MrNiceRicee, @WideLee, @bluefishs, @malaiwah, @bobashopcashier, @dsocolobsky, @iamagenius00, @IAvecilla, @aniruddhaadak80, @Es1la, @asheriif, @walli, @jquesnelle (original Tool Gateway work).

### All Contributors (alphabetical)

@0xyg3n, @10ishq, @A-afflatus, @Abnertheforeman, @admin28980, @adybag14-cyber, @akhater, @alexzhu0,
@AllardQuek, @alt-glitch, @aniruddhaadak80, @anna-oake, @anniesurla, @anthhub, @areu01or00, @arihantsethia,
@arthurbr11, @asheriif, @Aslaaen, @Asunfly, @austinpickett, @AviArora02-commits, @AxDSan, @azhengbot, @Bartok9,
@benbarclay, @bennytimz, @bernylinville, @bingo906, @binhnt92, @bkadish, @bluefishs, @bobashopcashier,
@brantzh6, @BrennerSpear, @brianclemens, @briandevans, @brooklynnicholson, @bugkill3r, @buray, @burtenshaw,
@cdanis, @cgarwood82, @ChimingLiu, @chongweiliu, @christopherwoodall, @coekfung, @cola-runner, @corazzione,
@counterposition, @cresslank, @cuyua9, @cypres0099, @danieldoderlein, @davetist, @davidvv, @DeployFaith,
@Dev-Mriganka, @devorun, @dieutx, @Disaster-Terminator, @dodo-reach, @draix, @DrStrangerUJN, @dsocolobsky,
@Dusk1e, @dyxushuai, @elkimek, @elmatadorgh, @emozilla, @entropidelic, @Erosika, @erosika, @Es1la, @etcircle,
@etherman-os, @ethernet8023, @fancydirty, @farion1231, @fatinghenji, @Fatty911, @fengtianyu88, @Feranmi10,
@flobo3, @francip, @fuleinist, @g-guthrie, @GenKoKo, @gianfrancopiana, @gnanam1990, @GuyCui, @haileymarshall,
@haimu0x, @handsdiff, @hansnow, @hedgeho9X, @helix4u, @hengm3467, @HenkDz, @heykb, @hharry11, @HiddenPuppy,
@honghua, @houko, @houziershi, @hsy5571616, @huangke19, @hxp-plus, @Hypn0sis, @I3eg1nner, @iacker,
@iamagenius00, @IAvecilla, @iborazzi, @Ifkellx, @ifrederico, @imink, @isaachuangGMICLOUD, @ismell0992-afk,
@j0sephz, @Jaaneek, @jackjin1997, @JackTheGit, @jaffarkeikei, @jerilynzheng, @JiaDe-Wu, @Jiawen-lee, @JimLiu,
@jinzheng8115, @jneeee, @jplew, @jquesnelle, @Julientalbot, @Junass1, @jvcl, @kagura-agent, @keifergu,
@kevinskysunny, @keyuyuan, @konsisumer, @kovyrin, @kshitijk4poor, @leeyang1990, @LehaoLin, @lengxii,
@LeonSGP43, @leozeli, @li0near, @liftaris, @Lind3ey, @Linux2010, @liujinkun2025, @LLQWQ, @Llugaes, @lmoncany,
@longsizhuo, @lrawnsley, @Lubrsy706, @lumenradley, @luyao618, @lvnilesh, @LVT382009, @m0n5t3r, @Magaav,
@MagicRay1217, @malaiwah, @manuelschipper, @Marvae, @MassiveMassimo, @mavrickdeveloper, @maxchernin, @memosr,
@meng93, @mengjian-github, @MestreY0d4-Uninter, @Mibayy, @MikeFac, @mikewaters, @milkoor, @minorgod,
@MrNiceRicee, @ms-alan, @mvanhorn, @n-WN, @N0nb0at, @Nan93, @NIDNASSER-Abdelmajid, @nish3451, @niyoh120,
@nocoo, @nosleepcassette, @NousResearch, @ogzerber, @omnissiah-comelse, @Only-Code-A, @opriz, @OwenYWT, @pedh,
@pefontana, @PeterBerthelsen, @phpoh, @pinion05, @plgonzalezrx8, @pradeep7127, @priveperfumes,
@projectadmin-dev, @PStarH, @rnijhara, @Roy-oss1, @roytian1217, @RucchiZ, @Ruzzgar, @RyanLee-Dev, @Salt-555,
@Sanjays2402, @sgaofen, @sharziki, @shenuu, @shin4, @SHL0MS, @shushuzn, @sicnuyudidi, @simon-gtcl,
@simon-marcus, @sirEven, @Sisyphus, @sjz-ks, @snreynolds, @Societus, @Somme4096, @sontianye, @sprmn24,
@StefanIsMe, @stephenschoettler, @Swift42, @taeng0204, @taeuk178, @tannerfokkens-maker, @TaroballzChen,
@ten-ltw, @teyrebaz33, @Tianworld, @topcheer, @Tranquil-Flow, @trevthefoolish, @TroyMitchell911, @UNLINEARITY,
@v1k22, @vivganes, @vominh1919, @vrinek, @VTRiot, @WadydX, @walli, @wenhao7, @WhiteWorld, @WideLee, @wujhsu,
@WuTianyi123, @Wysie, @xandersbell, @xiaoqiang243, @xiayh0107, @xinpengdr, @Xowiek, @ycbai, @yeyitech, @ygd58,
@youngDoo, @yudaiyan, @Yukipukii1, @yule975, @yyq4193, @yzx9, @ZaynJarvis, @zhang9w0v5, @zhanggttry,
@zhangxicen, @zhongyueming1121, @zhouxiaoya12, @zons-zhaozhy

Also: @maelrx, @Marco Rutsch, @MaxsolcuCrypto, @Mind-Dragon, @Paul Bergeron, @say8hi, @whitehatjr1001.


---

**Full Changelog**: [v2026.4.13...v2026.4.23](Local Sovereign Environment/compare/v2026.4.13...v2026.4.23)
