"""
NIA VoiceEngine — Always-On Voice I/O
Edge-TTS for natural speech (free, no API key, 300+ voices).
Microphone listening for wake word + continuous input.
Replaces the incomplete Piper/Whisper setup in audio_soul.py.
"""

import os
import io
import asyncio
import logging
import threading
import tempfile
import wave
import json
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger("VoiceEngine")

# Best Edge-TTS voices for NIA's persona (warm, Indian English female)
NIA_VOICE = "en-IN-NeerjaNeural"
FALLBACK_VOICE = "en-US-JennyNeural"


class VoiceEngine:
    """
    NIA's voice I/O system.
    - TTS: Edge-TTS (300+ voices, free, natural quality)
    - STT: Microphone → WAV → faster-whisper (local) or HF API
    - Wake word: Always-on listening via sounddevice + VAD
    """

    def __init__(self):
        self._tts_ready = False
        self._stt_ready = False
        self._listening = False
        self._voice = NIA_VOICE
        self._on_speech: Optional[Callable] = None
        self._stop_event = threading.Event()
        self._temp_dir = tempfile.mkdtemp(prefix="nia_voice_")

    def initialize(self) -> Dict[str, bool]:
        """Initialize voice subsystems."""
        status = {"tts": False, "stt": False}

        # TTS: Edge-TTS (always works, no API key)
        try:
            import edge_tts
            self._tts_ready = True
            status["tts"] = True
            logger.info("VoiceEngine TTS ready (edge-tts, voice=%s)", self._voice)
        except ImportError:
            logger.warning("edge-tts not installed")

        # STT: Try faster-whisper (local, fast)
        try:
            from faster_whisper import WhisperModel
            self._stt_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            self._stt_ready = True
            status["stt"] = True
            logger.info("VoiceEngine STT ready (faster-whisper tiny.en)")
        except Exception:
            logger.info("STT fallback: will use HF API for transcription")
            self._stt_model = None

        return status

    async def speak(self, text: str, voice: str = None, save_path: str = None) -> Dict[str, Any]:
        """
        Convert text to speech using Edge-TTS.
        Plays audio directly and optionally saves to file.

        Args:
            text: Text to speak
            voice: Voice name (default: NIA's Indian English voice)
            save_path: Optional path to save audio file

        Returns:
            {"audio_path": str, "duration_ms": int, "success": bool}
        """
        if not self._tts_ready:
            return {"error": "TTS not initialized", "success": False}

        voice = voice or self._voice
        clean_text = text.split("<|thought|>")[-1].strip()
        clean_text = clean_text.replace("[NIA_RESEARCH]", "").replace("[FINAL_CTOR]", "")

        try:
            import edge_tts

            output_path = save_path or os.path.join(self._temp_dir, f"nia_speech_{id(text)}.mp3")

            communicate = edge_tts.Communicate(clean_text, voice)
            await communicate.save(output_path)

            # Play audio (Windows)
            try:
                os.startfile(output_path)
            except Exception:
                pass

            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            duration_ms = (file_size * 8) // (48)  # rough estimate for MP3

            return {
                "audio_path": output_path,
                "duration_ms": duration_ms,
                "voice": voice,
                "success": True
            }
        except Exception as e:
            logger.error("Edge-TTS failed: %s", e)
            return {"error": str(e), "success": False}

    def speak_sync(self, text: str, voice: str = None) -> bool:
        """Synchronous wrapper for speak()."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context, run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(asyncio.run, self.speak(text, voice)).result()
                return result.get("success", False)
            else:
                result = loop.run_until_complete(self.speak(text, voice))
                return result.get("success", False)
        except Exception:
            result = asyncio.run(self.speak(text, voice))
            return result.get("success", False)

    async def listen(self, duration_seconds: int = 5, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Record audio from microphone and transcribe.

        Args:
            duration_seconds: How long to record
            sample_rate: Audio sample rate

        Returns:
            {"text": str, "success": bool}
        """
        try:
            import sounddevice as sd
            import numpy as np

            logger.info("Recording %ds of audio...", duration_seconds)
            audio = sd.rec(int(duration_seconds * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
            sd.wait()

            # Save to WAV
            wav_path = os.path.join(self._temp_dir, "recording.wav")
            with wave.open(wav_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())

            return await self.transcribe(wav_path)

        except Exception as e:
            logger.error("Listen failed: %s", e)
            return {"error": str(e), "success": False}

    async def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.
        Uses faster-whisper (local) or falls back to HF API.
        """
        # Local: faster-whisper
        if self._stt_ready and self._stt_model:
            try:
                segments, info = self._stt_model.transcribe(audio_path)
                text = " ".join(seg.text.strip() for seg in segments)
                return {"text": text, "language": info.language, "backend": "whisper", "success": True}
            except Exception as e:
                logger.warning("Whisper transcription failed: %s", e)

        # Fallback: HF API (speech-to-text)
        try:
            from model_router import get_router
            router = get_router()
            if router._hf_token:
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                resp = __import__("requests").post(
                    "https://api-inference.huggingface.co/models/openai/whisper-large-v3",
                    headers={"Authorization": f"Bearer {router._hf_token}"},
                    data=audio_bytes,
                    timeout=30
                )
                if resp.status_code == 200:
                    return {"text": resp.json().get("text", ""), "backend": "hf_api", "success": True}
        except Exception:
            pass

        return {"error": "No STT backend available", "success": False}

    def start_always_listening(self, on_speech: Callable, wake_word: str = "nia"):
        """
        Start always-on microphone listening with wake word detection.
        Uses energy-based VAD (simple but effective).
        """
        self._on_speech = on_speech
        self._listening = True
        self._stop_event.clear()
        threading.Thread(
            target=self._listening_loop,
            args=(wake_word,),
            daemon=True
        ).start()
        logger.info("Always-on listening started (wake_word=%s)", wake_word)

    def _listening_loop(self, wake_word: str):
        """Background loop: listen → detect speech → transcribe → callback."""
        try:
            import sounddevice as sd
            import numpy as np
        except ImportError:
            logger.warning("sounddevice not installed. Always-on listening disabled.")
            return

        SAMPLE_RATE = 16000
        CHUNK_DURATION = 2  # seconds per chunk
        ENERGY_THRESHOLD = 500  # minimum energy to consider speech

        while not self._stop_event.is_set():
            try:
                # Record a chunk
                audio = sd.rec(
                    int(CHUNK_DURATION * SAMPLE_RATE),
                    samplerate=SAMPLE_RATE, channels=1, dtype='int16'
                )
                sd.wait()

                # Energy check (skip silence)
                energy = np.sqrt(np.mean(audio.astype(float) ** 2))
                if energy < ENERGY_THRESHOLD:
                    continue

                # Save and transcribe
                wav_path = os.path.join(self._temp_dir, "listen_chunk.wav")
                with wave.open(wav_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(SAMPLE_RATE)
                    wf.writeframes(audio.tobytes())

                result = asyncio.run(self.transcribe(wav_path))
                text = result.get("text", "").lower().strip()

                if not text:
                    continue

                # Wake word check
                if wake_word in text:
                    # Strip wake word and pass to handler
                    command = text.replace(wake_word, "").strip()
                    if command and self._on_speech:
                        logger.info("Wake word detected: '%s'", command)
                        threading.Thread(
                            target=lambda: asyncio.run(self._on_speech(command)),
                            daemon=True
                        ).start()
                elif self._on_speech:
                    # Pass all speech (always-on mode)
                    threading.Thread(
                        target=lambda: asyncio.run(self._on_speech(text)),
                        daemon=True
                    ).start()

            except Exception as e:
                logger.debug("Listening chunk error: %s", e)
                self._stop_event.wait(1)

    def stop_listening(self):
        """Stop always-on listening."""
        self._listening = False
        self._stop_event.set()
        logger.info("Always-on listening stopped.")

    def set_voice(self, voice: str):
        """Change TTS voice."""
        self._voice = voice
        logger.info("Voice changed to: %s", voice)

    async def list_voices(self, language: str = "en") -> list:
        """List available Edge-TTS voices."""
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return [v for v in voices if language in v.get("Locale", "").lower()]
        except Exception:
            return []


_nia_voice = VoiceEngine()


def get_voice() -> VoiceEngine:
    """Get the singleton VoiceEngine instance."""
    return _nia_voice
