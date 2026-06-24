# wait-with-refresh — Design

## Goal
讓 `wait_until` 在等待售票時間期間，每輪同時重整瀏覽器頁面。

## Approach
為 `wait_until(target_dt, page=None)` 加入 optional `page` 參數。每輪 loop 先印倒數 log（`距離開始搶票時間還剩: {remaining:.0f}s`），若 page 不為 None 則呼叫 `await page.reload()`，再 sleep `min(5, remaining)` 秒。`main.py` 將 `page` 傳入即可啟用；不傳則行為與現在完全相同（向後相容）。

## Key Decisions
- `page` 為 optional，預設 `None`：不破壞現有呼叫方式，scheduler.py 保持向後相容。
- 重整在 log 之後、sleep 之前：確保每輪先記錄狀態再行動。
- `await page.reload()` 不等待特定 selector：重整後直接 sleep，不阻塞等待頁面完全載入（下一步 fill_search_form 自己有 wait_for）。
- log 格式改為繁體中文「距離開始搶票時間還剩: Xs」。

## File Structure
- Modify: `booker/scheduler.py` — `wait_until` 加 `page` 參數與重整邏輯
- Modify: `main.py` — 呼叫 `wait_until(sale_time, page=page)`

## Out of Scope
- 重整後等待特定頁面元素出現
- 可設定重整間隔（固定 5 秒）
- e-ticket 流程
