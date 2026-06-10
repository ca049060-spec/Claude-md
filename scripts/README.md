# Portfolio toolkit

A small set of **offline-first** scripts that turn an Edward Jones statement
into a consolidated view, a fee analysis, and printable reports. Everything
runs locally with no dependency beyond `PyYAML`; the analyst layer optionally
calls Finnhub if a key and network are available.

## Privacy model (read this first)

- **Your holdings live in `data/portfolio.yml`, which is gitignored.** None of
  your positions, balances, or personal details are ever committed.
- **All generated outputs are gitignored too** — `report.html`, `report.pdf`,
  `advisor_sheet.html`, `advisor_sheet.pdf`.
- The scripts themselves contain **no financial data** — they only read it from
  the local file at runtime. That's why they're safe to commit.
- Nothing is sent to any external service unless you explicitly run the analyst
  layer with a Finnhub key (`FINNHUB_API_KEY`).

## Setup

```bash
pip install pyyaml          # the only hard dependency
# create data/portfolio.yml  (see the schema below — it is gitignored)
```

## The scripts

| Script | What it does | Output |
|---|---|---|
| `analyst_ratings.py` | Per-stock analyst consensus, price target, upside. Mock by default; live with a Finnhub key. Uses US listings for interlisted TSX names. | console |
| `portfolio_review.py` | Asset mix, position weights, concentration / cash flags, "things to review". | console |
| `fee_and_performance.py` | Estimated annual mutual-fund fees and unrealized gain/loss vs cost base. | console |
| `fee_switch_plan.py` | Maps each fund to a low-cost equivalent; shows yearly saving, exit penalty, payback, and 10/20-yr compounded saving. | console |
| `build_report.py` | Consolidated one-page report. | `report.html` |
| `build_advisor_sheet.py` | Pre-filled fact-finding questions for your advisor. | `advisor_sheet.html` |
| `build_pdf.py` | Same report + advisor sheet, rendered as PDFs with **zero dependencies** (writes PDF directly — works with no browser or pip access). | `report.pdf`, `advisor_sheet.pdf` |

Run any of them with `python3 scripts/<name>.py`.

## Live analyst data (optional)

```bash
export FINNHUB_API_KEY=your_key_here
python3 scripts/portfolio_review.py
```

- Free Finnhub tier covers **US listings**; the script auto-uses the NYSE
  listing for interlisted Canadian names (TD, BNS, ENB, TRP, MFC). TSX-only
  names (e.g. MDA) won't have free coverage.
- The premium `price-target` endpoint is handled gracefully — if it's not on
  your plan, you still get the consensus rating and live price.
- Note: locked-down cloud environments may block `finnhub.io`; run locally or
  use an environment whose network policy allows it.

## `data/portfolio.yml` schema (gitignored)

```yaml
meta:
  as_of: 2026-05-31
  base_currency: CAD
  usd_cad_rate: 1.3795        # used to convert the USD sleeve into CAD
  account_type: LIRA

cad_sleeve:                   # values already in CAD
  cash: 140.46
  money_market:
    - { symbol: EVF, name: ..., units: 8670, price: 10.00, market_value: 86700.00 }
  stocks:
    - { symbol: TD, name: ..., shares: 200, price: 157.75, cost_base: 9838.32, market_value: 31550.00 }
  mutual_funds:
    # est_mer / target_mer / redemption_pct drive the fee + switch analysis
    - { symbol: MFC2946, name: ..., units: 1229.483, price: 49.559,
        cost_base: 25523.45, market_value: 60931.95,
        load: A, est_mer: 2.28, target_name: "Cdn equity index (XIC/VCN)",
        target_mer: 0.06, redemption_pct: 0.00 }

usd_sleeve:                   # values in USD; converted via meta.usd_cad_rate
  cash: 13.47
  stocks:
    - { symbol: NOW, name: ..., shares: 265, price: 124.37, cost_base: 25136.85, market_value: 32958.05 }
```

## Disclaimer

Informational only — **not financial advice**. MERs, target equivalents, and
redemption penalties are estimates to be verified against each fund's Fund
Facts. In a registered account (LIRA/RRSP/TFSA) the adjusted cost base is
informational and gains are not taxed; read the performance figures as a rough
performance indicator, not a tax calculation.
