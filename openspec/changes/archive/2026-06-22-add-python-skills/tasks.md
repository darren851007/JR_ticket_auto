# add-python-skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create five Python Claude Code skills under `~/.claude/skills/`, each a focused `SKILL.md` providing expert guidance for a domain used in the JR ticket automation project.

**Architecture:** Each skill is a directory containing a single `SKILL.md` with YAML frontmatter and expert guidance. The five skills cover: Playwright automation, FastAPI backend, Anthropic SDK integration, pandas data science, and pytest testing. No code is executed — only documentation files are written.

**Tech Stack:** Claude Code skills system (YAML frontmatter + Markdown), Playwright async_api, FastAPI + Pydantic, Anthropic Python SDK, pandas/numpy/matplotlib, pytest/pytest-asyncio

## Global Constraints

- Target base dir: `~/.claude/skills/` (absolute: `/Users/liuda/.claude/skills/`)
- Each skill: one directory + one `SKILL.md` — no other files
- Frontmatter fields: `name` (kebab-case, matches folder name) and `description` (one sentence, describes when to trigger the skill)
- Mode: Simple — no new tests required; verify `openspec/` files are intact after each task
- Do NOT modify any existing skill directories

---

### Task 1: python-automation skill

**Files:**
- Create: `/Users/liuda/.claude/skills/python-automation/SKILL.md`

**Interfaces:**
- Consumes: nothing
- Produces: `/Users/liuda/.claude/skills/python-automation/SKILL.md` — readable by Claude Code skill loader

- [ ] **Step 1: Create the skill directory**

```bash
mkdir /Users/liuda/.claude/skills/python-automation
```

Expected: no output, exit 0.

- [ ] **Step 2: Write SKILL.md**

Write the following content exactly to `/Users/liuda/.claude/skills/python-automation/SKILL.md`:

```markdown
---
name: python-automation
description: Expert guidance on Playwright browser automation, retry logic, APScheduler scheduling, and cookie session management. Use when writing or reviewing Python scripts that automate browser interactions for ticket booking or any web automation task.
---

# Python Browser Automation with Playwright

## 1. Async Playwright Setup

Always use the async API. Use `headless=False` during development, `headless=True` in production.

```python
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, slow_mo=50)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        await run(page, context)
        await browser.close()
```

## 2. Waiting — Never Use asyncio.sleep for Page State

Use Playwright's built-in wait methods:

```python
# Wait for element to appear
await page.wait_for_selector("button#submit", state="visible", timeout=10_000)

# Wait for navigation
await page.wait_for_load_state("networkidle")

# Wait for URL change
await page.wait_for_url("**/success**")

# Wait for a DOM condition
await page.wait_for_function("document.querySelector('#status').textContent === 'Available'")
```

`asyncio.sleep()` is acceptable only for rate-limiting between retry attempts, never for waiting on page state.

## 3. Retry Logic with Exponential Backoff

```python
import asyncio
import logging
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")
logger = logging.getLogger(__name__)

async def retry(
    fn: Callable[[], Awaitable[T]],
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
) -> T:
    for attempt in range(max_attempts):
        try:
            return await fn()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
            await asyncio.sleep(delay)
    raise RuntimeError("unreachable")
```

Apply the retry wrapper to the outer booking attempt, not to individual page interactions.

## 4. Cookie Session Persistence

Save and restore browser context cookies to avoid re-login on every run:

```python
import json
from pathlib import Path

COOKIES_FILE = Path("session_cookies.json")

async def save_cookies(context: BrowserContext) -> None:
    cookies = await context.cookies()
    COOKIES_FILE.write_text(json.dumps(cookies))

async def load_cookies(context: BrowserContext) -> bool:
    if not COOKIES_FILE.exists():
        return False
    cookies = json.loads(COOKIES_FILE.read_text())
    await context.add_cookies(cookies)
    return True
```

Add `session_cookies.json` to `.gitignore` — it contains your login session.

## 5. Anti-Detection Techniques

```python
import random

# Randomize viewport slightly
viewport = {
    "width": random.randint(1260, 1300),
    "height": random.randint(700, 740),
}

# Humanize timing
browser = await p.chromium.launch(slow_mo=random.randint(30, 80))

