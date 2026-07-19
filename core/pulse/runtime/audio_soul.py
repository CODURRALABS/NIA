import threading
import queue
import logging
import time
import os

logger = logging.getLogger("AudioSoul")

class AudioSoul:
    """
    The 'Voice & Ears' of NIA.
    V13.5 (500M Integrated) - Full-Duplex Emotive Audio System.
    """
    def __init__(self, rate=190, volume=1.0):
        self.ready = False
        self.engine = None
        self.stt_model = None
        self.last_user_tone = "Neutral"
        
        # 1. Initialize Neural TTS (Vocal Patterns)
        try:
            from piper import PiperVoice
            import sounddevice as sd
            import numpy as np
            
            # Path to Neural Seed (Amy - Low for CPU speed)
            model_path = os.path.join("agent-core", "models", "voice", "en_US-amy-low.onnx")
            config_path = model_path + ".json"
            
            if os.path.exists(model_path):
                self.voice_engine = PiperVoice.load(model_path, config_path=config_path)
                print(f"[SENSORY]: Neural Female Persona ignited: Amy (ONNX)")
                self.ready = True
            else:
                print(f"[SENSORY]: Neural voice model missing at {model_path}")
                self.ready = False
        except Exception as e:
            print(f"[SENSORY]: Neural TTS Initialization issue: {e}")
            self.ready = False

        # 2. Attempt Faster-Whisper Initialization (Local STT Core)
        try:
            from faster_whisper import WhisperModel
            # Use 'tiny.en' for local speed on 500M hardware constraints
            print("[SENSORY]: Calibrating Local Hearing (Faster-Whisper)...")
            # self.stt_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            # print("[SENSORY]: Hearing Calibrated.")
        except Exception:
            print("[SENSORY]: Hearing module offline (Missing faster-whisper).")

    def _apply_mood_cadence(self, mood: str):
        """Placeholder: Piper handles cadence via text prosody or model parameters."""
        pass

    def speak(self, text: str, mood: str = "Neutral"):
        """Asynchronous neural speech synthesis."""
        if not self.ready or not self.voice_engine:
            return

        def _vocal_synthesis():
            try:
                import numpy as np
                import sounddevice as sd
                
                # Clean text of any thought tags before speaking
                clean_text = text.split("<|thought|>")[-1].strip()
                clean_text = clean_text.replace("[NIA_RESEARCH]", "").replace("[FINAL_CTOR]", "").replace("[NIA_EXPLANATION]", "")
                
                # Stream synthesis to audio device
                with sd.OutputStream(samplerate=self.voice_engine.config.sample_rate, channels=1, dtype='int16') as stream:
                    for audio_item in self.voice_engine.synthesize(clean_text):
                        # Handle both raw bytes and AudioChunk objects (Piper/Sherpa/SiliconFlow)
                        if hasattr(audio_item, 'audio'):
                            audio_data_bytes = audio_item.audio
                        elif hasattr(audio_item, 'samples'):
                            audio_data_bytes = audio_item.samples
                        else:
                            audio_data_bytes = audio_item
                            
                        audio_data = np.frombuffer(audio_data_bytes, dtype='int16')
                        stream.write(audio_data)
                        
            except Exception as e:
                print(f"[SENSORY]: Neural Vocal synthesis error: {e}")
        
        threading.Thread(target=_vocal_synthesis, daemon=True).start()

    def transcribe_live(self, audio_chunk):
        """Processes real-time audio into text context."""
        if not self.stt_model:
            return None
        
        # Actual implementation links to sounddevice stream
        # segments, info = self.stt_model.transcribe(audio_chunk, beam_size=1)
        # return "".join([s.text for s in segments])
        return ""

    def analyze_tone(self, text_context: str) -> str:
        """
        Simple 100M Audio Core logic:
        Infer user tone from punctuation and keyword density.
        """
        if any(word in text_context.lower() for word in ["hey", "wow", "great"]):
            self.last_user_tone = "Happy / Enthusiastic"
        elif any(word in text_context.lower() for word in ["wait", "stop", "no"]):
            self.last_user_tone = "Urgent / Frustrated"
        else:
            self.last_user_tone = "Calm"
            
        return self.last_user_tone

    def stop(self):
        if self.ready and self.engine:
            try:
                self.engine.stop()
            except:
                pass

if __name__ == "__main__":
    audio = AudioSoul()
    audio.speak("Hearing and Speech protocols active, Boss.")
