# fill-station-search-form Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically fill the eki-net Station Search form from `config.yaml` and submit it after the sale opens.

**Architecture:** Add a `search` config block to `config.yaml`. Create `booker/search_form.py` with `fill_search_form(page, config)` that fills each field via Playwright (station names via JS `evaluate`, dropdowns via `select_option`, radio via `click`) then submits. Call it from `main.py` after `wait_until(sale_time)`.

**Tech Stack:** Python 3.11+, Playwright (async), PyYAML, `zoneinfo`

## Global Constraints

- Working directory: `/Users/liuda/VsCodeProjects/JR_ticket_auto`
- All async functions use `async def` and `await`
- Logger via `get_logger(name)` from `utils.logger`
- JST timezone via `ZoneInfo("Asia/Tokyo")`
- Selectors live in dicts in `booker/selectors.py` (follow `LOGIN` dict pattern)
- No new test files (Simple mode); run `pytest` if tests directory exists

---

### [x] Task 1: Selectors + config + search_form module

**Files:**
- Modify: `booker/selectors.py`
- Modify: `config.yaml`
- Create: `booker/search_form.py`

**Interfaces:**
- Consumes: `SEARCH_FORM` dict from `booker/selectors.py`; `config["search"]` dict
- Produces: `async def fill_search_form(page: Page, config: dict) -> None` in `booker/search_form.py`

- [ ] **Step 1: Add `SEARCH_FORM` dict to `booker/selectors.py`**

Append after the `LOGIN` dict:

```python
SEARCH_FORM = {
    "departure_input": "#TxtRideStation",
    "arrival_input":   "#TxtGetoffStation",
    "date_select":     "#DdlBoardingDate",
    "hour_select":     "select[name='Hour']",
    "minute_select":   "select[name='Minute']",
    "departure_radio": "#RdiDepartureArrivalChoice1",
    "arrival_radio":   "#RdiDepartureArrivalChoice2",
    "adults_select":   "#DdlAdultNumber",
    "children_select": "#DdlChildNumber",
    "search_button":   "#BtnTrainSearch",
}
```

- [ ] **Step 2: Add `search` block to `config.yaml`**

Append to the end of `config.yaml`:

```yaml
search:
  departure_station: "TOKYO"
  arrival_station:   "NAGAOKA"
  date:              "7/1"        # M/D (year auto-filled from current JST year)
  time:              "10:00"      # HH:MM
  time_type:         "departure"  # departure | arrival
  adults:            1
  children:          0
```

- [ ] **Step 3: Create `booker/search_form.py`**

```python
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
    rounded = round(int(minute_str) / 5) * 5
    minute = "55" if rounded >= 60 else str(rounded).zfill(2)

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
            el.value = value;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""",
        [selector, value],
    )
```

- [ ] **Step 4: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [ ] **Step 5: Commit**

```bash
git add booker/selectors.py booker/search_form.py config.yaml
git commit -m "feat: add SEARCH_FORM selectors, search config, and search_form module"
```

---

### [x] Task 2: Wire fill_search_form into main.py

**Files:**
- Modify: `main.py`

**Interfaces:**
- Consumes: `fill_search_form(page, config)` from `booker.search_form`

- [ ] **Step 1: Add import to `main.py`**

Add this line after the existing imports (around line 6):

```python
from booker.search_form import fill_search_form
```

- [ ] **Step 2: Call `fill_search_form` after `wait_until`**

Replace:
```python
        await wait_until(sale_time)
        logger.info("Sale is open — ready to book")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

With:
```python
        await wait_until(sale_time)
        logger.info("Sale is open — filling search form")
        await fill_search_form(page, config)
        logger.info("Search submitted — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

- [ ] **Step 3: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: wire fill_search_form into main after wait_until"
```

---

### [x] Revision 1 - Task 3: Untrack config.yaml from git

**Files:**
- No source files modified — git index only

**Interfaces:**
- Consumes: nothing
- Produces: `config.yaml` removed from git tracking

- [ ] **Step 1: Untrack config.yaml**

```bash
git rm --cached config.yaml
```

- [ ] **Step 2: Commit**

```bash
git commit -m "chore: untrack config.yaml (contains credentials, covered by .gitignore)"
```
