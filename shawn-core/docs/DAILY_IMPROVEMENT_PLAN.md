# ShawnOS Daily Improvement Plan

**Purpose**: A sequenced, living plan for improving ShawnOS daily — from the frontier of AI capability into real-world change in Shawn's 8 lanes.

**Rule**: One thing per session. Done means something changed outside the chat.

**Last updated**: 2026-06-30

---

## Where We Are Now

ShawnOS is at **v0.1 draft**. The foundation exists and is solid:

- 13 skills installed
- 6-agent council (Witness, Vale, V, Heart, North, Nika — Nika was just added)
- Resonance Web Phase 4.1 running with 1 registered signal
- Schemas for commitments, signals, evidence, sources
- MCP connectors live: Gmail, Google Drive, Google Calendar (available in Claude Code web sessions)

What is NOT yet true: ShawnOS has not yet produced real-world change in at least 3 lanes. That is the v1.0 gate. Everything between here and there is the plan.

---

## The Daily Ritual

Every session starts with three commands in this order:

```
1. North, where are we?          → north-where-are-we skill
2. What's the frontier finding?  → ai-frontier-scout agent
3. What do we build today?       → daily-build-planner agent
```

Total time: 10 minutes. Then build one thing.

---

## Phase 1 — Complete the Foundation
**Target: 1 week**

These are things that are started but not done. Finish them before adding anything new.

### Day 1 (Done in this session)
- [x] Add missing Nika agent (synthesis and governance)
- [x] Add AI Frontier Scout agent
- [x] Add Daily Build Planner agent
- [x] Add Lane Status Reporter agent
- [ ] Run daily ritual for the first time: North → Scout → Planner

### Day 2 — Resonance Verification
Run the Phase 4.1 verification script suite (see `CLAUDE_NEXT_STEPS_RESONANCE_4_1.md`):
```
python shawn-core\scripts\score_live_signal.py psig-20260616-ai-generated-content-flood
python shawn-core\scripts\review_matured_signals.py
python shawn-core\scripts\audit_hindsight_leakage.py
python shawn-core\scripts\compare_to_baselines.py
```
Done when: all 4 scripts run and return expected output.

### Day 3 — Second Resonance Signal
Register one new current public signal using the `resonance-live-registry` skill.
Pick something visible right now (AI, legal, health, markets) that has a 30-90 day review date.
Done when: second entry appears in `datasets/prospective_signal_registry.json`.

### Day 4 — First Real Commitment
Pick one overdue or active thing in any lane. Run `commitment-ledger`. Enter it.
Done when: JSONL file has one real commitment with due date, owner, and proof-of-change path.

### Day 5 — First Lane Status Report
Run `lane-status-reporter`. Report all 8 lanes even if most are UNKNOWN.
Done when: a report exists with at least one lane showing real data (not placeholder).

### Day 6 — One External-World Action
Take the RED lane from Day 5 and do the one next action.
Done when: appointment booked, document sent, calendar updated, or similar external change.

### Day 7 — Full Council Run
Bring a real decision (anything from the 8 lanes) to all 6 agents.
Run: Witness → Vale → V → Heart → North → Nika.
Done when: Nika produces one governing decision and one action is taken.

---

## Phase 2 — v0.2: Lane Infrastructure
**Target: Week 2**

Goal: make it easy to see status and update commitments without friction.

### Build: Commitment JSONL Editor Script
A simple Python script that can:
- `add` a commitment (prompts for fields)
- `list` open commitments by lane
- `close` a commitment with proof

Location: `shawn-core/scripts/commitment_editor.py`

### Build: Lane Status from Real Data
After Phase 1 Day 5, iterate the lane-status-reporter to pull from actual JSONL.
Done when: lane status auto-populates from commitment ledger without manual input.

### Build: Import/Export
Simple script to export commitment ledger as CSV for review.
Location: `shawn-core/scripts/export_commitments.py`

---

## Phase 3 — v0.3: External World Connections
**Target: Week 3-4**

These MCP servers are already connected in Claude Code web sessions:
- **Gmail** — search threads, create drafts
- **Google Drive** — read files, search, create
- **Google Calendar** — list events, create events, suggest times

### Build: Calendar Deadline Guard
When a commitment has a due date, create a Google Calendar event with a 2-day reminder.
Trigger: after `commitment-ledger` creates a JSONL entry.
Done when: one real calendar event is created from a real commitment.

