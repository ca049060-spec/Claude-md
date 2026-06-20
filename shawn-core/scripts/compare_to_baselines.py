#!/usr/bin/env python3
"""Baseline comparison placeholder for matured prospective Resonance signals.

Only reviewed signals can be scored. Open/pending signals are intentionally not
used for accuracy claims.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets" / "prospective_signal_registry.json"


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}")
        return 1
    signals = json.loads(REGISTRY.read_text(encoding="utf-8"))
    reviewed = [s for s in signals if s.get("accuracy_result") in {"useful", "wrong", "mixed", "untestable"}]
    pending = [s for s in signals if s.get("accuracy_result") == "pending"]

    print(f"Reviewed signals: {len(reviewed)}")
    print(f"Pending signals: {len(pending)}")

    if not reviewed:
        print("No reviewed signals yet. Baseline comparison is not valid until at least one signal matures and is reviewed.")
        print("Majority-class baseline: unavailable")
        print("Always-watch baseline: unavailable")
        print("Source-quality-only baseline: unavailable")
        print("Resonance adds value: untested")
        return 0

    counts = Counter(s.get("prediction_label", "unknown") for s in reviewed)
    print("Reviewed prediction labels:")
    for label, count in counts.most_common():
        print(f"- {label}: {count}")
    print("Manual source-backed evaluation still required for baseline scoring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
