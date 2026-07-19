# Privacy Policy — NIA (Sovereign Operations)

**Effective Date:** 2026-03-01 | **Compliant with:** DPDP Act (India, 2023)

---

## 1. Our Commitment: Total Screen & Voice Privacy
Unlike legacy assistants, NIA uses a **Local-First** multi-agent architecture. 

**CRITICAL POLICY STATEMENT:** 
> Screen data (captured by our UI-TARS inspired VisionModule) and ambient audio (captured via LiveKit VAD nodes) **never leave the local machine.** All perceptual data is processed in RAM and destroyed immediately after context extraction.

## 2. How Your Data is Handled

### Visual Grounding (VisionModule)
When you ask NIA to perform GUI automation, it takes rapid screenshots to calculate `(x,y)` coordinate mapping for cursor control. These image blobs are processed locally through lightweight vision models and are impossible to export or retrieve after the action is completed.

### Ambient Audio (AmbientSession)
NIA's VAD (Voice Activity Detection) runs locally. Audio is only converted to text upon detecting intentional speech directed at the system. No continuous audio streams are ever uploaded to the cloud.

### Sovereign Memory Storage
Long-term context, user preferences, and PRD insights are stored using an encrypted vector database (`SovereignMemory`).
- Data is encrypted at rest using **AES-256** binary blobs.
- The encryption key is generated and stored locally on your device.
- Even if the SQLite/JSON local files are extracted, they cannot be read without your local device credentials.

## 3. Telemetry (Opt-In Only)
By default, NIA sends 0 bytes of telemetry data. If you opt-in to help improve crash reporting, we only collect generic stack traces devoid of any personal or visual context.
