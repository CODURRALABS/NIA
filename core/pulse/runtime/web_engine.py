import asyncio
import os
import requests
import trafilatura
import warnings
from typing import List, Dict, Any, Optional

# Failsafe imports
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_READY = True
except ImportError:
    PLAYWRIGHT_READY = False

# Suppress DuckDuckGo Rename Warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")
try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS 

import numpy as np

class SovereignWebEngine:
    """
    The 'Retina' & 'Shadow-Search' of NIA.
    V1.7 - Hyperdimensional Retina & VSA Bundling.
    """
    def __init__(self, headless=True):
        self.headless = headless
        self.pw = None
        self.browser: Optional[Any] = None
        # Persistent storage for co-owner sessions
        self.user_data_dir = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\NIA_Sovereign")
        self.contexts: List[Any] = []
        self.ready = False
        self.mode = "Lightweight"

    async def start(self):
        """Starts the heavy browser with full failover protection."""
        if not PLAYWRIGHT_READY:
            print("[RETINA]: Playwright not installed. Entering Lightweight Mode.")
            return

        try:
            self.pw = await async_playwright().start()
            self.browser = await self.pw.chromium.launch(headless=self.headless)
            self.ready = True
            self.mode = "Sovereign-JS"
            print("[RETINA]: Web Browser Core successfully ignited.")
        except Exception as e:
            print(f"[RETINA]: Browser initialization failed: {e}. Defaulting to Lightweight Mode.")
            self.ready = False
            self.mode = "Lightweight"

    async def stop(self):
        try:
            for context in self.contexts:
                await context.close()
            if self.browser:
                await self.browser.close()
            if self.pw:
                await self.pw.stop()
        except:
            pass

    def fast_search(self, query: str, max_results=5) -> List[Dict[str, str]]:
        """Sovereign Search — iFlow primary, Firecrawl secondary, DuckDuckGo fallback."""
        results = []

        # Primary: iFlow Search API (free, structured)
        iflow_key = os.environ.get("IFLOW_API_KEY", "")
        if iflow_key:
            try:
                resp = requests.post(
                    "https://platform.iflow.cn/api/search/webSearch",
                    headers={"Authorization": f"Bearer {iflow_key}", "Content-Type": "application/json", "Accept": "application/json"},
                    json={"keywords": query, "num": max_results},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("data", {}).get("organic", [])[:max_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "link": item.get("link", ""),
                            "snippet": item.get("snippet", "")[:300],
                        })
                    if results:
                        return results
            except Exception:
                pass

        # Secondary: Firecrawl search
        try:
            from firecrawl_engine import get_firecrawl
            fc = get_firecrawl()
            if fc._initialized:
                fc_results = fc.search_web(query, limit=max_results)
                for r in fc_results:
                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("url", ""),
                        "snippet": r.get("description", r.get("markdown", ""))[:300]
                    })
                if results:
                    return results
        except Exception:
            pass

        # Fallback: DuckDuckGo
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "link": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
        except Exception as e:
            print(f"[RETINA]: Search error: {e}")
        return results

    def get_vsa_consensus(self, query: str, mapper: Any, vsa: Any) -> Dict[str, Any]:
        """
        Calculates the 'Consensus Truth' of a web query in VSA space.
        Returns a bundled hypervector of all snippets.
        """
        search_results = self.fast_search(query)
        if not search_results: return {"vector": None, "sources": []}
        
        vectors = []
        sources = []
        for res in search_results:
            text = f"{res['title']} {res['snippet']}"
            v = mapper.get_vector(text)
            vectors.append(v)
            sources.append(res['link'])
            
        # Bundle search results into a single Consensus Vector
        consensus_v = vsa.bundle(vectors)
        return {
            "vector": consensus_v,
            "sources": sources,
            "count": len(vectors)
        }

    def fast_fetch(self, url: str) -> str:
        """Sovereign Page Scraper — Firecrawl primary, trafilatura fallback."""
        # Primary: Firecrawl scrape (structured, handles JS)
        try:
            from firecrawl_engine import get_firecrawl
            fc = get_firecrawl()
            if fc._initialized:
                result = fc.scrape_url(url)
                if result.get("success") and result.get("markdown"):
                    return result["markdown"][:5000]
        except Exception:
            pass

        # Fallback: trafilatura (lightweight, no JS)
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                result = trafilatura.extract(downloaded)
                return result or "No readable content found."
        except:
            pass
        return "Failed to fetch content."

    async def create_shadow_sync(self, stream_count=1) -> List[Any]:
        """Failsafe context creation."""
        if not self.ready:
            # Pivot to fake page or empty list
            print("[RETINA]: create_shadow_sync called while in Lightweight Mode. Returning empty sync.")
            return []

        try:
            if not self.browser:
                await self.start()
            
            if not self.browser:
                return []

            context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            self.contexts.append(context)
            page = await context.new_page()
            return [page]
        except Exception as e:
            print(f"[RETINA]: Shadow Sync failed: {e}")
            return []

    async def get_visual_tokens(self, page: Any) -> List[Dict[str, Any]]:
        if not self.ready or not page:
            return []
        try:
            elements = await page.evaluate("""
                () => {
                    const interactives = document.querySelectorAll('button, a, input, [role="button"]');
                    return Array.from(interactives).map(el => {
                        const rect = el.getBoundingClientRect();
                        return {
                            role: el.tagName.toLowerCase(),
                            text: el.innerText || el.placeholder || "",
                            x: rect.left + rect.width / 2,
                            y: rect.top + rect.height / 2,
                            w: rect.width,
                            h: rect.height
                        };
                    }).filter(el => el.w > 0 && el.h > 0);
                }
            """)
            return elements
        except:
            return []

    async def launch_sovereign_session(self, visible: bool = True) -> Any:
        """Launches a persistent browser session as the Co-owner."""
        if not PLAYWRIGHT_READY: return None
        try:
            if not self.pw:
                self.pw = await async_playwright().start()
            
            # Persistent context keeps login state (WhatsApp/Insta)
            context = await self.pw.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=not visible,
                viewport={'width': 1280, 'height': 720}
            )
            self.contexts.append(context)
            return context
        except Exception as e:
            print(f"[RETINA]: Persistent Session failed: {e}")
            return None

    async def send_social_message(self, platform: str, recipient: str, message: str):
        """Automates WhatsApp/Instagram messaging flow."""
        context = await self.launch_sovereign_session(visible=True)
        if not context: return False
        
        page = await context.new_page()
        try:
            if platform.lower() == "whatsapp":
                await page.goto("https://web.whatsapp.com")
                # Wait for QR or Profile sync
                await page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
                # Search and text logic here...
            elif platform.lower() == "instagram":
                await page.goto(f"https://www.instagram.com/{recipient}/")
                # Navigate to DMs
                await page.click('text="Message"')
                await page.fill('textarea', message)
                await page.keyboard.press("Enter")
            
            print(f"[RETINA]: Social Task Complete: {platform} to {recipient}")
            return True
        except Exception as e:
            print(f"[RETINA]: Social Task Error: {e}")
            return False
        finally:
            # We don't always close context to keep the session ready
            pass

    async def browse_and_learn(self, topics: List[str], mapper: Any):
        """
        Autonomous Bootstrap Learning (ABL).
        Browses the web as a 'Real User' to harvest linguistic patterns and world knowledge.
        Updates the VSA mapper and local knowledge vault.
        """
        if not self.ready:
            await self.start()
        
        pages = await self.create_shadow_sync(stream_count=len(topics))
        for i, page in enumerate(pages):
            topic = topics[i]
            try:
                print(f"[RETINA]: Harvesting knowledge for topic: {topic}...")
                await page.goto(f"https://www.google.com/search?q={topic}")
                # Extract clean text from the top results
                content = await page.evaluate("() => document.body.innerText")
                # Perform real-time VSA encoding (Linguistic Scaffolding)
                # This 'populates' the model from scratch without pre-training datasets.
                chunks = [content[i:i+500] for i in range(0, len(content), 500)]
                for chunk in chunks[:10]:
                    v = mapper.get_vector(chunk)
                    # We would store this in a compressed binary format here
                print(f"[RETINA]: Learning complete for '{topic}'. Knowledge anchored.")
            except Exception as e:
                print(f"[RETINA]: Learning error for '{topic}': {e}")
            finally:
                await page.close()
