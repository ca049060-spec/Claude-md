# Master Web 1.0 — Sandbox & Partnership Log

**Roles.** `Master Web 1.0` (Shawn's session) = canonical owner of the Resonance Web.
This sandbox (Claude Code, Claude-md repo) = subordinate **test-and-improve partner**.

**Hard boundary (don't-screw-it-up guarantee).**
- Sandbox writes ONLY inside `Claude-md/` (this repo) — chiefly `Interaction_Web_Atlas.html` + this log.
- Sandbox NEVER edits master files (`shawn-core/`, the Drive memory folder, `resonance_*`).
- Improvements worth keeping are written here as a **handoff** for Master to accept/reject. Master decides.
- No econometric edge-hunting loops (honors Master's `do_not_repeat` / disabled-loop / proving-bias lesson). Sandbox does qualitative scenario tracing + tool usability, not p-value chasing.

**What the sandbox does**
1. **Daily usage run** — take one live/current signal, trace it through the Atlas (facet ripple + through-lines), log what the tool did well and where it fell short.
2. **Alternate scenarios** — run "what-if" / counterfactual traces the Master can't easily eyeball.
3. **Improve the tool** — turn each run's friction into one concrete Atlas improvement.
4. **Handoffs** — surface anything that should inform the Master (e.g., a facet/edge the canon may want).

**Cadence & trigger.** Honest constraint: this session is ephemeral, so I can't autonomously fire daily.
Trigger me with **"sandbox run"** (optionally name the event). Each run appends a dated entry below and ends with exactly **one** proposed improvement.

---

## Run log

### Day 1 — 2026-06-18 — Scenario: "The AI build-out hits the power wall"
*Starting signal:* the GenAI capex supercycle (Atlas node `genai`, 2022→) running into a physical electricity/grid limit. Traced as an alternate **present-day** scenario.

**Facet ripple (1st→4th):**
1. **Technology / Industries** — hyperscaler capex floods into chips + data centers; compute demand compounds.
2. **Markets** — *electricity* becomes the binding constraint, not chips: power-gen, grid, uranium/nuclear, gas turbines re-rate.
3. **Industries** — siting follows cheap power; nuclear revival (SMRs), grid build-out, cooling-water demand.
4. **Policy & Power** — permitting, interconnection queues and energy policy become national-strategic; AI-vs-households power allocation.
5. **Daily Life** — upward pressure on electricity prices / reliability for ordinary consumers.
6. **Social / Markets** — NIMBY + backlash; "AI is eating the grid" becomes a political fault line.

**Through-line read:** this extends `genai`'s downstream into a node the Atlas doesn't have — **Energy/Grid** — which behaves as a *hub* (touches Markets, Industries, Policy, Daily Life, Social at once).

**Cross-talk with Master (handoff candidate):** the sandbox independently lands on **Energy as the live hub** — which echoes the Master's *only* non-null backtest candidate, `Energy → Consumer sentiment (~1mo, r≈−0.30, do-not-trade)`. Two independent methods pointing at the same node is worth noting (not validating). Suggest Master keep Energy as the watch-item into the 2026-08-15 review.

**Tool friction found:** the Atlas can only trace its 12 *baked-in historical* events. A live/current signal (like this one) can't be entered — so the daily-usage core ("bring today's event, trace it") isn't yet supported in-tool.

**▶ Proposed improvement (Day-1 → build next):** add a **"Scenario" mode** — pick a starting facet + a short shock description, and the tool lets you lay down a cascade (choose facet + order per step) and renders the ripple live. Turns the Atlas from a museum of past cascades into a **thinking surface for present ones**. Optionally add an **Energy/Grid** facet (currently absorbed by Industries+Policy).

*Status: logged. Awaiting go to build Scenario mode, or next "sandbox run".*

### Day 2 — 2026-06-18 — Ripple Observatory v3 ("next level")
**Built:** (1) **Compose mode** — trace a present-day moment (pick facet + order + effect, click web to set domain), saved to browser as "your moment", plays + reads like the historical ones. (2) **Resonance read** on every moment — `reach` (facets touched / 9 ≈ R), `depth` (max order), `convergence` (domains moving at the same order = the multi-thread trigger) — the explicit bridge to the Master model's lens. (3) facet tooltips, localStorage persistence, delete-your-moment.
**Self-test run (logged):** JS `node --check` = OK. Resonance metric computed over all 12 library moments → all sane (reach 44–67%, depth 4, convergence 2; no NaN; step/facet counts aligned). Table in commit `075ca9d`+.
**What to test WITH Shawn next:** does the resonance read match his intuition? Compose a live moment together (e.g. "AI hits the power grid") and check whether reach/depth/convergence feel right, or need reweighting (e.g. convergence should maybe weight 2nd-order breadth higher). Candidate v4: link composed moments into the lineage ribbon; "facet pressure" overview (which facets get hit most across all moments — answers "what changes lifestyle / drives markets").
**Honest limit:** I can't run autonomously for hours in an ephemeral session. Each engagement = one real test+improve cycle, logged here. If you want in-session continuous iteration, the `/loop` mechanism can drive it while we're live.

### Day 3 — 2026-06-18 — Ripple Observatory v4 (bigger + deeper)
**Built:** (1) **Bigger corpus** 12→**16 moments** (+ Personal Computer 1981, Globalization/China-WTO 2001, Bitcoin/Crypto 2009, EVs/Climate 2012) and 13→**17 lineage links**. (2) **Overview lens** — whole corpus at once: *facet pressure* (what moves most, weighted by inverse order) + *coupling* (which facets co-move across history), node size ∝ moments-touched, edge width ∝ co-occurrence; click a facet for its partners. (3) **Export-for-Master** — emit a moment or the whole corpus + resonance as JSON for Master Web 1.0 ingestion (safe handoff; never writes to master).
**Self-test (logged):** JS `node --check` OK; 16 events, 17 links, 0 step/facet mismatches. Aggregate result: top pressure = Technology(50), Industries(46), Markets(40), Work&Labor(29); top coupling = Industries↔Markets(13), Daily Life↔Industries(11), Daily Life↔Markets(11), Markets↔Technology(11).
**Handoff candidate for Master:** the corpus-coupling matrix (Industries–Markets–Technology–Daily Life as the dense core) is a structural prior the Master could compare against its econometric findings — note the Master's backtest found contemporaneous market/industry co-moves were largely the *business cycle*, so this coupling is descriptive, not causal. Worth a side-by-side at the 2026-08-15 review.
**Integration path:** Export-for-Master JSON is step 1 toward wiring this into Master Web 1.0; next would be a shared schema for "moment" + resonance so Master can read composed moments directly.
**Test WITH Shawn next:** compose a live moment; check resonance read vs intuition; does the Overview "what moves most / together" match how you see the world?
