# NIA Technical Architecture

## 1. Engine: Sovereign Sparse-MoE
*   **Total Parameters:** ~536M.
*   **Layers:** 12 Transformer blocks.
*   **Attention:** Grouped Query Attention (GQA) with 16 Query heads and 4 KV heads (4:1 ratio).
*   **Positional Encoding:** Rotary Positional Embeddings (RoPE) initialized for 32k context.
*   **MoE Layer:** 8 specialized `SovereignExpert` modules per layer.
*   **Routing:** Top-2 Gating Network with load-balancing auxiliary loss.

## 2. Dimension Specifications
*   `d_model`: 1024
*   `d_ff`: 2048 (Expert internal dimension)
*   `num_heads`: 16
*   `num_kv_heads`: 4
*   `max_seq_len`: 32,768
*   `vocab_size`: 50,257

## 3. Sovereign Soul Architecture (DPMI)
NIA utilizes a **Deep Physics Mathematical Intelligence (DPMI)** bridge combined with **Vector Symbolic Architecture (VSA)** for deterministic reasoning.

### Key Components:
- **DPMI Bridge**: Interface to high-performance logic engines (Zig/Julia/Mojo).
- **VSA Engine**: Geometric reasoning space for absolute truth verification.
- **Recursive Thought Loop**: Refinement engine based on confidence and symmetry.
- **Linguistic Projection**: Claude-tier fluidity layer for natural expression.

## 4. Agentic Core (NIA-Agent)
The agentic framework handles tool execution, session persistence, and multi-platform communication.

### Core Structure:
- `core/agent/run_agent.py`: The `NIAAgent` class (Executive Loop).
- `core/agent/model_tools.py`: Tool orchestration and discovery.
- `core/agent/nia_state.py`: SQLite session store with FTS5 search.

## 5. Optimization & Deployment
- **Precision**: 4-bit inference for local velocity.
- **Kernel Fusion**: TensorRT 10.x `IMoELayer` compatibility.
- **Memory Management**: "RAM-Ninja" system to unload weights when idle (<100MB footprint).
