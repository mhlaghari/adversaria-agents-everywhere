# Adversaria — Product Success Overview & Launch Plan
*Laghari Labs · v0.3.12 · Compiled 27 June 2026 · Solo founder · <$2,000 budget · public launch in 2–4 weeks*

## 1. Executive Summary

**Verdict: the product is genuinely good; the launch plan as briefed is not — yet.** Adversaria is an impressive solo-founder v1 that ships, today and locally, the exact feature set its two closest rivals still gate or roadmap (on-device diarization, cross-meeting RAG, action items) plus the strictest privacy defaults in the category (SQLCipher at-rest, Touch ID / Windows Hello, per-meeting PIN, audio auto-deleted). But the briefed go-to-market aims its strongest weapon at the buyer least likely to pay for it, tries to charge before it can bill, and leads with a claim five funded rivals already make.

**The single recommended strategy:** Launch **free-only** in 4 weeks (soft date, gated on readiness — not the calendar) to harvest the unusually open switch market (59% of users say they'll change notetakers within 12 months). Lead with the *compliance gate* — "no bot joins, nothing leaves your machine" — not the privacy virtue, and open the Alex Bilzerian / Otter incident as the cold open. Keep broad privacy-conscious prosumers and the uncontested Arabic/RTL audience as the free top-of-funnel, but point the *paid* wedge at the buyer for whom privacy is a purchase-unblocker: regulated, client-facing solos and small firms (law, healthcare, finance, consulting). Defer Pro billing ~30–60 days until a Merchant-of-Record + offline license path is built and tested; capture intent via a waitlist now.

**Top 5 actions for the next 2–4 weeks:**
1. **Clear the four hard launch gates** (everything else slips): (1) macOS notarized, clean-machine install with zero terminal steps; (2) first-run wizard defaults no-GPU users straight to the Groq key path; (3) Groq long-meeting rate-limit (~6,000 TPM) fails *loud* with chunking/a clear message, never silently; (4) a capture-path QA matrix + a handful of Rust integration tests on the audio/storage boundary.
2. **Open-source one verifiable component** (the read-only MCP server or the capture/egress core) — converts your single biggest liability (closed-source vs two MIT rivals) into an HN trust token and a discovery asset.
3. **Rewrite every privacy claim to be literally true** and publish an honest data-flow page enumerating each egress (updater, in-app feedback, Google OAuth, MCP, Groq). Make the updater disclosed and disable-able so the "firewall test" actually passes. Never say "HIPAA / bar-approved" — say "designed for confidentiality."
4. **Run a private beta of 30–50** on the auto-updater to harden the untested capture path before any public spike; exit criterion = crash-free first run + first summary unaided on a clean Mac and a clean Windows box.
5. **Stage the launch as two peaks:** Show HN (Tue–Thu 8–10am PT) as the *primary* motion, Product Hunt 2–4 days later (12:01am PT, self-hunt); file AlternativeTo / SaaSHub / Privacy Guides submissions now so they index before launch day.

## 2. Is the Product Good?

**Yes — as an artifact it is a strong, differentiated v1 that out-ships funded competitors on local feature depth and privacy defaults.** Three things make it genuinely differentiated, and three things will hurt it at launch unless addressed.

**What makes it genuinely differentiated:**
1. **Deepest *shipped* local feature set in the niche.** Diarization + cross-meeting RAG ("Ask-All") + action-item extraction work today, where Meetily lists diarization and "chat with your meetings" as "Soon" and Hyprnote gates speaker ID behind its $8+/mo cloud. A present-tense, demonstrable delta — not a roadmap claim.
2. **Strictest privacy *defaults*, not privacy *marketing*.** Encryption-at-rest + biometric unlock + per-meeting PIN + audio deleted after transcription. The cloud field can't match it architecturally; the local field (Meetily, Hyprnote) doesn't ship it — Hyprnote deliberately *keeps* audio on disk as plaintext.
3. **Arabic/RTL-native UI on Windows *and* Mac today.** A real RTL interface (not just Whisper language coverage) plus same-day Windows support serves a global/MENA base and the privacy-conscious Windows user the funded leaders structurally ignore (Granola is cloud/US-first; Hyprnote is macOS-only until Q2 2026).

**What is most likely to hurt it at launch:**
1. **Closed-source against MIT incumbents on the shared wedge.** The privacy-maximalist who wants local can already get Meetily/Hyprnote for $0 *with auditable code*. Asking that buyer to trust a closed binary's privacy claim is the opposite of their instinct. *(Mitigation: open-source one component.)*
2. **Wrong beachhead for monetization.** "Privacy-conscious prosumers, global" is the segment where privacy is a stated-but-unpaid preference (#3 driver at 33%, ~7% measured premium, ATT shows ~96% take free privacy but ~nobody pays). Privacy converts to dollars only as a compliance gate for regulated pros. *(Mitigation: reposition — see §4.)*
3. **Charging in 2–4 weeks with no way to charge, and a free path that breaks under load.** No hosted billing exists; the Groq free tier's ~6,000 TPM ceiling fails on exactly the long meetings prosumers test with; the untested Rust capture path turns any dropped recording into instant churn. *(Mitigation: launch free-only + the four gates.)*

**SWOT (honest):**

| Strengths | Weaknesses |
|---|---|
| Exceptional shipped breadth for a solo v1 (capture+diarization+RAG+action items+encryption+biometric+calendar+recap+MCP+signed .dmg+auto-updater); strictest privacy architecture in the field; Groq BYO-key removes the no-GPU blocker; cross-platform *now* + Arabic/RTL. | Closed-source where auditability is the trust currency; no team features (single-user SQLite); no hosted billing infra; Rust backend has zero automated tests; macOS notarization unfinished; no onboarding wizard. |

| Opportunities | Threats |
|---|---|
| 59% likely to switch notetakers within 12 months = churn-harvesting; quantified privacy backlash as free ammo (Otter litigation, Fireflies BIPA, Google Meet's Mar-2026 bot default-deny, Bilzerian); regulated client-facing solos = fastest-warming, least-defended, real WTP; Arabic/RTL/MENA uncontested; channel fit near-perfect at ~$0. | Granola ($1.5B / $125M Series C) owns the no-bot wedge; "we don't store your audio" is "privacy enough" for ~80–90%; Meetily/Hyprnote own the exact local wedge with 252k/18k head starts and the capital to copy your diffs; platform commoditization (Zoom/MS/Google "good-enough free"); the privacy paradox. |

**Is "privacy" a strong enough wedge for prosumers? For the prosumers in the brief: no.** Privacy is a weak *primary* driver and a strong *gating* driver, and the brief picks the wrong side. Worse for Adversaria specifically: two free, open, auditable local rivals already exist, so a privacy-motivated prosumer's rational move is to download Meetily/Hyprnote at $0 — making "privacy" a reason to *not pay you*. The fix is positioning, not engineering.

**Pre-launch readiness checklist:**
- [ ] macOS notarized & Gatekeeper-clean (fresh-machine install, no terminal) + the full TCC chain (ScreenCaptureKit, mic, EventKit) correct or capture silently fails.
- [ ] Launch free-only. No in-binary license gating. Instrument upgrade intent.
- [ ] Guided first-run to a first summary with zero terminal use, defaulting non-tech users to Groq (note the `HF_HUB_DISABLE_XET=1` model-download gotcha).
- [ ] Capture-path reliability proven end-to-end (manual QA on real speech + a few Rust integration tests).
- [ ] Groq long-meeting behavior fails gracefully (chunk/queue or clear message).
- [ ] A defensible privacy/data-flow page.
- [ ] Positioning rewritten around the gate, Bilzerian cold-open, aimed at regulated pros.
- [ ] Launch assets staged (Show HN draft, PH "Coming Soon," directory submissions).
- [ ] No-telemetry bug-intake decided (in-app feedback + opt-in local log; never phone home silently).
- [ ] A loud answer to the closed-source-vs-MIT trust gap (open-source the core or publish a reproducible build).

## 3. The 360° Competitive Landscape

**The market splits into two camps Adversaria sits between:** well-funded cloud incumbents (Granola, Otter, Fireflies, Fathom, tl;dv, Circleback, Supernormal, Read AI) that win convenience and collaboration, and free open-source local tools (Meetily, Hyprnote) that own the exact privacy wedge with massive head starts. Adversaria's edge is the intersection neither camp occupies: strictest-default privacy + deepest shipped local features + cross-platform now.

**Master comparison**

| Product | Privacy model | Free / entry paid | Setup | Diarization | Collab | Platform | Funding |
|---|---|---|---|---|---|---|---|
| **Adversaria** | 100% on-device by default; audio deleted; encrypted at rest + Touch ID | Generous free / Pro $15/mo (planned) | Med (local LLM) · easy via Groq | On-device, free, shipped | None (single-user) | macOS + Windows | Bootstrapped solo |
| Granola | Local capture, cloud transcript+notes, cloud LLM, trains by default | $0 (25 notes lifetime) / $14 / $35 | Easy | Limited (cloud) | Shared folders / Spaces | mac/Win/iOS | $1.5B / $125M Series C |
| Meetily | 100% local default (Pro Hosted-AI opt-in); MIT | $0 (MIT) / $10–25 | Hard (Ollama/Python) | "Soon" / Pro-gated | Enterprise roadmap | mac/Win/Linux | Bootstrapped (Zackriya) |
| Otter.ai | Cloud, bot, voiceprints, trained on data | $0 (300 min/mo) / $16.99 / $30 | Easy | Yes (server voiceprint) | Yes | cloud/mobile/desktop/Chrome | ~$73–80M · $100M ARR · LAWSUIT |
| Fireflies | Cloud, bot, voiceprints | $0 (unlimited transcription) / $18 / $29 / $39 | Easy | Yes (mis-label complaints) | Yes | cloud/mobile/Chrome | $1B (secondary) · ~$19M · BIPA SUIT |
| Fathom | Cloud; bot + bot-free beta, all cloud-processed | $0 (unlimited recording) / $20 / $34 | Easy | Yes | Yes (team) | cloud/iOS | ~$21.7M · ~$30M ARR |
| tl;dv | Cloud, EU-hosted; bot + no-bot option | $0 / $18 / $29 | Easy | Yes (higher tier) | Yes | cloud/mobile/Chrome | ~$4.5–5.6M |
| Circleback | Cloud (bot + no-bot desktop, all cloud-processed) | No free (7-day trial) / $25 / $30 | Easy | "Flimsy" (per reviews) | Team tier | cloud/desktop/iOS/Android | $2.5M seed (YC W24) |
| Supernormal | Cloud, bot-free desktop, cloud-processed | $0 (15 credits/mo) / $20 / $40 | Easy | Unverified | Unlimited-seat credit pool | cloud/desktop | ~$12.9M (stale since 2023) |
| Hyprnote/Anarlog | Local-first default, keeps audio on disk, plaintext .md; speaker ID is paid cloud | $0 (MIT) / $8 / $25 | Med (BYO-LLM/HyprLLM) | Paid cloud only | Cloud sync/share (paid) | macOS only (Win/Linux Q2'26) | $2.2M total (YC S25) |
| Read AI (adjacent) | Cloud, bot, "digital twin," sentiment scoring | $0 (5 mtgs/mo) / $19.75 / $29.75 / $39.75 | Easy | Yes | Yes | cloud | $50M Series B · ~$450M val |

*Prices per user; annual-equivalent where reported. Granola's 25-note cap and several user counts are third-party/unverified.*

**How we beat them / where they beat us:**
- **Granola** — *Beat:* categorically — your transcript and notes never touch a server, and we don't train on you (Granola uploads both to US AWS, runs cloud LLMs, trains by default, org-wide opt-out paywalled to $35). *They beat us:* everything else — $1.5B war chest, beloved UX, mac/Win/iOS, viral VC loop, "we don't store your audio" satisfies 80–90%. Win the buyer for whom their cloud is disqualified by policy.
- **Meetily** — *Beat:* polish for non-tech users (signed/notarized + onboarding vs Ollama/Python friction, ~165 open issues), security (encryption + Touch ID they don't advertise), shipped depth (diarization + Ask-All vs their "Soon"). *They beat us:* 252k downloads, 12.9k stars, MIT auditability, Linux, SEO machine. Don't fight on stars/price.
- **Otter** — *Beat:* our architecture is the legal hedge for everything they're sued for (no bot = no covert-recording/consent claim; no voiceprint = no BIPA; nothing uploaded = nothing to intercept). *They beat us:* 35M users, $100M ARR, integrations, agents. Target the privacy-burned.
- **Fireflies** — *Beat:* no bot kills their most-documented complaint; no voiceprint sidesteps their active BIPA suit. *They beat us:* unlimited free transcription, 1M+ companies, network effects.
- **Fathom** — *Beat:* their "bot-free capture" still uploads to their cloud — disqualified for NDA/regulated buyers at any price; we capture in-person too. *They beat us:* best-in-class free tier, 5.0 G2 / 6,600 reviews, CRM depth.
- **tl;dv** — *Beat:* their EU servers still hold your meetings and send them to Anthropic; ours never do; no Arabic. *They beat us:* 2M users, 5,000+ integrations, sales coaching.
- **Circleback** — *Beat:* no free tier vs our $0 start; their "no-bot" desktop still runs the same US-cloud pipeline; their diarization is "flimsy." *They beat us:* best-rated note quality, 1,000+ automations.
- **Supernormal** — *Beat:* they abandoned locality for an agency-deliverables pivot; we stay on-device, no credit-metering. *They beat us:* finished decks/briefs, 700k+ orgs, enterprise certs.
- **Hyprnote/Anarlog** — *Beat:* cross-platform now (they're macOS-only until Q2 2026), diarization free-and-local (they charge cloud for speaker ID), audio auto-deleted (they keep it), encryption + Touch ID (they store plaintext .md). *They beat us:* 8.7k stars, MIT, YC S25, $2.2M, HyprLLM, weekly releases. If they ship Windows, a key opening closes — move now.
- **Read AI** — *Beat:* easy contrast — bot-based, cloud, surveillance-flavored (sentiment scoring). *They beat us:* $450M valuation, ~1M new users/month.

**Competitor pricing matrix (annual-equivalent unless noted)**

| Product | Free | Entry Pro (mo) | Entry Pro (annual) | Mid | Top/Enterprise |
|---|---|---|---|---|---|
| Meetily | $0 (MIT, unlimited) | $25 regular | $10 ($120/yr) | — | Custom |
| Hyprnote | $0 (MIT) | Lite $8 | Pro $25 / $250yr | — | Custom |
| Granola | $0 (25 notes lifetime) | $14 | $14 | — | $35 |
| Otter | $0 (300 min/mo) | $16.99 | $8.33 | Business $19.99 | Custom |
| Fireflies | $0 (unlimited transcription) | $18 | $10 | Business $19 | $39 (annual only) |
| Fathom | $0 (unlimited recording) | $20 | $16 | Business $25 | Custom |
| tl;dv | $0 (unlimited recording) | ~$29 | $18 | Business $29 | Custom |
| Circleback | None (7-day) | $25 | $20.83 | Team $25 | Custom |
| Supernormal | $0 (15 credits/mo) | $20 | — | Business $40 | Custom |
| Read AI | $0 (5 mtgs/mo) | $19.75 | $15 | Ent $22.50 | Ent+ $29.75 |
| **Adversaria (rec.)** | **$0 (generous, local)** | **$15** | **$10 ($120/yr)** | — | Seat-pack (later) |

Two anchors matter: direct local rivals price Pro at $8–$10/mo annual ($120/yr) and are free-forever OSS underneath; the prosumer cloud entry tier clusters $8.33–$20/mo. Adversaria's $10/yr-equivalent lands at exact parity with Meetily and just below Granola's $14.

## 4. Positioning & Messaging

**Lead with the gate, not the virtue; lead with the cloud, not the bot.** "No bot" is now commoditized (Granola, Fathom, Otter, Circleback, Supernormal, and Zoom all claim it; only 16% of users cite "botless" as a priority). The one claim the cloud no-bot tools *structurally cannot make* is "nothing leaves the machine" — so that is the headline, with "no bot" as the second sentence.

**Positioning statement:** For client-facing professionals who run calls they can't paste into someone else's cloud — consultants, lawyers, clinicians, financial advisors, founders, and privacy-conscious prosumers — **Adversaria** is a **bot-free, on-device meeting notetaker** that delivers Granola-grade notes, transcripts, and cross-meeting answers that stay entirely on your own machine: the audio is transcribed on-device and deleted, and the transcript never touches a server. Unlike cloud notetakers (Granola, Otter, Fireflies, Fathom) that upload your transcript and run it on someone else's LLM, and unlike local-but-leaky OSS tools (Meetily, Hyprnote) that keep your audio on disk and still ship diarization and cross-meeting search as "coming soon," Adversaria is sovereign by architecture — and already does the smart parts locally and free.

**One-liner (hero):** **No bot joins your call. Nothing leaves your machine.**

**Five taglines (pick by channel):**
1. "Your meetings never touch a server." — Privacy Guides / r/privacy / HN
2. "Granola-grade notes that physically can't leak."* — Product Hunt / alternative-to pages
3. "The notetaker your NDA would actually approve." — consultants/freelancers
4. "On-device meeting intelligence. Sovereign by architecture, not by policy." — r/LocalLLaMA / Lobsters
5. "Where your meetings turn into done." — North-Star line, productivity audience

*Honesty guardrail (see §8/P5): absolutes like "physically can't leak" are falsified by the auto-updater, in-app feedback, Google OAuth, MCP, and the Groq path. Use "your meeting content stays on your machine in local mode" rather than "physically can't leak," and keep the Groq label visible. The truthful firewall demo is: local mode, minus the disclosed updater check, makes no content calls.*

**Key messages, ranked for this buyer:**
1. **It can't leak — that's architecture, not a policy.** Audio, transcript, and AI run locally; the recording is deleted; notes live in an encrypted SQLite store unlocked by your face/fingerprint. No server to subpoena, breach, or train on.
2. **No bot, no "X has joined," no consent landmine.** Captures system audio + mic directly — your client never gets the popup and never self-censors. (72% report discomfort when a bot joins; 38% change what they say.)
3. **Private doesn't mean stripped-down — it's actually smarter.** On-device diarization, chat with one meeting, ask across all meetings, auto-extracted action items — shipped today, free, local. The leading OSS tools list these as "coming soon."
4. **Your meetings become a system, not a graveyard.** Action items roll into one to-do view + weekly recap; a built-in MCP server lets Claude/ChatGPT query your meetings — on your machine. (The North-Star differentiator no competitor has.)

*Supporting (global/MENA funnel):* "It speaks your language, right-to-left." A genuinely RTL-correct interface — nobody else in the category does this.

**The enemy / wedge narrative:** The enemy isn't a competitor — it's the surveillance-by-default cloud-AI meeting stack: a silent bot that joins uninvited, a transcript that lives on a US server forever, a model that trains on your client's words by default. It's no longer abstract — it's lawsuits and broken deals:
- **The Bilzerian incident (cold open).** After a Zoom with a VC firm ended, Otter kept transcribing the investors' private post-call debrief — "strategic failures and cooked metrics" — and emailed it to the founder. It killed the deal. (WaPo; corroborated by NPR.)
- **Otter** — *In re Otter.AI Privacy Litigation*, No. 5:25-cv-06911 (N.D. Cal.), four class actions consolidated Oct 22, 2025; the lead plaintiff had no Otter account.
- **Fireflies** — *Cruz v. Fireflies.AI*, No. 3:25-cv-03399 (C.D. Ill.), Dec 2025: voiceprints under Illinois BIPA ($1,000–$5,000/violation). Adversaria stores no voiceprint.
- **Even the giants retreated** — Zoom rewrote its ToS in Aug 2023 after granting itself a training license. Yet Granola still trains by default, opt-out paywalled to $35.
- **Platforms are codifying it** — since March 2026 Google Meet flags third-party notetaker bots as a "potential risk" with default-deny.

*Legal-hygiene note (§8/P5): cite only the public docket + WaPo/NPR; report facts, don't characterize — naming a $1B rival's active litigation in marketing invites a trade-libel nastygram.*

**Objection handling (top 5, condensed):**
- *"Do I have to set up Python/Ollama?"* — Two paths. Fully-local needs a local LLM (guided as far as possible). Or paste a free Groq key and run in ~60 seconds, no GPU — clearly labeled "not sovereign." Local stays the default.
- *"No GPU / will it melt my laptop?"* — Apple Silicon uses the Neural Engine you already paid for; Windows uses your GPU or falls back to CPU; if it can't, the Groq path gives the same notes with none of your machine's resources.
- *"Is local AI as good as cloud?"* — For accurate transcripts + structured summaries, yes (Whisper large-v3 + a 35B local model). Transcription is commoditized; the differentiators we do locally. A frontier cloud model is one toggle away per meeting.
- *"You're one person — what if you disappear?"* — Trust is falsifiable: run it behind a firewall and watch local mode make no content calls; every meeting exports to plain Markdown; code-signed, notarized, encrypted, no account, no server that receives your meetings.
- *"Why not just use Granola free?"* — Granola caps at 25 notes ever, trains on you by default, uploads every transcript to US cloud + a third-party LLM. Adversaria's free tier is unlimited, local, no account. Adversaria exists for the people who aren't fine with their meetings on AWS.

**Landing-page hero:**
# Your meetings. Your machine. Nobody else's.
Adversaria writes structured notes, action items, and answers from your calls — with no bot joining the meeting and your meeting content never leaving your computer. The audio is transcribed on-device and deleted. The transcript never touches a server. It just works, on Mac and Windows.
- 🚫 **No bot, no awkwardness.** It captures the call directly — clients never see "Adversaria has joined."
- 🔒 **Nothing leaves your machine.** Transcription and AI run locally; recordings are deleted; notes are encrypted and unlocked with your fingerprint. Run it behind a firewall and watch local mode stay silent.
- 🧠 **Smarter than a transcript.** On-device speaker labels, chat with any meeting, ask across all of them, action items that roll into your to-dos — all local, all free.

**Download free — Mac & Windows.** No account. No cloud. No catch. · *No GPU? Start in 60 seconds with a free Groq key → (not sovereign — transcript leaves device)*

## 5. Pricing Strategy

**Headline: free-forever generous tier; Pro at $15/mo or $120/yr (early-bird $96/yr) — but launch free-only and switch Pro on ~30–60 days later** once a Merchant-of-Record + offline license path is built and QA'd. Keep all inference local or BYO-key so Pro gross margin ≈ 100% with zero privacy liability. The product can't bill in 4 weeks; the pricing below is the *plan*, not the launch-day SKU.

**Design rule unique to this product:** Local inference costs the founder $0 and BYO-key inference costs $0 (the user's key pays). So gates must be **feature/value gates, never cost gates** — and the free tier must be genuinely generous, because the two most direct rivals are free-forever OSS. A stingy free tier loses the privacy crowd before pricing enters the conversation.

**FREE — "Private notes for every meeting" (deliberately generous, $0 marginal cost):** unlimited recording + on-device transcription + local-LLM summary + action items; **on-device diarization given away free**; chat-with-a-single-meeting; Copy + Export .md; Arabic/RTL + multilingual; **all privacy features** (encryption, Touch ID/Windows Hello, per-meeting PIN); free Groq BYO-key path; My Notes + custom vocabulary. *Why so much: it costs nothing to serve, it must beat Meetily/Hyprnote's free OSS, and "we don't paywall your privacy or your diarization" is itself a weapon.*

**PRO — "Your meetings as a searchable second brain + task engine":**
- **Cross-meeting "Ask" / RAG over all meetings** — the strongest lever; value compounds weekly as the free corpus grows (Granola's history-cap lever inverted into additive value, no resentment).
- **Calendar integration + attendee rosters** — only client-facing pros connect a calendar; the gate self-identifies the high-WTP buyer.
- **Advanced exports** (PDF/DOCX/Notion/Obsidian) — highest-intent paywall, fires when a note must reach a client.
- **Weekly recap + consolidated to-dos + read-only MCP server** — the North-Star "feed a task board + agent loop"; lowest-churn cohort.
- Unlimited custom prompt templates + priority support + early access.

**Price points & rationale:** Pro Monthly $15; Pro Annual $120/yr ($10/mo, "2 months free"); launch early-bird $96/yr (~$8/mo, time-boxed). $120/yr = exact parity with Meetily ("same price, but encrypted at rest, with diarization + RAG, on Windows *and* Mac, today"); $15 monthly anchors to Granola's $14 ("same money, and it physically can't upload your meeting"). Sit below Circleback's $20.83 no-free-tier floor. The $5/mo monthly-to-annual gap funnels cash upfront. Don't race to $8 — the ~7% privacy premium and the compliance-gate dynamic justify the top of the $10–20 band; regulated buyers read "$8" as "hobby project."

**Lifetime deal — CAREFUL, not launch capital.** A "Founder's Lifetime" at $149 capped to ~300 buyers is safe *because the product is local* (covers local + BYO-key at $0 marginal cost; explicitly exclude future hosted services). But the feasibility critique is right that 300 buyers of a closed-source $149 license — before you have an audience or a tested in-binary license path, from a crowd that can get Meetily/Hyprnote free and auditable — is not a runway assumption. Treat any LTD as later upside, run it after the license path is QA'd, then close it (LTDs cannibalize MRR).

**Team tier — NO at launch.** Single-user SQLite; real team features need a server (the exact cost + privacy liability the product avoids). If small firms ask, offer a trivial **seat-pack** (5 Pro entitlements at ~15% off) — pure billing, no new infra. Real multi-user is post-PMF.

**Billing & infra (post-launch, before charging):**
1. **Merchant of Record (LemonSqueezy), not raw Stripe** — global self-serve needs an MoR to remit worldwide VAT/GST; its checkout also issues license keys.
2. **Offline-verifiable license** — signed token (Ed25519/JWT) verified locally inside Tauri, online activation once, 1–2 device binding, offline grace window. No standing server. Keep license code away from the untested capture path.
3. **Monetize entitlements/features, never inference** — local = $0; BYO-key = the user pays and the transcript flows directly to the provider under their key (you never see it, externalizing cost + GDPR liability). Do NOT build hosted/managed inference under this brand (per-token COGS, makes you a data processor, breaks the brand). If ever demanded, ship a walled-off, opt-in, clearly-labeled "Managed AI" add-on at cost-plus.

**First-year revenue sensitivity (illustrative, once Pro is live):** Conservative — 8,000 downloads × 30% activation × 3% paid = 72 payers ≈ $800/mo ≈ $9.5K ARR. Base — 20,000 × 40% × 5% = 400 payers ≈ $4,400/mo ≈ $53K ARR. Optimistic — 50,000 × 50% × 8% = 2,000 payers ≈ $22,000/mo ≈ $264K ARR. Blended ARPU ~$11/mo. Activation is the #1 lever you control — the Groq path lifts it from ~30% toward 50%. Be honest: this is an indie/lifestyle trajectory, not venture-scale; the compliance-gated regulated-pro wedge is what supports top-of-band pricing and a real (if modest) curve via seat-packs.

## 6. Do You Need Beta Testers?

**YES — run a private beta of 30–50 before the public spike, primarily to de-risk, not to grow.** Your Rust backend has zero automated tests, you have two un-battle-tested install paths (Windows + un-finalized macOS notarization), and the Groq long-meeting rate-limit is a known sharp edge. A public HN/PH spike is the worst place to discover a first-run crash or a dropped recording — the one unrecoverable, churn-causing failure for a capture app. You already have the instrumentation (in-app sign-up + feedback + auto-updater), so the cost is low and the payoff (ship a fix to all testers in one auto-update) is high.

**Beta program design:**
- **How many:** 30–50 active — enough to surface crashes across hardware (Intel vs Apple Silicon, GPU vs no-GPU, Windows vs Mac) without drowning a solo founder.
- **Recruit from:** existing in-app beta sign-ups first; then r/macapps + r/LocalLLaMA ("looking for 25 testers for a local meeting notetaker"), your personal/indie network, and **3–5 friendly consultants/lawyers for the high-WTP signal** (also your first compliance design-partner conversations). Bias toward real meetings — Whisper hallucinates on silence.
- **Instrument feedback:** (1) in-app feedback as default; (2) a one-screen first-run survey; (3) a Discord/Telegram for fast back-and-forth; (4) a daily metric — % reaching a successful first summary (activation) + crash-free session rate.
- **Exit criteria to launch:** crash-free first run on a clean Mac and a clean Windows machine, the long-meeting Groq path degrades gracefully, and ≥80% of testers reach a first summary unaided. Auto-updater ships the fixes; launch on the hardened build.

## 7. The Launch Playbook

**One strategic decision governs everything:** lead with the gate, not the virtue; make **Show HN the primary motion** (merit-based, HN's favorite category, needs no pre-built audience) and demote Product Hunt to a second peak. This is a *credibility-and-list-building launch, not a revenue launch.* Your direct fight is Hyprnote and Meetily — not Granola. Three launch-day wedges against them: cross-platform now, stricter default privacy, shipped depth.

**Week-by-week (3-week core; stretch to 4):**
- **T-3 — Foundations & de-risking:** finish macOS notarization (hard blocker; verify clean-Mac install). Stand up PH "Coming Soon" (target 500–1,000 followers) + a landing page with a no-email-gate download. Recruit the 30–50 beta cohort. Submit to AlternativeTo (alt to Granola/Otter/Fireflies), SaaSHub, BetaList now so they index.
- **T-2 — Assets + beta loop:** produce the 60–90s captioned demo + a 10–15s silent GIF (sparse note → summary + action items). Write the Show HN post, PH first comment, 5–10 gallery images, taglines. Fix the top 3 crash/confusion bugs only. Add the Groq long-meeting graceful message. Soft-participate (don't pitch) in r/macapps, r/LocalLLaMA, r/privacy, Lobsters.
- **T-1 — Seeding & dry run:** draft launch-day email (link only — never "upvote"). Line up 8–12 supporters. Pitch newsletters/reviewers (embargoed). Dry-run install on a borrowed Windows machine + clean Mac. Pre-write the network-monitor "nothing leaves" note (honestly showing the disclosed updater check, nothing else in local mode).
- **T-0 — Launch week (two peaks):** Day 1 (Tue/Wed 8–10am PT) **Show HN first** — answer every comment fast/technically ~6 hrs. Day 3–4 (separate Tue/Wed/Thu 12:01am PT) Product Hunt (don't stack same-day). One fitted subreddit per day.
- **T+1 — Follow-through:** post results recap + roadmap (build-in-public). Convert attention into the Pro **waitlist** (no fake checkout). Submit to Privacy Guides forum / PrivacyToolsList / awesome-privacy-tools with evidence. Re-pitch reviewers with "#X on PH, front-page HN." Ship one fast visible fix.

*To stretch to 4 weeks, insert a week between T-2 and T-1 to grow PH followers toward 1,000 and run a second beta wave. To compress to 2, cut beta to ~15 trusted users and pitch only the 5 highest-fit newsletters. Take the 4-week end; the date is soft — ship the day the four gates are green.*

**Channels, ranked:**
1. **Hacker News "Show HN" (primary).** Title: `Show HN: Adversaria – On-device meeting notes, no bot, nothing leaves your Mac/PC`. Body in your own voice: one-line what, the problem (bot fatigue + Otter/Fireflies suits), the technical how (faster-whisper/MLX + Ollama, audio deleted, on-device diarization, encrypted SQLite), what's different, an honest ask. Mechanics: ~8–10 genuine upvotes + 2–3 thoughtful comments in the first 30 min; front page can drive 20k–80k visits. Tue–Thu 8–10am PT. Risks: closed-source scrutiny (have network-monitor proof + open-source one component); untested Rust path could crash (beta first); never vote-ring (lifetime domain ban).
2. **Product Hunt.** Self-hunt. 12:01am PT Tue/Wed/Thu. Target 200+ upvotes and 30+ comments by ~6am from verified accounts; reply within 15 minutes. First comment = highest-leverage asset (positioning + Bilzerian in two lines + what's different + the feedback you want). Top-5 realistic in the ~250–500 upvote range if early velocity holds. No "please upvote," no vote trading, no going dark.
3. **Named subreddits (10% rule, one at a time):** r/macapps (~172k, best Mac sub), r/LocalLLaMA, r/privacy + r/privacytoolsIO (bring your data-flow answer), r/selfhosted/r/opensource (softer while closed), r/productivity/r/macproductivity, Windows: r/windowsapps, r/software, r/Windows11. Niche: r/notetaking, r/ObsidianMD (.md export), r/Whisper. High-WTP seeding: r/Lawyertalk, r/medicine, r/medicalscribe, consultant communities — compliance framing (NYC Bar Op. 2025-6 "deploy AI locally").
4. **Indie + privacy directories (evergreen SEO):** AlternativeTo (DR-79), SaaSHub, StartupStash, SaaSworthy, PrivacyToolsList.com, awesome-privacy-tools, Slant. Caveat: Privacy Guides / PrivacyTools.io weight toward open-source/audited — you'll likely be deferred as a closed app; apply with no-egress evidence but treat a full listing as a stretch goal.
5. **Newsletters & reviewers (one hit ≈ a PH day):** TLDR Infosec (~400k), Secrets of Privacy, Osano "Privacy Insider," TechCrunch Privacy tip line; MacStories (Federico Viticci), The Sweet Setup, 9to5Mac, Tom's Guide, HiddenApp; Tiago Forte; Ben's Bites / TLDR AI.
6. **Privacy advocates (highest-credibility multipliers):** Naomi Brockwell (NBTV), Techlore — personal note + 60s demo + no-egress proof + no-strings review build; The New Oil, Privacy Guides forum (as a tool-review candidate).
7. **X build-in-public + Lobsters + Indie Hackers (slow burn):** demo GIF, the Bilzerian thread, substantive replies under Granola/Otter/Fireflies privacy threads. Lobsters (self-promo <25%) is a friendlier engineer signal than HN.

**Assets to build:** landing page (one scroll, dual Download buttons, 3-second proof row, Bilzerian block, feature triad, labeled Groq path, "how we prove nothing leaves" shot, Pro waitlist — no fake checkout); 60–90s captioned demo; 5–10 PH gallery images as a story; 10–15s silent GIF.

**Who to talk to (named, under $2k):** privacy advocates (Naomi Brockwell, Techlore, The New Oil); privacy/security newsletters (TLDR Infosec, Secrets of Privacy, Osano); Mac/productivity (MacStories, 9to5Mac, Tom's Guide, Tiago Forte, Ben's Bites/TLDR AI); high-WTP seeding in r/Lawyertalk, r/medicine, r/medicalscribe, consultant communities with the compliance framing.

**Budget (<$2,000):** most of the stack is ~$0. Reserve $300–800 for the demo video (or Screen Studio ~$89 DIY), GummySearch (~$29/mo), Loops/Resend free tier, and optionally $300–500 for one privacy/Mac newsletter sponsor slot only if organic doesn't land. Spend $0 on hunters or upvote services.

## 8. Risks & How The Plan Survives Them

Prioritized from both pressure-tests; each mitigation is baked into the plan, not appended.

| # | Risk | How the plan survives it |
|---|---|---|
| P1 | **Launching to an empty room (most likely flop cause).** Solo, no list, closed binary into a niche owned by two MIT rivals with 252k/18k head starts. | **Show HN primary** (merit-based); spend the weeks open-sourcing one verifiable component (worst liability → HN trust token + discovery asset). Lower the bar: this is a list-and-credibility launch, not a revenue launch. |
| P2 | **Compounding activation trap.** Non-tech users can't finish the local path (LLM server; `hf_xet` 0-byte bug) → pushed to Groq, where ~6,000 TPM silently fails on long meetings; if Show HN sends 20–80k people it dies in public. | Two hard gates: first-run wizard defaults no-GPU users straight to Groq; Groq long-meeting handling chunks/queues + shows a clear message, never silent. |
| P3 | **macOS notarization unfinished.** Un-notarized = Gatekeeper scare on every fresh Mac; the hardened-runtime TCC chain (ScreenCaptureKit, mic, EventKit) must be correct or capture silently fails. | Non-negotiable gate: fresh-machine install, no dev tools, zero terminal, records + summarizes end-to-end on a clean Mac and a borrowed Windows box. No pass, no launch date. |
| P4 | **Freemium billing + Pro in 2–4 weeks is infeasible and self-contradictory** (can't stand up MoR + offline Ed25519 verification + QA in a Rust backend with zero tests; the plan wants "$45k LTD cash" while saying "free-only"). | Launch free-only; no in-binary license gating; waitlist for Pro intent; drop the $45k-LTD-as-runway thesis; never build hosted inference; charge ~30–60 days post-launch. |
| P5 | **Absolute privacy claims are falsifiable + a liability** (updater, feedback, OAuth, MCP, Groq all egress; the "no-egress proof" would show egress; "bar-approved" invites reliance; naming a $1B rival's suit invites trade-libel). | Replace absolutes with precise true claims; publish a data-flow page enumerating every egress; make the updater disclosed/disable-able so the firewall demo is genuinely true; never claim HIPAA/"bar-approved" — say "designed for confidentiality"; cite only the public docket + WaPo/NPR. |
| P6 | **Rust capture path has zero tests; a dropped recording is the one unrecoverable churn event.** | A few integration tests on the audio/storage boundary + a manual full-flow QA matrix run through the 30–50 beta on the auto-updater. Exit: crash-free first run + first summary unaided. Keep license code away from this path. |
| M1 | **Privacy is a *negative* driver for prosumers** — the more they care, the more they're routed to free auditable Meetily/Hyprnote. The funnel and the payer are different humans. | Sell privacy as a compliance gate to regulated client-facing solos; price at the top of the band; keep broad prosumers/MENA as a $0 awareness funnel, never the monetization thesis. |
| M2 | **"No bot" is commoditized** (5 funded rivals + Zoom; only 16% prioritize botless). | Demote "no bot" to the second sentence; lead with "nothing leaves the machine"; Bilzerian cold-open. |
| M3 | **The Groq path deletes sovereignty for the median (non-tech) user**, while the local minority can pick free MIT rivals — a pincer. | Near-term: default to Groq with graceful failure + honest labeling. Roadmap (loudly stated): bundle a small on-device model so "sovereign" is the default reality. Monetize the provider-agnostic North-Star layer (meetings → to-do board + MCP/agent loop). |
| M4 | **TAM for the privacy-prosumer slice is indie-scale** (~$53K ARR base), not SaaS. | Be honest about the business; don't over-build SaaS billing; land regulated solos + 2–20-person firms; grow via seat-packs. The north-star agent category is a 12-month bet, not a 4-week launch. |
| M5 | **Closed-source is a trust liability in the only niche your wedge fits**, and the conversion thesis assumes month-2–3 retention you have no data for. | Open-source the privacy-critical core (or publish a reproducible build + Little Snitch zero-egress proof) loudly on the roadmap; pre-sell the compliance pitch to 5–10 regulated solos; harden capture in the beta. |
| P7 | **The 2–4 week timeline is over-stuffed** (realistically 6–10 weeks solo). | Cut to the four hard gates and let everything else slip; take the 4-week end; the date is soft — ship when the gates are green. |

## 9. 90-Day Success Metrics

**Because the launch is free-only, 90-day success is measured in reach, activation, retention, and validated intent — not MRR.** Pro revenue (if Pro ships around day 30–60) is upside.

| Metric | Floor | Target | Stretch | Why |
|---|---|---|---|---|
| Downloads (90 days) | 2,000 | 4,000 | 8,000+ | Show HN front page (20–80k visits) + a PH day + directories; Meetily/Hyprnote had multi-year flywheels you don't yet. |
| Activation (% reaching a first summary) | 30% | 40% | 50% | The #1 lever you control; the Groq-default wizard lifts it. The single most important number. |
| Local vs Groq split | — | measure | — | Tells you how big the no-GPU segment is and how much the bundled-local-model roadmap matters. |
| Crash-free first-run / session | 95% | 98%+ | 99%+ | A capture app lives or dies here. |
| D7 retention | 20% | 30% | 40% | Proves the habit loop. |
| D30 retention | 10% | 15% | 25% | The cohort that exists at month 2–3 when the cross-meeting "Ask" upgrade lever fires. |
| Pro waitlist signups | 250 | 500 | 1,000 | ~10–15% of activated; leading indicator of monetizable demand. |
| Regulated-pro design partners (paid pre-sales/LOIs) | 3 | 5–10 | 15 | The real validation of the thesis — worth more than 1,000 free prosumers. |
| GitHub stars (open-sourced component) | 200 | 750 | 2,000+ | Trust proxy + discovery flywheel that closes the closed-source gap. |
| Paid conversion (if Pro live, % of activated) | 3% | 5% | 8% | ~100–400 payers by day 90 in the target case. |

The two metrics to obsess over: **activation** (40%) and **regulated-pro pre-sales** (5–10). The first proves the product works for the user you invited; the second proves the business thesis. Vanity downloads without either are a failed launch that looked busy.

## 10. Sources

**Competitors (read live June 2026):** Granola — granola.ai/pricing, granola.ai/security, granola.ai/blog/series-c, techcrunch.com (2026-03-25, $125M/$1.5B), sifted.eu. Meetily — meetily.ai/pricing, github.com/Zackriya-Solutions/meetily. Hyprnote/Anarlog — anarlog.so/pricing, github.com/fastrepl/anarlog, news.ycombinator.com/item?id=44725306, pitchbook.com/profiles/company/847247-77. Otter — otter.ai/pricing, npr.org/2025/08/15/g-s1-83087, case 5:25-cv-06911. Fireflies — fireflies.ai/pricing, commlawgroup.com (Cruz v. Fireflies BIPA), case 3:25-cv-03399. Fathom — fathom.ai/pricing, techcrunch.com/2024/09/19, businesswire.com (Oct 2025 bot-free). tl;dv — tldv.io/app/pricing. Circleback — circleback.ai/pricing, security.circleback.ai. Supernormal — supernormal.com/pricing, balderton.com. Read AI — read.ai/plans-pricing, techcrunch.com/2024/10/28.

**Market/privacy/channels:** grandviewresearch.com (AI meeting assistant, $21.5B by 2033, 25.8% CAGR); gladia.io/meeting-assistant-market-map (switching/priority stats); washingtonpost.com/technology/2025/07/02 (bot fatigue + Bilzerian), uctoday.com (Bilzerian/Otter); nycbar.org Formal Opinion 2025-6 ("deploy AI locally"); iatrox.com (on-device clinical AI / HIPAA + all-party-consent); iapp.org (GDPR/EU AI Act), lw.com (Nov 2025 Digital Omnibus — loosening); Usercentrics/Sapio State of Digital Trust 2026 (~7% premium) via lasvegassun.com; Deloitte (privacy paradox); softwarefinder.com (B2B security in first call >50%); smollaunch.com (Product Hunt), flowjam.com (Hacker News front page), markepear.dev (dev-tool HN launch), privacyguides.org/tools, launchdirectories.com.

**Unverified / flagged:** Granola's "25 notes lifetime" cap (third-party, not on the official page); WAU/user counts (Granola ~80–100k; Meetily/Hyprnote self-reported); the "Gartner: 40% of enterprises will ban meeting bots by 2025" stat (likely apocryphal); the "62% would pay for a never-stores service" stat (untraceable — use Deloitte instead). Several competitor valuations (Otter, Supernormal, tl;dv, Circleback) are stale or undisclosed.