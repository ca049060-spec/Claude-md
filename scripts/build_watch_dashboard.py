#!/usr/bin/env python3
"""
build_watch_dashboard.py — render the ONE master watch dashboard.

Reads data/watch_state.json (the evergreen database produced by watch.py)
and emits watch.html: a single, always-current view that replaces the
scattered one-off report files. Grouped by tier, with a "What changed"
feed at the top so the first thing you see is the delta since last refresh.

Output is GITIGNORED (holds personal financial context).
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "watch_state.json"
OUT = ROOT / "watch.html"

TIER_ORDER = [
    ("Top 20 Confirmed (Tier 1)", "#3ddc97", "★ Confirmed — own-forever tier"),
    ("Conditional Top 20", "#5fe0a0", "Conditional Top-20"),
    ("Tier 2 — Watchlist", "#8fd14f", "Tier 2 — Watchlist"),
    ("Needs Work", "#e8c84a", "Needs Work"),
    ("Tactical Only", "#e8934a", "Tactical Only"),
    ("Speculative ($3-5K cap)", "#e8934a", "Speculative"),
]


def esc(s):
    return (str(s) if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def price_cell(rec):
    p = rec.get("price")
    if not p:
        return '<span class="muted">—</span>'
    sym = "C$" if rec.get("currency") == "CAD" else "$"
    return f'{sym}{p["last"]:.2f} <span class="muted">{esc(p.get("asof",""))}</span>'


def spark(hist):
    """Tiny inline SVG sparkline of composite history."""
    vals = [h.get("composite") for h in (hist or []) if h.get("composite") is not None]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    w, h = 70, 18
    pts = " ".join(f"{i/(len(vals)-1)*w:.1f},{h-(v-lo)/rng*h:.1f}" for i, v in enumerate(vals))
    return f'<svg width="{w}" height="{h}"><polyline points="{pts}" fill="none" stroke="#6fa8ff" stroke-width="1.5"/></svg>'


def row(rec):
    s = rec.get("vacs") or {}
    sc = "·".join(f"{k}{int(s[k])}" for k in ("V", "A", "C", "S")) if s else "—"
    flags = "".join(f'<div class="flag">⚠ {esc(f)}</div>' for f in rec.get("flags", []))
    held = '<span class="held">HELD</span>' if rec.get("held") else ""
    comp = rec.get("composite")
    comp_txt = f'{comp:.2f}' if comp is not None else "—"
    return f"""<tr>
      <td><b>{esc(rec['ticker'])}</b>{held}<div class="co">{esc(rec.get('company_name'))}</div></td>
      <td class="tag">{esc(rec.get('pillar'))}</td>
      <td class="num">{price_cell(rec)}</td>
      <td class="num">{esc(rec.get('gate_math'))}</td>
      <td class="vacs">{sc}{flags}</td>
      <td class="num"><b>{comp_txt}</b><div>{spark(rec.get('history'))}</div></td>
    </tr>"""


def section_redemption(recs):
    if not recs:
        return ""
    items = " · ".join(f"<b>{esc(r['ticker'])}</b> <span class='muted'>{esc(r.get('classification',''))}</span>" for r in recs)
    return f"""<div class="sec">🪦 Redemption watch — killed, but monitored for a comeback ({len(recs)})</div>
    <div class="watchrow">{items}</div>"""


def section_quality(recs):
    if not recs:
        return ""
    items = " · ".join(f"<b>{esc(r['ticker'])}</b> <span class='muted'>{esc(r.get('gate_math',''))}</span>" for r in recs)
    return f"""<div class="sec">💎 Quality compounders — too big to 20x, kept via escape hatch ({len(recs)})</div>
    <div class="watchrow">{items}</div>"""


def main():
    if not STATE.exists():
        raise SystemExit("No watch_state.json — run scripts/watch.py first.")
    db = json.loads(STATE.read_text())
    recs = list(db["tickers"].values())
    by_tier = {}
    for r in recs:
        if r["scope"] in ("survivor", "holding") and r.get("status") == "SCORED":
            by_tier.setdefault(r.get("classification"), []).append(r)
    quality = [r for r in recs if r["scope"] == "quality_compounder"]
    redemption = sorted([r for r in recs if r["scope"] == "redemption_watch"], key=lambda r: r["ticker"])

    # changelog feed (most recent first)
    recent = list(reversed(db.get("changelog", [])))[:14]
    feed = "".join(
        f'<div class="chg"><span class="chgt">{esc(c["ticker"])}</span> '
        f'<span class="muted">{esc(c["date"])}</span> — {esc(c["change"])}</div>'
        for c in recent) or '<div class="muted">No changes recorded yet — this is the baseline snapshot.</div>'

    blocks = []
    for name, color, label in TIER_ORDER:
        rs = sorted(by_tier.get(name, []), key=lambda r: -(r.get("composite") or 0))
        if not rs:
            continue
        rows = "".join(row(r) for r in rs)
        blocks.append(f"""<div class="sec" style="border-color:{color}">{esc(label)} ({len(rs)})</div>
        <table><tr><th>Name</th><th>Pillar</th><th class="num">Price</th><th class="num">20x gate</th>
        <th>V·A·C·S</th><th class="num">VACS</th></tr>{rows}</table>""")

    c = db.get("counts", {})
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>VACS Watch — live</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#0f1622;color:#e8edf4;padding:16px;line-height:1.4}}
.wrap{{max-width:920px;margin:0 auto}}
h1{{font-size:20px}} .sub{{color:#8aa0bd;font-size:12px;margin-bottom:14px}}
.band{{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}}
.kpi{{background:#16202e;border-radius:10px;padding:9px 13px;flex:1;min-width:90px}}
.kpi .n{{font-size:20px;font-weight:800}} .kpi .l{{font-size:9px;color:#8aa0bd;text-transform:uppercase;letter-spacing:1px}}
.feed{{background:#13202c;border:1px solid #1e3344;border-radius:10px;padding:10px 13px;margin-bottom:16px}}
.feed h2{{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#6fa8ff;margin-bottom:7px}}
.chg{{font-size:12px;padding:3px 0;border-bottom:1px solid #182636}} .chgt{{font-weight:700;color:#cfe0f5}}
.sec{{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#cdd9e8;margin:18px 0 7px;border-left:3px solid #444;padding-left:8px}}
table{{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:4px}}
td,th{{padding:7px 6px;border-bottom:1px solid #1c2735;text-align:left;vertical-align:top}}
th{{color:#7e93b0;font-size:10px;text-transform:uppercase}}
.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
.co{{font-size:11px;color:#8aa0bd}} .tag{{color:#6f8bb0;font-size:11px}}
.vacs{{font-size:12px;color:#b9c8db}} .muted{{color:#64748b;font-size:11px}}
.held{{background:#243a52;color:#7fb0e8;font-size:8px;padding:1px 5px;border-radius:7px;margin-left:5px;vertical-align:middle}}
.flag{{font-size:10px;color:#d98a8a;margin-top:2px}}
.watchrow{{font-size:12px;color:#aebbcd;background:#141d29;border-radius:8px;padding:9px 12px;margin-bottom:4px;line-height:1.9}}
</style></head><body><div class="wrap">
<h1>VACS Watch — live database</h1>
<div class="sub">Generated {esc(db.get('generated'))} · scope: {esc(db.get('scope_rule'))} · scores PROPOSED until ratified · not advice</div>
<div class="band">
<div class="kpi"><div class="n" style="color:#8fd14f">{c.get('survivor',0)}</div><div class="l">Survivors</div></div>
<div class="kpi"><div class="n" style="color:#7fb0e8">{c.get('holding',0)}</div><div class="l">Held</div></div>
<div class="kpi"><div class="n" style="color:#e8c84a">{c.get('redemption_watch',0)}</div><div class="l">Redemption watch</div></div>
<div class="kpi"><div class="n" style="color:#a78bfa">{c.get('quality_compounder',0)}</div><div class="l">Quality</div></div>
<div class="kpi"><div class="n">{c.get('total',0)}</div><div class="l">Total tracked</div></div>
</div>
<div class="feed"><h2>⚡ What changed since last refresh</h2>{feed}</div>
{''.join(blocks)}
{section_quality(quality)}
{section_redemption(redemption)}
<div class="sub" style="margin-top:18px">One file, always current. Regenerate with <code>python3 scripts/watch.py &amp;&amp; python3 scripts/build_watch_dashboard.py</code>.</div>
</div></body></html>"""
    OUT.write_text(html)
    print(f"build_watch_dashboard.py -> {OUT.relative_to(ROOT)} ({len(recs)} names)")


if __name__ == "__main__":
    main()
