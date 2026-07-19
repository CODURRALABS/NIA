"""
NIA Browser-Use Node — Vision-Based Web Automation
Uses browser-use for LLM-driven browser interaction.
Firecrawl upgrade: scraping goes through Firecrawl first,
browser-use is reserved for interactive tasks (forms, clicks, JS-heavy).
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("BrowserUseNode")


class BrowserUseNode:
    """
    Unified web automation for NIA.
    - Static scraping: Firecrawl (fast, structured)
    - Interactive tasks: browser-use Agent (LLM-driven)
    Requires: browser-use pip package + Firecrawl (optional but preferred).
    """

    def __init__(self):
        self._initialized = False

    def initialize(self) -> bool:
        """Check if browser-use is available."""
        if self._initialized:
            return True

        try:
            import browser_use
            self._initialized = True
            logger.info("Browser-Use node initialized.")
            return True
        except ImportError:
            logger.error("browser-use not installed. Run: pip install browser-use")
            return False

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a URL. Routes to Firecrawl (fast) or browser-use (JS-heavy).
        """
        # Try Firecrawl first (fast, structured)
        try:
            from firecrawl_engine import get_firecrawl
            fc = get_firecrawl()
            if fc._initialized:
                result = fc.scrape_url(url)
                if result.get("success"):
                    return {
                        "url": url,
                        "content": result.get("markdown", ""),
                        "metadata": result.get("metadata", {}),
                        "backend": "firecrawl",
                        "success": True
                    }
        except Exception:
            pass

        # Fallback: browser-use (handles JS, SPAs)
        return await self.execute_web_task(
            f"Go to {url} and extract all visible text content"
        )

    async def search_and_extract(self, query: str, extract_from: str = None) -> Dict[str, Any]:
        """
        Search the web and extract results.
        If extract_from URL is given, scrape that page after searching.
        """
        # Search via Firecrawl
        try:
            from firecrawl_engine import get_firecrawl
            fc = get_firecrawl()
            if fc._initialized:
                results = fc.search_web(query, limit=5)
                if results:
                    output = {
                        "query": query,
                        "results": results,
                        "backend": "firecrawl",
                        "success": True
                    }
                    if extract_from:
                        scrape = fc.scrape_url(extract_from)
                        output["page_content"] = scrape.get("markdown", "")
                    return output
        except Exception:
            pass

        # Fallback: browser-use
        task = f"Search for '{query}' and extract the top results"
        return await self.execute_web_task(task)


_nia_browser_use = BrowserUseNode()


def get_browser_use() -> BrowserUseNode:
    """Get the singleton Browser-Use node instance."""
    return _nia_browser_use
