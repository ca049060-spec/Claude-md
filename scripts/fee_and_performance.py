#!/usr/bin/env python3
"""
fee_and_performance.py
======================

Analysis that needs NO internet — it works entirely from the statements
you already have, so it runs anywhere (including locked-down environments).

It tells you two money things that matter most right now:

  1. FEES: roughly how much you pay every year for the mutual funds you
     hold (Series-A / DSC / low-load funds embed ~2%/yr), and what a
     lower-cost alternative might save.
  2. PERFORMANCE: unrealized gain/loss per holding (market value minus the
     adjusted cost base on the statement).

Like the other scripts, it holds no data itself — everything comes from
data/portfolio.yml (gitignored). Fee figures use the est_mer values in
that file, which are ESTIMATES to be verified against each Fund Facts.

NOTE: Informational only, not financial advice. In a registered account
(LIRA/RRSP/TFSA) the adjusted cost base is shown for information only and
gains are not taxed — so treat the performance section as a rough
performance read, not a tax figure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"

# If a fund has no est_mer in the file, assume this (typical Series A).
DEFAULT_MER = 2.00
# A realistic low-cost alternative (broad ETF / Series F) for comparison.
LOWCOST_MER = 0.25


def load() -> dict:
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")
    return yaml.safe_load(PORTFOLIO_FILE.read_text())


def money(x: float) -> str:
    return f"${x:,.0f}"


# --------------------------------------------------------------------------
# Fees
# --------------------------------------------------------------------------
def fee_analysis(data: dict) -> None:
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])
    if not funds:
        return

    print("MUTUAL FUND FEES (estimated)")
    head = f"{'Fund':<34}{'Load':<10}{'Value':>11}{'MER':>7}{'Annual cost':>13}"
    print(head)
    print("-" * len(head))

    total_value = 0.0
    total_cost = 0.0
    for f in funds:
        mv = float(f["market_value"])
        mer = float(f.get("est_mer", DEFAULT_MER))
        annual = mv * mer / 100
        total_value += mv
        total_cost += annual
        print(f"{f['name'][:33]:<34}{str(f.get('load', '?')):<10}"
              f"{money(mv):>11}{mer:>6.2f}%{money(annual):>13}")

    blended = (total_cost / total_value * 100) if total_value else 0
    print("-" * len(head))
    print(f"{'TOTAL':<34}{'':<10}{money(total_value):>11}{blended:>6.2f}%{money(total_cost):>13}")

    lowcost = total_value * LOWCOST_MER / 100
    print(
        f"\nYou pay roughly {money(total_cost)} per year in fund fees "
        f"(~{blended:.2f}% blended).\n"
        f"At a low-cost alternative (~{LOWCOST_MER:.2f}%, e.g. broad ETFs or "
        f"Series F) that would be about {money(lowcost)} —\n"
        f"a potential saving near {money(total_cost - lowcost)} per year, "
        f"which compounds significantly over time.\n"
        f"DSC/low-load funds may also charge a redemption fee if sold early "
        f"— check before switching."
    )


# --------------------------------------------------------------------------
# Performance (unrealized gain/loss vs adjusted cost base)
# --------------------------------------------------------------------------
def performance_analysis(data: dict) -> None:
    rate = float(data.get("meta", {}).get("usd_cad_rate", 1.0))
    rows: list[tuple[str, float, float]] = []   # (label, cost_cad, mv_cad)

    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        block = data.get(sleeve, {})
        for kind in ("stocks", "mutual_funds"):
            for h in block.get(kind, []):
                if "cost_base" in h:
                    rows.append((h["symbol"],
                                 float(h["cost_base"]) * fx,
                                 float(h["market_value"]) * fx))

    print("\nPERFORMANCE  (market value vs adjusted cost base, CAD)")
    head = f"{'Holding':<10}{'Cost base':>13}{'Market':>13}{'Gain/Loss':>13}{'Return':>9}"
    print(head)
    print("-" * len(head))

    tc = tm = 0.0
    for label, cost, mv in sorted(rows, key=lambda r: -(r[2] - r[1])):
        gl = mv - cost
        ret = (gl / cost * 100) if cost else 0
        tc += cost
        tm += mv
        print(f"{label:<10}{money(cost):>13}{money(mv):>13}{money(gl):>13}{ret:>8.1f}%")

    tgl = tm - tc
    tret = (tgl / tc * 100) if tc else 0
    print("-" * len(head))
    print(f"{'TOTAL':<10}{money(tc):>13}{money(tm):>13}{money(tgl):>13}{tret:>8.1f}%")
    print(
        "\nNote: this is a LIRA (registered), so the cost base is informational "
        "and these gains are not taxed. Read it as rough performance only."
    )


def main() -> None:
    data = load()
    print(f"\n{'='*72}\nPortfolio fee & performance analysis  (no internet needed)\n{'='*72}\n")
    fee_analysis(data)
    performance_analysis(data)
    print("\nInformational only — not financial advice. Fee figures are estimates;")
    print("verify each fund's MER and any redemption charges in its Fund Facts.")


if __name__ == "__main__":
    main()
