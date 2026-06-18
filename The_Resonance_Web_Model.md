# The Resonance Web Model
### A Unified, Academic Reconstruction of Shawn's Causal-Cascade Framework
**From the 2024 "interest-rate cascade" intuition → the 2025 Spider-Web metaphor → the 2026 Resonance Web**

---

*Compiled: 2026-06-17. Author of the underlying work: Shawn (shawn@nikaaihome.net). This document is a faithful synthesis assembled from the canonical project memories in the user's Google Drive (see §11, Source Register). Direct quotations of Shawn's own words are marked as such; everything else is reconstruction and connective exposition. Where the live engineering state is summarized, the **honest validation status** is preserved verbatim in spirit — the model is a disciplined instrument, not yet a proven predictor.*

---

## Abstract

This document consolidates a single line of intellectual work that the author began as an informal thought experiment in ChatGPT in early 2024 and has since developed into a structured, partially-operational forecasting and decision system. The founding intuition was simple and powerful: **the world is not a set of independent levers but a connected web, and a disturbance at one node propagates outward in second-, third-, and higher-order effects across society.** The canonical illustration was monetary: a change in **interest rates** alters **borrowing power**, which constrains the financing of **large/expensive projects**, which **delays or cancels** them, which **cascades** into employment, supply chains, regional economies, and sentiment.

Over two years this intuition was formalized in three named stages — **Cognitive Radar** (Apr 2025), the **Spider Web** metaphor (May 2025), and the **Resonance Web Model** (2026) — and equipped with an explicit architecture (input "threads"), a borrowed-methodology layer (the "Spider's Brain"), and a quantitative decision core. This paper presents the model's theory, structure, mathematics, empirical status, and governance discipline as a single coherent whole.

---

## 1. Introduction: the problem the model addresses

Most everyday reasoning about cause and effect is **linear and first-order**: *X causes Y.* Raise rates, cool inflation. Linear reasoning fails in complex social and economic systems because effects do not stop at Y. They continue: Y reshapes Z, Z feeds back on X, and the most consequential outcomes are often the **indirect** ones that no single actor intended and few anticipated.

The author's foundational illustration (as he recalls and described it in 2026):

> A rise in **interest rates** reduces **borrowing power**. With borrowing constrained, **expensive projects** — construction, infrastructure, capital expansion — can no longer secure financing. Those projects are **delayed or shelved**. That delay **cascades**: contractors lose work, suppliers lose orders, hiring freezes, dependent businesses contract, regional tax bases soften, and confidence falls — which feeds back into still weaker investment. A single first-order move (the rate change) thus produces a **fan of second- and third-order effects that ripple across society.**

> **Provenance caveat.** This interest-rate cascade is the author's own **recalled** framing of the idea's seed. It was **not located verbatim** in the recovered 2025-05-08 origin thread, where the model is articulated instead as *vibration/convergence across threads* in an investing context (§3). The cascade articulation may live in an earlier (2024) or later export not yet retrieved. It is kept here as a faithful **illustration of the model's logic** — higher-order effects propagating through a connected system — not as a sourced quotation.

The model's purpose is to make that fan of consequences **explicit, traceable, and — eventually — testable**: to see one or two steps further down the causal chain than ordinary reasoning does, and to convert that foresight into a disciplined judgment about whether to **act, watch, investigate, or wait.**

---

## 2. Provenance and lineage

The model is not a single invention but an **evolving lineage**. Preserving the lineage matters, because the system's own governance rules (see §9) require future work to *extend the canonical form rather than rebuild it from scratch.*

