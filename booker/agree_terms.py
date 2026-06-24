from playwright.async_api import Page
from booker.selectors import AGREEMENT
from utils.logger import get_logger

logger = get_logger("agree_terms")


async def agree_terms(page: Page, config: dict) -> None:
    logger.info("Waiting for service agreement page...")
    await page.locator(AGREEMENT["page_anchor"]).wait_for(state="visible", timeout=0)
    logger.info("Checking 'I agree' checkbox")
    await page.locator(AGREEMENT["checkbox_label"]).click()
    logger.info("Clicking Next")
    await page.locator(AGREEMENT["confirm_button"]).click()
    await page.wait_for_load_state("domcontentloaded")
    logger.info("Agreement confirmed")
