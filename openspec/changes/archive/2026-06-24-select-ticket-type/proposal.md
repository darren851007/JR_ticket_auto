# select-ticket-type

## What
After selecting a train, eki-net shows a "Buy tickets" page with two options: a regular magnetic ticket and a Shinkansen e-ticket. This change automates clicking the correct option based on `config.yaml`. The regular ticket flow is implemented; the e-ticket flow raises `NotImplementedError`.

## Why
Phase 3 ended at train selection. This phase bridges to the next booking step by automating the ticket type choice, which differs in flow and price between the two options.

## Mode: Simple
Simple: no new tests; existing tests must still pass.
