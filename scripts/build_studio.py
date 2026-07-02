#!/usr/bin/env python3
"""
build_studio.py — interactive Cash Deployment Studio (studio.html).

A self-contained, offline, INTERACTIVE page (vanilla JS, no server, no
libraries). Drag sliders to deploy the cash across jobs and candidate
stocks; everything updates live — remaining cash, defensive %, each new
position's portfolio weight, and the resulting asset mix bar. Presets let
you jump between strategies.

This is the "probe and visually represent" interface — think with it.
Regenerate: python3 scripts/build_studio.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
OUT = ROOT / "studio.html"


def load(n):
    p = D / n
    return yaml.safe_load(p.read_text()) if p.exists() else {}


def main() -> None:
    pf = load("portfolio.yml")
    if not pf:
        sys.exit("missing data/portfolio.yml")
    rate = float(pf["meta"].get("usd_cad_rate", 1.0))

    total = stocks_val = funds_val = cash = 0.0
    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        b = pf.get(sleeve, {})
        for s in b.get("stocks", []):
            stocks_val += s["market_value"] * fx
        for f in b.get("mutual_funds", []):
            funds_val += f["market_value"] * fx
        for m in b.get("money_market", []):
            cash += m["market_value"] * fx
        cash += b.get("cash", 0) * fx
    total = stocks_val + funds_val + cash

    # Deployable cash = the savings position (keep small float cash aside).
    deployable = round(cash, 0)

    # Candidate menu the user can fund (label, ccy note, sector gap filled).
    candidates = [
        {"id": "ASML", "name": "ASML (upsize)", "tag": "Forever · chips", "def": 8000},
        {"id": "TSM", "name": "TSM", "tag": "Forever · chip fab", "def": 0},
        {"id": "CDNS", "name": "Cadence", "tag": "Forever · chip design", "def": 0},
        {"id": "WCN", "name": "Waste Connections", "tag": "Forever · monopoly", "def": 10000},
        {"id": "ISRG", "name": "Intuitive Surgical", "tag": "Forever · healthcare", "def": 10000},
        {"id": "CSU", "name": "Constellation SW", "tag": "Forever · Canada", "def": 0},
        {"id": "DIP", "name": "Dip ammunition", "tag": "held in reserve", "def": 13000},
    ]
    state = {
        "total": round(total), "stocks": round(stocks_val),
        "funds": round(funds_val), "cash": round(cash),
        "deployable": deployable, "candidates": candidates,
        "defaultDefensive": 45000,
    }
    data_json = json.dumps(state)

    html = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cash Deployment Studio</title><style>
*{box-sizing:border-box}body{margin:0;background:#0f1522;color:#e8ecf5;
font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:22px 16px 60px}
h1{font-size:20px;margin:0}.sub{color:#8d97b0;font-size:12.5px;margin:3px 0 16px}
.big{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}
.kpi{flex:1;min-width:140px;background:#1a2336;border:1px solid #263354;border-radius:14px;padding:12px 14px}
.kpi .k{font-size:11px;color:#8d97b0;text-transform:uppercase;letter-spacing:.05em}
.kpi .v{font-size:22px;font-weight:700;margin-top:3px}
.g{color:#3ddc97}.r{color:#ff6b5e}.y{color:#ffd166}
.presets{display:flex;gap:8px;margin:8px 0 18px;flex-wrap:wrap}
.presets button{background:#1f2c45;color:#9db4e8;border:1px solid #2f4470;border-radius:20px;
padding:7px 15px;font-size:13px;font-weight:600;cursor:pointer}
.presets button:hover{background:#27375a}
.row{background:#1a2336;border:1px solid #263354;border-radius:12px;padding:12px 14px;margin:9px 0}
.row .top{display:flex;justify-content:space-between;align-items:baseline}
.row .nm{font-weight:700}.row .tag{font-size:11.5px;color:#8d97b0;margin-left:8px;font-weight:400}
.row .amt{font-variant-numeric:tabular-nums;font-weight:700;color:#3ddc97}
.row .wt{font-size:11.5px;color:#8d97b0}
input[type=range]{width:100%;margin:9px 0 0;accent-color:#0fa86e}
.mix{display:flex;height:30px;border-radius:9px;overflow:hidden;margin:6px 0 4px;border:1px solid #263354}
.mix span{display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#0f1522}
.legend{font-size:11.5px;color:#8d97b0}
.warn{color:#ff6b5e;font-weight:700}
.note{color:#5d6880;font-size:11.5px;margin-top:22px;border-top:1px solid #243049;padding-top:12px}
h2{font-size:13px;color:#9db4e8;text-transform:uppercase;letter-spacing:.06em;margin:22px 0 8px}
</style></head><body><div class="wrap">
<h1>🎛️ Cash Deployment Studio</h1>
<div class="sub">Drag to deploy your cash across jobs. Everything updates live. Nothing here places a trade — it's a thinking tool.</div>

<div class="big">
<div class="kpi"><div class="k">Cash to deploy</div><div class="v" id="kCash"></div></div>
<div class="kpi"><div class="k">Still unallocated</div><div class="v g" id="kLeft"></div></div>
<div class="kpi"><div class="k">Defensive sleeve</div><div class="v y" id="kDef"></div></div>
</div>

<h2>Asset mix after your plan</h2>
<div class="mix" id="mix"></div>
<div class="legend" id="legend"></div>

<div class="presets">
<button onclick="preset('conservative')">🛡️ Conservative</button>
<button onclick="preset('balanced')">⚖️ Balanced (mine)</button>
<button onclick="preset('builder')">🏗️ Builder</button>
<button onclick="preset('zero')">↺ Reset to 0</button>
</div>

<h2>Defensive sleeve — cash you KEEP</h2>
<div class="row"><div class="top"><span><span class="nm">Defensive (kept as cash)</span>
<span class="tag">2–3 yrs of future withdrawals — lets you never sell in a crash</span></span>
<span class="amt" id="aDEF">$0</span></div>
<input type="range" id="sDEF" min="0" max="86859" step="1000" oninput="render()"></div>

<h2>Deploy into Forever-20 + reserves</h2>
<div id="cands"></div>

<div class="note">Decision-support only — not financial advice. You own every decision.
Plays with sizing only; verify prices/availability before any real trade.</div>
</div>
<script>
const S = __DATA__;
const fmt = n => '$'+Math.round(n).toLocaleString();
// build candidate rows
let html='';
S.candidates.forEach(c=>{html+=`<div class="row"><div class="top">
<span><span class="nm">${c.name}</span><span class="tag">${c.tag}</span></span>
<span class="amt" id="a${c.id}">$0</span></div>
<input type="range" id="s${c.id}" min="0" max="40000" step="1000" oninput="render()">
<div class="wt" id="w${c.id}"></div></div>`;});
document.getElementById('cands').innerHTML=html;

function val(id){return +document.getElementById('s'+id).value;}
function setv(id,v){document.getElementById('s'+id).value=v;}

function preset(p){
  const z={DEF:0};S.candidates.forEach(c=>z[c.id]=0);
  let m=z;
  if(p==='conservative')m={DEF:60000,ASML:6000,WCN:8000,ISRG:0,TSM:0,CDNS:0,CSU:0,DIP:12000};
  if(p==='balanced')m={DEF:45000,ASML:8000,WCN:10000,ISRG:10000,TSM:0,CDNS:0,CSU:0,DIP:13000};
  if(p==='builder')m={DEF:30000,ASML:10000,WCN:10000,ISRG:9000,TSM:9000,CDNS:9000,CSU:0,DIP:9000};
  setv('DEF',m.DEF||0);S.candidates.forEach(c=>setv(c.id,m[c.id]||0));
  render();
}

function render(){
  let deployed=0, def=val('DEF');
  S.candidates.forEach(c=>{
    const v=val(c.id);
    document.getElementById('a'+c.id).textContent=fmt(v);
    const newW=(c.id==='DIP')?0:v/(S.total)*100;
    document.getElementById('w'+c.id).textContent=
      c.id==='DIP'? 'held in reserve' : (v>0? `→ new position ≈ ${newW.toFixed(1)}% of portfolio`:'');
    if(c.id!=='DIP') deployed+=v;
  });
  const dip=val('DIP');
  document.getElementById('aDEF').textContent=fmt(def);
  const used=def+deployed+dip;
  const left=S.deployable-used;
  document.getElementById('kCash').textContent=fmt(S.deployable);
  const kl=document.getElementById('kLeft');
  kl.textContent=fmt(left); kl.className='v '+(left<0?'r':'g');
  if(left<0) kl.innerHTML=`<span class="warn">${fmt(left)} OVER</span>`;
  document.getElementById('kDef').textContent=fmt(def+dip);

  // asset mix: stocks (existing+deployed), funds, cash(def+dip+leftover)
  const newStocks=S.stocks+deployed;
  const newCash=def+dip+Math.max(left,0);
  const tot=newStocks+S.funds+newCash;
  const segs=[['Stocks',newStocks,'#3ddc97'],['Funds',S.funds,'#9db4e8'],['Cash',newCash,'#ffd166']];
  let mh='',lg=[];
  segs.forEach(([n,v,c])=>{const p=v/tot*100;mh+=`<span style="width:${p}%;background:${c}">${p>9?Math.round(p)+'%':''}</span>`;
    lg.push(`<b style="color:${c}">■</b> ${n} ${fmt(v)}`);});
  document.getElementById('mix').innerHTML=mh;
  document.getElementById('legend').innerHTML=lg.join(' &nbsp; ');
}
preset('balanced');
</script></body></html>"""
    html = html.replace("__DATA__", data_json)
    OUT.write_text(html)
    print(f"Wrote {OUT} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
