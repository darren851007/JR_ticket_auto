from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.async_api import Page
from booker.selectors import SEARCH_FORM
from utils.logger import get_logger

logger = get_logger("search_form")
JST = ZoneInfo("Asia/Tokyo")


async def fill_search_form(page: Page, config: dict) -> None:
    search = config["search"]

    month, day = search["date"].split("/")
    year = datetime.now(tz=JST).year
    date_value = f"{year}{int(month):02d}{int(day):02d}"

    hour_str, minute_str = search["time"].split(":")
    hour = hour_str.zfill(2)
    rounded = min(round(int(minute_str) / 5) * 5, 55)
    minute = str(rounded).zfill(2)

    logger.info(f"Setting departure station: {search['departure_station']}")
    await _js_set(page, SEARCH_FORM["departure_input"], search["departure_station"])

    logger.info(f"Setting arrival station: {search['arrival_station']}")
    await _js_set(page, SEARCH_FORM["arrival_input"], search["arrival_station"])

    logger.info(f"Selecting date: {date_value}")
    await page.locator(SEARCH_FORM["date_select"]).select_option(date_value)

    logger.info(f"Selecting time: {hour}:{minute}")
    await page.locator(SEARCH_FORM["hour_select"]).select_option(hour)
    await page.locator(SEARCH_FORM["minute_select"]).select_option(minute)

    time_type = search.get("time_type", "departure")
    radio_key = "arrival_radio" if time_type == "arrival" else "departure_radio"
    logger.info(f"Selecting time type: {time_type}")
    await page.locator(SEARCH_FORM[radio_key]).click()

    logger.info(f"Selecting adults: {search['adults']}")
    await page.locator(SEARCH_FORM["adults_select"]).select_option(str(search["adults"]))

    logger.info(f"Selecting children: {search['children']}")
    await page.locator(SEARCH_FORM["children_select"]).select_option(str(search["children"]))

    logger.info("Clicking Search button")
    await page.locator(SEARCH_FORM["search_button"]).click()
    logger.info("Search submitted")


async def _js_set(page: Page, selector: str, value: str) -> None:
    await page.evaluate(
        """([selector, value]) => {
            const el = document.querySelector(selector);
            if (!el) throw new Error('Element not found: ' + selector);
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        [selector, value],
    )
