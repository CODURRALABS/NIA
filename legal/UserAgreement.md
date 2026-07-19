# NIA User Agreement (Data Sovereignty First)

**Effective Date:** 2026-03-01

Welcome to NIA. This document defines the terms under which you interact with the National Intelligent Agent. 

## 1. Sovereignty and Local-First Architecture
NIA is fundamentally different from cloud-based AI. It operates with a **Local-First Architecture**.
- Your data remains your property.
- The `agent-core` processes visual grounding and voice activity locally on your device.
- We do not possess the ability to access your local vector memory.

## 2. Multi-Agent Functionality
NIA operates using a multi-agent framework:
- **CodeAgent**: Has the authority to write and execute scripts locally to automate your tasks ("Vibe Coding"). By enabling this feature, you authorize NIA to modify local files in designated workspaces.
- **VisionModule**: Replicates human screen observation via coordinate mapping. Screenshots are ephemeral and pass instantly into local memory; they are never sent to external servers.
- **AmbientSession**: Operates voice activity detection (VAD). NIA will actively listen and may initiate conversation proactively (e.g., regarding system status or scheduled timers).

## 3. Assumption of Risk
Because NIA possesses high-agency execution capabilities (admin sovereignty mode), you retain ultimate responsibility for actions it takes on your behalf.
- Actions taken within banking, primary email, or system settings require explicit confirmation unless you bypass safe mode.
- Codurra Labs is not responsible for data loss resulting from user-authorized "Vibe Coding" scripts.

## 4. Governing Law
This agreement and all local processing protocols are governed strictly by the **Digital Personal Data Protection (DPDP) Act, 2023** of India, ensuring absolute protections of your digital footprint.