### Build: Drive Source Manifest Builder
When using `source-sweep`, write a source manifest JSON to a specific Drive folder.
Done when: one source manifest is stored in Drive and retrievable.

### Build: Gmail Draft on Commitment Overdue
If a commitment passes its due date, auto-draft a follow-up email for Shawn to review.
Done when: one overdue commitment generates a real Gmail draft.

---

## Phase 4 — v1.0: Living Proof
**Target: Month 2**

Gate: real external-world change in at least 3 lanes.

### Lane Proof Targets

| Lane | Proof of Change |
|------|----------------|
| Legal / MTO | Document submitted or appointment confirmed via commitment ledger |
| Money / Investments | One VACS+ analysis completed with a real buy/hold/skip decision logged |
| Seals Go Pro | One `seals-session-close` with customer contact logged and follow-up drafted |
| Health / TBI | One MTO review pack organized and meeting held |
| AI / NIKA / North | Two Resonance signals registered and one reviewed at maturity |

### One-Week Use Log
Keep a simple JSONL log of every session:
```json
{"date": "2026-07-01", "lane": "legal", "skill_used": "mto-review-pack", "external_change": "appointment booked"}
```
Done when: 7 consecutive days of logged sessions.

### Privacy Review
Run `privacy-redactor` on the entire repo before tagging v1.0.
Done when: no private data found or all flagged items removed.

---

## AI Frontier: What to Watch and Build

These are the cutting-edge capabilities (as of June 2026) most relevant to ShawnOS.

### 1. Multi-Agent Parallel Council
**What**: Run all 6 council lenses simultaneously instead of sequentially.
**Why it matters**: Full council analysis in seconds instead of minutes.
**How to build it**: Use Claude Code's workflow system with `parallel()` to fan out all 6 agents at once, then synthesize with Nika.
**Effort**: Medium — needs a workflow script.
**When**: Phase 2.

### 2. Extended Thinking for Resonance
**What**: Claude Opus 4.8 with extended thinking does multi-step reasoning before committing to an answer.
**Why it matters**: Resonance signal analysis is exactly this problem — weigh uncertain features, avoid hindsight.
**How to build it**: Use `model: claude-opus-4-8` with `thinking: enabled` in the resonance-web-map skill.
**Effort**: Easy — model switch in one skill.
**When**: Phase 1, Day 3.

### 3. MCP Memory (Drive as Persistent Store)
**What**: Google Drive MCP is already connected. Use it as external memory for commitments and signals.
**Why it matters**: ShawnOS state survives session resets if stored in Drive, not just in local files.
**How to build it**: After each session, write commitment JSONL and signal registry to a specific Drive folder.
**Effort**: Medium — needs write wrappers.
**When**: Phase 3.

### 4. Autonomous Daily Scan (CronCreate)
**What**: Schedule a daily run of AI Frontier Scout + Lane Status Reporter.
**Why it matters**: Shawn gets a daily push notification with system status and one frontier finding, without opening Claude Code.
**How to build it**: Use CronCreate to schedule a daily run, output to Drive, push notification with PushNotification tool.
**Effort**: Medium.
**When**: After Phase 2 is stable.

### 5. Structured JSON Output on All Skills
**What**: Skills return typed JSON matching the existing schemas instead of freeform text.
**Why it matters**: Skills can chain — VACS+ output can feed directly into commitment-ledger without copy-paste.
**How to build it**: Update each skill to use schema validation and return JSON.
**Effort**: Low per skill, cumulative.
**When**: One skill per week, starting Phase 2.

---

## Anti-Overbuilding Checklist

Before building anything, ask:

1. Is an existing tool unused that would solve this? → Use it first.
2. Has this workflow repeated 3 times? → If not, don't make it a skill yet.
3. Does this produce external-world change? → If it only produces text, don't build it.
4. Can it be done in one session? → If not, scope it to the first step only.
5. What is Nika's governance verdict? → If RED, stop.

---

## Daily Log

| Date | Phase | Task | Done? | External Change |
|------|-------|------|-------|-----------------|
| 2026-06-30 | 1 | Add 4 new agents + this plan | ✓ | Agents committed to repo |

---

## Council Notes on This Plan

**Vale says**: The v1.0 gate (real proof in 3 lanes) is the only one that matters. Everything else is infrastructure. Don't let Phase 2 and 3 become the goal.

**North says**: Run the daily ritual every session. One command, one build, one external action. That's the whole system.

**Nika says**: System health is AMBER. Foundation is solid, but no external proof yet. First real commitment entry moves it to GREEN.
