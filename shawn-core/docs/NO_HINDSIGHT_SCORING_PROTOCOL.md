# No-Hindsight Scoring Protocol

## Purpose

Prevent the Resonance Web from pretending that retrospective knowledge is prediction.

## Core rule

Score only what could reasonably be known at the information cutoff.

If a feature requires outcome knowledge, mark it unknown.

## Required fields for every prospective signal

- id
- title
- registration_date
- review_date
- status
- information_cutoff
- public_sources_available_at_cutoff
- primary_domain
- secondary_domains
- first_visible_signal
- feature_scores
- unknown_features
- prediction_label
- confidence
- bounded_action
- one_thing_not_to_do
- what_would_change_label
- expected_review_question
- later_outcome
- review_notes
- accuracy_result

## High-risk future-dependent fields

These should usually be unknown at registration time unless directly observable:

- cross_domain_reach
- second_order_potential
- institutional_response_lag
- policy_sensitivity
- cascade_potential

## Act gate

Use `act` only when all are true:

- source_quality >= 0.75
- actionability >= 0.75
- harm_if_wrong <= 0.35, if scored
- reversibility >= 0.55, if scored
- confidence >= 0.55
- distortion_pressure is not extreme

If those are not met, use one of:

- bounded_act
- act_watch
- watch
- investigate
- pause
- ignore

## Bounded action examples

Allowed bounded actions:

- record the signal
- gather primary sources
- confirm a deadline
- call a relevant office
- reduce exposure
- set a review date
- avoid relying on unsourced summaries

Not allowed as default bounded action:

- panic buying
- large speculative trade
- major public claim
- personal escalation
- broad certainty claim

## Review rule

Do not judge accuracy before review_date.

At review date, classify as:

- useful
- wrong
- mixed
- untestable

Then compare to baselines.
