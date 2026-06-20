#!/usr/bin/env python3
"""Append a hand-scored Resonance prospective signal to the registry.

This is intentionally simple: it creates a conservative template you can edit.
It does not browse, score, or invent sources for you.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets" / "prospective_signal_registry.json"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60] or "signal"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--primary-domain", default="unknown")
    parser.add_argument("--review-days", type=int, default=60)
    args = parser.parse_args()

    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    if REGISTRY.exists():
        signals = json.loads(REGISTRY.read_text(encoding="utf-8"))
    else:
        signals = []

    today = date.today()
    signal_id = f"psig-{today.isoformat().replace('-', '')}-{slugify(args.title)}"
    if any(s.get("id") == signal_id for s in signals):
        print(f"Signal already exists: {signal_id}")
        return 1

    signal = {
        "id": signal_id,
        "title": args.title,
        "registration_date": today.isoformat(),
        "review_date": (today + timedelta(days=args.review_days)).isoformat(),
        "status": "open",
        "information_cutoff": today.isoformat(),
        "primary_domain": args.primary_domain,
        "secondary_domains": [],
        "first_visible_signal": "TODO: describe first visible signal without outcome knowledge",
        "public_sources_available_at_cutoff": [],
        "feature_scores": {},
        "unknown_features": [
            "cross_domain_reach",
            "second_order_potential",
            "institutional_response_lag",
            "policy_sensitivity",
            "cascade_potential"
        ],
        "prediction_label": "investigate",
        "confidence": 0.0,
        "bounded_action": "TODO: one reversible action",
        "one_thing_not_to_do": "TODO: one harmful overreaction to avoid",
        "what_would_change_label": {},
        "expected_review_question": "TODO: what will be checked at review date?",
        "later_outcome": None,
        "review_notes": "Template registered. Must be filled with dated sources before treated as a frozen prediction.",
        "accuracy_result": "pending"
    }

    signals.append(signal)
    REGISTRY.write_text(json.dumps(signals, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Registered template signal: {signal_id}")
    print(f"Registry: {REGISTRY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
