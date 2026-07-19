"""
CameraModule: Accesses the system camera for user-facing vision.
Handles frame capture and streaming.
"""
import cv2
import logging
import base64
import time

logger = logging.getLogger("CameraModule")

class CameraModule:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None

    def _ensure_cap(self):
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error("Could not open camera.")
                return False
        return True

    def capture_frame(self):
        """Captures a single frame and returns it as a cv2 image."""
        if not self._ensure_cap():
            return None
        
        # Flush buffers to get fresh frame
        for _ in range(5):
            self.cap.read()
            
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to capture frame.")
            return None
        return frame

    def capture_base64(self, quality: int = 80):
        """Captures a frame and returns a base64 encoded JPEG string."""
        frame = self.capture_frame()
        if frame is None:
            return None
            
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        b64_str = base64.b64encode(buffer).decode('utf-8')
        return b64_str

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cam = CameraModule()
    print("Capturing test frame...")
    img_b64 = cam.capture_base64()
    if img_b64:
        print(f"Captured JPEG (Base64 length: {len(img_b64)})")
    cam.release()
