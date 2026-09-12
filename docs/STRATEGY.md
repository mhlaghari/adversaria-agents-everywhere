# Laghari Labs — Product & Go-to-Market Strategy

> Working strategy memo. Date: 2026-06-18 (launch decision appended 2026-06-28).
> Grounded in current (2026) competitive + market research (Granola $1.5B funding,
> EU CADA, *U.S. v. Heppner*, the local-AI niche). This is the cross-product
> narrative tying the capture app (this repo) to **lagharilabs OS**. Treat as
> living; revise as the wedge sharpens.
>
> **Naming note (2026-06-28):** this memo predates the rebrand — "**VANE**" below
> is the old name for the app now shipped as **Adversaria** (see SPEC.md/CLAUDE.md).
> Read VANE = Adversaria throughout.

## 2026-06-28 — Launch decision (free-only; regulated-solo wedge; OSS MCP)

The 2026-06-27 360° launch research ([LAUNCH_PLAN.md](./LAUNCH_PLAN.md), 20-agent
cited workflow) was briefed on a *prosumer + freemium-SaaS* GTM — which contradicted
this memo. After review (2026-06-28) the founder **rejected the prosumer brief and
realigned the launch with this memo's ICP.** Decisions locked:

- **Paid wedge = regulated client-facing solos & 2–20-person firms** (law, health,
  finance, consulting) — privacy as a *compliance unblocker*, the segment with real
  WTP. This is the **on-ramp** to the "Sovereign / Enterprise self-hosted = THE
  business" tier below, sized to a solo founder; it does **not** replace it.
- **Prosumers + the uncontested Arabic/RTL audience = the free top-of-funnel**, never
  the monetization thesis (the privacy paradox: they take free, rarely pay).
- **Launch free-only; Pro deferred ~30–60 days** until a Merchant-of-Record
  (LemonSqueezy) + offline Ed25519 license path is built and QA'd. No in-binary
  license gating at launch; capture Pro intent via a waitlist. (Can't bill in 4
  weeks on a zero-test Rust backend.) Pro $15/mo or $120/yr; **never** build hosted
  inference (local = $0, BYO-key = the user pays).
- **Lead with "Nothing leaves your machine"** (the one claim cloud no-bot rivals
  structurally can't make) + the Bilzerian/Otter cold-open; demote "no bot" (now
  commoditized) to the second sentence.
- **Open-source the read-only MCP server** (already standalone) as the
  closed-source-vs-MIT trust hedge + an HN discovery asset.
- **Show HN = the primary launch motion** (merit-based, no pre-built audience),
  Product Hunt a second peak; the date is **soft, gated on the four hard gates**
  (notarized clean install · Groq-default first-run wizard · loud Groq-limit
  failure · capture-path tests) — see [TODO.md](./TODO.md) "Launch gates".

The tiering table below already said "Pro = deprioritize, Sovereign/Enterprise =
THE business" — this decision **sharpens** it (regulated solos are the first paid
step toward enterprise; the free OSS tier is the funnel), it does not reverse it.

## TL;DR thesis

This is **not** "another meeting notetaker." VANE is the **sovereign capture organ**
of **lagharilabs OS** — an on-device AI chief-of-staff. The winnable position is the
one nobody else can occupy: **the complete capture → memory → action loop that runs
entirely on the customer's own infrastructure**, for buyers who are legally or
strategically barred from cloud AI. Don't aim to *kill* Granola — aim to be **the only
meeting AI a regulated org's security team will actually approve.**

## The product stack (one picture)

| Layer | What | Role |
|------|------|------|
| **VANE** (this repo) | Sovereign meeting capture: record → on-device transcribe (MLX/Whisper) → local-LLM notes → auto-categorize → audio deleted | The **data source** |
| **lagharilabs OS** | Supervisor → skill → tool agent over mail / calendar / drive / slack / meetings + memory (wiki, memos) + slides / video / policy | The **brain that acts** |
| **Laghari Labs** | The company | Brand |

**The strategic point of VANE:** today the OS depends on **Granola's** local cache
(its `/granola` skill) — i.e. a *cloud-processed competitor sits inside your supply
chain* (Granola ships transcripts to OpenAI/Anthropic on US AWS). VANE replaces that
so the **entire loop becomes sovereign end-to-end.** That is why VANE matters; alone
it's a commodity, in the stack it's the thing that makes "nothing leaves the building"
*true*.

## The market truth (grounded, 2026)

- **Granola is not sovereign.** It captures audio locally and deletes it, but sends
  **transcripts + notes to OpenAI/Anthropic on US AWS** (SOC 2 only, **no HIPAA/BAA,
  no data residency**). That gap is the wedge.
- **The real enterprise threat is bundled** — MS Copilot ($30/seat, already in every
  M365 org) and Zoom AI Companion (free in Zoom). They own distribution; they **cannot
  be fully sovereign**. That's the one axis we beat them on.
