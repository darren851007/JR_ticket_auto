import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.logger import get_logger

logger = get_logger("scheduler")
JST = ZoneInfo("Asia/Tokyo")

async def wait_until(target_dt: datetime, page=None) -> None:
    now = datetime.now(tz=JST)
    delta = (target_dt - now).total_seconds()
    if delta <= 0:
        logger.warning("sale_open_time is in the past — proceeding immediately")
        return
    logger.info(f"Waiting {delta:.1f}s until {target_dt.strftime('%Y-%m-%d %H:%M:%S')} JST")
    final_countdown = False
    while True:
        remaining = (target_dt - datetime.now(tz=JST)).total_seconds()
        if remaining <= 0:
            if page is not None:
                logger.info("售票時間到，重整頁面")
                await page.reload()
            break
        logger.info(f"距離開始搶票時間還剩: {remaining:.0f}s")
        if remaining > 10:
            if page is not None:
                await page.reload()
            await asyncio.sleep(min(5, remaining))
        else:
            if not final_countdown:
                if page is not None:
                    await page.reload()
                final_countdown = True
            await asyncio.sleep(min(1, remaining))

def parse_sale_open_time(raw: str) -> datetime:
    for fmt in ("%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=JST)
        except ValueError:
            continue
    raise ValueError(
        f"Cannot parse sale_open_time '{raw}'. "
        "Expected 'YYYY/M/D HH:MM' or 'YYYY-MM-DD HH:MM:SS'."
    )
