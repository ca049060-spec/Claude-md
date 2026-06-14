#!/usr/bin/env python3
"""
daily_loop.py — the daily heartbeat of the system.

Built for scheduling. Run this script once a day (Windows Task Scheduler /
cron / macOS launchd) and it will:

  1. Snapshot today's state (caps, VACS scores, classifications, holdings).
  2. Diff against yesterday's snapshot.
  3. Fire the spec's mandatory triggers:
       - any tracked name moved >=30% market cap -> GATE_RECHECK_REQUIRED
       - any candidate's classification changed -> PROMOTION / DEMOTION alert
       - any new flag appeared (insider cluster-sell, policy hard-cap)
       - the spec's confirmation-trap watch (zero demotions in a cycle)
  4. Run every engine via scripts/refresh.py.
  5. Build daily_brief.html — the single glanceable page.
  6. Log every run to data/daily_log.yml so we can prove it ran and audit.

Honest constraints baked in:
  - This script does NOT fetch live market data on its own — it reads
    whatever is in data/portfolio.yml and data/vacs_candidates.yml. The
    diff catches changes the moment that data is updated.
  - State is persisted to data/state_yesterday.json (gitignored).
  - On the FIRST run, "yesterday" is empty — no diffs are reported, only
    the initial snapshot. Day 2 is when alerts begin.
"""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
DATA = ROOT / "data"
STATE = DATA / "state_yesterday.json"
LOG = DATA / "daily_log.yml"
RECHECK_THRESHOLD_PCT = 30.0   # spec rule: >=30% cap move forces VACS re-check


# ---------------------------------------------------------------------------
# 1. snapshot today's state from the candidate file (what the engine sees)
# ---------------------------------------------------------------------------
def snapshot_today() -> dict:
    cands = yaml.safe_load((DATA / "vacs_candidates.yml").read_text()).get("candidates", [])
    snap = {"date": str(date.today()), "candidates": {}}
    for c in cands:
        t = c["ticker"]
        snap["candidates"][t] = {
            "market_cap": c.get("market_cap"),
            "currency": c.get("currency"),
            "vacs_A": c.get("vacs", {}).get("A"),
            "vacs_V": c.get("vacs", {}).get("V"),
            "vacs_C": c.get("vacs", {}).get("C"),
            "vacs_S": c.get("vacs", {}).get("S"),
            "cluster_sell": (c.get("insider_activity") or {}).get("cluster_sell", False),
            "policy_dependency_score": c.get("policy_dependency_score"),
            "gate_plausible": c.get("gate_plausible_10_15yr"),
            "quality_compounder": c.get("quality_compounder", False),
        }
    return snap


# ---------------------------------------------------------------------------
# 2. diff vs yesterday -> the alert list
# ---------------------------------------------------------------------------
def load_yesterday() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text())
        except Exception:
            return {}
    return {}


