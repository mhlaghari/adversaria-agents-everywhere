# Live Copilot — design spec (2026-09-02, v1.2; latency numbers MEASURED on the founder's Mac by the Antigravity/Gemini 3.8 Flash probe, `.recon/recon-agy-copilot-latency.md`)

**In one sentence:** while you record, when the other party asks something, a rail beside the transcript shows your own material first (instant, deterministic), then a short Claude answer whose every bullet is labeled *your notes* / *Claude* / *web*, behind one consent toggle that shows exactly what leaves the machine; with the toggle off the rail still shows what happened in previous meetings.

Owner: founder + Claude. Status: spec v1, build not started. Recon in git-excluded `.recon/`: `recon-agy-copilot-latency.md` (probe), `recon-muse-copilot-landscape.md` (market), `recon-codex-copilot-map.md` (code map). Decision record: ADR-020 in [docs/DECISIONS.md](../../DECISIONS.md).

## 1. The three use cases (founder, 2026-09-02)

| # | Situation | What the rail must do | Knowledge |
|---|-----------|-----------------------|-----------|
| U1 | Recurring meeting in a folder (daily stand-up, client project) | Before and during: what was discussed last time, open action items with owners, what to follow up. Items tick "came up" as the call proceeds. | Previous meetings in the folder. No model needed. |
| U2 | Job interview, founder is the candidate | The interviewer asks about a project → the founder's own write-up of that project, then talking points. A general question (encoders, transformers) → a crisp answer. A question about something he never built → "Not in your notes" + a suggested approach, never a false claim. | Vault + project folders (incl. a curated "Me" folder), past meetings; Claude for general knowledge; web only for current facts. |
| U3 | Expert call with no prior context (AI infra sizing, solutions architecture) | At start: the questions to ask and what good answers look like. During: the same live cards with a domain persona. | Claude + web; past meetings on similar topics as memory. |

## 2. Modes — the one switch that remains

The founder rejected a "deterministic ↔ creative" mode switch. What remains is a **consent** switch, because nothing leaves the machine unless the user said so (ADR-002 stays the spine even as "local-first" stops being the headline — ADR-020):

| Switch position | What happens | Egress |
|---|---|---|
| **No AI** | "Last time" / folder brief only (U1). Deterministic facts from the database: open items, decisions, follow-ups, attendees, dates. Live "came up" ticks via local embedding match. | None |
| **AI · Claude** (default when on) | Everything in No AI, plus live cards: local passages instantly, then a streamed Claude answer with provenance labels, web search on demand. | The detected question (+ up to 2 preceding Them turns for context) and the retrieved passages. **Never the transcript, never audio.** Shown in the "Will send" line before the meeting and in a receipt on the note after. |
| **AI · Local model** | Same loop on the configured local notes model (Ollama / Rapid-MLX). Measured: a full card in 0.5–0.8 s on the founder's Mac, i.e. FASTER than Claude; quality on open-ended interview answers is the unknown (blind comparison pending). UI copy: *answers from your machine; Claude gives stronger answers on general questions and can search the web*. | None |

Remembered per folder (a "Interviews" folder can default to AI · Claude; "Client X" to No AI). One line in Settings explains the three positions; no other knobs.

## 3. The loop (same for all three cases)

```
Them utterance confirmed ──▶ detect prompt ──▶ retrieve local knowledge ──▶ show passages (card, top)
        (Whisper ~1 s)          (regex, local)     (bge-m3 + cosine, ⏱ B)              │
                                                                                     ▼
                                                              Claude streams the answer (⏱ C1) ──▶ card fills in
                                                              web search only if needed (⏱ C2) ──▶ "web" addendum
```

