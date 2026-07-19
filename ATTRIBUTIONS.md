# NIA — Open Source Attribution

NIA is built on top of outstanding open-source projects. We are grateful to their authors.

## Core Dependencies

| Project | Author | License | Used In | What We Took |
|---------|--------|---------|---------|--------------|
| [Nebulara](https://github.com/CODURRALABS/NEBULARA) | CODURRA Labs | Proprietary | `core/pulse/runtime/nebulara_bridge.py`, `nebulara_soul.py`, `tools/nebulara/` | Native scripting language — bytecode VM, transpiler, standard library |
| [OpenClaw / NIA-Agent](https://github.com/NousResearch/openclaw) | Nous Research | MIT | `core/agent/` (~3,828 files) | Agent framework, skills, transports, gateway |
| [Pipecat](https://github.com/pipecat-ai/pipecat) | Daily | BSD-2 | `core/agent/pipecat/` | Real-time voice pipeline, WebRTC transport |
| [Aceternity UI](https://ui.aceternity.com/) | Aceternity | MIT | `components/ui/sidebar.tsx` | Sidebar component (verified copy) |
| [OpenManus](https://github.com/OpenManus/OpenManus) | OpenManus | MIT | `core/pulse/planning/openmanus_planner.py` | Planning loop pattern |
| [Mem0](https://github.com/mem0ai/mem0) | Mem0 Labs | Apache 2.0 | `core/pulse/memory/` | Cross-session memory plugins |
| [Honcho](https://github.com/plastic-labs/honcho) | Plastic Labs | MIT | `core/pulse/runtime/` | Persona engine pattern |
| [Hindsight](https://github.com/hindsight-ai/hindsight) | Hindsight AI | MIT | `core/pulse/memories/` | Reflection memory pattern |
| [Holographic](https://github.com/holographic-ai/holographic) | Holographic AI | MIT | `core/pulse/memories/` | Holographic memory pattern |
| [ByteRover](https://github.com/biterover/ByteRover) | ByteRover | MIT | `core/pulse/agents/` | Browser action patterns |
| [OpenCode](https://github.com/opencode-ai/opencode) | OpenCode | MIT | `core/pulse/runtime/` | CLI interface patterns |
| [vLLM](https://github.com/vllm-project/vllm) | vLLM Project | Apache 2.0 | `requirements.txt` | Model serving backend |
| [LiveKit](https://github.com/livekit/livekit) | LiveKit | BSD-2 | `requirements.txt` | Voice infrastructure |
| [LangChain](https://github.com/langchain-ai/langchain) | LangChain | MIT | `requirements.txt` | Agent patterns |

## Additional Tools (Integrated or Planned)

| Project | Author | License | Purpose |
|---------|--------|---------|---------|
| [Kimi Code CLI](https://github.com/MoonshotAI/kimi-code) | MoonshotAI | MIT | Coding agent (CLI) |
| [Browser-Use](https://github.com/browser-use/browser-use) | Browser Use | MIT | Vision-based web automation |
| [LangGraph](https://github.com/langchain-ai/langgraph) | LangChain | MIT | Orchestration / state machines |
| [Composio](https://github.com/ComposioHQ/composio) | Composio | MIT | 200+ tool integrations |
| [Firecrawl](https://github.com/firecrawl/firecrawl) | Firecrawl | AGPL-3.0 (server), MIT (SDK) | Web scraping / data extraction |
| [CUA](https://github.com/trycua/cua) | TryCua | MIT | Sandboxed computer use |
| [Open Interpreter](https://github.com/OpenInterpreter/open-interpreter) | Open Interpreter | Apache 2.0 | Sandboxed code execution |
| [VibeVoice](https://github.com/microsoft/VibeVoice) | Microsoft | MIT | ASR / TTS models |

## License Compliance

All borrowed code is used under its original license. Where required, license headers have been added to individual files. This attribution file serves as the comprehensive record of all open-source dependencies.

If you are an author of any included project and would like changes, please open an issue.
