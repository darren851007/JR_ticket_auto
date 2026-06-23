# select-train — Design

## Goal
Select the configured train and seat class from the eki-net search results page and click Select.

## Approach
Create `booker/train_select.py` with `select_train(page, config)`. After waiting for `#trainSearch_result`, scan all `h3.ts_resultTrainName` elements for a text match against `config.train.name` (case-insensitive). If no match, parse each train's departure time from `li.ts_resultDetailOutlineWItemDep` and pick the one closest to `config.train.departure_time`. Once the target train index N is determined, expand its seat list if collapsed, click the radio label matching `config.train.seat_class`, then click `button#SelectN`. Add a `train` block to `config.yaml` and call `select_train` from `main.py` after `fill_search_form`.

## Key Decisions
- **Name match is case-insensitive substring**: "toki 307" matches "Toki 307号" — handles minor formatting differences.
- **Departure time fallback**: parse "HH:MM" from `li.ts_resultDetailOutlineWItemDep` text (e.g., "11:40→13:21"), compute absolute delta to target, pick minimum.
- **Expand before selecting**: if the train's seat panel has `style="display: none;"`, click `button.ts_DetailTrainCheckBtn` for that train first, then wait for the panel to become visible.
- **Seat class mapping** in `TRAIN_SELECT` selectors: `reserved` → label containing "Reserved seat" (excluding TRAIN DESK), `non_reserved` → "Non-reserved seat", `green` → "Green", `gran_class` → "GranClass".
- **Select button**: `button#Select{N}` where N = 0-based index of matched train.
- **Selectors in `TRAIN_SELECT` dict**: follows existing `LOGIN` / `SEARCH_FORM` pattern in `selectors.py`.

## File Structure
- **Create** `booker/train_select.py` — `select_train(page, config)` coroutine
- **Modify** `booker/selectors.py` — add `TRAIN_SELECT` dict
- **Modify** `config.yaml` — add `train` block
- **Modify** `main.py` — call `select_train(page, config)` after `fill_search_form`

## Out of Scope
- Navigating to next/previous page of results
- Handling sold-out seat classes
- Waiting for the page after clicking Select
- Validating that the selected train actually exists before sale opens
