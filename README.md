# JR Ticket Auto

eki-net（JR East）新幹線車票自動購票程式，使用 Python async Playwright 驅動瀏覽器完成整個訂票流程。

## 功能

自動執行以下步驟：

1. 登入 eki-net
2. 等待售票開始時間
3. 填寫出發/到達車站、日期、時刻、人數
4. 選擇指定列車
5. 選擇票種（目前僅支援一般磁票）
6. 確認座位
7. 確認收據資訊
8. 同意服務條款
9. 填入信用卡資料並送出購買

## 環境需求

- Python 3.11+
- Chromium（由 Playwright 管理）

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## 設定

複製範例設定檔並填入您的資料：

```bash
cp config.example.yaml config.yaml
```

`config.yaml` 欄位說明：

```yaml
account:
  email: ""         # eki-net 帳號
  password: ""      # eki-net 密碼

sale_open_time: "2026/7/1 10:00"   # 售票開始時間 (JST)，格式：YYYY/M/D HH:MM

search:
  departure_station: "TOKYO"
  arrival_station:   "NAGAOKA"
  date:              "7/1"         # M/D
  time:              "12:40"       # HH:MM
  time_type:         "departure"   # departure | arrival
  adults:            2
  children:          0

train:
  name:           "Toki 307"       # 列車名稱（優先比對，大小寫不分）
  departure_time: "10:04"          # 出發時刻 fallback，HH:MM
  seat_class:     "reserved"       # reserved | non_reserved | green | gran_class

ticket_type: "regular"             # regular（e_ticket 尚未實作）

payment:
  card_number:   ""                # 16 位數字
  card_type:     "VISA"            # VISA | Master | JCB | AMEX | VIEW | Diners | VIEW Company
  expiry_month:  "01"              # MM
  expiry_year:   "27"              # YY（2 位數，例如 2027 → "27"）
  security_code: ""                # 3-4 位數字
```

> **注意：** `config.yaml` 包含帳號密碼與信用卡資料，已加入 `.gitignore`，請勿提交至版本控制。

## 執行

```bash
python main.py
```

程式會開啟 Chromium 視窗，執行完購買流程後瀏覽器保持開啟。按 `Ctrl+C` 結束。

發生錯誤時會在 `screenshots/` 儲存截圖，並於 `logs/` 記錄詳細 log。

## 專案結構

```
├── main.py                  # 主程式，串接所有步驟
├── config.yaml              # 設定檔（不追蹤）
├── config.example.yaml      # 設定範例
├── requirements.txt
├── booker/
│   ├── browser.py           # Playwright 瀏覽器管理
│   ├── login.py             # 登入
│   ├── scheduler.py         # 等待售票時間
│   ├── search_form.py       # 填寫搜尋表單
│   ├── train_select.py      # 選擇列車
│   ├── ticket_type_select.py# 選擇票種
│   ├── seat_select.py       # 確認座位
│   ├── confirm_receipt.py   # 確認收據資訊
│   ├── agree_terms.py       # 同意服務條款
│   ├── payment.py           # 填寫付款資料並送出
│   └── selectors.py         # 所有 CSS/XPath 選擇器
└── utils/
    ├── config_loader.py     # 讀取 config.yaml
    ├── logger.py            # 日誌設定
    └── notify.py            # 失敗通知
```