| Stage | Date | What it was |
|---|---|---|
| **Interest-rate cascade intuition** | recalled as early | The seed idea as the author describes it: society as an interconnected web; shocks propagate in higher-order ripples; interest-rate→borrowing→stalled-projects as the worked example. *Author's recollection — not found verbatim in the recovered 2025-05-08 origin thread (see §1 caveat).* |
| **Cognitive Radar** | 2025 | The "Cognitive Radar" label is crystallized in the **title** of the 2025-05-08 thread (*"Cognitive Radar: Instinct-Fused Stock Rotation Engine"*); canon dates a Cognitive-Radar precursor to ~Apr 2025. Artifact: *Cognitive Radar Daily Watchlist Scanner* (PDF, Oct 2025). |
| **Spider Web metaphor** | **2025-05-08** | The unifying image, **verbatim-sourced** from the thread *"Cognitive Radar Framework Prep"* (273 msgs), drafted with the AI persona **Astra**: you are the spider; feeders/threads are input domains; a vibration on any thread is a signal; convergence triggers action (§3). |
| **Resonance Web Model** | 2026 | The matured, canonical form. Formal signal-sorting (six dispositions), a quantitative cascade/distortion math core (R/D/L/C/A/P), phased backtests, and a "dashboard-ready" engineering state (Phase 5.3). |

> **Note on parallel artifacts.** In June 2026 a working "Spider Web" macro radar (`nika/spider_web/`) was built as a market-data sensor. It was subsequently **reconciled as a subordinate component** of the canonical Resonance Web — explicitly *not* a rival framework. This document treats the **Resonance Web as canonical** and the Spider-Web radar as one instrument under it.

---

## 3. The founding metaphor (Shawn's own words, 2025-05-08)

The model's central image is recorded **verbatim** in the ChatGPT thread **"Cognitive Radar Framework Prep"** (2025-05-08, 273 messages) — the dated origin of the spider-web theory, developed with the AI partner Shawn named **"Astra."** After rejecting the AI's earlier flowchart attempts, Shawn dictated the model in his own words (informal phrasing preserved):

> *"…it's like a spider web, right? Your decision, anyone, there could be main feeders, right? So that's like major news event driven things, um, it could be sentiment building, uh, you could have… catalyst events, and they all come together like a web, and like a spider does, right? It's got this big web of things going out there. When something hits somewhere on its web, it could be news cycle, it could be something else that triggers it in action, and you have a predefined set of things that you'll do. … So, just like a fly would hit, and the spider goes to it, it just feels that one string going into the web could be that information that we're tuning to. … you get my image around the web. I think that's actually a really good one."*

Just before it, he introduced the intake side of the model — the **"feeders"**:

> *"there should be information feeders. So where do you get the information from? You have to think of it as how you take in information, right? … You keep sequences, sentences, and you take the past data to predict the future. Then you normalize the data."*

And he named the model's purpose — not prediction, but **getting there first**:

> *"this isn't me playing like predicting the future it's about me getting in the head between you know before most of the retail investors get in. … I'll be lucky if I catch one or two waves in my whole career before they happen."*

Astra (the AI) then crystallized the structure back to him — the formulation the whole system still rests on:

> *"You're constructing a **sensory network** — like a **spider's web of signal threads** … You're not reacting to* data *— you're reacting to* vibration*. … **You = the spider / The web = your interconnected data environment / Each thread = a different input domain.**"*

— and gave it its first project name, ***"The Spider Web Signal Engine v0.1."*** The chat's own title, *"Cognitive Radar: Instinct-Fused Stock Rotation Engine,"* is where the **Cognitive Radar** label enters the lineage.

The metaphor compresses the entire architecture into one picture:

- **You = the spider.** The decision-maker sits at the center.
- **Feeders / threads = input domains.** Channels through which information arrives (news, sentiment, catalysts, institutional flow, …).
- **Vibration = a signal.** An event "hits" a thread.
- **Convergence = the action trigger.** A single vibration is noise; *simultaneous* vibration across several threads is what the spider moves on — against a **predefined set of responses**.

The design goal that follows: be a **mid-curve signal interceptor** — ahead of the retail crowd, just behind smart money — a **pressure-convergence detector, not a point-forecaster**: to *feel the string before the fly even knows it's caught.*

> **Sourcing note.** Every quote in this section is Shawn's or Astra's verbatim text from the 2025-05-08 origin thread (recovered from the raw ChatGPT export `2025-05-08_threads.json`). In that origin conversation the model is framed as **vibration/convergence across threads in an investing context** — see §1 for how this relates to the interest-rate "cascade" framing.

---

## 4. Theoretical framing

