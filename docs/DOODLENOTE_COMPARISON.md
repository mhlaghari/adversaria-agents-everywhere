# DoodleNote comparison: who is who, who is better, what we lack

_Research completed 2026-09-03 (three agents: a Claude web-research pass over
the live site, the public repo, the update feed and GitHub API; an Antigravity
worker doing the same independently; a third Claude pass fact-checking the
first two against live sources). Every claim below was seen in a primary source
by at least two of the three passes unless marked "single-source" or
"unverified". Written in answer to Hamza's question: "assess this app, tell me
which one is mine versus theirs, which one is better, what does our app lack
that they have."_

_Correction 2026-09-03 (evening): the first pass listed our MCP server as
missing because the inventory searched only this repo. `adversaria-mcp` was
extracted to its own repo on 2026-06-24 and is live on PyPI (0.2.0). Fixed below._

## Which one is which

| | **Adversaria (ours)** | **DoodleNote (theirs)** |
|---|---|---|
| Maker | Laghari Labs (Hamza), lagharilabs.com/adversaria | Onyx Dev Labs, Fort Worth TX (Sean Inman, MSP owner + CISSP, ~94% of commits; Alec Tribble). One dev plus Cursor agents. No funding disclosed. |
| Pitch | Privacy-first, bot-free, on-device notetaker | "AI meeting notes without the bot. Nothing leaves your computer." Same pitch, near word-for-word. |
| Born | Repo history back to mid-2026, MIT through v0.3.68, ELv2 since | Repo created 2026-07-04, v0.1.0 on 2026-07-05, domain registered 2026-07-07 |
| Today | Public 0.3.82; 0.3.83 built and notarized, unpublished; master carries Live Copilot + exports beyond that | v0.4.18 (2026-09-01). 29 shipped versions in eight weeks (GitHub Releases only from v0.4.17). |
| Stack | Tauri + Rust + React, Python FastAPI ML sidecar; MLX Whisper / faster-whisper; Rapid-MLX or Ollama | Electron 44 + React 19 + TipTap; Swift sidecar running NVIDIA Parakeet via FluidAudio on the Neural Engine; sherpa-onnx zipformer on Windows; node-llama-cpp GGUF for notes; Next.js + Vercel + Neon for sync |
| License / repo | Source-available (Elastic License 2.0); mirror github.com/LaghariLabs/adversaria, master not yet synced | MIT; github.com/Onyx-Dev-Labs/doodle-note, 89 stars, 12 forks, 2 outside issues (both filed 2026-09-02/03) |
| Business model | Free today, Pro planned (~$15/mo, offline license) | Free forever local app; Sync $10/user/month (multi-device sync, web library, share links, team workspaces), 15-day trial, self-hostable sync server |

## The one-line answer

**Adversaria is the deeper product; DoodleNote is the smoother one.** We win on
everything that needs real ML work (multilingual transcription, diarization,
ten note languages, copilot, grounded follow-ups, graph, insights, encryption).
They win on the boring adoption plumbing we have not shipped: ringing-call
prompt with auto-stop on Mac, Microsoft 365 calendar, a downloadable Windows
build, a rich-text editor, in-app one-click MCP connect, and a sync/share/team tier.
Their two biggest weaknesses (English-only, no diarization) are exactly our two
loudest strengths, and their own issue tracker is already asking for them
(issue #118, 2026-09-03: Parakeet produced "English-shaped noise" on Danish;
maintainer: "We will include this in our next release").

Neither product has measurable traction yet: DoodleNote has no Hacker News,
Product Hunt or Reddit presence and 89 stars after two months.

## Feature-by-feature

Legend: ✅ has it · 🟡 partial · ❌ missing. "Ours" = master as of `52636c4`.

