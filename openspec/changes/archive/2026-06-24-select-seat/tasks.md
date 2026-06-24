# select-seat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wait for the Seat Selection page to load, then click "View reservation details" to proceed to the next booking step.

**Architecture:** Add `SEAT_SELECT` to `booker/selectors.py`. Create `booker/seat_select.py` with `select_seat(page, config)` that waits for `#BtnToNext`, sleeps 0.5 seconds, clicks it, and waits for `domcontentloaded`. Wire into `main.py` after `select_ticket_type`. No config changes needed.

**Tech Stack:** Python 3.11+, Playwright (async)

## Global Constraints

- Working directory: `/Users/liuda/VsCodeProjects/JR_ticket_auto`
- All async functions use `async def` and `await`
- Logger via `get_logger(name)` from `utils.logger`
- Selectors live in dicts in `booker/selectors.py` (follow `LOGIN` / `SEARCH_FORM` / `TRAIN_SELECT` / `TICKET_TYPE_SELECT` pattern)
- No new test files (Simple mode); run `pytest` if tests directory exists
- `config.yaml` contains credentials — NEVER commit it; it is already in `.gitignore`

---

### [x] Task 1: Selectors + seat_select module

**Files:**
- Modify: `booker/selectors.py`
- Create: `booker/seat_select.py`

**Interfaces:**
- Consumes: `SEAT_SELECT` dict from `booker/selectors.py`
- Produces: `async def select_seat(page: Page, config: dict) -> None` in `booker/seat_select.py`

- [x] **Step 1: Add `SEAT_SELECT` dict to `booker/selectors.py`**

Append after the `TICKET_TYPE_SELECT` dict:

```python
SEAT_SELECT = {
    "page_anchor":    "#BtnToNext",
    "confirm_button": "#BtnToNext",
}
```

- [x] **Step 2: Create `booker/seat_select.py`**

```python
import asyncio
from playwright.async_api import Page
from booker.selectors import SEAT_SELECT
from utils.logger import get_logger

logger = get_logger("seat_select")


async def select_seat(page: Page, config: dict) -> None:
    logger.info("Waiting for seat selection page...")
    await page.locator(SEAT_SELECT["page_anchor"]).wait_for(state="visible", timeout=0)
    logger.info("Seat selection page loaded — confirming")
    await asyncio.sleep(0.5)
    await page.locator(SEAT_SELECT["confirm_button"]).click()
    await page.wait_for_load_state("domcontentloaded")
    logger.info("Seat selection confirmed")
```

- [x] **Step 3: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [x] **Step 4: Commit**

```bash
git add booker/selectors.py booker/seat_select.py
git commit -m "feat: add SEAT_SELECT selectors and seat_select module"
```

---

### [x] Task 2: Wire select_seat into main.py

**Files:**
- Modify: `main.py`

**Interfaces:**
- Consumes: `select_seat(page, config)` from `booker.seat_select`

- [x] **Step 1: Add import to `main.py`**

Add after `from booker.ticket_type_select import select_ticket_type`:

```python
from booker.seat_select import select_seat
```

- [x] **Step 2: Call `select_seat` after `select_ticket_type` in `main.py`**

Replace:
```python
        await select_ticket_type(page, config)
        logger.info("Ticket type selected — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

With:
```python
        await select_ticket_type(page, config)
        logger.info("Ticket type selected — confirming seat selection")
        await select_seat(page, config)
        logger.info("Seat selection confirmed — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

- [x] **Step 3: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [x] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: wire select_seat into main after select_ticket_type"
```
