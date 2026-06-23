from playwright.async_api import Page
from booker.selectors import LOGIN
from utils.logger import get_logger

logger = get_logger("login")
LOGIN_URL = "https://www.eki-net.com/en/jreast-train-reservation/Top/Index"

async def login(page: Page, config: dict) -> None:
    logger.info("Navigating to eki-net login page")
    await page.goto(LOGIN_URL, wait_until="domcontentloaded")

    try:
        await page.locator(LOGIN["login_button"]).first.click(timeout=5_000)
        await page.wait_for_load_state("domcontentloaded")
    except Exception:
        pass  # form may already be visible

    logger.info("Filling credentials")
    await page.locator(LOGIN["email_input"]).first.fill(config["account"]["email"])
    await page.locator(LOGIN["password_input"]).first.fill(config["account"]["password"])
    await page.locator(LOGIN["submit_button"]).first.click()
    await page.wait_for_load_state("domcontentloaded")

    indicator = page.locator(LOGIN["logged_in_indicator"]).first
    if not await indicator.is_visible(timeout=10_000):
        raise RuntimeError("Login failed — logged-in indicator not found after submit")

    logger.info("Login successful")
