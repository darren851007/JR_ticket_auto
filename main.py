import asyncio
from utils.config_loader import load_config
from utils.logger import get_logger
from utils.notify import notify_failure
from booker.browser import BrowserManager
from booker.login import login
from booker.scheduler import wait_until, parse_sale_open_time
from booker.search_form import fill_search_form
from booker.train_select import select_train

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
        logger.info("Sale is open — filling search form")
        await fill_search_form(page, config)
        logger.info("Search submitted — selecting train")
        await select_train(page, config)
        logger.info("Train selected — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        logger.info("Stopped by user — browser left open")
    except Exception as e:
        logger.error(f"Error: {e}")
        await mgr.screenshot(page, "error")
        notify_failure(str(e))
        logger.info("Browser left open for inspection. Press Ctrl+C to exit.")
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
