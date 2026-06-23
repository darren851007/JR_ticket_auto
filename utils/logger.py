import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

_JST = ZoneInfo("Asia/Tokyo")
_LOG_NAME = datetime.now(tz=_JST).strftime("%Y%m%d_%H%M%S")

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s %(message)s")

    os.makedirs("logs", exist_ok=True)
    fh = logging.FileHandler(f"logs/{_LOG_NAME}.log", encoding="utf-8")
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
