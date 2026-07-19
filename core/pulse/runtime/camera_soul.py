import os
import time
import threading
import logging
import cv2
from typing import Any

logger = logging.getLogger("CameraSoul")

class CameraSoul:
    """
    The 'Face' of the User for NIA.
    V13.5 (Emotive Integration) - Facial Recognition & Emotional Sync.
    """
    def __init__(self, thalamus: Any = None):
        self.vsa = thalamus
        self.ready = False
        self.cap = None
        self.current_user_emotion = "Neutral"
        self.face_count = 1
        self._monitoring = False
        
        try:
            # Check if camera 0 is available
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.ready = True
                print("[SENSORY]: Camera Soul ignited. User Recognition Active.")
            else:
                print("[SENSORY]: Camera not found. User Recognition Disabled.")
        except Exception as e:
            print(f"[SENSORY]: Camera initialization failed: {e}")

    def get_user_emotion(self) -> str:
        """
        Processes a single frame to detect user emotion via DeepFace.
        Uses threading to avoid blocking the reasoning core.
        """
        if not self.ready:
            return "Unknown (Camera Offline)"

        def _analyze():
            try:
                from deepface import DeepFace
                ret, frame = self.cap.read()
                if ret:
                    # GPT-5 Precision: Rapid facial analysis
                    results = DeepFace.analyze(
                        frame, 
                        actions=['emotion'], 
                        enforce_detection=False,
                        detector_backend='opencv',
                        silent=True
                    )
                    
                    if results:
                        # DeepFace returns a list of results
                        self.current_user_emotion = results[0]['dominant_emotion']
                        self.face_count = len(results)
                        if self.vsa:
                            self.vsa.update_sensory_mesh("mood", self.current_user_emotion)
                            self.vsa.update_sensory_mesh("faces", str(self.face_count))
            except Exception:
                pass # Silently fail to maintain stability

        threading.Thread(target=_analyze, daemon=True).start()
        return self.current_user_emotion

    def get_face_count(self) -> int:
        """Returns the number of people detected in the last frame (V17)."""
        return self.face_count

    def close(self):
        if self.cap:
            self.cap.release()

if __name__ == "__main__":
    cam = CameraSoul()
    if cam.ready:
        print(f"Current User Emotion: {cam.get_user_emotion()}")
        time.sleep(2)
        print(f"Current User Emotion: {cam.get_user_emotion()}")
        cam.close()
