# select-train Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Find the configured train in the eki-net search results, expand its seat panel, select the configured seat class, and click Select.

**Architecture:** Add a `train` block to `config.yaml`. Create `booker/train_select.py` with `select_train(page, config)` that waits for results, matches by name (case-insensitive substring) then falls back to closest departure time, expands the seat panel if collapsed, clicks the correct seat-class label, and clicks `button#SelectN`. Add `TRAIN_SELECT` selectors to `selectors.py`. Call from `main.py` after `fill_search_form`.

**Tech Stack:** Python 3.11+, Playwright (async), `re`, `zoneinfo`

## Global Constraints

- Working directory: `/Users/liuda/VsCodeProjects/JR_ticket_auto`
- All async functions use `async def` and `await`
- Logger via `get_logger(name)` from `utils.logger`
- Selectors live in dicts in `booker/selectors.py` (follow `LOGIN` / `SEARCH_FORM` pattern)
- No new test files (Simple mode); run `pytest` if tests directory exists

---

### Task 1: Selectors + config + train_select module

**Files:**
- Modify: `booker/selectors.py`
- Modify: `config.yaml`
- Create: `booker/train_select.py`

**Interfaces:**
- Consumes: `TRAIN_SELECT` dict from `booker/selectors.py`; `config["train"]` dict
- Produces: `async def select_train(page: Page, config: dict) -> None` in `booker/train_select.py`

- [ ] **Step 1: Add `TRAIN_SELECT` dict to `booker/selectors.py`**

Append after the `SEARCH_FORM` dict:

```python
TRAIN_SELECT = {
    "results_section": "#trainSearch_result",
    "train_name":      "h3.ts_resultTrainName",
    "departure_time":  "li.ts_resultDetailOutlineWItemDep",
    "expand_button":   "button.ts_DetailTrainCheckBtn",
    "seat_list":       "ul.selService_formTrainSeatSelList",
}
```

- [ ] **Step 2: Add `train` block to `config.yaml`**

Append to the end of `config.yaml`:

```yaml
train:
  name:           "Toki 307"   # 車次名稱（優先比對，大小寫不分）
  departure_time: "10:04"      # 出發時刻 fallback HH:MM
  seat_class:     "reserved"   # reserved | non_reserved | green | gran_class
```

- [ ] **Step 3: Create `booker/train_select.py`**

```python
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
```

- [ ] **Step 4: Verify existing tests still pass**

```bash
cd /Users/liuda/VsCodeProjects/JR_ticket_auto
pytest --tb=short 2>/dev/null || echo "No tests found — OK"
```

Expected: all pass (or "No tests found — OK")

- [ ] **Step 5: Commit**

```bash
git add booker/selectors.py booker/train_select.py config.yaml
git commit -m "feat: add TRAIN_SELECT selectors, train config, and train_select module"
```

---

### Task 2: Wire select_train into main.py

**Files:**
- Modify: `main.py`

**Interfaces:**
- Consumes: `select_train(page, config)` from `booker.train_select`

- [ ] **Step 1: Add import to `main.py`**

Add after the existing imports:

```python
from booker.train_select import select_train
```

- [ ] **Step 2: Call `select_train` after `fill_search_form`**

Replace:
```python
        await fill_search_form(page, config)
        logger.info("Search submitted — ready for next step")
        logger.info("Press Ctrl+C to exit (browser stays open).")
        await asyncio.Event().wait()
```

With:
```python
        await fill_search_form(page, config)
        logger.info("Search submitted — selecting train")
        await select_train(page, config)
        logger.info("Train selected — ready for next step")
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
git commit -m "feat: wire select_train into main after fill_search_form"
```
