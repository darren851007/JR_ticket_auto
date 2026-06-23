# eki-net-booker-phase1

## What
Build the first phase of the JR Shinkansen ticket automation system targeting eki-net (JR East). This phase covers project scaffolding, browser startup, login, and waiting until the configured sale open time — everything needed before the actual booking flow begins.

## Why
The previous codebase was reset. A clean rebuild is needed with a more stable architecture: login happens immediately on startup (not T-30s before sale), `sale_open_time` supports a more natural `YYYY/M/D HH:MM` format, and the browser is never auto-closed so the user can inspect the state after failure or completion.

## Mode: Simple
Simple: no new tests; existing tests must still pass.
