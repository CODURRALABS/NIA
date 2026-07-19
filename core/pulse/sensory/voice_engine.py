"""
VoiceEngine: NIA's 'Mouth'.
Handles Text-to-Speech (TTS) using pyttsx3 or Sarvam AI.
"""
import logging
import threading
import pyttsx3
import os
import requests

logger = logging.getLogger("VoiceEngine")

class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.is_speaking = False
        self.sarvam_api_key = os.environ.get("SARVAM_API_KEY")
        
        # Configure local voice
        voices = self.engine.getProperty('voices')
        # Try to find a female/premium sounding voice if available
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        self.engine.setProperty('rate', 175) # Speaking speed
        self._lock = threading.Lock()

    def speak(self, text: str, use_sarvam: bool = True):
        """Speaks the text in a non-blocking thread."""
        if not text:
            return

        if use_sarvam and self.sarvam_api_key:
            threading.Thread(target=self._speak_sarvam, args=(text,), daemon=True).start()
        else:
            threading.Thread(target=self._speak_local, args=(text,), daemon=True).start()

    def _speak_local(self, text: str):
        with self._lock:
            try:
                self.is_speaking = True
                logger.info(f"Speaking (Local): {text}")
                
                # For basic pyttsx3, we chunk the text to handle interrupts between sentences
                sentences = text.split('.')
                for sentence in sentences:
                    if os.environ.get("STOP_SPEAKING") == "true":
                        logger.info("Speech interrupted.")
                        break
                    if sentence.strip():
                        self.engine.say(sentence)
                        self.engine.runAndWait()
            except Exception as e:
                logger.error(f"Local TTS Error: {e}")
            finally:
                self.is_speaking = False
                os.environ["STOP_SPEAKING"] = "false"

    def save_to_file(self, text: str, filename: str):
        """Saves text to a wav file."""
        with self._lock:
            try:
                logger.info(f"Saving to file: {filename}")
                self.engine.save_to_file(text, filename)
                self.engine.runAndWait()
                return True
            except Exception as e:
                logger.error(f"Save to file Error: {e}")
                return False

    def _speak_sarvam(self, text: str):
        """Sarvam AI TTS integration."""
        import base64
        import tempfile
        import time
        try:
            import winsound
        except ImportError:
            winsound = None

        try:
            self.is_speaking = True
            logger.info(f"Speaking (Sarvam): {text}")
            
            payload = {
                "inputs": [text],
                "target_language_code": "hi-IN",
                "speaker": "ritu",
                "pace": 1.1,
                "enable_preprocessing": True,
                "model": "bulbul:v3"
            }
            
            headers = {
                "api-subscription-key": self.sarvam_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://api.sarvam.ai/text-to-speech", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            audios = data.get("audios", [])
            audio_content = data.get("audio_content")
            b64_audio = audio_content if audio_content else (audios[0] if audios else None)
            
            if b64_audio and winsound:
                wav_bytes = base64.b64decode(b64_audio)
                temp_path = os.path.join(tempfile.gettempdir(), f"nia_sarvam_{int(time.time())}.wav")
                with open(temp_path, "wb") as f:
                    f.write(wav_bytes)
                
                winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            else:
                if not winsound:
                    logger.error("winsound not available (Not on Windows). Falling back to local.")
                else:
                    logger.error("No audio content in Sarvam response.")
                self._speak_local(text)
                
        except Exception as e:
            logger.error(f"Sarvam TTS Error: {e}, falling back to local")
            self._speak_local(text)
        finally:
            self.is_speaking = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ve = VoiceEngine()
    ve.speak("Sovereign Core online. Hello, I am NIA.")
    import time
    time.sleep(5)
