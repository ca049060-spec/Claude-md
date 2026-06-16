#!/usr/bin/env python3
"""Review open Resonance prospective signals whose review date has matured.

This script does not judge outcomes automatically. It tells you which frozen
signals are due for human/source-backed review.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datasets" / "prospective_signal_registry.json"


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def main() -> int:
    if not REGISTRY.exists():
        print(f"Registry not found: {REGISTRY}")
        return 1

    signals = json.loads(REGISTRY.read_text(encoding="utf-8"))
    today = date.today()
    matured = []
    open_future = []

    for signal in signals:
        if signal.get("status") != "open":
            continue
        review_date = parse_date(signal["review_date"])
        if review_date <= today:
            matured.append(signal)
        else:
            open_future.append(signal)

    print(f"Registry: {REGISTRY}")
    print(f"Today: {today.isoformat()}")
    print(f"Open signals: {len(matured) + len(open_future)}")
    print(f"Matured signals due for review: {len(matured)}")

    if matured:
        print("\nDue now:")
        for signal in matured:
            print(f"- {signal['id']} | {signal['title']} | review_date={signal['review_date']}")
            print(f"  Review question: {signal.get('expected_review_question', '')}")
    else:
        if open_future:
            next_due = min(parse_date(s["review_date"]) for s in open_future)
            print(f"Next review date: {next_due.isoformat()}")
        print("No matured signals yet. Do not judge accuracy until review date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
