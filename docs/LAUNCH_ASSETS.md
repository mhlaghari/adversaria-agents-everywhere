# Launch assets — canonical copy + inventory

_Everything needed to submit Adversaria anywhere, written once so it isn't
rewritten per channel. **Paste from here.** Strategy lives in
[LAUNCH_PLAN.md](./LAUNCH_PLAN.md) (channel ranking, risks, timing); this file is
the raw material._

**Last updated: 2026-07-25 · describes v0.3.64**

> ⚠️ **Only the user can submit.** Product Hunt requires the maker's own account,
> HN bans domains for submissions that look manufactured, and directories need
> real accounts. An agent writes the copy; the user posts it.

---

## 1. The one-liner ladder

Reuse these verbatim; most directories ask for one of these four lengths.

**Tagline (≤60 chars)**
> Meeting notes that organize themselves, on your Mac

**Short (≤160 chars)**
> A free, open-source meeting notetaker that runs entirely on your Mac. No bot
> joins the call, nothing is uploaded, and your meetings become searchable.

**Medium (~300 chars)**
> Adversaria records, transcribes, and summarizes meetings entirely on your own
> machine — no bot joins the call and nothing is uploaded. It then does the part
> other tools skip: compiles every action item onto one board, writes your week,
> and builds a searchable graph of the people and topics across your history.
> Free and MIT licensed.

**Long (~1000 chars)** — see §2.

---

## 2. The standalone one-pager

**Adversaria — meeting notes that organize themselves**
Free · MIT · macOS (Apple Silicon) · Windows in progress
Download: https://github.com/LaghariLabs/adversaria-releases/releases/latest
Source: https://github.com/LaghariLabs/adversaria
Site: https://lagharilabs.com/adversaria

**The problem.** Meeting notetakers are good at capture and bad at what comes
after. You record, you get a clean transcript and a tidy summary, and it joins
the hundred before it. Three weeks later you're hunting for a decision you know
someone made, in a meeting you can't name, on a date you don't remember.

**What it does.**
- **Records without a bot.** Captures the audio your Mac already plays and the
  mic it already hears, as two separate streams, so it always knows who spoke.
  The recording is deleted once it's transcribed.
- **Transcribes and summarizes on your own hardware.** Whisper on your GPU, a
  local model for the notes. Works with the network off.
- **Compiles every action item** from every meeting onto one board — overdue /
  this week / later, with owners and due dates.
- **Writes your week** — decisions made, open loops carried forward.
- **Builds a knowledge graph** of every meeting, person and topic; attendees are
  captured automatically and a person's role and company are filled in from what
  was said out loud.
- **Answers questions across your whole history**, with the meetings it drew from.
- **Exports** to slides, Markdown (Obsidian-ready with wikilinks), or a portable
  bundle.
- **Speaks MCP** — a separate read-only server lets Claude, Claude Code, or any
  MCP client query your meetings, still locally.

**Why it's different.** Cloud notetakers either put a bot in your call or ship
your transcript to a model provider. Adversaria has no server. And where most
tools stop at the summary, this one treats the summary as the input — the
organization layer is the product.

**Honest limits.** macOS Apple Silicon only today. First run downloads ~3.5 GB of
models. A cloud model can be used via your own API key if your machine can't run
one locally — that's opt-in and stated in the UI.

---

## 3. Channel-ready copy

### 3.1 Show HN (the primary channel — see LAUNCH_PLAN.md §7)

_Refreshed 2026-08-17 against v0.3.80 (three engines, Core Audio process tap,
Windows honestly framed as a native rebuild)._

**Title**
> Show HN: Adversaria – On-device meeting notes with no bot and no uploads (MIT)

**Body**
> I got tired of meeting notetakers that record everything and organize nothing,
> so I built one that runs entirely on my Mac.
>
> It captures system audio and the mic as two separate streams (no bot joins
> the call — and no screen-recording permission either: capture is a Core Audio
> process tap), transcribes on-device with your pick of Whisper (MLX), Qwen3-ASR
> (52 languages), or Cohere's speech model, and writes the notes with a local
> LLM. The recording is deleted once transcription succeeds. With the network
> off it behaves identically.
>
> The part I actually cared about is what happens after the summary: it compiles
> action items from every meeting onto one board, writes a weekly briefing, and
> builds a graph of people and topics you can query across your whole history
> (FTS5 + on-device embeddings + graph anchoring, RRF-fused). A separate
> read-only MCP server lets Claude or any MCP client answer from your meetings.
>
> Stack: Tauri/Rust, Core Audio process tap + cpal for capture, MLX Whisper /
> Qwen3-ASR / Cohere for transcription, a managed local LLM runtime (MLX),
> SQLCipher for storage. macOS Apple Silicon today; the Windows build is being
> rebuilt natively (the frozen-Python sidecar kept losing fights with antivirus).
> MIT licensed.
>
> It's the first thing I've shipped notarized and public, so I'd genuinely like
> to hear where the first-run experience breaks.
>
> Source: https://github.com/LaghariLabs/adversaria

