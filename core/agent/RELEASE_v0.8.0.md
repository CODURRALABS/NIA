# NIA v0.8.0 (v2026.4.8)

**Release Date:** April 8, 2026

> The intelligence release — background task auto-notifications, free MiMo v2 Pro on Nous Portal, live model switching across all platforms, self-optimized GPT/Codex guidance, native Google AI Studio, smart inactivity timeouts, approval buttons, MCP OAuth 2.1, and 209 merged PRs with 82 resolved issues.

---

## ✨ Highlights

- **Background Process Auto-Notifications (`notify_on_complete`)** — Background tasks can now automatically notify the agent when they finish. Start a long-running process (AI model training, test suites, deployments, builds) and the agent gets notified on completion — no polling needed. The agent can keep working on other things and pick up results when they land. ([#5779](Local Sovereign Environment/pull/5779))

- **Free Xiaomi MiMo v2 Pro on Nous Portal** — Nous Portal now supports the free-tier Xiaomi MiMo v2 Pro model for auxiliary tasks (compression, vision, summarization), with free-tier model gating and pricing display in model selection. ([#6018](Local Sovereign Environment/pull/6018), [#5880](Local Sovereign Environment/pull/5880))

- **Live Model Switching (`/model` Command)** — Switch models and providers mid-session from CLI, Telegram, Discord, Slack, or any gateway platform. Aggregator-aware resolution keeps you on OpenRouter/Nous when possible, with automatic cross-provider fallback when needed. Interactive model pickers on Telegram and Discord with inline buttons. ([#5181](Local Sovereign Environment/pull/5181), [#5742](Local Sovereign Environment/pull/5742))

- **Self-Optimized GPT/Codex Tool-Use Guidance** — The agent diagnosed and patched 5 failure modes in GPT and Codex tool calling through automated behavioral benchmarking, dramatically improving reliability on OpenAI models. Includes execution discipline guidance and thinking-only prefill continuation for structured reasoning. ([#6120](Local Sovereign Environment/pull/6120), [#5414](Local Sovereign Environment/pull/5414), [#5931](Local Sovereign Environment/pull/5931))

- **Google AI Studio (Gemini) Native Provider** — Direct access to Gemini models through Google's AI Studio API. Includes automatic models.dev registry integration for real-time context length detection across any provider. ([#5577](Local Sovereign Environment/pull/5577))

- **Inactivity-Based Agent Timeouts** — Gateway and cron timeouts now track actual tool activity instead of wall-clock time. Long-running tasks that are actively working will never be killed — only truly idle agents time out. ([#5389](Local Sovereign Environment/pull/5389), [#5440](Local Sovereign Environment/pull/5440))

- **Approval Buttons on Slack & Telegram** — Dangerous command approval via native platform buttons instead of typing `/approve`. Slack gets thread context preservation; Telegram gets emoji reactions for approval status. ([#5890](Local Sovereign Environment/pull/5890), [#5975](Local Sovereign Environment/pull/5975))

- **MCP OAuth 2.1 PKCE + OSV Malware Scanning** — Full standards-compliant OAuth for MCP server authentication, plus automatic malware scanning of MCP extension packages via the OSV vulnerability database. ([#5420](Local Sovereign Environment/pull/5420), [#5305](Local Sovereign Environment/pull/5305))

- **Centralized Logging & Config Validation** — Structured logging to `~/.nia/logs/` (agent.log + errors.log) with the `nia logs` command for tailing and filtering. Config structure validation catches malformed YAML at startup before it causes cryptic failures. ([#5430](Local Sovereign Environment/pull/5430), [#5426](Local Sovereign Environment/pull/5426))

- **Plugin System Expansion** — Plugins can now register CLI subcommands, receive request-scoped API hooks with correlation IDs, prompt for required env vars during install, and hook into session lifecycle events (finalize/reset). ([#5295](Local Sovereign Environment/pull/5295), [#5427](Local Sovereign Environment/pull/5427), [#5470](Local Sovereign Environment/pull/5470), [#6129](Local Sovereign Environment/pull/6129))

- **Matrix Tier 1 & Platform Hardening** — Matrix gets reactions, read receipts, rich formatting, and room management. Discord adds channel controls and ignored channels. Signal gets full MEDIA: tag delivery. Mattermost gets file attachments. Comprehensive reliability fixes across all platforms. ([#5275](Local Sovereign Environment/pull/5275), [#5975](Local Sovereign Environment/pull/5975), [#5602](Local Sovereign Environment/pull/5602))

- **Security Hardening Pass** — Consolidated SSRF protections, timing attack mitigations, tar traversal prevention, credential leakage guards, cron path traversal hardening, and cross-session isolation. Terminal workdir sanitization across all backends. ([#5944](Local Sovereign Environment/pull/5944), [#5613](Local Sovereign Environment/pull/5613), [#5629](Local Sovereign Environment/pull/5629))

---

## 🏗️ Core Agent & Architecture

### Provider & Model Support
- **Native Google AI Studio (Gemini) provider** with models.dev integration for automatic context length detection ([#5577](Local Sovereign Environment/pull/5577))
- **`/model` command — full provider+model system overhaul** — live switching across CLI and all gateway platforms with aggregator-aware resolution ([#5181](Local Sovereign Environment/pull/5181))
- **Interactive model picker for Telegram and Discord** — inline button-based model selection ([#5742](Local Sovereign Environment/pull/5742))
- **Nous Portal free-tier model gating** with pricing display in model selection ([#5880](Local Sovereign Environment/pull/5880))
- **Model pricing display** for OpenRouter and Nous Portal providers ([#5416](Local Sovereign Environment/pull/5416))
- **xAI (Grok) prompt caching** via `x-grok-conv-id` header ([#5604](Local Sovereign Environment/pull/5604))
- **Grok added to tool-use enforcement models** for direct xAI usage ([#5595](Local Sovereign Environment/pull/5595))
- **MiniMax TTS provider** (speech-2.8) ([#4963](Local Sovereign Environment/pull/4963))
- **Non-agentic model warning** — warns users when loading NIA LLM models not designed for tool use ([#5378](Local Sovereign Environment/pull/5378))
- **Ollama Cloud auth, /model switch persistence**, and alias tab completion ([#5269](Local Sovereign Environment/pull/5269))
- **Preserve dots in OpenCode Go model names** (minimax-m2.7, glm-4.5, kimi-k2.5) ([#5597](Local Sovereign Environment/pull/5597))
- **MiniMax models 404 fix** — strip /v1 from Anthropic base URL for OpenCode Go ([#4918](Local Sovereign Environment/pull/4918))
- **Provider credential reset windows** honored in pooled failover ([#5188](Local Sovereign Environment/pull/5188))
- **OAuth token sync** between credential pool and credentials file ([#4981](Local Sovereign Environment/pull/4981))
- **Stale OAuth credentials** no longer block OpenRouter users on auto-detect ([#5746](Local Sovereign Environment/pull/5746))
- **Codex OAuth credential pool disconnect** + expired token import fix ([#5681](Local Sovereign Environment/pull/5681))
- **Codex pool entry sync** from `~/.codex/auth.json` on exhaustion — @GratefulDave ([#5610](Local Sovereign Environment/pull/5610))
- **Auxiliary client payment fallback** — retry with next provider on 402 ([#5599](Local Sovereign Environment/pull/5599))
- **Auxiliary client resolves named custom providers** and 'main' alias ([#5978](Local Sovereign Environment/pull/5978))
- **Use mimo-v2-pro** for non-vision auxiliary tasks on Nous free tier ([#6018](Local Sovereign Environment/pull/6018))
- **Vision auto-detection** tries main provider first ([#6041](Local Sovereign Environment/pull/6041))
- **Provider re-ordering and Quick Install** — @austinpickett ([#4664](Local Sovereign Environment/pull/4664))
- **Nous OAuth access_token** no longer used as inference API key — @SHL0MS ([#5564](Local Sovereign Environment/pull/5564))
- **NIA_PORTAL_BASE_URL env var** respected during Nous login — @benbarclay ([#5745](Local Sovereign Environment/pull/5745))
- **Env var overrides** for Nous portal/inference URLs ([#5419](Local Sovereign Environment/pull/5419))
- **Z.AI endpoint auto-detect** via probe and cache ([#5763](Local Sovereign Environment/pull/5763))
- **MiniMax context lengths, model catalog, thinking guard, aux model, and config base_url** corrections ([#6082](Local Sovereign Environment/pull/6082))
- **Community provider/model resolution fixes** — salvaged 4 community PRs + MiniMax aux URL ([#5983](Local Sovereign Environment/pull/5983))

### Agent Loop & Conversation
- **Self-optimized GPT/Codex tool-use guidance** via automated behavioral benchmarking — agent self-diagnosed and patched 5 failure modes ([#6120](Local Sovereign Environment/pull/6120))
- **GPT/Codex execution discipline guidance** in system prompts ([#5414](Local Sovereign Environment/pull/5414))
- **Thinking-only prefill continuation** for structured reasoning responses ([#5931](Local Sovereign Environment/pull/5931))
- **Accept reasoning-only responses** without retries — set content to "(empty)" instead of infinite retry ([#5278](Local Sovereign Environment/pull/5278))
- **Jittered retry backoff** — exponential backoff with jitter for API retries ([#6048](Local Sovereign Environment/pull/6048))
- **Smart thinking block signature management** — preserve and manage Anthropic thinking signatures across turns ([#6112](Local Sovereign Environment/pull/6112))
- **Coerce tool call arguments** to match JSON Schema types — fixes models that send strings instead of numbers/booleans ([#5265](Local Sovereign Environment/pull/5265))
- **Save oversized tool results to file** instead of destructive truncation ([#5210](Local Sovereign Environment/pull/5210))
- **Sandbox-aware tool result persistence** ([#6085](Local Sovereign Environment/pull/6085))
- **Streaming fallback** improved after edit failures ([#6110](Local Sovereign Environment/pull/6110))
- **Codex empty-output gaps** covered in fallback + normalizer + auxiliary client ([#5724](Local Sovereign Environment/pull/5724), [#5730](Local Sovereign Environment/pull/5730), [#5734](Local Sovereign Environment/pull/5734))
- **Codex stream output backfill** from output_item.done events ([#5689](Local Sovereign Environment/pull/5689))
- **Stream consumer creates new message** after tool boundaries ([#5739](Local Sovereign Environment/pull/5739))
- **Codex validation aligned** with normalization for empty stream output ([#5940](Local Sovereign Environment/pull/5940))
- **Bridge tool-calls** in copilot-acp adapter ([#5460](Local Sovereign Environment/pull/5460))
- **Filter transcript-only roles** from chat-completions payload ([#4880](Local Sovereign Environment/pull/4880))
- **Context compaction failures fixed** on temperature-restricted models — @MadKangYu ([#5608](Local Sovereign Environment/pull/5608))
- **Sanitize tool_calls for all strict APIs** (Fireworks, Mistral, etc.) — @lumethegreat ([#5183](Local Sovereign Environment/pull/5183))

### Memory & Sessions
- **Supermemory memory provider** — new memory plugin with multi-container, search_mode, identity template, and env var override ([#5737](Local Sovereign Environment/pull/5737), [#5933](Local Sovereign Environment/pull/5933))
- **Shared thread sessions** by default — multi-user thread support across gateway platforms ([#5391](Local Sovereign Environment/pull/5391))
- **Subagent sessions linked to parent** and hidden from session list ([#5309](Local Sovereign Environment/pull/5309))
- **Profile-scoped memory isolation** and clone support ([#4845](Local Sovereign Environment/pull/4845))
- **Thread gateway user_id to memory plugins** for per-user scoping ([#5895](Local Sovereign Environment/pull/5895))
- **Honcho plugin drift overhaul** + plugin CLI registration system ([#5295](Local Sovereign Environment/pull/5295))
- **Honcho holographic prompt and trust score** rendering preserved ([#4872](Local Sovereign Environment/pull/4872))
- **Honcho doctor fix** — use recall_mode instead of memory_mode — @techguysimon ([#5645](Local Sovereign Environment/pull/5645))
- **RetainDB** — API routes, write queue, dialectic, agent model, file tools fixes ([#5461](Local Sovereign Environment/pull/5461))
- **Hindsight memory plugin overhaul** + memory setup wizard fixes ([#5094](Local Sovereign Environment/pull/5094))
- **mem0 API v2 compat**, prefetch context fencing, secret redaction ([#5423](Local Sovereign Environment/pull/5423))
- **mem0 env vars merged** with mem0.json instead of either/or ([#4939](Local Sovereign Environment/pull/4939))
- **Clean user message** used for all memory provider operations ([#4940](Local Sovereign Environment/pull/4940))
- **Silent memory flush failure** on /new and /resume fixed — @ryanautomated ([#5640](Local Sovereign Environment/pull/5640))
- **OpenViking atexit safety net** for session commit ([#5664](Local Sovereign Environment/pull/5664))
- **OpenViking tenant-scoping headers** for multi-tenant servers ([#4936](Local Sovereign Environment/pull/4936))
- **ByteRover brv query** runs synchronously before LLM call ([#4831](Local Sovereign Environment/pull/4831))

---

## 📱 Messaging Platforms (Gateway)

### Gateway Core
- **Inactivity-based agent timeout** — replaces wall-clock timeout with smart activity tracking; long-running active tasks never killed ([#5389](Local Sovereign Environment/pull/5389))
- **Approval buttons for Slack & Telegram** + Slack thread context preservation ([#5890](Local Sovereign Environment/pull/5890))
- **Live-stream /update output** + forward interactive prompts to user ([#5180](Local Sovereign Environment/pull/5180))
- **Infinite timeout support** + periodic notifications + actionable error messages ([#4959](Local Sovereign Environment/pull/4959))
- **Duplicate message prevention** — gateway dedup + partial stream guard ([#4878](Local Sovereign Environment/pull/4878))
- **Webhook delivery_info persistence** + full session id in /status ([#5942](Local Sovereign Environment/pull/5942))
- **Tool preview truncation** respects tool_preview_length in all/new progress modes ([#5937](Local Sovereign Environment/pull/5937))
- **Short preview truncation** restored for all/new tool progress modes ([#4935](Local Sovereign Environment/pull/4935))
- **Update-pending state** written atomically to prevent corruption ([#4923](Local Sovereign Environment/pull/4923))
- **Approval session key isolated** per turn ([#4884](Local Sovereign Environment/pull/4884))
- **Active-session guard bypass** for /approve, /deny, /stop, /new ([#4926](Local Sovereign Environment/pull/4926), [#5765](Local Sovereign Environment/pull/5765))
- **Typing indicator paused** during approval waits ([#5893](Local Sovereign Environment/pull/5893))
- **Caption check** uses exact line-by-line match instead of substring (all platforms) ([#5939](Local Sovereign Environment/pull/5939))
- **MEDIA: tags stripped** from streamed gateway messages ([#5152](Local Sovereign Environment/pull/5152))
- **MEDIA: tags extracted** from cron delivery before sending ([#5598](Local Sovereign Environment/pull/5598))
- **Profile-aware service units** + voice transcription cleanup ([#5972](Local Sovereign Environment/pull/5972))
- **Thread-safe PairingStore** with atomic writes — @CharlieKerfoot ([#5656](Local Sovereign Environment/pull/5656))
- **Sanitize media URLs** in base platform logs — @WAXLYY ([#5631](Local Sovereign Environment/pull/5631))
- **Reduce Telegram fallback IP activation log noise** — @MadKangYu ([#5615](Local Sovereign Environment/pull/5615))
- **Cron static method wrappers** to prevent self-binding ([#5299](Local Sovereign Environment/pull/5299))
- **Stale 'nia login' replaced** with 'nia auth' + credential removal re-seeding fix ([#5670](Local Sovereign Environment/pull/5670))

### Telegram
- **Group topics skill binding** for supergroup forum topics ([#4886](Local Sovereign Environment/pull/4886))
- **Emoji reactions** for approval status and notifications ([#5975](Local Sovereign Environment/pull/5975))
- **Duplicate message delivery prevented** on send timeout ([#5153](Local Sovereign Environment/pull/5153))
- **Command names sanitized** to strip invalid characters ([#5596](Local Sovereign Environment/pull/5596))
- **Per-platform disabled skills** respected in Telegram menu and gateway dispatch ([#4799](Local Sovereign Environment/pull/4799))
- **/approve and /deny** routed through running-agent guard ([#4798](Local Sovereign Environment/pull/4798))

### Discord
- **Channel controls** — ignored_channels and no_thread_channels config options ([#5975](Local Sovereign Environment/pull/5975))
- **Skills registered as native slash commands** via shared gateway logic ([#5603](Local Sovereign Environment/pull/5603))
- **/approve, /deny, /queue, /background, /btw** registered as native slash commands ([#4800](Local Sovereign Environment/pull/4800), [#5477](Local Sovereign Environment/pull/5477))
- **Unnecessary members intent** removed on startup + token lock leak fix ([#5302](Local Sovereign Environment/pull/5302))

### Slack
- **Thread engagement** — auto-respond in bot-started and mentioned threads ([#5897](Local Sovereign Environment/pull/5897))
- **mrkdwn in edit_message** + thread replies without @mentions ([#5733](Local Sovereign Environment/pull/5733))

### Matrix
- **Tier 1 feature parity** — reactions, read receipts, rich formatting, room management ([#5275](Local Sovereign Environment/pull/5275))
- **MATRIX_REQUIRE_MENTION and MATRIX_AUTO_THREAD** support ([#5106](Local Sovereign Environment/pull/5106))
- **Comprehensive reliability** — encrypted media, auth recovery, cron E2EE, Synapse compat ([#5271](Local Sovereign Environment/pull/5271))
- **CJK input, E2EE, and reconnect** fixes ([#5665](Local Sovereign Environment/pull/5665))

### Signal
- **Full MEDIA: tag delivery** — send_image_file, send_voice, and send_video implemented ([#5602](Local Sovereign Environment/pull/5602))

### Mattermost
- **File attachments** — set message type to DOCUMENT when post has file attachments — @nericervin ([#5609](Local Sovereign Environment/pull/5609))

### Feishu
- **Interactive card approval buttons** ([#6043](Local Sovereign Environment/pull/6043))
- **Reconnect and ACL** fixes ([#5665](Local Sovereign Environment/pull/5665))

### Webhooks
- **`{__raw__}` template token** and thread_id passthrough for forum topics ([#5662](Local Sovereign Environment/pull/5662))

---

## 🖥️ CLI & User Experience

### Interactive CLI
- **Defer response content** until reasoning block completes ([#5773](Local Sovereign Environment/pull/5773))
- **Ghost status-bar lines cleared** on terminal resize ([#4960](Local Sovereign Environment/pull/4960))
- **Normalise \r\n and \r line endings** in pasted text ([#4849](Local Sovereign Environment/pull/4849))
- **ChatConsole errors, curses scroll, skin-aware banner, git state** banner fixes ([#5974](Local Sovereign Environment/pull/5974))
- **Native Windows image paste** support ([#5917](Local Sovereign Environment/pull/5917))
- **--yolo and other flags** no longer silently dropped when placed before 'chat' subcommand ([#5145](Local Sovereign Environment/pull/5145))

### Setup & Configuration
- **Config structure validation** — detect malformed YAML at startup with actionable error messages ([#5426](Local Sovereign Environment/pull/5426))
- **Centralized logging** to `~/.nia/logs/` — agent.log (INFO+), errors.log (WARNING+) with `nia logs` command ([#5430](Local Sovereign Environment/pull/5430))
- **Docs links added** to setup wizard sections ([#5283](Local Sovereign Environment/pull/5283))
- **Doctor diagnostics** — sync provider checks, config migration, WAL and mem0 diagnostics ([#5077](Local Sovereign Environment/pull/5077))
- **Timeout debug logging** and user-facing diagnostics improved ([#5370](Local Sovereign Environment/pull/5370))
- **Reasoning effort unified** to config.yaml only ([#6118](Local Sovereign Environment/pull/6118))
- **Permanent command allowlist** loaded on startup ([#5076](Local Sovereign Environment/pull/5076))
- **`nia auth remove`** now clears env-seeded credentials permanently ([#5285](Local Sovereign Environment/pull/5285))
- **Bundled skills synced to all profiles** during update ([#5795](Local Sovereign Environment/pull/5795))
- **`nia update` no longer kills** freshly-restarted gateway service ([#5448](Local Sovereign Environment/pull/5448))
- **Subprocess.run() timeouts** added to all gateway CLI commands ([#5424](Local Sovereign Environment/pull/5424))
- **Actionable error message** when Codex refresh token is reused — @tymrtn ([#5612](Local Sovereign Environment/pull/5612))
- **Google-workspace skill scripts** can now run directly — @xinbenlv ([#5624](Local Sovereign Environment/pull/5624))

### Cron System
- **Inactivity-based cron timeout** — replaces wall-clock; active tasks run indefinitely ([#5440](Local Sovereign Environment/pull/5440))
- **Pre-run script injection** for data collection and change detection ([#5082](Local Sovereign Environment/pull/5082))
- **Delivery failure tracking** in job status ([#6042](Local Sovereign Environment/pull/6042))
- **Delivery guidance** in cron prompts — stops send_message thrashing ([#5444](Local Sovereign Environment/pull/5444))
- **MEDIA files delivered** as native platform attachments ([#5921](Local Sovereign Environment/pull/5921))
- **[SILENT] suppression** works anywhere in response — @auspic7 ([#5654](Local Sovereign Environment/pull/5654))
- **Cron path traversal** hardening ([#5147](Local Sovereign Environment/pull/5147))

---

## 🔧 Tool System

### Terminal & Execution
- **Execute_code on remote backends** — code execution now works on Docker, SSH, Modal, and other remote terminal backends ([#5088](Local Sovereign Environment/pull/5088))
- **Exit code context** for common CLI tools in terminal results — helps agent understand what went wrong ([#5144](Local Sovereign Environment/pull/5144))
- **Progressive subdirectory hint discovery** — agent learns project structure as it navigates ([#5291](Local Sovereign Environment/pull/5291))
- **notify_on_complete for background processes** — get notified when long-running tasks finish ([#5779](Local Sovereign Environment/pull/5779))
- **Docker env config** — explicit container environment variables via docker_env config ([#4738](Local Sovereign Environment/pull/4738))
- **Approval metadata included** in terminal tool results ([#5141](Local Sovereign Environment/pull/5141))
- **Workdir parameter sanitized** in terminal tool across all backends ([#5629](Local Sovereign Environment/pull/5629))
- **Detached process crash recovery** state corrected ([#6101](Local Sovereign Environment/pull/6101))
- **Agent-browser paths with spaces** preserved — @Vasanthdev2004 ([#6077](Local Sovereign Environment/pull/6077))
- **Portable base64 encoding** for image reading on macOS — @CharlieKerfoot ([#5657](Local Sovereign Environment/pull/5657))

### Browser
- **Switch managed browser provider** from Browserbase to Browser Use — @benbarclay ([#5750](Local Sovereign Environment/pull/5750))
- **Firecrawl cloud browser** provider — @alt-glitch ([#5628](Local Sovereign Environment/pull/5628))
- **JS evaluation** via browser_console expression parameter ([#5303](Local Sovereign Environment/pull/5303))
- **Windows browser** fixes ([#5665](Local Sovereign Environment/pull/5665))

### MCP
- **MCP OAuth 2.1 PKCE** — full standards-compliant OAuth client support ([#5420](Local Sovereign Environment/pull/5420))
- **OSV malware check** for MCP extension packages ([#5305](Local Sovereign Environment/pull/5305))
- **Prefer structuredContent over text** + no_mcp sentinel ([#5979](Local Sovereign Environment/pull/5979))
- **Unknown toolsets warning suppressed** for MCP server names ([#5279](Local Sovereign Environment/pull/5279))

### Web & Files
- **.zip document support** + auto-mount cache dirs into remote backends ([#4846](Local Sovereign Environment/pull/4846))
- **Redact query secrets** in send_message errors — @WAXLYY ([#5650](Local Sovereign Environment/pull/5650))

### Delegation
- **Credential pool sharing** + workspace path hints for subagents ([#5748](Local Sovereign Environment/pull/5748))

### ACP (VS Code / Zed / JetBrains)
- **Aggregate ACP improvements** — auth compat, protocol fixes, command ads, delegation, SSE events ([#5292](Local Sovereign Environment/pull/5292))

---

## 🧩 Skills Ecosystem

### Skills System
- **Skill config interface** — skills can declare required config.yaml settings, prompted during setup, injected at load time ([#5635](Local Sovereign Environment/pull/5635))
- **Plugin CLI registration system** — plugins register their own CLI subcommands without touching main.py ([#5295](Local Sovereign Environment/pull/5295))
- **Request-scoped API hooks** with tool call correlation IDs for plugins ([#5427](Local Sovereign Environment/pull/5427))
- **Session lifecycle hooks** — on_session_finalize and on_session_reset for CLI + gateway ([#6129](Local Sovereign Environment/pull/6129))
- **Prompt for required env vars** during plugin install — @kshitijk4poor ([#5470](Local Sovereign Environment/pull/5470))
- **Plugin name validation** — reject names that resolve to plugins root ([#5368](Local Sovereign Environment/pull/5368))
- **pre_llm_call plugin context** moved to user message to preserve prompt cache ([#5146](Local Sovereign Environment/pull/5146))

### New & Updated Skills
- **popular-web-designs** — 54 production website design systems ([#5194](Local Sovereign Environment/pull/5194))
- **p5js creative coding** — @SHL0MS ([#5600](Local Sovereign Environment/pull/5600))
- **manim-video** — mathematical and technical animations — @SHL0MS ([#4930](Local Sovereign Environment/pull/4930))
- **llm-wiki** — Karpathy's LLM Wiki skill ([#5635](Local Sovereign Environment/pull/5635))
- **gitnexus-explorer** — codebase indexing and knowledge serving ([#5208](Local Sovereign Environment/pull/5208))
- **research-paper-writing** — AI-Scientist & GPT-Researcher patterns — @SHL0MS ([#5421](Local Sovereign Environment/pull/5421))
- **blogwatcher** updated to JulienTant's fork ([#5759](Local Sovereign Environment/pull/5759))
- **claude-code skill** comprehensive rewrite v2.0 + v2.2 ([#5155](Local Sovereign Environment/pull/5155), [#5158](Local Sovereign Environment/pull/5158))
- **Code verification skills** consolidated into one ([#4854](Local Sovereign Environment/pull/4854))
- **Manim CE reference docs** expanded — geometry, animations, LaTeX — @leotrs ([#5791](Local Sovereign Environment/pull/5791))
- **Manim-video references** — design thinking, updaters, paper explainer, decorations, production quality — @SHL0MS ([#5588](Local Sovereign Environment/pull/5588), [#5408](Local Sovereign Environment/pull/5408))

---

## 🔒 Security & Reliability

### Security Hardening
- **Consolidated security** — SSRF protections, timing attack mitigations, tar traversal prevention, credential leakage guards ([#5944](Local Sovereign Environment/pull/5944))
- **Cross-session isolation** + cron path traversal hardening ([#5613](Local Sovereign Environment/pull/5613))
- **Workdir parameter sanitized** in terminal tool across all backends ([#5629](Local Sovereign Environment/pull/5629))
- **Approval 'once' session escalation** prevented + cron delivery platform validation ([#5280](Local Sovereign Environment/pull/5280))
- **Profile-scoped Google Workspace OAuth tokens** protected ([#4910](Local Sovereign Environment/pull/4910))

### Reliability
- **Aggressive worktree and branch cleanup** to prevent accumulation ([#6134](Local Sovereign Environment/pull/6134))
- **O(n²) catastrophic backtracking** in redact regex fixed — 100x improvement on large outputs ([#4962](Local Sovereign Environment/pull/4962))
- **Runtime stability fixes** across core, web, delegate, and browser tools ([#4843](Local Sovereign Environment/pull/4843))
- **API server streaming fix** + conversation history support ([#5977](Local Sovereign Environment/pull/5977))
- **OpenViking API endpoint paths** and response parsing corrected ([#5078](Local Sovereign Environment/pull/5078))

---

## 🐛 Notable Bug Fixes

- **9 community bugfixes salvaged** — gateway, cron, deps, macOS launchd in one batch ([#5288](Local Sovereign Environment/pull/5288))
- **Batch core bug fixes** — model config, session reset, alias fallback, launchctl, delegation, atomic writes ([#5630](Local Sovereign Environment/pull/5630))
- **Batch gateway/platform fixes** — matrix E2EE, CJK input, Windows browser, Feishu reconnect + ACL ([#5665](Local Sovereign Environment/pull/5665))
- **Stale test skips removed**, regex backtracking, file search bug, and test flakiness ([#4969](Local Sovereign Environment/pull/4969))
- **Nix flake** — read version, regen uv.lock, add nia_logging — @alt-glitch ([#5651](Local Sovereign Environment/pull/5651))
- **Lowercase variable redaction** regression tests ([#5185](Local Sovereign Environment/pull/5185))

---

## 🧪 Testing

- **57 failing CI tests repaired** across 14 files ([#5823](Local Sovereign Environment/pull/5823))
- **Test suite re-architecture** + CI failure fixes — @alt-glitch ([#5946](Local Sovereign Environment/pull/5946))
- **Codebase-wide lint cleanup** — unused imports, dead code, and inefficient patterns ([#5821](Local Sovereign Environment/pull/5821))
- **browser_close tool removed** — auto-cleanup handles it ([#5792](Local Sovereign Environment/pull/5792))

---

## 📚 Documentation

- **Comprehensive documentation audit** — fix stale info, expand thin pages, add depth ([#5393](Local Sovereign Environment/pull/5393))
- **40+ discrepancies fixed** between documentation and codebase ([#5818](Local Sovereign Environment/pull/5818))
- **13 features documented** from last week's PRs ([#5815](Local Sovereign Environment/pull/5815))
- **Guides section overhaul** — fix existing + add 3 new tutorials ([#5735](Local Sovereign Environment/pull/5735))
- **Salvaged 4 docs PRs** — docker setup, post-update validation, local LLM guide, signal-cli install ([#5727](Local Sovereign Environment/pull/5727))
- **Discord configuration reference** ([#5386](Local Sovereign Environment/pull/5386))
- **Community FAQ entries** for common workflows and troubleshooting ([#4797](Local Sovereign Environment/pull/4797))
- **WSL2 networking guide** for local model servers ([#5616](Local Sovereign Environment/pull/5616))
- **Honcho CLI reference** + plugin CLI registration docs ([#5308](Local Sovereign Environment/pull/5308))
- **Obsidian Headless setup** for servers in llm-wiki ([#5660](Local Sovereign Environment/pull/5660))
- **NIA Mod visual skin editor** added to skins page ([#6095](Local Sovereign Environment/pull/6095))

---

## 👥 Contributors

### Core
- **@teknium1** — 179 PRs

### Top Community Contributors
- **@SHL0MS** (7 PRs) — p5js creative coding skill, manim-video skill + 5 reference expansions, research-paper-writing, Nous OAuth fix, manim font fix
- **@alt-glitch** (3 PRs) — Firecrawl cloud browser provider, test re-architecture + CI fixes, Nix flake fixes
- **@benbarclay** (2 PRs) — Browser Use managed provider switch, Nous portal base URL fix
- **@CharlieKerfoot** (2 PRs) — macOS portable base64 encoding, thread-safe PairingStore
- **@WAXLYY** (2 PRs) — send_message secret redaction, gateway media URL sanitization
- **@MadKangYu** (2 PRs) — Telegram log noise reduction, context compaction fix for temperature-restricted models

### All Contributors
@alt-glitch, @austinpickett, @auspic7, @benbarclay, @CharlieKerfoot, @GratefulDave, @kshitijk4poor, @leotrs, @lumethegreat, @MadKangYu, @nericervin, @ryanautomated, @SHL0MS, @techguysimon, @tymrtn, @Vasanthdev2004, @WAXLYY, @xinbenlv

---

**Full Changelog**: [v2026.4.3...v2026.4.8](Local Sovereign Environment/compare/v2026.4.3...v2026.4.8)
