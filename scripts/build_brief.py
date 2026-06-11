#!/usr/bin/env python3
"""
build_brief.py — research brief + projection page (brief.html, gitignored).

Generates an interactive page that combines:
  1. THE WHY — one card per Forever-20 candidate: thesis, moat, how it
     compounds, the bear risk, and how it fits YOUR portfolio.
  2. THE PROJECTION — under the Builder profile, where the portfolio
     lands at 5, 10, 15, 20 years across three scenarios (bear / base /
     bull), with a slider to play with assumptions.

Self-contained, offline. Refresh via:  python3 scripts/build_brief.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
OUT = ROOT / "brief.html"


def load(n):
    p = D / n
    return yaml.safe_load(p.read_text()) if p.exists() else {}


# Hand-curated brief per name. Kept short on purpose — the dashboard is
# for glances, the brief for understanding, neither for reading novels.
# Each entry: thesis, moat (the durable why), how it compounds, bear
# risk, fit (how it slots into THIS portfolio).
BRIEFS = {
    "ASML": {
        "tag": "Forever · Chip equipment monopoly",
        "thesis": "ASML makes the only machines on Earth that can print the most advanced chips. Without ASML, no NVIDIA, no Apple Silicon, no AI as we know it.",
        "moat": "Sole supplier of EUV lithography — a 30-year, $30B+ R&D head start that effectively cannot be replicated. They are the bottleneck of the digital economy.",
        "compounds": "Every chip generation requires more ASML machines, and each machine costs more (~$200M+ for EUV, ~$400M+ for High-NA). Customers cannot defer purchases without losing the node race.",
        "bear": "Concentrated customers (TSMC, Samsung, Intel) means a single buyer cycle delay hits revenue hard; export restrictions to China are a persistent overhang.",
        "fit": "You already own a small position. Upsizing turns it into a real Forever-20 anchor — your most defensible compounder, currently your most under-sized.",
    },
    "TSM": {
        "tag": "Forever · Chip fabrication monopoly",
        "thesis": "TSMC is the contract manufacturer for nearly every advanced chip in the world. Apple, NVIDIA, AMD — none of them make their own chips; TSMC does.",
        "moat": "Two-node process leadership compounds with scale: each new node costs $20B+ to develop, which has knocked Intel and Samsung off pace. Now effectively the sole leading-edge fab.",
        "compounds": "Pricing power is rising as competition thins. AI silicon demand gives TSMC the right to raise wafer prices, which they have repeatedly done.",
        "bear": "Taiwan geopolitics — a single, low-probability, catastrophic tail risk no diversification fully neutralizes. Cyclicality in mature nodes.",
        "fit": "Pairs with ASML as the matching chokepoint: ASML makes the machines, TSMC runs them. Buy on a real dip (semis routinely give 25-35% drawdowns), don't chase.",
    },
    "CDNS": {
        "tag": "Forever · Chip design monopoly",
        "thesis": "Every chip ever designed — by anyone — runs through Cadence or Synopsys software. A literal duopoly on the tools, with ~85% combined share.",
        "moat": "Engineers are trained on these tools at university; foundries certify against them; switching costs are measured in years. 85%+ recurring revenue.",
        "compounds": "AI is making chips more complex, not simpler — meaning more design tools, more verification cycles, more IP licensing. The duopoly is the toll-booth.",
        "bear": "Already trades at ~60x earnings; China export restrictions on EDA software could shave a customer pool overnight.",
        "fit": "Completes the semiconductor chokepoint trifecta with ASML + TSM. Pick CDNS or SNPS — coin flip; CDNS has slightly tighter financial discipline.",
    },
    "WCN": {
        "tag": "Forever · Local-monopoly compounder",
        "thesis": "Garbage doesn't care about the economy. Waste Connections owns landfills in secondary markets where they're often the only game in town.",
        "moat": "Landfill permits are nearly impossible to get in 2026; the ones already approved are irreplaceable assets. Local monopoly = local pricing power.",
        "compounds": "Two engines: (1) annual pricing increases of 4-6% above inflation, (2) disciplined acquisition flywheel buying up smaller haulers at scale advantages.",
        "bear": "Premium valuation (>30x earnings) leaves little room for error; M&A multiples in waste keep rising and could compress returns on capital.",
        "fit": "Your portfolio is heavy on cyclicals (banks, energy, semis). WCN is the opposite — GDP-proof, defensive ballast that still compounds. The 'sleep at night' forever pick.",
    },
    "ISRG": {
        "tag": "Forever · Healthcare razor-blade",
        "thesis": "Intuitive Surgical makes the da Vinci surgical robot. Once a hospital buys one and trains surgeons on it, they buy the disposable instruments for life.",
        "moat": "10,000+ systems installed globally; surgeons trained on da Vinci think in da Vinci's UI. Switching means retraining an entire surgical staff.",
        "compounds": "Razor-blade economics: each procedure consumes ~$1,500 of Intuitive's instruments; procedure volume grows ~15-17% annually; new surgical categories keep opening.",
        "bear": "Medtronic (Hugo) and J&J (Ottava) are launching credible competitors after 25 years of monopoly. Pricing could compress for the first time.",
        "fit": "Fills your 0% healthcare gap with a true monopoly — not a drug company gambling on patents, but a toll on the entire shift to robotic surgery.",
    },
    "KLAC": {
        "tag": "Forever · Hidden semiconductor monopoly",
        "thesis": "KLA makes the inspection machines that check whether a chip wafer has defects. >85% market share in optical wafer inspection — the quiet third leg of the chip-equipment trio.",
        "moat": "As chips get smaller, defects matter more — so the share of fab budgets going to KLA grows faster than overall equipment spending.",
        "compounds": "Structural mix shift: process-control intensity rising every node. KLA grows ~2x the broader equipment market over time.",
        "bear": "Brutal cyclicality (chip downturns are -40% earnings declines); China is a major customer at risk.",
        "fit": "The deep cut. If you want ASML+TSM+KLAC, you'd own the entire chip chokepoint chain — but three positions in semis is concentration. Pick two of the three.",
    },
    "CSU": {
        "tag": "Forever · The Canadian legend",
        "thesis": "Constellation Software has compounded shareholder capital at ~30% annually for two decades by quietly buying small, boring vertical-market software companies and letting them keep running.",
        "moat": "The acquisition flywheel is the moat: 1,000+ companies acquired, decentralized model, near-zero churn (the software is mission-critical to its users).",
        "compounds": "Endless tuck-in pipeline at low multiples; cash from existing businesses funds the next ones. Spinoffs (Topicus, Lumine) keep extending the runway.",
        "bear": "Size — they're now too big for small deals to move the needle. Founder Mark Leonard's eventual succession is a real risk to capital allocation discipline.",
        "fit": "TSX-listed Canadian compounder, anti-correlated to your bank/energy exposure. The closest thing to a Canadian Berkshire Hathaway.",
    },
}

# Default Builder allocation, used for the projection.
BUILDER = {"DEF": 30000, "ASML": 10000, "WCN": 10000, "ISRG": 9000,
           "TSM": 9000, "CDNS": 9000, "DIP": 9000}


def main() -> None:
    pf = load("portfolio.yml")
    if not pf:
        sys.exit("missing data/portfolio.yml")
    rate = float(pf["meta"].get("usd_cad_rate", 1.0))

    total = stocks = funds = cash = 0.0
    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        b = pf.get(sleeve, {})
        for s in b.get("stocks", []):
            stocks += s["market_value"] * fx
        for f in b.get("mutual_funds", []):
            funds += f["market_value"] * fx
        for m in b.get("money_market", []):
            cash += m["market_value"] * fx
        cash += b.get("cash", 0) * fx
    total = stocks + funds + cash

    # After the Builder plan: ETF-swap funds (no value change), redeploy
    # most of cash into stocks, keep $30K as defensive sleeve.
    new_stocks = stocks + sum(v for k, v in BUILDER.items() if k not in ("DEF", "DIP"))
    new_cash = BUILDER["DEF"] + BUILDER["DIP"]
    new_total = new_stocks + funds + new_cash

    # Fee savings flow back as additional invested capital each year.
    fee_savings_yr = 4038

    state = {
        "total": round(total), "stocks": round(stocks), "funds": round(funds),
        "cash": round(cash), "newTotal": round(new_total),
        "newStocks": round(new_stocks), "newCash": round(new_cash),
        "feeSavings": fee_savings_yr,
        "briefs": [
            {"id": k, **v} for k, v in BRIEFS.items()
        ],
    }
    data_json = json.dumps(state)

    html = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Research Brief & Projection</title><style>
*{box-sizing:border-box}body{margin:0;background:#0f1522;color:#e8ecf5;
font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:780px;margin:0 auto;padding:22px 16px 60px}
h1{font-size:22px;margin:0}.sub{color:#8d97b0;font-size:12.5px;margin:3px 0 22px}
h2{font-size:13px;color:#9db4e8;text-transform:uppercase;letter-spacing:.06em;margin:26px 0 10px}
.card{background:#1a2336;border:1px solid #263354;border-radius:14px;padding:16px;margin:10px 0}
.card .tk{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.card .nm{font-size:18px;font-weight:700;color:#3ddc97}
.card .tag{font-size:11.5px;color:#8d97b0}
.card p{margin:6px 0;font-size:13.8px}
.card .lbl{color:#9db4e8;font-weight:700;text-transform:uppercase;font-size:10.5px;letter-spacing:.05em}
.card .bear{color:#ff9890}.card .fit{color:#ffd166}
.proj{background:#1a2336;border:1px solid #263354;border-radius:14px;padding:16px}
.scen{display:flex;gap:8px;margin:10px 0 4px}
.scen div{flex:1;text-align:center;padding:10px;border-radius:10px;font-weight:700;font-size:13px}
.bear-c{background:#3a1d1a;color:#ff9890}.base-c{background:#1b2c46;color:#9db4e8}.bull-c{background:#11321f;color:#3ddc97}
.scen .lbl{font-size:10.5px;text-transform:uppercase;color:#8d97b0;font-weight:600;letter-spacing:.05em;margin-bottom:3px}
.scen .v{font-size:18px}
table.years{width:100%;border-collapse:collapse;margin-top:8px}
table.years td,table.years th{padding:7px;text-align:right;border-bottom:1px solid #243049;font-size:13.5px}
table.years th{color:#8d97b0;font-weight:600;font-size:11.5px;text-transform:uppercase;text-align:right}
table.years td:first-child,table.years th:first-child{text-align:left;color:#9db4e8}
.slider{margin:14px 0 6px}.slider label{font-size:12px;color:#8d97b0}
input[type=range]{width:100%;accent-color:#0fa86e}
.assump{font-size:11.5px;color:#5d6880;line-height:1.6;margin-top:10px;padding-top:10px;border-top:1px solid #243049}
.note{color:#5d6880;font-size:11.5px;margin-top:24px;border-top:1px solid #243049;padding-top:12px}
</style></head><body><div class="wrap">

<h1>📖 Research Brief & Projection</h1>
<div class="sub">The why behind each name, and where the Builder profile takes you. Generated __DATE__.</div>

<h2>The Builder Plan — projection</h2>
<div class="proj">
<div style="font-size:13.5px;line-height:1.7">
Starting from <b id="pT">$0</b> today. Builder profile redeploys ~$56K of cash into 5 Forever-20 positions
plus dip reserve, while the fee switch saves an extra <b>$4,038/yr</b> that's reinvested every year.
Stocks compound at the assumed rate below; the defensive sleeve grows at 4%/yr.
</div>

<div class="slider">
<label>Assumed annual stock-portfolio return: <b id="rLbl">7%</b> (Base)</label>
<input type="range" id="r" min="3" max="11" step="0.5" value="7" oninput="render()">
</div>

<div class="scen">
<div class="bear-c"><div class="lbl">Bear · 4%/yr</div><div class="v" id="b5">$0</div><div style="font-size:11px;opacity:.8" id="b20">at 20y</div></div>
<div class="base-c"><div class="lbl">Base · 7%/yr</div><div class="v" id="m5">$0</div><div style="font-size:11px;opacity:.8" id="m20">at 20y</div></div>
<div class="bull-c"><div class="lbl">Bull · 10%/yr</div><div class="v" id="u5">$0</div><div style="font-size:11px;opacity:.8" id="u20">at 20y</div></div>
</div>

<table class="years" id="tbl"></table>

<div class="assump">
<b>Assumptions:</b> stocks compound at the slider rate; defensive cash 4%/yr; the $4,038/yr in fee
savings is reinvested into stocks each year. <b>What this is not:</b> a prediction. Markets don't deliver
smooth returns. Real path = volatile, with multi-year drawdowns. The point of Forever-20 + dip-ladders
+ defensive sleeve is to keep you invested through them.
</div>
</div>

<h2>The names — one card each</h2>
<div id="briefs"></div>

<div class="note">Decision-support only — not financial advice. Briefs are condensed research summaries
of public information as of June 2026. Verify before any real trade. You own every decision.</div>
</div>

<script>
const S = __DATA__;
const fmt = n => '$'+Math.round(n/1000).toLocaleString()+'K';
const fmtM = n => '$'+(n/1000000).toFixed(2)+'M';
const out = n => n>=1000000 ? fmtM(n) : fmt(n);

function project(r, years){
  // Year-by-year: stocks compound, fee savings added, cash grows 4%.
  let stk = S.newStocks + S.funds; // funds become ETFs, part of stock allocation post-switch
  let csh = S.newCash;
  const out = [];
  for(let y=1;y<=years;y++){
    stk = stk * (1+r) + S.feeSavings;
    csh = csh * 1.04;
    out.push({y, stk, csh, tot: stk+csh});
  }
  return out;
}

function render(){
  const r = +document.getElementById('r').value;
  document.getElementById('rLbl').textContent = r.toFixed(1)+'% (' + (r<=5?'Conservative':r<=8?'Base':r<=10?'Optimistic':'Bull') + ')';
  document.getElementById('pT').textContent = fmt(S.total);

  const bear20 = project(0.04, 20);
  const base20 = project(r/100, 20);
  const bull20 = project(0.10, 20);

  document.getElementById('b5').textContent = out(bear20[4].tot);
  document.getElementById('m5').textContent = out(base20[4].tot);
  document.getElementById('u5').textContent = out(bull20[4].tot);
  document.getElementById('b20').textContent = 'at 20y → ' + out(bear20[19].tot);
  document.getElementById('m20').textContent = 'at 20y → ' + out(base20[19].tot);
  document.getElementById('u20').textContent = 'at 20y → ' + out(bull20[19].tot);

  // Year table for the chosen scenario
  let html = '<tr><th>Year</th><th>Bear 4%</th><th>Your '+r.toFixed(1)+'%</th><th>Bull 10%</th></tr>';
  [5,10,15,20].forEach(yr=>{
    html += `<tr><td>+${yr}y</td><td>${out(bear20[yr-1].tot)}</td><td><b>${out(base20[yr-1].tot)}</b></td><td>${out(bull20[yr-1].tot)}</td></tr>`;
  });
  document.getElementById('tbl').innerHTML = html;
}

// Render the brief cards
let bh = '';
S.briefs.forEach(b => {
  bh += `<div class="card"><div class="tk"><span class="nm">${b.id}</span><span class="tag">${b.tag}</span></div>
  <p>${b.thesis}</p>
  <p><span class="lbl">Moat</span><br>${b.moat}</p>
  <p><span class="lbl">How it compounds</span><br>${b.compounds}</p>
  <p class="bear"><span class="lbl" style="color:#ff9890">Bear risk</span><br>${b.bear}</p>
  <p class="fit"><span class="lbl" style="color:#ffd166">Fit in your portfolio</span><br>${b.fit}</p></div>`;
});
document.getElementById('briefs').innerHTML = bh;
render();
</script></body></html>"""
    html = html.replace("__DATA__", data_json).replace("__DATE__", str(date.today()))
    OUT.write_text(html)
    print(f"Wrote {OUT} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
