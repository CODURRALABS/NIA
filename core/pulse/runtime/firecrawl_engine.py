"""
NIA Firecrawl Engine — Web Scraping & Data Extraction
Wraps firecrawl-py for structured web data extraction.
Replaces trafilatura for high-value scraping tasks.
"""

import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("FirecrawlEngine")


class NIAFirecrawlEngine:
    """
    Firecrawl-powered web scraping engine for NIA.
    Supports: scrape (single URL), search, crawl (full site), structured extraction.
    Requires: FIRECRAWL_API_KEY env var, or self-hosted instance via FIRECRAWL_URL.
    """

    def __init__(self):
        self.app = None
        self._initialized = False

    def initialize(self) -> bool:
        """Lazy-initialize the Firecrawl client."""
        if self._initialized:
            return True

        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            logger.warning("FIRECRAWL_API_KEY not set. Firecrawl engine unavailable.")
            return False

        try:
            from firecrawl import Firecrawl
            base_url = os.environ.get("FIRECRAWL_BASE_URL")
            if base_url:
                self.app = Firecrawl(api_key=api_key, api_url=base_url)
                logger.info(f"Firecrawl engine initialized with custom URL: {base_url}")
            else:
                self.app = Firecrawl(api_key=api_key)
                logger.info("Firecrawl engine initialized (default URL).")
            self._initialized = True
            return True
        except ImportError:
            logger.error("firecrawl-py not installed. Run: pip install firecrawl-py")
            return False
        except Exception as e:
            logger.error(f"Firecrawl initialization failed: {e}")
            return False

    def scrape_url(self, url: str, formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape a single URL and return content.
        Returns: {"url": str, "markdown": str, "html": str, "metadata": dict}
        """
        if not self._initialized and not self.initialize():
            return {"error": "Firecrawl not initialized"}

        try:
            formats = formats or ["markdown"]
            doc = self.app.scrape(url, formats=formats)
            return {
                "url": url,
                "markdown": getattr(doc, "markdown", ""),
                "html": getattr(doc, "html", ""),
                "metadata": getattr(doc, "metadata", {}),
                "success": True
            }
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            return {"url": url, "error": str(e), "success": False}

    def search_web(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web and return structured results.
        Returns: [{"url": str, "title": str, "markdown": str, "description": str}]
        """
        if not self._initialized and not self.initialize():
            return []

        try:
            results = self.app.search(query, limit=limit)
            return [
                {
                    "url": r.get("url", ""),
                    "title": r.get("title", ""),
                    "markdown": r.get("markdown", ""),
                    "description": r.get("description", "")
                }
                for r in (results.get("data", []) if isinstance(results, dict) else [])
            ]
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []

    def crawl_site(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Crawl an entire site and return all pages.
        Returns: list of page dicts with url, markdown, metadata.
        """
        if not self._initialized and not self.initialize():
            return []

        try:
            results = self.app.crawl(url, limit=limit)
            return [
                {
                    "url": page.get("url", ""),
                    "markdown": page.get("markdown", ""),
                    "metadata": page.get("metadata", {})
                }
                for page in (results.get("data", []) if isinstance(results, dict) else [])
            ]
        except Exception as e:
            logger.error(f"Crawl failed for {url}: {e}")
            return []

    def extract_structured(self, urls: List[str], schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Use Firecrawl's AI agent to extract structured data from URLs.
        Returns: extracted data dict.
        """
        if not self._initialized and not self.initialize():
            return {"error": "Firecrawl not initialized"}

        try:
            prompt = "Extract all relevant information from these pages"
            if schema:
                prompt += f" in this structure: {schema}"

            result = self.app.agent(urls=urls, prompt=prompt)
            return {
                "data": result.data if hasattr(result, "data") else result,
                "success": True
            }
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            return {"error": str(e), "success": False}


_nia_firecrawl = NIAFirecrawlEngine()


def get_firecrawl() -> NIAFirecrawlEngine:
    """Get the singleton Firecrawl engine instance."""
    return _nia_firecrawl
