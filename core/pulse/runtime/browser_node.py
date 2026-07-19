import os
import sys
import logging
from typing import Optional, Dict, Any

# Configure Sovereign Logging
logging.basicConfig(level=logging.INFO, format="[SOVEREIGN BROWSER]: %(message)s")

try:
    import trafilatura
except ImportError:
    logging.warning("'trafilatura' not found. Rule-based refinement will be limited.")
    trafilatura = None

class SovereignBrowserNode:
    """
    Sovereign Browser Node for NIA.
    Provides high-velocity, refined web access for the Live-Knowledge Bridge.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NIA/Sovereign-Core"
        }

    def browse(self, url: str) -> Dict[str, Any]:
        """
        Fetch and refine content from a URL.
        """
        logging.info(f"Accessing URL: {url}")
        
        try:
            # Phase 1: Raw Retrieval
            import requests
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            raw_html = response.text
            
            # Phase 2: Refined Rule-Based Cleaning
            if trafilatura:
                # trafilatura is world-class for rule-based extraction
                refined_text = trafilatura.extract(raw_html, include_comments=False, include_tables=True)
            else:
                # Basic cleaning fallback
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(raw_html, "html.parser")
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                refined_text = soup.get_text(separator="\n", strip=True)
            
            # Phase 3: Knowledge Synthesis Readiness
            return {
                "url": url,
                "status": "SUCCESS",
                "content": refined_text or "No refined content extracted.",
                "length": len(refined_text) if refined_text else 0
            }
            
        except Exception as e:
            logging.error(f"Access failed: {e}")
            return {
                "url": url,
                "status": "FAILED",
                "error": str(e)
            }

    def clear_data(self, content: str) -> str:
        """
        Secondary refinement to remove noise before model injection.
        """
        if not content:
            return ""
        # Rule-based noise filtering (e.g. repetitive links, cookie notices)
        lines = content.split("\n")
        cleaned_lines = [l.strip() for l in lines if len(l.strip()) > 20] # Filter out short noise
        return "\n".join(cleaned_lines)

if __name__ == "__main__":
    # Test Node
    node = SovereignBrowserNode()
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    result = node.browse(test_url)
    print(f"\n--- BROWSER NODE TEST ---")
    print(f"URL: {result['url']}")
    print(f"Status: {result['status']}")
    if result["status"] == "SUCCESS":
        print(f"Extracted Length: {result['length']}")
        print(f"Snippet: {result['content'][:500]}...")
    print("--- END TEST ---\n")
