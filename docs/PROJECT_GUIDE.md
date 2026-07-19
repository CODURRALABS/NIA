# NIA Project Guide

Welcome to the unified NIA Sovereign workspace. The project has been restructured for professional organization and localized sovereignty.

## 1. Directory Structure

- `core/`: The unified backend engine.
    - `agent/`: The NIA-Agentic Core (Executive Soul). Responsible for tool use, sessions, and platforms.
    - `pulse/`: The NIA-Pulse Engine (Sovereign Soul). Responsible for VSA reasoning and DPMI logic.
        - `runtime/`: Core logic modules (thalamus, vsa, chat, etc.).
        - `vision/`: Screen perception and OCR.
- `docs/`: Unified documentation and vision.
- `models/`: Local weights for the NIA-Core models.
- `app/`: Next.js frontend (Sovereign Hub).

## 2. Key Components

### 2.1 Aether-Soul (Transformer Model)
The primary reasoning model located in `models/nia-core`. It provides high-velocity linguistic capabilities.

### 2.2 Sovereign-Pulse (DPMI/VSA Engine)
The deterministic logic engine located in `core/pulse/runtime`. It ensures absolute mathematical precision and truth verification.

## 3. Getting Started

To launch the entire system:
```powershell
node nia-bootstrap.mjs
```

## 4. Sovereignty Protocols
- **Local-First**: All reasoning happens on-device. Cloud failovers are enabled as fallback only.
- **Zero-Telemetry**: No data leaves the device without explicit Boss approval.
- **Self-Healing**: The Immune Soul monitors and repairs core logic leaks.
