# eki-net-booker-phase1 — Design

## Goal
Scaffold the JR ticket automation project and implement the first execution phase: open browser → login to eki-net → wait until sale_open_time.

## Approach
Use async Playwright for browser automation. Each concern lives in its own module under `booker/` (browser lifecycle, login, scheduling) and `utils/` (config, logging, notifications). `main.py` orchestrates the sequence. The browser is never closed automatically — on success it waits for the user to close manually; on failure it stays open for inspection.

## Key Decisions
- **Login on startup**: Browser launches and login runs immediately when the script starts, not at T-30s. Allows running the script well in advance and letting it idle.
- **Flexible `sale_open_time` format**: Parser supports `YYYY/M/D HH:MM` (primary) with fallback to `YYYY-MM-DD HH:MM:SS` for backwards compatibility.
- **Browser stays open**: `BrowserManager` exposes no auto-close in the happy path or error path; `page.wait_for_close()` is used so the user controls teardown.
- **JST timezone**: All time comparisons are done in `Asia/Tokyo` via `zoneinfo`.

## File Structure
- `main.py` — async entry point; orchestrates startup → login → wait
- `booker/__init__.py` — empty package marker
- `booker/browser.py` — `BrowserManager`: `start()`, `screenshot()`, `close()`
- `booker/login.py` — `login(page, config)`: navigate, fill credentials, verify success
- `booker/scheduler.py` — `wait_until(dt)`, `parse_sale_open_time(raw)`
- `utils/__init__.py` — empty package marker
- `utils/config_loader.py` — `load_config(path)`: reads and validates `config.yaml`
- `utils/logger.py` — `get_logger(name)`: file + console handler, timestamped log file
- `utils/notify.py` — `notify_success(path)`, `notify_failure(msg)`: macOS notifications + sound
- `config.yaml` — live config (gitignored): account credentials, sale_open_time
- `config.example.yaml` — committed example with placeholder values
- `requirements.txt` — playwright, pyyaml, zoneinfo (stdlib), playsound or similar

## Out of Scope
- `booker/search.py`, `booker/selector.py`, `booker/payment.py` — Phase 2
- `utils/retry.py` and per-step retry logic — Phase 2
- Multiple train options / fallback trains — Phase 2
- Any web UI or API layer
