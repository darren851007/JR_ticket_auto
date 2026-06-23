import subprocess
from utils.logger import get_logger

logger = get_logger("notify")

def _mac_notify(title: str, message: str) -> None:
    safe_title = title.replace('"', '\\"')
    safe_message = message.replace('"', '\\"')
    script = f'display notification "{safe_message}" with title "{safe_title}"'
    subprocess.run(["osascript", "-e", script], check=False)

def notify_success(screenshot_path: str) -> None:
    logger.info(f"Success — screenshot: {screenshot_path}")
    _mac_notify("JR Ticket Bot", f"Booking ready — check browser")

def notify_failure(message: str) -> None:
    logger.error(f"Failure: {message}")
    _mac_notify("JR Ticket Bot", f"Booking failed: {message}")
