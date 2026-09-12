# Marketing Strategy — Adversaria Competitive Assessment

> Written 2026-06-24. Comprehensive review of the product, competitive landscape,
> and go-to-market recommendations. Grounded in a deep read of the entire codebase
> + competitive research. Treat as a living strategy doc; revisit quarterly.

---

## Executive Summary

Adversaria is an unusually serious, well-engineered project for an early-stage
product. The codebase quality, documentation discipline, and strategic clarity
are far above what you'd expect at v0.1.1. The "sovereign capture organ of
lagharilabs OS" thesis is coherent and differentiated. But there are real
concerns about product-market fit of "sovereign-first," UX maturity gaps, and
the size of the wedge against incumbents. This document breaks down pros, cons,
competitive positioning, and a prioritized roadmap of suggested improvements.

---

## Pros — What's Working Well

### 1. Architecture is genuinely clean

The three-layer separation (React → Tauri/Rust → Python ML) is well-chosen.
Each layer has a clear contract:

- **Rust backend** owns state, persistence, IPC, and audio capture.
- **Python service** owns ML inference (Whisper + LLM).
- **React frontend** is presentation-only.

The `#[cfg]`-gated platform splits for Windows (WASAPI) and macOS
(ScreenCaptureKit + cpal) are done properly — shared surface, OS-specific
internals. This is not a prototype that needs a rewrite; it's production-shaped.

### 2. Privacy story is real, not marketing

- Audio deleted after transcription.
- SQLite local.
- Nothing leaves the machine.
- No bot joins the call.

Granola deletes audio but ships transcripts to OpenAI/Anthropic on AWS — you
don't. For regulated buyers, this isn't a feature checkbox, it's the whole
product. The STRATEGY.md correctly identifies this as the wedge.

### 3. Documentation discipline is exceptional

CLAUDE.md, ARCHITECTURE.md, HANDOFF.md, STATUS.md, LESSONS_LEARNED.md, TODO.md,
DECISIONS.md, STRATEGY.md, SPEC_RESKIN.md — all kept current, cross-linked,
dated. The LESSONS_LEARNED.md entries follow the exact format you'd want:
Symptom → Root cause → Fix → Prevention, with commit hashes. Most solo-developer
projects have zero docs; yours could onboard a new engineer in hours.

### 4. The "10× workflow" thesis is correct

> "Every morning, your day's to-dos are auto-deployed from yesterday's meetings
> + inbox, onto a board — fully local."

This is the right north star. Meeting notes that sit in a list are a commodity.
Meeting notes that feed a task board + agent loop are a moat. The technical
foundation for this (`action_items` table, FTS5, the OS bridge via MCP) is
already laid. You're not starting from zero.

### 5. Technical choices are well-reasoned

- **Qwen 3.6 35B A3B (MoE)** — benchmarked against 6 alternatives on a real
  transcript, not just vibes. MoE means ~3B active parameters, fast latency,
  fits on consumer hardware.
- **SQLite + JSON columns** — correct pushback against the prototype's in-memory
  array. FTS5 search is already wired.
- **Dual capture** (system audio + mic) with speaker labeling — the right
  architecture for meeting notes, and harder than it looks.
- **Prompt templates as first-class editable files** — not hardcoded. Users can
  add their own.
- **PBKDF2 for PIN-based privacy lock** — correct crypto choice for a UI gate.

### 6. You're actually shipping

DMG builds, version bumps, a CHANGELOG, signed artifacts, code-signed with a
stable identity so macOS permissions survive reinstalls. This is real packaging
work, not a dev-only toy.

---

## Cons — What Needs Work

### 1. "Sovereign-first" limits your TAM severely

Your STRATEGY.md says: *"Demand is a compliance wedge, not a consumer one."*
This is honest. But it means your initial addressable market is organizations
that (a) have compliance requirements barring cloud AI, (b) have the hardware to
run local models, and (c) will pay for software. That's small law firms, defense
contractors, EU-regulated entities. You need to be in the room with these buyers
— and they buy through RFPs, security reviews, and procurement cycles, not
Product Hunt launches.

The strategy is rational but the go-to-market path is long and expensive.

### 2. Hardware requirements are a real barrier

