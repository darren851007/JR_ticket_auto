# wait-with-refresh

## What
在登入後、售票時間開始前的等待期間，每 5 秒印一次倒數 log 並重整頁面，直到售票時間到達為止。修改 `wait_until` 函式加入 optional `page` 參數，`main.py` 傳入 page 即可啟用重整行為。

## Why
搶票頁面可能因長時間未操作而失效或過期。每 5 秒重整頁面可確保頁面狀態保持最新，提升售票一開始即可立刻操作的成功率。

## Mode: Simple
Simple：不新增測試；現有測試必須通過。
