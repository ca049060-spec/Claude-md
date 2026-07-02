#!/usr/bin/env python3
"""
test_engine.py — sanity tests for the analyst-weighting model.

Run: python3 scripts/test_engine.py
Exits non-zero on any failure. These tests check the model BEHAVES the way
it claims to, with synthetic cases where the right answer is known:

  1. A proven analyst outscores an unproven one.
  2. More history -> more score, all else equal.
  3. A star analyst's dissent moves the weighted consensus more than a
     weak analyst's dissent (the entire point of the model).
  4. Unknown/partial track records degrade gracefully (no crash, neutral).
  5. Weighted targets ignore mixed-currency contamination.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyst_scoring import track_record_score  # noqa: E402
from weighted_consensus import weigh_ticker, value_to_label  # noqa: E402

FAILURES = []


def check(name: str, cond: bool, detail: str = "") -> None:
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f"  ({detail})" if detail else ""))
    if not cond:
        FAILURES.append(name)


# 1. Proven beats unproven.
good = track_record_score({"success_rate": 0.74, "avg_return": 40.0, "num_calls": 200})
weak = track_record_score({"success_rate": 0.45, "avg_return": 3.0, "num_calls": 200})
check("proven analyst outscores weak one", good > weak + 20, f"{good} vs {weak}")

# 2. History matters.
thin = track_record_score({"success_rate": 0.74, "avg_return": 40.0, "num_calls": 3})
check("thin history dampens score", thin < good, f"{thin} < {good}")

# 3. Star dissent moves consensus more than weak dissent.
star_sell = weigh_ticker([
    {"rating": "Buy", "track": {"success_rate": 0.50, "avg_return": 5, "num_calls": 50}},
    {"rating": "Buy", "track": {"success_rate": 0.50, "avg_return": 5, "num_calls": 50}},
    {"rating": "Sell", "track": {"success_rate": 0.80, "avg_return": 45, "num_calls": 300}},
])
weak_sell = weigh_ticker([
    {"rating": "Buy", "track": {"success_rate": 0.50, "avg_return": 5, "num_calls": 50}},
    {"rating": "Buy", "track": {"success_rate": 0.50, "avg_return": 5, "num_calls": 50}},
    {"rating": "Sell", "track": {"success_rate": 0.35, "avg_return": -5, "num_calls": 10}},
])
check("star dissent drags consensus harder than weak dissent",
      star_sell["weighted_value"] < weak_sell["weighted_value"],
      f"{star_sell['weighted_value']} < {weak_sell['weighted_value']}")

# 4. Partial/null tracks degrade gracefully.
r = weigh_ticker([
    {"rating": "Buy", "track": None},
    {"rating": "Buy", "track": {"success_rate": None, "avg_return": None}},
    {"rating": "Buy", "track": {"success_rate": 0.70, "avg_return": 20.0, "num_calls": None}},
])
check("null/partial tracks don't crash and count as untracked",
      r["num_tracked"] == 1 and r["weighted_label"] in ("Buy", "Strong Buy"),
      f"tracked={r['num_tracked']}, label={r['weighted_label']}")

# 5. Mixed currencies: target averaged only in the modal currency.
r = weigh_ticker([
    {"rating": "Buy", "target": 100, "ccy": "USD", "track": None},
    {"rating": "Buy", "target": 105, "ccy": "USD", "track": None},
    {"rating": "Buy", "target": 1900, "ccy": "EUR", "track": None},
])
check("mixed-currency targets don't contaminate the average",
      r["target_ccy"] == "USD" and 100 <= r["weighted_target"] <= 105,
      f"{r['target_ccy']} {r['weighted_target']}")

# 6. Label mapping is sane at boundaries.
check("label boundaries", value_to_label(1.6) == "Strong Buy"
      and value_to_label(0.7) == "Buy" and value_to_label(0.0) == "Hold"
      and value_to_label(-0.8) == "Sell")

print()
if FAILURES:
    print(f"{len(FAILURES)} test(s) FAILED: {FAILURES}")
    sys.exit(1)
print("All model sanity tests passed.")
