# Mem0 Memory Provider

Server-side LLM fact extraction with semantic search, reranking, and automatic deduplication.

## Requirements

- `pip install mem0ai`
- Mem0 API key from [app.mem0.ai](https://app.mem0.ai)

## Setup

```bash
nia memory setup    # select "mem0"
```

Or manually:
```bash
nia config set memory.provider mem0
echo "MEM0_API_KEY=your-key" >> ~/.nia/.env
```

## Config

Config file: `$NIA_HOME/mem0.json`

| Key | Default | Description |
|-----|---------|-------------|
| `user_id` | `nia-user` | User identifier on Mem0 |
| `agent_id` | `nia` | Agent identifier |
| `rerank` | `true` | Enable reranking for recall |

## Tools

| Tool | Description |
|------|-------------|
| `mem0_profile` | All stored memories about the user |
| `mem0_search` | Semantic search with optional reranking |
| `mem0_conclude` | Store a fact verbatim (no LLM extraction) |
