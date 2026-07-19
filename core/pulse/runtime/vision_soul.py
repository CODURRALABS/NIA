import os
import time
import threading
import logging
from typing import Any

logger = logging.getLogger("VisionSoul")

class VisionSoul:
    """
    The 'Eyes' of NIA.
    V13.5 (100M Integrated) - Fail-Safe Perception & Coordinate Mapping.
    """
    def __init__(self, thalamus: Any = None, capture_interval=2.0):
        self.vsa = thalamus
        self.interval = capture_interval
        self.active = False
        self.ready = False
        self.screen_width = 1920 # Default, updated on start
        self.screen_height = 1080
        
        try:
            import pyautogui
            import pytesseract
            from PIL import Image
            self.pyautogui = pyautogui
            self.pytesseract = pytesseract
            self.Image = Image
            
            self.screen_width, self.screen_height = self.pyautogui.size()
            
            # 1. Attempt to find Tesseract Binary (Common Windows requirement)
            tess_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Users\Admin\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            for path in tess_paths:
                if os.path.exists(path):
                    self.pytesseract.pytesseract.tesseract_cmd = path
                    break
            
            self.ready = True
            print(f"[SENSORY]: Vision Module ignited. Resolution: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            print(f"[SENSORY]: Vision libraries issue: {e}. Eyes set to OFFLINE mode.")

    def capture_screen(self):
        """Captures the screen and extracts text context with coordinate metadata."""
        if not self.ready:
            return "VISION_STATUS: OFFLINE (Check local Tesseract installation)."

        try:
            screenshot = self.pyautogui.screenshot()
            # GPT-5 Precision: OCR + Location detection
            text_data = self.pytesseract.image_to_string(screenshot)
            
            self.last_view = text_data[:1000].replace("\n", " ").strip()
            if self.vsa:
                self.vsa.update_sensory_mesh("vision", f"Scanning: {self.last_view[:100]}...")
            return self.last_view if self.last_view else "Screen appears blank or dark."
        except Exception as e:
            return f"VISION_ERROR: {e}"

    def map_coordinate(self, x_ratio: float, y_ratio: float):
        """Maps 0.0-1.0 ratios to actual screen pixels for NIA's hands."""
        target_x = int(x_ratio * self.screen_width)
        target_y = int(y_ratio * self.screen_height)
        return target_x, target_y

    def get_current_view(self) -> str:
        return self.last_view if self.last_view else "Vision state: CALIBRATING."

if __name__ == "__main__":
    vision = VisionSoul()
    print(f"[Vision Test]: {vision.capture_screen()}")
