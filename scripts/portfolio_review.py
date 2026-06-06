#!/usr/bin/env python3
"""
portfolio_review.py
===================

Goes a step beyond a flat list of analyst ratings: it weights everything
by how much money you actually have in each position, then surfaces
"things to review."

It answers questions a plain ratings table can't:
  - How is my money split across stocks / funds / cash?
  - Which of my BIG positions do analysts feel lukewarm about?
  - Am I over-concentrated in any single name?
  - Where do analysts see the most upside, weighted by what I own?

Like analyst_ratings.py, this contains NO holdings itself — it reads
data/portfolio.yml (gitignored) and reuses the analyst-data functions.

NOTE: This is informational tooling, not financial advice. It flags
things worth a closer look; it does not tell you to buy or sell.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Reuse the analyst-data + scoring helpers we already built.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyst_ratings as ar  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"

# Tunable thresholds for the review flags (kept here so they're easy to see).
CONCENTRATION_PCT = 10.0     # single position above this % = concentrated
LARGE_POSITION_PCT = 5.0     # "big" position for the weak-rating check
CASH_DRAG_PCT = 15.0         # combined cash/money-market above this = flag


# --------------------------------------------------------------------------
# 1. Load everything into one currency (CAD) so weights are comparable
# --------------------------------------------------------------------------
def load_positions() -> tuple[list[dict], float]:
    """Return (positions, total_cad).

    Each position: {name, symbol, kind, value_cad, sleeve}.
    'kind' is one of: stock, fund, cash. USD values are converted to CAD
    using the rate stored in the portfolio's meta block.
    """
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")

    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    rate = float(data.get("meta", {}).get("usd_cad_rate", 1.0))

    positions: list[dict] = []
    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        block = data.get(sleeve, {})

        for s in block.get("stocks", []):
            positions.append({
                "name": s.get("name", s["symbol"]),
                "symbol": s["symbol"],
                "kind": "stock",
                "sleeve": sleeve,
                "price": float(s.get("price", 0.0)),
                "value_cad": float(s["market_value"]) * fx,
            })
        for f in block.get("mutual_funds", []):
            positions.append({
                "name": f.get("name", f["symbol"]),
                "symbol": f["symbol"], "kind": "fund", "sleeve": sleeve,
                "price": 0.0, "value_cad": float(f["market_value"]) * fx,
            })
        for m in block.get("money_market", []):
            positions.append({
                "name": m.get("name", m["symbol"]),
                "symbol": m["symbol"], "kind": "cash", "sleeve": sleeve,
                "price": 0.0, "value_cad": float(m["market_value"]) * fx,
            })
        if block.get("cash"):
            positions.append({
                "name": "Cash balance", "symbol": "CASH",
                "kind": "cash", "sleeve": sleeve, "price": 0.0,
                "value_cad": float(block["cash"]) * fx,
            })

    total = sum(p["value_cad"] for p in positions)
    for p in positions:
        p["weight"] = (p["value_cad"] / total * 100) if total else 0.0
    return positions, total


# --------------------------------------------------------------------------
# 2. Attach analyst data to each stock (mock or live, same as before)
# --------------------------------------------------------------------------
def attach_analyst_view(positions: list[dict], api_key: str | None) -> None:
    """Add consensus / upside fields to each stock position in place."""
    for p in positions:
        if p["kind"] != "stock":
            continue
        if api_key:
            try:
                d = ar.fetch_live(ar.analyst_symbol(p["symbol"], p["sleeve"]), api_key)
            except Exception:
                d = ar.fetch_mock(p["symbol"], p["price"])
        else:
            d = ar.fetch_mock(p["symbol"], p["price"])
        p["consensus"] = ar.consensus_label(d)
        p["upside"] = ar.upside_pct(d)


# --------------------------------------------------------------------------
# 3. Generate review flags (transparent, rule-based)
# --------------------------------------------------------------------------
def build_recommendations(positions: list[dict], total: float) -> list[str]:
    """Return a list of plain-English 'things to review' notes."""
    notes: list[str] = []

    # a) Single-name concentration.
    for p in sorted(positions, key=lambda x: -x["weight"]):
        if p["kind"] == "stock" and p["weight"] >= CONCENTRATION_PCT:
            notes.append(
                f"Concentration: {p['symbol']} is {p['weight']:.1f}% of the "
                f"whole portfolio (${p['value_cad']:,.0f}). A single stock "
                f"that large drives a lot of your risk — worth a look."
            )

    # b) Big positions analysts are lukewarm/negative on.
    for p in positions:
        if p["kind"] != "stock" or p["weight"] < LARGE_POSITION_PCT:
            continue
        if p.get("consensus") in ("Hold", "Sell", "Strong Sell"):
            notes.append(
                f"Review: {p['symbol']} is a sizable position "
                f"({p['weight']:.1f}%) but analyst consensus is "
                f"'{p['consensus']}'. Worth understanding why."
            )
        elif p.get("upside") is not None and p["upside"] < 0:
            notes.append(
                f"Review: {p['symbol']} ({p['weight']:.1f}%) trades ABOVE "
                f"the average analyst target ({p['upside']:+.1f}%). Analysts "
                f"see limited room — consider whether to trim."
            )

    # c) Cash drag.
    cash = sum(p["value_cad"] for p in positions if p["kind"] == "cash")
    cash_pct = (cash / total * 100) if total else 0.0
    if cash_pct >= CASH_DRAG_PCT:
        notes.append(
            f"Cash: {cash_pct:.1f}% (${cash:,.0f}) sits in cash / savings. "
            f"That's a meaningful drag if it's not intentional — consider "
            f"whether some should be deployed."
        )

    # d) Where analysts are most positive (constructive, not just warnings).
    best = [p for p in positions if p["kind"] == "stock"
            and p.get("consensus") in ("Buy", "Strong Buy")
            and (p.get("upside") or 0) > 0]
    best.sort(key=lambda x: -(x["upside"] or 0))
    if best:
        top = best[0]
        notes.append(
            f"Most upside: analysts are most constructive on {top['symbol']} "
            f"({top['consensus']}, {top['upside']:+.1f}% to target)."
        )

    return notes


# --------------------------------------------------------------------------
# 4. Print the report
# --------------------------------------------------------------------------
def main() -> None:
    api_key = ar.os.environ.get("FINNHUB_API_KEY")
    source = "LIVE (Finnhub)" if api_key else "MOCK (illustrative)"

    positions, total = load_positions()
    attach_analyst_view(positions, api_key)

    print(f"\nPortfolio Review  —  analyst data: {source}")
    print(f"Total value: CAD ${total:,.0f}\n")

    # Allocation by kind.
    print("Asset mix")
    print("-" * 32)
    for kind, label in (("stock", "Individual stocks"),
                        ("fund", "Mutual funds"),
                        ("cash", "Cash / savings")):
        val = sum(p["value_cad"] for p in positions if p["kind"] == kind)
        pct = (val / total * 100) if total else 0
        print(f"{label:<20}{pct:>5.1f}%  ${val:,.0f}")

    # Stock holdings, largest first, with the analyst view.
    print("\nStock holdings (by size)")
    head = f"{'Ticker':<7}{'Weight':>7}  {'Value(CAD)':>12}  {'Consensus':<12}{'Upside':>8}"
    print(head)
    print("-" * len(head))
    stocks = sorted((p for p in positions if p["kind"] == "stock"),
                    key=lambda x: -x["weight"])
    for p in stocks:
        up = p.get("upside")
        up_str = f"{up:+.1f}%" if up is not None else "  n/a"
        print(
            f"{p['symbol']:<7}{p['weight']:>6.1f}%  ${p['value_cad']:>10,.0f}  "
            f"{p.get('consensus', 'n/a'):<12}{up_str:>8}"
        )

    # Recommendations.
    print("\nThings to review")
    print("-" * 32)
    for i, note in enumerate(build_recommendations(positions, total), 1):
        print(f"{i}. {note}\n")

    print("Informational only — not financial advice.")
    if not api_key:
        print("(Analyst figures are MOCK. Set FINNHUB_API_KEY for live data.)")


if __name__ == "__main__":
    main()