A 35B model (even MoE with ~3B active) + Whisper large-v3 = you need a machine
with a decent GPU. The RTX 5090 dev box is not what most people have. Even on
Apple Silicon, `qwen3.6-35b` + `whisper-large-v3-mlx` together need significant
RAM.

Your BYOK/subscription idea is the right instinct, but:
- **BYOK:** Users bring their own API key. Clever — lets you sell to people who
  want privacy *control* even if they use cloud inference. The Settings already
  has this. But the UX around the cloud warning needs polish.
- **Subscription:** You'd need to proxy LLM calls. This makes YOU the data
  processor, which brings GDPR/HIPAA liability. You'd need infrastructure,
  SOC 2, data processing agreements — the enterprise apparatus STRATEGY.md lists
  as "unglamorous gating work." It's doable but expensive.

### 3. Speaker diarization is the biggest feature gap

Meetily (OSS, Rust, ~12.5k stars) ships speaker diarization — splitting "Them"
into individual speakers. Your STRATEGY.md acknowledges this: *"the biggest
depth gap vs Meetily; legal/clinical buyers need who-said-what."* In a meeting
with 4 people, "Them: ..." for every line is significantly less useful than
named speakers. If a buyer evaluates Adversaria vs Meetily side-by-side, this
will lose you deals.

### 4. The UX, while much improved, is still v0.x

The dark glass aesthetic is good — the reskin was well-executed. But:

- **Chat answers are not streamed** — they arrive as one blob after the LLM
  finishes. Streaming is table stakes for chat UX in 2026.
- **No friendly "LLM server is down" UX** — you get a raw `Connection refused`
  errno. This is in TODO.md and it's a real papercut.
- **Live transcription is a "rolling window" MVP** — 12-30s latency, system
  audio only, no stitched transcript. It's a preview, not a real-time feature.
  Competitors do real-time.
