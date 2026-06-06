#!/usr/bin/env python3
"""
analyst_ratings.py
==================

For each individual stock you hold, show what analysts currently think:

  - Consensus rating (Strong Buy ... Strong Sell), derived from the
    buy / hold / sell counts.
  - Average 12-month price target vs. the current price.
  - Implied upside or downside (%).

HOW DATA IS SOURCED
-------------------
By default this script runs on MOCK data so you can see the output format
without needing an account anywhere. As soon as you set a real API key:

    export FINNHUB_API_KEY=your_key_here

...it fetches live data from Finnhub instead. Nothing else changes.

PRIVACY
-------
This file contains NO holdings of its own. Every symbol and price comes
from data/portfolio.yml, which is gitignored and never leaves your machine.
That keeps your positions private while the code stays shareable.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

import yaml

# --------------------------------------------------------------------------
# 1. Where things live
# --------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"


# --------------------------------------------------------------------------
# 2. Read the holdings (just the individual stocks — funds have no
#    single-name analyst coverage)
# --------------------------------------------------------------------------
def load_stocks() -> list[dict]:
    """Return individual stocks as [{symbol, provider_symbol, price}, ...].

    The CAD sleeve is Toronto-listed, so those symbols get a ".TO" suffix
    for the data provider; the USD sleeve is US-listed and needs no suffix.
    """
    if not PORTFOLIO_FILE.exists():
        sys.exit(
            f"Could not find {PORTFOLIO_FILE}.\n"
            "This file holds your holdings locally (it is gitignored)."
        )

    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    stocks: list[dict] = []
    for sleeve, suffix in (("cad_sleeve", ".TO"), ("usd_sleeve", "")):
        for stock in data.get(sleeve, {}).get("stocks", []):
            stocks.append({
                "symbol": stock["symbol"],
                "provider_symbol": stock["symbol"] + suffix,
                "price": float(stock.get("price", 0.0)),
            })
    return stocks


# --------------------------------------------------------------------------
# 3. The data providers
# --------------------------------------------------------------------------
# Each provider returns the same shape so the rest of the script doesn't
# care where the numbers came from:
#
#   {
#     "strong_buy": int, "buy": int, "hold": int,
#     "sell": int, "strong_sell": int,
#     "current_price": float, "target_mean": float,
#   }

def _finnhub_get(path: str, params: dict, api_key: str) -> dict | list:
    """Tiny helper: GET a Finnhub endpoint and return parsed JSON."""
    params = {**params, "token": api_key}
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"https://finnhub.io/api/v1/{path}?{query}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_live(provider_symbol: str, api_key: str) -> dict:
    """Fetch real analyst data from Finnhub for one symbol.

    Recommendation trends and quote are on the FREE tier. Price target is
    a PREMIUM endpoint, so we try it but fall back to no target (0.0) if
    it's forbidden — that way free-tier users still get the consensus
    rating and the live price.
    """
    # Recommendation trends -> most recent month's buy/hold/sell counts.
    recs = _finnhub_get("stock/recommendation", {"symbol": provider_symbol}, api_key)
    latest = recs[0] if recs else {}

    # Quote -> current price (field "c" = current).
    quote = _finnhub_get("quote", {"symbol": provider_symbol}, api_key)

    # Price target (mean of analyst targets) — premium; degrade gracefully.
    try:
        target = _finnhub_get("stock/price-target", {"symbol": provider_symbol}, api_key)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):       # not available on this plan
            target = {}
        else:
            raise

    return {
        "strong_buy":  latest.get("strongBuy", 0),
        "buy":         latest.get("buy", 0),
        "hold":        latest.get("hold", 0),
        "sell":        latest.get("sell", 0),
        "strong_sell": latest.get("strongSell", 0),
        "current_price": quote.get("c", 0.0),
        "target_mean":   target.get("targetMean", 0.0),
    }


def fetch_mock(symbol: str, price: float) -> dict:
    """Deterministic, illustrative analyst data derived from the ticker.

    We seed a tiny pseudo-random spread off a hash of the symbol so each
    stock looks distinct and the output is stable run-to-run. These are
    NOT real opinions — they exist only to demonstrate the report. The
    current price comes from your local portfolio file.
    """
    seed = int(hashlib.md5(symbol.encode()).hexdigest(), 16)
    strong_buy = seed % 7
    buy = (seed // 7) % 8
    hold = (seed // 56) % 6
    sell = (seed // 336) % 3
    strong_sell = (seed // 1008) % 2
    # Target = price nudged by a deterministic factor in roughly -5%..+22%.
    factor = 1 + (((seed // 2016) % 27) - 5) / 100
    return {
        "strong_buy": strong_buy, "buy": buy, "hold": hold,
        "sell": sell, "strong_sell": strong_sell,
        "current_price": price, "target_mean": round(price * factor, 2),
    }


# --------------------------------------------------------------------------
# 4. Turn raw counts into a human verdict
# --------------------------------------------------------------------------
def consensus_label(d: dict) -> str:
    """Collapse the buy/hold/sell counts into a single weighted verdict.

    We score each analyst: Strong Buy = 5 ... Strong Sell = 1, then
    average. This is the same idea brokers use for a 'consensus rating'.
    """
    weights = {
        "strong_buy": 5, "buy": 4, "hold": 3, "sell": 2, "strong_sell": 1,
    }
    total = sum(d[k] for k in weights)
    if total == 0:
        return "No coverage"
    score = sum(d[k] * w for k, w in weights.items()) / total
    if score >= 4.5:
        return "Strong Buy"
    if score >= 3.5:
        return "Buy"
    if score >= 2.5:
        return "Hold"
    if score >= 1.5:
        return "Sell"
    return "Strong Sell"


def upside_pct(d: dict) -> float | None:
    """Percent the average price target sits above (or below) the price."""
    if not d["current_price"] or not d["target_mean"]:
        return None
    return (d["target_mean"] / d["current_price"] - 1) * 100


# --------------------------------------------------------------------------
# 5. Print the report
# --------------------------------------------------------------------------
def main() -> None:
    api_key = os.environ.get("FINNHUB_API_KEY")
    source = "LIVE (Finnhub)" if api_key else "MOCK (illustrative)"

    print(f"\nAnalyst view of your individual holdings  —  data source: {source}\n")
    header = f"{'Ticker':<7}{'Consensus':<13}{'Price':>10}{'Target':>10}{'Upside':>9}   Analysts (B/H/S)"
    print(header)
    print("-" * len(header))

    for stock in load_stocks():
        if api_key:
            try:
                d = fetch_live(stock["provider_symbol"], api_key)
            except urllib.error.HTTPError as e:
                print(f"{stock['symbol']:<7}error fetching live data ({e.code})")
                continue
        else:
            d = fetch_mock(stock["symbol"], stock["price"])

        verdict = consensus_label(d)
        up = upside_pct(d)
        up_str = f"{up:+.1f}%" if up is not None else "   n/a"
        buys = d["strong_buy"] + d["buy"]
        sells = d["sell"] + d["strong_sell"]

        print(
            f"{stock['symbol']:<7}{verdict:<13}"
            f"{d['current_price']:>10.2f}{d['target_mean']:>10.2f}"
            f"{up_str:>9}   {buys}/{d['hold']}/{sells}"
        )

    print(
        "\nB/H/S = analysts rating Buy / Hold / Sell.  "
        "Upside = avg price target vs current price."
    )
    if not api_key:
        print(
            "\nThis is MOCK data. To see live analyst numbers, get a free key at\n"
            "https://finnhub.io/  then run:  export FINNHUB_API_KEY=your_key\n"
        )


if __name__ == "__main__":
    main()
