#!/usr/bin/env python3
"""
vacs.py — Shawn's VACS Automated Scoring Engine (v2.0 spec implementation).

Faithful to VACS_Scoring_Engine_Spec_v2.json. Built around the spec's own
core warning: automating VACS INDUSTRIALIZES confirmation bias. So:
  - Stage 1 (20x gate) and Stage 2 (mechanical vetoes) are DETERMINISTIC and
    run FIRST and HARD — ~80% of candidates die before any subjective score.
  - V/A/C/S subjective scores are NEVER invented. Missing => status INCOMPLETE.
  - Every score is wrapped in a provenance object (PROPOSED until ratified).
  - Adversarial is scored LAST and is the most important dimension.
  - Quality-compounder routing is tagged escape_hatch_used for audit.
  - Batch with zero demotions emits a confirmation-trap warning.

Reproduces the spec's regression cases (BWXT 4.42, OKLO 2.67, ATS gate-kill).

Candidates live in data/vacs_candidates.yml. NOT financial advice.
"""
from __future__ import annotations
import sys
from datetime import date
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "data" / "vacs_candidates.yml"

ACTIVE_PILLARS = {"nuclear_smr", "space", "defense", "ai_physical", "copper", "robotics"}
BWXT_BENCHMARK = 4.42
STALENESS_DAYS = 7


def score_obj(value, source, evidence="", state="PROPOSED"):
    return {"value": value, "source": source, "provenance_state": state,
            "ratified_label": "SHAWN'S" if state == "RATIFIED" else "PROPOSED",
            "evidence": evidence, "timestamp": str(date.today())}


def classify(comp):
    if comp >= 4.0:  return "Top 20 Confirmed (Tier 1)"
    if comp >= 3.75: return "Conditional Top 20"
    if comp >= 3.5:  return "Tier 2 — Watchlist"
    if comp >= 3.0:  return "Needs Work"
    if comp >= 2.5:  return "Tactical Only"
    if comp >= 2.0:  return "Speculative ($3-5K cap)"
    return "Reject"


def gate_target(cap, ccy):
    t = cap * 20
    sym = "C$" if ccy == "CAD" else "$"
    def h(n):
        for d, s in ((1e12,"T"),(1e9,"B"),(1e6,"M")):
            if abs(n) >= d: return f"{sym}{n/d:.0f}{s}"
        return f"{sym}{n:.0f}"
    return h(cap), h(t)