**Mechanics:** Tue–Thu, 8–10am PT. Answer every comment fast and technically for
~6 hours. Never solicit upvotes — it's a lifetime domain ban.

### 3.2 Product Hunt

**Name:** Adversaria
**Tagline:** Meeting notes that organize themselves, on your Mac
**Topics:** Productivity · Mac · Open Source · Artificial Intelligence · Privacy

**Description**
> Adversaria records, transcribes, and summarizes your meetings entirely on your
> own machine. No bot joins the call, nothing is uploaded, and the recording is
> deleted the moment it's transcribed. Pick your on-device engine — Whisper,
> Qwen3-ASR (52 languages), or Cohere — and get speaker-labeled transcripts and
> notes in 10 languages.
>
> But local was the floor. The reason I built it is what happens after the
> summary: every action item from every meeting lands on one board, your week
> gets written for you, and a knowledge graph ties together the people and topics
> across your whole history — so you can ask what you decided about pricing and
> get an answer with the meetings it came from.
>
> Free and MIT licensed. macOS (Apple Silicon) today; Windows is being rebuilt
> natively.

**First comment (highest-leverage asset)**
> Hi PH — I'm Hamza, I built this solo.
>
> I kept ending up with months of recorded meetings and no way to find anything
> in them. Every tool is good at capture; almost none of them help afterwards.
> So Adversaria treats the summary as the input, not the output — action items
> compile onto one board, the week writes itself, and everything is searchable
> across your whole history.
>
> It runs on your own machine (your pick of three on-device speech engines, a
> local model for the notes), which also means there's no server to trust. It's
> free and MIT licensed, and there's a read-only MCP server so Claude or Copilot
> can query your meetings without them leaving your Mac.
>
> What I'd most like feedback on: the first-run experience. It downloads a few GB
> of models the first time, and I want to know exactly where that loses people.

### 3.3 Reddit (one subreddit at a time; 10% self-promo rule)

Targets, in order: r/macapps · r/LocalLLaMA · r/selfhosted · r/opensource ·
r/privacy · r/ObsidianMD (lead with Markdown/wikilink export) · r/notetaking.

**Title:** I built a free, open-source meeting notetaker that runs entirely on
your Mac — no bot, no uploads
**Body:** use the one-pager (§2), then add one sub-specific line — for
r/LocalLLaMA name the models; for r/ObsidianMD lead with vault export.

### 3.4 Directory submissions

