#!/usr/bin/env python3
"""
weighted_consensus.py  (v2 of the analyst engine)
=================================================

The upgrade over a raw consensus: every analyst's vote is weighted by their
measured track record. A Strong Buy from a #50-ranked analyst with a 74% win
rate moves the needle far more than the same call from someone who's wrong
half the time.

Pipeline:
  data/research_calls.yml   per-stock named-analyst calls + track records
                            (gathered by research agents from public sources)
  analyst_scoring.py        turns each track record into a 0-100 score
  THIS SCRIPT               -> quality-weighted consensus per ticker
                            -> data/weighted_consensus.yml (consumed by the
                               PDF report builder)

Honesty rules baked in:
  - Analysts with no findable track record get a neutral 50 score (half
    weight), clearly marked — we never invent a record.
  - Weighted targets only average calls quoted in the same currency.
  - Output marks how many of the calls carried a real track record, so you
    can see how solid each weighted consensus is.

Decision-support only — NOT financial advice. Past performance does not
guarantee future results.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyst_scoring import track_record_score  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
CALLS_FILE = REPO_ROOT / "data" / "research_calls.yml"
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"
OUT_FILE = REPO_ROOT / "data" / "weighted_consensus.yml"

# Rating <-> numeric scale.
RATING_VALUE = {"Strong Buy": 2.0, "Buy": 1.0, "Hold": 0.0,
                "Sell": -1.0, "Strong Sell": -2.0}
NEUTRAL_SCORE = 50.0   # weight for analysts with no findable track record


def value_to_label(v: float) -> str:
    if v >= 1.5:
        return "Strong Buy"
    if v >= 0.5:
        return "Buy"
    if v > -0.5:
        return "Hold"
    if v > -1.5:
        return "Sell"
    return "Strong Sell"


def holdings_set() -> set[str]:
    """Tickers actually owned (to split holdings vs watchlist)."""
    if not PORTFOLIO_FILE.exists():
        return set()
    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    held = set()
    for sleeve in ("cad_sleeve", "usd_sleeve"):
        for s in data.get(sleeve, {}).get("stocks", []):
            held.add(s["symbol"])
    return held


def weigh_ticker(calls: list[dict]) -> dict:
    """Compute the quality-weighted consensus for one ticker."""
    num = den = 0.0
    tracked = 0
    best = None           # highest-scored analyst on the name
    tgt_by_ccy: dict[str, list[tuple[float, float]]] = {}

    for c in calls:
        track = c.get("track")
        if track:
            score = track_record_score(track)
            tracked += 1
        else:
            score = NEUTRAL_SCORE
        w = score / 100.0
        v = RATING_VALUE.get(c.get("rating", "Hold"), 0.0)
        num += w * v
        den += w

        if c.get("target") is not None:
            tgt_by_ccy.setdefault(c.get("ccy", "USD"), []).append(
                (w, float(c["target"])))

        if best is None or score > best["score"]:
            best = {"analyst": c.get("analyst", "?"), "firm": c.get("firm", "?"),
                    "rating": c.get("rating", "?"), "target": c.get("target"),
                    "ccy": c.get("ccy", "USD"), "score": round(score, 1),
                    "tracked": bool(track)}

    wavg = num / den if den else 0.0
    # Weighted target in the most-quoted currency.
    w_target = ccy = None
    if tgt_by_ccy:
        ccy, pairs = max(tgt_by_ccy.items(), key=lambda kv: len(kv[1]))
        wsum = sum(w for w, _ in pairs)
        if wsum:
            w_target = round(sum(w * t for w, t in pairs) / wsum, 2)

    return {
        "weighted_value": round(wavg, 2),
        "weighted_label": value_to_label(wavg),
        "weighted_target": w_target,
        "target_ccy": ccy,
        "num_calls": len(calls),
        "num_tracked": tracked,
        "top_analyst": best,
    }


def main() -> None:
    if not CALLS_FILE.exists():
        sys.exit(f"Missing {CALLS_FILE} — run the research agents first.")
    raw = yaml.safe_load(CALLS_FILE.read_text())
    stocks = raw.get("stocks", raw)   # tolerate either nesting
    held = holdings_set()

    results: dict[str, dict] = {}
    for ticker, blob in stocks.items():
        if not isinstance(blob, dict) or not blob.get("calls"):
            continue
        r = weigh_ticker(blob["calls"])
        r["held"] = ticker in held
        r["price"] = blob.get("price")
        if r["price"] and r["weighted_target"]:
            r["upside_pct"] = round(
                (r["weighted_target"] / r["price"] - 1) * 100, 1)
        results[ticker] = r

    OUT_FILE.write_text(yaml.safe_dump(
        {"as_of": raw.get("as_of", ""), "results": results},
        sort_keys=False, allow_unicode=True))

    # Console report, holdings first then watchlist, best-weighted first.
    def section(title: str, items: list[tuple[str, dict]]) -> None:
        if not items:
            return
        print(f"\n{title}")
        head = (f"{'TICKER':<8}{'W-CONSENSUS':<13}{'W-TGT':>9}{'CALLS':>6}"
                f"{'TRACKED':>8}   TOP ANALYST (score)")
        print(head)
        print("-" * len(head))
        for t, r in items:
            ta = r["top_analyst"] or {}
            tgt = (f"{r['target_ccy']} {r['weighted_target']:,.0f}"
                   if r["weighted_target"] else "-")
            mark = "" if ta.get("tracked") else " *"
            print(f"{t:<8}{r['weighted_label']:<13}{tgt:>9}{r['num_calls']:>6}"
                  f"{r['num_tracked']:>8}   {ta.get('analyst','?')} "
                  f"({ta.get('firm','?')}) {ta.get('score','?')}{mark}")

    pick = lambda held_flag: sorted(
        ((t, r) for t, r in results.items() if r["held"] == held_flag),
        key=lambda kv: -kv[1]["weighted_value"])
    print("\nQUALITY-WEIGHTED ANALYST CONSENSUS"
          "\n(votes weighted by each analyst's measured track record)")
    section("YOUR HOLDINGS", pick(True))
    section("WATCHLIST CANDIDATES", pick(False))
    print("\n*  top analyst had no findable track record (neutral weight)."
          "\nDecision-support only — not financial advice.")


if __name__ == "__main__":
    main()
