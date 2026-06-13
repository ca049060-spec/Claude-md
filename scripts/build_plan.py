#!/usr/bin/env python3
"""
build_plan.py — "The Plan, on one page" (plan.html, gitignored).

Not a data table — a calm, plain-language, visual one-pager designed to be
understood at a glance by someone who thinks in pictures, not text. It tells
the story: where you stand -> the 3 moves in order -> what you'll own ->
what NOT to do -> the timeline. Big type, short sentences, lots of air.
"""
from __future__ import annotations
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "plan.html"
pf = yaml.safe_load((ROOT / "data" / "portfolio.yml").read_text())

# A few real numbers so the page stays honest/current.
TOTAL = 553291
FEES_NOW = 4490
GAIN = 185000

# Target mix (plain-language buckets, % of book) — from the master allocation.
MIX = [
    ("Your conviction stocks",  30, "#0fa86e", "MDA, BWXT, ASML, NOW, TSM — the ones you believe in for years"),
    ("The whole world",         30, "#9b6dff", "two simple ETFs (XAW + VFV) — global, cheap, diversified"),
    ("Canadian dividend payers", 22, "#4a86e8", "TD, Manulife, Enbridge, TC Energy — steady income"),
    ("Safety + dry powder",      17, "#e0a800", "short bonds + T-bill cash, ready to buy dips"),
    ("One lottery ticket",        1, "#e0526a", "BEAM — tiny, high-risk, sized so it can't hurt you"),
]

moves = [
    ("1", "📧", "Send one email", "Today",
     "Email Wes the question sheet (already written for you).",
     "It unlocks everything below — and confirms you can hold the ETFs.",
     "#0fa86e"),
    ("2", "🔄", "Swap 5 pricey funds for 2 cheap ETFs", "When Wes replies",
     "Your 5 mutual funds cost ~$4,490/year. ETFs cost almost nothing.",
     "Same money, global diversification, ~$4,000/year back in your pocket.",
     "#4a86e8"),
    ("3", "🎯", "Put your cash to work — slowly", "Over the summer",
     "Buy a little now (TSM), set price alerts for the rest, let dips come.",
     "No rushing. The Fed meeting Tuesday may hand you cheaper prices.",
     "#9b6dff"),
]

donts = [
    ("Don't buy the SpaceX IPO", "Too big to grow the way you need. You'd be buying others' exit."),
    ("Don't add MDA today", "It's ~C$57 — above your buy line. You already own 900 shares."),
    ("Don't deploy everything before Tuesday", "The Fed meeting + hot inflation = wait for the likely dip."),
    ("Don't chase the hot names", "MP, LEU and friends already ran. Patience, or pass."),
]

timeline = [
    ("TODAY", "Send the email. Buy nothing in a rush.", "#0fa86e"),
    ("THIS WEEK", "Set your price alerts. Watch, don't act.", "#4a86e8"),
    ("TUE Jun 17", "Fed meeting. If markets dip — that's your buy window.", "#e0a800"),
    ("AUGUST", "MDA earnings. The real test of your biggest holding.", "#9b6dff"),
    ("ONGOING", "Add great companies on weakness. Never panic-sell.", "#7a8699"),
]

def money(x): return f"${x:,.0f}"

mixbar = "".join(f"<span style='width:{p}%;background:{c}'></span>" for _,p,c,_ in MIX)
mixrows = "".join(
    f"<div class=mixrow><span class=dot style='background:{c}'></span>"
    f"<span class=mixp>{p}%</span><span class=mixn><b>{n}</b><br><span class=sm>{d}</span></span></div>"
    for n,p,c,d in MIX)

movecards = "".join(
    f"""<div class=move>
      <div class=mnum style='background:{c}'>{num}</div>
      <div class=mbody>
        <div class=mtop><span class=micon>{icon}</span><span class=mtitle>{title}</span>
          <span class=mwhen>{when}</span></div>
        <div class=mwhat>{what}</div>
        <div class=mwhy>↳ {why}</div>
      </div></div>"""
    for num,icon,title,when,what,why,c in moves)

dontcards = "".join(
    f"<div class=dont><span class=x>✕</span><div><b>{t}</b><br><span class=sm>{r}</span></div></div>"
    for t,r in donts)

timerows = "".join(
    f"<div class=trow><span class=tlabel style='color:{c}'>{w}</span>"
    f"<span class=tline style='background:{c}'></span><span class=ttext>{t}</span></div>"
    for w,t,c in timeline)

