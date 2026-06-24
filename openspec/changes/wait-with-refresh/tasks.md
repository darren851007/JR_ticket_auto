# wait-with-refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在等待售票時間期間，每 5 秒印倒數 log 並重整瀏覽器頁面。

**Architecture:** 修改 `wait_until` 加入 optional `page` 參數；有傳入時每輪呼叫 `page.reload()`。`main.py` 傳入 `page` 啟用重整行為，不傳則維持原有行為（向後相容）。

**Tech Stack:** Python asyncio, Playwright async API (`Page.reload()`)

## Global Constraints

- Python 3.11+
- Playwright `Page` type 來自 `playwright.async_api`
- `page` 參數必須為 optional（預設 `None`），不可破壞現有呼叫方式
- log 訊息格式：`距離開始搶票時間還剩: {remaining:.0f}s`

---

### [x] Task 1: 修改 `wait_until` 加入頁面重整邏輯，並更新 `main.py`

**Files:**
- Modify: `booker/scheduler.py`
- Modify: `main.py`

**Interfaces:**
- Produces: `async def wait_until(target_dt: datetime, page=None) -> None`

- [x] **Step 1: 修改 `booker/scheduler.py`**

將 `wait_until` 改為以下內容（完整替換整個函式）：

```python
async def wait_until(target_dt: datetime, page=None) -> None:
    now = datetime.now(tz=JST)
    delta = (target_dt - now).total_seconds()
    if delta <= 0:
        logger.warning("sale_open_time is in the past — proceeding immediately")
        return
    logger.info(f"Waiting {delta:.1f}s until {target_dt.strftime('%Y-%m-%d %H:%M:%S')} JST")
    while True:
        remaining = (target_dt - datetime.now(tz=JST)).total_seconds()
        if remaining <= 0:
            break
        logger.info(f"距離開始搶票時間還剩: {remaining:.0f}s")
        if page is not None:
            await page.reload()
        await asyncio.sleep(min(5, remaining))
```

- [x] **Step 2: 修改 `main.py`**

將第 29 行：
```python
        await wait_until(sale_time)
```
改為：
```python
        await wait_until(sale_time, page=page)
```

- [x] **Step 3: 確認現有測試仍通過**

```bash
pytest --tb=short -q
```

若無測試檔案，輸出應為 `no tests ran`，視為通過。

- [x] **Step 4: Commit**

```bash
git add booker/scheduler.py main.py
git commit -m "feat: refresh page every 5s while waiting for sale time"
```