The model is an applied synthesis of several established traditions in systems and forecasting science. It is worth naming them, because the framework's credibility rests on standing on this prior art rather than reinventing it.

- **Systems thinking & feedback** — the world as stocks, flows, and feedback loops; consequences loop back on their causes. The interest-rate cascade is a textbook reinforcing/balancing-loop story.
- **Higher-order effects** — the explicit discipline of asking "and then what?" repeatedly: first-order (rates ↑), second-order (financing ↓), third-order (projects shelved), fourth-order (employment/sentiment), and so on.
- **Sectoral interdependence** — borrowing from Godley-style sectoral balances and macro "plumbing" (liquidity, repo, offshore dollar) to track how pressure in one sector must appear somewhere else.
- **Probabilistic, calibrated forecasting** — rather than single predictions, the model runs *distributions* and scores itself with strictly-proper rules (see §6's "Spider's Brain").

The conceptual claim is modest and honest: **mapping the web does not predict the future; it widens the field of view and disciplines the response.**

---

## 5. Architecture: the fourteen threads

The Spider-Web layer operationalizes "the web" as **14 input threads**. The first nine are Shawn's original design (kept verbatim); five were added in a 2026 research pass.

**Shawn's original nine:**
1. **Event Catalysts** — regulatory/filing feeds (SEDAR+, EDGAR, NRC, FCC).
2. **Sentiment** — crowd mood (via the `last30days` plugin).
3. **Institutional Movement** — 13F filings, insider buying, BIS banking statistics; the spine for Godley sectoral balances.
4. **Macro Themes** — long-cycle (Dalio) plus monetary "plumbing" (Alden): fiscal-dominance index, liquidity state.
5. **Geopolitical Tensions** — structural constraints (Zeihan) plus the Caldara–Iacoviello Geopolitical Risk index.
6. **Manufacturing / Buildouts** — energy-shock backbone (Hamilton: 10 of 11 post-WWII recessions preceded by an oil spike).
7. **Retail Herding** — crowd-positioning (`last30days`, Google Trends, AAII).
8. **Long-Term Sector Turns** — the "K-Wave 6" pillars: Nuclear, Space, Defense, AI Infrastructure, Critical Minerals, Robotics.
9. **Volatility Echoes** — the "Five Gauges": WTI, 10Y yield, DXY, Gold, HY OAS, VIX.

**Added in the 2026 v0.2 pass:**
10. **Plumbing / On-chain** — Tether issuance, BTC basis, repo, CFTC COT, central-bank swap lines (Snider/Wang/Pozsar territory).
11. **Ground Truth** — physical-economy proxies that bypass official statistics (Kpler/Vortexa shipping AIS, NASA VIIRS night-lights, Li Keqiang proxy).
12. **Central-Bank Linguistics** — FOMC hawkishness NLP (Hansen–Lozano), policy-uncertainty indices, daily GPR.
13. **Tail Surveillance** — exogenous-shock sensors (Biobot wastewater, CISA KEV cyber, RAPID AMOC, NOAA space weather).
14. **AI-as-Macro** — AI buildout treated as a *regime* variable, not a sector story (hyperscaler capex, datacenter revenue, EIA power-demand outlook).

Each asset/theme receives a **Tension Index** score (0–10) across the threads. **Convergence of high tension across multiple threads** — not any single reading — is what fires a reflex/alert. (First live run, 2026-06-16: Gold registered 6.9/10 tension, z = +2.76σ, with no multi-thread convergence — "the web is calm.")

---

## 6. The "Spider's Brain": methodology layer

Above the raw threads sits a methodology layer that imports rigor from non-financial forecasting disciplines. This is what separates the model from a dashboard of indicators.

- **Tension Index** (Shawn, 2025) — the per-asset, cross-thread 0–10 convergence score.
- **Ensemble forecasting** (ECMWF) — run multiple causal frameworks in parallel; the *distribution* of their outputs is the forecast.
- **CRPS scoring** (Hersbach, 2000) — a strictly-proper score that cannot be gamed by hedging.
- **Reliability diagrams** (Hamill, 2001) — calibration checks: do "70%" claims happen 70% of the time?
- **Analysis of Competing Hypotheses** (Heuer/CIA) — select the *least-inconsistent* hypothesis, not the most-consistent one.
- **Indications & Warning** (military doctrine) — separate *indicators*, *warnings*, and *predictions*.
- **Pre-mortem** (Klein) — every high-confidence call must state its explicit failure mode in advance.
- **Multi-model superensemble** (Krishnamurti, 1999) — weight each analyst/source by realized hit-rate, not reach.
- **Lead-time degradation curve** (ECMWF) — publish the model's own CRPS as a function of lead time; be honest about the horizon over which it is actually useful.

---

## 7. The Resonance Web: from sensing to deciding

The Spider Web *senses*. The **Resonance Web** *decides*. It is "Shawn's signal-sorting framework": it takes one live signal — an event, an article, a market move, a legal or medical deadline, a family issue, an AI pattern — and routes it into exactly one of six dispositions, always ending in **one concrete action or a dated no-action**:

> **act · act-watch · watch · investigate · pause · ignore**

This is the practical payoff of the whole lineage. The interest-rate cascade taught the author to *see* the ripples; the Resonance Web forces a *response discipline* so that seeing more does not collapse into endless analysis.

### 7.1 The mathematical core

A shared engine (`resonance_core.py`, config `resonance_weights_v0.4.json`) scores each signal on ten formal components:

- **R — Resonance / reach** (how widely the signal propagates across the web)
- **D — Distortion** (how much noise, hype, or misinformation surrounds it)
- **L — Loop** (whether it feeds a self-reinforcing cycle)
- **C — Confidence**
- **A — Actionability**
- **P — Priority**
- plus **reversibility, harm, source-adjustment,** and an overall **confidence** penalty.

A relational **matrix** of domain-to-domain edges models cascades (e.g. the 8×8/56-edge "lane matrix"; the Phase-3 public-event atlas uses a 15×15 / 210-edge matrix with damping). This matrix is the formal descendant of the interest-rate cascade: it encodes *which domains push on which others, and how hard.*

### 7.2 Phase history (engineering)

The model has been built and stress-tested in disciplined phases, each reviewed adversarially (the "Vale + Auditor" review):

- **Phase 1 — Backtest spine.** 10 cases, 11 features, ordered rule set. Reached 10/10 *in-sample self-consistency* after one principled rule fix.
- **Phase 2 — Cascade layer.** 8×8 lane matrix; 9/10 in-sample. Review found the cascade was *decorative* (it didn't actually drive the label) and the matrix saturated.
- **Phase 3 — Global Cascade Atlas.** 15-domain × 15 matrix (210 edges); 30 real public events (COVID, Ukraine, SVB, ChatGPT launch, CrowdStrike, etc.) scored blind by 11 parallel agents. 18/30 = 60% in-sample vs ~53% floor.
- **Phase 4 — Math Core & Calibration.** Formal engine + frozen priors + train/holdout split. Train 57%, holdout 67% — *statistically insignificant* over the majority-class baseline.
- **Phase 4.1 — No-Hindsight Repair.** Fixed the *testing method*: separated teaching mode from prospective mode, marked outcome-features "unknown" instead of guessing them, and registered live prospective signals.
- **Phase 5.3 — Canonical, "dashboard-ready."** Four active prospective signals (GPU capex, commercial real estate, cyber, housing) source-verified and passing the current-source gate.

---

## 8. Empirical status — stated honestly

A defining feature of this work is its refusal to overclaim. The canonical status, preserved faithfully:

- The backtests demonstrate **in-sample self-consistency, not validation.** Features, rules, and labels were author-set in hindsight.
- Against simple baselines (e.g. a one-feature source-quality rule), the model **ties, with p ≈ 0.43 — not significant.**
- There are **zero reviewed prospective cases**, so there is **no demonstrated forecast skill yet.**
- A recurring finding across phases: **the cascade matrix never actually drove the decision**, and backtests measured *hindsight, not foresight.*

The honest verdict: this is a **rigorously-built instrument with a genuine validation gap.** Its current proven value is as a **teaching tool and a ranking lens** (cascade / distortion / actionability rankings), and as a **falsifiable market-tension log** — not as a demonstrated oracle.

---

## 9. Governance and discipline

The project carries its own meta-rules, learned the hard way:

- **Elaboration-over-action trap.** The dominant risk is building ever-more structure instead of using the instrument. Rule: *do not wire all 14 threads before going live; add one thread per week; the radar is a tool, not the work.*
- **Read the canon first.** Before building in any domain, read the canonical `CURRENT_STATE` document and search prior work — memory-index files go stale and cause parallel rebuilds. (The June 2026 Spider-Web radar was the *6th* parallel rebuild of the same concept; it had to be reconciled as subordinate.)
- **Single canonical artifact.** Extend or use prior work; never spawn a rival. The decision engine is `resonance_core.py`; everything else feeds it.

---

## 10. Current state and next action (as of 2026-06-17)

The canonical source of truth is `shawn-core/docs/RESONANCE_CURRENT_STATE.md` ("Read this FIRST… Do not rebuild completed phases"). Its state as of this writing:

- **Status:** Resonance Web at **Phase 5.3, `dashboard_ready: yes`.** Phases **4, 4.1, 5, 5.1, 5.2, 5.3** are marked **`do_not_repeat`.** Phase 6 (dashboard) is unlocked but **optional**.
- **Live prospective signals:** four — **PS-06 (GPU capex), PS-07 (commercial real estate), PS-08 (cyber), PS-09 (housing)** — are **source-verified and passed** the current-source gate. The earlier placeholders **PS-01…05 expired.**
- **Honest status, unchanged:** **not a proven predictor.** Zero reviewed cases; in-sample it only **ties a one-feature source-quality baseline (p = 0.43)**; forecast value is **untested until the review.**
- **`next_single_action`: nothing is required until 2026-08-15** — then run `review_matured_signals.py` + `compare_to_baselines.py` (the no-hindsight registry review follows on 2026-09-14).
- **Decision criterion:** *if the Resonance Web does not beat baselines on blind cases, keep the cascade/distortion rankings as a teaching tool and stop calling it a predictor.*
- **Engineering housekeeping:** five feature branches (`feature/resonance-web-phase-1` … `phase-4-1`) remain **unmerged and unpushed**, pending your go-ahead.

---

## 11. The 2026 instrument ecosystem {#ecosystem}

By mid-2026 the web model is not a lone artifact but the **apex layer of a family of sibling instruments**, each occupying a different altitude of the same "sense → decide" pipeline. The Resonance Web is canonical; the others are subordinate sensors and validators that feed or test it.

| Instrument | Altitude / role | Relationship to the web model | Status (2026-06-17) |
|---|---|---|---|
| **Resonance Web** | Decision engine (signal → disposition) | **Canonical.** The matured framework. | Phase 5.3, dashboard-ready |
| **Spider Web radar** | Macro market-data sensor (14 threads) | **Subordinate** sensor under Resonance; produces `tension_index.csv` falsifiable market calls. *Not* a rival framework. | 4 threads live; reconciled 2026-06-17 |
| **Market Radar** | Ticker-level retail-sentiment + catalyst dashboard | One altitude **below** Spider Web; scored call-log on `last30days`. | Live |
| **Quantum Radar** | Quantum-investing deep-dive (12 names) | Sibling vertical radar. | Built 2026-06-14; **both schedules disabled 2026-06-16** |
| **Pulse Engine** | Self-curating multi-source watchlist (~109 seed names) | Upstream discovery feed. | Iteration 0 working 2026-06-16 |
| **Predictor Scoreboard** | External-forecaster validation | The **honesty counterweight**: scores real pundits so the model is benchmarked against verified human skill. | Methodology validated 2026-06-16 |

**The Predictor Scoreboard deserves special note** because it embodies the model's validation ethic. Run over **242 dated calls**, with a deliberately strict methodology (90-day horizon, market-adjusted vs SPY, signed, equal-weighted, half-split stability test, and — the subtle catch — benchmarked against the **+7.13% "mention-universe" selection-bias floor**, not just SPY), it found exactly **one** verified human predictor: **Stan Wong (Stockchase)** — 123 calls, **69.1% hit rate at 90 days, p < 0.0005**, stable across both halves of the window, with edge concentrated in short discipline. One aggregator panel **failed** (49.6%, a coin-flip whose apparent edge was a regime flip — "that flip *is* the noise signature"). This is the same standard the Resonance Web holds itself to in §8: *beat the right baseline on out-of-sample data, or don't claim skill.*

---

## 12. Code cross-reference — doc ↔ code linkage {#code-linkage}

This section makes the document **linkable to the codebase in both directions.** The canonical engine lives in the `shawn-core` working tree (and operational scripts under `nika/`); it is not yet pushed to GitHub, so the references below are **stable logical paths** rather than URLs. Two linking conventions are defined:

- **Doc → code:** the table maps each model concept (and its section anchor) to the concrete file, script, skill, config, or branch that implements it.
- **Code → doc:** each major section above carries a stable anchor (e.g. `#ecosystem`, `#code-linkage`); source files can reference them as `The_Resonance_Web_Model.md#<anchor>` in comments or docstrings. Recommended anchors to cite from code: `#code-linkage`, `#ecosystem`, plus the section numbers in §5 (threads), §7.1 (math core), §7.2 (phases), §8 (status), §10 (current state).

### 12.1 Canonical engine & state

| Concept (doc) | Code artifact |
|---|---|
| Source of truth / current state (§10) | `shawn-core/docs/RESONANCE_CURRENT_STATE.md` |
| Math core — R/D/L/C/A/P (§7.1) | `shawn-core/scripts/resonance_core.py` |
| Frozen priors + calibrated thresholds | `shawn-core/configs/resonance_weights_v0.4.json` |
| Signal-sorting skill (six dispositions, §7) | `~/.claude/skills/resonance-web-map/` (source in `shawn-core`) |
| Live prospective signal scoring (§10) | `shawn-core/scripts/score_live_signal.py PS-06` |
| Scheduled review (2026-08-15) | `shawn-core/scripts/review_matured_signals.py` + `compare_to_baselines.py` |

### 12.2 Phase backtests → branches

| Phase (doc §7.2) | Branch / commit | Run command |
|---|---|---|
| Phase 1 — backtest spine | `feature/resonance-web-phase-1` (a67e449) | `python shawn-core/scripts/run_resonance_backtest.py` |
| Phase 2 — cascade layer | `feature/resonance-web-phase-2` (ed45908) | `python shawn-core/scripts/run_resonance_cascade.py` |
| Phase 3 — global cascade atlas | `feature/resonance-web-phase-3-global-atlas` (7021ea3) | `python shawn-core/scripts/run_global_event_backtest.py` |
| Phase 4 — math core & calibration | `feature/resonance-web-phase-4-math-core` (f7e4396) | `python shawn-core/scripts/run_resonance_holdout_eval.py` |
| Phase 4.1 — no-hindsight repair | `feature/resonance-web-phase-4-1-no-hindsight-repair` (c140414) | `python shawn-core/scripts/score_live_signal.py PS-06` |

*(All five branches are currently unmerged and unpushed — see §10.)*

### 12.3 Spider Web radar (subordinate sensor, §11)

| Concept | Code artifact |
|---|---|
| Radar home | `nika/spider_web/` |
| Build spec / thread sequence | `nika/spider_web/SPIDER_WEB.md` |
| Falsifiable market-call log | `nika/spider_web/tension_index.csv` |
| Daily briefing surface | `nika/spider_web/briefings/latest.md` |
| Schedules | `SpiderWebWeekly` (Sun 18:00) + `SpiderWebBreakIn` (daily 08:30) |
| Data connectors | FRED CSV, Yahoo Finance, `last30days` plugin, EIA |

### 12.4 Sibling instruments (§11)

| Instrument | Code location |
|---|---|
| Market Radar | `C:\Users\spias\market_radar\` (scored `call_log.csv`) |
| Quantum Radar | `nika/quantum_radar/reports/latest.html` (schedules `QuantumRadarWeekly` / `QuantumRadarBreakIn`, disabled) |
| Pulse Engine | `C:\Users\spias\pulse_engine\` |
| Predictor Scoreboard | `C:\Users\spias\scoreboard_backtest\` (`02_score.py`, `03_diagnose.py`, `scoreboard_results.csv`) |

### 12.5 Origin material (provenance, §2–§3)

| Item | Location |
|---|---|
| Per-conversation ChatGPT archive (1,101 files, Nov 2023 → Oct 2025) | `nika/index/chatgpt_synthesized/` (`_INDEX.md` for chronological list) |
| May-2025 spider-web capture | `nika/index/chatgpt_synthesized/2025-05-08_681d14db_cognitive_radar_framework_prep.md` |
| Cognitive Radar artifact (Apr/Oct 2025) | `Cognitive_Radar_Daily_Watchlist_Scanner.pdf` (Drive) |
| Unified local search (5,474+ docs) | `python nika/index/query.py "term"` |

> **To wire this up concretely:** once `shawn-core` (and/or `nika`) is pushed to GitHub, the logical paths in §12.1–§12.5 become clickable links by prefixing the repo blob URL, and code files can back-link to this document's anchors (§12 intro). If you want, I can also emit a machine-readable `resonance_web.linkmap.json` mapping each anchor ↔ code path so tooling can resolve the cross-links automatically.

---

## 13. Glossary

- **Thread** — one input domain feeding the web (14 total).
- **Vibration / Signal** — an event arriving on a thread.
- **Tension Index** — 0–10 per-asset score across threads; convergence triggers a reflex.
- **Convergence** — simultaneous high tension on multiple threads; the action trigger.
- **Resonance (R)** — how far a signal propagates through the web.
- **Distortion (D)** — surrounding noise/hype/misinformation.
- **Loop (L)** — self-reinforcing feedback.
- **Disposition** — one of *act / act-watch / watch / investigate / pause / ignore*.
- **In-sample vs. prospective** — fit to known cases vs. tested on genuinely unseen future cases.
- **CRPS** — Continuous Ranked Probability Score; a strictly-proper forecast score.

---

## 14. Source register

This document was reconstructed from the following canonical files in the author's Google Drive (folder ID `1xQHQZUIhgXjB2t9vjvg2q1WEvptISe-e`), all owned by shawn@nikaaihome.net:

| Source | Role here |
|---|---|
| `project_resonance_web.md` (modified 2026-06-17) | Canonical current form; phase history; honest status. |
| `project_spider_web.md` (modified 2026-06-17) | 14-thread architecture; Spider's-Brain methodology; the verbatim May-2025 metaphor. |
| `feedback_read_canon_first.md` (2026-06-17) | Governance: lineage, canonical-vs-parallel, read-the-canon rule. |
| `MEMORY.md` (index, updated 2026-06-17) | Canonical current-state pointers; instrument ecosystem; code paths. |
| `project_predictor_scoreboard.md` (2026-06-16) | Validation ethic; Stan Wong; the mention-universe baseline. |
| `feedback_elaboration_over_action.md` | Governance: the elaboration trap. |
| `Cognitive_Radar_Daily_Watchlist_Scanner.pdf` (2025-10) | Cognitive Radar stage artifact. |
| **`2025-05-08_threads.json` → thread *"Cognitive Radar Framework Prep"*** (Drive, raw ChatGPT export) | **Verbatim origin** of the spider-web metaphor, the "feeders," the "catch the vibration first" purpose, and the *Astra* persona (§3). |
| ChatGPT export archive, 2024 `*_threads.json` | Possible home of the earlier interest-rate-cascade framing — **searched but not yet located** (see §1 caveat). |

> **Provenance note.** The spider-web passages in §3 are quoted **verbatim** from the 2025-05-08 origin thread (raw ChatGPT export). The interest-rate cascade in §1/§2 is the author's **recalled** illustration; it was **searched for and not located** in that origin thread (which frames the model as vibration/convergence in an investing context), so it is presented as illustration of the model's logic, not as a sourced quotation — it may live in a 2024 or later export not yet retrieved. All engineering states, phase results, and the honest validation status in §7–§10 are taken directly from the canonical project memories and reported without embellishment.

---

*End of document.*
