---
name: resonance-no-hindsight-audit
description: Check prospective Resonance records for fields that may have been scored using outcome knowledge.
---

# resonance-no-hindsight-audit

## Purpose

Audit current-signal records for accidental hindsight leakage.

## Check

High-risk future-dependent fields should usually be marked unknown at registration time:

- cross_domain_reach
- second_order_potential
- institutional_response_lag
- policy_sensitivity
- cascade_potential

## Use when

- a new signal is added
- a signal is reviewed
- the model seems overconfident
- fields were scored without clear cutoff evidence

## Output

1. number of records checked
2. records with possible leakage
3. fields that should be unknown
4. suggested correction
5. whether the record remains usable

## Rule

If a feature needs the future to know it, do not score it at registration.
