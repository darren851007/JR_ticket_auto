import re
from playwright.async_api import Page
from booker.selectors import TRAIN_SELECT
from utils.logger import get_logger

logger = get_logger("train_select")

SEAT_CLASS_TEXT = {
    "reserved":     "Reserved seat",
    "non_reserved": "Non-reserved seat",
    "green":        "Green",
    "gran_class":   "GranClass",
}


async def select_train(page: Page, config: dict) -> None:
    train_cfg = config["train"]

    logger.info("Waiting for search results...")
    await page.locator(TRAIN_SELECT["results_section"]).wait_for(state="visible", timeout=0)

    name_els = await page.locator(TRAIN_SELECT["train_name"]).all()
    target_idx = None

    target_name = train_cfg["name"].lower()
    for i, el in enumerate(name_els):
        text = (await el.text_content() or "").lower()
        if target_name in text:
            logger.info(f"Matched train by name at index {i}: {await el.text_content()}")
            target_idx = i
            break

    if target_idx is None:
        logger.info(f"Train '{train_cfg['name']}' not found — falling back to closest departure time")
        th, tm = map(int, train_cfg["departure_time"].split(":"))
        target_minutes = th * 60 + tm
        min_delta = float("inf")
        dep_els = await page.locator(TRAIN_SELECT["departure_time"]).all()
        for i, el in enumerate(dep_els):
            text = await el.text_content() or ""
            match = re.search(r"(\d{1,2}):(\d{2})", text)
            if match:
                h, m = int(match.group(1)), int(match.group(2))
                delta = abs(h * 60 + m - target_minutes)
                if delta < min_delta:
                    min_delta = delta
                    target_idx = i
                    logger.info(f"Closest departure so far: {h:02d}:{m:02d} (index {i}, delta {delta}min)")

    if target_idx is None:
        raise RuntimeError("No train found matching name or departure time")

    expand_btns = await page.locator(TRAIN_SELECT["expand_button"]).all()
    if target_idx < len(expand_btns):
        btn_class = await expand_btns[target_idx].get_attribute("class") or ""
        if "active" not in btn_class:
            logger.info(f"Expanding seat panel for train index {target_idx}")
            await expand_btns[target_idx].click()
            await page.locator(TRAIN_SELECT["seat_list"]).nth(target_idx).wait_for(
                state="visible", timeout=10_000
            )

    seat_class = train_cfg["seat_class"]
    seat_text = SEAT_CLASS_TEXT.get(seat_class, "Reserved seat")
    logger.info(f"Selecting seat class: {seat_text}")
    seat_list = page.locator(TRAIN_SELECT["seat_list"]).nth(target_idx)

    if seat_class == "reserved":
        label = seat_list.locator(
            "label.selService_formTrainSeatSelListItemLink"
        ).filter(
            has=page.locator(".selService_formTrainSeatSelListItemLink-sale.normal")
        ).filter(has_not_text="TRAIN DESK").first
    else:
        label = seat_list.locator(f"label:has-text('{seat_text}')").first

    await label.click()
    logger.info(f"Clicked seat class: {seat_text}")

    logger.info(f"Clicking Select button (index {target_idx})")
    await page.locator(f"button#Select{target_idx}").click()
    logger.info("Train selected")
