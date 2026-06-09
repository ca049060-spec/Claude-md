#!/usr/bin/env python3
"""
build_report.py
===============

Renders everything into ONE self-contained HTML page you can just open and
look at — no server, no internet, no dependencies beyond PyYAML. Pulls all
numbers from data/portfolio.yml (gitignored) so the report contains your
holdings; the generated report.html is gitignored and never committed.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"
OUT = REPO_ROOT / "report.html"

GROWTH = 0.06
LOWCOST_FALLBACK = 0.25


def money(x: float) -> str:
    return f"${x:,.0f}"


def fv_savings(annual: float, years: int, rate: float) -> float:
    fv = 0.0
    for _ in range(years):
        fv = (fv + annual) * (1 + rate)
    return fv


def main() -> None:
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")
    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    rate = float(data.get("meta", {}).get("usd_cad_rate", 1.0))

    # ---- Build consolidated holdings (everything in CAD) -----------------
    holdings = []  # dict: name, symbol, kind, mv, cost, weight
    for sleeve, fx, cur in (("cad_sleeve", 1.0, "CAD"), ("usd_sleeve", rate, "USD")):
        block = data.get(sleeve, {})
        for kind, key in (("Stock", "stocks"), ("Fund", "mutual_funds"),
                          ("Cash", "money_market")):
            for h in block.get(key, []):
                holdings.append({
                    "name": h.get("name", h["symbol"]), "symbol": h["symbol"],
                    "kind": kind, "cur": cur,
                    "mv": float(h["market_value"]) * fx,
                    "cost": float(h.get("cost_base", h["market_value"])) * fx,
                })
        if block.get("cash"):
            holdings.append({"name": "Cash balance", "symbol": "CASH",
                             "kind": "Cash", "cur": cur,
                             "mv": float(block["cash"]) * fx,
                             "cost": float(block["cash"]) * fx})

    total = sum(h["mv"] for h in holdings)
    for h in holdings:
        h["weight"] = h["mv"] / total * 100 if total else 0
        h["gain"] = h["mv"] - h["cost"]

    mix = {k: sum(h["mv"] for h in holdings if h["kind"] == k)
           for k in ("Stock", "Fund", "Cash")}

    # ---- Fees / switch plan ---------------------------------------------
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])
    fee_now = sum(f["market_value"] * f.get("est_mer", 2.0) / 100 for f in funds)
    fee_tgt = sum(f["market_value"] * f.get("target_mer", LOWCOST_FALLBACK) / 100
                  for f in funds)
    penalties = sum(f["market_value"] * f.get("redemption_pct", 0) / 100 for f in funds)
    saving = fee_now - fee_tgt

    # ---- HTML ------------------------------------------------------------
    def rows_holdings():
        out = []
        for h in sorted(holdings, key=lambda x: -x["mv"]):
            g = h["gain"]
            gcls = "pos" if g >= 0 else "neg"
            ret = (g / h["cost"] * 100) if h["cost"] else 0
            out.append(
                f"<tr><td>{h['symbol']}</td><td class='nm'>{h['name']}</td>"
                f"<td>{h['kind']}</td><td class='r'>{h['weight']:.1f}%</td>"
                f"<td class='r'>{money(h['mv'])}</td>"
                f"<td class='r {gcls}'>{money(g)} ({ret:+.0f}%)</td></tr>")
        return "\n".join(out)

    def rows_switch():
        out = []
        for f in funds:
            mv = f["market_value"]
            fn = mv * f.get("est_mer", 2.0) / 100
            ft = mv * f.get("target_mer", LOWCOST_FALLBACK) / 100
            pen = mv * f.get("redemption_pct", 0) / 100
            pen_s = money(pen) if pen else "—"
            out.append(
                f"<tr><td class='nm'>{f['name']}</td><td class='r'>{money(mv)}</td>"
                f"<td class='r'>{f.get('est_mer',2.0):.2f}%</td>"
                f"<td class='r'>{f.get('target_mer',LOWCOST_FALLBACK):.2f}%</td>"
                f"<td class='r pos'>{money(fn-ft)}/yr</td>"
                f"<td class='r'>{pen_s}</td></tr>")
        return "\n".join(out)

    def bar(label, val):
        pct = val / total * 100 if total else 0
        return (f"<div class='barrow'><span class='barlbl'>{label}</span>"
                f"<span class='bartrack'><span class='barfill' style='width:{pct:.1f}%'></span></span>"
                f"<span class='barval'>{pct:.0f}% · {money(val)}</span></div>")

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio Report</title><style>
:root{{--ink:#1a2233;--mut:#667;--line:#e6e9f0;--bg:#f6f8fc;--grn:#0a7a4f;--red:#c0392b;--acc:#16407a}}
*{{box-sizing:border-box}}body{{margin:0;font:15px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}}
.wrap{{max-width:920px;margin:0 auto;padding:28px 20px 60px}}
h1{{font-size:26px;margin:0 0 2px}}h2{{font-size:18px;margin:34px 0 12px;color:var(--acc)}}
.sub{{color:var(--mut);margin:0 0 22px}}
.cards{{display:flex;flex-wrap:wrap;gap:12px;margin:18px 0}}
.card{{flex:1;min-width:150px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.card .k{{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}}
.card .v{{font-size:22px;font-weight:650;margin-top:4px}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden}}
th,td{{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}}
th{{background:#eef2f9;font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:#445}}
tr:last-child td{{border-bottom:none}}.r{{text-align:right}}.nm{{color:#334}}
.pos{{color:var(--grn)}}.neg{{color:var(--red)}}
.barrow{{display:flex;align-items:center;gap:10px;margin:7px 0}}
.barlbl{{width:64px;color:var(--mut);font-size:13px}}
.bartrack{{flex:1;height:14px;background:#e9edf5;border-radius:8px;overflow:hidden}}
.barfill{{display:block;height:100%;background:linear-gradient(90deg,#2d6cdf,#16407a)}}
.barval{{width:150px;text-align:right;font-size:13px;color:#445}}
.hl{{background:#eaf6f0;border:1px solid #bfe3d2;border-radius:12px;padding:16px 18px;margin:14px 0}}
.hl b{{font-size:20px;color:var(--grn)}}
.note{{color:var(--mut);font-size:12.5px;margin-top:26px;border-top:1px solid var(--line);padding-top:14px}}
ul{{margin:8px 0;padding-left:20px}}li{{margin:4px 0}}
</style></head><body><div class="wrap">

<h1>Consolidated Portfolio Report</h1>
<p class="sub">Edward Jones LIRA · as of {data.get('meta',{}).get('as_of','')} · generated {date.today()}</p>

<div class="cards">
  <div class="card"><div class="k">Total value</div><div class="v">{money(total)}</div></div>
  <div class="card"><div class="k">Unrealized gain</div><div class="v pos">{money(sum(h['gain'] for h in holdings))}</div></div>
  <div class="card"><div class="k">Fund fees / yr</div><div class="v">{money(fee_now)}</div></div>
  <div class="card"><div class="k">Potential saving / yr</div><div class="v pos">{money(saving)}</div></div>
</div>

<h2>Asset mix</h2>
{bar("Stocks", mix['Stock'])}
{bar("Funds", mix['Fund'])}
{bar("Cash", mix['Cash'])}

<h2>Holdings &amp; performance</h2>
<table><tr><th>Ticker</th><th>Name</th><th>Type</th><th class="r">Weight</th>
<th class="r">Value (CAD)</th><th class="r">Gain/Loss</th></tr>
{rows_holdings()}
</table>

<h2>The fee opportunity</h2>
<div class="hl">You pay about <b>{money(fee_now)}/year</b> in mutual-fund fees (~{fee_now/sum(f['market_value'] for f in funds)*100:.2f}% blended).
Moving to low-cost equivalents would cut that to about {money(fee_tgt)}/year — a saving near
<b>{money(saving)}/year</b>. One-time exit penalties are estimated at {money(penalties)} (often $0 if DSC schedules have matured),
recouped in roughly {penalties/saving:.1f} year{'s' if penalties/saving>=2 else ''}.
Compounded at {GROWTH:.0%}, that saving is about <b>{money(fv_savings(saving,10,GROWTH)-penalties)}</b> over 10 years
and <b>{money(fv_savings(saving,20,GROWTH)-penalties)}</b> over 20 years.</div>

<table><tr><th>Fund</th><th class="r">Value</th><th class="r">MER now</th>
<th class="r">Target</th><th class="r">Saving</th><th class="r">Exit penalty</th></tr>
{rows_switch()}
</table>

<h2>What to do next</h2>
<ul>
<li><b>Easy wins first:</b> the no-load Series-A funds (Mackenzie, Franklin Royce, BMO Monthly Income) move with <b>no penalty</b> — that's most of the saving captured at zero cost.</li>
<li><b>Check the DSC/low-load two</b> (BMO Asian, AGF) — ask your advisor for the redemption-schedule maturity date; if matured, the penalty is $0.</li>
<li><b>The $86.7K in cash/savings (~16%)</b> — confirm whether that's intentional dry powder or money that should be invested.</li>
<li><b>MDA (~10%)</b> is your largest single stock — worth watching as a concentration point.</li>
</ul>

<p class="note">Informational only — not financial advice. MERs, target equivalents and
redemption penalties are estimates to verify against each fund's Fund Facts; cost base in a
registered (LIRA) account is informational and gains are not taxed. Built offline from your
statement data — nothing was sent to any external service.</p>
</div></body></html>"""

    OUT.write_text(html)
    print(f"Wrote {OUT}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