def evaluate(c: dict) -> dict:
    r = {"ticker": c.get("ticker"), "as_of": c.get("as_of_date"), "flags": []}

    # Stage 0 — ETF short-circuit
    if c.get("is_etf"):
        r["status"] = "ETF_EXPRESSION"
        r["line"] = f"{c['ticker']} — ETF: pillar expression, not VACS-scored."
        return r

    # required fields
    for f in ("ticker", "company_name", "as_of_date", "market_cap", "currency", "thesis_pillars_touched"):
        if c.get(f) in (None, ""):
            r["status"] = "INCOMPLETE"; r["missing"] = f; return r

    # staleness
    try:
        if (date.today() - date.fromisoformat(c["as_of_date"])).days > STALENESS_DAYS:
            r["flags"].append(f"STALE as_of_date (> {STALENESS_DAYS}d) — gate may be invalid")
    except Exception:
        pass

    cap = float(c["market_cap"]); ccy = c["currency"]
    caph, tgth = gate_target(cap, ccy)
    r["gate_math"] = f"{caph} x20 = {tgth}"

    # Stage 1 — 20x gate (deterministic math + judgment boolean)
    plaus = c.get("gate_plausible_10_15yr")
    if plaus is None:
        r["status"] = "INCOMPLETE"; r["missing"] = "gate_plausible_10_15yr (judgment + evidence)"; return r
    if plaus is False:
        r["status"] = "GATE_FAIL"
        why = c.get("gate_evidence", "future cap implausible vs TAM")
        # escape hatch: quality compounder
        if c.get("quality_compounder"):
            r["routing"] = "Quality Compounder"; r["escape_hatch_used"] = True
            r["line"] = f"{c['ticker']} — Gate fails ({caph}x20={tgth}). {why}. -> Quality Compounder (escape hatch), NOT Top 20."
        else:
            r["line"] = f"{c['ticker']} — Gate fails. {caph}x20={tgth}. {why}."
        return r

    # Stage 2 — mechanical vetoes
    if not (set(c["thesis_pillars_touched"]) & ACTIVE_PILLARS):
        r["status"] = "WRONG_PILLAR"; r["line"] = f"{c['ticker']} — Wrong pillar. Killed."; return r
    pol = c.get("policy_dependency_score")
    hard_cap_top20 = False
    if pol is not None and pol <= 2.5:
        hard_cap_top20 = True
        r["flags"].append(f"Policy dependency {pol} <=2.5 (single reversible EO) — HARD-CAP: cannot be Top-20")
    insider = c.get("insider_activity", {}) or {}
    forced_adv = None
    if insider.get("cluster_sell"):
        forced_adv = 2.0
        r["flags"].append("Insider cluster-selling — Adversarial forced <=2.0")

    # Stage 4 — subjective V/A/C/S (NEVER invented)
    vacs_in = c.get("vacs", {}) or {}
    scores = {}
    for dim in ("V", "A", "C", "S"):
        v = vacs_in.get(dim)
        ev = vacs_in.get(dim + "_evidence", "")
        if v is None or ev == "":
            r["status"] = "INCOMPLETE"
            r["missing"] = f"VACS {dim} score+evidence (engine never fabricates subjective scores)"
            return r
        scores[dim] = score_obj(float(v), c.get("vacs_source", "LLM_PROPOSED"), ev)
    if forced_adv is not None and scores["A"]["value"] > forced_adv:
        scores["A"]["value"] = forced_adv
        scores["A"]["evidence"] += " | capped by insider cluster-sell veto"

    # Stage 5 — composite + classification (deterministic)
    comp = round(sum(scores[d]["value"] for d in scores) / 4, 2)
    label = classify(comp)
    if hard_cap_top20 and comp >= 4.0:
        label = "Tactical/Speculative (Top-20 barred: policy hard-cap)"
    if comp > BWXT_BENCHMARK:
        r["flags"].append(f"PROPOSED {comp} EXCEEDS BWXT benchmark {BWXT_BENCHMARK} — extraordinary justification required")
    r.update(status="SCORED", scores={d: scores[d]["value"] for d in scores},
             composite=comp, classification=label)
    return r


def render(r: dict) -> str:
    t = r["ticker"]
    if r["status"] == "ETF_EXPRESSION": return r["line"]
    if r["status"] == "INCOMPLETE":     return f"{t} — INCOMPLETE: missing {r['missing']}"
    if r["status"] in ("GATE_FAIL", "WRONG_PILLAR"): return r["line"]
    s = r["scores"]
    out = [f"{t} — VACS",
           f"  Gate: {r['gate_math']} — PASSES",
           f"  V {s['V']} | A {s['A']} | C {s['C']} | S {s['S']}  ->  VACS {r['composite']} — {r['classification']}"]
    for f in r.get("flags", []):
        out.append(f"  ⚠ {f}")
    return "\n".join(out)


def main() -> None:
    if not CAND.exists():
        sys.exit(f"Missing {CAND}")
    cands = yaml.safe_load(CAND.read_text()).get("candidates", [])
    results = [evaluate(c) for c in cands]
    print(f"\n{'='*60}\n  VACS ENGINE — {len([r for r in results if r['status']=='SCORED'])} scored / {len(results)} candidates\n{'='*60}\n")
    demotions = 0
    for r in results:
        print(render(r)); print()
        if r["status"] in ("GATE_FAIL", "WRONG_PILLAR") or \
           (r["status"] == "SCORED" and r["composite"] < 3.5):
            demotions += 1
    # confirmation-trap monitor
    scored = [r for r in results if r["status"] == "SCORED"]
    if scored and demotions == 0:
        print("⚠ BATCH WARNING: zero demotions — confirmation-trap risk. Re-hunt disconfirming evidence.")
    print("\nPROPOSED until you ratify. Not financial advice.")


if __name__ == "__main__":
    main()
