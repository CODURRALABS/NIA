"""
BrowserAgent: Automated web browsing using Playwright.
"""
import asyncio
import logging
import os
try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

logger = logging.getLogger("BrowserAgent")

class BrowserAgent:
    def __init__(self):
        self.browser = None
        self.page = None
        self._playwright = None

    async def _ensure_browser(self):
        if not async_playwright:
            logger.error("playwright not installed.")
            return False
        if not self.browser:
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
        return True

    async def navigate(self, url: str):
        if not await self._ensure_browser(): return False
        logger.info(f"Browsing to: {url}")
        await self.page.goto(url)
        return True

    async def search(self, query: str):
        url = f"https://www.google.com/search?q={query}"
        return await self.navigate(url)

    async def click(self, selector: str):
        if not self.page: return False
        logger.info(f"Clicking: {selector}")
        await self.page.click(selector)
        return True

    async def type(self, selector: str, text: str):
        if not self.page: return False
        logger.info(f"Typing '{text}' into {selector}")
        await self.page.fill(selector, text)
        await self.page.press(selector, "Enter")
        return True

    async def close(self):
        if self.browser:
            await self.browser.close()
            await self._playwright.stop()
            self.browser = self.page = self._playwright = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = BrowserAgent()
    async def test():
        await agent.navigate("https://www.google.com")
        await agent.type("input[name='q']", "Codurra Labs")
        await asyncio.sleep(5)
        await agent.close()
    asyncio.run(test())
