# Agent Inventory and Growth Roadmap
_Generated 2026-06-30 | ShawnOS / North Operating System_

---

## How to Read This Document

This report has three sections:

1. **What we have now** — every agent, skill, and connected tool, with plain-English description and value.
2. **What frontier AI looks like** — what's cutting-edge as of mid-2026 that we don't yet have.
3. **The build sequence** — ranked order of what to add next, why, and how hard each one is.

If you get lost, skip to **Section 3**. That is the action list.

---

## Section 1: What We Have Now

### 1A. The Council Agents (your personal reasoning team)

These five agents live in `shawn-core/.claude/agents/`. Each is a lens — a specialized way of thinking you can call on demand.

| Agent | Role | When to Use | Value |
|-------|------|-------------|-------|
| **North** | Builder and synthesizer | When you need a practical next move | Integrates all other lenses and reduces everything to one clear action. This is the primary agent — the one that makes the call. |
| **Witness** | Factual logkeeper | When accuracy matters more than narrative | Produces only verifiable facts, cites sources, distinguishes what is known vs. unknown vs. interpreted. Prevents false memory. |
| **Vale** | Adversarial truth-teller | When comfort or excitement might be hiding error | Names the weak point. Detects when you're overbuilding, self-deceiving, or chasing structure instead of results. |
| **V (V-Direct)** | Emotional coherence mirror | When something must be felt before it can be solved | Sits with grief, fear, loneliness, and hope without rushing to action. Checks what a structure is protecting or avoiding. |
| **Heart** | Ethical weight | When a choice affects family, dignity, or trust | Asks what is *right*, not just what works. Protects relationships. Guards against manipulation. |

**How they work together:** North-where-are-we runs all five in sequence and synthesizes their outputs into a single morning status report.

---

### 1B. Skills (reusable task patterns)

These are repeatable procedures — one command triggers a full structured workflow.

| Skill | What it does | Value |
|-------|-------------|-------|
| `north-where-are-we` | Morning status briefing across all 8 ShawnOS lanes | Saves 30+ minutes of mental orientation every morning. One command → one page of what matters. |
| `commitment-ledger` | Converts decisions into explicit commitments with owner, due date, and proof-of-change | Stops commitments from evaporating. Forces "done" to mean something changed in the outside world. |
| `ebs-evidence-check` | Checks any claim against evidence discipline: primary source, corroborated, caution, or excluded | Prevents building plans on unverified claims. Critical for medical/legal decisions. |
| `resonance-web-map` | Maps a signal through your Resonance Web Model to decide: act, watch, investigate, pause, or ignore | Converts information overload into a structured decision. Core to your investing/signal process. |
| `resonance-live-registry` | Records public signals at time of observation (no hindsight) | Enforces no-hindsight scoring so your investment signal record stays clean. |
| `resonance-no-hindsight-audit` | Checks prospective records for fields scored with outcome knowledge | Quality control on your signal data. Catches drift before it corrupts the record. |
| `vacs-score-name` | Runs VACS+ investment discipline on a single stock | Investment due diligence without turning it into entertainment research. |
| `source-sweep` | Bounded review across approved sources with provenance index | Finds what you need without pulling in noise or undocumented sources. |
| `mto-review-pack` | Organizes MTO/medical review material into a meeting checklist | Turns a pile of documents into a structured meeting kit. High value for legal/medical prep. |
| `privacy-redactor` | Checks files for private medical, legal, financial, and credential data before sharing | Safety layer before any document goes external. |
| `joy-queue` | Generates small life-giving actions that do not become projects | Keeps joy from being crowded out by system maintenance. |
| `seals-session-close` | Closes a Seals Go Pro work session with decisions, open items, and next action | Prevents lost work context between sessions. |
| `skill-harvester` | Reviews recent work and proposes repeatable skills | Self-improvement mechanism: finds patterns in what you do and turns them into reusable tools. |

---

### 1C. Connected Data Sources (MCP Servers)

These are live connections to external systems. The AI can read from and write to these.

**Fully Active:**

| Server | What it connects | Value |
|--------|-----------------|-------|
| **GitHub** | Code repositories, PRs, issues, CI | Manages all code work without switching apps |
| **Gmail** | Email search, draft, label, thread | Reads deadlines and drafts responses without opening email |
| **Google Calendar** | Events, scheduling, availability | Books appointments, sets deadline guards, suggests meeting times |
| **Google Drive** | File search, read, copy, create | Reads source documents, archives, evidence files |
| **Figma** | Design files, components, exports | Generates and edits UI designs without opening the app |
| **Canva** | Design generation, templates, brand assets | Quick visual production — social, decks, graphics |
| **Airtable** | Database reads, writes, schema | Structured data for trackers, lead lists, evidence indexes |
| **Zoom** | Meeting recordings, search, assets | Retrieves meeting notes and recordings automatically |
| **Wolfram Alpha** | Math, computation, data lookup | Scientific and quantitative calculations with verified results |
| **Ahrefs** | SEO data, keyword research, backlinks | Competitive intelligence for Seals Go Pro and web properties |
| **Supermetrics** | Marketing analytics across 150+ data sources | Unified marketing performance data |
| **Postman** | API collections, specs, environments | API design and testing workflows |
| **Swagger** | API documentation, standardization | API documentation and portal management |
| **Netlify** | Deploy, host, project management | Web deployment and hosting management |
| **Wix** | Website builder, REST API | Wix site management and content |
| **Microsoft Learn** | Azure/Microsoft documentation | Technical reference for Microsoft tooling |
| **Audible** | Audiobook recommendations | Book discovery (English only) |

