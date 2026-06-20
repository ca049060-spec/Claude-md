# Resonance Phase 4.1 Report

## Summary

Phase 4.1 repairs the Phase 4 weakness by moving from retrospective-only backtests to a prospective signal registry.

The model is now split into:

1. historical cascade teaching mode
2. current-signal registry mode

## What changed

- Added a frozen registry for current signals.
- Added a review script for matured signals.
- Added a scoring display script for registered signals.
- Added a registration helper script.
- Added a conservative no-hindsight audit script.
- Added a baseline comparison placeholder that refuses accuracy claims until signals mature.
- Added schemas and Claude skills for registry/audit use.

## First registered signal

`psig-20260616-ai-generated-content-flood`

Label:

`act_watch`

Confidence:

`0.57`

Review date:

`2026-08-15`

## Why this matters

The model no longer needs to pretend old cases prove forecasting skill.

It now records current signals before outcomes are known and waits for review.

## Current expected script results

Before 2026-08-15:

- `review_matured_signals.py` should report 0 matured signals.
- `audit_hindsight_leakage.py` should report no obvious field-level leakage.
- `compare_to_baselines.py` should report that baseline comparison is not valid yet.
- `score_live_signal.py psig-20260616-ai-generated-content-flood` should display the frozen score.

## Boundary

Phase 4.1 does not prove prediction power.

It creates the conditions under which prediction usefulness can be tested later.
