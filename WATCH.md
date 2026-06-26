# VACS Evergreen Watch

A continuously-refreshable database + dashboard for the hit list. Built to
answer one question on demand: **what changed, and does it move any name's
score?**

## The honest cadence story

You asked for a refresh "every minute, constantly looking for new data." Here
is why that's the wrong tool, and what we built instead.

- **Nothing but price moves by the minute.** Filings, M&A, insider Form 4s,
  permits, EIA approvals — the things that actually move a VACS score — change
  on an hours-to-days cadence. A per-minute *research* crawl re-reads the same
  news thousands of times for ~zero new signal.
- **No process lives forever here.** The Claude container sleeps when you're
  away, so anything "always-on" must run on outside infrastructure (a cron),
  not inside a session.
- **Cost.** A per-minute LLM deep-crawl of ~16 names is tens of millions of
  tokens/day for no incremental edge.

### Two tiers instead

| Tier | What it does | Cost | Cadence |
|------|--------------|------|---------|
| 🟢 **Fast** (`watch.py`) | Mechanical: re-score, fetch cheap price, diff vs last snapshot, log what moved | ~free, no LLM | Tight loop / cron OK |
| 🔵 **Deep** (research agents) | LLM + web: refresh narrative, catalysts, news, insider context; re-propose V/A/C/S | Real tokens | A few times/day, or **event-driven** when the fast tier flags a change |

The fast tier is the heartbeat. When it detects a material change (score move,
cap move ≥5%, a new flag), that's the trigger to fire the deep tier on just
that one name — "always fresh" without watching paint dry.

## Files

- `scripts/watch.py` — fast tier. Builds/updates `data/watch_state.json`
  (the database: per-ticker record + 60-snapshot history + rolling changelog).
  Run `--prices` to attempt cheap quotes (best-effort; needs network).
- `scripts/build_watch_dashboard.py` — renders `watch.html`, the single
  always-current master dashboard (replaces the old scattered one-off files).
- `data/watch_state.json` — the database. **Gitignored** (personal data).
- `watch.html` — the dashboard. **Gitignored** (personal data).

## Scope (your choice: survivors + holdings + redemption watch)

- `survivor` — cleared the gate + VACS-scored → deep-crawl
- `holding` — on a brokerage statement → deep-crawl, always
- `redemption_watch` — gate-failed / rejected → LIGHT watch, only to catch a
  left-for-dead name turning a corner (e.g. a sudden acquisition)
- `quality_compounder` — too big to 20x, kept via the escape hatch

## Running it

```bash
# one mechanical refresh (heartbeat)
python3 scripts/watch.py            # add --prices to try live quotes
python3 scripts/build_watch_dashboard.py

# or roll it into the whole-system rebuild
python3 scripts/refresh.py
```

## Making it truly "evergreen"

Three ways to run it on a schedule, cheapest → most autonomous:

1. **In-session loop** — `/loop 30m python3 scripts/watch.py`. Runs only while
   a Claude session is open. Good for an active research session.
2. **Local cron** — a `cron`/launchd entry on a machine you control runs the
   fast tier on a timer and keeps the data on that machine.
3. **Scheduled GitHub Action** (`.github/workflows/vacs-watch.yml`) — runs in
   the cloud on a cron, even while you're away. **Precondition:** this requires
   committing the candidate/data files to the repo, which your `.gitignore`
   currently forbids ("never commit until repo is confirmed private"). Enable
   ONLY after you confirm the repo is private and add an `ANTHROPIC_API_KEY`
   secret. Until then it stays `workflow_dispatch`-only (manual) and never
   auto-runs.

> Personal financial data never leaves the machine until you confirm the repo
> is private. That's why the database and dashboard are gitignored.
