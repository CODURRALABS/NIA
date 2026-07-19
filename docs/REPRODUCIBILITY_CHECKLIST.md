# NIA Reproducibility Checklist (Cold Start)

To run the NIA Hybrid Sovereign Architecture on a new machine, follow these steps to ensure all "Souls" are functional.

## 1. Environment & Dependencies
- [ ] **Python 3.10+**: Required for `torch` and `transformers`.
- [ ] **Node.js 18+**: Required for the Next.js frontend.
- [ ] **Tesseract OCR**: 
  - Install via: `winget install UB-Mannheim.TesseractOCR`
  - Verify path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- [ ] **Git (Optional)**: While NIA is sovereign, Git is used for initial cloning.

## 2. Dependency Installation
```powershell
# Python Backend
pip install -r requirements.txt

# Next.js Frontend
npm install
```

## 3. Model Assets
Ensure the following directory exists and contains the model tensors:
- [ ] `models/nia-core/` (Target: 500M parameter GQA/MoE)

## 4. Verification Tests
Run the following scripts in order to verify system integrity:
1. `python scratch/test_model.py`: Verifies linguistic generation.
2. `python scratch/benchmark.py`: Measures system performance and latency.
3. `node nia-bootstrap.mjs`: Launches the full integrated ecosystem.

## 5. Troubleshooting
- **Vision Offline**: Ensure Tesseract is in the system PATH or correctly set in `core/pulse/runtime/vision_soul.py`.
- **DPMI Bridge Failure**: Check `nerve_bridge.py` for correct NumPy version compatibility.
- **Next.js Build Errors**: Delete `.next/` folder and run `npm run build` manually.

***
*Status: Reproducibility Verified.*
