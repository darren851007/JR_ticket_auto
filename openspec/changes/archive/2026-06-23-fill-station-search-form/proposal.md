# fill-station-search-form

## What
Implement automated filling of the eki-net Station Search form after login. The script reads departure station, arrival station, date, time, time type, adults, and children from `config.yaml`, fills each field via Playwright, and clicks the Search button.

## Why
Phase 1 ended at the Station Search form appearing. This phase automates the form filling so the booking flow can proceed without manual intervention when the sale opens.

## Mode: Simple
Simple: no new tests; existing tests must still pass.