1. **Trigger.** Dual capture already separates *Me* and *Them* (`live.py` per-source captions). Only *Them* is watched. A confirmed utterance is a prompt when it ends with `?` or starts with a request stem (*what / how / why / when / which / can you / could you / tell me / walk me through / describe / explain*). ⏱ D reports regex precision/recall vs a 4B classifier; regex is the default unless the probe says otherwise. The Moonshine partial (0.5 s) may pre-start retrieval on the same rule; the card only renders on the confirmed line. Rhetorical questions produce cards the user ignores; acceptable. **Manual fallback (Muse, every winner has one):** hold ⌘⇧C (or click the rail) to force a card on the last *Them* turn; anti-spam: one card per question, 8 s debounce, and a "Not a question" dismiss that raises the threshold for that meeting.
2. **Retrieve (always, deterministic).** Query = the question (+ previous Them turn). Sources, in this order, all local: the folder's previous meetings (U1), the context index over vault + project roots (`search_context_doc_ids`), past meetings (`embeddings.rs` top-k), this meeting's attachments and typed notes. Top 3 passages above the existing 0.55 floor, each ≤ 600 chars, with a source pointer (file path or meeting title + date). Shown immediately as the top of the card, verbatim, no model involved.
3. **Answer (AI modes only).** One Messages API call from the sidecar (Python SDK, streaming): `model="claude-opus-5"`, `thinking={"type":"adaptive"}`, `output_config={"effort":"low"}`, `max_tokens≈400`, `tools=[web_search_20260209, max_uses=1]`. System prompt fixed (cacheable): *live copilot; ≤3 bullets of ≤12 words; label each bullet [your notes] only when it restates a passage verbatim, [Claude] for own knowledge, [web] with the domain for searched facts; if the question is about the user's own experience and no passage covers it, the first bullet is "Not in your notes" followed by a suggested approach; search the web only for current facts, products, versions, never for the user's experience.* User message = question + passages + (U3) the domain persona line from the folder's standing instructions.
4. **Card.** Streams in under the passages. Provenance labels are rendered as colored chips, not text. Passages are sent as `document` blocks with `citations: {enabled: true}` (Claude API, no beta): a bullet that carries a citation is `[your notes]` and the code checks that its `cited_text` is verbatim in the passage; a bullet without one is `[Claude]`; a bullet whose text came from a `web_search_tool_result` is `[web · domain]`. Belt and braces: the ≥3-word verbatim check from the follow-up work runs on top, so a mislabeled bullet is downgraded, never promoted. Card layers (Muse): a glance layer of ≤3 bullets, then a collapsed longer script (≤60 s spoken) the user can expand. Web bullets carry the domain and are appended when the search returns (the card does not wait for it).

## 4. The rail

