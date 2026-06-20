---
name: source-sweep
description: Run a bounded source review across approved sources and return a provenance-safe index.
---

# source-sweep

## Purpose
Find relevant source material without swallowing the whole archive.

## Inputs
- lane
- query
- date range if known
- approved source type

## Output
- top source items
- relevance reason
- freshness/currency
- privacy risk
- next action

## Rules
- Search narrowly first.
- Deduplicate.
- Prefer source manifests over copying private contents.
- Stop when enough evidence exists for the decision.