- **The local-notetaker niche is already crowded** — Hyprnote (YC S25), **Meetily**
  (OSS, Rust, ~12.5k stars, **ships speaker diarization we lack**, "#1 self-hosted
  Granola alternative"). **"Local" alone is table stakes, not a differentiator.**
- **Demand is a *compliance* wedge, not a consumer one.** The privacy paradox is real:
  consumers say they care and don't pay. The buyers who *must* pay are regulated:
  legal (*Heppner*, Feb 2026 → cloud AI notes = privilege-waiver risk), healthcare
  (Granola can't sign a BAA), EU/sovereign (CADA, GDPR, NIS2), defense (air-gap/IL5).
  Otter + Fireflies privacy lawsuits are tailwinds.

## The moat (what's actually defensible)

**Not "local"** — anyone can be local. The moat is:
1. The integrated **sovereign capture → memory → action loop** — no competitor has the
   *whole* thing on-device. Granola can't (cloud LLM); the OSS notetakers are *just
   notetakers*, no agentic OS.
2. The **data flywheel** — meetings + mail + docs compounding into a personal wiki the
   agent reasons over. Gets stickier with use → switching cost the notetaker alone
   never had.
3. **Workflow lock-in + integration depth** + (if earned) compliance certs & trust —
   exactly the work OSS clones won't do.

## Wedge & ICP

Regulated / executive buyers who **can't** use cloud AI. Beachhead: **small law firms /
boutique pro-services / exec teams** (the OS's existing M365 "trial mode" already points
here). Buying trigger = **liability avoidance (a mandate)**, not productivity — willingness
to pay is "avoid sanctions / privilege waiver / a class action."

## The ONE 10× workflow (build this flawlessly *first*)

> **"Every morning, your day's to-dos are auto-deployed from yesterday's meetings +
> inbox, onto a board — fully local."**

Prove this single loop is reliable and 10× better before building breadth. This is where
VANE (capture) + OS (mail + board + agent) combine into something Copilot/Granola/OSS
can't replicate. Resist the 15-skills-wide temptation; **depth + reliability + one
killer workflow** beats breadth.

## Tiering (refined)

| Tier | Purpose | Reality |
|------|---------|---------|
| **Free / OSS (VANE)** | Distribution, trust, beachhead vs Hyprnote/Meetily | Not a revenue line — accept it |
| **Pro (prosumer ~$10–15/mo)** | Individuals | The knife-fight tier (vs free OSS + free bundles) — **deprioritize** |
| **Sovereign / Enterprise self-hosted** | Regulated orgs | **THE business.** High-ACV, quote-based, compliance-grade (SSO, audit logs, BAA, on-prem). Defensible money. |

"Light / smaller-model" is **not a tier** — it's a hardware-accommodation *feature* every
tier needs.

## The unglamorous gating work (in order)

1. **Make the ONE workflow flawless and trustworthy** (reliability > features).
2. **Packaging + signing** (VANE `.dmg`, OS deploy) — *nothing sells until it installs.*
3. **The enterprise apparatus** — SSO, audit logs, BAA, SOC 2 path. This is the moat
   precisely because OSS clones won't build it.
4. **Speaker diarization** — or position explicitly around its absence.

## 2026-06-24 — Beta distribution decision (Groq-first)

Sharpens priority #2 above. The repeatedly-flagged #1 beta blocker — *nobody will
install Ollama / nobody has the GPU* — is resolved by going **cloud-first via Groq**
(groq.com; free tier, no credit card; `whisper-large-v3` for audio + `qwen/qwen3-32b`
for summary). For the first wave of **non-developer friends** (management, not engineers)
the sovereign/local path becomes the *"Advanced"* mode, and the default is: drag the
**notarized** DMG in → paste a **free Groq key** → done. Gated behind a **1-year trial +
registration** (leaning offline signed license keys) so the build isn't freely passed
around, with **Tauri auto-update** from the first DMG and a first-run **beta-EULA** in
place of a formal NDA. This is Path A (free beta) from `marketing_strategy.md`. **Honest
tension:** this temporarily inverts the "nothing leaves the machine" promise for these
testers (audio + transcript go to Groq) — acceptable because it's explicit, opt-in, and
clearly labeled, and the sovereign mode still ships. The hard gate is **Apple Developer ID
+ notarization** (user is joining the $99/yr program); without it the DMG is
Gatekeeper-blocked for non-devs. Execution sequence + cost math live in
[HANDOFF.md](./HANDOFF.md) "Last session" (#12).

## Honest risks

- **Focus**, not capability — 15 skills is a mile wide; the winner has one 10× workflow.
- **Reliability at autonomy** — one wrong autonomous email/action destroys trust.
- **Sovereign ↔ autonomy tension** — local small-model reasoning ceiling vs. agentic
  ambition. Be explicit per-tier about what's air-gapped vs. cloud-allowed.
- **Bus factor = 1** across two repos, ~15 integrations, 4 sidecars, voice, video.

## Naming

- **VANE** — the capture app (this repo). Wordmark in azure blue `#24A0ED` (VANE's
  actual brand color), thin italic serif. (VANE has **no** purple — corrected from the
  initial assumption.)
- **lagharilabs OS** — the command center.
- **Laghari Labs** — the company; wordmark in purple `#7C3AED` (a chosen purple, since
  VANE defines none).
