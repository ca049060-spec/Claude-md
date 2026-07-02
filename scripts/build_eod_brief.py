#!/usr/bin/env python3
"""
build_eod_brief.py — the end-of-day brief.

Answers one question every evening: "what's going on?" It reads the evergreen
database, your decision journal, the evolution log, and the legal radar, then
writes eod_brief.html — a personal digest, not a generic market recap:
  - portfolio pulse
  - what moved today (from the watch changelog)
  - YOUR scorecard (your calls vs the cautious call — the anti-generic core)
  - on the radar (deep-crawl names + flags)
  - legal radar (new litigation sense)
  - how the system evolved (so improvement is visible)
  - open loops to grade

Output is GITIGNORED (personal context). NOT financial advice.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "watch_state.json"
JOURNAL = ROOT / "data" / "decision_journal.yml"
EVOLUTION = ROOT / "data" / "evolution_log.yml"
LITIGATION = ROOT / "data" / "litigation.local.yml"
OUT = ROOT / "eod_brief.html"


def load_yaml(p):
    if p.exists():
        try:
            return yaml.safe_load(p.read_text()) or {}
        except Exception:
            return {}
    return {}


def esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    db = json.loads(STATE.read_text()) if STATE.exists() else {"tickers": {}, "changelog": [], "counts": {}}
    journal = load_yaml(JOURNAL).get("decisions", [])
    evo = load_yaml(EVOLUTION).get("milestones", [])
    lit = load_yaml(LITIGATION).get("findings", [])

    today = str(date.today())
    recs = db.get("tickers", {})
    counts = db.get("counts", {})

    # --- scorecard: your calls vs the cautious call ---
    graded = [d for d in journal if d.get("winner") in ("shawn", "cautious", "tie")]
    you = sum(1 for d in graded if d["winner"] == "shawn")
    cautious = sum(1 for d in graded if d["winner"] == "cautious")
    tie = sum(1 for d in graded if d["winner"] == "tie")
    open_calls = [d for d in journal if d.get("winner") == "open"]
    wins = [d for d in graded if d["winner"] == "shawn"]
    miss = [d for d in graded if d["winner"] == "cautious"]

    # --- what moved today ---
    todays = [c for c in db.get("changelog", []) if c.get("date") == today]
    recent = list(reversed(db.get("changelog", [])))[:8]
    moved = todays if todays else recent
    moved_html = "".join(
        f'<div class="chg"><b>{esc(c["ticker"])}</b> <span class="muted">{esc(c["date"])}</span> — {esc(c["change"])}</div>'
        for c in moved) or '<div class="muted">Quiet day — no tracked name moved materially.</div>'

    # --- on the radar (deep-crawl set + flags) ---
    radar = sorted([r for r in recs.values() if r.get("deep_crawl")],
                   key=lambda r: -(r.get("composite") or 0))
    radar_html = ""
    for r in radar:
        flags = "".join(f'<span class="flag">⚠ {esc(f)}</span>' for f in r.get("flags", []))
        comp = f'{r["composite"]:.2f}' if r.get("composite") is not None else "—"
        radar_html += (f'<tr><td><b>{esc(r["ticker"])}</b>{" <span class=held>HELD</span>" if r.get("held") else ""}'
                       f'<div class="co">{esc(r.get("company_name"))}</div></td>'
                       f'<td class="tag">{esc(r.get("classification"))}</td>'
                       f'<td class="num">{comp}</td><td>{flags}</td></tr>')

    # --- legal radar ---
    lit_html = "".join(
        f'<div class="lit"><span class="sev sev-{esc(f.get("severity","medium"))}"></span>'
        f'<b>{esc(f.get("ticker"))}</b> — {esc(f.get("case"))} '
        f'<span class="muted">({esc(f.get("court"))} · {esc(f.get("docket"))})</span>'
        f'<div class="co">{esc(f.get("relevance"))}</div></div>'
        for f in lit) or '<div class="muted">No litigation flagged on tracked names yet.</div>'

    # --- evolution ---
    evo_html = "".join(
        f'<div class="evo"><span class="muted">{esc(m.get("date"))}</span> '
        f'<span class="kind">{esc(m.get("kind"))}</span> {esc(m.get("gained"))}</div>'
        for m in list(reversed(evo))[:5])

    # --- open loops ---
    loops_html = "".join(
        f'<div class="loop"><b>{esc(d.get("id"))}</b> — {esc(d.get("cautious_call"))} '
        f'<span class="muted">(grade: {esc(d.get("magnitude"))})</span></div>'
        for d in open_calls) or '<div class="muted">No open calls to grade.</div>'

    wins_txt = " · ".join(f'{esc(w["id"].split("_")[0])} {esc(w.get("magnitude","").split(";")[0])}' for w in wins[:5])
    miss_txt = " · ".join(f'{esc(m["id"])}: {esc(m.get("magnitude",""))}' for m in miss) or "none recorded"

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>End of Day — {today}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0e1521;color:#e8edf4;padding:16px;line-height:1.45}}
.wrap{{max-width:860px;margin:0 auto}}
h1{{font-size:21px}} .date{{color:#6fa8ff;font-weight:700}}
.hello{{color:#9fb2cc;font-size:13px;margin:4px 0 16px}}
.band{{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap}}
.kpi{{background:#16202e;border-radius:10px;padding:9px 13px;flex:1;min-width:88px}}
.kpi .n{{font-size:20px;font-weight:800}} .kpi .l{{font-size:9px;color:#8aa0bd;text-transform:uppercase;letter-spacing:.8px}}
.sec{{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#cdd9e8;margin:20px 0 8px;border-left:3px solid #2f5fa0;padding-left:8px}}
.card{{background:#141d29;border-radius:10px;padding:11px 14px;margin-bottom:4px}}
.chg{{font-size:13px;padding:3px 0;border-bottom:1px solid #1b2939}}
.score{{display:flex;gap:10px;align-items:center;background:#13251c;border:1px solid #1f4a32;border-radius:10px;padding:12px 15px}}
.score .big{{font-size:30px;font-weight:800;color:#3ddc97}} .score small{{color:#9fb2cc;font-size:12px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td,th{{padding:7px 6px;border-bottom:1px solid #1c2735;text-align:left;vertical-align:top}}
th{{color:#7e93b0;font-size:10px;text-transform:uppercase}}
.num{{text-align:right;font-variant-numeric:tabular-nums}} .co{{font-size:11px;color:#8aa0bd}}
.tag{{color:#6f8bb0;font-size:11px}} .muted{{color:#64748b}} .held{{background:#243a52;color:#7fb0e8;font-size:8px;padding:1px 5px;border-radius:7px}}
.flag{{display:inline-block;font-size:10px;color:#e0a3a3;background:#2a1a1d;border-radius:6px;padding:1px 6px;margin:1px}}
.lit{{font-size:13px;padding:6px 0;border-bottom:1px solid #1b2939;position:relative;padding-left:16px}}
.sev{{position:absolute;left:0;top:9px;width:8px;height:8px;border-radius:50%}}
.sev-high{{background:#e8593d}} .sev-medium{{background:#e8c84a}} .sev-low{{background:#5fae6b}}
.evo{{font-size:12px;padding:4px 0;border-bottom:1px solid #1b2939;color:#c7d4e4}}
.kind{{background:#1d2c3f;color:#8fb6e8;font-size:9px;text-transform:uppercase;letter-spacing:.5px;padding:1px 6px;border-radius:6px;margin-right:5px}}
.loop{{font-size:12px;padding:3px 0;color:#c7d4e4}}
</style></head><body><div class="wrap">
<h1>End of Day — <span class="date">{today}</span></h1>
<div class="hello">Here's what's going on, Shawn. Your system — not a generic feed. {len(recs)} names tracked, {len(radar)} on deep watch.</div>

<div class="band">
<div class="kpi"><div class="n">{counts.get('total',len(recs))}</div><div class="l">Tracked</div></div>
<div class="kpi"><div class="n" style="color:#8fd14f">{len(radar)}</div><div class="l">Deep watch</div></div>
<div class="kpi"><div class="n" style="color:#e8593d">{sum(len(r.get('flags',[])) for r in recs.values())}</div><div class="l">Active flags</div></div>
<div class="kpi"><div class="n" style="color:#e8c84a">{len(open_calls)}</div><div class="l">Open calls</div></div>
<div class="kpi"><div class="n" style="color:#a78bfa">{len(lit)}</div><div class="l">Legal items</div></div>
</div>

<div class="sec">⚡ What moved today</div>
<div class="card">{moved_html}</div>

<div class="sec">🏆 Your scorecard — your judgment vs the cautious call</div>
<div class="score"><div class="big">{you}&ndash;{cautious}{f'&ndash;{tie}' if tie else ''}</div>
<div><small>Graded divergent calls where you went against the cautious/AI read.<br>
<b style="color:#8fd14f">Wins:</b> {wins_txt or '—'}<br>
<b style="color:#e0a3a3">Honest miss:</b> {miss_txt}</small></div></div>

<div class="sec">🎯 On the radar (deep-crawl set)</div>
<table><tr><th>Name</th><th>Tier</th><th class="num">VACS</th><th>Flags</th></tr>{radar_html}</table>

<div class="sec">⚖️ Legal radar (new sense)</div>
<div class="card">{lit_html}</div>

<div class="sec">🧬 How the system evolved (latest)</div>
<div class="card">{evo_html}</div>

<div class="sec">🔄 Open loops to grade</div>
<div class="card">{loops_html}</div>

<div class="hello" style="margin-top:18px">Regenerate anytime: <code>python3 scripts/build_eod_brief.py</code>. Scores PROPOSED until you ratify. Not advice.</div>
</div></body></html>"""
    OUT.write_text(html)
    print(f"build_eod_brief.py -> {OUT.relative_to(ROOT)} (scorecard {you}-{cautious}-{tie}, {len(radar)} on radar, {len(lit)} legal)")


if __name__ == "__main__":
    main()
