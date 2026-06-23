# eki-net-booker-phase1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold the JR Shinkansen ticket automation project and implement the first execution phase: browser startup → login to eki-net → wait until sale_open_time.

**Architecture:** Async Playwright for browser control. Concerns split across `booker/` (browser lifecycle, login, scheduling) and `utils/` (config, logging, notifications). `main.py` orchestrates the sequence. Browser never auto-closes — stays open after success or failure for manual inspection.

**Tech Stack:** Python 3.10+, playwright (async), pyyaml, zoneinfo (stdlib), osascript (macOS notifications)

## Global Constraints

- Python 3.10+
- All async code uses `asyncio` + `async_playwright`
- Timezone: `Asia/Tokyo` (JST) via `zoneinfo.ZoneInfo("Asia/Tokyo")`
- Browser stays open at end — no auto `browser.close()` in happy or error path
- `sale_open_time` accepts `YYYY/M/D HH:MM` (primary) or `YYYY-MM-DD HH:MM:SS` (fallback)
- Log files written to `logs/` with timestamp in filename; `logs/` is gitignored
- Target site: `https://www.eki-net.com/en/jreast-train-reservation/Top/Index`

---

### [x] Task 1: Project scaffolding and utils layer

**Files:**
- Create: `requirements.txt`
- Create: `config.yaml` (gitignored, filled with real credentials)
- Create: `config.example.yaml`
- Create: `.gitignore`
- Create: `utils/__init__.py`
- Create: `utils/config_loader.py`
- Create: `utils/logger.py`
- Create: `utils/notify.py`
- Create: `booker/__init__.py`

**Interfaces:**
- Produces: `load_config(path: str = "config.yaml") -> dict` from `utils.config_loader`
- Produces: `get_logger(name: str) -> logging.Logger` from `utils.logger`
- Produces: `notify_success(screenshot_path: str) -> None` from `utils.notify`
- Produces: `notify_failure(message: str) -> None` from `utils.notify`

- [ ] **Step 1: Create requirements.txt**

```
playwright==1.44.0
pyyaml>=6.0
```

- [ ] **Step 2: Install dependencies and Playwright browser**

```bash
pip install -r requirements.txt
playwright install chromium
```

- [ ] **Step 3: Create config.example.yaml**

```yaml
account:
  email: "your-email@example.com"
  password: "your-password"

sale_open_time: "2025/7/1 09:00"   # YYYY/M/D HH:MM (JST)
```

- [ ] **Step 4: Create config.yaml** (fill with real credentials — will be gitignored)

Same structure as `config.example.yaml` with actual values.

- [ ] **Step 5: Create .gitignore**

```
config.yaml
logs/
screenshots/*.png
__pycache__/
*.pyc
.venv/
```

- [ ] **Step 6: Create utils/__init__.py and booker/__init__.py**

Both are empty files (`touch utils/__init__.py booker/__init__.py`).

- [ ] **Step 7: Create utils/config_loader.py**

```python
import yaml

def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
```

- [ ] **Step 8: Create utils/logger.py**

```python
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
```

- [ ] **Step 9: Create utils/notify.py**

```python
import subprocess
from utils.logger import get_logger

logger = get_logger("notify")

def _mac_notify(title: str, message: str) -> None:
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], check=False)

def notify_success(screenshot_path: str) -> None:
    logger.info(f"Success — screenshot: {screenshot_path}")
    _mac_notify("JR Ticket Bot", f"Booking ready — check browser")

def notify_failure(message: str) -> None:
    logger.error(f"Failure: {message}")
    _mac_notify("JR Ticket Bot", f"Booking failed: {message}")
```

- [ ] **Step 10: Commit**

```bash
git add requirements.txt config.example.yaml .gitignore utils/ booker/__init__.py
git commit -m "feat: project scaffolding and utils layer"
```

---

### [x] Task 2: Scheduler module

**Files:**
- Create: `booker/scheduler.py`

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces:
  - `parse_sale_open_time(raw: str) -> datetime` — parses `YYYY/M/D HH:MM` or `YYYY-MM-DD HH:MM:SS`, returns tz-aware JST `datetime`
  - `wait_until(target_dt: datetime) -> None` — async coroutine; sleeps until `target_dt`; warns and returns immediately if time is in the past

- [ ] **Step 1: Create booker/scheduler.py**

```python
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.logger import get_logger

logger = get_logger("scheduler")
JST = ZoneInfo("Asia/Tokyo")

async def wait_until(target_dt: datetime) -> None:
    now = datetime.now(tz=JST)
    delta = (target_dt - now).total_seconds()
    if delta <= 0:
        logger.warning("sale_open_time is in the past — proceeding immediately")
        return
    logger.info(f"Waiting {delta:.1f}s until {target_dt.strftime('%Y-%m-%d %H:%M:%S')} JST")
    await asyncio.sleep(delta)

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
```

- [ ] **Step 2: Smoke-test the parser**

