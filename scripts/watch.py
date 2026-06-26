#!/usr/bin/env python3
"""
watch.py — the evergreen VACS watch engine (the "database" layer).

This is the FAST/CHEAP tier of the continuous-crawl system. It is purely
mechanical (no LLM, no opinions): it re-runs the VACS engine over the
candidate set, classifies each name into a watch SCOPE, fetches an optional
cheap price quote, then DIFFS the new snapshot against the last one and
writes a changelog of what actually moved. It maintains a persistent
database (data/watch_state.json) with per-ticker history.

Two-tier design (see WATCH.md):
  - FAST tier  = this script. Mechanical re-score + price + diff. Cheap
                 enough to run on a tight loop / cron.
  - DEEP tier  = LLM research agents (run separately) that refresh the
                 narrative/catalyst/news fields. Triggered a few times a
                 day, or EVENT-DRIVEN when this fast tier flags a change.

SCOPE (per Shawn's choice: "survivors + holdings + redemption watch"):
  - survivor          : cleared the gate + got VACS-scored (deep-crawl)
  - holding           : on a brokerage statement (deep-crawl, always)
  - redemption_watch  : gate-failed / rejected (LIGHT watch — we only want
                        to catch a left-for-dead name turning a corner)

Database + dashboard hold personal financial context, so both are GITIGNORED.
NOT financial advice. All scores PROPOSED until Shawn ratifies.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from vacs import evaluate, HOLDINGS, CAND  # reuse the one true engine

STATE = ROOT / "data" / "watch_state.json"
CAP_MOVE_PCT = 5.0  # market-cap move that earns a changelog line


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_price(ticker: str, ccy: str, timeout: float = 6.0):
    """Best-effort cheap quote from stooq (no API key). Returns dict or None.
    Network may be blocked by sandbox policy — fails silently and the
    dashboard simply shows '—'. Honest by design: we never fake a price."""
    suffix = {"USD": ".us", "CAD": ".ca", "AUD": ".au"}.get(ccy, ".us")
    sym = ticker.lower().replace(".", "-") + suffix
    url = f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlcv&h&e=csv"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            rows = resp.read().decode().strip().splitlines()
        if len(rows) < 2:
            return None
        cols = rows[1].split(",")
        close = cols[6]
        if close in ("N/D", "", None):
            return None
        return {"last": float(close), "asof": cols[1], "source": "stooq"}
    except Exception:
        return None


def scope_of(res: dict, ticker: str) -> str:
    if ticker in HOLDINGS:
        return "holding"
    if res["status"] == "SCORED":
        return "survivor"
    if res.get("escape_hatch_used"):
        return "quality_compounder"
    return "redemption_watch"


# Per Shawn's narrowed choice: the EXPENSIVE deep (LLM) crawl runs only on
# holdings + top contenders. Everything else is tracked by the cheap fast
# tier but does NOT trigger a deep research refresh.
TOP_TIERS = {"Top 20 Confirmed (Tier 1)", "Conditional Top 20", "Tier 2 — Watchlist"}


def is_deep_crawl(res: dict, ticker: str) -> bool:
    return ticker in HOLDINGS or res.get("classification") in TOP_TIERS


def snapshot(c: dict, res: dict, with_price: bool) -> dict:
    """Build the current per-ticker record from a candidate + engine result."""
    v = c.get("vacs", {}) or {}
    rec = {
        "ticker": c["ticker"],
        "company_name": c.get("company_name"),
        "pillar": (c.get("thesis_pillars_touched") or ["?"])[0],
        "market_cap": c.get("market_cap"),
        "currency": c.get("currency"),
        "as_of_date": c.get("as_of_date"),
        "held": c["ticker"] in HOLDINGS,
        "scope": scope_of(res, c["ticker"]),
        "deep_crawl": is_deep_crawl(res, c["ticker"]),
        "status": res["status"],
        "gate_math": res.get("gate_math"),
        "composite": res.get("composite"),
        "classification": res.get("classification") or res.get("status"),
        "vacs": res.get("scores"),
        "flags": res.get("flags", []),
        # narrative fields — seeded from the candidate file, refreshed by the
        # DEEP (LLM) tier over time:
        "thesis": c.get("gate_evidence"),
        "catalyst": v.get("C_evidence"),
        "risk": v.get("A_evidence"),
        "price": fetch_price(c["ticker"], c.get("currency", "USD")) if with_price else None,
        "last_refresh": now_iso(),
    }
    return rec


def diff(old: dict, new: dict) -> list[str]:
    """What materially changed for one ticker since last run."""
    out = []
    if old is None:
        out.append(f"ADDED to watch ({new['scope']}, {new['classification']})")
        return out
    if (old.get("composite") or 0) != (new.get("composite") or 0):
        out.append(f"VACS {old.get('composite')} -> {new.get('composite')} "
                   f"({old.get('classification')} -> {new.get('classification')})")
    oc, nc = old.get("market_cap"), new.get("market_cap")
    if oc and nc and oc != 0:
        pct = (nc - oc) / oc * 100
        if abs(pct) >= CAP_MOVE_PCT:
            out.append(f"Market cap {pct:+.0f}% ({oc:,.0f} -> {nc:,.0f})")
    of, nf = set(old.get("flags", [])), set(new.get("flags", []))
    for f in nf - of:
        out.append(f"NEW FLAG: {f}")
    for f in of - nf:
        out.append(f"FLAG CLEARED: {f}")
    if old.get("scope") != new.get("scope"):
        out.append(f"Scope {old.get('scope')} -> {new.get('scope')}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", action="store_true",
                    help="fetch cheap quotes (best-effort; off by default)")
    args = ap.parse_args()

    if not CAND.exists():
        sys.exit(f"Missing {CAND}")
    cands = yaml.safe_load(CAND.read_text()).get("candidates", [])

    prev = {}
    if STATE.exists():
        prev = json.loads(STATE.read_text()).get("tickers", {})

    tickers, changelog = {}, []
    for c in cands:
        if not c.get("ticker"):
            continue
        res = evaluate(c)
        rec = snapshot(c, res, args.prices)
        # carry history forward
        hist = (prev.get(c["ticker"], {}) or {}).get("history", [])
        hist = hist + [{"date": str(date.today()), "composite": rec["composite"],
                        "market_cap": rec["market_cap"],
                        "price": (rec["price"] or {}).get("last") if rec["price"] else None}]
        rec["history"] = hist[-60:]  # keep last 60 snapshots
        changes = diff(prev.get(c["ticker"]), rec)
        if changes:
            for ch in changes:
                changelog.append({"date": str(date.today()), "ticker": c["ticker"], "change": ch})
        tickers[c["ticker"]] = rec

    # names that dropped off entirely
    for t in prev:
        if t not in tickers:
            changelog.append({"date": str(date.today()), "ticker": t, "change": "REMOVED from candidate set"})

    db = {
        "generated": now_iso(),
        "scope_rule": "survivors + holdings + redemption_watch",
        "counts": {
            "survivor": sum(1 for r in tickers.values() if r["scope"] == "survivor"),
            "holding": sum(1 for r in tickers.values() if r["scope"] == "holding"),
            "quality_compounder": sum(1 for r in tickers.values() if r["scope"] == "quality_compounder"),
            "redemption_watch": sum(1 for r in tickers.values() if r["scope"] == "redemption_watch"),
            "total": len(tickers),
        },
        "tickers": tickers,
        # keep a rolling changelog across runs
        "changelog": (json.loads(STATE.read_text()).get("changelog", []) if STATE.exists() else [])
                     + changelog,
    }
    db["changelog"] = db["changelog"][-200:]
    STATE.write_text(json.dumps(db, indent=2))

    print(f"watch.py — {db['counts']['total']} names tracked "
          f"({db['counts']['survivor']} survivor / {db['counts']['holding']} held / "
          f"{db['counts']['redemption_watch']} redemption-watch / "
          f"{db['counts']['quality_compounder']} quality)")
    if changelog:
        print(f"  {len(changelog)} change(s) this run:")
        for ch in changelog[-12:]:
            print(f"    • {ch['ticker']}: {ch['change']}")
    else:
        print("  no material changes since last refresh.")
    print(f"  database -> {STATE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
