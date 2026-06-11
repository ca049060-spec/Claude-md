#!/usr/bin/env python3
"""
build_dashboard.py — the evergreen dashboard.

One self-contained HTML page (dashboard.html, gitignored) designed for
GLANCING, not reading: big tiles, the Forever-20 board, color-coded
holdings, the MDA dip-ladder, and a short action queue.

Regenerate any time with:  python3 scripts/build_dashboard.py
It reads whatever is currently in data/, so it's always current.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
OUT = ROOT / "dashboard.html"


def load(name):
    p = D / name
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def money(x):
    return f"${x:,.0f}"


def main() -> None:
    pf = load("portfolio.yml")
    wc = load("weighted_consensus.yml").get("results", {})
    f20 = load("forever20.yml")
    if not pf:
        sys.exit("missing data/portfolio.yml")

    rate = float(pf["meta"].get("usd_cad_rate", 1.0))

    # Totals
    total = gain = cash = 0.0
    rows = []
    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        b = pf.get(sleeve, {})
        for s in b.get("stocks", []):
            mv = s["market_value"] * fx
            total += mv
            gain += mv - s.get("cost_base", s["market_value"]) * fx
            rows.append((s["symbol"], mv, s.get("price")))
        for f in b.get("mutual_funds", []):
            mv = f["market_value"] * fx
            total += mv
            gain += mv - f.get("cost_base", f["market_value"]) * fx
        for m in b.get("money_market", []):
            total += m["market_value"] * fx
            cash += m["market_value"] * fx
        c = b.get("cash", 0) * fx
        total += c
        cash += c

    funds = pf.get("cad_sleeve", {}).get("mutual_funds", [])
    fee_now = sum(f["market_value"] * f.get("est_mer", 2.0) / 100 for f in funds)
    fee_tgt = sum(f["market_value"] * f.get("target_mer", 0.25) / 100 for f in funds)

    members = f20.get("members", [])
    tier1 = f20.get("tier1", [])
    tier3 = f20.get("tier3", [])
    themes = f20.get("watch_themes", [])
    member_syms = [m["ticker"] for m in members]

    # Forever-20 board: filled + empty slots
    slots = "".join(
        f"<div class='slot filled'>{m['ticker']}</div>" for m in members
    ) + "".join("<div class='slot'></div>" for _ in range(20 - len(members)))

    cand_chips = "".join(
        f"<span class='chip t1'>{c['ticker']}</span>" for c in tier1
    ) + "".join(f"<span class='chip t3'>{c['ticker']}</span>" for c in tier3)

    # Holdings rows with weighted view
    def pill(lbl):
        cls = "buy" if "Buy" in (lbl or "") else ("sell" if "Sell" in (lbl or "") else "hold")
        return f"<span class='pill {cls}'>{lbl or 'n/a'}</span>"

    hold_rows = ""
    for sym, mv, _ in sorted(rows, key=lambda r: -r[1]):
        r = wc.get(sym, {})
        up = r.get("upside_pct")
        upbar = ""
        if up is not None:
            w = min(abs(up), 40) * 2.2
            color = "#0a7a4f" if up >= 0 else "#c0392b"
            upbar = (f"<span class='bar'><span style='width:{w}px;background:{color}'></span></span>"
                     f"<b style='color:{color}'>{up:+.0f}%</b>")
        star = " ⭐" if sym in member_syms else ""
        hold_rows += (f"<tr><td><b>{sym}</b>{star}</td><td>{money(mv)}</td>"
                      f"<td>{pill(r.get('weighted_label'))}</td><td>{upbar}</td></tr>")

    # MDA dip ladder
    mda_price = next((p for s, _, p in rows if s == "MDA" and p), None)
    ladder = ""
    if mda_price:
        for lvl, amt in ((55, "$5K"), (49, "$5K"), (43, "$7K")):
            hit = mda_price <= lvl
            ladder += (f"<div class='rung {'hit' if hit else ''}'>"
                       f"<span>C${lvl}</span><span>buy {amt}</span>"
                       f"<span>{'TRIGGERED' if hit else f'{(mda_price-lvl)/mda_price*100:.0f}% away'}</span></div>")

    theme_chips = "".join(f"<span class='chip th'>{t['theme']}</span>" for t in themes)

    html = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shawn's Money Dashboard</title><style>
:root{{--ink:#172033;--mut:#69728a;--line:#e3e8f2;--grn:#0a7a4f;--red:#c0392b;--blu:#16407a;--gold:#b8860b}}
*{{box-sizing:border-box}}body{{margin:0;background:#0f1522;color:#e8ecf5;font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:22px 16px 50px}}
h1{{font-size:21px;margin:0}}/* dark theme, glanceable */
.sub{{color:#8d97b0;font-size:12.5px;margin:2px 0 18px}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}
.tile{{background:#1a2336;border:1px solid #263354;border-radius:14px;padding:14px}}
.tile .k{{font-size:11px;color:#8d97b0;text-transform:uppercase;letter-spacing:.05em}}
.tile .v{{font-size:24px;font-weight:700;margin-top:4px}}
.g{{color:#3ddc97}}.r{{color:#ff6b5e}}.y{{color:#ffd166}}
h2{{font-size:15px;color:#9db4e8;margin:26px 0 10px;text-transform:uppercase;letter-spacing:.06em}}
.board{{display:grid;grid-template-columns:repeat(10,1fr);gap:6px}}
.slot{{aspect-ratio:1.6;border:1.5px dashed #2c3a5e;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;color:#3e4f78}}
.slot.filled{{border:none;background:linear-gradient(135deg,#0a7a4f,#0fa86e);color:#fff}}
.chips{{margin-top:10px}}.chip{{display:inline-block;margin:3px 4px 0 0;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600}}
.chip.t1{{background:#2a3a22;color:#a4e786;border:1px solid #41602f}}
.chip.t3{{background:#33243d;color:#d0a4f5;border:1px solid #543a66}}
.chip.th{{background:#1f2c45;color:#9db4e8;border:1px solid #2f4470}}
table{{width:100%;border-collapse:collapse;background:#1a2336;border-radius:14px;overflow:hidden}}
td{{padding:9px 12px;border-bottom:1px solid #243049;font-size:13.5px}}
tr:last-child td{{border-bottom:none}}
.pill{{padding:2px 10px;border-radius:12px;font-size:11.5px;font-weight:700}}
.pill.buy{{background:#11321f;color:#3ddc97}}.pill.hold{{background:#33301a;color:#ffd166}}.pill.sell{{background:#3a1d1a;color:#ff6b5e}}
.bar{{display:inline-block;width:90px;height:8px;background:#243049;border-radius:5px;margin-right:8px;vertical-align:middle;overflow:hidden}}
.bar span{{display:block;height:100%}}
.rung{{display:flex;justify-content:space-between;background:#1a2336;border:1px solid #263354;border-radius:10px;padding:9px 14px;margin:6px 0;font-size:13.5px}}
.rung.hit{{border-color:#0fa86e;background:#11321f}}
.q{{background:#1a2336;border-left:4px solid #ffd166;border-radius:10px;padding:11px 14px;margin:7px 0;font-size:14px}}
.q b{{color:#ffd166}}
.note{{color:#5d6residual880;font-size:11.5px;color:#5d6880;margin-top:26px;border-top:1px solid #243049;padding-top:12px}}
</style></head><body><div class="wrap">

<h1>💼 The Machine — your money at a glance</h1>
<div class="sub">LIRA · statements {pf['meta'].get('as_of','')} · dashboard {date.today()} · refresh: <code>python3 scripts/build_dashboard.py</code></div>

<div class="tiles">
<div class="tile"><div class="k">Total</div><div class="v">{money(total)}</div></div>
<div class="tile"><div class="k">Unrealized gain</div><div class="v g">{money(gain)}</div></div>
<div class="tile"><div class="k">Fees: now → target</div><div class="v y">{money(fee_now)} → {money(fee_tgt)}</div></div>
<div class="tile"><div class="k">Cash (dry powder)</div><div class="v">{money(cash)}</div></div>
</div>

<h2>⏳ Decisions waiting on you</h2>
<div class="q"><b>1.</b> Send <b>advisor_sheet.pdf</b> to Wes — unlocks the $4,038/yr fee switch.</div>
<div class="q"><b>2.</b> Pick first Forever-20 inductees (Tier-1 chips below) — 2–3 max this quarter.</div>
<div class="q"><b>3.</b> Approve a TSM patience-entry ladder (waiting beats chasing).</div>

<h2>🏛️ Forever 20 — {len(members)} of 20 slots filled</h2>
<div class="board">{slots}</div>
<div class="chips"><b style="font-size:12px;color:#8d97b0">CANDIDATES&nbsp;</b>{cand_chips}</div>

<h2>📊 Holdings — weighted analyst view (⭐ = forever member)</h2>
<table>{hold_rows}</table>

<h2>🪜 MDA dip ladder (price C${mda_price})</h2>
{ladder}

<h2>🔭 Watch themes</h2>
<div class="chips">{theme_chips}</div>

<div class="note">Decision-support only — not financial advice. You own every decision.
Data: your statements + public analyst sources. Nothing here is shared anywhere.</div>
</div></body></html>"""

    OUT.write_text(html)
    print(f"Wrote {OUT} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
