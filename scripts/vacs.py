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

# Spec's formal rejections register — KILL on sight unless force_rescore
# (a documented material change). Prevents re-researching dead names.
REJECTIONS = {"ASML", "PLTR", "MOD", "VRT", "OKLO", "AVAV", "KTOS", "CCJ",
              "NXE", "IVN", "JOBY", "ACHR", "NNOX", "BE"}

# Statement-verified holdings (holdings_vs_candidates_rule). Everything else
# scored is a CANDIDATE, never a holding, until it's on a brokerage statement.
# Tickers live in a GITIGNORED local file (data/holdings.local.yml) so they
# never land in a public repo; falls back to empty (candidates-only) if absent.
def _load_holdings():
    f = ROOT / "data" / "holdings.local.yml"
    if f.exists():
        try:
            return set((yaml.safe_load(f.read_text()) or {}).get("holdings", []))
        except Exception:
            return set()
    return set()


HOLDINGS = _load_holdings()


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

    # Rejections register — don't re-research dead names (unless material change)
    if c["ticker"] in REJECTIONS and not c.get("force_rescore"):
        r["status"] = "ALREADY_REJECTED"
        r["line"] = f"{c['ticker']} — Already rejected (register). Needs documented material change to re-run."
        return r

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


def tag(t):
    return " [HELD]" if t in HOLDINGS else ""


def main() -> None:
    if not CAND.exists():
        sys.exit(f"Missing {CAND}")
    cands = yaml.safe_load(CAND.read_text()).get("candidates", [])
    results = [evaluate(c) for c in cands]
    scored = sorted([r for r in results if r["status"] == "SCORED"],
                    key=lambda x: -x["composite"])
    quality = [r for r in results if r.get("escape_hatch_used")]
    killed = [r for r in results if r["status"] in
              ("GATE_FAIL", "WRONG_PILLAR", "ALREADY_REJECTED", "ETF_EXPRESSION")
              and not r.get("escape_hatch_used")]

    print(f"\n{'='*66}\n  VACS RANKED BOARD — {len(scored)} contenders / {len(results)} screened\n{'='*66}")

    # --- THE RANKED TOP-20 CONTENDERS ---
    print("\n  RANK  TICKER        VACS   CLASSIFICATION")
    print("  " + "-" * 60)
    for i, r in enumerate(scored, 1):
        top20 = r["composite"] >= 4.0 and "barred" not in r["classification"]
        mark = "★" if top20 else " "
        print(f"  {mark}{i:<4}{r['ticker']+tag(r['ticker']):<14}{r['composite']:<6.2f} {r['classification']}")
        for f in r.get("flags", []):
            if "forced" in f or "HARD-CAP" in f or "EXCEEDS" in f:
                print(f"        ⚠ {f}")

    # --- QUALITY COMPOUNDERS (gate-failed, kept via escape hatch) ---
    if quality:
        print("\n  QUALITY COMPOUNDERS — too big to 20x; NOT Top-20 asymmetric bets")
        print("  " + "-" * 60)
        for r in quality:
            print(f"     {r['ticker']+tag(r['ticker']):<14}{r['gate_math']}  (escape hatch)")

    # --- KILLED ---
    if killed:
        print("\n  KILLED / SCREENED OUT")
        print("  " + "-" * 60)
        for r in killed:
            reason = {"GATE_FAIL": "gate fail", "WRONG_PILLAR": "wrong pillar",
                      "ALREADY_REJECTED": "already rejected", "ETF_EXPRESSION": "ETF"}[r["status"]]
            print(f"     {r['ticker']+tag(r['ticker']):<14}{reason}")

    # --- confirmation-trap monitor ---
    demotions = len([r for r in scored if r["composite"] < 3.5]) + len(killed) + len(quality)
    print("\n  " + "-" * 60)
    if scored and demotions == 0:
        print("  ⚠ ZERO demotions — confirmation-trap risk. Re-hunt disconfirming evidence.")
    else:
        print(f"  ✓ {demotions} demotions/kills this cycle (spec wants >=1).")
    confirmed = [r for r in scored if r["composite"] >= 4.0 and "barred" not in r["classification"]]
    print(f"  ★ Top-20 Confirmed: {len(confirmed)}  ({', '.join(r['ticker'] for r in confirmed) or 'none yet'})")
    print("\n  All scores PROPOSED until Shawn ratifies. [HELD]=on a statement. Not advice.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
