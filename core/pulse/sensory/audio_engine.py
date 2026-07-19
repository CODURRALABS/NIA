"""
AudioEngine: NIA's 'Ears'.
Handles ambient audio monitoring, VAD, and wake-word detection.
"""
import logging
import threading
import time
import speech_recognition as sr
try:
    from livekit.plugins import vad
except ImportError:
    vad = None

logger = logging.getLogger("AudioEngine")

class AudioEngine:
    def __init__(self, wake_word: str = "nia"):
        self.wake_word = wake_word.lower()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.stop_event = threading.Event()
        self.last_transcript = ""
        self.is_active = False # True when wake word detected

        # Adjust for ambient noise on startup
        with self.microphone as source:
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def start(self):
        """Starts the background listening thread."""
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("Audio Engine started. Listening ambiently...")

    def stop(self):
        self.stop_event.set()
        self.is_listening = False
        logger.info("Audio Engine stopped.")

    def _listen_loop(self):
        import whisper
        import numpy as np
        import sounddevice as sd
        from scipy.io.wavfile import write
        import io

        # Load a small, fast model for real-time
        model = whisper.load_model("base")
        logger.info("Whisper model loaded for real-time STT.")

        def callback(indata, frames, time, status):
            if status:
                logger.warning(status)
            if np.any(indata):
                # Simple energy-based VAD
                energy = np.linalg.norm(indata)
                if energy > 0.5: # Threshold
                    self.is_active = True

        while not self.stop_event.is_set():
            try:
                # Capture short chunks for low latency
                duration = 2 # seconds
                fs = 16000
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
                sd.wait()
                
                # Convert to format Whisper expects
                audio_data = recording.flatten().astype(np.float32)
                
                result = model.transcribe(audio_data, fp16=False)
                text = result["text"].lower().strip()
                
                if text:
                    logger.debug(f"STT: {text}")
                    if self.wake_word in text:
                        logger.info(f"WAKE WORD '{self.wake_word}' DETECTED!")
                        self.is_active = True
                        self.last_transcript = text.replace(self.wake_word, "").strip()
            except Exception as e:
                logger.error(f"Error in audio loop: {e}")
                time.sleep(1)

    def get_and_clear_active_state(self):
        """Checks if NIA was recently 'woken' and clears the flag."""
        if self.is_active:
            self.is_active = False
            return True, self.last_transcript
        return False, ""

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = AudioEngine()
    engine.start()
    try:
        while True:
            woken, text = engine.get_and_clear_active_state()
            if woken:
                print(f"I'm awake! You said: {text}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        engine.stop()
