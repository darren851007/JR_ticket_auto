import os
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.async_api import async_playwright, Browser, Page
from utils.logger import get_logger

logger = get_logger("browser")
JST = ZoneInfo("Asia/Tokyo")

class BrowserManager:
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self, headless: bool = False) -> tuple[Browser, Page]:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()
        logger.info("Browser launched")
        return self._browser, page

    async def screenshot(self, page: Page, label: str) -> str:
        os.makedirs("screenshots", exist_ok=True)
        ts = datetime.now(tz=JST).strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{ts}_{label}.png"
        await page.screenshot(path=path)
        logger.info(f"Screenshot saved: {path}")
        return path

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed")
