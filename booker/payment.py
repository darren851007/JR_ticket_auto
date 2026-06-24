from playwright.async_api import Page
from booker.selectors import PAYMENT
from utils.logger import get_logger

logger = get_logger("payment")

CARD_TYPE_VALUES = {
    "VISA":         "0",
    "Master":       "1",
    "JCB":          "2",
    "AMEX":         "3",
    "VIEW":         "4",
    "Diners":       "5",
    "VIEW Company": "6",
}


async def fill_payment(page: Page, config: dict) -> None:
    pay = config["payment"]

    logger.info("Waiting for payment page...")
    await page.locator(PAYMENT["page_anchor"]).wait_for(state="visible", timeout=0)

    logger.info("Filling card number")
    await page.locator(PAYMENT["card_number"]).fill(pay["card_number"])

    card_value = CARD_TYPE_VALUES.get(pay["card_type"])
    if card_value is None:
        raise ValueError(f"Unknown card_type: {pay['card_type']!r}. Expected one of {list(CARD_TYPE_VALUES)}")
    logger.info(f"Selecting card type: {pay['card_type']}")
    await page.locator(PAYMENT["card_type"]).select_option(card_value)

    logger.info(f"Selecting expiry: {pay['expiry_month']}/20{pay['expiry_year']}")
    await page.locator(PAYMENT["expiry_month"]).select_option(pay["expiry_month"])
    await page.locator(PAYMENT["expiry_year"]).fill(pay["expiry_year"])

    logger.info("Filling security code")
    await page.locator(PAYMENT["security_code"]).fill(pay["security_code"])

    logger.info("Clicking Reserve now — purchase will be submitted")
    await page.locator(PAYMENT["submit_button"]).click()
    await page.wait_for_load_state("domcontentloaded")
    logger.info("Purchase submitted")
