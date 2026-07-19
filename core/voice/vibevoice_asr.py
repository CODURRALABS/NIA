"""
NIA VibeVoice ASR — Long-Form Transcription
Microsoft VibeVoice-ASR for 60-minute single-pass transcription with speaker diarization.
Alternative to faster-whisper for long audio.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("VibeVoiceASR")


class NIAVibeVoiceASR:
    """
    Long-form ASR using Microsoft VibeVoice.
    Handles up to 60 minutes of audio in a single pass with speaker labels.
    Requires: VibeVoice model files + GPU VRAM (7B params).
    """

    def __init__(self):
        self.model = None
        self.processor = None
        self._initialized = False
        self._device = "cuda" if _check_cuda() else "cpu"

    def initialize(self) -> bool:
        """Load the VibeVoice ASR model."""
        if self._initialized:
            return True

        try:
            from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

            model_id = "microsoft/VibeVoice-ASR"
            logger.info(f"Loading VibeVoice ASR model: {model_id}")

            self.processor = AutoProcessor.from_pretrained(model_id)
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype="auto",
                device_map=self._device
            )

            self._initialized = True
            logger.info(f"VibeVoice ASR loaded on {self._device}")
            return True
        except ImportError:
            logger.error("transformers not installed or VibeVoice model unavailable")
            return False
        except Exception as e:
            logger.error(f"VibeVoice ASR initialization failed: {e}")
            return False

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file with speaker diarization.
        
        Args:
            audio_path: Path to audio file (WAV, MP3, etc.)
        
        Returns:
            {"text": str, "speakers": bool, "duration": float, "success": bool}
        """
        if not self._initialized and not self.initialize():
            return {"error": "VibeVoice ASR not initialized", "success": False}

        try:
            import torch

            inputs = self.processor(audio_path, return_tensors="pt", sampling_rate=16000)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=8192
                )

            text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]

            return {
                "text": text,
                "speakers": True,
                "duration": len(text.split()) / 150,  # rough estimate
                "success": True
            }
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return {"error": str(e), "success": False}

    def is_available(self) -> bool:
        """Check if the model can be loaded."""
        return self._initialized or self.initialize()


def _check_cuda() -> bool:
    """Check if CUDA is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


_nia_vibevoice = NIAVibeVoiceASR()


def get_vibevoice_asr() -> NIAVibeVoiceASR:
    """Get the singleton VibeVoice ASR instance."""
    return _nia_vibevoice