Right column of the recording companion gets three tabs: **Notes · Last time · Copilot** (badge = unread cards). Copilot tab: a consent bar on top ("Copilot on · Claude · sends the question and 3 passages, never the transcript"), then cards newest-first. Card anatomy: the question in muted text; up to 3 passages with source chips; then ≤3 bullets with provenance chips; footer: `Pin to notes` (appends to YOUR NOTES) and `Open source`. Glanceable type (≥15 px, high contrast). The notch pill shows the newest card's first bullet. Keyboard: ⌘⇧↓ next card, ⌘⇧P pin, ⌘⇧C force a card. The rail and the pill may be excluded from screen sharing with the OS window-sharing exclusion API (a courtesy to the user, like a notes window); we never market "undetectable" (ADR-020; the Cluely backlash and breach are the cautionary tale in Muse's memo). "Last time" tab = the U1 brief (open items with owners and due, decisions, follow-ups, attendees; checkboxes write `done` on the source meeting's rows).

At record start (before any question): U1 folder brief renders immediately; U3 "questions to ask" list is generated once from the title / calendar event / standing instructions (AI modes only, not latency-critical).

## 5. Latency budget — measured (probe 2026-09-02, this Mac: Whisper large-v3 MLX, Moonshine v2, bge-m3, Ollama qwen3.5:4b, Rapid-MLX qwen3.6-35b)

| Stage | Target | Measured (median) |
|---|---|---|
| A. question end → confirmed Whisper caption | ≤ 1.2 s | **1.68 s** (1.65–1.74; 9 runs, very stable) |
| A′. Moonshine partial containing the question's key words | ≤ 0.6 s | **−1.5 s** (0.5–2.0 s BEFORE the speaker finishes); full-utterance partial at +0.50 s |
| B. retrieval (bge-m3 embed + cosine over 4,178 vectors) | ≤ 0.2 s | **32 ms** (embed) + 0.1 ms (search) |
| C4. local 4B card, first token / full 3 bullets | report | **28 ms / 508 ms** (1,814-token prompt) |
| C5. local 35B (Rapid-MLX) first token / full | report | **83 ms / 820 ms** |
| C1. Claude Opus 5 first token / full | ≤ 1.5 s / ≤ 3.5 s | **not measured: no Anthropic credentials on this Mac** (`ant` not installed, no API key). Estimate 0.8–1.5 s TTFT → 2.5–3.2 s end-to-end reactive. Needs `ant auth login` or an API key to measure. |
| C2. web-search addendum | ≤ 10 s | not measured; +1.5–3.5 s typical |
| **End-to-end, reactive (confirmed caption)** | ≤ 3 s | **1.74 s first token · 2.2 s full card (4B) · 2.5 s (35B)** |
| **End-to-end, speculative (retrieve on the partial, generate at silence)** | | **≈0.03 s first token · ≈0.5 s full card** |
| D. question detection | | **sentence-level regex: recall 1.00, precision 0.875 (3 FPs = tag questions "Alright?", "Got it?"), 0.005 ms** · 4B classifier: recall 0.19, 78 ms → rejected |

**What the numbers change (v1.1):**
1. **The local tier is fast, not slow.** A full 3-bullet card in 0.5–0.8 s on this Mac. The "AI · Local model" label must not say *slow*; the open question is *quality* for interview answers, not speed. Measure quality blind (10 interview questions, local 35B vs Claude) once Claude credentials exist.
2. **Speculative retrieval on the partial is the design.** The partial carries the question's key words 0.5–2 s before the person finishes; retrieval runs then (32 ms), so passages are on screen at silence and generation starts at silence. The confirmed caption only re-validates the trigger (and cancels a card if the confirmed text is not a question).
3. **Labels are assigned in code, not by the model.** Both local models mislabeled retrieved material as `[web]`. The model's own tags are ignored: `your notes` = citation/verbatim-verified against a passage; `web` = came from a search result; everything else = the model's name. This was already the rule; the probe makes it mandatory.
4. **Detector = sentence-level regex + a tag-question filter** (drop turns ≤3 words ending in `?`). No model in the trigger path.
5. **Claude's role narrows to quality and the web**, both worth it for the interview and expert cases, neither needed for speed. Cost of a Claude card is unchanged (cents).

Cost: ~1.5–2.5k input tokens + ~150 output per Claude question (system prompt cached); a 45-minute interview with 20 questions is well under one dollar.

## 6. Data and persistence

- `copilot_mode` per folder (`none` | `claude` | `local`), default `none`; a meeting inherits its folder's, overridable in the consent bar for that meeting only.
- `copilot_cards` rows per meeting: `at` (transcript offset), `question`, `passages_json` (text + source), `answer_md`, `provenance_json`, `egress_chars`, `web_used`. They render in the finished note as a collapsed "Copilot cards" section and feed the receipt ("Copilot sent 7 questions and 19 passages to Claude · 0 web searches").
- Nothing else is stored; no audio or transcript ever leaves.

## 6b. What the code already gives us (Codex map, `.recon/recon-codex-copilot-map.md`; file:line as of 2026-09-02 on `feat/meeting-context-followup`)

- **Live unit exists.** `/live_feed` returns confirmed utterances per source (`them` = system audio, `me` = mic; `models.py:401-409`, `server.py:1052-1110`); Rust `feed_live_source` de-duplicates and emits one **`live-transcript`** event per confirmation and **`live-partial`** for previews (`commands.rs:5826-5853`; payload structs are command-private at `commands.rs:35-50`). The frontend listener is in `App.tsx:442-491` (not `useRecording.ts`). **Hook point for the detector: right after de-duplication in `feed_live_source`, for `source == "them"`, pushed into a bounded background worker** so the sequential system→mic 500 ms loop (`commands.rs:5888-5923`) never awaits retrieval or a model.
- **Retrieval is split.** Meeting FTS + embeddings cover transcripts/summaries (`embeddings.rs:1-13`, `storage.rs:960-979`); the context index covers vault Markdown + project cards (`context_index.rs:517-598`, `storage.rs:3105`). **Typed notes and staged attachments are React state until stop** (`App.tsx:125-128`, `useRecording.ts:142-166`) — slice B needs live adapters for both.
- **Streaming transport exists** for single-meeting chat: `/chat_stream` SSE → Rust callback → Tauri IPC channel (`server.py:608-649`, `commands.rs:2588-2632`). Mirror it for cards. Ask-across-meetings is non-streaming.
- **No Anthropic SDK today**; `claude_api_key` is an ADR stub; provider keys live in `config.json` (redacted only in diagnostics; `types.rs:507-523`, `config.rs:158-166`) — slice C should move keys to secure storage.
- **No folder identity at record start** (start clears the viewed folder; `App.tsx:512-522`) — slice A must add folder selection/default resolution before any "Last time" brief or per-folder mode can work.
- **Consent must be enforced in Rust** before the sidecar request, bound to the exact serialized payload shown in "Will send"; today a global provider choice makes notes/chat cloud-capable without per-run confirmation (`commands.rs:2425-2475`) — the copilot must not inherit that.
- **Guards:** never take Python's `_WHISPER_LOCK` (`server.py:1072-1101`); no SQLite writes for partials/tokens (one write per confirmed question + one on stream end); keep the copilot off the 45-min transcription watchdog's queue (`useRecording.ts:197-205`); cap outbound context like Ask does (4k/meeting, 16k total; `commands.rs:2973-3016`); pill headline is a **separate `copilot-headline` event**, never piggybacked on `live-partial`; pin-to-notes appends through the existing `setUserNotes` path (no DB write during recording).
- **⚠ Gap the probe did not cover: local-model cards under load.** The probe measured the local 4B/35B with the live feed idle. During a real recording Whisper confirmations, Moonshine partials, and a local LLM card share the GPU; the queue is already paused while recording to protect live captions (`useRecording.ts:180-198`). Before making the local model the AI default, re-run stage C4/C5 **while a live feed replay is running**. If cards steal from captions, the local tier falls back to passages-only during speech and generates at silence.

## 7. Slices (build order; each a stuntman delegation with a self-contained spec)

0. **Probe (running):** Antigravity on Gemini 3.8 Flash measures A–D on this Mac. Muse maps the market; Codex maps the code. The spec's ⏱ cells and file:line references are filled from them.
1. **Slice A — U1 "Last time" / folder brief (No AI):** folder selection/default at record start (`App.tsx`), `storage::get_folder_copilot_brief(folder_id)` on `get_meetings_for_folder` + `get_action_items_on` (open rows) + the decision-section parser lifted out of `recap.rs`; read-only Tauri command + TS wrapper; the tab in the aside; tests on `in_memory_db()` + FolderView/companion Vitest. Do not reuse `get_folder_overview` (it calls the LLM). No egress. Ships alone.
2. **Slice B — detector + local passages:** hook after de-dup in `feed_live_source` for `them`, bounded worker; shared `CopilotQuestion/Passage/Card` types in `types.rs`; a `copilot-card` event; retrieval tiers: folder-filtered meeting FTS → context FTS → 8-s-bounded semantic enrichment; live adapters for typed notes + staged attachments; `Notes · Last time · Copilot` tabs; tests for de-dup, rate limit, folder filter, empty hits. No egress. Ships alone.
3. **Slice C — model cards + consent:** Anthropic Python SDK in the sidecar (new module/route, explicit models; question + bounded passages + folder persona only); local-model variant on the same route; SSE → Rust stream reader → IPC channel → incremental card; **consent token in Rust** bound to the frozen "Will send" payload; one `copilot_cards` row per question + stream end (passage ids/hashes, chars, provider, web flag, cancel state); receipt on the note; provider keys to secure storage.
4. **Slice D — provenance + "Not in your notes":** passage blocks with stable ids and citations; labels assigned in code (citation/verbatim → `your notes`; search result → `web`; else the model); ≥3-word overlap check; personal-question rule; Python tests for prompt assembly, label parsing, malicious passage text, domain extraction; Rust serialization tests; Vitest chips.
5. **Slice E — pill headline + pin + keys:** `copilot-headline` event → `RecordingBubble` (expressive mode first; minimal mode has no text region); pin via `setUserNotes`; shortcuts registered beside ⌘⇧M in `tray.rs` with collision tests.
6. **Polish:** "came up" ticks on the brief, per-folder defaults UI, Settings copy, Interview Assist shell (§7c).

## 7b. Positioning (ADR-020; Muse landscape memo)

Headline = capability: **"The live copilot that answers from your notes."** Reassurance block underneath: *On-device by default. Claude and the web only when you flip AI on, and only your question and the matching passages ever leave. Nothing is kept anywhere else.* This is the pattern every winner in the memo uses (Granola leads with note quality, Hyprnote/Meetily lead with local only where capability is commodity). What no product does today is the three-label contract plus "Not in your notes"; that is the claim to own. Marketing docs (`docs/STRATEGY_HANDOFF.md`, `docs/marketing_strategy.md`) are NOT updated yet — TODO.

## 7c. Interview Assist as a second shell, not a fork (Muse OSS recon, `.recon/recon-muse-oss-copilots.md`)

Verdict: **fork none.** The three most active open-source Cluely alternatives (Glass 7.6k★, cheating-daddy 5.6k★, Interview Coder 4.4k★) are Electron and **GPL-3.0** (copyleft: incompatible with a closed commercial app), Pluely went closed-source, Natively is source-available (personal use only). None captures audio better than Adversaria's Rust + sidecar; the founder's "couldn't get them to work" is explained by macOS TCC (Screen Recording vs Audio Capture split, false-denied `getMediaAccessStatus`) plus retired Gemini 2.5 model IDs returning 404.
What to borrow (all one-liners in Tauri 2): overlay window = `alwaysOnTop`, `transparent`, `decorations: false`, `contentProtected: true` (→ `NSWindowSharingNone` / `WDA_EXCLUDEFROMCAPTURE`; best-effort on macOS 15.4+), runtime `setIgnoreCursorEvents(true)` for click-through. Prompt shape (write our own; cheating-daddy's pack is GPL): 1–3 sentences, ready to speak, resume/JD-grounded, no coaching. GhostPilot's Alt+P screenshot-question hotkey for coding questions.
Shape: **one engine, two shells.** Interview Assist = a second Tauri window/app on the same capture + sidecar + index, with the overlay flags above, a curated "Me" folder, and AI on by default; Adversaria keeps the rail with No AI default. Marketed as "your notes, your words", never "undetectable".

## 8. Non-goals (v1)

No screen-share reading, no browser overlay, no auto-answering in the call, no cross-device sync, no fine-tuning. No mode switch beyond consent. No "stealth" claims in marketing.

## 9. Open questions for the founder

1. Default for an "Interviews" folder: AI · Claude on, or ask each time?
2. How many preceding Them turns travel with the question (0, 1, 2)? More context, more egress.
3. Should `[Claude]` bullets be allowed to mention the founder's experience at all, or must anything about him come only from `[your notes]`? (Recommended: only from notes.)

## 10. Verification

Probe numbers reproduced by Claude; unit tests per slice (Python: detector, label verification, prompt assembly; Rust: brief queries on `in_memory_db()`; Vitest: rail, consent bar, cards); one recorded rehearsal interview with the founder reading from the rail; egress checked by counting bytes in the request log against the "Will send" line.
