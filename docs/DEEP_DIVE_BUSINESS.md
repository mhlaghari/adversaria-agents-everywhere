# Adversaria — Business Deep Dive

> **Product:** Adversaria (formerly "Meeting Note Taker")  
> **Company:** Laghari Labs  
> **Version:** v0.3.14 (committed 2026-07-02)  
> **Platform:** Windows + macOS (Apple Silicon)  
> **Tagline:** *Nothing leaves your machine.*

---

## Table of Contents

1. [What It Is](#1-what-it-is)
2. [Why It Exists — The Problem](#2-why-it-exists--the-problem)
3. [How It Works (Business View)](#3-how-it-works-business-view)
4. [Who It's For — The Market](#4-who-its-for--the-market)
5. [Competitive Landscape](#5-competitive-landscape)
6. [Strategic Positioning & Wedge](#6-strategic-positioning--wedge)
7. [Go-to-Market Strategy](#7-go-to-market-strategy)
8. [The 10× Workflow Vision](#8-the-10×-workflow-vision)
9. [Current Status & Launch Gates](#9-current-status--launch-gates)
10. [Risks & Honest Assessment](#10-risks--honest-assessment)
11. [Roadmap & What's Next](#11-roadmap--whats-next)
12. [Why You Should Care](#12-why-you-should-care)

---

## 1. What It Is

Adversaria is a **privacy-first, bot-free AI meeting notetaker** that runs entirely on your own computer. No bot joins your call. No audio, transcript, or summary is ever uploaded. It listens over your speakers and your microphone — just like a person in the room — and produces structured meeting notes, action items, to-do lists, weekly recaps, and a cross-meeting knowledge graph from everything you've discussed.

The name is Latin — *"a notebook of jottings"* — and it describes exactly what it does: a personal, private, always-on notebook for the meetings in your life.

At its simplest: press a hotkey, have a meeting, stop recording — seconds later you have a speaker-labeled transcript, a structured summary with decisions and action items, and everything saved locally. Audio is deleted immediately after transcription.

---

## 2. Why It Exists — The Problem

### The core insight

Meeting notetakers are not new. Granola, Otter.ai, Fireflies, Fathom — they're well-funded, well-known products. But they all share a fundamental tradeoff: **they ship your meeting data to the cloud.** Fireflies and Otter need a bot in your calendar. Granola deletes your audio but sends your transcript to Anthropic/OpenAI on AWS. Even if you trust them today, your organization's compliance officer, legal counsel, or IT security team may not — and often, they *cannot*.

The market is bifurcated:

- **Consumers/prosumers** say they care about privacy but mostly don't pay for it.
- **Regulated professionals** — lawyers (privilege-waiver risk), healthcare providers (HIPAA, no BAA from Granola), defense contractors (air-gap), EU companies (GDPR sovereignty) — **must** keep their data on-device. They *will* pay for software that lets them.

Adversaria exists to serve the second group — and the strategic bet is that the first group will follow as privacy awareness rises and cloud-AI liability lawsuits become more common.

### The product gap

Before Adversaria, a regulated professional had two choices:
1. **Use a cloud notetaker** (Granola, Otter, Fireflies) — convenient, but your meeting data leaves your machine. For a lawyer, that's a privilege-waiver lawsuit waiting to happen. For a doctor, it's an OCR/HIPAA violation. For a defense contractor, it's a security incident.
2. **Take manual notes** — private, but slow, error-prone, and you miss half the conversation.

Adversaria provides a **third option**: all the convenience of an AI notetaker with none of the data-leakage risk. Your notes stay on your laptop. The AI runs on your laptop. The model downloads to your laptop. **Nothing leaves.**

---

## 3. How It Works (Business View)

### The loop

1. **Record** — Press Ctrl+Shift+M (or the tray menu, or the in-app button) to start. The app captures your system audio (the meeting) *and* your microphone (you) simultaneously — two separate channels. No bot joins the call.
2. **Transcribe** — Stop recording and the app runs on-device speech-to-text using Whisper (OpenAI's open transcription model), accelerated by your GPU (NVIDIA CUDA on Windows, Apple Silicon GPU/MLX on Mac). It separates "Me" (your mic) from "Them" (everyone else) and, when enabled, splits "Them" into individual speakers.
3. **Summarize** — The transcript is sent to a local LLM (Ollama or Rapid-MLX) running on your machine — 35 billion parameters (active ~3B via mixture-of-experts) — which produces a structured summary: title, attendees, key topics, decisions, action items, follow-ups. In Arabic, English, or the meeting's spoken language.
4. **Store & Review** — The meeting (transcript, summary, action items, tags, your personal notes) is saved to an **encrypted-at-rest** SQLite database. Audio files are deleted the moment transcription succeeds. You can re-summarize, chat with the meeting ("what did we decide about X?"), search across all meetings, or export it as a beautiful slide, Markdown, or a portable JSON bundle.
5. **Act** — Action items from every meeting flow into a consolidated **To-dos view** with due dates, assignees, and a Today/Overdue filter. A **Weekly recap** gives you a Mon–Sun digest. The **Knowledge Graph** shows every meeting, person, tag, and action owner as an interactive map. This is the foundation for the killer workflow: every morning, your day's to-dos auto-deploy from yesterday's meetings onto a board — fully local.

### The privacy architecture

| Data | What happens | Where |
|------|-------------|-------|
| Audio (WAV) | Captured → transcribed → **deleted** | Local temp → SQLite recording store |
| Transcript | Stored in encrypted SQLite | Your machine only |
| Summary | Generated locally, stored encrypted | Your machine only |
| Action items | Extracted locally, stored encrypted | Your machine only |
| LLM inference | Runs on your GPU/CPU | Your machine (Ollama / Rapid-MLX) |
| Transcription | Runs on your GPU/CPU | Your machine (Whisper, CUDA/MLX) |
| Cloud opt-in | Never the default; UI-labeled; per-run consent required | Loopback only unless you explicitly turn it on |

**No telemetry. No analytics. No cloud dependency (unless you explicitly opt in via BYOK).**

---

## 4. Who It's For — The Market

### Primary beachhead: Regulated client-facing solos

The **initial paying market** is individual professionals in regulated industries who:

- **Can't use cloud AI** due to compliance, liability, or contract terms
- **Have the hardware** to run local models (Apple Silicon Mac, or a PC with a decent GPU)
- **Take lots of meetings** and need structured notes
- **Will pay** for software that keeps their data sovereign

**Specific personas:**
- **Solo/small-firm lawyers** — privilege-waiver risk from sending transcripts to cloud AI; need who-said-what for depositions, client calls, and court-prep. The billable-hour incentive to capture every meeting is real.
- **Healthcare practitioners** (therapists, clinicians, specialists) — HIPAA restricts sending patient data to third parties. Many use no AI notetaker at all; they'd use one if it stayed on-device.
- **Consultants & fractional executives** — multiple clients, each with different confidentiality boundaries. A single tool that never exfiltrates data is simpler than managing NDAs + Granola + manual notes.
- **EU/sovereign/defense professionals** — GDPR and national security requirements mean cloud AI is simply not an option.

### Secondary funnel: Prosumers & Arabic/RTL users

The **free funnel** is individual professionals who want privacy *control* (even if they're not legally required to have it), plus Arabic/RTL-native speakers who have few good meeting-note options in their language. This group is the distribution engine — they tell their regulated-friend about it.

### Tertiary: The lagharilabs OS bridge

Adversaria is also the **"sovereign capture organ"** of the larger **lagharilabs OS** ecosystem (a separate project: an AI-agentic command center that replaces Copilot/ChatGPT Desktop). In that context, Adversaria provides the meeting-memory layer — the OS ingests meetings via MCP and answers questions across them. The business model for this tier is OS licensing/enterprise, not per-seat SaaS.

---

## 5. Competitive Landscape

| Dimension | Granola | Meetily | Fireflies/Otter | Zoom/MS Copilot | **Adversaria** |
|-----------|---------|---------|----------------|-----------------|----------------|
| **Privacy** | Partial (audio deleted, transcripts to cloud) | **Full (local)** | None (all cloud) | Bundled, cloud | **Full (local)** |
| **Setup ease** | One-click install | OSS, needs setup | One-click signup | Bundled | Depends (on-device needs GPU/LLM; BYOK simpler) |
| **Speaker diarization** | Yes | **Yes** | Yes | Yes | **Implemented (sherpa-onnx, anonymous speaker-N)** |
| **Real-time transcription** | Yes | No | Yes | Yes | MVP rolling preview |
| **Task board / Kanban** | No | No | Limited | No | **Data foundation built** |
| **Cross-meeting RAG (Ask)** | No | No | Some | No | **Yes (FTS5 + structured routing)** |
| **Knowledge Graph** | No | No | No | No | **Yes (from local data, zero LLM)** |
| **Export / Import bundles** | Limited | No | Via API | No | **Yes (`.adversaria.json`, backup-all)** |
| **Encrypted at rest** | No | No | N/A (cloud) | No | **Yes (SQLCipher + OS keychain)** |
| **Arabic / RTL** | No | Partial | No | Partial | **Yes (fully)** |
| **Platform** | macOS only | Cross-platform | Web + apps | Embedded | **Windows + macOS** |
| **Collaboration** | Yes | No | Yes | Yes | No (single-user by design) |
| **Price** | Free (VC-funded) | Free (OSS) | $10-30/mo | Bundled | **Free (launch); Pro later** |
| **Valuation / Traction** | $1.5B | ~12.5k GitHub stars | Public (NASDAQ) | Microsoft/Zoom | Pre-revenue |

### Key differentiators

1. **True local sovereignty** — No one else can truthfully say "nothing leaves your machine" for the full pipeline. Granola sends transcripts to cloud AI. Meetily is local but lacks features, diarization is in C++ (hard to modify), and the product vision is narrower.
2. **The data-integration moat** — The Knowledge Graph, cross-meeting Ask system, action-items database, and future Kanban board form a connected data layer no competitor has. Granola's notes are per-meeting silos. Adversaria's meetings talk to each other.
3. **Arabic/RTL as a first-class feature** — None of the Western competitors handle Arabic properly. This is a real moat in a large, underserved market.
4. **No bot = no calendar spam** — Every cloud competitor requires a bot to join your call or read your calendar. Adversaria listens over your speakers. No bot in your Zoom, no calendar invite from "Fireflies Bot", no embarrassing "your meeting was recorded" notification.

---

## 6. Strategic Positioning & Wedge

### The strategy, in one sentence

> Sell **sovereignty** to regulated professionals who **must** keep data on-device, give it away free to prosumers who care about privacy, and build the moat through the integrated **capture → memory → action loop** that no cloud competitor can match.

### The pricing model

| Tier | Audience | What they get | Price |
|------|----------|---------------|-------|
| **Free (Adversaria)** | Prosumers, Arabic/RTL users, technical evaluators | Full local pipeline, all current features | **$0** |
| **BYOK (free feature)** | Users who have their own API key (Groq/OpenAI/DeepSeek) | Cloud LLM/transcription with their key, their choice | **$0** |
| **Pro (waitlist at launch, switch on ~30-60 days)** | Power users who want features | Kanban board, slide export, Markdown export, priority support | **~$15/mo or $120/yr** via LemonSqueezy + offline Ed25519 license |
| **Sovereign / Enterprise** | Regulated orgs (law firms, healthcare, defense, EU) | Self-hosted, SSO, audit logs, BAA, on-prem deployment, quote-based | **High-ACV** (the real business) |

### Why free-only at launch (decided 2026-06-28)

The founder made a deliberate strategic choice: **launch free-only, no paid gating**. Rationale:
- Building Pro/licensing infra before PMF is validated would waste time building something nobody needs yet.
- The **bottleneck is distribution**, not monetization — get users first.
- Capture Pro intent via a **waitlist** at launch, not a paywall.
- The paid wedge targets **regulated client-facing solos**, not broad prosumers — a narrower, higher-ACV market that needs a different sales motion anyway.
- **Open-source the read-only MCP server** as a trust signal and HN discovery asset.

### The broader play: lagharilabs OS

Adversaria is not just "another meeting notetaker." It is the **sovereign capture organ** of **lagharilabs OS** — the larger AI-agentic command surface. Alone it's a commodity; in the stack it's irreplaceable. The OS already consumes Adversaria's data via a read-only MCP server (standalone, open-source), answering questions like "what did we decide in last week's client call?" from within the OS.

The strategic bet: the integrated **capture → memory → action** loop that runs entirely on the customer's own hardware is the moat, not any single feature.

---

## 7. Go-to-Market Strategy

### Launch channels (prioritized)

1. **Show HN** — the primary launch channel. The narrative writes itself: "I built an AI meeting notetaker that doesn't send your data to the cloud. Nothing leaves your machine. (Open-source the MCP server.)" Privacy-focused launches do well on HN.
2. **r/macapps, r/LocalLLaMA, r/privacy** — niche communities where the sovereignty story resonates.
3. **Beta of 30–50 technical design partners** — before the public spike, recruit from existing sign-ups + the communities above + **3–5 friendly consultants/lawyers** (first compliance design-partner conversations).
4. **Product Hunt "Coming Soon"** — indexed early, launches later.
5. **AlternativeTo, SaaSHub, PrivacyToolsList** — SEO-driven discovery from users searching for "privacy-first meeting notetaker."

### Key messaging

- **Lead:** "Nothing leaves your machine." (Not "no bot" — privacy is the headline, not the feature.)
- **Body:** The Bilzerian/Otter cold-open: Otter shipped a lawsuit magnet, we ship sovereignty. Demo the 60-second install-to-notes flow.
- **Trust:** Cite the public record of competitor lawsuits (Otter class-action, Fireflies data-sharing) as tailwinds. "Designed for confidentiality" — never "HIPAA-approved" or "bar-approved" until those audits exist.

### The four hard launch gates

| # | Gate | Status | Notes |
|---|------|--------|-------|
| 1 | **Notarized, clean-Mac install — zero terminal** | ⛔ **BLOCKED** on Apple Developer enrollment | Self-signed DMG works for devs; Gatekeeper blocks non-devs. Apple enrollment failing with generic error. |
| 2 | **First-run wizard → first summary with zero terminal** | Not built | Groq preset + guided model download for local path. |
| 3 | **Groq long-meeting rate-limit (~6,000 TPM) fails LOUD** | Not built | Silent failure = instant churn on the first long meeting prosumers test. |
| 4 | **Capture-path reliability proven** | Partial | Rust tests on audio/storage boundary are thin. Full QA matrix pending. |

---

## 8. The 10× Workflow Vision

This is the north star, and it's what STRATEGY.md calls "the thing that makes Adversaria not just another notetaker":

> **Every morning, your day's to-dos are auto-deployed from yesterday's meetings + inbox, onto a board — fully local.**

Today, a professional might:
1. Take notes in a meeting (or use Granola)
2. Manually extract action items into a task manager (Todoist, Notion, Asana)
3. Manually follow up
4. Manually prepare for the next meeting by searching through old notes

**With Adversaria's full vision:**
1. Record meeting → transcript + summary + action items auto-extracted
2. Action items flow into a **Kanban board** (To Do / In Progress / Done) with assignees, due dates
3. The **Weekly recap** surfaces everything you committed to, across meetings
4. The **Knowledge Graph** shows who you met with, what was discussed, and what was decided
5. The **Ask system** answers cross-meeting questions: "What did we agree about X in the last month?"

The **data foundation is already built**: action_items table in encrypted SQLite, FTS5 full-text search, structured summary extraction, weekly rollup, cross-meeting intent routing. The missing piece is the Kanban UI — which is the user's stated #1 priority.

---

## 9. Current Status & Launch Gates

### What's shipped (v0.3.14, 2026-07-02)

Nearly everything in the original product spec is **built and verified**:

- ✅ Core record → transcribe → summarize → store loop (GPU accelerated, dual-channel)
- ✅ Speaker-labeled transcripts (Me/Them + anonymous Speaker-N diarization)
- ✅ Structured summary cards (collapsible, action-item checkboxes, Arabic RTL)
- ✅ Re-summarize with different templates
- ✅ Chat with a meeting (grounded Q&A, persisted history, streaming)
- ✅ Cross-meeting Ask (FTS5 retrieval, intent-routed to summaries/todos/transcripts)
- ✅ Action items table (DB-backed, assignees, due dates, Today/Overdue filters)
- ✅ Weekly recap (Mon–Sun digest)
- ✅ Knowledge Graph (interactive cytoscape.js graph from SQLite, zero LLM)
- ✅ Export/Import bundles + backup-all/restore
- ✅ Beautiful slide export (dark "Meeting Minutes" HTML → one-page PDF)
- ✅ Markdown export, audio-file import (iPhone voice memos → notes)
- ✅ Colorful per-meeting tags + tag editing
- ✅ Meeting search (SQLite FTS5)
- ✅ Pin, delete, privacy lock (per-meeting PIN + Touch ID)
- ✅ Editable summaries, editable prompt templates
- ✅ Custom vocabulary + personal name (biases Whisper spelling)
- ✅ Auto-detect meetings (mic-based, off by default)
- ✅ Arabic / multilingual summaries with full RTL rendering
- ✅ Floating recording bubble (with audio-reactive waveform)
- ✅ Back-to-back recording queue (record while previous transcribes)
- ✅ Data-loss protection (audio kept on failure, retryable)
- ✅ Encryption-at-rest (SQLCipher, 256-bit key in OS keychain)
- ✅ macOS port (ScreenCaptureKit + cpal, MLX, fully featured)
- ✅ Opt-in cloud LLM provider (Groq, DeepSeek, OpenRouter, any OpenAI-compatible)
- ✅ Tauri v2 auto-updater (minisign-verified, round-trip tested)
- ✅ Reskinned UI (dark-glass theme, self-hosted Inter font)
- ✅ .dmg packaging (one-command build, bundled sidecar, auto-install)
- ✅ LLM provider → model auto-match, BYOK "Test connection" button
- ✅ Signed release builds with stable identity (TCC grants survive reinstalls)

### What's NOT yet shipped (launch blockers or planned)

- 🔴 **macOS notarization** — blocked on Apple Developer enrollment (generic "could not be completed at this time" error). Self-signed DMG works for technical users. Without notarization, non-developer friends can't install without terminal.
- 🔴 **First-run wizard** — guided setup from zero to first summary. Especially important for users who want local mode (model download) or cloud mode (Groq key entry).
- 🔴 **Groq rate-limit handling** — free Groq tier limits at ~6,000 TPM; long meetings will hit this. Must fail loudly, not silently.
- 🟠 **Kanban board** — the user's #1 requested feature. Data foundation is built; UI pending.
- 🟠 **Microsoft calendar** (Google OAuth done, EventKit done, Microsoft is the next provider)
- 🟡 **One-click installer bundling a quantized model** — so first-time users need zero terminal
- 🟡 **Homebrew/WinGet distribution**
- 🟡 **Multi-user / team sharing** (for the law-firm beachhead)
- 🟡 **Hybrid mode** (local transcription + cloud summary opt-in)

---

## 10. Risks & Honest Assessment

This section is deliberately candid. From the strategy docs.

### Working

- **Core loop is real and mature** on both Windows and macOS. The engineering is ahead of distribution.
- **Privacy story is genuinely defensible** — audio deleted, SQLCipher-encrypted DB, no telemetry, local AI. This is not marketing fluff; it's verified in the code.
- **Documentation discipline is exceptional** — a new engineer could onboard in hours. Most solo-dev projects have zero.
- **Shipping velocity is high** — from first commit to v0.3.14 in ~3 weeks, with dozens of verified features, a cross-platform port, packaging, encryption, diarization, export/import, and a knowledge graph.

### Not working / risk

1. **Distribution is zero.** The product has no users outside the founder. All the engineering excellence means nothing until people install it. The notarization block is the single biggest risk.

2. **Bus factor = 1.** One person across two repos (Adversaria + lagharilabs OS), multiple sidecars, platform-specific audio stacks, a Python ML service with multiple backends, a Rust frontend backend, React UI, packaging scripts, MCP server. Any extended outage of the founder stops everything.

3. **Hardware requirements are a real adoption barrier.** Whisper large-v3 + Qwen3.6-35B need significant RAM/VRAM. A MacBook Air with 8 GB won't run the local pipeline smoothly. The BYOK cloud-LLM path mitigates this, but the out-of-box experience is "you need a powerful computer."

4. **Setup complexity.** Even on a good machine: install app → ensure Python service runs → ensure Ollama/Rapid-MLX runs → download model → set `HF_HUB_DISABLE_XET=1` on macOS. A Granola user installs one app and it works. Every abstraction layer you ask a user to understand is a conversion loss.

5. **"Sovereign-first" limits TAM.** The honest strategy admits that the initial addressable market is organizations with compliance requirements AND capable hardware AND budget. That's a small, long-sales-cycle niche. The product needs to find and convert these buyers efficiently.

6. **Reliability at autonomy risk.** One bad autonomous action (deleting data, shipping a broken freeze) destroys the trust that the entire product rests on. The compliance pitch works *only if the product is flawless*.

7. **Sovereign ↔ autonomy tension.** Local models (35B MoE at Q4) are nowhere near GPT-5 or Claude Opus 4.8 capability. The more agentic the product becomes, the more it strains against the on-device model ceiling. Cloud fallback via BYOK is a partial answer but reintroduces the data-sovereignty question.

---

## 11. Roadmap & What's Next

### Immediate (before public launch)

1. **Unblock Apple Developer enrollment** (phone callback, address/card on Apple ID, try cellular enrollment)
2. **Notarized DMG** — the single gate that unlocks non-technical testers
3. **First-run wizard** — Groq preset → test → first summary in 2 clicks
4. **Loud Groq rate-limit failure UX** — don't let the free tier's constraint become a death, make it a clear upsell or workaround
5. **Kanban board** — the 10× workflow the user asked for first

### Short-term (post-launch)

6. **Speaker diarization quality improvements** — the biggest competitive gap vs Meetily
7. **Microsoft calendar integration** (Google + EventKit done)
8. **Drag-drop action items → calendar** — close the loop between notes and schedule
9. **Publish to Homebrew** — one-command install

### Medium-term (3–6 months)

10. **Multi-user / team sharing** — shared meeting libraries for the law-firm beachhead
11. **Calendar-driven pre-meeting prep** — "Up next: Client call. Last meeting notes: [link]. Suggested prep: [...]"
12. **Hybrid mode** (local transcription + cloud summary opt-in) — bridges the hardware gap
13. **Mobile read-only companion** (today's action items, meeting summaries, via MCP)

### Strategic

14. **OSE the MCP server** (already decided, already standalone) — distribution + trust play
15. **Build 2–3 compliance case studies** (one law firm, one healthcare, one EU agency) — the sales collateral the enterprise tier needs
16. **Open beta of 30–50 users** on the auto-updater channel before the public spike

---

## 12. Why You Should Care

### If you're a regulated professional (law / healthcare / defense / EU)

You have a problem that has no good solution today. You either use cloud AI and hope nobody audits you, or you take manual notes and miss half your meetings. Adversaria is the first product that solves this honestly: **your data never leaves your machine**, the AI runs on-device, and the output is genuinely useful. It's not a compliance checkbox — it's a better way to work.

### If you're a prosumer who cares about privacy

You shouldn't have to choose between privacy and productivity. Adversaria gives you both — and it's free. The local pipeline is genuinely impressive: a 35B-parameter LLM running on your laptop, producing summaries that compete with cloud services. Plus it handles Arabic natively, which almost nothing else does.

### If you're an investor

The compliance-AI market is real and growing. Otter.ai faces a class-action lawsuit over data privacy. Granola ships transcripts to the cloud. Regulated professionals are actively looking for alternatives — and they have budget. Adversaria's engineering is ahead of its distribution, and the founder has shown extraordinary shipping velocity (production-grade product in <3 weeks). The capital need is relatively modest: notarization ($99/yr + time), cloud inference credits for the BYOK path, and Go-to-market execution. The risk is not technical — it's sales and distribution.

### If you're an engineer

The architecture is genuinely clean. Three layers (React → Rust/Tauri → Python/ML) with clear contracts, proper platform isolation, real testing discipline, and documentation that is, frankly, unreasonably good for a solo project. The Knowledge Graph, export/import bundle system, streaming-chat pipeline, and SQLCipher integration are production-quality work. This is what engineering looks like when you build for the long term from day one.

---

*Written 2026-07-02 · Based on codebase v0.3.14 · Companion: [DEEP_DIVE_TECHNICAL.md](./DEEP_DIVE_TECHNICAL.md)*
