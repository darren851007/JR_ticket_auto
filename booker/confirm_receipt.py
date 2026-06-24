from playwright.async_api import Page
from booker.selectors import RECEIPT_INFO
from utils.logger import get_logger

logger = get_logger("confirm_receipt")


async def confirm_receipt(page: Page, config: dict) -> None:
    logger.info("Waiting for receipt information page...")
    await page.locator(RECEIPT_INFO["page_anchor"]).wait_for(state="visible", timeout=0)
    logger.info("Receipt information page loaded — clicking Next")
    await page.locator(RECEIPT_INFO["confirm_button"]).click()
    await page.wait_for_load_state("domcontentloaded")
    logger.info("Receipt information confirmed")