- **The floating recording bubble** needed a multi-session debug (JS emit from a
  separate webview doesn't reach a minimized window). It's fixed now but speaks
  to the complexity of cross-window Tauri UX.
- **Sample/placeholder content** in WeeklyView (lorem ipsum) — still in the
  code. It makes the shipped product look unfinished.
- **No onboarding flow** — the intro splash exists, but there's no guided
  first-recording experience.

### 5. The app is complex to set up

You need: the app installed + Python service running + Ollama/Rapid-MLX running
+ model downloaded + ffmpeg on PATH + `HF_HUB_DISABLE_XET=1` on macOS. A
Granola user installs one app and it works. An Adversaria user needs a
LaunchAgent, model downloads, and terminal knowledge. This is fine for a dev
tool; it's a conversion killer for a product.

### 6. No collaborative/team features

Granola, Fireflies, Otter all let you share meeting notes with teammates,
comment, assign action items to others. Adversaria is single-user SQLite. For
the solo practitioner use case this is fine. For the "small law firm" beachhead,
the first question after "is it private?" is "can my paralegal see my notes?"
Currently: no.

### 7. Technical debt is growing

Looking at the raw numbers: `commands.rs` at 1193 lines, `Settings.tsx` at 1098
lines, `storage.rs` at 1078 lines, `NoteViewer.tsx` at 771 lines. These are
getting big and will become harder to change. No Rust tests for the backend
(only Python has 110 tests). The frontend has no E2E tests. The `App.tsx` alone
has 30+ `useState` hooks. This is manageable for a solo dev but a sign to start
decomposing.

---

## Competitive Positioning

Based on STRATEGY.md's own analysis (which is credible) and market research:

| Dimension | Granola | Meetily | Fireflies/Otter | Adversaria |
|-----------|---------|---------|-----------------|------------|
| **Privacy** | Partial (audio deleted, transcripts to cloud) | Full (local) | None (all cloud) | **Full (local)** |
| **Setup ease** | One-click install | OSS, needs setup | One-click | Complex (LLM server + model) |
| **Speaker diarization** | Yes | **Yes** | Yes | **No** |
| **Real-time transcription** | Yes | No | Yes | MVP preview only |
| **Task board / kanban** | No | No | Limited | **Foundation built** |
| **Cross-meeting RAG** | No | No | Some | **Yes (FTS5)** |
| **Price** | Free (funded) | Free (OSS) | Freemium → $10-30/mo | Free (currently) |
| **Platform** | macOS | Cross-platform | Web + apps | Windows + macOS |
| **Collaboration** | Yes | No | Yes | No |

**Your differentiation is real but narrow.** If you match on diarization (even
feature-flagged), improve onboarding, and ship the Kanban board, you have a
genuinely differentiated product for the compliance niche.

### Key competitors to watch

- **Granola** — $1.5B valuation, best-in-class UX, macOS-only. Sends transcripts
  to cloud AI. Your privacy story beats them for regulated buyers, but their UX
  and setup ease beat you for everyone else.
- **Meetily** — OSS, Rust, ~12.5k GitHub stars. "#1 self-hosted Granola
  alternative." Ships speaker diarization you lack. Your strategy and agentic
  vision beat them; their feature completeness beats you today.
- **Fireflies.ai / Otter.ai** — Cloud-native, bot-joins-call model. Dominant in
  enterprise. Privacy-conscious buyers are actively leaving them (lawsuits are
  tailwinds for you).
- **MS Copilot / Zoom AI Companion** — Bundled, free, massive distribution.
  Cannot be fully sovereign — this is the axis you beat them on.

---

## Tiering Strategy (refined from STRATEGY.md)

| Tier | Purpose | Recommendation |
|------|---------|----------------|
| **Free / OSS (Adversaria)** | Distribution, trust, beachhead vs Hyprnote/Meetily | Not a revenue line — accept it. Publish to Homebrew/WinGet. |
| **BYOK (free feature)** | Users bring their own API key | Zero operational cost, zero liability. Expands user base to people who want privacy *control* without local hardware. Ship this now. |
| **Pro (prosumer ~$10-15/mo)** | Individuals | The knife-fight tier (vs free OSS + free bundles). Deprioritize until enterprise tier is proven. |
| **Sovereign / Enterprise self-hosted** | Regulated orgs | **THE business.** High-ACV, quote-based, compliance-grade (SSO, audit logs, BAA, on-prem). Defensible money. |
| **Adversaria Cloud (future)** | Managed inference with client-side encryption | Subscription play for teams that want privacy without hardware. Higher margin, higher liability. Only build after enterprise tier has paying customers. |

---

## BYOK vs Subscription — Recommendation

**Start with BYOK (free).** Let users bring their own OpenAI/Anthropic/DeepSeek/
Grok API keys. You already have the Settings UI for this. It's zero operational
cost, zero liability, and expands your user base. Ship it as a free feature —
it's a distribution play.

**Wait on subscription.** A managed inference tier means you become the data
processor. You need:
- GPU infrastructure or API reselling
- SOC 2 / ISO 27001 (enterprise buyers require it)
- Data processing agreements (GDPR)
- BAA (HIPAA, if healthcare)
- Support burden

The brand tension of "we're private" while you process their data is real.
Don't build the subscription infrastructure before you have paying users asking
for it.

**The hybrid path:** Ship BYOK now. If a company says "we love Adversaria but
don't want to manage API keys," offer them a managed deployment (you run the
infra on their behalf, in their cloud tenant or yours, under a DPA). This is
enterprise sales, not self-serve SaaS, and the pricing should reflect that.

---

## Suggested Features & Improvements (ordered by impact)

### Immediate (next 2-4 weeks)

1. **Streaming chat responses.** Token-by-token streaming in MeetingChat. Every
   competitor does this; its absence makes the app feel slow even when the model
   is fast. The `summarizer.py` async infrastructure is already in place.

