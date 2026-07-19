import random
import asyncio
from playwright.async_api import Page

class SovereignShadowObfuscator:
    """
    The @SHADOW class for NIA.
    Generates "Human Entropy" to mathematically mimic human behavior and mask NIA.
    """
    async def generate_entropy(self, page: Page):
        """
        Performs random decoy interactions (scrolling, hovering).
        """
        # 1. Random Jittery Scroll
        scroll_amount = random.randint(100, 500)
        await page.mouse.wheel(0, scroll_amount)
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # 2. Random Mouse Jitter (Move to random spot)
        viewport = page.viewport_size
        if viewport:
            target_x = random.randint(0, viewport['width'])
            target_y = random.randint(0, viewport['height'])
            # Move with some 'human-like' delay
            await page.mouse.move(target_x, target_y, steps=random.randint(5, 15))
            
        # 3. Random Idle
        await asyncio.sleep(random.uniform(1.0, 3.0))

    async def simulate_human_reading(self, page: Page, duration_sec: float):
        """
        Simulates a human reading a page with slight scrolling.
        """
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < duration_sec:
            # Small scroll down
            await page.mouse.wheel(0, random.randint(20, 100))
            await asyncio.sleep(random.uniform(2.0, 5.0))
            # Small jitter
            await self.generate_entropy(page)
