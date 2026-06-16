---
name: commitment-ledger
description: Convert decisions into explicit commitments with owner, due date, status, and proof-of-change.
---

# commitment-ledger

## Purpose
Stop decisions from dissolving into memory.

## Use when
- Shawn says "I'll do..."
- a legal/medical/business action gets identified
- a task needs external-world follow-up
- a decision has a date, owner, or consequence

## Commitment schema
```json
{"created":"YYYY-MM-DD","lane":"Legal / MTO","commitment":"text","owner":"Shawn","due":"YYYY-MM-DD","status":"open","external_proof":"","notes":""}
```

## Procedure
1. Identify the commitment.
2. Ask only if owner/date is genuinely unclear.
3. Add to `data/commitments.jsonl` or produce the JSONL line.
4. Define proof of completion.
5. Schedule review only when supported.

## Anti-overbuilding
No dashboards until the JSONL file has at least 10 real commitments and 3 completed items.
