# select-seat

## What
After clicking "Buy tickets", eki-net shows a Seat Selection page with the train info and a "View reservation details" button. This change automates proceeding past that page by waiting for it to load and clicking the confirm button, using the pre-selected default seat condition (Adjacent seats only).

## Why
Phase 4 ended at ticket type selection. This phase bridges to the next booking step by automatically confirming the seat selection page without requiring manual intervention.

## Mode: Simple
Simple: no new tests; existing tests must still pass.
