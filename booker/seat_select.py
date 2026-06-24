from playwright.async_api import Page
from booker.selectors import SEAT_SELECT
from utils.logger import get_logger

logger = get_logger("seat_select")


async def select_seat(page: Page, config: dict) -> None:
    logger.info("Waiting for seat selection page...")
    await page.locator(SEAT_SELECT["page_anchor"]).wait_for(state="visible", timeout=0)
    logger.info("Seat selection page loaded — confirming")
    await page.locator(SEAT_SELECT["confirm_button"]).click()
    await page.wait_for_load_state("domcontentloaded")
    logger.info("Seat selection confirmed")
