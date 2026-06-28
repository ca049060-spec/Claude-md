# AI Improvement Log

Daily record of the ShawnOS AI improvement cycle (Lane 7).
One entry per day. One improvement per day. Done means committed.

---

<!-- Format:
Date: YYYY-MM-DD
Candidate chosen: [name]
Outcome: KEEP / DISCARD / STOPPED
File committed: [path or none]
Lesson: [one sentence]
-->

## First 5 Days — Recommended Sequence

These are the five highest-value improvements to run first, in order.
Each is buildable in a single 45-minute session.

### Day 1 — Session Bridge Logger
**What**: A JSONL logger that captures key facts, commitments, and decisions at session end so North can reload context in a new session without re-reading the whole chat.
**Lane(s)**: All 8 (foundational)
**Start**: New file shawn-core/scripts/session-log.js or a new skill session-bridge.md
**Why first**: Every other improvement is undermined by session amnesia. Fix memory before building features.

### Day 2 — Drive/Gmail/Calendar Connector Wrappers
**What**: Thin wrapper skills for the MCP tools already connected (Google Drive, Gmail, Google Calendar). Each wrapper constrains the tool to ShawnOS use cases — no freeform queries.
**Lane(s)**: Legal/MTO, Health, Work/Income, Seals Go Pro
**Start**: shawn-core/.claude/skills/ — three new files: drive-fetch.md, gmail-thread.md, calendar-deadline.md
**Why second**: These MCP tools are already connected and sitting unused. One session turns them into real connectors.

### Day 3 — Parallel Evidence Finder
**What**: A multi-agent workflow that searches three evidence sources in parallel and returns a provenance-ranked list. Replaces manual source searching in the Legal/MTO lane.
**Lane(s)**: Legal/MTO
**Start**: New workflow shawn-core/workflows/evidence-sweep.js using pipeline() pattern
**Why third**: Highest-friction lane. Reduces one of Shawn's biggest manual burdens.

### Day 4 — Self-Audit Loop for Skills
**What**: A pattern that adds a one-step self-check at the end of any skill output before returning — "did this produce one clear external action?" Retrofitted to the 3 highest-use existing skills first.
**Lane(s)**: All (quality layer)
**Start**: Edit commitment-ledger.md, north-where-are-we.md, ebs-evidence-check.md
**Why fourth**: Existing skills don't verify their own output. This catches drift without adding a new agent.

### Day 5 — Lane Status Dashboard v0.2
**What**: A script that reads LANE_INDEX.md and commitment JSONL files and prints a one-page status report for all 8 lanes. Replaces manual LANE_INDEX updates.
**Lane(s)**: All 8
**Start**: shawn-core/scripts/dashboard.js or dashboard.py
**Why fifth**: Roadmap item v0.2. After 4 days of foundation work, this is the first visible product.