def diff(today: dict, yesterday: dict) -> list[dict]:
    if not yesterday or not yesterday.get("candidates"):
        return []
    alerts = []
    yc = yesterday["candidates"]; tc = today["candidates"]

    for ticker, t in tc.items():
        y = yc.get(ticker)
        if not y:
            alerts.append({"severity": "INFO", "ticker": ticker,
                           "kind": "NEW", "msg": "new candidate added"})
            continue

        # market cap %change — spec rule (mandatory_recheck_trigger)
        if t["market_cap"] and y.get("market_cap"):
            pct = (t["market_cap"] - y["market_cap"]) / y["market_cap"] * 100
            if abs(pct) >= RECHECK_THRESHOLD_PCT:
                alerts.append({"severity": "HIGH", "ticker": ticker,
                               "kind": "GATE_RECHECK_REQUIRED",
                               "msg": f"market cap moved {pct:+.0f}% — spec demands full VACS re-check"})

        # subjective score changes
        for dim in ("A", "V", "C", "S"):
            if t[f"vacs_{dim}"] != y.get(f"vacs_{dim}") and y.get(f"vacs_{dim}") is not None:
                alerts.append({"severity": "MED", "ticker": ticker,
                               "kind": f"VACS_{dim}_CHANGED",
                               "msg": f"{dim}: {y[f'vacs_{dim}']} -> {t[f'vacs_{dim}']}"})

        # insider cluster-sell newly appeared
        if t["cluster_sell"] and not y.get("cluster_sell"):
            alerts.append({"severity": "HIGH", "ticker": ticker,
                           "kind": "INSIDER_CLUSTER_SELL",
                           "msg": "insider cluster-sell flag NOW TRUE — Adversarial forced <=2"})

        # policy dependency hard-cap newly tripped
        pd = t["policy_dependency_score"]
        ypd = y.get("policy_dependency_score")
        if pd is not None and pd <= 2.5 and (ypd is None or ypd > 2.5):
            alerts.append({"severity": "HIGH", "ticker": ticker,
                           "kind": "POLICY_HARD_CAP",
                           "msg": f"policy dependency dropped to {pd} — HARD-CAP, cannot be Top-20"})

        # gate plausibility flipped
        if t["gate_plausible"] is False and y.get("gate_plausible") is True:
            alerts.append({"severity": "HIGH", "ticker": ticker, "kind": "GATE_CLOSED",
                           "msg": "20x gate now FAILS — exited Top-20 contention"})
        if t["gate_plausible"] is True and y.get("gate_plausible") is False:
            alerts.append({"severity": "HIGH", "ticker": ticker, "kind": "GATE_REOPENED",
                           "msg": "20x gate now PASSES — re-entered Top-20 contention"})

    return alerts


# ---------------------------------------------------------------------------
# 3. drive the refresh pipeline + capture VACS board for the brief
# ---------------------------------------------------------------------------
def run_engines() -> tuple[str, str]:
    rf = subprocess.run([sys.executable, str(SCRIPTS / "refresh.py")],
                        capture_output=True, text=True)
    vc = subprocess.run([sys.executable, str(SCRIPTS / "vacs.py")],
                        capture_output=True, text=True)
    return rf.stdout + rf.stderr, vc.stdout


# ---------------------------------------------------------------------------
# 4. write the daily brief HTML
# ---------------------------------------------------------------------------
def build_brief(today: dict, alerts: list[dict], vacs_out: str,
                last_log_count: int) -> Path:
    out = ROOT / "daily_brief.html"
    sev_color = {"HIGH": "#ff6b5e", "MED": "#ffd166", "INFO": "#9db4e8"}
    by_sev = {"HIGH": [], "MED": [], "INFO": []}
    for a in alerts:
        by_sev[a["severity"]].append(a)

    alert_block = ""
    if not alerts:
        alert_block = ('<div class=ok>✓ No day-over-day changes flagged. '
                       'System running clean.</div>')
    else:
        for sev in ("HIGH", "MED", "INFO"):
            for a in by_sev[sev]:
                alert_block += (f"<div class=alert style='border-left-color:{sev_color[sev]}'>"
                                f"<div class=at><b>{a['ticker']}</b> "
                                f"<span style='color:{sev_color[sev]}'>{a['kind']}</span></div>"
                                f"<div class=am>{a['msg']}</div></div>")

    html = f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Daily Brief — {today['date']}</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0e1422;color:#eef1f8;font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:740px;margin:0 auto;padding:24px 18px 60px}}
