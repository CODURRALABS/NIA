"""
AmbientSession implementation for NIA, inspired by livekit/agents.
Handles Voice Activity Detection (VAD) and proactive speaking logic.
"""
import time
import random

class AmbientSession:
    def __init__(self):
        self.is_listening = True
        self.vad_active = False
        
    def monitor_ambient_audio(self):
        """Simulates VAD listening in the background."""
        print("[Audio] Ambient VAD listening initialized.")
        while self.is_listening:
            # Simulate silence -> speech detection
            time.sleep(2)
            if random.random() > 0.8:
                self.vad_active = True
                print("[Audio] Voice Activity Detected (VAD triggered). Routing to STT.")
                self.vad_active = False
            else:
                print("[Audio] Monitoring...")
                
    def proactive_speak(self, event_type: str):
        """NIA speaks autonomously based on system events."""
        if event_type == "storage_low":
            msg = "System storage is dropping below optimal levels. Would you like me to clean up temp files?"
        elif event_type == "timer_end":
            msg = "Your study timer has ended. Taking a 5 minute break is recommended."
        else:
            msg = "I have an update for you."
            
        print(f"[Audio] Proactive TTS: '{msg}'")

if __name__ == "__main__":
    session = AmbientSession()
    session.proactive_speak("timer_end")
