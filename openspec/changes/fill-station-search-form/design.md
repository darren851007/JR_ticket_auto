# fill-station-search-form — Design

## Goal
Fill the eki-net Station Search form from config and submit it.

## Approach
Add a `search` block to `config.yaml` with all form parameters. Create `booker/search_form.py` with a single `fill_search_form(page, config)` coroutine that fills each field via Playwright selectors and submits. Station name inputs are set directly via `page.evaluate()` (JS) with `input` and `change` events dispatched. Date is formatted from `M/D` + current JST year to `YYYYMMDD` for the select option. Minutes are rounded to the nearest 5. Call `fill_search_form` from `main.py` after `login()`.

## Key Decisions
- **JS direct-set for station inputs**: clicking the input triggers a popup modal; bypassing it via `page.evaluate()` is simpler and sufficient for automation.
- **Date format `M/D` in config**: year is auto-filled from current JST year, keeping config minimal.
- **Minute rounding**: `#DdlBoardingDate` minute select only has 5-minute increments; round `config.search.time` minutes to nearest 5.
- **Selectors in `SEARCH_FORM` dict**: follows existing `LOGIN` dict pattern in `selectors.py`.

## File Structure
- **Create** `booker/search_form.py` — `fill_search_form(page, config)` coroutine
- **Modify** `booker/selectors.py` — add `SEARCH_FORM` dict with all form field selectors
- **Modify** `config.yaml` — add `search` block
- **Modify** `main.py` — call `fill_search_form(page, config)` after `login(page, config)`

## Out of Scope
- Handling the station autocomplete popup
- Validating that the station name exists on eki-net
- Waiting for search results after clicking Search
- Round-trip / return journey support
