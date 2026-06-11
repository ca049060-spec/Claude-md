#!/usr/bin/env python3
"""
analyst_scoring.py
==================

Measures analysts by their *track record* instead of taking every opinion at
face value — modelled on the public TipRanks methodology:

  1. Success rate  — how OFTEN the analyst's calls make money.
  2. Average return — how MUCH their calls make (the primary factor).
  3. Significance  — enough calls that it isn't luck.

Those combine into a transparent 0-100 "track-record score". The point: when
two analysts disagree about a stock you own, you can weight the one who's
actually been right more heavily than the one who hasn't.

This is decision-support, NOT financial advice. Scores reflect past
performance, which does not guarantee future results.

Data lives in data/analyst_calls.yml (public analyst-performance data, no PII).
Start small and broaden over time — that's the design.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CALLS_FILE = REPO_ROOT / "data" / "analyst_calls.yml"

# How the three factors combine. Return is primary (like TipRanks), success
# rate secondary, significance a confidence dampener. Tweak openly here.
RETURN_FULL_MARKS = 50.0   # avg_return (%) that earns full points on that axis
SIGNIF_FULL_MARKS = 50     # num_calls that counts as "statistically solid"
W_RETURN, W_SUCCESS = 0.55, 0.45
ASSUMED_CALLS = 25         # when the call count isn't published, assume a
                           # moderate history rather than zero (sell-side
                           # analysts on TipRanks typically have 100+ ratings)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def track_record_score(a: dict) -> float:
    """0-100 score from success rate, average return, and call count.

    Tolerates partial records: a missing call count falls back to
    ASSUMED_CALLS; missing rate/return are treated as 0 (callers should
    treat fully-null tracks as 'no record' before getting here).
    """
    ret_comp = clamp((a.get("avg_return") or 0.0) / RETURN_FULL_MARKS)
    suc_comp = clamp(a.get("success_rate") or 0.0)
    # Significance: few calls -> pull the score toward neutral.
    signif = clamp((a.get("num_calls") or ASSUMED_CALLS) / SIGNIF_FULL_MARKS)
    confidence = 0.6 + 0.4 * signif          # 0.6 (thin) .. 1.0 (solid)
    base = W_RETURN * ret_comp + W_SUCCESS * suc_comp
    return round(100 * base * confidence, 1)


def main() -> None:
    if not CALLS_FILE.exists():
        sys.exit(f"Could not find {CALLS_FILE}.")
    data = yaml.safe_load(CALLS_FILE.read_text())
    analysts = data.get("analysts", [])
    for a in analysts:
        a["score"] = track_record_score(a)
    analysts.sort(key=lambda x: -x["score"])

    print(f"\nAnalyst track-record scores  (source: {data.get('source','')})")
    print(f"Formula: return {W_RETURN:.0%} + success {W_SUCCESS:.0%}, "
          f"dampened by call count.\n")
    head = f"{'Analyst':<22}{'Firm':<10}{'Win%':>6}{'AvgRet':>8}{'Calls':>7}{'SCORE':>7}"
    print(head)
    print("-" * len(head))
    for a in analysts:
        print(f"{a['name'][:21]:<22}{str(a.get('firm','-'))[:9]:<10}"
              f"{a.get('success_rate',0)*100:>5.0f}%{a.get('avg_return',0):>7.1f}%"
              f"{a.get('num_calls',0):>7}{a['score']:>7.1f}")

    # Show which of YOUR holdings these top analysts cover.
    covered: dict[str, list] = {}
    for a in analysts:
        for t in a.get("covers", []) or []:
            covered.setdefault(t, []).append(a)
    if covered:
        print("\nYour holdings covered by a tracked analyst:")
        for t, who in covered.items():
            top = max(who, key=lambda x: x["score"])
            print(f"  {t}: {top['name']} ({top['firm']}) — score {top['score']:.0f} "
                  f"({top.get('success_rate',0)*100:.0f}% win, "
                  f"{top.get('avg_return',0):.0f}% avg return)")

    print("\nNext: broaden the dataset — add the analysts who cover MDA, NOW, TD,")
    print("etc., so the consensus on each of your stocks can be re-weighted by")
    print("who has the best record. This v1 proves the method on a seed sample.")
    print("\nDecision-support only — not financial advice. Past performance does")
    print("not guarantee future results.")


if __name__ == "__main__":
    main()
