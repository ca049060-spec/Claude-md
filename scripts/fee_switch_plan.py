#!/usr/bin/env python3
"""
fee_switch_plan.py
==================

A concrete "what if I moved out of high-fee funds" plan — fully offline,
built from the statement data already on hand.

For each mutual fund it maps to a lower-cost equivalent (from the
target_* fields in the portfolio file) and shows:

  - annual fee now vs. at the low-cost equivalent
  - the yearly saving
  - any one-time redemption / DSC penalty to get out
  - payback period (penalty / annual saving)
  - the saving compounded over 10 and 20 years

This is decision-support, NOT financial advice or a tax calculation.
Redemption penalties and MERs are ESTIMATES — confirm each fund's DSC
schedule and Fund Facts, and check whether a switch fits your plan,
before acting.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"

# Assumed annual growth used only to compound the *savings* over time.
GROWTH = 0.06
HORIZONS = (10, 20)


def money(x: float) -> str:
    return f"${x:,.0f}"


def future_value_of_savings(annual_saving: float, years: int, rate: float) -> float:
    """FV of saving `annual_saving` at the start of each year for `years`."""
    fv = 0.0
    for _ in range(years):
        fv = (fv + annual_saving) * (1 + rate)
    return fv


def main() -> None:
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")
    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])
    if not funds:
        sys.exit("No mutual funds found in the portfolio file.")

    print(f"\n{'='*74}\nFee-switch plan — moving to lower-cost equivalents\n{'='*74}")
    print(f"(growth assumption for compounding savings: {GROWTH:.0%}/yr)\n")

    tot_now = tot_target = tot_saving = tot_penalty = 0.0

    for f in funds:
        mv = float(f["market_value"])
        cur_mer = float(f.get("est_mer", 2.0))
        tgt_mer = float(f.get("target_mer", 0.25))
        pen_pct = float(f.get("redemption_pct", 0.0))

        fee_now = mv * cur_mer / 100
        fee_tgt = mv * tgt_mer / 100
        saving = fee_now - fee_tgt
        penalty = mv * pen_pct / 100
        payback = (penalty / saving) if saving > 0 else float("inf")

        tot_now += fee_now
        tot_target += fee_tgt
        tot_saving += saving
        tot_penalty += penalty

        print(f"{f['name']}  ({money(mv)})")
        print(f"    now:    {cur_mer:>5.2f}%  ->  {money(fee_now)}/yr")
        print(f"    target: {tgt_mer:>5.2f}%  ->  {money(fee_tgt)}/yr   "
              f"[{f.get('target_name', 'low-cost ETF')}]")
        print(f"    saving: {money(saving)}/yr", end="")
        if penalty > 0:
            print(f"   |  est. redemption penalty {money(penalty)} "
                  f"({pen_pct:.1f}%)  ->  pays back in "
                  f"{payback:.1f} yr" + (" " if payback >= 1 else ""))
        else:
            print("   |  no redemption penalty (no-load)")
        print()

    print("-" * 74)
    print(f"TOTAL fees now:        {money(tot_now)}/yr")
    print(f"TOTAL fees at target:  {money(tot_target)}/yr")
    print(f"TOTAL annual saving:   {money(tot_saving)}/yr")
    print(f"TOTAL est. penalties:  {money(tot_penalty)} (one-time, if all moved today)")
    if tot_saving > 0:
        print(f"Blended payback:       {tot_penalty / tot_saving:.1f} yr to recoup penalties\n")

    for yrs in HORIZONS:
        fv = future_value_of_savings(tot_saving, yrs, GROWTH)
        print(f"Saving compounded over {yrs} yr (net of one-time penalties): "
              f"{money(fv - tot_penalty)}")

    print("\nLikely sequencing: the no-load Series-A funds (no penalty) are the")
    print("easy wins to move first; the DSC/low-load funds need their redemption")
    print("schedule checked — if you've held them past it, the penalty is $0.")
    print("\nInformational only — not financial advice. Penalties & MERs are")
    print("estimates; confirm each fund's Fund Facts and DSC schedule first.")


if __name__ == "__main__":
    main()
