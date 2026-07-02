#!/usr/bin/env python3
"""
fund_alpha.py — does each mutual fund EARN its fee, or just charge it?

The honest test that settles "keep vs switch": did the fund beat its
benchmark index, net of fees? A big cumulative gain means nothing if the
ANNUAL return lagged a cheap index — that's the illusion long holds create.

For each fund it computes:
  - annual lag vs benchmark (benchmark_return - fund_return)
  - the dollar drag per year on the current position
  - what the SAME money would be worth today if it had tracked the index
  - a keep/switch verdict

Reads data/fund_alpha.yml. Fill the null benchmark numbers from each fund's
MRFP (ask the advisor) to convert LIKELY_LAG / PENDING into hard verdicts.
Decision-support, not advice.
"""
from __future__ import annotations
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "data" / "fund_alpha.yml"


def money(x): return f"${x:,.0f}"


def main() -> None:
    funds = yaml.safe_load(F.read_text())["funds"]
    print(f"\n{'='*64}\n  FUND ALPHA — does the fee buy performance?\n{'='*64}\n")

    total_value = total_drag = 0.0
    switch_value = 0.0
    for f in funds:
        v = f["value"]; total_value += v
        print(f"{f['name']}  ({money(v)})  [{f['ticker']}]")
        fr, br = f.get("fund_10yr"), f.get("bench_10yr")
        if fr is not None and br is not None:
            lag = br - fr
            drag = v * lag / 100
            total_drag += drag
            # what $value would be in 10yr indexed vs fund (forward illustration)
            idx10 = (1 + br/100)**10
            fnd10 = (1 + fr/100)**10
            gap_pct = (idx10/fnd10 - 1) * 100
            verdict = "SWITCH" if lag > 0.3 else "KEEP"
            if verdict == "SWITCH":
                switch_value += v
            print(f"   10yr: fund {fr:.2f}%/yr  vs  benchmark {br:.2f}%/yr  "
                  f"=  {lag:+.2f}%/yr {'LAG' if lag>0 else 'BEAT'}")
            print(f"   Annual drag on this position: ~{money(drag)}/yr")
            print(f"   Over 10yr, indexing would leave you ~{gap_pct:.0f}% richer on this money")
            print(f"   >>> VERDICT: {verdict}\n")
        elif fr is not None:
            print(f"   10yr: fund {fr:.2f}%/yr  vs  benchmark <needs MRFP figure>")
            print(f"   Absolute {fr:.1f}%/yr is weak for this category — "
                  f"{f.get('verdict','?')}")
            print(f"   >>> VERDICT: GET BENCHMARK # AT WES (leaning switch)\n")
            switch_value += v   # provisional
        else:
            print(f"   No data ({f.get('source','')}).")
            print(f"   >>> VERDICT: PENDING — ask Wes for 10yr fund-vs-benchmark\n")

    print("-" * 64)
    print(f"  Confirmed/likely SWITCH bucket: ~{money(switch_value)} of {money(total_value)}")
    print(f"  Measured annual drag (where data exists): ~{money(total_drag)}/yr")
    print(f"  Rule: anything that LAGGED its benchmark net of fees -> switch.")
    print(f"        anything that genuinely BEAT it -> keep.")
    print(f"  Still need from Wes: 10yr fund-vs-benchmark for Mackenzie + AGF,")
    print(f"  and the exact benchmark figure for BMO Asian + Franklin Royce.\n")


if __name__ == "__main__":
    main()
