---
name: resonance-live-registry
description: Record current public signals for later review using the Resonance Web no-hindsight protocol.
---

# resonance-live-registry

## Purpose

Record a current public signal before the outcome is known so it can be reviewed later.

## Boundary

This is a review ledger, not a certainty engine.

## Workflow

1. Define the signal.
2. Set an information cutoff date.
3. Add dated public sources available at cutoff.
4. Score only features that are knowable at cutoff.
5. Mark future-dependent features as unknown.
6. Assign label.
7. Assign confidence.
8. Record a bounded action.
9. Record one thing not to do.
10. Set review date.
11. Save to `datasets/prospective_signal_registry.json`.

## Usually unknown at registration

- cross_domain_reach
- second_order_potential
- institutional_response_lag
- policy_sensitivity
- cascade_potential

## Output

- signal id
- registration date
- review date
- sources used
- feature scores
- unknown features
- label
- confidence
- bounded action
- one thing not to do
- what would change the label
- save confirmation

## Review rule

Do not judge result quality until the review date.