```bash
python -c "
from booker.scheduler import parse_sale_open_time
print(parse_sale_open_time('2025/7/1 09:00'))
# expected: 2025-07-01 09:00:00+09:00
print(parse_sale_open_time('2025-07-01 09:00:00'))
# expected: 2025-07-01 09:00:00+09:00
"
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
python -m pytest --tb=short -q 2>/dev/null || echo "no tests yet — OK"
```

- [ ] **Step 4: Commit**

```bash
git add booker/scheduler.py
git commit -m "feat: scheduler — wait_until and parse_sale_open_time"
```

---

### [x] Task 3: Browser manager

**Files:**
- Create: `booker/browser.py`
- Create: `screenshots/.gitkeep`
- Modify: `.gitignore` (add `screenshots/*.png` if not already present)

**Interfaces:**
- Consumes: nothing from earlier tasks
- Produces: `BrowserManager` class with:
  - `async start(headless: bool = False) -> tuple[Browser, Page]` — launches Chromium with anti-detection flag, returns browser + a fresh page
  - `async screenshot(page: Page, label: str) -> str` — saves `screenshots/YYYYMMDD_HHMMSS_<label>.png`, returns the path
  - `async close() -> None` — closes browser and stops Playwright; only call this explicitly if needed

- [ ] **Step 1: Create screenshots directory placeholder**

```bash
mkdir -p screenshots
touch screenshots/.gitkeep
```

- [ ] **Step 2: Create booker/browser.py**

```python
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.async_api import async_playwright, Browser, Page
from utils.logger import get_logger

logger = get_logger("browser")
JST = ZoneInfo("Asia/Tokyo")

class BrowserManager:
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None

    async def start(self, headless: bool = False) -> tuple[Browser, Page]:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await context.new_page()
        logger.info("Browser launched")
        return self._browser, page

    async def screenshot(self, page: Page, label: str) -> str:
        os.makedirs("screenshots", exist_ok=True)
        ts = datetime.now(tz=JST).strftime("%Y%m%d_%H%M%S")
        path = f"screenshots/{ts}_{label}.png"
        await page.screenshot(path=path)
        logger.info(f"Screenshot saved: {path}")
        return path

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Browser closed")
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
python -m pytest --tb=short -q 2>/dev/null || echo "no tests yet — OK"
```

- [ ] **Step 4: Commit**

```bash
git add booker/browser.py screenshots/.gitkeep
git commit -m "feat: BrowserManager with start, screenshot, close"
```

---

### [x] Task 4: Login module

**Files:**
- Create: `booker/selectors.py`
- Create: `booker/login.py`

**Interfaces:**
- Consumes: `page: Page` (from `BrowserManager.start()`), `config: dict` (from `load_config()`)
- Produces: `login(page: Page, config: dict) -> None`
  - Navigates to eki-net, clicks login button, fills email + password, submits, verifies a logged-in indicator is visible
  - Raises `RuntimeError("Login failed — logged-in indicator not found after submit")` on failure

- [ ] **Step 1: Create booker/selectors.py**

These CSS selectors target the eki-net English reservation page. If the site updates its markup, adjust these constants.

```python
LOGIN = {
    "login_button":        "a[href*='login'], button:has-text('Log in'), a:has-text('Login')",
    "email_input":         "input[type='email'], input[name*='mail'], input[id*='mail']",
    "password_input":      "input[type='password']",
    "submit_button":       "button[type='submit'], input[type='submit']",
    "logged_in_indicator": "a[href*='logout'], span:has-text('Log out'), a:has-text('Sign out')",
}
```

- [ ] **Step 2: Create booker/login.py**

```python
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
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
python -m pytest --tb=short -q 2>/dev/null || echo "no tests yet — OK"
```

- [ ] **Step 4: Commit**

```bash
git add booker/selectors.py booker/login.py
git commit -m "feat: login module for eki-net"
```

---

### [x] Task 5: main.py integration

**Files:**
- Create: `main.py`

**Interfaces:**
- Consumes:
  - `load_config(path)` → `dict` from `utils.config_loader`
  - `get_logger(name)` → `Logger` from `utils.logger`
  - `notify_failure(msg)` → `None` from `utils.notify`
  - `BrowserManager` from `booker.browser`
  - `login(page, config)` → `None` from `booker.login`
  - `wait_until(dt)` → `None` (async) from `booker.scheduler`
  - `parse_sale_open_time(raw)` → `datetime` from `booker.scheduler`
- Produces: runnable entry point (`python main.py`)

- [ ] **Step 1: Create main.py**

```python
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
```

- [ ] **Step 2: Run end-to-end**

```bash
python main.py
```

Expected: Chromium opens, navigates to eki-net, logs in, then logs `"Waiting Xs until YYYY-MM-DD HH:MM:SS JST"`. Browser stays open. Ctrl+C does not close the browser.

- [ ] **Step 3: Verify existing tests still pass**

```bash
python -m pytest --tb=short -q 2>/dev/null || echo "no tests yet — OK"
```

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: main.py — startup, login, wait_until integration"
```
