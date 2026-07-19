import logging
from typing import Any

logger = logging.getLogger("SociusSoul")

class SociusSoul:
    """
    NIA Social Vibe Sensor.
    V17 - Dynamically switches between Silent and Audio alerts based on privacy needs.
    """
    def __init__(self, camera: Any, voice: Any, notify: Any):
        self.camera = camera
        self.voice = voice
        self.notify = notify
        print("[SENSORY]: Socius Soul active. Monitoring social environment...")

    def deliver_alert(self, message: str, emotion: str = "neutral"):
        """
        Deliver message via Audio if alone, or Notification if crowded.
        Boss's privacy is the primary goal.
        """
        # Get face count from CameraSoul
        faces = self.camera.get_face_count() if hasattr(self.camera, 'get_face_count') else 1
        
        if faces > 1:
            # Crowd detected - Silent notification
            self.notify.show_alert("Sovereign Update", message)
            logger.info(f"Socius: Crowd detected ({faces} faces). Delivering silent notification.")
        else:
            # Alone - Direct neural voice
            self.voice.speak(message)
            logger.info("Socius: Alone. Delivering audio response.")

    def get_vibe(self) -> str:
        """Analyzes the room mood via emotion averages."""
        # Future: Average the emotions of all faces detected
        return "Calm"
