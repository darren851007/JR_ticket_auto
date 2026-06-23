import asyncio
from utils.config_loader import load_config
from utils.logger import get_logger
from utils.notify import notify_failure
from booker.browser import BrowserManager
from booker.login import login
from booker.scheduler import wait_until, parse_sale_open_time

logger = get_logger("main")

async def main():
    config = load_config("config.yaml")
    sale_time = parse_sale_open_time(config["sale_open_time"])
    mgr = BrowserManager()

    logger.info(f"Sale opens: {sale_time.strftime('%Y-%m-%d %H:%M:%S')} JST")

    _, page = await mgr.start(headless=False)

    try:
        await login(page, config)
        await wait_until(sale_time)
        logger.info("Sale is open — ready to book")
        logger.info("Close the browser window when done.")
        await page.wait_for_close()

    except KeyboardInterrupt:
        logger.info("Stopped by user — browser left open")
    except Exception as e:
        logger.error(f"Error: {e}")
        await mgr.screenshot(page, "error")
        notify_failure(str(e))
        logger.info("Browser left open for inspection. Close manually when done.")
        await page.wait_for_close()

if __name__ == "__main__":
    asyncio.run(main())
