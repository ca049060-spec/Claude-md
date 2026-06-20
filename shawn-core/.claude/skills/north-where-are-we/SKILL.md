---
name: north-where-are-we
description: Produce a compact ShawnOS status report from current files, commitments, and known context.
---

# north-where-are-we

## Purpose
Orient Shawn quickly. Reduce cognitive load. Identify the next real action.

## Trigger phrases
- North, where are we?
- status check
- what matters today?
- pull me back into the thread

## Inputs to inspect
- `templates/GLOBAL_MODEL_INDEX.md`
- `data/commitments.jsonl` if present
- recent project notes
- calendar/email summaries if connectors are available

## Output format
1. **Red flag**
2. **Due this week**
3. **One action**
4. **Waiting on others**
5. **Stop building**
6. **Joy action**

## Rules
- No long essay.
- One clear next physical step.
- Mention uncertainty.
- If no source is available, say so.