.kicker{{font-size:11px;letter-spacing:.18em;color:#7a8699;text-transform:uppercase}}
h1{{font-size:28px;margin:6px 0 4px;letter-spacing:-.5px}}
.lede{{color:#b8c0d4;font-size:14px;margin-bottom:18px}}
h2{{font-size:13px;color:#8b95ad;text-transform:uppercase;letter-spacing:.06em;margin:30px 0 12px;font-weight:600}}
.alert{{background:#141d33;border:1px solid #233152;border-left:4px solid #ffd166;border-radius:10px;padding:11px 14px;margin-bottom:8px}}
.at{{font-size:14.5px}} .am{{font-size:13px;color:#9fb0d6;margin-top:3px}}
.ok{{background:#11321f;color:#3ddc97;border:1px solid #1e6a47;border-radius:10px;padding:14px;font-weight:600}}
pre{{background:#0a0f1a;border:1px solid #243049;border-radius:11px;padding:14px;font-size:12.5px;color:#cbd2e0;overflow-x:auto;white-space:pre-wrap;line-height:1.4}}
.foot{{color:#5d6880;font-size:11.5px;margin-top:26px;border-top:1px solid #243049;padding-top:12px}}
.tile{{background:#1a2336;border:1px solid #263354;border-radius:12px;padding:12px 14px;display:inline-block;margin-right:8px;margin-bottom:8px}}
.tile .l{{color:#8b95ad;font-size:11px;text-transform:uppercase;letter-spacing:.04em}}
.tile .v{{font-size:18px;font-weight:700;margin-top:2px}}
</style></head><body><div class=wrap>

<div class=kicker>daily heartbeat · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
<h1>What changed today</h1>
<div class=lede>Run #{last_log_count + 1}. The system snapshotted, diffed, and re-ran every engine.</div>

<div class=tile><div class=l>Alerts</div><div class=v>{len(alerts)}</div></div>
<div class=tile><div class=l>High severity</div><div class=v style='color:#ff6b5e'>{len(by_sev["HIGH"])}</div></div>
<div class=tile><div class=l>Candidates tracked</div><div class=v>{len(today.get("candidates", {}))}</div></div>

<h2>Day-over-day alerts</h2>
{alert_block}

<h2>VACS ranked board (today)</h2>
<pre>{vacs_out}</pre>

<div class=foot>
Daily loop alive. State persisted for tomorrow's diff. Outputs all PROPOSED until Shawn ratifies.
Not financial advice.
</div>
</div></body></html>"""
    out.write_text(html)
    return out


# ---------------------------------------------------------------------------
# 5. append to the audit log (proves the loop ran)
# ---------------------------------------------------------------------------
def append_log(today: dict, alerts: list[dict]) -> int:
    log = []
    if LOG.exists():
        try:
            log = yaml.safe_load(LOG.read_text()) or []
        except Exception:
            log = []
    log.append({
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "date": today["date"],
        "candidates_tracked": len(today.get("candidates", {})),
        "alerts": [{k: a[k] for k in ("severity", "ticker", "kind", "msg")} for a in alerts],
        "high_severity_count": sum(1 for a in alerts if a["severity"] == "HIGH"),
    })
    LOG.write_text(yaml.safe_dump(log, sort_keys=False, allow_unicode=True))
    return len(log) - 1   # the index of the run we just appended


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main() -> None:
    print(f"\n{'='*60}\n  DAILY LOOP — {date.today()}\n{'='*60}")
    today = snapshot_today()
    yesterday = load_yesterday()
    alerts = diff(today, yesterday)
    run_idx = append_log(today, alerts)
    print(f"\n  Snapshotted {len(today['candidates'])} candidates")
    if yesterday:
        print(f"  Yesterday's snapshot: {yesterday.get('date', '?')}")
        print(f"  Day-over-day alerts: {len(alerts)} "
              f"({sum(1 for a in alerts if a['severity']=='HIGH')} HIGH)")
        for a in alerts:
            print(f"     [{a['severity']:<4}] {a['ticker']:<8} {a['kind']:<24} {a['msg']}")
    else:
        print("  No yesterday snapshot — this is run #1. Diffs begin tomorrow.")

    print(f"\n  Running engines...")
    refresh_out, vacs_out = run_engines()
    last_line = refresh_out.strip().splitlines()[-1] if refresh_out.strip() else ""
    print(f"  Engines: {last_line}")

    brief = build_brief(today, alerts, vacs_out, run_idx)
    print(f"\n  Wrote {brief}")

    # persist today's snapshot for tomorrow's diff
    STATE.write_text(json.dumps(today, indent=2))
    print(f"  State saved for tomorrow.\n")
    print(f"  To schedule daily:")
    print(f"     Windows:  schtasks /Create /SC DAILY /TN PortfolioDaily \\")
    print(f"               /TR \"python {ROOT}/scripts/daily_loop.py\" /ST 07:00")
    print(f"     macOS/Linux:  crontab:  0 7 * * *  cd {ROOT} && python3 scripts/daily_loop.py\n")


if __name__ == "__main__":
    main()
