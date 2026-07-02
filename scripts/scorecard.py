#!/usr/bin/env python3
"""
scorecard.py — does Shawn actually have edge, or is it the regime?

Reads data/decision_journal.yml and answers the question STATISTICALLY,
honestly, with the one correction most people skip: correlated calls are
NOT independent evidence. Three space stocks ripping in a space-stock bull
market is ~one bet, not three. So we compute BOTH:

  1. Naive posterior  — treat every graded call as independent (flattering)
  2. Clustered posterior — collapse each independence-cluster to ONE outcome
                           (honest; this is what actually matters)

Bayesian model: each "does Shawn's divergent call beat the cautious one?"
is Bernoulli(p). Prior Beta(1,1) (uniform — no assumption of edge). Posterior
Beta(1+wins, 1+losses). We report the posterior mean and P(p > 0.5) — the
probability he has REAL edge, not a coin flip.

This is the loop the conversation kept circling: stop arguing, start scoring.
Re-run as calls resolve; the answer sharpens every quarter.
"""
from __future__ import annotations
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
JOURNAL = ROOT / "data" / "decision_journal.yml"


def beta_mean(a, b):
    return a / (a + b)


def prob_p_gt_half(a, b, steps=20000):
    """P(p > 0.5) under Beta(a,b) via simple numerical integration."""
    # integrate the Beta pdf from 0.5 to 1 (unnormalized) / full integral
    import math
    logB = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    def pdf(x):
        if x <= 0 or x >= 1:
            return 0.0
        return math.exp((a - 1) * math.log(x) + (b - 1) * math.log(1 - x) - logB)
    # trapezoid over [0,1], track tail [0.5,1]
    full = tail = 0.0
    prev_x = 0.0
    prev_f = 0.0
    for i in range(1, steps + 1):
        x = i / steps
        f = pdf(x)
        area = (prev_f + f) / 2 * (1 / steps)
        full += area
        if x > 0.5:
            tail += area
        prev_x, prev_f = x, f
    return tail / full if full else float("nan")


def main() -> None:
    data = yaml.safe_load(JOURNAL.read_text())
    decs = data.get("decisions", [])
    graded = [d for d in decs if d.get("winner") in ("shawn", "cautious", "tie")]
    openc = [d for d in decs if d.get("winner") == "open"]

    # --- Naive: each graded call independent (ties = half) ---
    wins = sum(1 for d in graded if d["winner"] == "shawn")
    losses = sum(1 for d in graded if d["winner"] == "cautious")
    ties = sum(1 for d in graded if d["winner"] == "tie")
    n_eff_naive_w = wins + 0.5 * ties
    n_eff_naive_l = losses + 0.5 * ties
    a_n, b_n = 1 + n_eff_naive_w, 1 + n_eff_naive_l

    # --- Clustered: collapse each cluster to ONE net outcome ---
    clusters: dict[str, list] = {}
    for d in graded:
        clusters.setdefault(d["cluster"], []).append(d["winner"])
    cl_wins = cl_losses = cl_ties = 0.0
    cluster_verdict = {}
    for cl, outs in clusters.items():
        s = outs.count("shawn"); c = outs.count("cautious")
        if s > c:
            cl_wins += 1; cluster_verdict[cl] = "shawn"
        elif c > s:
            cl_losses += 1; cluster_verdict[cl] = "cautious"
        else:
            cl_ties += 1; cluster_verdict[cl] = "tie"
    a_c = 1 + cl_wins + 0.5 * cl_ties
    b_c = 1 + cl_losses + 0.5 * cl_ties

    print(f"\n{'='*64}\n  SHAWN vs THE CAUTIOUS CALL — does the edge exist?\n{'='*64}")
    print(f"\nGraded divergent calls: {len(graded)}   (open, awaiting outcome: {len(openc)})")
    print(f"  Raw record: {wins} Shawn / {losses} cautious / {ties} tie")

    print(f"\n--- (1) NAIVE model — every call counts (flattering) ---")
    print(f"  Posterior Beta({a_n:.1f}, {b_n:.1f})")
    print(f"  P(Shawn's call > coin flip) = {prob_p_gt_half(a_n,b_n)*100:.0f}%")
    print(f"  Best estimate of his hit rate = {beta_mean(a_n,b_n)*100:.0f}%")

    print(f"\n--- (2) CLUSTERED model — correlated calls = ONE bet (honest) ---")
    for cl, v in cluster_verdict.items():
        print(f"     {cl:<18} -> {v}")
    print(f"  Independent clusters: {len(clusters)}  ({cl_wins:.0f} win / {cl_losses:.0f} loss / {cl_ties:.0f} tie)")
    print(f"  Posterior Beta({a_c:.1f}, {b_c:.1f})")
    print(f"  P(Shawn has real edge) = {prob_p_gt_half(a_c,b_c)*100:.0f}%")
    print(f"  Best estimate of edge hit rate = {beta_mean(a_c,b_c)*100:.0f}%")

    print(f"\n--- VERDICT ---")
    pc = prob_p_gt_half(a_c, b_c)
    if pc > 0.95:
        v = "PROVEN edge (clustered P>95%)."
    elif pc > 0.8:
        v = "PROBABLE edge — strong but NOT yet statistically proven."
    elif pc > 0.6:
        v = "SUGGESTIVE — leans toward edge; too few independent calls to trust."
    else:
        v = "UNPROVEN — indistinguishable from luck so far."
    print(f"  {v}")
    print(f"  Independent bets so far: ~{len(clusters)}. Need ~15-20 graded,")
    print(f"  UNCORRELATED calls across DIFFERENT regimes to reach proof.")
    print(f"  Every win above shares one tailwind (2026 frontier-tech bull),")
    print(f"  so even the clustered number is optimistic until a down-regime test.\n")


if __name__ == "__main__":
    main()
