import asyncio
from playwright.async_api import Page
from booker.selectors import TICKET_TYPE_SELECT
from utils.logger import get_logger

logger = get_logger("ticket_type_select")


async def select_ticket_type(page: Page, config: dict) -> None:
    ticket_type = config["ticket_type"]

    logger.info("Waiting for ticket type selection page...")
    await page.locator(TICKET_TYPE_SELECT["page_anchor"]).wait_for(state="visible", timeout=0)

    if ticket_type == "regular":
        logger.info("Selecting regular ticket")
        await asyncio.sleep(0.1)
        await page.locator(TICKET_TYPE_SELECT["regular"]).click()
        await page.wait_for_load_state("domcontentloaded")
        logger.info("Regular ticket selected")
    elif ticket_type == "e_ticket":
        raise NotImplementedError("e-ticket flow is not yet implemented")
    else:
        raise ValueError(f"Unknown ticket_type: {ticket_type!r}. Expected 'regular' or 'e_ticket'.")