# Suppress navigator.webdriver flag
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
""")

# Click at a random position within the element bounds
async def human_click(page: Page, selector: str) -> None:
    elem = page.locator(selector)
    box = await elem.bounding_box()
    x = box["x"] + box["width"] * random.uniform(0.2, 0.8)
    y = box["y"] + box["height"] * random.uniform(0.2, 0.8)
    await page.mouse.click(x, y)
```

## 6. Scheduling with APScheduler

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

scheduler = AsyncIOScheduler()

scheduler.add_job(
    check_and_book,           # your async booking coroutine
    trigger=IntervalTrigger(seconds=30),
    id="ticket_check",
    replace_existing=True,
)

scheduler.start()

try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    scheduler.shutdown()
```

## 7. Debugging — Screenshots and Traces

```python
# Capture screenshot on error
try:
    await do_booking_step(page)
except Exception:
    await page.screenshot(path="debug_error.png", full_page=True)
    raise

# Full trace for complex debugging
async with async_playwright() as p:
    browser = await p.chromium.launch()
    context = await browser.new_context()
    await context.tracing.start(screenshots=True, snapshots=True)
    # ... do work ...
    await context.tracing.stop(path="trace.zip")
    # View with: playwright show-trace trace.zip
```

## 8. Checklist
- [ ] Use `async with async_playwright()` — never call `.stop()` manually
- [ ] All page-state waits use Playwright APIs, not `asyncio.sleep`
- [ ] Retry wrapper applied at the booking-attempt level, not per page action
- [ ] `session_cookies.json` in `.gitignore`
- [ ] Set `PWDEBUG=1` env var to open Playwright Inspector for step-by-step debugging
- [ ] Install: `pip install playwright apscheduler && playwright install chromium`
```

- [ ] **Step 3: Verify the file exists and has correct frontmatter**

```bash
head -5 /Users/liuda/.claude/skills/python-automation/SKILL.md
```

Expected output:
```
---
name: python-automation
description: Expert guidance on Playwright browser automation...
---
```

---

### Task 2: python-fastapi skill

**Files:**
- Create: `/Users/liuda/.claude/skills/python-fastapi/SKILL.md`

**Interfaces:**
- Consumes: nothing
- Produces: `/Users/liuda/.claude/skills/python-fastapi/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir /Users/liuda/.claude/skills/python-fastapi
```

Expected: no output, exit 0.

- [ ] **Step 2: Write SKILL.md**

Write the following content exactly to `/Users/liuda/.claude/skills/python-fastapi/SKILL.md`:

```markdown
---
name: python-fastapi
description: Expert guidance on FastAPI application design, routing, dependency injection, Pydantic settings, and webhook notifications. Use when building or reviewing FastAPI REST APIs, monitoring endpoints, or notification systems.
---

# FastAPI Best Practices

## 1. Project Structure

```
app/
├── main.py           # FastAPI app, middleware, lifespan hooks
├── config.py         # Pydantic Settings (reads from env vars)
├── routers/
│   ├── status.py     # /status endpoints
│   └── webhook.py    # /webhook endpoints
└── dependencies.py   # Shared Depends() functions
```

## 2. Pydantic Settings — Always Read Config from Environment

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jr_username: str
    jr_password: str
    line_token: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    check_interval_seconds: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

Never hardcode credentials. Use `.env` (via `python-dotenv`) or OS environment variables.

## 3. Router Organization

```python
# routers/status.py
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/status", tags=["status"])

@router.get("/")
async def get_status():
    return {"running": True, "interval_seconds": settings.check_interval_seconds}
```

```python
# main.py
from fastapi import FastAPI
from app.routers import status, webhook

app = FastAPI(title="JR Ticket Monitor")
app.include_router(status.router)
app.include_router(webhook.router)
```

## 4. BackgroundTasks — Non-Blocking Notifications

```python
from fastapi import BackgroundTasks
import httpx

def send_line_notification(message: str, token: str) -> None:
    httpx.post(
        "https://notify-api.line.me/api/notify",
        headers={"Authorization": f"Bearer {token}"},
        data={"message": message},
    )

@router.post("/notify")
async def notify(message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_line_notification, message, settings.line_token)
    return {"queued": True}
```

Use `BackgroundTasks` for fire-and-forget notifications. For retries or guaranteed delivery, use a task queue (Celery or arq).

## 5. HTTPException and Custom Error Handlers

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": str(exc)})

# Inside a route:
raise HTTPException(status_code=404, detail="No tickets found for this date")
```

## 6. async vs sync Endpoints

- `async def`: use when the handler calls `await` (httpx async, database async)
- `def`: use for CPU-bound or sync-library calls — FastAPI runs them in a threadpool automatically
- Never call blocking I/O (`requests.get`, `open()`) inside `async def` — use `httpx.AsyncClient` or `aiofiles`

## 7. Running the Server

```bash
pip install fastapi uvicorn pydantic-settings httpx
uvicorn app.main:app --reload --port 8000
# API docs at http://localhost:8000/docs
```

## 8. Checklist
- [ ] All secrets in environment variables — never in source code
- [ ] `.env` added to `.gitignore`
- [ ] Routers use `prefix` and `tags` for clean auto-generated `/docs`
- [ ] Long-running operations use `BackgroundTasks` or an external queue
- [ ] Sync blocking calls wrapped in `asyncio.to_thread()` if called from async context
```

- [ ] **Step 3: Verify the file exists**

```bash
head -5 /Users/liuda/.claude/skills/python-fastapi/SKILL.md
```

Expected output:
```
---
name: python-fastapi
description: Expert guidance on FastAPI application design...
---
```

---

### Task 3: python-llm-integration skill

**Files:**
- Create: `/Users/liuda/.claude/skills/python-llm-integration/SKILL.md`

**Interfaces:**
- Consumes: nothing
- Produces: `/Users/liuda/.claude/skills/python-llm-integration/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir /Users/liuda/.claude/skills/python-llm-integration
```

Expected: no output, exit 0.

- [ ] **Step 2: Write SKILL.md**

Write the following content exactly to `/Users/liuda/.claude/skills/python-llm-integration/SKILL.md`:

```markdown
---
name: python-llm-integration
description: Expert guidance on using the Anthropic Python SDK — messages API, tool use, streaming, Vision, and cost control. Use when calling Claude from Python, designing agentic workflows, or parsing complex web content with AI.
---

# Anthropic SDK (Claude) Integration

## 1. Basic Setup

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Is ticket 14:00 available?"}],
)
print(message.content[0].text)
```

Set `ANTHROPIC_API_KEY` in your environment — never pass it as a string literal in code.

## 2. System Prompts

```python
message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    system="You are a JR ticket availability parser. Extract seat availability from HTML. Respond only with JSON: {\"available\": bool, \"seats\": int}",
    messages=[{"role": "user", "content": f"<html>{page_html}</html>"}],
)
```

System prompts set persistent behavior for the conversation. Keep them focused — one clear instruction per sentence.

## 3. Tool Use (Function Calling)

```python
tools = [
    {
        "name": "select_train",
        "description": "Select a train to book based on available options",
        "input_schema": {
            "type": "object",
            "properties": {
                "train_id": {
                    "type": "string",
                    "description": "The train ID from the search results",
                },
                "seat_class": {
                    "type": "string",
                    "enum": ["ordinary", "green"],
                    "description": "Seat class preference",
                },
            },
            "required": ["train_id", "seat_class"],
        },
    }
]

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=256,
    tools=tools,
    messages=[{
        "role": "user",
        "content": f"Available trains: {trains_json}. Pick the best one departing around 14:00.",
    }],
)

if response.stop_reason == "tool_use":
    tool_block = next(b for b in response.content if b.type == "tool_use")
    inputs = tool_block.input  # dict: {"train_id": "...", "seat_class": "..."}
```

## 4. Vision — Parse Screenshots

```python
import base64
from pathlib import Path

def image_to_base64(path: str) -> str:
    return base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")

message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=512,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_to_base64("screenshot.png"),
                },
            },
            {
                "type": "text",
                "text": "What seats are available? Reply as JSON: {\"ordinary\": int, \"green\": int}",
            },
        ],
    }],
)
```

Use Vision when page structure is too dynamic for HTML parsing, or when a CAPTCHA image must be read.

## 5. Streaming

```python
with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final_message = stream.get_final_message()
```

Use streaming when showing Claude's response to a user in real time. For programmatic parsing, use the non-streaming API instead (simpler to work with).

## 6. Cost Control

```python
# Always set max_tokens — no open-ended calls
# Approximate pricing (check docs for current rates):
# claude-opus-4-5:         input ~$15/MTok,  output ~$75/MTok
# claude-haiku-4-5-20251001: input ~$0.80/MTok, output ~$4/MTok

# Log usage after every call
print(f"Tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out")

# Use Haiku for high-frequency parsing, Opus for complex decisions
model = "claude-haiku-4-5-20251001" if task == "parse_html" else "claude-opus-4-5"
```

## 7. Multi-Turn Conversation

```python
messages = []

def chat(user_input: str) -> str:
    messages.append({"role": "user", "content": user_input})
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=messages,
    )
    assistant_text = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_text})
    return assistant_text
```

## 8. Error Handling

```python
import anthropic
import time

def create_with_retry(client, **kwargs):
    for attempt in range(3):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            time.sleep(60 * (attempt + 1))
        except anthropic.APIStatusError as e:
            raise  # Non-retriable — surface immediately
    raise RuntimeError("Rate limit retries exhausted")
```

## 9. Checklist
- [ ] `ANTHROPIC_API_KEY` in environment, never in source code
- [ ] `max_tokens` always specified — no open-ended calls
- [ ] Use `claude-haiku-4-5-20251001` for high-frequency/cheap parsing tasks
- [ ] Log `usage.input_tokens` + `usage.output_tokens` per call for cost visibility
- [ ] Handle `anthropic.RateLimitError` with exponential backoff
- [ ] Install: `pip install anthropic`
```

- [ ] **Step 3: Verify the file exists**

```bash
head -5 /Users/liuda/.claude/skills/python-llm-integration/SKILL.md
```

Expected output:
```
---
name: python-llm-integration
description: Expert guidance on using the Anthropic Python SDK...
---
```

---

### Task 4: python-data-science skill

**Files:**
- Create: `/Users/liuda/.claude/skills/python-data-science/SKILL.md`

**Interfaces:**
- Consumes: nothing
- Produces: `/Users/liuda/.claude/skills/python-data-science/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir /Users/liuda/.claude/skills/python-data-science
```

Expected: no output, exit 0.

- [ ] **Step 2: Write SKILL.md**

Write the following content exactly to `/Users/liuda/.claude/skills/python-data-science/SKILL.md`:

```markdown
---
name: python-data-science
description: Expert guidance on pandas and numpy for data analysis — vectorized operations, data cleaning, groupby, memory optimization, and visualization. Use when writing or reviewing DataFrame-heavy Python scripts or data pipelines.
---

# Python Data Science with pandas & numpy

## 1. Core Principle — Avoid Loops, Use Vectorization

```python
import pandas as pd
import numpy as np

# BAD — iterrows() is 100–1000x slower than vectorized ops
for i, row in df.iterrows():
    df.at[i, "available"] = row["seats"] > 0

# GOOD — vectorized
df["available"] = df["seats"] > 0
```

If you find yourself writing `for ... in df.iterrows()`, stop and find the vectorized equivalent.

## 2. Loading Data — Specify Types at Load Time

```python
df = pd.read_csv(
    "ticket_log.csv",
    parse_dates=["checked_at"],
    dtype={
        "train_id": "str",
        "seats_ordinary": "int16",
        "seats_green": "int16",
        "available": "bool",
    },
)
```

Always specify `dtype` and `parse_dates` at load time. This prevents silent type coercion bugs and reduces memory use.

## 3. Data Cleaning Checklist

```python
# 1. Check for nulls
print(df.isnull().sum())

# 2. Drop exact duplicates
df = df.drop_duplicates()

# 3. Coerce numeric columns safely (non-numeric → NaN, not error)
df["seats"] = pd.to_numeric(df["seats"], errors="coerce")

# 4. Fill or drop nulls with explicit intent
df["seats"] = df["seats"].fillna(0).astype("int16")

# 5. Assert invariants
assert df["seats"].between(0, 1000).all(), "Seat count out of expected range"
```

## 4. Groupby and Aggregation

```python
# Availability rate per train per hour of day
hourly = (
    df
    .assign(hour=df["checked_at"].dt.hour)
    .groupby(["train_id", "hour"])
    .agg(
        checks=("available", "count"),
        available_pct=("available", "mean"),
    )
    .reset_index()
)
```

Chain `.assign()` → `.groupby()` → `.agg()` → `.reset_index()` for readable, non-mutating pipelines.

## 5. Merging DataFrames

```python
# Always specify `on` and `how` explicitly
result = pd.merge(
    availability_df,
    train_schedule_df,
    on="train_id",
    how="left",
)

# Validate cardinality — left join should not fan out
assert len(result) == len(availability_df), "Unexpected fan-out in merge"
```

## 6. Memory Optimization

```python
# Downcast numerics — reduces memory 2–4x
df["seats"] = df["seats"].astype("int16")     # was int64
df["price"] = df["price"].astype("float32")   # was float64

# Category dtype for low-cardinality strings
df["seat_class"] = df["seat_class"].astype("category")

# Check current usage
print(f"{df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# Read large files in chunks
chunks = pd.read_csv("large_log.csv", chunksize=10_000)
result = pd.concat([process(chunk) for chunk in chunks], ignore_index=True)
```

## 7. Saving Results

```python
# CSV — portable, human-readable
df.to_csv("output.csv", index=False)

# SQLite — queryable, good for append logs
import sqlite3
with sqlite3.connect("ticket_log.db") as conn:
    df.to_sql("availability", conn, if_exists="append", index=False)

# Parquet — fast, compressed, preserves dtypes (best for analysis)
df.to_parquet("output.parquet", index=False)
```

## 8. Ticket Availability Heatmap

```python
import matplotlib.pyplot as plt

pivot = hourly.pivot(index="hour", columns="train_id", values="available_pct")

fig, ax = plt.subplots(figsize=(12, 5))
im = ax.imshow(pivot.T, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
ax.set_xticks(range(24))
ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Train ID")
plt.colorbar(im, label="Availability Rate (0=none, 1=always)")
plt.title("JR Ticket Availability by Hour")
plt.tight_layout()
plt.savefig("availability_heatmap.png", dpi=150)
```

## 9. Checklist
- [ ] No `iterrows()` — vectorize or use `.apply()` as last resort
- [ ] Specify `dtype` and `parse_dates` at `read_csv()` time
- [ ] Validate merge cardinality with `assert`
- [ ] Log memory: `df.memory_usage(deep=True).sum() / 1e6` MB
- [ ] Store running logs in SQLite; export final results as CSV or Parquet
- [ ] Install: `pip install pandas numpy matplotlib`
```

- [ ] **Step 3: Verify the file exists**

```bash
head -5 /Users/liuda/.claude/skills/python-data-science/SKILL.md
```

Expected output:
```
---
name: python-data-science
description: Expert guidance on pandas and numpy...
---
```

---

### Task 5: python-testing skill

**Files:**
- Create: `/Users/liuda/.claude/skills/python-testing/SKILL.md`

**Interfaces:**
- Consumes: nothing
- Produces: `/Users/liuda/.claude/skills/python-testing/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir /Users/liuda/.claude/skills/python-testing
```

Expected: no output, exit 0.

- [ ] **Step 2: Write SKILL.md**

Write the following content exactly to `/Users/liuda/.claude/skills/python-testing/SKILL.md`:

```markdown
---
name: python-testing
description: Expert guidance on pytest for Python projects — async testing, fixtures, parametrize, Playwright page.route() mocking, and FastAPI TestClient. Use when writing, structuring, or reviewing tests for Python automation scripts or web APIs.
---

# Python Testing with pytest

## 1. Project Structure

```
tests/
├── conftest.py           # Shared fixtures (browser, event_loop, settings override)
├── fixtures/
│   └── search_results.html  # Saved HTML snapshots for parser tests
├── unit/
│   ├── test_retry.py
│   └── test_parser.py
├── integration/
│   └── test_booking_flow.py
└── e2e/
    └── test_full_run.py
```

Run unit tests in CI (fast, no browser). Run e2e tests locally or in a dedicated environment.

## 2. pytest.ini — Enable asyncio_mode

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
```

With `asyncio_mode = auto`, all `async def test_*` functions run as async tests automatically. No `@pytest.mark.asyncio` decorator needed per test.

## 3. conftest.py — Browser Lifecycle Fixtures

```python
# tests/conftest.py
import pytest
import asyncio
from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        yield b
        await b.close()

@pytest.fixture
async def page(browser):
    ctx = await browser.new_context()
    pg = await ctx.new_page()
    yield pg
    await ctx.close()
```

Use `scope="session"` for the browser (expensive startup). Use `scope="function"` (default) for pages — each test gets a clean state.

## 4. Playwright page.route() — Mock External Requests

Intercept real network calls and serve saved HTML fixtures instead:

```python
from pathlib import Path

async def test_availability_parser(page):
    # Intercept JR website requests and serve a local fixture
    await page.route(
        "**/jr-reservation.eki-net.com/**",
        lambda route: route.fulfill(
            status=200,
            content_type="text/html",
            body=Path("tests/fixtures/search_results.html").read_text(),
        ),
    )
    result = await parse_availability(page)
    assert result["14:00"]["ordinary"] == 3
    assert result["14:00"]["green"] == 1
```

Save fixture HTML files by running the real flow once and writing `await page.content()` to a file.

## 5. Parametrize — Multiple Scenarios in One Test

```python
import pytest

@pytest.mark.parametrize("date,train_id,expected_ordinary", [
    ("2025-08-01", "NOZOMI-300", 5),
    ("2025-08-01", "HIKARI-500", 0),
    ("2025-08-15", "NOZOMI-300", 12),
])
async def test_seat_count(date, train_id, expected_ordinary, page):
    await setup_fixture_for(page, date, train_id)
    result = await get_available_seats(page, date, train_id)
    assert result["ordinary"] == expected_ordinary
```

## 6. Testing Retry Logic

```python
async def test_retry_succeeds_on_third_attempt():
    call_count = 0

    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("simulated timeout")
        return "booked"

    result = await retry(flaky, max_attempts=5, base_delay=0.01)
    assert result == "booked"
    assert call_count == 3
```

## 7. FastAPI TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_status_endpoint():
    response = client.get("/status/")
    assert response.status_code == 200
    data = response.json()
    assert data["running"] is True
    assert "interval_seconds" in data
```

For async routes with async dependencies, use `httpx.AsyncClient` with `transport=ASGITransport(app=app)` instead.

## 8. Mocking with pytest-mock

```python
def test_line_notification_sent_on_success(mocker):
    mock_post = mocker.patch("app.routers.webhook.httpx.post")

    response = client.post("/notify?message=Ticket+found")

    assert response.status_code == 200
    mock_post.assert_called_once()
    assert "Ticket found" in mock_post.call_args.kwargs["data"]["message"]
```

Prefer `mocker.patch` (pytest-mock) over `unittest.mock.patch` — it auto-cleans up after each test and has a cleaner API.

## 9. Checklist
- [ ] `asyncio_mode = auto` in `pytest.ini`
- [ ] Browser fixture `scope="session"`, page fixture `scope="function"`
- [ ] Network calls mocked with `page.route()` — no real HTTP in unit/integration tests
- [ ] Fixture HTML files saved in `tests/fixtures/`
- [ ] Run fast tests: `pytest tests/unit/ -v`
- [ ] Run all: `pytest -v`
- [ ] Install: `pip install pytest pytest-asyncio pytest-mock playwright`
```

- [ ] **Step 3: Verify the file exists**

```bash
head -5 /Users/liuda/.claude/skills/python-testing/SKILL.md
```

Expected output:
```
---
name: python-testing
description: Expert guidance on pytest for Python projects...
---
```

---

### Final Verification

- [ ] **Confirm all five skills are present**

```bash
ls /Users/liuda/.claude/skills/ | grep python
```

Expected output:
```
python-automation
python-data-science
python-fastapi
python-llm-integration
python-testing
```

- [ ] **Confirm openspec change files are intact**

```bash
ls /Users/liuda/VsCodeProjects/JR_ticket_auto/openspec/changes/add-python-skills/
```

Expected: `design.md  proposal.md  tasks.md`