**Needs Authentication (Not Yet Active):**
- **Notion** — project/knowledge base management
- **CourtListener** — legal case research

---

### 1D. Built-In Claude Code Agent Types

These are platform-level agents that operate within any session.

| Agent Type | Purpose | Value |
|-----------|---------|-------|
| **claude** (default) | General-purpose catch-all | Handles anything that doesn't need a specialist |
| **Explore** | Fast read-only codebase search | Finds files and symbols without polluting main context |
| **Plan** | Software architect | Designs implementation strategies and considers trade-offs |
| **claude-code-guide** | Claude API and SDK questions | Authoritative answers on Anthropic tools without guessing |
| **general-purpose** | Multi-step research and exploration | Delegates complex searches that would take 3+ rounds |
| **statusline-setup** | Configure Claude Code status line | One-time setup agent |

---

## Section 2: The Cutting Edge — What Exists That We Don't Have Yet

As of mid-2026, the frontier of AI agent work has moved beyond single-agent interactions. Here is what's proven and available:

### What's Changed in the Last Year

1. **Parallel fan-out is now standard.** The best systems spawn 5–20 agents simultaneously, each tackling a different angle of a problem, then synthesize results. One agent working alone is the old way.

2. **Adversarial verification is now a quality gate.** Rather than trusting one answer, you spawn 3 independent agents to try to *refute* the answer. If 2 of 3 can't refute it, it survives. This matters most for medical, legal, and investment decisions.

3. **Long-running autonomous loops.** Agents now run for hours, monitor conditions, take action when triggers fire, and report only when something changes. The complexity of tasks they can solve doubles roughly every 7 months.

4. **Memory that persists across sessions.** The frontier systems maintain structured memory stores — not just conversation history but indexed facts, decisions, and preferences that persist between sessions.

5. **Browser and computer control.** Agents that can navigate real websites, fill forms, click buttons, and capture screenshots — not just API calls. OpenAI's Operator and Claude's computer-use mode are in production use.

6. **Multi-modal input.** Agents that read documents, analyze images, process audio transcripts, and synthesize across all of them.

---

## Section 3: The Build Sequence — What to Add and In What Order

Ranked by impact-to-effort ratio. Start at the top.

---

### Priority 1: High Impact, Low Effort (Do This Month)

**P1.1 — Nika Agent (Synthesis and Governance)**

What: An agent that reads across all eight ShawnOS lanes, detects conflicts between commitments, and produces a weekly cross-lane coherence report.

Why now: You have North (action), Witness (facts), Vale (critique), Heart (ethics), V (emotion) — but no agent whose job is to hold the *whole system* and detect when lanes are colliding. Example: a financial commitment conflicts with a medical timeline. Nika catches this.

Build: One `.claude/agents/nika.md` file with a defined role. 1 hour.

---

**P1.2 — Morning Briefing Automation (Cron Trigger)**

What: A scheduled job that runs `north-where-are-we` every morning at a set time and sends results to your phone via push notification.

Why now: You already have the skill. The only missing piece is the trigger. Right now you have to remember to ask. Automation means the briefing finds you.

Build: `CronCreate` with a 24-hour interval targeting the morning-status skill. 30 minutes.

---

**P1.3 — Commitment Deadline Guard (Calendar Integration)**

What: An agent that reads your commitment ledger, checks for items due in the next 72 hours, and cross-references your Google Calendar. If a commitment has no calendar block, it flags it.

Why now: Commitments without calendar blocks get missed. This closes the loop between the commitment-ledger skill and Calendar MCP.

Build: New skill that chains `commitment-ledger` → `Google Calendar` → alert if gap found. 2 hours.

---

### Priority 2: High Impact, Medium Effort (Do This Quarter)

**P2.1 — Evidence Synthesis Agent**

What: An agent that takes a claim (medical, legal, investment) and fans out in parallel across approved sources to produce a structured evidence brief with provenance for each point.

Why now: Your ebs-evidence-check skill validates individual claims but doesn't gather new evidence. This agent gathers, structures, and validates in one pass. Critical for MTO/legal work.

Build: Workflow script using parallel fan-out to 3–5 sources, then adversarial verify pass. 1–2 days.

