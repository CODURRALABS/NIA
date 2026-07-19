# LIMITS_AND_RULES: The Sovereign Guardrails

## 1. Sovereign Rule #1: No Cloud Leaks
- No data, logs, or weights shall leave the local environment without Ayush-approval.
- All training must use `streaming=True` to minimize local disk footprint (Limit: 2GB cache).

## 2. Architectural Rule: Sparse-MoE Optimization
- The total parameter count must stay near **500M** (Current: 537M).
- The compiled binary must not exceed **1GB** (Targeting 4-bit TensorRT-LLM).

## 3. Communication Rule: The Gentleman
- The model must output logic in `<thought>` blocks before concluding.
- Responses must be precise, logical, and devoid of "AI assistant" fluff.

## 4. Deployment Rule: Aether Core First
- Native `torch.nn` only. No high-level wrappers that obscure the sovereign core logic.
- TensorRT 10.x compatibility is non-negotiable for low-latency kernel fusion.
