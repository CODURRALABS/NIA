"""
VisionModule implementation for NIA, inspired by bytedance/UI-TARS.
Handles screenshot capture and coordinate mapping for UI grounding.
"""
import pyautogui
import numpy as np
from PIL import Image, ImageChops
import os

class VisionModule:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        
    def capture_viewport(self) -> Image.Image:
        """Captures the current screen."""
        screenshot = pyautogui.screenshot()
        # print(f"[Vision] Captured viewport ({self.screen_width}x{self.screen_height})")
        return screenshot
        
    def map_coordinate(self, logical_x: float, logical_y: float) -> tuple[int, int]:
        """Maps logical coordinates (0.0 to 1.0) to physical screen coordinates."""
        # Ensure we stay within bounds
        lx = max(0.0, min(1.0, logical_x))
        ly = max(0.0, min(1.0, logical_y))
        physical_x = int(lx * (self.screen_width - 1))
        physical_y = int(ly * (self.screen_height - 1))
        return physical_x, physical_y

    def get_pixel_diff(self, img1: Image.Image, img2: Image.Image) -> float:
        """
        Calculates the percentage of different pixels between two images.
        Useful for verifying if a UI action caused a visual change.
        """
        if img1.size != img2.size:
            return 100.0
            
        diff = ImageChops.difference(img1, img2)
        # Convert to grayscale to get a single band of diff
        diff = diff.convert("L")
        # Get statistics: how many pixels are non-zero (changed)
        stat = np.array(diff)
        changed_pixels = np.count_nonzero(stat > 5) # Threshold of 5 to ignore tiny noise
        total_pixels = img1.size[0] * img1.size[1]
        
        return (changed_pixels / total_pixels) * 100.0

    def perform_click(self, x: int, y: int, action_desc: str):
        """Executes a click at the given physical coordinates."""
        print(f"[Vision] Triggering click at ({x}, {y}): {action_desc}")
        # In actual deployment, pyautogui.click(x, y) would be called here.
        
if __name__ == "__main__":
    vision = VisionModule()
    img = vision.capture_viewport()
    px, py = vision.map_coordinate(0.5, 0.5) # Center
    vision.perform_click(px, py, "Clicking center of screen")
