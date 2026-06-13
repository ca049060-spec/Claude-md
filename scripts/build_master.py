#!/usr/bin/env python3
"""
build_master.py — the whole ~$553K on one page (master.html, gitignored).

Synthesizes: current stocks (portfolio.yml) + the ETF core that the fund
proceeds become (etf_core.yml) + the cash deployment (deployment_plan.yml)
into a single TARGET end-state view, with a move tag on every line.
"""
from __future__ import annotations
from datetime import date
from pathlib import Path
import yaml, sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "master.html"
pf = yaml.safe_load((ROOT / "data" / "portfolio.yml").read_text())
rate = float(pf["meta"].get("usd_cad_rate", 1.0))

def sv(sym):  # statement value of a held stock in CAD
    for sl, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        for s in pf.get(sl, {}).get("stocks", []):
            if s["symbol"] == sym:
                return s["market_value"] * fx
    return 0.0

# TARGET end-state buckets (synthesis — see etf_core.yml / deployment_plan.yml)
# REVISED after live-data pass: cash cut from ~20% to ~9% (locked-till-55 +
# external income = sequence risk is near-zero, so stay invested); freed cash
# goes into the global ETF core. HISA yield fell to ~1.8% so reserve sits in
# CBIL (T-bills). Healthcare ETF dropped — redundant w/ ~11% healthcare already
# inside VFV/XAW. Values are MAY 31 STATEMENT $ (his actual book); see NOW flag.
buckets = [
    ("Conviction / Forever", "#0fa86e", [
        ("MDA",  sv("MDA"),  "HOLD — never trim (live ~C$57, above C$55 rung)"),
        ("NOW",  sv("NOW"),  "HOLD — ⚠ verify statement value vs market"),
        ("BWXT", sv("BWXT"), "HOLD — forever"),
        ("ASML", sv("ASML")+12000, "ADD +$12K (upsize monopoly)"),
        ("TSM",  8000, "NEW — buy now"),
    ]),
    ("Canadian income keepers", "#4a86e8", [
        ("TD",  sv("TD"),  "HOLD — Warsh winner"),
        ("MFC", sv("MFC"), "HOLD — rates tailwind"),
        ("TRP", sv("TRP"), "HOLD"),
        ("ENB", sv("ENB"), "HOLD"),
        ("BNS", sv("BNS"), "TRIM candidate (only Hold)"),
    ]),
    ("Global ETF core (from funds)", "#9b6dff", [
        ("XAW", 105000, "NEW — all-world ex-Canada (0.22%)"),
        ("VFV", 60000,  "NEW — S&P 500 (0.09%); covers healthcare too"),
    ]),
    ("Defensive sleeve (from funds)", "#e0a800", [
        ("XSB", 50000, "NEW — short bonds (0.10%), rate-resilient"),
    ]),
    ("Cash reserve / dip ammo", "#7a8699", [
        ("CBIL", 48000, "T-bill ETF (0.10%) — dip + FOMC ammo, ~9%"),
    ]),
    ("Speculative", "#e0526a", [
        ("BEAM", 3000, "lottery ≤1%"),
    ]),
]

total = sum(v for _, _, items in buckets for _, v, _ in items)
def money(x): return f"${x:,.0f}"

# stacked bar
bar = "".join(
    f"<span style='width:{sum(v for _,v,_ in items)/total*100:.2f}%;background:{c}'></span>"
    for _, c, items in buckets)

legend = " &nbsp; ".join(
    f"<b style='color:{c}'>■</b> {name} {sum(v for _,v,_ in items)/total*100:.0f}%"
    for name, c, items in buckets)

sections = ""
for name, c, items in buckets:
    bt = sum(v for _, v, _ in items)
    rows = "".join(
        f"<tr><td><b>{t}</b></td><td class=r>{money(v)}</td>"
        f"<td class=r>{v/total*100:.1f}%</td><td class=mv>{mv}</td></tr>"
        for t, v, mv in items)
    sections += (f"<h2 style='color:{c}'>{name} — {money(bt)} "
                 f"<span style='color:#69728a;font-weight:400'>"
                 f"({bt/total*100:.0f}%)</span></h2>"
                 f"<table>{rows}</table>")

html = f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Master Allocation</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#0f1522;color:#e8ecf5;
font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:820px;margin:0 auto;padding:22px 16px 60px}}
h1{{font-size:22px;margin:0}}.sub{{color:#8d97b0;font-size:12.5px;margin:3px 0 16px}}
.tot{{font-size:30px;font-weight:700;margin:6px 0}}
.bar{{display:flex;height:30px;border-radius:9px;overflow:hidden;margin:12px 0 6px;border:1px solid #263354}}
.bar span{{display:block;height:100%}}
.legend{{font-size:11.5px;color:#8d97b0;line-height:1.9}}
h2{{font-size:14px;margin:24px 0 6px;text-transform:uppercase;letter-spacing:.04em}}
table{{width:100%;border-collapse:collapse;background:#1a2336;border:1px solid #263354;border-radius:12px;overflow:hidden}}
td{{padding:8px 12px;border-bottom:1px solid #243049;font-size:13.5px}}
tr:last-child td{{border-bottom:none}}.r{{text-align:right;font-variant-numeric:tabular-nums}}
.mv{{color:#9db4e8;font-size:12px;text-align:right}}
.note{{color:#5d6880;font-size:11.5px;margin-top:24px;border-top:1px solid #243049;padding-top:12px}}
</style></head><body><div class=wrap>
<h1>🗺️ Master Allocation — target end-state</h1>
<div class=sub>Everything on one page · generated {date.today()} · current stocks + ETF core (from funds) + cash plan</div>
<div class=tot>{money(total)}</div>
<div class=bar>{bar}</div>
<div class=legend>{legend}</div>
{sections}
<div class=note><b>Revised after live-data check (Jun 13).</b> Cash cut from ~20% to ~9%:
this LIRA is locked till age 55 and you have outside income, so near-term sequence risk is ~0 —
stay invested, don't hoard cash (HISA now yields only ~1.8%). Values are May-31 statement dollars
(your actual book). ⚠ NOW's statement value looks inconsistent with the live market price — verify
the line with EJ. Target end-state, not yet executed: fee switch → ETF core lands → layer conviction
on dips. Decision-support only, not financial advice. You own every decision.</div>
</div></body></html>"""
OUT.write_text(html)
print(f"Wrote {OUT} — total {money(total)}")
