# select-ticket-type Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After train selection, automatically click the correct ticket type button based on `config["ticket_type"]`, with e-ticket stubbed as `NotImplementedError`.

**Architecture:** Add `TICKET_TYPE_SELECT` selectors to `booker/selectors.py`. Create `booker/ticket_type_select.py` with `select_ticket_type(page, config)` that waits for the ticket type page, then clicks `#BtnBuyATicketForMagneticTicket` for `"regular"` or raises `NotImplementedError` for `"e_ticket"`. Wire into `main.py` after `select_train`. Add `ticket_type: "regular"` to `config.yaml`.

**Tech Stack:** Python 3.11+, Playwright (async)

## Global Constraints

- Working directory: `/Users/liuda/VsCodeProjects/JR_ticket_auto`
- All async functions use `async def` and `await`
- Logger via `get_logger(name)` from `utils.logger`
- Selectors live in dicts in `booker/selectors.py` (follow `LOGIN` / `SEARCH_FORM` / `TRAIN_SELECT` pattern)
- No new test files (Simple mode); run `pytest` if tests directory exists
- `config.yaml` contains credentials — NEVER commit it; it is already in `.gitignore`

---

### [x] Task 1: Selectors + config + ticket_type_select module

**Files:**
- Modify: `booker/selectors.py`
- Modify: `config.yaml`
- Create: `booker/ticket_type_select.py`

**Interfaces:**
- Consumes: `TICKET_TYPE_SELECT` dict from `booker/selectors.py`; `config["ticket_type"]` string
- Produces: `async def select_ticket_type(page: Page, config: dict) -> None` in `booker/ticket_type_select.py`

- [x] **Step 1: Add `TICKET_TYPE_SELECT` dict to `booker/selectors.py`**

Append after the `TRAIN_SELECT` dict:

```python
TICKET_TYPE_SELECT = {
    "page_anchor": "#BtnBuyATicketForMagneticTicket",
    "regular":     "#BtnBuyATicketForMagneticTicket",
    "e_ticket":    "#BtnBuyATicketForICCard",
}
```

- [x] **Step 2: Add `ticket_type` field to `config.yaml`**

Append to the end of `config.yaml`:

```yaml
ticket_type: "regular"   # regular | e_ticket (e_ticket not yet implemented)
```

- [x] **Step 3: Create `booker/ticket_type_select.py`**

```python
from playwright.async_api import Page
from booker.selectors import TICKET_TYPE_SELECT
from utils.logger import get_logger

logger = get_logger("ticket_type_select")


async def select_ticket_type(page: Page, config: dict) -> None:
    ticket_type = config["ticket_type"]

    logger.info("Waiting for ticket type selection page...")
    await page.locator(TICKET_TYPE_SELECT["page_anchor"]).wait_for(state="visible", timeout=0)

    if ticket_type == "regular":
        logger.info("Selecting regular ticket")
        await page.locator(TICKET_TYPE_SELECT["regular"]).click()
        await page.wait_for_load_state("domcontentloaded")
        logger.info("Regular ticket selected")
    elif ticket_type == "e_ticket":
        raise NotImplementedError("e-ticket flow is not yet implemented")
    else:
        raise ValueError(f"Unknown ticket_type: {ticket_type!r}. Expected 'regular' or 'e_ticket'.")
```

- [x] **Step 4: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [x] **Step 5: Commit**

```bash
git add booker/selectors.py booker/ticket_type_select.py
git commit -m "feat: add TICKET_TYPE_SELECT selectors and ticket_type_select module"
```

Note: do NOT add `config.yaml` — it is untracked (credentials, covered by `.gitignore`).

---

### [x] Task 2: Wire select_ticket_type into main.py

**Files:**
- Modify: `main.py`

**Interfaces:**
- Consumes: `select_ticket_type(page, config)` from `booker.ticket_type_select`

- [x] **Step 1: Add import to `main.py`**

Add after the existing imports (after `from booker.train_select import select_train`):

```python
from booker.ticket_type_select import select_ticket_type
```

- [x] **Step 2: Call `select_ticket_type` after `select_train` in `main.py`**

Replace:
```python
        await select_train(page, config)
        logger.info("Train selected — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

With:
```python
        await select_train(page, config)
        logger.info("Train selected — selecting ticket type")
        await select_ticket_type(page, config)
        logger.info("Ticket type selected — ready for next step")
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
git commit -m "feat: wire select_ticket_type into main after select_train"
```