html = f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Your Plan</title><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0e1422;color:#eef1f8;font:16px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:680px;margin:0 auto;padding:28px 18px 70px}}
.sm{{font-size:13px;color:#97a1b8;line-height:1.45}}
.kicker{{font-size:12px;letter-spacing:.18em;color:#7a8699;text-transform:uppercase}}
h1{{font-size:30px;margin:6px 0 4px;letter-spacing:-.5px}}
.lede{{font-size:16px;color:#b8c0d4;margin-bottom:8px}}

/* where you stand */
.stand{{background:linear-gradient(135deg,#16203a,#121a30);border:1px solid #243150;border-radius:18px;padding:22px;margin:18px 0 8px}}
.big{{font-size:44px;font-weight:750;letter-spacing:-1px;line-height:1}}
.chips{{display:flex;gap:10px;margin-top:16px;flex-wrap:wrap}}
.chip{{flex:1;min-width:150px;background:#0e1626;border:1px solid #223;border-radius:12px;padding:12px 14px}}
.chip .n{{font-size:20px;font-weight:700}}
.chip.good .n{{color:#3ddc97}} .chip.warn .n{{color:#ffce5a}}
.chip .l{{font-size:11.5px;color:#8b95ad;text-transform:uppercase;letter-spacing:.04em;margin-top:2px}}

.sect{{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:#8b95ad;margin:34px 0 14px;font-weight:600}}

/* moves */
.move{{display:flex;gap:14px;background:#141d33;border:1px solid #233152;border-radius:16px;padding:16px;margin-bottom:12px}}
.mnum{{flex:0 0 38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;color:#06210f}}
.mtop{{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:6px}}
.micon{{font-size:20px}}
.mtitle{{font-size:18px;font-weight:700}}
.mwhen{{margin-left:auto;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#0e1422;background:#8b95ad;border-radius:20px;padding:3px 10px;font-weight:700}}
.mwhat{{font-size:15px;color:#dfe5f2}}
.mwhy{{font-size:13.5px;color:#9fb0d6;margin-top:5px}}

/* mix */
.mixbar{{display:flex;height:34px;border-radius:11px;overflow:hidden;margin-bottom:14px;border:1px solid #243150}}
.mixbar span{{display:block;height:100%}}
.mixrow{{display:flex;align-items:flex-start;gap:11px;padding:9px 2px;border-bottom:1px solid #1c2740}}
.mixrow:last-child{{border:none}}
.dot{{flex:0 0 12px;height:12px;border-radius:50%;margin-top:5px}}
.mixp{{flex:0 0 42px;font-weight:750;font-size:16px}}
.mixn{{font-size:14.5px}}

/* donts */
.dont{{display:flex;gap:12px;align-items:flex-start;background:#1c1320;border:1px solid #43263a;border-radius:13px;padding:13px 15px;margin-bottom:9px}}
.x{{flex:0 0 24px;height:24px;border-radius:50%;background:#e0526a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800;margin-top:1px}}

/* timeline */
.trow{{display:flex;align-items:center;gap:13px;margin-bottom:11px}}
.tlabel{{flex:0 0 92px;font-size:12px;font-weight:800;letter-spacing:.04em;text-align:right}}
.tline{{flex:0 0 10px;height:10px;border-radius:50%}}
.ttext{{font-size:14.5px;color:#dfe5f2}}

.foot{{margin-top:34px;padding:16px 18px;background:#121a2e;border:1px solid #223;border-radius:14px}}
.foot b{{color:#eef1f8}}
.flag{{background:#1c1812;border:1px solid #4a3a18;border-radius:13px;padding:13px 15px;margin-top:14px;font-size:13.5px;color:#e8d9b0}}
</style></head><body><div class=wrap>

<div class=kicker>Your money · plan on one page</div>
<h1>Here's what to do — and why</h1>
<div class=lede>Plain version. No jargon. You decide everything.</div>

<div class=stand>
  <div class=sm style="color:#8b95ad;letter-spacing:.04em;text-transform:uppercase;font-size:11.5px">What you have</div>
  <div class=big>{money(TOTAL)}</div>
  <div class=chips>
    <div class="chip good"><div class=n>+{money(GAIN)}</div><div class=l>Total gain so far</div></div>
    <div class="chip warn"><div class=n>{money(FEES_NOW)}/yr</div><div class=l>Hidden fund fees (fixable)</div></div>
    <div class="chip"><div class=n>$86.9K</div><div class=l>Cash to put to work</div></div>
  </div>
  <div class=sm style="margin-top:14px">You're up 22% in six months on your own calls. Healthy and growing —
  but quietly overpaying ~$4,490 a year in fund fees you don't need. That's the first thing we fix.</div>
</div>

<div class=sect>Do these 3 things, in order</div>
{movecards}

<div class=sect>What you'll own when it's done</div>
<div class=mixbar>{mixbar}</div>
{mixrows}

<div class=sect>Just as important — what NOT to do</div>
{dontcards}

<div class=sect>How it unfolds</div>
{timerows}

<div class=flag>⚠️ <b>One thing to check:</b> your ServiceNow (NOW) value on the statement looks off versus
its real market price. Ask Edward Jones to confirm that line — it could be a data quirk, or your value
could be understated. Worth 30 seconds to know.</div>

<div class=foot>
<b>The whole plan in one breath:</b> send the email today, swap the pricey funds for two cheap ETFs,
and feed your cash into a few great companies slowly through the summer — buying dips, never panic-selling.
That's it.<br><br>
<span class=sm>Built {date.today()} from your real statements. Not financial advice — these are well-researched
options. Every decision is yours.</span>
</div>
</div></body></html>"""
OUT.write_text(html)
print(f"Wrote {OUT} ({len(html):,} bytes)")
