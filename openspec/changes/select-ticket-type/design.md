# select-ticket-type — Design

## Goal
Read `config["ticket_type"]`, wait for the ticket type selection page, then click the matching button.

## Approach
Create `booker/ticket_type_select.py` with `select_ticket_type(page, config)`. It waits for `#BtnBuyATicketForMagneticTicket` (the page anchor, `timeout=0`), then branches on `config["ticket_type"]`: `"regular"` clicks that button and waits for `domcontentloaded`; `"e_ticket"` raises `NotImplementedError`; any other value raises `ValueError`. Add `TICKET_TYPE_SELECT` selectors to `selectors.py`, `ticket_type` field to `config.yaml`, and call the function from `main.py` after `select_train`.

## Key Decisions
- **Page anchor = regular button**: `#BtnBuyATicketForMagneticTicket` serves as both the page-ready signal and the click target for regular tickets — no separate wait selector needed.
- **e-ticket is NotImplementedError**: the two flows differ enough that e-ticket is a separate future change. Raising at runtime makes the gap explicit.
- **ValueError for unknown values**: fail loudly rather than silently defaulting.
- **Selectors in `TICKET_TYPE_SELECT` dict**: follows existing `LOGIN` / `SEARCH_FORM` / `TRAIN_SELECT` pattern.

## File Structure
- **Modify** `booker/selectors.py` — add `TICKET_TYPE_SELECT` dict
- **Create** `booker/ticket_type_select.py` — `select_ticket_type(page, config)` coroutine
- **Modify** `config.yaml` — add `ticket_type: "regular"` field
- **Modify** `main.py` — import and call `select_ticket_type` after `select_train`

## Out of Scope
- E-ticket flow implementation
- Parsing or verifying the price shown on the ticket selection page
- Handling the page that appears after clicking (next step)
