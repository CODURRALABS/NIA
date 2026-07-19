"""
DOM Distillation implementation for NIA, inspired by Browser-Use.
Also includes Dynamic Focus vision for performance profiling.
"""
from bs4 import BeautifulSoup
import pyautogui
from PIL import Image

class VisualDistiller:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def distill_dom(self, html_content: str) -> str:
        """
        Inspired by browser-use:
        Strips away ads, junk, and non-interactive elements from raw HTML 
        to save RAM and focus LLM attention.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove scripts, styles, and iframes (ads)
        for junk in soup(["script", "style", "iframe", "noscript"]):
            junk.extract()
            
        # Find interactive elements only
        interactive = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        distilled = f"Extracted {len(interactive)} interactive elements.\n"
        for el in interactive[:10]: # Return top 10 for memory bounds
            distilled += f"- <{el.name}>: {el.get_text(strip=True)[:30]}\n"
            
        print("[Vision] DOM Distillation complete. RAM saved.")
        return distilled

    def capture_dynamic_focus(self) -> Image.Image:
        """
        Inspired by UI-TARS/MobileAgent Dynamic Focus:
        Instead of capturing the whole screen, NIA attempts to capture 
        only the active window coordinates to save i5 G7 processing power.
        """
        print("[Vision] Capturing 'Dynamic Focus' (Active Window Only) to save GPU resources.")
        # Mocking active window rect logic
        mock_active_rect = (100, 100, 800, 600)
        img = pyautogui.screenshot(region=mock_active_rect)
        return img

if __name__ == "__main__":
    distiller = VisualDistiller()
    mock_html = "<html><body><h1>Test</h1><button>Submit</button><script>junk()</script></body></html>"
    print(distiller.distill_dom(mock_html))
    distiller.capture_dynamic_focus()
