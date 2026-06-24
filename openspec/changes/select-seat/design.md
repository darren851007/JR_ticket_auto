# select-seat — Design

## Goal
Wait for the Seat Selection page to load, then click "View reservation details" to proceed.

## Approach
Create `booker/seat_select.py` with `select_seat(page, config)`. It waits for `#BtnToNext` to become visible (`timeout=0`), sleeps 0.5 seconds, clicks it, then waits for `domcontentloaded`. Add `SEAT_SELECT` to `selectors.py` and wire into `main.py` after `select_ticket_type`. No config changes needed — the page defaults to Adjacent seats which is sufficient.

## Key Decisions
- **No seat condition config**: the page pre-selects "Adjacent seats only"; no click needed before confirming. Keeps the implementation minimal.
- **`#BtnToNext` as both anchor and action**: it appears as soon as the page loads, so it doubles as the page-ready signal and the click target.
- **0.5s delay before click**: consistent with the pattern used in `login.py` and `ticket_type_select.py` to avoid race conditions on freshly loaded pages.
- **Seat map not implemented**: `#BtnSelectWithSeatMap` opens a popup with a different flow; out of scope.

## File Structure
- **Modify** `booker/selectors.py` — add `SEAT_SELECT` dict
- **Create** `booker/seat_select.py` — `select_seat(page, config)` coroutine
- **Modify** `main.py` — import and call `select_seat` after `select_ticket_type`

## Out of Scope
- Seat map popup flow
- Configuring seat condition (adjacent / any / 2-row)
- Configuring car position (any / near ends / away from ends)