2. **Friendly LLM-down UX.** Instead of `Connection refused`, show a banner:
   "Your LLM server isn't running. Start it with: `rapid-mlx serve qwen3.6-35b
   --port 8000`" with a copy button. This one change makes the difference
   between "this app is broken" and "I need to start my server."

3. **Remove sample/placeholder content.** The lorem ipsum in WeeklyView
   undermines credibility. Ship empty states that are honest: "No meetings this
   week yet. Record one to see your recap."

4. **One-click BYOK onboarding.** Add a "Test connection" button next to each
   provider in Settings that calls `/v1/models` and shows a green check or
   specific error.

### Short-term (next 1-3 months)

5. **Speaker diarization (even basic).** This is the #1 competitive gap. Even a
   simple implementation (WhisperX-style timestamp alignment + clustering) would
   close the gap with Meetily. Ship it behind a feature flag if it's
   compute-heavy.

6. **Guided onboarding.** First-launch wizard: "Welcome to Adversaria. Let's
   get you set up." → Check LLM server → Download model if needed → Test
   recording → Show first note. This converts "complex setup" into "guided
   experience."

7. **The Kanban board (your 10× workflow).** The data foundation is already in
   the `action_items` table. Build a proper board view with columns (To Do / In
   Progress / Done), drag-and-drop, and auto-population from meetings. This is
   what STRATEGY.md calls "the thing nobody else can do."

8. **One-click installer that includes the LLM.** Investigate bundling a
   quantized model (e.g., `qwen3.6-8b-Q4_K_M`) directly in the installer so a
   first-time user gets a working app with zero terminal commands. Even a
   smaller model that's "good enough" for meeting notes beats "install Ollama,
   pull model, configure LaunchAgent."

### Medium-term (3-6 months)

9. **Multi-user / team sharing.** For the law firm beachhead: shared meeting
   libraries, per-user action items, role-based access. Could start simple — a
   shared SQLite on a network drive with file locking.

10. **Calendar-driven pre-meeting prep.** You already have calendar integration
    (Google OAuth + macOS EventKit). Before a meeting starts, show: "Up next:
    Client call with Acme Corp (3 attendees from calendar). Last meeting notes:
    [link]. Suggested prep questions: [...]" This is a feature Granola doesn't
    do well.

11. **Hybrid mode (local transcription + cloud summary).** Let users keep
    transcription local (privacy-sensitive audio) but optionally use a cloud LLM
    for summarization. This addresses the hardware barrier — you can run Whisper
    on-device but offload the 35B model to the cloud.

12. **Mobile companion app.** Not full recording — a read-only view of today's
    action items and meeting summaries. The MCP server already exposes the data.
    A simple iOS/Android app that reads from the desktop SQLite via a local sync
    would be a differentiator.

### Strategic

13. **Publish to Homebrew / WinGet.** `brew install adversaria` is the OSS
    distribution play. Your STRATEGY.md says "Free/OSS = distribution, trust,
    beachhead." Make it one command to install.

14. **Build case studies in the compliance niche.** One law firm, one healthcare
    practice, one EU government agency — real users with real compliance needs.
    Their testimonials are your enterprise sales collateral.

15. **Consider "Adversaria Cloud" for teams that want privacy WITHOUT hardware.**
    Architecture: client-side encryption before transit, server-side processing
    in a sovereign cloud (EU DC), zero retention of audio. It's not "nothing
    leaves the machine" — it's "nothing leaves your control."

---

## The Strategic Fork

You're at a decision point:

**Path A — polish Adversaria into a product.**
Priority: onboarding, diarization, Kanban board, BYOK, Homebrew. Target:
individual professionals who want privacy + the compliance niche. Revenue:
enterprise self-hosted deals. This path competes with Granola/Meetily head-on.

**Path B — keep Adversaria as the capture organ of lagharilabs OS.**
Priority: MCP server, OS integration, the agent loop. Target: the full
lagharilabs OS user. Revenue: OS licensing/enterprise. This path makes
Adversaria a component, not a standalone product.

Both are valid. But they have different priorities, and trying to do both at
once will dilute both. Pick one and commit.

---

## Bottom Line

Adversaria is a **genuinely good piece of engineering** with a **clear strategic
thesis** and a **narrow but real wedge** (compliance-grade privacy). The biggest
risks are:

1. The hardware barrier limiting adoption
2. Speaker diarization being missing vs. Meetily
3. Onboarding complexity
4. The long enterprise sales cycle for the compliance niche

The path from "impressive dev project" to "real product" runs through: make it
install in one click, make the first recording magical, close the diarization
gap, ship the Kanban board, and let people use their own API keys. Everything
else is optimization.

---

*Last updated: 2026-06-24*
