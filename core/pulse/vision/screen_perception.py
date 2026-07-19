"""
ScreenPerception: The 'Eyes' of NIA.
Handles VLM-based screen analysis and object detection.
"""
import logging
import os
from PIL import Image
from vision.vision_module import VisionModule

logger = logging.getLogger("ScreenPerception")

class ScreenPerception:
    def __init__(self):
        self.vision = VisionModule()
        self.last_analysis = {}

    def analyze_screen(self) -> dict:
        """
        Captures the screen and uses a VLM to identify UI elements and context.
        Returns a structured dictionary of detected objects.
        """
        logger.info("Analyzing viewport...")
        screenshot = self.vision.capture_viewport()
        
        visual_context = "Vision systems offline or obscured."
        
        gemini_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDUJdC_38CWkjxjppAMW7LwMr5H73OK18A")
        if gemini_key:
            try:
                from google import genai
                # Pass API key explicitly to avoid relying on global environment resolution issues
                client = genai.Client(api_key=gemini_key)
                logger.info("Triggering Gemini 1.5 Flash Vision Multimodal Analysis...")
                
                # Gemini natively accepts PIL Image objects in the contents array!
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[screenshot, "You are NIA, an advanced Operating Entity. Analyze this screenshot of the user's active screen. Provide a highly precise, concise 2-sentence summary of exactly what the user is currently looking at or doing."]
                )
                visual_context = response.text.strip()
                logger.info(f"VLM Success: {visual_context}")
            except Exception as e:
                logger.error(f"VLM Vision Pipeline Error: {e}")
        
        results = {
            "detected_elements": [
                {"label": "vlm_active", "box_2d": [0.0, 0.0, 1.0, 1.0], "text": "Multimodal Sight Active"}
            ],
            "visual_context": visual_context,
            "timestamp": getattr(self.vision, 'screen_width', 0)
        }
        
        self.last_analysis = results
        return results

    def find_element(self, query: str) -> dict:
        """Searches last analysis for a specific element matching the query."""
        for element in self.last_analysis.get("detected_elements", []):
            if query.lower() in element["label"].lower() or query.lower() in element.get("text", "").lower():
                return element
        return {}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    perception = ScreenPerception()
    analysis = perception.analyze_screen()
    print(f"Perceived Context: {analysis['visual_context']}")
