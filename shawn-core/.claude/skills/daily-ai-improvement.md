# Skill: daily-ai-improvement

**Trigger**: Shawn says "daily AI" or "what are we improving today" or "AI improvement cycle" — or as the first thing after `North, where are we?` on any day Shawn has 45 minutes.

**Purpose**: Run the daily cycle that finds one AI improvement, builds it, tests it, and commits it to the repo. One improvement per day. Done means committed.

---

## The Sequence

### Step 1 — SCOUT (5 min)
Invoke Scout: "Scout, what's new?"
Scout returns 3-5 candidates ranked by actionability.
If Scout returns zero actionable items, stop for today and log why.

### Step 2 — RESONATE (5 min)
Run `resonance-web-map` on the top 2 candidates.
Each candidate gets one of: ACT / WATCH / IGNORE.
If both are WATCH or IGNORE, pick the next candidate down.
If all 5 are WATCH or IGNORE, stop for today — no improvement today.

### Step 3 — PICK (2 min)
North picks one ACT candidate.
State it in one sentence: "Today we are building [name] because [specific reason for Shawn]."
Get a yes or a redirect from Shawn before proceeding.

### Step 4 — FORGE (20-30 min)
Invoke Forge: "Forge, build [chosen thing]."
Forge returns file path, complete content, commit message, and lanes served.
Do not modify Forge's output. Pass it directly to Calibrate.

### Step 5 — CALIBRATE (10 min)
Invoke Calibrate: "Calibrate, test [new file]."
Calibrate runs three tests and returns KEEP / REVISE / DISCARD.
- KEEP: proceed to Step 6.
- REVISE: send the one-change instruction back to Forge. One loop only.
- DISCARD: log the lesson using skill-harvester. Stop for today.

### Step 6 — COMMIT (5 min)
Write the file to disk.
Run: git add [file path]
Run: git commit -m "[Forge's commit message]"
Run: git push -u origin [current branch]

Done when: the commit appears in the remote repo. Not before.

---

## Log entry (after every cycle, pass or stop)

Append to shawn-core/docs/AI_IMPROVEMENT_LOG.md:

```
Date: [date]
Candidate chosen: [name]
Outcome: KEEP / DISCARD / STOPPED
File committed: [path or none]
Lesson: [one sentence]
```

---

## Hard rules

- One improvement per day maximum. Do not chain two builds.
- If Shawn is in doom mode or cognitive load is high, skip to joy-queue instead.
- Never commit without Calibrate's KEEP verdict.
- If the total time exceeds 60 minutes, stop and log where it stalled.
