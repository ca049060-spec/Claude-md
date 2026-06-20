#!/usr/bin/env python3
"""Conservative audit for hindsight leakage in prospective signals."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets" / "prospective_signal_registry.json"
HIGH_RISK_UNKNOWNS = {
    "cross_domain_reach",
    "second_order_potential",
    "institutional_response_lag",
    "policy_sensitivity",
    "cascade_potential",
}


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}")
        return 1
    signals = json.loads(REGISTRY.read_text(encoding="utf-8"))
    problems = []
    for signal in signals:
        unknown = set(signal.get("unknown_features", []))
        scores = set(signal.get("feature_scores", {}).keys())
        scored_high_risk = sorted(HIGH_RISK_UNKNOWNS & scores)
        missing_unknowns = sorted(HIGH_RISK_UNKNOWNS - unknown - scores)
        if scored_high_risk:
            problems.append((signal["id"], "high-risk future-dependent fields were scored", scored_high_risk))
        if missing_unknowns:
            problems.append((signal["id"], "high-risk fields neither scored nor marked unknown", missing_unknowns))

    print(f"Audited signals: {len(signals)}")
    if not problems:
        print("No obvious hindsight leakage detected by conservative field audit.")
        return 0

    print("Potential hindsight leakage issues:")
    for signal_id, issue, fields in problems:
        print(f"- {signal_id}: {issue}: {', '.join(fields)}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
