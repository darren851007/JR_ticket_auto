import asyncio
from playwright.async_api import Page
from booker.selectors import LOGIN
from utils.logger import get_logger

logger = get_logger("login")
LOGIN_URL = "https://www.eki-net.com/en/jreast-train-reservation/Top/Index"

async def login(page: Page, config: dict) -> None:
    logger.info("Navigating to eki-net login page")
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")

    logger.info("Waiting for login form — please click 'Log in' in the browser")
    await page.locator(LOGIN["email_input"]).wait_for(state="visible", timeout=0)
    logger.info("Login form detected, filling credentials")
    await page.locator(LOGIN["email_input"]).first.fill(config["account"]["email"])
    await page.locator(LOGIN["password_input"]).first.fill(config["account"]["password"])
    await page.locator(LOGIN["submit_button"]).first.click()
    await page.wait_for_load_state("domcontentloaded")

    logger.info("Waiting for 'Purchase tickets' button to confirm login...")
    await page.locator(LOGIN["logged_in_indicator"]).first.wait_for(state="visible", timeout=0)
    logger.info("Login successful")
    await asyncio.sleep(0.5)
    await page.locator(LOGIN["logged_in_indicator"]).first.click()
    logger.info("Clicked 'Purchase tickets'")

    logger.info("Waiting for Route Search page to load...")
    await page.locator(LOGIN["route_search_page"]).wait_for(state="visible", timeout=0)
    logger.info("Route Search page loaded — ready to proceed")
    await asyncio.sleep(0.5)
    await page.locator(LOGIN["route_search_page"]).click()
    logger.info("Clicked 'Search by Station'")

    logger.info("Waiting for Station Search form to load...")
    await page.locator(LOGIN["station_search_page"]).wait_for(state="visible", timeout=0)
    logger.info("Station Search form loaded — ready to proceed")