Use the ladder in §1. Consistent everywhere:
- **Category:** Productivity / Meeting notes / AI assistant
- **Platforms:** macOS (Apple Silicon)
- **Pricing:** Free · open source (MIT)
- **Alternative to:** Granola, Otter, Fireflies (only where the field exists —
  don't editorialize)

Targets: AlternativeTo · SaaSHub · StartupStash · Slant · awesome-privacy-tools ·
PrivacyToolsList · Product Hunt · BetaList · TAAFT · MCP registries (for
`adversaria-mcp`).

---

## 4. Asset inventory — what exists and where

| Asset | Location | State |
|---|---|---|
| Notarized DMG (0.3.64) | releases repo, `latest` | ✅ published |
| Auto-update manifest | `latest-beta.json` on the release | ✅ serving 0.3.64 |
| Demo video (47s, 1080p60) | `marketing/product-demo/renders/` | ✅ rendered; source is `index.html`, re-render after feature changes |
| Carousel (10 slides + PDF) | user's Desktop `adversaria-carousel/` | ✅ built; **not** rebuilt with real screenshots yet |
| Real screenshot (meeting note) | user's Desktop `adversaria-screenshots/` | ✅ 1 of ~4 wanted |
| Org avatar candidates | user's Desktop `laghari-org-avatar/` | ⏳ not uploaded |
| Launch video v2/v3/v4 | `marketing/launch-video*/renders/` | ⚠️ pre-dates the organization-first positioning |
| LinkedIn post | posted 2026-07-25 | ✅ live |

**Missing:** To-dos / Graph / Weekly screenshots (need a *debug* build —
`ADVERSARIA_DATA_DIR` is `#[cfg(debug_assertions)]` only, so a release build
ignores it and will open the user's REAL data. A demo DB is seeded at
`scratchpad/demo-data`). Website feature grid still pre-dates this positioning.

---

## 4b. Submission log — what's already been sent

**Do not re-submit these.** Update this table whenever something is sent.

| Target | State | Link / note |
|---|---|---|
| GitHub topics + homepage (both repos) | ✅ done 07-25 | 18 topics on `adversaria`, 11 on `adversaria-mcp` |
| `punkpeye/awesome-mcp-servers` (91k★) | 🟡 PR open, **needs user** | [#10922](https://github.com/punkpeye/awesome-mcp-servers/pull/10922). Maintainer requires a **Glama score badge** before merge → submit at <https://glama.ai/mcp/servers>, **claim it as owner** (needs the user's account), then the badge gets added to the entry. Dockerfile is already committed and verified |
| `jaywcjlove/awesome-mac` (108k★) | ✅ PR open | [#2408](https://github.com/jaywcjlove/awesome-mac/pull/2408) — Note-taking, alphabetically first |
| `pluja/awesome-privacy` (19k★) | ✅ PR open | [#960](https://github.com/pluja/awesome-privacy/pull/960) — Notes and Tasks. Their checklist requires no third-party trackers; verified the live page loads only lagharilabs.com + a github.com link |
| `tauri-apps/awesome-tauri` (8k★) | ⏳ **blocked** | Good fit (Applications → Productivity) but **requires signed commits**, and no signing key is configured. Needs the user to set up SSH/GPG signing and register it on GitHub |
| `rust-unofficial/awesome-rust` (58k★) | ⏳ **not eligible yet** | Objective bar: **>50 GitHub stars** or >2000 crates.io downloads. Repo had 1 star on 07-25. Revisit after traction |
| MCP Registry | ⏳ blocked on user | `server.json` is committed to the mcp-server repo. Needs `uv publish` (PyPI token) then `mcp-publisher login github` (interactive OAuth) — see that repo's README |
| `modelcontextprotocol/servers` | ❌ **don't submit** | Third-party listings retired; they redirect to the MCP Registry |
| `awesome-selfhosted` (308k★) | ❌ **don't submit** | Scope is self-hostable *network services / web apps*. Adversaria is a desktop app and would be rejected |
| AlternativeTo / SaaSHub / Slant / StartupStash | ⏳ user | Copy in §1 |
| Product Hunt | ⏳ user | Copy in §3.2 |
| Show HN | ⏳ **gated** — see §6 | Copy in §3.1 |
| Reddit | ⏳ user | §3.3 |

---

## 5. Positioning rules (decided 2026-07-25 — don't relitigate)

1. **Lead with organization, not privacy.** "Capture is solved; what happens
   afterward isn't." Privacy is a supporting *flexibility* point, because the app
   genuinely supports a BYOK cloud path and must not over-claim.
2. **Never name or disparage competitors.** No bot-shaming, no Granola/Otter
   digs. The category observation is fine; the sneer is not.
3. **Credit prior art loudly.** Whisper, MLX, Silero, sherpa-onnx, Tauri, Ollama
   — and Meetily, whose VAD constants are used and attributed in `live.py` and
   the CHANGELOG. Stripping that credit is the actually-risky move.
4. **No fabricated proof.** The demo does not recreate the "Wi-Fi off" beat from
   `demo-video/SCRIPT.md`; animating evidence is different from illustrating a UI.
5. **Screenshots must never show real meetings.** Use `marketing/demo-data/`
   (7 synthetic bundles) or a seeded demo DB.

---

## 6. ⚠️ Gate before Show HN

`LAUNCH_PLAN.md` risk P2: a broken first run in front of an HN front page is
unrecoverable, and **the product has had one external tester**. 0.3.61–0.3.64
have never run on a machine other than the developer's, and the 0.3.64
permissions fix has never met a real macOS prompt (this Mac already holds both
grants).

**Gate: ~5 clean first-runs on machines that aren't the developer's.** Directory
submissions and Product Hunt are lower-stakes and can go first; HN is the one
shot.

---

## 7. Legal note (2026-07-25)

The user is a **full-time employee whose contract prohibits outside activity**,
and is UAE-based. No trade licence is needed while nothing is sold, but the
employment clause is live and the project is public under his own name. Options
discussed: seek written permission (recommended), reduce the company framing, or
proceed knowingly.

**RESOLVED 2026-08-17 (founder decision): proceed with the launch push on the
open-source/no-revenue framing.** His words: it's open source, he's not selling
it and making no money; if it catches on he'll quit and go full-time (and set up
properly then). Consequences for all public copy, standing until he quits:
present as a **personal open-source project** ("I built this", free, MIT) — no
"our company sells/offers" framing, no pricing or premium-tier talk in public
(the Workspaces/Teams premium ideas stay private planning). The existing §3
Show HN / PH copy already complies. Do not relitigate the decision; do surface
this note before any *monetization* move (that's the trigger to revisit, per
his own plan).