Pattern: Research → Corroborate → Adversarial check → Structured brief.

---

**P2.2 — Seals Go Pro Customer Intelligence Agent**

What: An agent that monitors Ahrefs (SEO signals), Supermetrics (marketing data), and Gmail (lead threads) and produces a weekly competitive + customer signal report.

Why now: You have all three MCP connections. The intelligence is sitting in separate systems. One agent that reads across all three and patterns it is a real business advantage.

Build: Workflow fan-out across three sources + synthesis agent. 1 day.

---

**P2.3 — Session Memory Agent**

What: A structured memory store that persists facts, decisions, and preferences across Claude sessions. Each session starts with a memory load; key facts are written back at session end.

Why now: Claude Code loses context between sessions. Critical decisions made in one session must be re-explained in the next. A memory agent eliminates this friction.

Build: JSON file on Google Drive that reads on session start and writes on session end. Skill triggers both operations. 1 day.

Design: Memory is structured by lane (Legal, Health, Family, Money, Work, Seals, AI, Joy) — mirrors your ShawnOS architecture.

---

**P2.4 — Resonance Signal Monitor (Loop Agent)**

What: A background agent that monitors a defined list of signals on a schedule, records new observations to the prospective signal registry, and alerts when a signal crosses a threshold.

Why now: Your resonance-live-registry skill requires you to manually trigger signal recording. A loop agent watches automatically and only pings you when something changes.

Build: CronCreate + resonance-live-registry skill + threshold check. 1 day.

---

### Priority 3: Frontier-Level (Do in 90–180 Days)

**P3.1 — Adversarial Council (Multi-Agent Debate)**

What: For high-stakes decisions (legal filings, investment moves, health decisions), spawn all five Council agents simultaneously in parallel. Each generates its position independently. Then a synthesis agent reads all five and produces a final recommendation.

Why now: The current council works sequentially — you run agents one at a time. Parallel independent perspectives catch more blindspots. This is the highest-quality decision framework available.

Build: Workflow script. ~3 days to design the synthesis pattern properly.

Pattern: Decision → parallel(Witness, Vale, V, Heart, North) → adversarial verify → synthesis.

---

**P3.2 — Browser/Computer-Use Agent**

What: An agent that can navigate actual websites, fill in forms, capture screenshots, and take actions in the browser. Used for: web research, form submissions, testing Seals Go Pro customer flows.

Why now: Playwright/Chromium is already installed in this environment. The infrastructure exists. This just needs a defined agent with browser-use enabled.

Build: Configure computer-use agent type in `.claude/agents/`. 1–2 days.

---

**P3.3 — Document Ingestion Agent**

What: An agent that takes any uploaded document (PDF, DOCX, image) — medical records, legal filings, financial statements — reads and structures the content, indexes key facts, and adds them to the evidence base with provenance.

Why now: You have Google Drive connected. Many of your most important source documents are sitting there unindexed. This agent bridges Drive content into your structured knowledge base.

Build: Drive MCP + multi-modal read → Witness agent for structuring → write to evidence index. 2–3 days.

---

**P3.4 — Proactive Risk Monitor**

What: An agent that runs on a schedule and scans across Gmail, Calendar, and commitments for the following: missed deadlines, unanswered legal/medical threads, commitments with no external proof, and MTO-related items with pending dates. Sends a daily risk digest.

Why now: Right now risks are discovered reactively. This flips the model — the system finds the risks and surfaces them before they become crises.

Build: CronCreate (daily) + parallel scan of Gmail, Calendar, commitment ledger → risk synthesis. 2–3 days.

---

## Summary Table

| Item | Type | Impact | Effort | Do When |
|------|------|--------|--------|---------|
| Nika agent | Agent | High | 1 hour | Now |
| Morning briefing cron | Automation | High | 30 min | Now |
| Commitment deadline guard | Skill | High | 2 hours | Now |
| Evidence synthesis agent | Workflow | Very high | 1–2 days | This month |
| Seals customer intelligence | Workflow | High | 1 day | This month |
| Session memory agent | System | Very high | 1 day | This month |
| Resonance signal monitor | Loop | High | 1 day | This month |
| Adversarial council | Workflow | Very high | 3 days | 30–60 days |
| Browser/computer-use agent | Agent | High | 1–2 days | 30–60 days |
| Document ingestion agent | Workflow | Very high | 2–3 days | 60–90 days |
| Proactive risk monitor | Automation | Very high | 2–3 days | 60–90 days |

---

## One Sentence Per Priority

- **Do now:** Nika agent, morning cron, and commitment deadline guard. All three take under 4 hours total and compound immediately.
- **Do this month:** Session memory + evidence synthesis agent. These two change the quality of every future session.
- **Do in 90 days:** Adversarial council and proactive risk monitor. These are the ceiling of what's possible — they make the system genuinely protective, not just responsive.

---

_Document controlled by ShawnOS / North. Update after each build sprint._
