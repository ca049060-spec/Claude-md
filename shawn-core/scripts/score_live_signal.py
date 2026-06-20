#!/usr/bin/env python3
"""Print the frozen score for a registered Resonance prospective signal."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets" / "prospective_signal_registry.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("signal_id", nargs="?", help="Signal id. If omitted, prints all open signals.")
    args = parser.parse_args()

    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}")
        return 1

    signals = json.loads(REGISTRY.read_text(encoding="utf-8"))
    selected = signals
    if args.signal_id:
        selected = [s for s in signals if s.get("id") == args.signal_id]
        if not selected:
            print(f"No signal found with id: {args.signal_id}")
            return 1

    for signal in selected:
        print("=" * 80)
        print(signal["id"])
        print(signal["title"])
        print(f"status: {signal.get('status')} | review_date: {signal.get('review_date')} | result: {signal.get('accuracy_result')}")
        print(f"prediction_label: {signal.get('prediction_label')} | confidence: {signal.get('confidence')}")
        print("\nfeature_scores:")
        for key, value in signal.get("feature_scores", {}).items():
            print(f"  {key}: {value}")
        print("\nunknown_features:")
        for key in signal.get("unknown_features", []):
            print(f"  - {key}")
        print("\nbounded_action:")
        print(signal.get("bounded_action", ""))
        print("\none_thing_not_to_do:")
        print(signal.get("one_thing_not_to_do", ""))
        print("\nwhat_would_change_label:")
        print(json.dumps(signal.get("what_would_change_label", {}), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