| Area | Adversaria (ours) | DoodleNote (theirs) |
|---|---|---|
| macOS Apple Silicon | ✅ signed + notarized | ✅ signed + notarized, macOS 14+ |
| Intel Mac | ❌ | ❌ (Neural Engine dependency) |
| Windows | 🟡 code complete, but no public build since 0.3.76; site shows a waitlist | 🟡 beta 0.4.11 (~163 MB NSIS), downloadable, unsigned (SmartScreen); ships via a beta feed while the production updater feed is stale at 0.3.4 |
| iOS / web | ❌ | 🟡 iOS "in development"; web library for Sync users |
| Bot-free dual capture | ✅ Core Audio process tap + cpal mic (no Screen Recording permission) | ✅ Core Audio tap 14.2+ with ScreenCaptureKit fallback, AVAudioEngine mic with Apple Voice Processing echo cancellation |
| Meeting detection | 🟡 Windows only (registry ConsentStore poll); never auto-records; nothing on macOS | ✅ prompt within ~5 s while Zoom / Teams / FaceTime / Slack huddle is ringing, mic-watcher (4 s debounce), **auto-stop 12 s after the meeting app releases the mic + auto-generate notes** |
| Calendar | 🟡 EventKit (macOS) + Google read-only; Microsoft not built | ✅ Microsoft 365 + Google, "Coming up" card, menu-bar countdown, meeting-start prompts |
| Transcription engine | ✅ Whisper (MLX / faster-whisper), Qwen3-ASR, Cohere Transcribe, optional BYOK endpoint | ✅ Parakeet TDT v2 batch + Parakeet Unified streaming (Mac), zipformer (Windows) |
| Languages | ✅ Whisper multilingual, Qwen3-ASR 52, Cohere 14 | ❌ **English only in the shipped app** (v3 multilingual compiled but not exposed; PR #117 open) |
| Live transcript | ✅ two-tier (Moonshine preview ~0.5 s, Whisper confirmed) | ✅ streaming partials per channel (transcript panel closed by default, not marketed) |
| Speaker labels | ✅ Me/Them + anonymous diarization of the remote side (Speaker 1/2, sherpa-onnx); rename propagates | 🟡 You/Them only; **no diarization**, all remote participants collapse into "Them"; rename once propagates |
| Custom vocabulary / word fix | ✅ initial_prompt vocabulary, "Fix this word" | ❌ none found |
| Local LLM | ✅ Rapid-MLX (Mac) / Ollama (Win), RAM-sized recommendation | ✅ node-llama-cpp in-process; catalog Fast Qwen3 4B / Balanced Llama 3.1 8B / Quality Gemma 3 12B, sized to RAM |
| BYOK cloud | ✅ opt-in, labelled: local / grok / openrouter / custom | ✅ OpenAI, Anthropic, Groq, OpenRouter, Ollama |
| Note languages | ✅ 10 + "Match spoken", RTL | ❌ English |
| Templates | ✅ 8 shipped + user-created + auto-routing by meeting type | 🟡 7 shipped (General, Customer discovery, Site survey, Troubleshooting, 1:1, Standup, Interview); **no custom prompts** |
| Long meetings | ✅ num_ctx computed at runtime | ✅ map-reduce over ~40 min |
| Granola-style merge of own notes | ✅ typed notes steer summary, "From Your Notes" section, "Context used" strip | ✅ rough jottings merged with transcript |
| Notes editor | 🟡 plain textarea + editable markdown | ✅ **TipTap rich text**: images, formatting toolbar, persistent to-do checkboxes |
| Chat with meeting / across meetings | ✅ local LLM over FTS5; bge-m3 embeddings for copilot | ✅ per-meeting Ask + Home "Ask anything" with citations; 🟡 cross-meeting is 20k-char stuffing of recent notes, no embeddings |
| Live in-meeting copilot | ✅ slices A+B: "Last time" brief + own passages on detected questions, no model | ❌ |
| Follow-up / action items | ✅ triage board, digests, grounded "Follow-up from <meeting>" (Done only on verbatim quote) | 🟡 checkbox action items with owners; no follow-up tracking, no "last time" context |
| Related meetings / weekly briefing / knowledge graph / speaking insights | ✅ all four | ❌ |
| Folders / tags / search | ✅ folders, tags, heatmap, @person, archive, PIN lock | ✅ folders ("Spaces"), trash, quick notes, full-text search; tags unverified; no people view |
| Audio after the meeting | 🟡 deleted after transcription (by design); failed ones kept | ✅ kept locally as m4a, click-to-seek playback, re-transcribe from recording |
| Audio / video import | ✅ audio files | ✅ wav / mp3 / m4a **and MP4** |
| Crash recovery | ✅ encrypted chunk spool | ✅ ~30 s checkpoint chunks stitched on relaunch |
| Exports | ✅ Markdown, themed HTML deck + PDF via print, `.adversaria` portable doc, whole-folder export, backup/restore | 🟡 Markdown, PDF (Electron print) |
| Obsidian | ✅ vault sync incl. person profiles | ❌ |
| MCP server for Claude / Codex | ✅ `adversaria-mcp` 0.2.0 on PyPI (`uvx adversaria-mcp`, MIT, github.com/LaghariLabs/adversaria-mcp): 4 read tools + `start_task` / `complete_task` write-back; separate install, no in-app connect button | ✅ bundled read-only MCP (5 tools) with one-click connect in Settings for Claude Desktop / Claude Code / Codex, plus hosted MCP for Sync users |
| Sync / web library / share links / team workspaces | ❌ | ✅ (paid $10 tier) |
| Notion / Slack / Zapier / CRM / email send | ❌ | ❌ |
| Encryption at rest | ✅ SQLCipher DB, keychain keys, Touch ID, per-meeting PIN | ❌ none found (plain JSON + m4a in userData); Sync is TLS-only, no E2E |
| Telemetry | ✅ none | ✅ none found; updater polls with autoDownload |
| Onboarding | ✅ guided; multi-GB model download; ffmpeg from PATH still required | ✅ first-run wizard (permissions, engine, model); ~440 MB Parakeet + 2.4 to 7.3 GB GGUF |
| Installer size | Tauri binary (small) + models | ~188 MB DMG + models |
| Auto-update | ✅ Tauri updater, beta channel | ✅ electron-updater (Mac feed current; Windows feed stale) |
| Themes / tray / pill | ✅ 6 themes, tray hotkeys, floating notch pill | 🟡 dark mode; menu-bar indicator is an open PR |
| Release cadence | ~weekly | 29 versions in 8 weeks, ten on one day |

## What we lack that they have (ordered by how much it changes daily use)

1. **Ringing-call prompt + auto-stop on macOS.** They offer to record within
   about 5 s of Zoom / Teams / FaceTime / Slack huddle ringing, then stop and
   generate notes when the call ends. We detect on Windows only and never stop
   on our own. This is the single largest gap in the "it just works" feeling.
2. **Microsoft 365 calendar.** `docs/SPEC_CALENDAR.md` exists; not built.
3. **A downloadable Windows build.** Theirs is an unsigned beta with a stale
   updater feed, and they still ship it. Our code is complete and unshipped.
4. **Rich-text notes editor** (TipTap: images, toolbar, checkbox state that
   survives reopen). Ours is a textarea plus rendered markdown.
5. **In-app one-click MCP connect.** Both ship an MCP server, and ours does
   more (agents can take and report back action items). Theirs is bundled in
   the app with a connect button in Settings; ours is a separate `uvx` install
   the user wires up by hand.
6. **Sync, web library, share links, team workspaces.** Their entire revenue
   line. Our docs already list team sharing as a known gap.
7. **Keep the audio and seek it.** Local playback with click-to-jump and
   re-transcribe. Our delete-after-transcribe is a privacy choice, but an
   opt-in "keep this recording" would close it.
8. **MP4 import.**
9. **Echo cancellation on the mic** (Apple Voice Processing I/O) for
   no-headphones calls. Unknown whether cpal path does this; worth checking.
10. **Model catalog UX**: three named tiers with RAM minimums. We recommend one
    model; parity in substance, theirs is easier to explain.

## What we have that they lack

- Multilingual transcription (their users are already asking, issue #118).
- Speaker diarization on the remote channel.
- Notes in 10 languages with RTL.
- Custom templates and automatic template routing.
- Live Copilot (Last time + passages), grounded follow-up check, Related
  meetings, Weekly briefing, Knowledge graph, Meeting insights.
- Encryption at rest, Touch ID, per-meeting PIN; audio never retained.
- Obsidian sync, `.adversaria` portable document, themed deck export,
  backup/restore, 6 themes, floating pill, vocabulary + Fix this word.
- Embedding-based retrieval (bge-m3) rather than 20k-character stuffing.
- MCP task write-back: `start_task` / `complete_task` let an agent work our
  action items and report back for approval. Theirs is read-only.
- A Tauri/Rust footprint instead of Electron.

## Threat assessment

- **Positioning overlap: high.** Same tagline logic, same free-local model,
  same Mac + Windows target, both open-ish source. A buyer comparing the two
  landing pages will not see a difference in pitch.
- **Execution risk to us: moderate.** One developer with Cursor agents shipping
  every 1 to 3 days, MIT, and a working sync tier. Electron and English-only
  are structural; the rest is velocity.
- **Where they will catch up next:** multilingual (they said "next release"),
  menu-bar indicator (PR #119), transcript import (#116).
- **Where they are unlikely to catch up:** diarization, encryption at rest,
  the copilot / memory layer, non-English notes.

## Recommendations (founder decisions, not started)

1. Ship the macOS ringing-call prompt with auto-stop before any other new
   feature; it is the one thing they have that changes every single meeting.
2. Publish the Windows beta as-is with a SmartScreen note, the way they do.
3. Build Microsoft 365 calendar from `docs/SPEC_CALENDAR.md`.
4. Surface the existing `adversaria-mcp` server inside the app: a Settings row
   that writes the `uvx adversaria-mcp` entry for Claude Desktop, Claude Code
   and Codex, and a line on the landing page. The server already exists and
   does more than theirs.
5. Put "52 languages" and "who said what" on the landing page above the fold;
   their tracker proves the demand.
6. Decide the sync question consciously: their $10 Sync tier is the revenue
   model we said we would not build until enterprise proved out
   (`docs/marketing_strategy.md`). Keep that decision, but say so.

## Sources

- Site: https://www.doodlenote.ai/ , /pricing , /privacy (effective
  2026-08-31), /changelog , /terms , /download/mac , /download/win
- Update feeds: https://www.doodlenote.ai/updates/latest-mac.yml (0.4.18,
  2026-09-01, DMG 187.9 MB), /updates/latest-beta.yml (Windows beta 0.4.11,
  162.9 MB, 2026-08-03), /updates/latest.yml (Windows production, stale at 0.3.4)
- Repo: https://github.com/Onyx-Dev-Labs/doodle-note (README, engine/README.md,
  apps/desktop/package.json, packages/ai/src/{catalog,templates,cloud-engine,
  global-ask-prompt}.ts, packages/doodle-note-mcp/README.md, SELF-HOSTING.md,
  SECURITY.md, TRADEMARK.md); issues #116, #118; PRs #117, #119
- Company: https://www.onyxdev.io/ , https://seaninman.com
- Our side: `SPEC.md`, `STATUS.md`, `docs/HANDOFF.md`, `docs/ARCHITECTURE.md`,
  `docs/marketing_strategy.md`, `docs/MEETILY_COMPARISON.md`, `README.md`
- Full agent dossiers were kept in the session scratchpad only; this document
  is the durable record.
