#!/usr/bin/env python3
"""
build_advisor_sheet.py
======================

Generates a one-page "take this to your advisor" sheet (advisor_sheet.html,
gitignored) — the exact questions whose answers confirm or correct every
estimate behind the fee-switch plan. Each question is pre-filled with the
specific fund and the number we assumed, with a blank to write the real one.

The point: one short conversation (or secure message) gets you from
"Claude's estimates" to verified facts you can act on.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"
OUT = REPO_ROOT / "advisor_sheet.html"


def money(x: float) -> str:
    return f"${x:,.0f}"


def main() -> None:
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")
    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])

    fee_now = sum(f["market_value"] * f.get("est_mer", 2.0) / 100 for f in funds)

    q_rows = []
    n = 0

    # Q1..n: MER confirmation per fund.
    for f in funds:
        n += 1
        q_rows.append(f"""
<div class="q"><span class="qn">{n}</span>
<div><b>{f['name']}</b> ({f['symbol']}, {f.get('load','?')} series) —
what is the exact MER I'm paying on this fund?
<div class="assume">I'm assuming ~{f.get('est_mer',2.0):.2f}% &nbsp;→&nbsp; about {money(f['market_value']*f.get('est_mer',2.0)/100)}/yr on my {money(f['market_value'])}.</div>
<div class="blank">Actual MER: ____________ %</div></div></div>""")

    # DSC / low-load schedule questions.
    for f in funds:
        if f.get("redemption_pct", 0) > 0:
            n += 1
            q_rows.append(f"""
<div class="q"><span class="qn">{n}</span>
<div><b>{f['name']}</b> is {f.get('load','?')} — when does its redemption
schedule mature, and what penalty (if any) applies if I sell <i>today</i>?
<div class="assume">I'm assuming a worst case of {f.get('redemption_pct',0):.1f}% (~{money(f['market_value']*f.get('redemption_pct',0)/100)}). If the schedule has matured, it should be $0.</div>
<div class="blank">Maturity date: ____________ &nbsp;&nbsp; Penalty today: ____________</div></div></div>""")

    # Structural questions.
    extra = [
        ("Can each of these funds be switched to its <b>Series F</b> (or a "
         "low-cost ETF) <b>inside this LIRA without leaving Edward Jones</b>? "
         "What would my all-in cost (MER + any advisory fee) be after the switch?",
         "Blank to fill: all-in cost after switch: ____________ %"),
        ("Are there <b>any account-level or trading fees</b> I'd trigger by "
         "selling these funds and buying ETFs — commissions, switch fees, "
         "early-redemption (short-term trading) fees?",
         "List: ______________________________________________"),
        ("The ~$86,700 in the high-interest savings position — what rate is it "
         "earning right now, and are there better cash-equivalent options "
         "inside the LIRA?",
         "Rate: ____________ %"),
        ("Since my accounts were consolidated, can you confirm the <b>total "
         "annual cost of the relationship</b> — all embedded fund fees plus any "
         "account fees — as one dollar figure?",
         "Total $/yr: ____________"),
    ]
    for q, blank in extra:
        n += 1
        q_rows.append(f"""
<div class="q"><span class="qn">{n}</span><div>{q}
<div class="blank">{blank}</div></div></div>""")

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Advisor conversation sheet</title><style>
body{{font:14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#1a2233;margin:0;background:#fff}}
.wrap{{max-width:820px;margin:0 auto;padding:30px 26px}}
h1{{font-size:22px;margin:0 0 4px}}
.sub{{color:#667;margin:0 0 18px}}
.why{{background:#eaf6f0;border:1px solid #bfe3d2;border-radius:10px;padding:12px 16px;margin-bottom:20px}}
.q{{display:flex;gap:12px;padding:11px 4px;border-bottom:1px solid #e6e9f0}}
.qn{{flex:0 0 26px;height:26px;border-radius:50%;background:#16407a;color:#fff;text-align:center;line-height:26px;font-weight:600;font-size:13px}}
.assume{{color:#667;font-size:12.5px;margin-top:3px}}
.blank{{color:#16407a;font-size:13px;margin-top:5px}}
.note{{color:#667;font-size:12px;margin-top:18px}}
</style></head><body><div class="wrap">
<h1>Questions for my Edward Jones advisor</h1>
<p class="sub">Re: LIRA — fund costs &amp; lower-cost options · prepared {date.today()}</p>
<div class="why">Why I'm asking: my five mutual funds appear to cost roughly
<b>{money(fee_now)}/year</b> in embedded fees (~2.25% blended). I'd like to verify
the exact numbers and understand my lower-cost options. Nothing here is a
decision yet — it's fact-finding.</div>
{''.join(q_rows)}
<p class="note">Tip: this can be sent as a secure message instead of a call —
written answers are easier to compare against the estimates. Once filled in,
update the portfolio file and re-run the fee-switch plan with real numbers.</p>
</div></body></html>"""

    OUT.write_text(html)
    print(f"Wrote {OUT}  ({n} questions)")


if __name__ == "__main__":
    main()
