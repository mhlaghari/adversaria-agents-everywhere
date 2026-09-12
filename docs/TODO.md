# TODO / Backlog

Prioritized work for Meeting Note Taker. Known *bugs* first (verified, currently
live), then the roadmap toward a Granola-quality product, then smaller polish.

Mark items done by moving them to the bottom "Done" section with the date.

> **2026-09-11 — 🟠 Companion layout de-noise shipped without its four tests** (`copilot_focus_narrow`, `consent_summary_per_mode`, `consent_hint_only_for_selected_mode`, `stale_no_speech_notice_clears`; spec `.recon/interview-copilot-20260908/spec-layout-frontend.md`). Add them before commit.
>
> **2026-09-09 — ✅ SLICE 2 BUILT (uncommitted, `feat/live-copilot-c`; founder rehearsal pending).** Shipped: answer shapes, `copilot_deepseek_model` (default flash), `/copilot/warm` + keep_alive 30m (warm-up must use the answer path's `num_ctx`, see LESSONS 2026-09-09), standing pack (`build_pack`, ≤ 6,000 bytes, cached prefix), card memory (`recent_cards`, `resolved_question`), folder-only keyword gate + `folders.folder_terms` acronyms + tier d score 0.86 + 0.10 × coverage + canonical dedup, `copilot-folder-ready` readiness. Follow-ups now open: 🟠 close the local upstream once the NEXT line completes (the 35B sometimes rambles to the 640-token cap, "done" 1.7 to 12 s while the visible card is complete); 🟠 shape adherence on the 35B is loose (definitions come back as four sentences) — measure on DeepSeek Flash before tuning; 🔵 speculative start on partial captions; 🔵 practice runner with blind A/B ratings and export; 🔵 `first_sentence_ms`; 🔵 semantic tier for folder docs.
>
> **2026-09-08 — 🟠 COPILOT REV 6 SLICE 2 = THE INTERVIEW COPILOT (contract drafted, awaiting founder go).**
> Founder decision 2026-09-08: the Live Copilot is for interviews; the meeting flow stays the product.
> Contract: `.recon/interview-copilot-20260908/CONTRACT-2-interview.md` (Claude + Astra). Ship before the
> interview, in order: (1) evidence that wins — folder-doc score 0.86 to 0.96 (today max 0.75, below live
> notes 0.9 / meetings 0.85 / attachments 0.8), one-keyword folder tier plus a per-folder acronym allowlist
> ("What is RAG?" retrieves nothing today), canonical-path dedup across source kinds, Purpose before About Me
> in the header (cloud cap 1,200 bytes cuts it), "N sources indexed" readiness line; (2) bounded card memory —
> request schema v7 `recent_cards` (max 3 done cards of the session, never evidence, 2,400/1,600-byte budget),
> `resolved_question` for retrieval (cards 73/74 on 2026-09-07 show the failure); (3) practice runner — question
> bank file, one question at a time through the existing queue, ratings 1 to 5, blind Local/DeepSeek pairs,
> Markdown export, gate = median ≥ 4 and ≥ 80 % at 4 or 5. Deferred: running summary, local judge, prefetch,
> help hotkey, a semantic tier for folder docs (`/embed`). Evidence for the copilot: the 25-file Adversaria dossier
> in `~/Desktop/Adversaria Copilot Sources/adversaria/` (retrieval-shaped; see LESSONS 2026-09-08). Founder items:
> refresh/edit the folder profile, purpose, voice samples, DeepSeek default; move the four interview notes out of
> the sources directory; reconcile career numbers (8 vs 5 engineers; 25 min → 80 to 140 s vs ~150 s vs ~14 min);
> write the twelve ERDC agents down.

> **2026-09-05 — 🟠 REALTIME COPILOT V2 IMPLEMENTED (uncommitted, `feat/live-copilot-c`).**
> Durable session-bound answers (`docs/superpowers/specs/2026-09-05-realtime-copilot-v2.md`),
> 1-active/1-waiting queue, guarded terminal persistence (retried 3x), registered loopback endpoints,
> authoritative `[DONE]`, five-token provenance, and companion sheet/strip. Expressive bubble headline
> (`copilot-headline`) is deferred; companion answer strip and slide-over sheet are implemented.
> Provider, mode, question/context/persona/web are frozen at capture; grounding passages are retrieved
> when a queued card becomes active (retry reuses only completed retrieval and requires current provider/web consent to match).
> All automated contract suites green:
> - **Frontend:** 41 files / **377 tests** passed (vitest), `tsc --noEmit` clean, bundle/security green.
> - **Rust:** **414 passed / 1 ignored** (cargo test), `cargo fmt` and `cargo clippy` clean.
> - **Python:** **645 passed / 1 skipped** (pytest), ruff check/format clean; focused replay harness **25/25** after the final privacy, evidence, lifecycle, answer-shape, feed-failure and cadence fixes.
> - **E1a Service Replay Harness:** Built (`scripts/copilot-e2e/replay.py`); verified dry-run simulation
>   (`.recon/realtime-copilot-20260905/e1a-dry-run-host-final.json`, simulation with 0 executed/passed, not acceptance evidence);
>   honest structured skip recorded (`e1a-results-host-final.json`) confirming local service is offline without downloading models.
> - **Native Operator Runbook:** Staged at `.recon/realtime-copilot-20260905/native-runbook.md` with disposable data, invented fixtures, frame-derived measurements, and an explicit delayed-engine prerequisite for deterministic queue stress.
> - **Installed App Notice:** Installed notarized app at `/Applications/Adversaria.app` is version **0.3.83** from an earlier build that does not contain these uncommitted v2 changes.
> - **Completion Matrix Status:**
>   - [x] **S1–S4 Contracts, Core, Transport, Frontend UI** — automated contract suites pass across layers.
>   - [x] **S5 Synthetic Fixtures & E1a Replay Harness** — 14 invented scenarios, dry-run simulation verified, honest offline service skip recorded.
>   - [x] **S6 Architecture, Operator Runbook & Handoff Docs** — complete.
>   - [ ] 🟡 **E1b Native AI Local** — pending native capture / virtual loopback.
>   - [ ] 🟡 **E2 Native AI Claude** — pending credential (Anthropic API key).
>   - [ ] 🟡 **E3 Under Load Benchmarking** — pending native capture setup (≤20% live caption p95 regression check).
>   - [ ] 🟡 **E4 Founder Rehearsal** — pending interactive rehearsal in native app.

> **2026-09-03 (evening) — 🟣 Competitive gaps vs DoodleNote (see
> [docs/DOODLENOTE_COMPARISON.md](./DOODLENOTE_COMPARISON.md)).** Founder
> decisions pending, not started. DoodleNote (doodlenote.ai, Onyx Dev Labs,
> MIT, Electron, v0.4.18 on 2026-09-01) ships the same pitch as a free local
> app plus a $10/user/month Sync tier; assessed 2026-09-03 by three agents.
> Six things they have that we do not, ordered by how much they change daily
> use:
> - [ ] 🟡 **macOS ringing-call prompt + auto-stop when the call ends.** We
>       detect on Windows only and never stop on our own; they prompt within
>       ~5 s of Zoom / Teams / FaceTime / Slack huddle ringing, then stop and
>       generate notes when the call ends.
> - [ ] 🟡 **Microsoft 365 calendar.** `docs/SPEC_CALENDAR.md` exists; not built.
> - [ ] 🟡 **Publish the Windows beta as-is with a SmartScreen note.** Our code
>       is complete and unshipped; theirs is an unsigned beta and they ship it.
> - [ ] 🟡 **Rich-text notes editor.** Ours is a textarea plus rendered
>       markdown; theirs is TipTap with images, a toolbar and checkbox state
>       that survives reopen.
> - [ ] 🟡 **In-app one-click MCP connect**: a Settings row that writes the
>       `uvx adversaria-mcp` entry for Claude Desktop / Claude Code / Codex.
>       The server itself exists (`LaghariLabs/adversaria-mcp` 0.2.0 on PyPI).
> - [ ] 🟡 **Opt-in keep-recording** with click-to-seek playback and
>       re-transcribe. Delete-after-transcribe stays the default (privacy
>       choice); this is an explicit per-recording opt-in.

> **2026-09-03 (overnight) — ✅ EXPORTS built (commit `39b6782` on
> `feat/live-copilot`, awaiting the founder's dev-app review; specs `.recon/spec-export-E1-rust.md` /
> `spec-export-E2-frontend.md`, code map `.recon/recon-codex-export-map.md`):**
> (1) theme-matched slide deck + print/PDF — the deck (`exportDocument.ts`)
> was fixed dark and blind to `data-theme`; now takes an `ExportTheme`
> snapshot of the live CSS tokens (Laghari Labs → Laghari deck), print CSS
> follows the theme, an in-deck Print / Save as PDF button, an "Export as
> PDF…" menu item. Not done: embedding the `laghari` fonts (Pixelify Sans /
> IBM Plex Mono are name-only, no local files) → 🟡 bundle licensed font files
> later; a native one-click PDF (WKWebView PDF was dropped earlier) → 🟡.
> (2) `.adversaria` document: versioned JSON envelope with stable meeting +
> folder uids, rich action-item state, attachment metadata (no file bytes),
> folder export/import, re-import de-dup by uid, legacy `.adversaria.json`
> still imports, `bundle.fileAssociations` + open-with (`RunEvent::Opened`,
> argv, single-instance args → `open-adversaria-file`). 🟡 follow-ups: ship
> file bytes for small text attachments; drag-and-drop import (native
> drag-drop is disabled on the main window for the folder DnD); Windows
> association needs a real installer test; plaintext warning copy.
> Founder review 2026-09-03 07:11: the themed deck DID work (his 07:13
> export carries the Laghari palette) but *Export as PDF…* saving an .html
> confused him → FIXED `73fcf81` (opens the deck in the browser with `#print`);
> 🟡 PPT/PPTX export — founder: "not a priority at the moment"; 🔴→✅ companion
> right column broke when the tabs were put inside the 280 px aside → FIXED
> `73fcf81`; copilot force card for solo testing → FIXED `1f6f701`.
> **2026-09-02 (late) — 🟠 LIVE COPILOT (ADR-020).** Slices A+B BUILT
> (`34d04a2`, `23ab875`, unmerged); slices C (Claude/local cards + consent),
> D (provenance), E (pill/pin/keys) and the local-under-load probe remain. Also: 🟡 marketing/strategy docs still
> lead with "100% local" — rewrite headline to capability ("answers from your
> notes") with privacy as reassurance once the copilot ships; 🟡 curated "Me"
> folder in the vault (CV, project write-ups) as an explicit local-knowledge
> source for interviews; 🟡 decide screen-share exclusion for rail + pill.
> **2026-09-02 (evening) — 🔴→✅ An attached previous meeting did nothing
> visible (BUILT + VERIFIED on `feat/meeting-context-followup`, uncommitted;
> founder must first delete test rows 260–292 from the real DB — HANDOFF top).** Repro: founder
> attached meeting 166 while recording 259; `attached_context_for` sent its
> summary as background and the prompt says "never treat it as said in this
> meeting" → Follow-ups "None mentioned", no receipt anywhere. Fix built
> (specs `.recon/spec-ctx-{1,2,3}-*.md`): structured `prior_meetings` with open
> to-dos → deterministic "Follow-up from <meeting>" section (Done/Discussed only
> with a verbatim transcript quote, else Still open) + "Context used" chip strip
> + honest companion copy. Follow-ups filed from the probe, NOT in this slice:
> 🟡 status words/heading are English even for Arabic/Spanish output
> (`output_language`); 🟡 attached FILES stay background only (Muse suggests a
> "Context from <file>" section when there is overlap); 🟡 pre-existing: on
> short transcripts `qwen3.5:4b` sometimes omits the trailing "Action Items" /
> "Follow-ups" sections from its JSON and `_render` does not fill them (probe
> run A: 3/3 omitted; new to-dos were folded into Key Topics) — consider a
> template-section fallback; 🟡 `structure_note` passes `user_notes: None`.
> Seen in the 09-02 demo run (real model): 🟡 when the model emits the
> follow-up section itself it lands wherever the model put it (after "From
> Your Notes" in that run) — the reconciler should always move it before
> "From Your Notes"; 🟡 `_ensure_user_notes_section` only fills the section
> when it is missing entirely, so a note the model drops (3 of 4 rendered)
> is lost — reconcile per note like the follow-up items.
> **2026-09-02 — 🟣 FOUNDER ASK: WORKSPACE REDESIGN — local model curates,
> Claude Code / Codex executes (direction agreed, build NOT started; "tomorrow").**
> Founder: "the local model sucks at doing things"; keep the split view; the
> local model should provide context from his whole graph and Claude should
> execute. What exists already (do not rebuild): Claude Code + Codex are run
> engines (`workspace_runs.rs::detect_engines`; spawn in `commands.rs`
> `claude -p <brief> --permission-mode acceptEdits --add-dir …` / `codex exec -s
> workspace-write --cd <out> <brief>`), the two-pane screen (C2 `540d856`),
> retrieval grounding (`embeddings` top-3 meetings + `context_index` top-5
> vault/project hits at 0.55, folder excerpts inlined only for `local`). No
> model curates the brief today. Agreed shape:
> - **Curator (always local, extractive):** given the retrieval candidates and
>   full transcripts, select what matters for THIS task and quote it verbatim
>   with a source pointer per passage; never paraphrase facts (the Qwen probe
>   invented specifics when ungrounded). Bounded job, must be seconds not
>   minutes.
> - **Executor (Local / Claude Code / Codex, default Claude Code when
>   installed):** receives the curated brief; the brief is the exact payload
>   that leaves the machine, so a pre-run "Will send: N meetings, N notes, N
>   files" card is the per-run opt-in ADR-002 promised. Today's cloud caption
>   ("Full agent: reads folders, writes files") never mentions egress — fix in
>   the same slice.
> - **Screen:** keep the two panes (right pane becomes the curated-context
>   preview) + the Workshop Bench lifecycle: "On the bench" strip with phase
>   narration, review sheet listing every source with excerpt peek, one-sentence
>   Redo, Accept only inside the sheet, committed undo. Bench board:
>   https://claude.ai/code/artifact/146ad588-1ced-4009-b8ca-cbf82342ca91
>   (drawn single-column; founder now prefers the split — his call pending).
> - **Rejected as default:** Claude Code pulling context itself via the
>   companion MCP (best answers, unbounded invisible egress); maybe a later
>   per-workspace toggle.
> Slices: **probe first** (Antigravity, ~1 h: time the notes model curating a
> real workspace into a cited brief; speed + hallucination are the risky
> assumptions) → **W1** `/curate_brief` endpoint + cited brief section +
> receipt → **W2** curator/executor split, default engine, "Will send" card,
> honest egress caption → **W3** Bench lifecycle in the two-pane screen →
> **W4** "Needs one answer" / "Needs context" states so the executor stops
> instead of improvising. Branch off master (0.3.83 is on it).
> **2026-09-01 — ✅ SHIPPED in 0.3.83 (2026-09-02; built on `feat/live-captions`): the streaming
> preview tier.** Decided and built the same day (ADR-019): NOT tier (a)/(b)/(c)
> below as written — the probe showed sherpa-onnx has Moonshine only OFFLINE, and
> the streaming Zipformer is ALL-CAPS/~20% WER — but a fourth shape: Moonshine v2
> tiny re-decodes the unconfirmed tail every 500 ms (casing, punctuation, ~6% WER,
> 12–49 ms/decode, 44 MB, both platforms) and the Whisper caption replaces it per
> utterance. Measured on the real service: first grey words at 0.5 s. Remaining
> from this thread: 🟡 LocalAgreement option (show only the prefix two decodes
> agree on, +500 ms, kills flicker/hallucinated dates on tiny windows); 🟡 Apple
> `SpeechAnalyzer` Swift sidecar as a macOS-native tier behind the same contract;
> 🟡 Arabic preview when a comparable small model exists; 🟡 Windows CPU
> validation of the 500 ms cadence on a low-end box (the whisper live model there
> is the full CT2 turbo, so confirmations stay slow even though the preview is fast).

> **2026-08-31 — 🔬 FOUNDER ASK: match Windows Live Captions' latency for our
> live transcription (researched, verified 08-31; ready to slice).** What
> Windows does: a fully on-device STREAMING ASR (transducer-family: emits
> words WHILE speech continues and revises them, typically running on
> NPU on Copilot+ machines). Our live path is chunked Whisper: VAD waits for
> the utterance to END, then transcribes it (fast, ~0.2 s) on a 1 s poll
> (`LIVE_CHUNK_SECS`), so perceived lag ≈ utterance length + poll — words
> never appear mid-sentence. Three adoptable tiers:
> (a) QUICK WIN, no new models: decode the in-progress utterance every poll
> and show the unconfirmed tail greyed, confirming the prefix once two
> consecutive decodes agree (the whisper-streaming "LocalAgreement" trick).
> (b) STREAMING-NATIVE live engine, keep large-v3/MLX for the final
> transcript: Moonshine v2 (streaming encoder, words-as-you-speak, ~6x
> smaller than large-v3, English-strong, Python bindings) or sherpa-onnx
> streaming Zipformer (CPU real-time, multilingual).
> (c) macOS-NATIVE, the true Live Captions equivalent: Apple SpeechAnalyzer /
> SpeechTranscriber (macOS 26): on-device, streaming volatile+final results,
> measured ~2.2x faster than large-v3-turbo at comparable quality, runs on
> the ANE; needs a small Swift sidecar since it is a Swift API.
> Recommendation: (a) first (one slice in the Python live path), then (c) as
> the macOS live engine behind the existing engine abstraction.

> **2026-08-30 — ✅ MEETING PROJECTS shipped: committed (`635101f`), pushed,
> and cut into 0.3.82 (notarization + Windows CI in flight the same day).** Reused `workspaces` as Projects rather than
> creating a second container: sidebar create/count/expand, move-menu and drag
> filing, project chip/suggestion banner, ProjectView, live standing
> instructions, per-project Web research control, local cached Project overview,
> attendee frequency, action-item completion, responsive layout, and confirmed
> non-destructive project deletion are built. Verification: TypeScript clean,
> 225/225 Vitest, Rust fmt/check clean, 330 passed + 1 ignored, native wide-window
> click-through complete. **Next:** build Related meetings beneath each note. Record-start filing
> remains deferred because a fresh recording has no title/summary signal for the
> existing suggestion ranker.

> **2026-08-29 — 🧭 FOUNDER UNIFICATION (supersedes the thread≠workspace split
> on the boards): ONE container — the "meeting workspace".** The 08-27 design
> had threads (memory, Meetings area) and workspaces (factory, Workspaces tab)
> as separate organs. The founder collapsed them: a client project is ONE
> object with two faces — a MEETING face (record, live rail, what-was-discussed
> /what-to-talk-about, briefings) and a WORK face (tasks, artifacts, approvals).
> The closed loop that requires this: meeting → side quests (diagram, research)
> → workspace does them → **the artifacts join the project's memory** → next
> meeting's live rail draws on prior meetings + open items + THAT RESEARCH
> ("if they mention something, I can refer to my research"). The factory feeds
> the copilot. At record start the app asks/suggests "which project is this?"
> (calendar/attendee-suggested, founder confirms — suggest-don't-guess).
> Also from 08-29: the in-meeting copilot intent — at record start ask what
> KIND of meeting (interview/client/follow-up); live suggestions are
> retrieval-first (surface the founder's OWN history/artifacts — safe) vs
> generative solutioning (risky, must look different on screen). Attachments
> should also be addable from the meeting page, not only mid-recording.
> Naming ("meeting workspace" vs project) open. Boards to be merged into one
> when the founder calls it. Nothing built yet.

> **2026-08-28 — 🟣 FOUNDER ASK, noted only (do not execute yet): the in-meeting
> screen wastes a wide window, and meetings should carry their own context.**
> The full-screen recording view (`RecordingCompanion.tsx`) is one centered
> vertical stack — transcript on top, notes below — so at full screen both
> flanks are dead space and the transcript gets half the height. Asks:
> (1) dock the live transcript to the left or right, notes fill the other side;
> (2) a **+ add-context button usable mid-meeting** — attach documents, previous
> meetings, files — so the live assistant and the eventual notes carry that
> context; (3) future: **"meeting projects" in the Meetings area (explicitly NOT
> workspaces)** — interconnected meetings that surface highlights and
> things-to-talk-about during the call. Overlaps the parked 🟣 2026-08-26
> related-meetings/pre-meeting-briefing ask; the live screen is likely where
> that briefing should land. Existing machinery to reuse: rolling live summary
> (notch panel), `hybrid_rank`/graph retrieval, `calendarEventAt`, open
> `ActionItem` rows. Concept boards:
> live screen ("The Meeting Room") →
> https://claude.ai/code/artifact/e27c26d6-478d-4933-b89b-9c4725ead417
> meeting threads ("The Thread Between Meetings") →
> https://claude.ai/code/artifact/a8989fb6-b949-43ce-86fc-0a417688d00c

> **2026-08-26 — 🔵 FIRST REAL TEST-DRIVE of auto-staffing: matcher fine, three
> gaps in what it staffs.** Founder ran the six seeded tasks. Findings:
>
> **(1) Diagrams were black-and-white and plain (FIXED same day).** The built-in
> `drawio-diagram` fallback specified `style="rounded=1;whiteSpace=wrap;html=1;"`
> with no fill at all, so every non-claude engine produced grey boxes. `addons.rs`
> now carries a semantic palette (draw.io's own canonical pairs: blue app/service,
> green datastore + `shape=cylinder3`, yellow queue, orange gateway, grey external
> w/ dashed edges, red error, purple model/AI), a rhombus rule for decisions, a
> swimlane rule for grouping, and coloured edges with `dashed=1` for optional
> flows. Colour now carries meaning rather than decoration.
>
> **(2) 🔴 The research task could not research — the network gate has no UI.**
> The Deep research skill correctly refused ("Do not use outside knowledge or
> browse the web unless the brief explicitly says network access is allowed") and
> returned an honest but useless answer: "the context contains no competitor
> data", listing Otter/Fireflies/Gong as things it was forbidden to name. **The
> unblock is small and already half-built:** `workspaces.network_allowed` EXISTS
> in the schema (`storage.rs:504`, default 0) with no UI and nothing reading it
> into the brief. Slice: a per-workspace network toggle, the brief stating network
> is allowed when it is on, and the receipt naming every URL fetched. That also
> unlocks porting LL-OS `DeepResearcher`.
>
> **(3) 🔴 "Build a landing page" silently produced a Marp slide deck — the
> Skill-Finder case, confirmed in the wild.** No front-end/landing skill exists,
> so the matcher picked the nearest wrong thing (`slides-deck`) and ran it
> confidently. This is exactly the failure the Skill Finder screen was drawn for
> ("Nothing here fits · closest installed: Marketing copy (partial), Slides deck
> (wrong shape) · Missing: a front-end build method"). **Rule to build:** when the
> best score is below a threshold, staff NOTHING and say what is missing rather
> than running the nearest match. Silent wrong-skill is worse than no skill.

> **2026-08-26 — 🟣 FOUNDER ASK: meetings need to know about each other (two
> parts, artifact to be made once the shape is decided).**
>
> **(a) Related meetings under the generated notes.** After a meeting's notes are
> generated, show the related meetings beneath them. Founder's case: recurring
> daily stand-ups across two or three projects, plus client meetings — today each
> note is an island, so the thread is invisible. **Mostly a surfacing job, not new
> intelligence:** the retrieval already exists and is proven — `hybrid_rank` +
> graph anchors + FTS5, and the workspace context engine already pulls "top 3
> related via graph" with per-run receipts (`select_related_meetings` in
> `workspace_runs.rs`). Open calls: where it sits in `NoteViewer` (below the
> summary vs its own tab), how many to show, whether the reason for relatedness is
> named the way run receipts do it, and whether the user can pin/remove a link.
>
> **(b) Projects, and a pre-meeting briefing.** Meetings need a grouping — a
> project or thread — so the app can answer "what is this a continuation of".
> Payoff the founder wants: **before** a client meeting, a notification saying what
> was discussed last time, what to cover now, and which action items are still
> open. Overlaps heavily with **Meetings as Projects** (board, blocked only on the
> per-project Agents on/off decision) — decide whether this IS that feature's
> slice 1 rather than a parallel thing. Infrastructure that already exists and
> should be reused: meeting→workspace binding, the notch/alert surface for the
> pre-meeting nudge, calendar lookup (`calendarEventAt`) to know a meeting is
> about to start, and open `ActionItem` rows for the "still open" list. Open
> calls: automatic grouping vs manual, how far ahead the briefing fires, and
> whether it is a notch alert, a notification, or a card in the app.
>
> Founder: build an artifact for this once the shape is worked out. Parked while
> Workspaces continues.

> **2026-08-26 — 🔴 A hung transcribe request wedges the background queue (founder
> repro: changed the notes model mid-transcription).** Symptom looks cosmetic — a
> "Transcribing…" tag stuck on a meeting that finished — but it is not. The tag is
> `meeting.id === transcribingId` (`MeetingsList.tsx:93`); `transcribingId` is React
> state cleared ONLY in the `.finally()` of `transcribeMeeting(job.id)`
> (`useRecording.ts:205-210`). Two gaps let that promise never settle: (1) the shared
> HTTP client is built with `reqwest::Client::new()` (`http_client.rs:281`) and
> reqwest imposes **no request timeout** by default, so a service that stops
> responding without closing the socket — what a model swap / sidecar restart can
> cause — hangs forever; (2) there is no `AbortController`/`setTimeout` watchdog
> anywhere in `useRecording.ts`. **Severity is the queue, not the badge:** the drain
> effect early-returns while `transcribingId !== null` (`useRecording.ts:150`), so
> NO further background transcription runs for the rest of the session.
> Verified on meeting 247: transcript 17,290 chars, summary 2,707 chars,
> `audio_file_path` NULL (deleted, which only happens on success) — the work
> completed and was persisted; only the response was lost. There is no `status`
> column on `meetings`, so nothing is stuck server-side. Workaround: restart the app.
> Fix: per-request timeouts (generous on `/transcribe` + `/summarize`, short on
> `/health`) — **NOT** a global one, `http_client.rs:388` warns the client must not
> impose a short timeout because model downloads are multi-GB — plus a client-side
> watchdog that clears `transcribingId` so a hung request can never wedge the queue.
> Optionally have a model change cancel or await in-flight jobs. Check whether
> meeting 245 ("Untranscribed recording", audio still on disk) is a casualty.

> **2026-08-25 — 👁 WATCH: prime-agent as a 4th workspace engine (founder ask,
> assessed, deferred).** github.com/PrimeIntellect-ai/prime-agent (MIT, ~18k★):
> autonomous agent with headless JSON mode (`prime-agent --mode json "…"` →
> NDJSON ending in `agent_end`) and a Continual Harness (per-workspace memory
> across runs — thematically a great Workspaces fit). Mechanically easy: probe
> in `detect_engines` (workspace_runs.rs:344), spawn branch beside claude/codex
> (commands.rs:6300), whitelist (commands.rs:5973), picker entry. **Blocked on
> the locked guardrail** (output-dir-only writes, network off): their README
> explicitly says it is NOT a sandbox — model-generated Python runs with full
> user permissions, no write/network restriction flags — and runs are
> daemon-backed (outlive the app; conflicts with Pause-all/kill-on-stop).
> Revisit when upstream ships sandbox flags OR the founder creates an explicit
> "no guardrails" consent tier. Safe slice 1 if wanted early: manual-only runs
> (never autopilot), cwd = output dir, caption "runs outside Adversaria's
> guardrails", `prime-agent shutdown` wired into Pause-all + app exit. Not
> installed on this Mac as of 2026-08-25.

> **2026-08-25 — 🐛 Engine dropdown: same model shown as both "not downloaded"
> and "on this computer" (founder repro, `qwen3.5:4b`).** Not a lie, a merge of
> two lists that check two different Ollamas: curated tier rows compute
> `installed` against the app-managed **sidecar** (port 27434, app-data store —
> `setup.rs:313` → `has_tag`), while the raw "on this computer" rows scan the
> **user's own Ollama** on 11434 (`setup.rs:176`, `ollama_profiles()` at
> `setup.rs:215`). Stacked mismatch: on Apple Silicon >32 GB + Ollama ≥0.19 the
> curated 4B tier looks for the MLX variant `qwen3.5:4b-mlx`
> (`effective_tag_for`, `ollama_engine.rs:152`), which the user doesn't have —
> so even a shared store wouldn't match. No functional bug (selecting the
> `ollama:` row works; downloading the curated row pulls a second ~3.4 GB
> copy). Fix ideas: have the curated row also `tag_matches` against the
> detected 11434 set and render "already in your Ollama — select below", or
> dedupe the pair into one row.

> **2026-08-22 — 🟣 WORKSPACES AUTOPILOT (founder idea, brainstormed +
> board approved; Phase 3a/3b/3c, post-launch build).** The workspace
> becomes a place where to-dos ARRIVE on their own, agents work them
> unattended, and the founder approves/rejects from a progress card.
> Four decisions LOCKED by the founder (AskUserQuestion, this date):
> (1) **routing = bind meeting → workspace once** (graph-suggested via
> `hybrid_rank` + shared attendees, one-tap confirm, stored on the
> meeting; unbound meetings → Inbox where nothing runs; "Push to
> workspace…" stays in the ⋯ menu as the per-item override); (2)
> **always auto-run** — founder override, REVERSES the 08-17 "no
> autonomous triggers" item; trust moves to standing guardrails
> (output-dir-only writes, network off per workspace, one run at a
> time per workspace + time budget, cloud engines caption that the
> context list leaves the machine) + ONE global "Pause all agents";
> (3) **Grok (xAI) joins as a BYOK engine** (off until keyed) and
> **"Get 2 takes"** is a per-task mode (same brief, two engines, A/B
> review card), never the default; (4) **Approve = mark done + keep
> artifact**, export ("Copy into project" / "Send to vault") is a
> separate opt-in action. Approve writes the three `ActionItem`
> fields that already exist unwired: `status: ai_done → done`,
> `completed_by = agent:<engine>`, `evidence = artifact path`. Reject
> = one-line reason appended to the brief + automatic re-run (still
> no chat thread). Card = approval ring (approved/total) + three
> counts: running (blue, agent acting) · awaiting review (AMBER — new
> app-wide meaning: an agent is waiting on you) · queued. Context
> engine (3b): brief gains top-3 related meetings via `hybrid_rank`,
> top-5 Obsidian vault notes (vault READ is new — `second_brain.rs`
> only writes today; graphify MCP when attached, folder read as
> fallback), and every retrieved item is named on a per-run receipt.
> "needs you" classification keeps non-agent to-dos (record the demo)
> out of the run queue. Model deltas: `Meeting.workspace_id`,
> `WorkspaceTask.status` +awaiting_review/rejected/needs_you,
> `rejection_notes`/`attempt`, `WorkspaceRun.receipt`/`take_group`,
> context kind vault/graph, engine `grok`, global `agents_paused`.
> Annotated board (mechanism diagram + 5 screens + data table + build
> order): https://claude.ai/code/artifact/28a0832e-be32-4c0e-9b7b-75ed04cd6328
> Open calls: done signal (toast vs pill flash) · retrieval caps (3
> meetings / 5 notes) · binding-suggestion threshold · per-task time
> budget (10 min?).
> **BUILT 2026-08-22 (same day, Phase 3a, uncommitted, dev-gated):**
> routing + auto-push, review queue, approve/reject, autopilot, global
> Pause, crash-safe re-queue, card ring + counts, binding banner. Built by
> Codex (stuntman, 3 delegations), reviewed + gated by Claude (cargo 252 ·
> clippy · fmt · tsc · vitest 158). 3a deviations: bindings table instead
> of `Meeting.workspace_id`; no `rejected`/`needs_you` statuses yet.
> Remaining: **3b** context engine (related meetings via `hybrid_rank`,
> vault READ via graphify MCP / folder, named receipt, needs-you
> classification) · **3c** Grok BYOK + "Get 2 takes". See HANDOFF.md.
> Live-run findings 08-22: needs-you classification should lead 3b (an
> agent ran "Record 90-second demo video"); add title-level dedup on
> push (pre-3a hand-pushed task was duplicated).
> Same evening (delegation 4): in-app artifact preview ✅ · routing moved
> to the to-do board ✅ · related meetings via graph in every brief +
> context receipt ✅. Still open for 3b: vault READ (graphify MCP /
> folder), needs-you classification, title-level push dedup.
> Layout round (delegation 5, CSS only) ✅: titles wrap, preview stays in
> the card, pause bar no longer folds, preview lists show markers.
> 🔴 Relevance floor for related meetings: `hybrid_rank` always yields its
> top 3, so unrelated meetings enter the brief (seen: trading bot +
> interview + Tatweer for an "Arrival Kit on the website" task). 3b must
> return 0–3 above a score threshold and rank on the to-do text.
> ✅ Done same night (delegation 6): floor + to-do-text ranking + labelled
> receipt; local engine fixed (`/draft_stream`). ✅ Skills & agents
> catalog (delegation 7). In flight: vault + projects context engine
> ✅ (delegation 10: 8 s embed timeouts + local engine writes real files.)
> 🟠 Embeddings still require Ollama (`embedder.py` is Ollama-only, default
> `bge-m3`), even on macOS where the notes model is managed Rapid-MLX. Without
> it every semantic path (Ask, graph similarity, related meetings, vault /
> projects search) silently degrades to keyword FTS. Options: serve bge-m3
> through Rapid-MLX/MLX (`mlx-embeddings`), or bundle a small embedder in the
> Python service; either way show "semantic search: off" in Setup status
> instead of failing quietly. **Verified 08-23: the app never pulls any Ollama
> model itself** (no `/api/pull` anywhere; `ollama_profiles_are_never_
> downloadable`), so a NEW user gets semantic search only if they happen to
> have Ollama + `bge-m3` already; the `/embed` failure is logged to stderr
> only. (Founder asked 08-23: "does it get downloaded automatically?" — no.)
> 🟠 Resilience (found 08-23 live): a wedged Ollama made `client.embed`
> hang ~2 min twice per run before the FTS fallback kicked in, and a
> backend restart mid-run failed the draft call. Wrap the two embed calls
> in `related_meetings_for_text` / `context_index::search` with
> `tokio::time::timeout(8 s)`, and make "notes model unreachable" a
> retryable failure (auto re-queue once). Gotcha: `ollama ps` empty + embed
> curl hanging = restart Ollama.app (quit + `open -a Ollama`).
> ✅ (delegation 8, see HANDOFF). ✅ 08-23 delegation 9 = needs-you
> triage (`task_triage::needs_you`, `agent_eligible` column, autopilot skips
> them, "Let an agent try" override) + title-level push dedup + vault file
> names in FTS. Brainstorm boards (founder 08-22 night, both researched
> by subagents against the real code):
> • **Meetings as Projects** https://claude.ai/code/artifact/b69dacc7-dafb-4eca-90c0-a10895cf9e74 — a Project IS a
> workspace, the bindings table is the folder; sidebar All/Inbox/Projects,
> project page (meetings · open to-dos · people · artifacts), four filing
> gestures. ⚠️ Decision needed: **filing ≠ running** — per-project
> `agents_enabled` switch (default off for new projects) so filing a
> meeting never starts cloud agents; also fix the split membership
> count (bindings vs context items). Slice 1 ≈ a day.
> • **Share sheet & connections** https://claude.ai/code/artifact/16583952-cf7f-4ee9-8fb3-8341de9ad52b — Notion / Slack /
> CRM as a per-meeting push with preview + push log (reuse
> `second_brain` markdown, keyring tokens, no OAuth backend); order
> Slack webhook → Notion markdown API → Attio → HubSpot; Granola parity
> table; hosted MCP servers only as workspace connections for agent work,
> never the push mechanism. Decisions: paste-a-token OK? Slack payload
> scope? People tab before CRM?

> **2026-08-17 — 🟣 WORKSPACES (founder's next flagship; brainstormed +
> UX flow sketched, post-launch build).** The meeting produces work; the
> workspace is where a local agent does the work. Three decisions LOCKED
> by the founder (AskUserQuestion, this date): (1) **brain is pluggable
> from day one** — bundled local LLM tier, auto-detected installed agent
> CLIs (Claude Code / Codex, driven headless), BYOK cloud as explicit
> opt-in; (2) **a workspace is a long-lived PROJECT**, action items from
> many meetings flow into it ("Send to workspace" from any to-do's ⋯
> menu, source meeting auto-attached as context); (3) **v1 showcase =
> repo → architecture doc + diagram via CONNECTED TOOLS** (founder
> override 08-17: NOT built-in Mermaid rendering — Phase 3 is a
> connections layer: attach MCP servers (Draw.io = flagship), skills,
> and agents to a workspace; the agent writes e.g. a .drawio artifact
> and the artifact card offers "Open in Draw.io", which is local-first
> since the Draw.io desktop app runs offline).
> UI: second tab after Graph, blue, ✦ — blue reserved app-wide for
> "agent acting". Web research off by default per workspace; context
> list == permission list; run log = trust surface; artifact carries a
> provenance receipt incl. "Network: never touched"; Stop always one
> click; NO chat thread in v1 (refine task + re-run). Six-screen UX
> flow board (annotated wireframes):
> https://claude.ai/code/artifact/c6a2c0a2-7bdc-4f50-8f1f-d8fd521f85ce
> Open calls: run history retention · per-workspace concurrency · done
> notification (toast vs pill flash) · bridge verb name. Related:
> **Teams** = premium expansion, BLOCKED on the sync ADR (same decision
> as the 08-12 multi-device item). ⚠️ Public copy: no premium/pricing
> talk (LAUNCH_ASSETS §7 framing) — Workspaces teased in the Andrew
> email as "what I'm building next" only.

> **2026-08-17 — 🟡 No manual "Check for updates" control (founder-filed,
> fresh-account QA).** The updater checks at launch + every 6 h and shows
> a toast when it finds one (`UpdatePrompt.tsx`) — but a user TOLD an
> update exists has no button to force a check; the founder's only path
> was quit-and-relaunch. Add "Check for updates" (Settings → General,
> next to the version line) that calls the same `check()` and reports
> "You're on the latest" honestly when there's nothing.**

> **2026-08-17 — 🟡 Shared model storage: stop per-account re-downloads
> (founder-filed during fresh-account QA).** He now has the same 1.2 GB
> Qwen3-ASR model downloaded in two macOS accounts on one machine. Reuse
> WITHIN an account already works (any tool's HuggingFace cache is
> detected — `whisper_model_is_cached` walks the standard HF cache), but
> caches are per-user by macOS design, and other ecosystems' formats
> (whisper.cpp GGML, OpenAI .pt) are genuinely unusable by our runtimes
> (MLX / CT2 / sherpa conversions). The real feature: an optional shared
> model directory (e.g. `/Users/Shared/Adversaria/models` or a
> user-chosen path) that the service treats as a secondary HF cache root
> — read from it first, download into it when configured. Needs: path
> setting in Settings › Transcription, permissions story (world-readable),
> and the downloader + `_hf_cache_root()` honoring it. Niche for typical
> users, real for shared Macs and QA machines.**

> **2026-08-14 — 🟠 Notarization: switch to an App Store Connect API key.**
> OPEN, founder action (~5 min in ASC → Users and Access → Integrations →
> Keys). The keychain-profile credential is now proven fragile THREE ways:
> revoked-password reports as missing (0.3.73), high-load transient lookup
> failure (0.3.73/0.3.75, documented in build-dmg.sh), and — discovered
> during the 0.3.78 cut — **fast-user-switching locks the data-protection
> keychain**, so a release cannot notarize while a QA account is active.
> A `.p8` API key on disk (`notarytool --key/--key-id/--issuer`) is immune
> to all three and survives Apple-ID password changes. Wire build-dmg.sh
> to prefer key-based auth when the key vars are set.

> **2026-08-14 — 🟡 Fix-this-word should also work in the Summary tab.** OPEN.
> The founder met "cloud code" in the NOTES and tried to fix it there —
> the affordance only exists in the Transcript tab (v1 scope). The engine
> already rewrites the summary; only the selection surface is missing.
> Extend the same popover to the Summary tab's rendered sections.

> **2026-08-14 — 🟡 Dictionary phrases beat homophones — surface this.** OPEN.
> Founder case: "Claude" in the dictionary did NOT fix "cloud code" (by
> design — cloud↔Claude similarity 0.73 < fuzzy threshold, and rewriting
> real words is the homophone trap), but the PHRASE entry "Claude Code"
> fixes it perfectly (live-proven: window match ratio ≈0.95). Two
> follow-ups: (a) one line of hint copy at the dictionary input — "for
> names that sound like real words, add the full phrase (e.g. Claude
> Code)"; (b) Cohere has NO decode-time glossary (sherpa lacks a context
> param) so the post-hoc corrector is its only layer — sherpa's hr-dict/
> rule-fst hooks are the eventual decode-time answer, filed with the
> Cohere engine entry.

> **2026-08-14 — 🟡 Dev builds poison the shared registration state.** OPEN.
> Dev builds (no compiled endpoint, by design) write "queued / no endpoint"
> registration state into the app-data store the INSTALLED app shares —
> founder's shipped 0.3.77 showed "Registration queued" purely from dev
> sessions (binary verified to carry the endpoint via `strings`; users
> unaffected). Fix in the dev-spool-key spirit: a debug build should not
> WRITE registration retry state (or should namespace it), so the installed
> app's Registration section always reflects its own reality. Interim:
> clicking Retry now on the shipped build delivers and clears.

> **2026-08-14 — 📝 README refresh (founder-filed).** OPEN. The new Author
> section needs Hamza's LinkedIn URL (placeholder sits in README.md), and
> the README deserves a general pass — it predates the Qwen engine, the
> 10 notes languages, and the tap capture. Flows to the public mirror via
> the queued sync-public PR; do the refresh BEFORE that sync so the
> mirror's front door is current.

> **2026-08-14 — 🔵 Mac App Store: NOT VIABLE today — filed as a watch
> item, not work (founder asked 2026-08-14).** Research verdict: Core
> Audio process taps — the capture path we JUST adopted to fix DRM
> blanking — do not work reliably inside the App Sandbox, and the App
> Store REQUIRES the sandbox. Apps in exactly our category (system-audio
> capture: AudioCap-style tools, Granola) all distribute outside MAS via
> Developer ID + notarization — which is precisely our current pipeline,
> so we already have the only distribution Apple's rules permit for this
> product class. Revisit only if Apple adds a sandbox-compatible
> system-audio entitlement (watch WWDC notes yearly). Windows equivalent
> (Microsoft Store) is unexamined and less restrictive — could be part of
> the Windows rewrite conversation.

> **2026-08-14 — 🟠 Cohere Transcribe as the third on-device engine
> (founder-filed for 0.3.78+).** OPEN. Spike PASSED 2026-08-12 (sherpa-onnx
> int8, 1.6 GB, word-perfect English with the best punctuation of the
> tested engines; Arabic correct). Same integration shape as the Qwen
> engine (registry entry + transcriber class + chunked-window timestamps).
> THREE known wrinkles to resolve in the spec: (1) sherpa's Cohere impl
> REQUIRES an explicit language per stream — silent empty output without
> it, no auto-detect, no code-switching (this is the Principle-6 problem:
> where does "which language is this meeting in" live without a setting
> people must touch?); (2) no `context` glossary param — sherpa offers
> hr-dict/rule-fst hooks instead, needs investigation; (3) macOS runtime
> is CPU (fine: 4.2 s for the long VO clip — also the realistic Windows
> profile). INTERIM ANSWER for "my model isn't in the list": Settings →
> Transcription → Self-hosted takes ANY OpenAI-compatible transcription
> server — a Cohere lover can serve their model behind one TODAY.

> **2026-08-13 (live dev test) — 🟡 "Encrypted recording spool is missing" is
> a misleading error when start() blocks on the keychain.** OPEN. Sequence:
> record click claims the `recording` flag (audio/macos.rs start(),
> compare_exchange FIRST), then `SpoolSession::start` blocks on the OS
> keychain dialog (`adversaria-recordings`/`spool-key-v1`,
> recording_spool.rs:22) — if the user stops/toggles while the dialog is up,
> stop() sees is_recording=true but no spool and reports "Encrypted
> recording spool is missing", which reads like data loss when NOTHING had
> started recording. Fix: stop() with a missing spool while start is
> mid-flight should say "Recording never finished starting — approve the
> keychain prompt and try again." Dev-only trigger today (ad-hoc dev
> signatures re-prompt every rebuild; the packaged app's stable signature
> is in the item's ACL), but any slow keychain would reproduce it in prod.

> **2026-08-12 (evening) — founder ask: THEMES.** OPEN.
> - [ ] 🟡 **Light theme + theme picker (Dark / Light / System).** Founder is
>       tired of dark-only. Honest sizing from the code: the MECHANISM is cheap
>       — `src/prototype.css:1` + `src/index.css:10` already define a semantic
>       token layer (`--bg-*`, `--text-*`, `--border-*`, accents) with 573
>       `var()` references, so a `[data-theme="light"]` override block + a
>       `theme` field in `AppConfig` + a Settings › General control + a
>       `prefers-color-scheme` listener for System is ~a day. The REAL cost is
>       the audit: **181 raw hex + 234 raw rgba() in CSS bypass the tokens**
>       (most are dark-specific white-alpha overlays/borders/glass that must
>       flip to black-alpha in light), plus ~24 hardcoded hex in TSX inline
>       styles (speaker colors were already chosen to read on both, per the
>       comment at `NoteViewer.tsx:87`), plus QA across Settings' 8 sections,
>       graph, notch pill, companion/recording windows, tray. Estimate 2–4
>       focused days for a light theme that doesn't look half-painted.
>       **Dark stays the default** (the product's dark identity is deliberate —
>       see brand-separation history); Light/System become choices.
>       **2026-08-13 — founder extension: WHITE-LABEL BRAND PACKS.** Send a
>       company's people Adversaria in THEIR branding (colors, heading font,
>       co-branded wordmark) as a sales motion. Rides the same token layer:
>       a brand pack = ~5 tokens + a font + a wordmark line, loadable at
>       startup (JSON), one build serves every client. Interactive concept
>       the founder approved exploring:
>       https://claude.ai/code/artifact/0d1f37cb-62e6-4f82-b954-ac9d9dbd540a
>       (dark/light/two fictional client skins on the real app layout).
>       Sequence AFTER light mode lands — it is the light-mode work plus a
>       loader, not a separate engine.

> **2026-08-12 (later) — two more founder asks (Hamza, verbal). Both OPEN,
> both deliberately DEFERRED by him ("we could add that later").**
> - [ ] 🟡 **Notes need a real summary paragraph:** today's templates can yield
>       "Key decisions" as a few disjointed sentences that don't stand alone.
>       Founder wants an **executive-summary paragraph** (or a detailed-summary
>       variant) in the note. Templates live in `python-service/prompts/*.md`
>       (general / one-on-one / client-meeting / brain-dump) and are seeded to
>       the user's data dir with versioned backup (the 0.3.72 prompt-seeding
>       mechanism) — changing shipped templates re-seeds safely, but users who
>       EDITED a template keep their copy, so the change must be additive and
>       announced, not assumed. Also applies to the Arabic templates.
> - [ ] 🔵 **Local-first multi-device sync (office Mac ↔ home Mac; iOS/Android
>       eventually):** founder takes meetings on two machines and wants one
>       synced meeting history — "everything local, syncs across all devices",
>       explicitly as the path to future mobile apps. BIG architecture item —
>       needs an ADR + design doc BEFORE any code: the DB is SQLCipher with
>       per-machine keychain keys; sync must not violate Principle "nothing
>       leaves the machine" (transport must be user-owned: e.g. an
>       end-to-end-encrypted file in the user's own iCloud Drive/folder-sync, a
>       LAN/P2P channel, or a CRDT engine) and must survive both machines
>       editing offline. Do not bolt on a cloud account.

> **2026-08-12 — founder-requested features (Hamza, verbal). Both OPEN.**
> - [ ] 🟠 **Bring-your-own transcription model (on-device):** evaluate
>       **Cohere Transcribe 03-2026** (2B, 14 langs incl. Arabic, Apache 2.0,
>       leads Open ASR leaderboard at 5.42% WER) and **Qwen3-ASR 0.6B/1.7B**
>       (52 langs incl. dialectal Arabic, Apache 2.0, MLX port + sherpa-onnx
>       support — same models would serve the Windows native rewrite) as
>       pluggable engines beside Whisper. **Rollout per founder: Hamza tests
>       first, friend gets it after.** Phase-0 spike gates it (half-day, run
>       both on a real dual-channel recording from this Mac): segment-timestamp
>       quality (the Me/Them turn pipeline needs it), a vocabulary-biasing
>       equivalent (our glossary rides Whisper `initial_prompt`), Arabic +
>       code-switch quality vs large-v3, silence behavior, RAM/speed. The
>       registry is already backend-keyed (`transcriber.py` — MLX vs CT2), so
>       a new engine is additive, and nothing may auto-download (SPEC V2/V3).
>       Trigger: a friend already had a Whisper model and didn't want a second
>       multi-GB download; he prefers Cohere's model.
> - [ ] 🟠 **Rename an attendee and propagate through the meeting:** misheard
>       name (real case: "Danish" transcribed as "dhanesh") should be fixable
>       once, in the attendees row, with every reference following — attendee
>       chip, speaker labels in `transcript_turns`, occurrences in the flat
>       transcript + turn texts + summary (word-boundary, case-preserving —
>       REUSE the deterministic vocabulary-correction logic from 08-02, which
>       already fixed the word-swallowing/casing traps), plus offer the
>       existing add-to-dictionary flow so FUTURE meetings hear it right.
>       Precedent that retroactive rewriting is safe/supported:
>       `merge_meeting_speakers` (`commands.rs:4304`) already rewrites all
>       turns + flat transcript in one IPC command. UI: attendee chips are
>       add/remove-only today (`NoteViewer.tsx` `persistAttendees`) — rename
>       is the missing affordance.

> **2026-08-11 — from the adaptive-`num_ctx` work (summarizer.py). Both OPEN.**
> - [ ] 🟠 **The Python service never calls `logging.basicConfig`**, so the root
>       logger stays at WARNING and **no `logger.info` from `src.*` ever reaches
>       the log** under `uvicorn --log-level info` (that flag configures uvicorn's
>       own loggers only). Every diagnostic INFO line we add — including the new
>       `Context sizing: adaptive: … (bound by …)` line, which exists precisely so
>       a field problem can be diagnosed without telemetry — is invisible in
>       production. FIX: one `logging.basicConfig(level=INFO)` at service startup
>       (`run_service.py` / `server.py`). See LESSONS_LEARNED 2026-08-11.
> - [ ] 🟡 **Behavior change to watch on small machines:** the truncation retry is
>       now capped by the RAM tier instead of a hard-coded 32768, so a `<16 GB`
>       box stops at 16384 and no longer retries upward. Deliberate (a notetaker
>       must not evict everything else), but if 8 GB users report incomplete notes
>       on long meetings, this is the knob — and the honest answer is likely "pick
>       a less verbose model", which the failure copy already says.

> **2026-08-05 — NEW, verified in code, ALL OPEN. Any one of the first three can
> kill the Windows sidecar on every launch (the "Local AI is not reachable"
> report). `config.py`, `server.py`, and `transcriber.py` were untouched by the
> 08-05 fix commit.**
> - [x] 🔴 **FIXED 2026-08-05.** `python-service/src/config.py` hardcoded the macOS data path
>       in the frozen branch, with no platform switch, and runs it at import
>       time** (`PROMPTS_DIR = _resolve_prompts_dir()`, line 101). On Windows the
>       sidecar uses `C:\Users\<user>\Library\Application Support\meeting-note-taker\prompts`
>       — a legal but nonsense path that Rust's `%APPDATA%\meeting-note-taker`
>       (`config.rs:20-23`) never reads. Rust never supplies
>       `ADVERSARIA_DATA_DIR` (only `HF_HUB_DISABLE_XET` +
>       `ADVERSARIA_PARENT_GUARD`, `commands.rs:195-204`), so the override is
>       always absent in production. **This is a second, independent cause of the
>       "my todo template is not there" report below** — Windows templates are
>       seeded to a phantom folder. And because the `mkdir` is unguarded at import,
>       any failure there kills the sidecar on every launch. FIX: platform-aware
>       base (`%APPDATA%` on win32), and wrap the `mkdir` so an unwritable target
>       degrades to the bundled read-only prompts instead of aborting the import.
> - [x] 🔴 **FIXED 2026-08-05.** `server.py`: the parent-death guard hard-exited on ANY
>       stdin exception. `try: sys.stdin.buffer.read() except Exception: pass` falls
>       through to an unconditional `os._exit(0)`, so an unusable stdin is an
>       instant, repeatable suicide loop — mislogged as "Parent process closed
>       stdin". The Windows build is `console=False`, and `run_service.py:26`
>       repairs only stdout/stderr, never the stdin the guard depends on. FIX:
>       exit only on a clean EOF (`read()` returning `b""`); log and return on an
>       exception; add `stdin` to `_ensure_stdio`.
> - [x] 🟠 **FIXED 2026-08-05.** `transcriber.py` imported `faster_whisper` at module scope, and
>       `server.py:44` imports that module at module scope, so a clean Windows box
>       missing the MSVC runtime dies before uvicorn binds instead of degrading.
>       FIX: move the import into the transcriber constructor so the service still
>       binds and reports `transcriber_state = error`. (`_patch_cuda_path()` runs
>       from the constructor at `transcriber.py:1059` — far too late to help.)
> - [x] 🔴 **FIXED 2026-08-05.** The to-do digest could not be turned off — `src-tauri/src/reminders.rs`
>       fires an OS notification for due/overdue action items with **no config
>       gate whatsoever**: once ~20 s after launch (`INITIAL_DELAY`) and again when
>       the clock crosses 09:00 local. There is no `AppConfig` field for it
>       (`types.rs` has only `meeting_reminder_enabled` / `_minutes`, which belong
>       to the *pre-meeting* alert in `meeting_reminders.rs` — a different module).
>       A user who does not want to-do notifications has no way to stop them.
>       FIX: add `todo_digest_enabled` (default true, to preserve current
>       behaviour) + `todo_digest_hour`, gate the loop in `reminders.rs`, and
>       surface both in Settings. Small and self-contained.
> **How the four above were fixed (`0c3…`, 2026-08-05):** `config.py` gained
> `_packaged_data_dir()` (%APPDATA% on win32, Application Support on darwin,
> XDG on linux) matching `config.rs::app_data_dir`, and `_resolve_prompts_dir`
> now degrades to the read-only bundled templates instead of raising at import.
> The stdin guard exits only on a clean EOF and logs-and-returns otherwise;
> `stdin` was deliberately NOT added to `run_service._ensure_stdio`, because a
> devnull stdin returns EOF immediately and would cause the very suicide loop
> being fixed (the earlier note here recommending that was wrong). `faster_whisper`
> moved into `_create_model` behind `TYPE_CHECKING`. The digest is gated on new
> `todo_digest_enabled` (default **true** — it shipped ungated, so defaulting to
> false would silently remove a notification users already get) + configurable
> `todo_digest_hour`, re-read every loop iteration so Settings takes effect
> without a restart. Gates: pytest 389 · cargo 203 · vitest 111 · tsc · clippy ·
> fmt · ruff check.
>
> - [ ] 🟡 **Notification settings are scattered and one default is wrong in the
>       UI** — found while redesigning Settings. There are FOUR notification
>       surfaces: `auto_detect_meetings` (master switch for the record offer),
>       `meeting_alert_style` (`notch_drop` / `pill_nudge` / `off`),
>       `meeting_reminder_enabled` + `_minutes` (pre-meeting, **off by default**),
>       and the ungated to-do digest above. Today they live in two different tabs
>       (Recording, General) under labels no one searching for "notifications"
>       would scan — Hamza could not find the record prompt at all. The prototype
>       gathers all four into one **Notifications** section.
> - [x] 🔴 **FIXED 2026-08-07 — "Transcribe: Needs attention" with a model on
>       disk.** Reported from Hamza's Windows office machine, which had large-v3
>       downloaded. Cause was mine: `SetupStatusSection`'s else-branch treated an
>       ABSENT `transcriber_state` the same as `"error"`, so an unknown rendered as
>       a fault — and it renders before the first `/health` reply lands, and on any
>       service predating V3. Now `undefined` → "Checking…" with a new neutral
>       `unknown` tone (grey, and deliberately NOT counted toward the overall
>       badge: amber during a normal startup teaches people to ignore amber), and
>       it raises no issue. A real `error` now says "The model on this computer
>       wouldn't load" and prefers the SERVICE's own reason over our guess — the
>       old copy could tell a machine with a downloaded model that no model was
>       downloaded. Two tests pin both halves.
> - [ ] 🟠 **STILL UNKNOWN: why the Windows transcriber errors at all.** If Hamza's
>       machine reports `transcriber_state: "error"` (not merely unknown), the
>       reason is in `%APPDATA%\meeting-note-taker\logs\adversaria-service.log` —
>       `_init_transcriber` logs the traceback via `logger.exception("Transcriber
>       init failed")`. Since 0.3.73 moved the `faster_whisper` import into
>       `_create_model`, a missing MSVC runtime now surfaces HERE as an errored
>       transcriber instead of killing the service, so this may be the same
>       underlying DLL problem wearing a new face. **Get that traceback before
>       changing anything.**
> - [x] 🔴 **FIXED 2026-08-08. `publish-release.sh` exits 0 when an asset upload fails** (hit while
>       shipping 0.3.74, 2026-08-06). A DNS drop mid-publish failed the 880 MB DMG
>       upload AND the draft cleanup, and the script still returned success — so
>       the release sat as a DRAFT with 2 of 4 assets while the tooling reported a
>       finished ship. Only checking the live manifest caught it. `gh release
>       upload`/`create` results are not tested; add `set -o pipefail` discipline
>       and fail loudly, because the one thing a publish script must never do is
>       claim success. (No user impact that time: GitHub does not serve draft
>       releases through `/releases/latest`, so 0.3.73 stayed Latest.)
>       **FIX (2026-08-08):** the script now creates a DRAFT, diffs uploaded
>       assets via `gh release view --json assets`, deletes the draft on any
>       miss, undrafts with `--draft=false --latest`, then runs the new
>       `scripts/verify-published.sh` — a verifier that can genuinely FAIL
>       (live manifest version, re-downloaded SHA-256 vs provenance, REAL
>       minisign verification via a locally-compiled `minisign-verify`, per-
>       check PASS/FAIL summary). Missing DMG / macOS-only now hard-fail unless
>       `--allow-missing-dmg` / `--allow-macos-only`. Live-proven on v0.3.75:
>       macOS bytes match provenance, both platform signatures verify; the
>       wrong-tag sabotage drill exits 1. The Windows exe's hash is now recorded
>       into channel provenance at publish time (0.3.75's never was — that gap
>       is permanent for that release and honestly reported by the verifier).
>       Recovery that worked, worth keeping: upload the missing assets to the
>       existing draft with `--clobber`, verify the manifest already in it, then
>       `gh release edit <tag> --draft=false --latest` — no need to re-upload the
>       1.6 GB that already landed.
> - [x] 🟡 **RESOLVED 2026-08-06 — and it was NOT data loss.** A spool whose channel manifest is missing was an infinite retry dead
>       end** (reported 2026-08-06 from the friend's Windows machine:
>       `Could not read recording manifest: The system cannot find the file
>       specified. (os error 2)` alongside "press Transcribe now to retry").
>       `prepare_for_transcription` (recording_spool.rs:445-452) checks only that
>       the path is a directory ending `.adversaria-spool`, then reads
>       `manifest.json` and surfaces the raw OS error. There is NO handling for
>       "the spool directory is there but its manifest is gone", so the UI keeps
>       inviting a retry that can never succeed for that recording. **Fix the
>       advice before the cause:** detect an unreadable/incomplete spool and say
>       the recording cannot be recovered (and why), instead of an `os error 2`
>       plus a button that will fail forever.
>       Likely how it got that way, unverified: `remove_recording` (:713) uses
>       `remove_dir_all`, which on Windows can fail partway through when a file is
>       locked or has been quarantined — leaving the directory behind after the
>       manifest has already gone. Aggressive security software is the leading
>       suspect on that machine, since the service exe appears to be blocked too.
>       Worth making the removal tolerant of partial failure and idempotent.
>       **2026-08-06 — WIDER THAN ONE MACHINE.** Hamza's own dev log shows at
>       least EIGHT spools failing recovery with `Could not read system recording
>       manifest: No such file or directory (os error 2)` — the CHANNEL manifest
>       (`system.json`, recording_spool.rs:528) this time, not `manifest.json`.
>       So this is not one friend's antivirus; something routinely leaves spools
>       without their manifests on a healthy Mac. Investigate what writes/removes
>       channel manifests before assuming security software. Each of those is a
>       recording the user can never recover, and the UI still offers a retry.
>       **RESOLVED — the diagnosis was wrong and the disk settled it.** All nine
>       spools on Hamza's machine contain ONLY `manifest.json`: `state=pending`,
>       `channels: []`, **zero bytes of audio**, created 24-25 Jul, and **no
>       meeting row references any of them**. They are not recordings that lost a
>       manifest — they are starts that captured nothing (a channel is only
>       recorded on `finish`). Every launch then re-marked them pending (all nine
>       `updated_at` were identical: the recovery pass that night), failed to read
>       a channel manifest that was never written, and logged it as an
>       "authentication failure" — forever, with nothing to recover.
>       FIX: `recording_spool::is_empty_capture` + a guard in `recover_recordings`
>       that discards such a spool before re-marking it, gated twice (no audio AND
>       no meeting points at it). Six tests pin the NO cases — a channel manifest,
>       a single recorded byte, a subdirectory, and an unreadable directory all
>       mean "leave it alone", because over-deleting costs a recording and
>       under-deleting costs an empty folder.
>       **ALSO RESOLVED 2026-08-06 — the friend's case now tells the truth.** A
>       missing channel index is terminal (the encrypted records cannot be read
>       without their nonce prefix and format), so `decrypt_channel` returns a
>       message led by `recording_spool::UNRECOVERABLE_PREFIX` naming the likely
>       cause, and `useRecording` no longer appends "the recording is safe — press
>       Transcribe now to retry" to it. Other I/O errors stay retryable: a locked
>       or briefly unreadable file is a different problem from an absent one, and
>       suppressing a retry there would lose a recoverable recording. The phrase
>       lives in one Rust constant mirrored by `src/lib/recordingErrors.ts`, with a
>       test on each side so they cannot drift.
>       NOT done: the "Not transcribed yet" panel still shows a Transcribe-now
>       button for such a meeting. Hiding it needs the recording asset's state
>       plumbed to the frontend, which is not exposed today — worth doing, but a
>       bigger change than the message.
> - [ ] 🟡 **"Can't download the local model" is not a separate bug** (same
>       report). `start_model_download` is an HTTP call to the Python sidecar
>       (`http_client.rs:399` ← `commands.rs:4580`), so with the sidecar down the
>       download cannot start at all. The UI should say the local AI service has
>       to be running before offering a download, rather than letting the user
>       press Download and watch nothing happen. Same root cause as Local AI
>       Offline — do not chase it separately.
> - [x] 🟠 **FIXED + DEPLOYED 2026-08-06. The website served the macOS DMG to Windows visitors** (reported by
>       Hamza 2026-08-06 from his Windows machine). The Download button hands over
>       `Adversaria-macos-arm64.dmg` regardless of platform, so a Windows user
>       downloads a file they cannot open — a pure conversion loss on the one page
>       that matters. Both stable asset names already exist on every release, so
>       the fix is platform detection on the button, not new build work:
>       macOS → `.../releases/latest/download/Adversaria-macos-arm64.dmg`,
>       Windows → `.../releases/latest/download/Adversaria-windows-x64-setup.exe`.
>       Offer both explicitly rather than guessing only from the user agent, since
>       a Mac user on a work PC still needs the other file. The site lives in the
>       separate `lagharilabs-website` repo, not here.
>       **DONE** (`lagharilabs-website` 25d5c59, deployed to Cloudflare Pages —
>       verified live on lagharilabs.com): the nav and hero CTAs are now
>       platform-aware, the static href stays the .dmg so a no-JS visitor is no
>       worse off, the hero button names the platform it will give you, and an
>       adjacent link always offers the other one. Non-Mac/non-Windows visitors get
>       the releases page instead of a wrong guess. Pages is NOT wired to git for
>       this project — a push does nothing on its own; deploy with
>       `npx wrangler pages deploy dist --project-name=lagharilabs --branch=main`.
> - [ ] 🟠 **Per-field config patching** — prerequisite for the Settings redesign.
>       `updateConfig` round-trips the whole `AppConfig`; a whole-config save while
>       `state.sidecar == None` resets the live base URL to the static
>       `python_service_url` (`commands.rs:4375`), and a background download
>       completion can wipe unsaved edits across tabs. Autosave multiplies both.
>
> **2026-08-04 — reported by Hamza AFTER installing 0.3.72:**
> - [x] 🔴 **Windows: "The model download was interrupted. Check the connection
>       and retry." will not clear** — **FIXED 2026-08-05 (`bc7f1dd`).** The
>       "second hypothesis" was the right one: on Windows `whisper-main`,
>       `whisper-live` and the Settings picker entry **alias one CT2 snapshot**,
>       but their download states were tracked independently, so one alias stayed
>       `state="error"` forever after another had already fetched and verified the
>       shared artifact. `model_setup` now collapses aliases by
>       `(repo_id, revision, allow_patterns)` and a losing duplicate worker can no
>       longer overwrite a verified state with its late network error. The
>       tray-quit theory was wrong; the restart-surviving channel was `/health`'s
>       `transcriber_detail`, recomputed from disk on every boot
>       (`server.py:204`). Shipped 0.3.72 also had **no engine gate at all** in
>       the chrome, so a self-hosted user was shown local-model failures —
>       now gated.
> - [ ] 🟠 **No force re-download** (carried over, now believed load-bearing):
>       `start_model_download` early-returns on a `ready` profile, so a
>       corrupt-or-partial-but-cached model can never be re-fetched from the UI.
>       This is the most likely reason a stuck download feels permanent. Needs a
>       `force`/reset path in `model_setup.py` that clears the profile and any
>       `blobs/<sha>*.incomplete` leftovers.
>       **2026-08-08 — HALF DONE:** `model_setup.reset_model_download()` +
>       `POST /setup/model_download/{id}/reset` exist with pytest coverage
>       (clears `*.incomplete`, resets to pending/can_retry), and
>       `start_model_download` auto-clears zero-byte incompletes on retry from
>       an error state. STILL OPEN: no UI button calls the reset endpoint yet,
>       and a `ready`-but-corrupt profile still cannot be re-fetched (reset
>       does not clear a ready state). Wire the button + the ready-state force
>       path before calling this closed.
> - [ ] 🟡 **"My todo template is not there"** — it IS installed and served
>       (`/templates` returns `brain-dump`; the file is 6,209 B on disk). It
>       renders as **"Brain dump"** since template names are now display-
>       formatted, and `NewNoteButton`'s scaffold list (Blank / Meeting prep /
>       Daily standup / Idea dump) is a SEPARATE list that deliberately excludes
>       prompt templates. If Hamza meant that picker, consider surfacing prompt
>       templates there too — two lists both called "template" is the confusion.
>       **2026-08-05 — that diagnosis was made on macOS and is incomplete for
>       Windows.** `config.py:87-93` (above) seeds and saves Windows templates to
>       `C:\Users\<user>\Library\Application Support\…`, so on Windows the file may
>       genuinely be in a folder nothing else reads. Fix the path first, then
>       re-check whether the picker confusion is still the remaining issue. The
>       Settings prototype separates "default template" (a preference) from
>       "edit template wording" (an action) to remove the naming collision.

> **2026-08-03 (evening) — template polish. Built + reviewed; 5 confirmed
> defects fixed by hand after the workflow was stopped mid-verify. SHIPPED in
> 0.3.71/0.3.72.**
> Gates after the fixes: tsc · vitest 107 · cargo 197 + clippy + fmt · pytest 373.
> - [x] 🟡 **Template names rendered as raw slugs** ("one-on-one", "youtube").
>       Display-only `src/lib/templateNames.ts` (the slug stays the API key,
>       `_safe_name` validates it); wired into TemplatesCalendarTab ×2 and both
>       NoteViewer sites, with a generic prettifier for custom templates.
> - [x] 🟠 **`general.md`: TL;DR + due dates.** Needed a cross-layer
>       `meeting_date` (Rust → Python) because the summarizer had NO date
>       context, so "by Friday" could not resolve. Only 42/217 to-dos had a due
>       date before this.
> - [x] 🟠 **New `brain-dump.md`** for the morning ritual: solo monologue, recall
>       turned UP (tentative items count), every bullet a self-contained
>       imperative for Claude/MCP to execute, in the exact shape storage.rs
>       parses into to-do rows.
> - [x] 🔴 **`due:` was swallowed as an assignee** (review, storage.rs): a bullet
>       with no `Owner:` prefix had everything up to the colon claimed as the
>       assignee, leaving the bare DATE as the task text. `split_due` now runs
>       BEFORE `split_label`, and its separator is optional (the LLM drifts off
>       the em-dash form). Same widening mirrored in `src/lib/summary.ts`.
> - [x] 🔴 **A cleared deadline came back** (review, storage.rs `merge_due`):
>       empty was treated as "nothing to protect", so clearing a due in the
>       To-dos tab was silently undone on the next re-summarize. The stored
>       value now always wins for an existing row.
> - [x] 🔴 **The deadline vanished from the note** (review, SummaryView): the due
>       marker was stripped from the bullet and rendered NOWHERE. Now shown as a
>       `badge-due` from the stored column (authoritative — user edits win).
> - [x] 🟠 **DATE CONTEXT went to all 9 templates** (review) though only
>       `general.md` had rules for it. Injection is now opt-in: a template gets
>       the date only if it mentions `DATE CONTEXT`.
> - [x] 🟠 **`brain-dump.md` could never set a due date** (review) — the one
>       template built to feed the to-do list. Given the same deadline rule, and
>       an escape hatch ("(unclear)") so "resolve every it/that" cannot become
>       guessing when the referent is genuinely unrecoverable.
> - [x] 🔴 **STALE PROMPTS — FIXED.** Hamza's packaged app was running
>       `general.md` **frozen at Jun 20** (2,563 bytes vs the repo's 6,353) —
>       under half its size, missing ~6 weeks of anti-hallucination tuning.
>       Cause: seeding copied a bundled template only `if not dest.exists()`, so
>       anything present at first launch was never updated; templates added
>       later (youtube/detailed/interview, Jul 10-11) DID arrive, which is why
>       only some were current. Invisible in dev, which reads the repo folder.
>       FIX (config.py): ownership is now explicit. `save_prompt` and
>       `delete_prompt` claim a template in `prompts/_user_templates.json`;
>       `_seed_bundled_prompts` skips anything claimed and keeps everything else
>       current. Installs predating that record have no ownership data, so a
>       differing file is **backed up to `<name>.bak-<stamp>.md` before being
>       refreshed** — a pre-existing hand-edit is recoverable, never lost.
>       Backups are excluded from `list_template_files` (the name-safety regex
>       rejects them) so they cannot appear in the picker, and are gitignored.
> - [x] 🟡 **Deleting a bundled template now sticks** — `delete_prompt` claims
>       the name, so seeding cannot resurrect it on the next start.
> - [ ] 🟡 **Imported audio is told today's date** (commands.rs ~:1829) — the
>       prompt asserts "Today is <import date> — the date of this recording" for
>       a file recorded weeks ago, so a spoken "by Friday" resolves wrong.
>       Consistent with the row (imports store `recorded_at: now`) and the app
>       has no better date, so LEFT AS IS deliberately. Fix properly only if the
>       true recording time is ever captured.
> - [ ] 🟡 **Relative deadlines have no lower bound** (general.md): "before the
>       15th" spoken after the 15th could resolve into the past. Reviewer-raised,
>       unverified, not fixed.

> **2026-08-03 — transcription BYOK made first-class (Hamza's office DGX runs a
> self-hosted Whisper). Built + reviewed (5 confirmed defects, all fixed);
> SHIPPED in 0.3.71:**
> - [x] 🟠 **Transcription BYOK was dressed as "Groq".** The plumbing was
>       already generic (`transcribe_cloud` POSTs to
>       `{base_url}/audio/transcriptions`, auth header only when a key is set),
>       but the UI called it "Online service", hardcoded the Groq URL/key help,
>       and warned "**not sovereign** — audio leaves your device" even for a box
>       on your own LAN. FIXED: **three explicit engines** — On-device /
>       Self-hosted server / Cloud service — driven by a new
>       `transcription_provider` config field with a tested migration
>       (`classify_transcription_provider`: loopback / RFC-1918 / `.local` /
>       `.internal` / single-label → self_hosted; unparseable → cloud, the
>       conservative side). Hamza's own config (blank URL) classifies local.
> - [x] 🔴 **A false privacy claim was possible** (review, HIGH): switching
>       cloud → self-hosted kept the cloud URL, so the panel said "never to a
>       third party" while still uploading to Groq. FIXED, and hardened past the
>       report: the reassuring copy is gated on the **actual host**
>       (`txOwnNetwork`), not the label the user picked — pick self-hosted and
>       type a public URL and you get a warning instead. The claim cannot lie.
> - [x] 🔴 **API key crossed trust domains** (review, HIGH): the key was never
>       cleared on an engine switch, so a Groq key could be Bearer-sent to the
>       office DGX (and an internal token to Groq). FIXED: the key is cleared
>       whenever the engine changes (not on URL keystrokes — that would fight
>       the user mid-typing).
> - [x] 🟠 **Wizard stamped "self_hosted" on any URL** (review): a pasted public
>       URL inherited "stays on your network" forever. FIXED: the wizard derives
>       the provider from the host and makes the user explicitly confirm a
>       public address before saving it.
> - [x] 🟠 **"Transcription ready ✓" for an endpoint never contacted** (review):
>       a typo'd host finished setup as ready and failed on the first real
>       meeting. FIXED: the wizard probes `{base}/models` before promising;
>       unverified endpoints are named honestly ("Adversaria hasn't reached that
>       address yet") with a save-anyway path.
> - [x] 🟠 **A background download landing wiped unsaved Settings edits**
>       (review): `activateWhisperModel` pushed the whole disk config into
>       Settings state. FIXED: only the field the backend rewrote is merged back
>       over the live in-memory config.
> - [ ] 🟡 **Sovereignty pill still counts any remote endpoint as "not local"**
>       (App.tsx ~:171). Deliberately unchanged — self-hosted IS the user's own
>       infrastructure, so arguably it should read sovereign, but that redefines
>       a shipped indicator. Hamza's call.

> **2026-08-03 — a fresh Windows user finished setup with no model and got
> "No transcription model is downloaded yet" instead of notes. Wizard rebuilt +
> reviewed (5 confirmed defects, all fixed); SHIPPED in 0.3.71.**
> - [x] 🟠 **The wizard made skipping the download the primary action.**
>       "Start using Adversaria" was the primary button, the model download a
>       "Choose & download it in Settings" detour, and the footnote blessed
>       going in without a model. FIXED: `TranscriptionDownloadCard` in
>       Welcome.tsx — model picker with real sizes (platform default
>       preselected), ONE explicit "Download (size)" button that persists the
>       choice then starts it, live progress bar + percent, honest failure with
>       a working action, "Transcription ready ✓" when it lands. Finishing mid-
>       download still works (progress continues in the chrome strip). Founder
>       rule preserved and TESTED: nothing downloads without a click.
> - [x] 🔴 **The wizard could show "Transcription ready ✓" on a machine that
>       cannot transcribe** (found in review). Readiness was `service ready OR
>       weights on disk`, but server.py only reaches `transcriber_state:"error"`
>       AFTER the weights are cached — so the OR *always* won on a truncated
>       snapshot / missing CUDA libs / MLX fallback. Green check, no card,
>       failed meeting. FIXED: an explicit engine error vetoes the fallback.
> - [x] 🔴 **The failure branch was a dead end** (found in review): "Retry
>       download" only restarts *download* errors, so an engine-load failure
>       left a no-op button — and that branch hid the picker AND the Settings
>       link. FIXED: failure detail is a banner ABOVE the picker; every rendered
>       button issues a real request, and the card explains when the service
>       refuses to re-fetch a model it already holds.
> - [x] 🟠 **Unbounded catalogue retry** (found in review): re-probed every 2 s
>       forever when the sidecar never answers — the poll-storm anti-pattern
>       again. FIXED: 5 retries with backoff (~60 s), then an honest message and
>       a working "Try again".
> - [x] 🟠 **Doubled transcription polling** (found in review): the card mounted
>       a second `useTranscriptionSetup()` while App.tsx:74 already ran one.
>       FIXED: App's instance is threaded in as `transcriptionSetup`; a
>       `SelfPolled…` wrapper keeps standalone rendering legal (no conditional
>       hooks). Regression test fails if anyone reverts to a self-mounted hook.
> - [ ] 🔴 **Windows auto-update has NEVER worked — ONE step left, and it is
>       Hamza's.** macOS is fine and always was: the installed 0.3.70 app polls
>       `latest-beta.json` (verified with `strings` on the shipped binary), that
>       asset exists on the release, and it carries a signed `darwin-aarch64`
>       entry. (An earlier note in this file claiming a 404 was reading
>       `tauri.conf.json`'s stable endpoint, not the beta build that actually
>       shipped — corrected 2026-08-03.) Windows had THREE gaps; two are now
>       fixed in this branch:
>       - [x] `scripts/publish-release.sh` wrote a macOS-only manifest. It now
>             emits a `windows-x86_64` entry when `ADVERSARIA_WINDOWS_DIR`
>             points at a CI build's `*-setup.exe` + `*-setup.exe.sig`, uploads
>             the exe under the stable website name, and warns loudly when a
>             release is going out macOS-only.
>       - [x] `.github/workflows/release-windows.yml` uploaded
>             `*-setup.nsis.zip[.sig]`, which this build NEVER produces —
>             `createUpdaterArtifacts: true` re-uses the NSIS installer itself,
>             so the pair is `-setup.exe` + `-setup.exe.sig` (Tauri v2 docs;
>             `.nsis.zip` is the `"v1Compatible"` shape). The `.sig` the
>             manifest needs was therefore never uploaded at all. Fixed.
>       - [ ] **HAMZA:** add `TAURI_SIGNING_PRIVATE_KEY` and
>             `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` to the PUBLIC repo's Actions
>             secrets (`gh secret set …`, never paste the key into a chat).
>             Without it CI takes the `no-updater.conf.json` branch and produces
>             an installer with no updater artifacts at all.
>       Then: build Windows in CI → `gh run download <id> -D /tmp/win` →
>       `ADVERSARIA_WINDOWS_DIR=/tmp/win ./scripts/publish-release.sh "notes"`.
>       UNVERIFIED end-to-end until that secret exists — nobody has ever
>       published a Windows updater manifest from this repo.
> - [ ] 🟡 **GuidedTour suspends exactly when it is most needed**
>       (App.tsx:639 `suspend={transcription.state === "failed"}`) — an
>       engine-level failure is precisely when the user should be walked to
>       Settings › AI Model. Pre-existing; product call, not fixed.
> - [ ] 🟡 **No force re-download** of a model the service already holds:
>       `model_setup.start_model_download` early-returns on a `ready` profile,
>       so a corrupt-but-cached model cannot be re-fetched from the UI. The card
>       now says so honestly instead of looking broken; a real fix needs a
>       `force`/reset path in python-service.

> **2026-08-02 — found diagnosing Hamza's slow/hot machine (verified live on his
> install of 0.3.70; the first two ship to every user). ALL FOUR FIXED
> 2026-08-02, adversarially reviewed — SHIPPED in 0.3.71:**
> - [x] 🟠 **SetupStatusStrip polls all 8 model-download endpoints every 4 s,
>       forever.** Measured: 35,400 of 36,681 sidecar-log lines (96%) in ~13 h on
>       **every installed copy**. FIXED: download-start event bus
>       (`beginModelDownload` in `modelDownloads.ts` pings subscribers at start
>       AND on settle, so a poll can't race the start command); strip idles at a
>       60 s safety heartbeat, `useTranscriptionSetup` fast-polls only while a
>       download is in flight; uvicorn access-log filter drops 2xx GET
>       `/setup/model_download/*` records (errors still log); sidecar log
>       rotates to `.old` at 5 MB.
> - [x] 🟠 **Stale `adversaria-service` sidecars are never reaped** (four dev
>       orphans, ~1.6 GB each; a crash/force-quit orphans users' too). FIXED,
>       belt + suspenders: startup reaper in `commands.rs` (sysinfo; kills
>       name-matched sidecars whose parent is dead — PPID 1 / unrecorded / gone;
>       pure decision fn + 5 unit tests; live-verified against a real orphan
>       while sparing the running app's own pair) + parent-death guard (Rust
>       spawns with piped stdin + `ADVERSARIA_PARENT_GUARD=1`; the service
>       hard-exits on stdin EOF, dev runs unaffected). DEFERRED: Windows
>       llama-server orphan reap (path-matched to the engine dir) — needs a
>       Windows box to even compile-check; notes in HANDOFF.
> - [x] 🟠 **Ollama loads the model without `num_ctx` → 262,144 ctx = 16 GB.**
>       ROOT CAUSE FOUND during review: it WAS the app — with
>       `llm_provider=local` + an Ollama tag, `commands.rs:1989` routes
>       summaries through Ollama's OpenAI-compatible `/v1` surface, which cannot
>       carry `num_ctx` at all, so the guard on the native path never applied.
>       FIXED: every Ollama completion goes through `_ollama_options()`
>       (num_ctx always present), and the summarizer now detects a
>       loopback-`:11434` base_url and serves it with the native Ollama client
>       (chat + stream) instead of the OpenAI path — `num_ctx` applies on the
>       exact config that hit this live. Runner drops ~16 GB → ~7 GB.
> - [x] 🟠 **Custom-vocabulary bias too weak for the product's own name**
>       ("Adversaria" → "Adverse Area", meetings 217–219). FIXED: deterministic
>       post-pass `apply_vocabulary_corrections` (transcriber.py) rewrites
>       fuzzy near-misses of vocab terms on both channels, both backends;
>       Settings copy now nudges exact casing. Adversarial review caught 2 real
>       defects in the first cut — greedy fuzzy windows swallowed short
>       follower words ("Adversaria is" → "Adversaria"), and a lowercase vocab
>       entry downgraded correct casing — both fixed (exact-over-fuzzy at every
>       window size, possessive `'s` peeled and preserved, lowercase entries
>       impose nothing) with regression tests for every reviewer scenario.

> **2026-08-01 — deferred from Setup V3 (scoped out deliberately, bounded):**
> - [ ] **`import_audio` (commands.rs ~:1690) still summarizes before persisting
>       the transcript** — the same ordering bug V3 fixed in `transcribe_meeting`
>       / `transcribe_and_summarize`. Blast radius is bounded: on summarize
>       failure it falls back to a pending meeting with audio kept, which the
>       fixed pipeline + the new transcription drain recover correctly — it just
>       wastes one Whisper run. Same ~20-line reorder when touched next.
> - [ ] **Notes drain fires only on engine-configured events** (per spec). A
>       meeting whose notes failed because the engine was *momentarily* down,
>       with no config change afterwards, waits for the manual "Generate notes"
>       button. Fine for now; revisit if it shows up in support.
> - [ ] Delete stray untracked `src-tauri/src/http_client 2.rs` (macOS copy
>       artifact; not in the module tree).
> - [x] **Updater only checks at launch, silently** (UpdatePrompt.tsx) — an
>       always-running app misses releases for days (bit Hamza on 0.3.70,
>       2026-08-01: no toast until relaunch). FIXED 2026-08-03: `RECHECK_MS`
>       6-hour interval sharing one `runCheck()` with the mount check, stops
>       once an update is found, cleared on unmount (4 fake-timer tests). The
>       quiet "check failed" state is still not surfaced — deliberate, silence
>       is right for offline/dev; revisit only if support needs it.

> **2026-07-29 — Windows findings from Hamza's office box (REPORTED, NOT FIXED —
> he asked for diagnosis only; fix on his word):**
> - [ ] **A real meeting is categorized as "youtube". OPEN — do not "fix" it in
>       the classifier.** Chain: `summarizer.classify_category` returns youtube
>       at `me_ratio <= 0.15`; `transcriber.py:279` promotes that to a *hint*;
>       `resolve_category` lets the hint outrank even the LLM's content
>       classification. So an empty mic channel silently overrules a correct
>       reading of the transcript.
>       **Attempted 2026-07-29 and REVERTED:** guarding `me == 0` → "meeting"
>       breaks `test_diarized_video_is_youtube_not_brainstorm`, which encodes a
>       REAL feature — a muted viewer watching a video has no mic lines either.
>       From the transcript alone the two cases are genuinely indistinguishable.
>       **The disambiguation must come from the capture layer,** which can tell
>       *silence* (mic streamed near-zero frames) from *absence* (mic never
>       captured) — the transcript cannot. Likely fix: Rust passes a
>       "mic channel actually captured" signal and the youtube hint is
>       suppressed when it's false.
>       **Hamza checks tomorrow at the office (07-30): does that meeting's
>       transcript contain ANY "Me" lines?** Zero ⇒ WASAPI capture bug (wrong
>       default input device, or a meeting app holding it exclusively) and the
>       category is just the visible symptom — the bigger loss is his own speech
>       missing from the transcript. Some ⇒ re-tune the ratio instead.
> - [x] **White-on-white dropdowns in Settings (Windows only).** FIXED 07-29
>       (`.settings-select` opaque background + `color-scheme: dark` + an
>       `option` rule, since the OS draws that popup and inherits nothing). macOS renders
>       native `<select>` controls that ignore most CSS, so the dark theme never
>       had to style them; WebView2 paints them, giving OS-default white on our
>       inherited white text. Fix: explicit background/color on
>       `.settings-select` + its `<option>`s, plus `color-scheme: dark` so the
>       native popup follows. Cosmetic, low risk, Windows-only — no reason to
>       hold a macOS release for it.
>
> **2026-07-28 — setup-redesign QA (the redesign itself is implemented, see
> SETUP_REDESIGN_SPEC.md):**
> - [ ] Fresh macOS user account: full 3-screen wizard run; ≥5 GB download bar
>       moves continuously; background sample ✓; reminder fires T−5.
> - [ ] Fresh Windows 11 (no Ollama, non-admin): consent card → engine install
>       (tar.exe unzip!) → llama-server serves → sample passes. **Installer:**
>       CI artifact `adversaria-windows-beta-*` from run 30446906346 (85 MB,
>       expires 2026-08-12; unsigned → SmartScreen "More info → Run anyway").
> - [ ] DECISION (Hamza): add TAURI_SIGNING_PRIVATE_KEY(+password) to the
>       public repo's Actions secrets so Windows builds can sign auto-update
>       artifacts — required for a REAL Windows release with updates; the
>       candidate ships installer-only without it.
> - [ ] Windows box WITH Ollama: its models offered, nothing auto-installs.
> - [ ] Existing-user upgrade: no wizard, settings intact in 5 tabs, no
>       surprise notifications.
> - [x] Merge the public sync PR when its 3 checks are green. (PR #3 merged 2026-07-28)

> **2026-07-15 release-hardening ledger:** current plan execution and external
> acceptance work are tracked in [CODEX_TODO.md](./CODEX_TODO.md). Keep this
> historical product backlog intact; do not use older counts below as current
> release evidence.

> - [ ] 🟠 **DRM course/streaming video blanks while Adversaria records (macOS)
>       — reported by Hamza 2026-08-11, verified by his own A/B test.** A video
>       on Krish Naik's academy site (ed-tech DRM player) disappears the moment
>       recording starts and returns when it stops; a generic screen recorder
>       reproduces it; **Granola does not trigger it and keeps transcribing.**
>       Cause: our macOS system-audio capture is a ScreenCaptureKit stream —
>       even audio-only SCK registers as a screen-capture session, and DRM
>       players blank playback for the viewer when ANY capture session exists.
>       Granola-class apps use Core Audio process taps (macOS 14.4+), which
>       capture system audio with NO capture session — invisible to DRM.
>       THE FIX IS ALSO THE ONBOARDING PRIZE: migrating to audio taps removes
>       the Screen Recording permission entirely (the scariest TCC prompt we
>       have + the restart-asymmetry saga) in favor of the milder
>       "System Audio Recording Only" grant. Capture-layer surgery — spike
>       first (API floor 14.4 vs our min target, DRM-audio tap behavior,
>       aggregate-device + cpal coexistence, migration for existing users'
>       grants), do NOT rush into the launch window. Decision memo:
>       [AUDIO_TAP_MIGRATION.md](./AUDIO_TAP_MIGRATION.md) — CONFIRMED,
>       migrate recommended (~1–1.5 wk, Phase-0 go/no-go spike first).
>       2026-08-11 proving the adaptive-sizing line): the service configures no
>       handler for its own loggers, so only WARNING+ escapes via lastResort —
>       `"Starting ML service lifespan"` and the new `"Context sizing:
>       adaptive…"` line are invisible in dev logs AND the packaged sidecar
>       log, which the diagnostics bundle ships. Diagnosability polish: give
>       the app logger a real handler/level at startup (mind the uvicorn
>       access-log filter and the 5 MB rotation), then verify the sizing line
>       lands in `adversaria-service.log`.

Legend: 🔴 correctness bug · 🟠 high-impact feature · 🟡 nice-to-have · 🔵 infra/distribution

---

## 🪟 2026-07-27 — Windows port follow-ups

The port itself is built and green on Windows (see
[HANDOFF.md](./HANDOFF.md) "Last session (2026-07-27)"). These are what it left open.

- 🔴 **Smoke the frozen sidecar — it has never been executed.** The dev box
  refuses to launch the PyInstaller exe (`Access is denied` from every shell,
  sandbox off, while trusted exes in the same tree run). Defender is disabled
  there, so a third-party EDR is the likely cause. Until it runs, `console=False`
  + the `_ensure_stdio()` guard, the CUDA-from-frozen-bundle path, and clean
  shutdown are all **unproven**. Start it by hand, `curl /health`, then confirm
  via Task Manager that quitting the app leaves no `adversaria-service.exe`.
- 🔴 **PyInstaller exes get heuristically flagged by EDR** — the block above is
  a real user-facing failure mode, not just a dev-box quirk. It is a second,
  independent argument for code signing beyond SmartScreen.
- 🟠 **Windows ships CPU-only today — decide how GPU gets delivered.** Bundling
  CUDA makes the sidecar 2.4 GB (1.9 GB of it 15 CUDA DLLs) and **NSIS cannot
  package it at all** (~2 GB ceiling; MSI is no better). See LESSONS. The
  installer therefore defaults to `ADVERSARIA_BUNDLE_CUDA=0`. Options, best
  first:
  1. **Download the CUDA runtime on first run** into the app-data dir and add
     that dir to `_patch_cuda_path()`. Consistent with how model weights already
     work (deliberately not in the DMG), keeps the installer small, and gives
     GPU users the full path. **Recommended.**
  2. Trim cuDNN to only what CTranslate2 loads — but this must be validated on a
     real GPU by asserting `device == "cuda"`, because a wrong guess degrades to
     CPU *silently*.
  3. Ship two installers (CPU / CUDA), with the CUDA one distributed as a zip
     rather than an NSIS installer.
  Note today's fallback already works for anyone with the **NVIDIA CUDA Toolkit**
  installed — `_patch_cuda_path()`'s Toolkit branch is the one that still
  functions when frozen.
- 🔵 **Write `scripts/sync-public.sh`.** The repos have no shared history, so
  workspace-only commits are **never linted on Windows** — the permissions work
  had a `-D warnings` error sitting in `open_privacy_settings` that CI could not
  have caught. Every unsynced commit is unlinted on the platform it most affects.
- 🟠 **Windows live captions run the full large-v3.** `_build_live_transcriber`
  guards on `isinstance(..., MlxWhisperTranscriber)` and falls back to the main
  model, so captions work but lag. Giving Windows the turbo model means a second
  CUDA model resident — fine on the 5090, an OOM risk on a modest GPU. Needs a
  VRAM check or an explicit setting, not an unconditional second model.
- 🟡 **`permissions.rs` claims Windows has no mic gate — that is only half
  true.** Loopback needs nothing, but Settings → Privacy → Microphone → "Let
  desktop apps access your microphone" will make WASAPI mic capture fail while
  the Windows stub reports `Granted`. Mic capture is best-effort, so the meeting
  still records system audio and the user is never told why "Me" is missing.
- 🔵 **Decide code signing.** Azure Artifact Signing (~$10/mo, instant SmartScreen
  reputation) is likely **not available from the UAE** — eligibility is US/CA/EU/UK.
  Confirm before betting on it; otherwise OV (~$200–450/yr) or ship unsigned with
  a documented "More info → Run anyway" step.

---

## 🎯 2026-07-25 — CRM ARC + OPEN-SOURCE / MONETIZATION DIRECTION

**Context (2026-07-25):** after trying HeyClicky the user reassessed direction.
Verified: **HeyClicky is not a competitor** — it's a screen-aware AI teaching
assistant + voice-spawned agents (Claude + AssemblyAI + ElevenLabs, cloud;
screenshots leave the machine, "basic text summaries" retained), $0/$20/$100 mo,
25k+ users, by Farza of buildspace. Zero overlap with bot-free on-device meeting
capture. What it demonstrates is **craft + distribution**, and that people pay
$20/mo for a Mac AI utility. Full competitive read belongs in
[marketing_strategy.md](./marketing_strategy.md) (not yet written there).

**SHIPPED this session** (commits `f39bb2c`, `cde6d9b`, `1c9251c`):
- Contact details on person profiles (email/phone/LinkedIn) + graph search +
  role/company prefill from what the meeting said.

**Next, in rough priority order:**

- 🟠 **People tab.** A person is currently only reachable by clicking a graph
  node — a discovery dead end. A list view is the single biggest unlock now that
  profiles carry contact details.
- 🟠 **Last-contact + going-cold nudge.** Every meeting already has a timestamp
  per person; surface "last spoken N days ago" and a nudge. ⚠️ The user notes
  this is **useless for his own meetings and essential for sales users** — build
  it for the sales persona, don't force it on everyone.
- 🟠 **Sales-call prompt template** (`python-service/prompts/sales-call.md`).
  Contact + company, pain described, current solution, budget/authority/timeline,
  objections, competitors mentioned, explicit next step with owner + date.
  Templates are just markdown files discovered dynamically — cheapest possible
  vertical.
- 🟠 **CRM export.** Do the dumb version first: formatted summary to clipboard +
  CSV/JSON. Works with every CRM on day one, no API keys, nothing leaves unless
  the user pastes it. Real HubSpot/Salesforce/Attio integrations come later and
  MUST be explicit opt-in, summary-only — never audio or transcript.
- 🟡 **Company as a first-class entity** — "everyone I know at Fluence Pay".
- 🟡 **More vertical templates:** legal intake (parties, matter ref, facts
  asserted, limitation dates, advice given, conflicts check — strongest moat,
  privilege makes cloud upload a liability; needs a real lawyer to review),
  recruiting scorecard, research/UX interview. **Clinical/therapy (SOAP/DAP) is
  high value but highest burden** — HIPAA, BAAs, audit trails; hold until another
  vertical is proven and a clinician shapes the template.
- 🟡 Pipeline/deal stages — only if actually going after sales teams.

**Monetization direction (discussed, NOT decided).** Sovereignty does not block
revenue: you sell the app, not inference. The segment cloud competitors are
structurally locked out of — law, healthcare, finance, government, defense —
currently just doesn't record meetings at all. Three thesis-compatible revenue
lines: (1) paid commercial license, free for personal; (2) **end-to-end
encrypted team sync** — the one hosted thing that doesn't contradict "nothing
leaves your machine", because what leaves is ciphertext the server can't read
(Obsidian Sync model); (3) org deployment — MDM package, policy, audit log, SSO.
**Rejected:** a hosted cloud freemium tier competing with Granola on convenience
— that surrenders the moat. See [DECISIONS.md](./DECISIONS.md) if/when this is
ratified as an ADR.

**Open question the user raised and has NOT answered: team sharing.** How do a
bank / law firm / hospital / sales team share meeting notes and client records
while individual consultants use it free? That's the shape of the paid tier and
it's undesigned.

---

> **⚠️ 2026-07-25: the section below is largely SUPERSEDED.** Most of the
> setup-wizard churn bundle shipped in 0.3.60 (seamless first-run: auto model
> downloads, one combined progress bar, no manual retries, sidecar-boot wait).
> It has not been reconciled item-by-item — verify against the live wizard before
> treating any 🔴 below as open.

## 🎯 2026-07-18 (night) — SETUP-WIZARD CHURN BUNDLE (clean-machine test on the 8 GB MacBook)

User's own first-install run of the notarized 0.3.49 surfaced these; his words:
"I don't want people to churn on the setup." Priority-ordered; fix as ONE
bundle (frontend Welcome.tsx + wizard flow; needs refreeze + re-notarize):

- 🔴 **Model download blocks the whole wizard** — can't proceed past step 4
  while 3.1 GB downloads; no background-continue. Fix: download continues in
  the background, wizard advances (gate only the first transcription on it).
- 🔴 **No progress/ETA on the download** — "5 minutes and not downloaded" is
  indistinguishable from a stall. `model_download_status` already returns
  aggregate progress (http_client.rs:218) — show %, MB, and a
  slow-connection reassurance line.
- 🔴 **Sidecar boot has no UX** — first launch Gatekeeper-verifies the 1.4 GB
  sidecar (minutes, one-time); the wizard just errors "service not ready;
  retry" (http_client.rs:208). Fix: inline "Verifying the app bundle —
  first launch can take a few minutes…" state with auto-retry.
- 🔴 **Wizard modal blurs the app** — the "Local ML Service" status pill is
  invisible behind it; surface service status INSIDE the wizard.
- 🟠 **Pre-existing Ollama models neither detected nor explained** — user had
  pulled Qwen 4B via Ollama; wizard still (correctly — bundled Rapid-MLX is a
  separate runtime) downloads the pinned meeting model but never SAYS so.
  Add one line of copy; optionally detect Ollama and mention it.
- 🟠 **Registration step retries forever on endpoint-less builds**
  (registration.rs:98) — hide/skip the step when no endpoint is compiled in;
  bake the production Formspree endpoint into release builds.
- 🔵 Verified NOT the cause: hf_xet stall — packaged spawn sets
  `HF_HUB_DISABLE_XET=1` (commands.rs:119); notarized sidecar entitlements
  intact. Worth adding: download resume-on-relaunch verification.

Round 2 of the same test (post-model-download), two 🔴 FIXED in 0.3.50:
- ✅ **ffmpeg dependency** — every transcription failed on the fresh Mac
  (`[Errno 2] ... 'ffmpeg'`): MLX `_collect_segments` passed a PATH so
  mlx-whisper shelled out to a system ffmpeg (Homebrew-only). Now decodes
  in-process via the existing PyAV `_decode_to_mono16k` (transcriber.py:1145).
- ✅ **Mic prompt never appeared** (app absent from Privacy → Microphone, level
  bubble flat): main app was hardened-runtime-signed with NO
  `com.apple.security.device.audio-input` entitlement → macOS never asks on
  fresh machines (dev Macs masked it via pre-hardening TCC grants). Fixed:
  NEW `src-tauri/entitlements-app.plist` + `sign_file --entitlements` on the
  main app (build-dmg.sh:164). Needs mic RETEST on the clean machine.
Still open from round 2 (wizard-bundle additions):
- ✅ **DONE 2026-07-25 (`cbd8e62`)** — ~~🔴 Permissions step in setup~~ — request mic + screen-recording (with the
  why) during the wizard, not lazily at first record. MUST also handle the
  STALE/DECLINED TCC state (Settings shows the toggle ON for an older copy
  while the running copy is declined — hit on the clean machine after the
  Gatekeeper move dance): detect `NoShareableContent`/declined, and guide
  `tccutil reset ScreenCapture|Microphone com.meetingnotetaker.app` + toggle
  re-grant + restart instead of surfacing the raw error string.
- 🟠 **Guided "record your first meeting" tutorial** right after setup (user's
  churn-killer idea).
- 🔴 **Failed capture start must surface immediately** — on the clean machine
  a record attempt with dead screen-capture let the user believe it recorded
  for 2 minutes, then said "not recording" only at stop. Start errors need a
  blocking dialog at press time, and the record UI must not enter the
  recording state when the backend refused.
- 🟠 **Permissions copy must state the restart asymmetry** — mic grants apply
  instantly, screen-recording grants require a full app restart; the wizard
  and the grant-error dialog should both say so.

Round 3 (2026-07-19 morning, same dev-signed 0.3.50 on the test Mac — LOGGED
ONLY, user still testing, no fixes yet):
- 🔴 **"Not recording" at stop while audio WAS being spooled** — a mic-only
  recording (worked fine the night before, incl. YouTube) said "not
  recording" at stop; after force-quit + relaunch an UNTRANSCRIBED RECORDING
  appeared — i.e. capture ran and spooled while the app's recording state
  said otherwise. State desync between the recording flag and the live
  capture session (stop-flag race family; relates to the open recovery-scan
  quarantine item). Key repro note: intermittent ACROSS app sessions, not a
  permissions problem (grants were settled and working the previous night).
- 🔴 **Setup name never reaches Settings** — the wizard's name field was
  filled, but `user_name` stayed empty in Settings and the app refers to the
  user as "Me". Wire Welcome.tsx's name input → config `user_name` (it feeds
  relabel_me, Insights owner resolution, vault notes — silently degrading
  several features when lost).
- 🟠 **Live-caption lag on low-RAM hardware** — on the 8 GB MacBook the live
  transcript ran minutes behind (user accepts, but): consider a smaller live
  model / lower cadence on low-memory machines, and show a "captions are
  catching up" hint instead of silent lag.
- 🔴 **Recording while a final transcription runs starves the live pipeline —
  and MISFIRES the silence watchdog.** Meeting #1 still final-transcribing;
  user started recording #2: recording animation fine, but 5 min of loud
  continuous speech produced ZERO live transcript, and the "is anybody
  there?" silence prompt fired — a false positive. Likely GPU/model
  contention (large-v3 final job starving /live_feed). HAZARD: the silence
  watchdog feeds the auto-discard flow — a REAL meeting recorded during a
  long transcription could be flagged (or discarded) as silent. Fixes to
  weigh: silence detection must key on AUDIO ENERGY, not caption presence ·
  live feed gets priority/queue fairness vs final jobs · or defer final
  transcription while a recording is live. (User is verifying whether both
  meetings eventually transcribe correctly.)
- 🟠 **Queued recording had no Transcribe button** until app restart (recovery
  scan / stuck-pending UX — relates to the existing quarantine follow-up).
- 🟡 **Spotlight doesn't find the app** after drag-install on the clean
  machine (LaunchServices/mdimport? investigate CFBundleDisplayName).

## 🚨 2026-07-19 — 8 GB is UNSHIPPABLE as-is: 30 min to process a meeting (LAUNCH BLOCKER)

- 🔴🔴 **A meeting took ~30 minutes to process on the 8 GB M1** (Hamza,
  clean-machine). No user tolerates this; it blocks the friend/Aleph-Alpha
  test and any 8 GB launch. Root: the packaged summarizer model is too big for
  8 GB (dev = qwen3.6:35b 23 GB → swap-to-disk death) + Whisper large-v3 +
  live model, all fighting 8 GB unified memory. **Fix = implement the
  PERF_8GB tiering:** detect RAM (`sysctl hw.memsize`) in the setup wizard →
  on ≤8 GB pin **whisper-large-v3-turbo-4bit (~0.5 GB)** + **qwen3.5:4b
  single-shot (~3.4 GB, EXP-3-validated: ties the 35B)** + never-two-models-
  resident orchestration (load/unload around jobs; queue finals behind live
  recording — also fixes the caption-starvation + false-silence bugs). Target:
  ~30 min → a few minutes. First step: split the 30 min into
  transcribe-vs-summarize and confirm which packaged model 8 GB loads.
- 🟠 **Setup/model-selection UX (Hamza directive 2026-07-20):** make setup
  SIMPLE (one clear recommendation, not two equal option cards) · **DETECT
  models the user already pulled via Ollama** (`/api/tags`) and reuse them
  instead of re-downloading multi-GB · recommend by RAM (infra exists,
  setup.rs) · **recommend ≠ force — Settings must own a model picker so the
  user can change it** (mind the cached-config-at-startup gotcha). Full
  contract: [SETUP_MODEL_UX.md](./SETUP_MODEL_UX.md). Sibling to the perf fix
  above + the wizard-churn bundle.

## 🎯 2026-07-20 — Notch pill + meeting-detected alerts (DECIDED, needs build)

- 🟠 **Ship the notch pill + meeting-detected alerts, user-selectable in
  Settings** (Hamza picked A2+A4+B2+B3). Two config fields:
  `notch_pill_style` (minimal/expressive/hidden) + `meeting_alert_style`
  (notch_drop/pill_nudge/off); consent-first invariant (offers only, ⌘⇧M or
  confirm starts recording). Cheap tier first: B2 minimal + A4 pill-nudge
  (reuse tray.rs/⌘⇧M + a small always-on-top pill window). Bigger lift behind
  the setting: B3 expressive hover-expand "island" (live captions) + A2
  notch-drop. **SCOPED → [NOTCH_PILL_SCOPE.md](./NOTCH_PILL_SCOPE.md): the
  surface ALREADY EXISTS** (recording bubble = a top-center transparent
  always-on-top pill with a live waveform feed; meeting card too; widget
  routing + components + config pattern all present). B2-minimal ~90% built.
  Tiers 1-3 (config+Settings · B2+A4 · A2) = S/M reuse — ship as one
  delegation. Tier 4 (B3 interactive) — **DECIDED 2026-07-20: Option A now,
  Option B later.** **Option A (THE BUILD, ~1 day):** convert the existing
  recording-bubble webview window to a **non-activating NSPanel**
  (tauri-nspanel or ~30 lines objc2-app-kit) — clickable-without-stealing-
  focus, keeps the HTML/CSS pill, transparency VERIFIED safe in packaged
  0.3.50 (#13415 doesn't bite). **Option B (FUTURE update, ~3-4 days):** native
  Swift notch helper as a 3rd sidecar (NotchyPrompter reuse) for exact native
  pixels — full plan on file, ship later. Contract + mockup + scope:
  [SETUP_MODEL_UX.md](./SETUP_MODEL_UX.md) §Notch-pill,
  [NOTCH_PILL_SCOPE.md](./NOTCH_PILL_SCOPE.md).

## 🎯 2026-07-19 — Transcript-junk pre-cleaning (EXP-3 find; attendee-halluc. RETRACTED)

- ❌ **RETRACTED — "summarizer hallucinates attendees" was a MEASUREMENT
  ERROR, not a bug.** The names that looked invented (Dr.Hend/Jamshed/Alaa
  etc.) are REAL attendees in the bundle's `attendees` metadata; the app feeds
  that to the summarizer, so the 35B named them correctly. Both LLM judges and
  the first `faithfulness.py` checked against the transcript only (where the
  garbled audio never spells the names) → false alarm. Corrected checker: 0
  fabrications for every model incl. the 35B. **No attendee-hallucination bug.**
- 🟠 **STILL REAL — the "Me"/mic channel produces transcription junk** that
  pollutes transcripts (and would mislead any downstream reader): caption
  credits ("Teksting av Nicolai Winther", "Subtitles by…"), repetition
  hallucinations ("God of God"), and nonsense food words ("1.5 kg of chicken
  breast") appear on the user's own channel. This is the mic-channel
  hallucination-on-silence family (same root as talk-time inflation /
  vocab-echo, transcriber.py). Fix: strip known caption-credit patterns +
  tighten the mic VAD/hallucination gate so junk never reaches the transcript
  or the LLM. NOT about attendees — about clean transcripts.

## 🎯 2026-07-18 — Insights talk-time attribution (daily-drive find)

- 🔴 **Insights inflates the user's ("Me") talk time** — user shown as top
  talker in a meeting where they spoke least. Verified 2026-07-18; three
  stacked mechanisms (details in the session investigation, artifact
  e1682883):
  1. **Echo bleed (primary, no headphones):** no AEC anywhere in capture
     (`src-tauri/src/audio/macos.rs` — mic is raw cpal; only the app's own
     audio is excluded from system capture). Sole defense is text-dedup
     `strip_mic_bleed` (`python-service/src/transcriber.py:231-265`) which
     never matches utterances < 4 words (`_BLEED_MIN_WORDS`, `:228`),
     needs 0.85 ordered similarity (`:226`), 10 s window (`:227`) — short
     and garbled bleed survives as "Me".
  2. **Fragmentation amplifier (persists with headphones):** diarization
     splits the remote side into Speaker 1/2/3 rows while Me stays whole
     (`stats.rs:60-124` per-label keys, sorted `:161-165`; UI renders one row
     per label, no owner-vs-rest aggregation, `NoteViewer.tsx:1224`). Plus
     `build_labeled_turns` coalescing (`transcriber.py:135-151`) lets Me
     absorb inter-segment silence gaps that the fragmented side doesn't.
  3. **Hallucination leak:** VAD gate keeps the FULL segment span if ≥ 0.5 s
     overlaps voice (`keep_voiced_segments`, `transcriber.py:294-307`) — a
     30 s hallucinated mic segment survives off a cough.
  **Fix ladder:** stage 1 safe (owner-vs-rest aggregation, gap-free
  talk_seconds, clip VAD-kept spans) · stage 2 careful (bleed-dedup tuning —
  touches real transcripts, needs tests) · stage 3 post-launch (real AEC,
  WebRTC-APM-style with system audio as reference). **Decision 2026-07-18:
  tab kept as "Beta" with your-delivery-only content (You vs Everyone-else
  balance + owner-only coaching cards — built, uncommitted). The ladder
  above remains the path out of Beta.**
- 🟡 **Standalone notes — hidden for launch 2026-07-18** (user verdict:
  "crap — fix or hide"). `NewNoteButton` unmounted in `App.tsx`, ⌘⇧N
  unregistered in `tray.rs`; component kept on disk, existing note rows
  still viewable, My Notes/Structure-with-AI/vault export untouched.
  **Finish list if revived (S-B):** note-aware viewer (hide
  Transcript/Insights/Chat/attendees/dictionary/"Regenerate Notes" for
  notes), kill the "· 0 min" card meta (`MeetingsList.tsx:684`), vault
  frontmatter `type: note` (`second_brain.rs:70`), reconcile "New
  Standalone Note"/"New note"/summary-"Notes" naming.

## 🎯 Current — 2026-07-16 (hand-test audit + app-layout)

All on branch **`handtest-hardening`** (not master). Full findings + priority-ordered
fix plan: **[HANDTEST_FINDINGS.md](./HANDTEST_FINDINGS.md)**.

- ✅ **Double-start race — FIXED 2026-07-16, SHIPPED in v0.3.43 (installed &
  verified).** One record toggle could spawn TWO capture sessions 145 ms apart (twin
  spools/`recording_assets` rows, duplicated live captions, older session stranded
  `capturing` — the stuck-spool generator). Both causes fixed: (a) `App.tsx`
  tray/hotkey `listen()` cleanup now chains unlisten off the kept registration
  promises (the old push-into-array pattern leaked the first mount's listeners
  under StrictMode's dev double-mount); (b) `AudioCapture::start()` now claims the
  recording flag atomically (macOS `compare_exchange`, Windows check+set under one
  lock hold) with rollback on spool failure; `useRecording.start()` keeps status
  "recording" when the backend refuses with "Already recording". Related follow-up
  still open: recovery scan should quarantine manifest-less spools instead of
  retrying forever.
- ✅ **Live-caption repetition-loop hallucination — FIXED 2026-07-16, SHIPPED in
  v0.3.43 (the first build to carry the gate live).** "pre pre
  pre …" spam in the live transcript (final transcript was always clean). New
  `is_repetition_loop()` in `live.py` (≥8 tokens, ≤2 distinct → drop) applied in
  `/live_feed` alongside the filler gate; live-preview only, finals untouched.
  pytest 268 ✓.
- ✅ **P0-1 JIT entitlements** — the bundled ML sidecar was `SIGKILL`ed on launch in
  *every* packaged build (llvmlite JIT under hardened runtime) → "Local ML Service:
  Offline". Fixed (`python-service/entitlements.plist` + `allow-jit`). A working
  **NotchyPrompter Dev v0.3.41 DMG** now exists (the ML service actually runs).
- ✅ **P0-2 keychain-denial → app crash** — `lib.rs` no longer `.expect()`s on `init_db`;
  graceful dialog + clean exit.
- ✅ **build-dmg.sh Gatekeeper regression** — `spctl --assess` under `set -e` aborted every
  self-signed build after signing; now non-fatal unless `RELEASE_MODE=1` (`b9be659`).
- 🔴 **Live-transcript auto-scroll** — during recording it stays pinned at the top; user must
  manually scroll to see the latest line. Fix: stick-to-bottom, pause when the user scrolls up.
- 🟠 **Recording-companion view — user picked Option B "even split"** — the narrow,
  docked-while-recording window gets its own layout (it's the real use case, per screenshot):
  ~50% live transcript (auto-scroll) / ~50% notes editor + collapsed header (mark + ⋯ menu,
  no wrap/overflow). Mockups: <https://claude.ai/code/artifact/ed35dc38-d140-44bd-b283-122412266817>.
- 🟠 **Responsive layout** — "crumbles" below ~1024px (header wordmark wraps, tab bar overflows
  to a `>` chevron). Collapse sidebar to a drawer + tighten padding.
- ✅ **Hotkey (⌘⇧M record toggle) — ROOT-CAUSED & FIXED 2026-07-16 (uncommitted; rides the
  next freeze).** NOT a registration failure or conflict: `tray.rs` called `register()` then
  `on_shortcut()`, but `on_shortcut` registers *again* → macOS rejects the same-process
  duplicate (`eventHotKeyExistsErr -9878`) → the handler was silently never attached (error
  swallowed by `let _ =`), so the OS delivered ⌘⇧M/⌘⇧N to the app and the plugin dropped them.
  Fix: `on_shortcut()` only + gate on `ShortcutState::Pressed` (handlers fire on key-down AND
  key-up — ungated, each press would double-toggle). Verified end-to-end in `tauri dev`
  (background ⌘⇧M starts/stops real captures; user's own presses worked). ⚠️ The installed
  v0.3.41 still has the dead hotkey until re-freeze. Full detail in HANDOFF + LESSONS_LEARNED.
- ✅ **Silent recording transcribes the custom VOCABULARY (prompt-echo) — found by the user
  2026-07-16, FIXED same day (rides the next freeze).** A no-speech recording produced
  "[00:00] Tatweer OS, Echelon, Tatweer" (a subset of `custom_vocabulary`) and the summary
  fabricated "Hamza listed three key initiatives". Cause: the vocabulary is Whisper's
  `initial_prompt` (transcriber.py:850/988) and Whisper echoes the prompt on (near-)silent
  audio; the v0.3.41 Silero-VAD gate covered only the MIC track — the SYSTEM track was
  ungated. It also contaminated the HEAD of real meetings (meeting 134 opens with the full
  vocab echo before the video audio starts). Fix: the gate is now generic
  (`drop_unvoiced_segments`) and applied to BOTH tracks in both `transcribe_dual` paths;
  +2 wiring tests through `_merge_dual` (pytest 261 ✓). Python change → re-freeze required
  to reach the installed app. Junk test meetings 136-138 deleted from the DB (backup kept).
- ✅ **Live "Thank you / Thanks for watching" filler hallucinations — GATED 2026-07-16
  (uncommitted; rides the next freeze).** Live pipeline had no confidence filter: VAD
  triggers on breath/noise → turbo-q4 emits Whisper's canonical fillers. Fix (live-preview
  only, finals untouched): `drop_no_speech=True` on the live transcriber (drops
  `no_speech_prob > 0.6` segments) + `is_filler_hallucination()` blocklist in `/live_feed`.
  The *saved* instances were the silent-system-track bug (fixed `16de4fb`; DB-verified all
  on `Them:`). pytest 266 ✓.
- 🟡 **Model tiers** — bake-off verdict: the shipped 4B is *safe* (never fabricated, just lower
  recall), the 27B is *not clearly better* than a 9B; all profiles sit in one band on synthetic
  data → don't restructure tiers without a real **private-corpus baseline** (Codex's open Phase-2 gate).
- 🔵 **Push the 2 CI workflow files** — blocked; needs `gh auth refresh -s workflow`.
- 🔵 **Onboarding model-detection** (detect installed Ollama/HF models so users don't re-download)
  + permissions "Grant + ✓" UX — larger features, scoped in HANDTEST_FINDINGS.md.

---

## 🟠 Next up — user-requested 2026-07-09 (queue after the launch-video work)

1. ✅ **Sidebar declutter BUILT & VERIFIED 2026-07-10 (in dev, UNCOMMITTED) —
   user picked C (pins + auto-archive)** (stunt delegation round 1, $2.24;
   verified by Claude: tsc ✓ · cargo 95 · pytest 207; frontend+Rust only →
   **live-testable in `tauri dev`**, re-freeze only to ship). From 3 sketches at
   <https://claude.ai/code/artifact/9fd91b39-b673-4bb7-81d1-e108cf76fdb8>.
   The build bundles two same-day user reports: (a) **selected-meeting
   highlight** — the open meeting wasn't highlighted in the list
   (`.meeting-card.selected` existed in prototype.css:520 but MeetingsList
   never received the selection); (b) **clear-all-filters** — "Clear filter"
   only reset the date; now clears search text + date + tag pill together,
   shows whenever any filter is active, and the search box gets its own ×.
   Plus: `archive_after_days` config (Settings: Never/14/30/60/90, default
   30; filters/search always span the archive) and attendees added to the
   text-search haystack. Spec: session scratchpad `spec-sidebar-c.md`.
   **Follow-on ✅ BUILT same day — find-by-person (user picked sample 1,
   @person in search):** `@` in the sidebar search → attendee autocomplete
   (meeting counts, generic labels excluded) → removable chips that
   AND-compose with text/day/tag and span the archive. Shipped in v0.3.32
   with the rest.
2. ✅ **BUILT 2026-07-10 (with #3, in dev, UNCOMMITTED) — YouTube → YouTube
   template automatically.** `youtube.md` already existed (v0.3.19); the gap
   was the auto-switch, closed by #3's routing below.
3. ✅ **BUILT 2026-07-10 (in dev, UNCOMMITTED) — category → template
   auto-routing + bidirectional `interview.md`.** Summarize with the default
   template now routes pre-LLM: `category_hint` (mic-bleed, wins) → cheap
   one-word LLM classify over the first 4000 chars (`_classify_category_llm`)
   → me/them heuristic; `route_template()` maps youtube→youtube,
   brainstorm→brainstorm, one_on_one→one-on-one, interview→NEW `interview.md`
   (detects which side "Me" is on: interviewer vs candidate; sections:
   Overview / Questions Asked / Answer Highlights / Red & Green Flags /
   Follow-ups & Next Steps — the last matches the action-item heading regex).
   New `auto_template: bool` on `SummarizeRequest`, set by Rust only where the
   template came from the default (`transcribe_and_summarize`,
   `transcribe_meeting`, `import_audio`; `false` in `resummarize_meeting` +
   `structure_note`) — **manual choices are never overridden**. Fail-open at
   every step. Built via stunt delegation (1 round, $4.58, zero Anthropic
   credits); verified by Claude: pytest 207 · cargo 95 · tsc ✓. ⚠️ Python
   change → reaches the installed app only after a re-freeze.
4. ✅ **read.ai research DONE 2026-07-10 — verdict: build the speech-based
   coaching half; the affective half is impossible-by-design (and that's the
   pitch).** Sources: read.ai support docs + 2026 reviews, all fetched
   2026-07-10 (full sourced report in the session transcript).
   - **read.ai's notetaking layer** (summaries, action items, topics, key
     questions, cross-meeting search) = table stakes Adversaria already
     matches locally. Nothing to chase.
   - **Its signature Sentiment / Engagement / Read Score / Bias / Charisma
     are facial-video metrics** delivered by a bot in the call ("based
     entirely on Read's visual analysis" — their own docs; they strip the
     facial part for EU/UK users). 🔴 DO NOT BUILD — needs other
     participants' cameras + a bot; breaks the thesis and is legally exposed
     (EU AI Act). A text-only "sentiment" would be a weak, over-promising
     proxy — skip or ship only as an honest "transcript tone" label.
   - **The speech-based coaching metrics are all pure arithmetic on data we
     already store** (diarized, timestamped, speaker-labeled segments).
     Ranked build shortlist (value ÷ cost):
     1. **Talk-time panel** — % per speaker, talk-to-listen, longest
        monologue: sum existing segment durations in Rust; zero LLM.
     2. **Pace + filler words** — WPM per speaker (words ÷ speaking secs;
        read.ai target 130–175) + filler-rate dictionary count (<4%); zero LLM.
     3. **Interruption detection** — overlapping segment boundaries
        (B starts before A ends); pure timestamp arithmetic.
     4. **Private "self-coaching" recap + follow-up-email draft** — one
        local-LLM call each (new prompt templates over the computed metrics /
        the summary); analyzes the user's OWN "Me" track only → no consent
        issue. = read.ai's Speaker Coach minus faces, 100% local.
   - **Positioning:** "the coaching, without the creepy" — read.ai's most
     criticized trait (facial analysis of unconsenting participants) is
     exactly what Adversaria's thesis refuses; the useful half costs ~zero
     new ML. Decision pending the user: greenlight items 1–3 (one
     Rust-arithmetic build) and/or 4 (prompt work).

---

## 🔴 DISCOVERED 2026-07-11 — recording is RAM-only until stop: a mid-meeting crash loses ALL audio

Investigating the user's "resume a meeting after accidental close" ask revealed
the capture pipeline buffers raw PCM entirely in memory (`audio/mod.rs:52`,
`StreamState.buffer: Vec<u8>`); the WAV is written only at stop, and no
startup recovery exists. A crash mid-recording = total loss (plus ~GB-scale
RAM on long meetings). Proposed pair (user assessing):
- **A. Crash-safe recording (urgent):** stream PCM to a temp file per channel
  during capture; finalize header at stop; startup scan wraps orphaned
  captures into a pending "Recovered recording" meeting (normal retry queue).
- **B. "Resume recording" on a meeting:** transcript-level append — record a
  normal new session, transcribe, append turns (times offset by prior
  duration, "— resumed —" boundary marker, no cross-boundary interruption
  counting), merge attendees, re-summarize combined (ord-sync preserves user
  edits). Works for already-transcribed meetings (no audio needed — audio-level
  stitching rejected: violates delete-after-transcribe). Disabled while
  queued/transcribing.

## 🎯 ACCURACY DEEP-DIVE — 2026-07-11 (user: "nobody will use it if it isn't ≥95% accurate")

Full plan + evidence: <https://claude.ai/code/artifact/1c9b7964-1a5b-424f-a419-1671169ca478>.
Basis: 9-stage pipeline sweep (40+ failure modes, mitigations cited file:line —
sweep agent report in the 2026-07-11 session) + the live "Presented by Hamza"
experiments (two prompt fixes failed; the structural payload fix verified).
**Doctrine established: accuracy is won at the stage where the error enters;
prompts are advisory, structure is enforceable.**

Ranked plan (greenlights pending):
1. **Bleed-strip v2** — time-overlap + containment scoring (asymmetric bleed
   runs 71–84% similarity, below the current 0.85 symmetric ratio;
   `_BLEED_SIMILARITY`/`strip_mic_bleed` transcriber.py:231-265). Root fix for
   the whole mislabeling class.
2. **Eval harness** (`python-service/eval/`) — replay the real corpus, score
   attribution/numbers/action-traceability per release. Baseline FIRST.
3. **Auto-roster at transcription** — pass the overlapping calendar event's
   attendees as `known_attendees` (the two `TODO: calendar roster` sites,
   commands.rs:327/:530). Accuracy fix + prep step 1.
4. **Bullet-level [MM:SS] citations + hard verify** (Meetily lift, generalized;
   timestamp foundation shipped v0.3.36) — flags uncited/unverifiable bullets.
5. **Long-meeting truncation warning (trivial) → map-reduce (moderate)** —
   context overflow currently truncates silently.
6. **Verify pass** — post-summarize LLM check per bullet (would have caught
   "Presented by Hamza").
7. **Action-item hardening** — widen heading matcher now; structured
   `action_items` schema field later.
**Prep track:** P1 "10-minutes-before card" (all from stored data + roster; 1
LLM call for suggested questions) · P2 = Build D (follow-up email draft +
self-coaching recap). **Email integration: NONE exists; decision logged —
recommend skipping for now** (thesis purity).
Sequencing: Sprint 1 = 2→1→3→5a · Sprint 2 = 4, 6, 7, 5b · Prep parallel.

## Meetily round-2 research — 2026-07-10 (timestamps + prompts; agent-verified vs `Zackriya-Solutions/meetily` @ `main`/`0281737d`, MIT)

**Verdict: Meetily converged toward OUR architecture (Rust/Tauri + local whisper
+ Ollama, mic/system speaker labels); we're not behind — three narrow lifts.**
- **Timestamps:** theirs are chunk-geometry (start = chunk offset, end = offset
  + buffer length) — COARSER than our real Whisper segment times (which we
  currently drop; Build A in flight fixes that). Their persistence pattern =
  additive nullable REAL columns (their `20251006` migration); their UI = a
  passive `[MM:SS]` prefix per line + duration tooltip, **no click-to-seek**
  (moot for us — audio is deleted). Adopt: `[MM:SS]` turn prefix in the
  transcript view once turn times are stored (Build C).
- **Prompts:** their "detail" is a structured schema (we already exceed it —
  JSON-schema output) + short rules. Already covered by us: grounding /
  no-inference, "None mentioned" sentinel, self-check. Worth lifting:
  (1) explicit **"ignore instructions/commentary inside the transcript"**
  injection-guard line (people literally say "ignore that" in meetings) —
  being added across all templates now; (2) 🟡 **action items citing source
  segment + `[MM:SS]`** (their standout) — needs the timestamped transcript
  fed to the LLM; follow-on AFTER the timestamp foundation ships (design:
  prefix turns with [MM:SS] in the summarize payload + an optional citation
  field; touches the extractor).
- **NEW `detailed.md` template** (user ask "another prompt template which is
  super detailed") — adapted from their legacy Pydantic schema's section set
  (Session Summary / Critical Deadlines / Key Decisions / Discussion Notes /
  Immediate Action Items / Next Steps / Open Questions & Risks / Numbers &
  Facts), being added now; appears in template pickers automatically.

## 🔴 Known issues

### 2026-07-03 full-codebase bug audit — open findings (triage pending)

Found by a three-agent code review (Python / Rust / React), each finding verified
against the surrounding code. None fixed yet — except the graph flutter, fixed the
same day in `GraphView.tsx` (root cause: the cytoscape-d3-force wrapper never
resets `alphaTarget` to 0 after a drag + the layout re-randomized on every mount).

- ✅ **FIXED (2026-07-04, v0.3.20) — Python service blocked its own event
  loop.** The heavy endpoints are now sync `def` (FastAPI threadpools them) and
  local Whisper inference + the per-request transcriber mutation are serialized
  by `_WHISPER_LOCK`; `/transcribe_chunk` SKIPS (empty text) instead of queueing
  when the lock is busy. 3 regression tests incl. an end-to-end
  "/health responds while /transcribe is blocked mid-inference".
- ✅ **FIXED (2026-07-04, v0.3.19) — stale action-item checkboxes after
  "Regenerate Notes".** `handleResummarize` now reloads action items after the
  new summary lands (mirrors `handleSaveSummary`).
- ✅ **FIXED (2026-07-04, v0.3.19) — no `busy_timeout` on SQLite.** `open_keyed`
  now sets a 5 s busy timeout on every connection (all opens route through it).
  WAL mode is still a possible future improvement.
- ✅ **FIXED (2026-07-04, v0.3.20) — live-caption task leak + temp-file race.**
  `LIVE_CAPTION_EPOCH` atomic: each recording start bumps it, stale loops exit
  at their next wake; each loop writes its own `mnt_live_window_{epoch}.wav`.
- ✅ **FIXED (2026-07-04, v0.3.20) — wrong meeting shown on rapid switching.**
  `selectMeeting` now has a latest-wins ref guard; superseded fetches are
  dropped.
- ✅ **FIXED (2026-07-06, v0.3.22) — placeholder bullets shifted the
  actionable-checkbox mapping.** `SummaryView` now skips `isPlaceholderBullet`
  bullets when advancing the index (mirrors the Rust extractor) and renders
  them without a checkbox.
- ✅ **FIXED (2026-07-04, v0.3.20) — silence auto-stop timer reset on every tab
  switch.** `setAutoStop` now keeps the previous object when values are
  unchanged, so the auto-stop effect (and its silence clock) no longer re-runs
  per navigation.
- ✅ **FIXED (2026-07-06, v0.3.22) — the small-bug sweep:** empty system capture
  now errors clearly at stop ("check the Screen Recording permission") instead
  of minting a forever-broken pending meeting; `relabel_me` uses a replacement
  lambda (backslash in "Your Name" no longer 500s, regression-tested);
  `config.json` read-modify-write cycles serialized via
  `config::update_config_with` (calendar connect/disconnect/enable); import
  tempfile via `mkstemp` (fd leak + Windows PermissionError);
  `ask_all_meetings` persists the user turn up front (survives LLM errors);
  imported timestamps normalized to UTC (lexicographic sort correctness);
  MeetingChat stream callbacks no-op after unmount.
- 🟡 Remaining (accepted for now): WAV header u32 truncation >4 GiB
  (`audio/mod.rs` — OOM hits first); Settings immediate-persist toggles commit
  other unsaved edits (design choice); vocab-hallucinated mic lines on silent
  audio ("Tatweer OS, Claude, Hira" — noted 2026-07-06, needs its own look).

### Ask-tab RAG upgrade research — 2026-07-06 (agent-verified vs current sources)

> **✅ UPDATE 2026-07-09: the recommended hybrid retriever is BUILT** (in dev,
> uncommitted — pending the user's `tauri dev` smoke + commit + re-freeze).
> Python `POST /embed` (Ollama bge-m3) + `src-tauri/src/embeddings.rs`
> (self-healing chunk index in SQLCipher) + `retrieve_meetings_hybrid`
> (FTS5 + chunk-cosine + attendee/tag anchors, RRF-fused; detail answers
> ground in matched chunks). cargo 81 · pytest 187 · tsc ✓. Details:
> [HANDOFF.md](./HANDOFF.md) "Last session". Research below kept for the why.

Current Ask = **keyword RAG** (FTS5 BM25 + `rank_meetings` fallback → top-5 into
local LLM; no embeddings, no graph traversal). Question researched: adopt
GraphRAG (user's instinct: "we have a good graph")? **Verdict: NO to full/Lazy
GraphRAG — overkill and wrong-fit for a single-user, few-hundred-meeting,
small-local-LLM app.** Key nuance: the app's graph is a cheap **metadata** graph
(meetings↔people↔tags), NOT the LLM-extracted entity-relationship KG GraphRAG
needs — GraphRAG wouldn't reuse it; it'd add a separate expensive multi-call LLM
indexing pass (entity extraction + community summaries over every transcript,
re-run on each new meeting). GraphRAG only wins on *global/thematic sensemaking*
(a minority of meeting questions); vector RAG wins on the specific-fact/entity
questions that dominate here.
- 🟠 **RECOMMENDED (rank 1+2, ship together): hybrid retriever = local semantic
  (vector) search + graph-assisted anchoring over the EXISTING metadata graph,
  fused with the FTS keyword layer.** Vectors fix the biggest gap (keyword search
  misses "trading bot" ≈ "algorithmic trading agent"); the metadata graph
  answers person/tag-scoped questions ("what did I discuss with Basim") by
  traversing person→meetings. 100% local, no privacy change.
  - **Embedding model:** BGE-M3 (BAAI, MIT, 1024-dim, 100+ langs, strongest
    Arabic of the practical options) — or Qwen3-Embedding-0.6B (Apache-2.0).
    Run via MLX / Ollama (both pullable). **Storage:** `sqlite-vec` v0.1.9
    (slots into the existing SQLCipher DB) or in-memory cosine over a BLOB column
    (zero new dep; brute-force KNN is ms at this corpus size).
  - **Architecture:** new `POST /embed` in the Python service (already loads ML
    models); Rust stores per-CHUNK vectors (⚠️ chunk at segment/action-item
    granularity, not whole-meeting) + hybrid score fusion before the existing
    top-5 stuffing. Effort: moderate.
  - **Global themes** ("recurring themes across all my meetings") stay weak —
    approximate later with a cheap map-reduce over vector/tag clusters, BEFORE
    ever reaching for GraphRAG.
- 🔵 **DEFER: LightRAG** (HKUDS, EMNLP 2025, `lightrag-hku`, incremental updates,
  tuned for 7–32B local via Ollama) — the ONLY graph-native option worth it, and
  only if users later demand true cross-corpus thematic synthesis at a corpus
  size where the map-reduce approximation breaks. Not now. Never full MS GraphRAG.

### Meetily (MIT) reuse research — 2026-07-06 (agent-verified against their repo)

Meetily went MIT (`github.com/Zackriya-Solutions/meetily`; deps all permissive;
Parakeet model CC-BY-4.0 = attribution only). Verdicts:
- 🟠 **ADOPT: VAD-gated live captions (the #1 steal, ~1–2 days).** Replace our
  30 s-window/12 s re-transcribe loop with **Silero VAD segmentation →
  transcribe each utterance ONCE** (their `audio/vad.rs`): 30 ms chunks,
  redemption 2000 ms, min_speech 250 ms, pre/post-pad 300/400 ms — tuned
  constants documented as hard-won. Options: `silero_rs` (MIT) in our Rust
  capture layer feeding `/transcribe_chunk` per utterance, or `silero-vad` in
  the Python service gating the rolling buffer. Kills redundant compute and
  mid-word cuts. Note: theirs is append-only per-utterance (no partial-result
  correction) — still strictly better than ours.
- ✅ **SPIKED & SKIPPED (2026-07-06): Parakeet-TDT-0.6B.** Benchmarked on M5 Max
  vs mlx-whisper. **Disqualified: 25 European languages only, NO Arabic** (nor
  Urdu/Persian) — a hard blocker for this user. Also strictly dominated: on
  Metal, `whisper-large-v3-turbo` is ~82–86× RTFx (**~2.3× faster than Parakeet
  int8-CPU**), same clean-English accuracy, all 100 languages, zero new deps.
  Parakeet's CoreML/ANE path crashes or is slower than CPU. Packaging cost was
  low (1.1 MB, reuses existing onnxruntime), so SKIP is on merit, not weight.
  Revisit only for a Windows/CPU-only English-first path. Full report:
  scratchpad/parakeet-spike/SPIKE_REPORT.md.
- ✅ **DECIDED (2026-07-06) — keep `whisper-large-v3` as the default; do NOT
  flip to turbo.** Ran an Arabic A/B (macOS `say -v Majed` clip, both models via
  mlx-whisper): turbo was **~3.5× faster** (0.74s vs 2.60s, confirms the win)
  but its **Arabic is materially rougher** — it drops diacritics/tashkeel
  (مرحبا vs مرحباً), hamzas on alif (الاول vs الأول, انهاء vs إنهاء), and all
  punctuation; both models made the same hard-word slips. English quality is
  identical (per the spike). Since the user records Arabic, large-v3 stays the
  default. **Turbo remains a one-click option in Settings → Transcription** for
  English-only sessions (already selectable via the `whisper_model` picker) — no
  code change needed. Full A/B in the session transcript.
- 🟡 **CHERRY-PICK if we see artifacts:** their audio hygiene (persistent
  rubato resampler — per-chunk caused 173% RMS blowup; ring-buffer window
  alignment with zero-padding; proportional soft-clip mixing).
- ✅ **DIARIZATION: take nothing.** Their OSS "speaker" field is mic-vs-system
  channel attribution only (weaker than our Me/Them + sherpa split); real
  diarization is closed-source Pro. We are ahead — keep sherpa-onnx.

1. 🔴 **OPEN (2026-06-25) — auto-updater ships an ad-hoc-signed app → resets TCC
   grants.** The updater `.app.tar.gz` is created by `tauri build` from the
   ad-hoc-signed app, *before* `scripts/build-dmg.sh`'s NotchyPrompter Dev re-sign
   (line ~61). So an auto-updated app is `Signature=adhoc` and **loses mic / screen
   recording / calendar permissions** (TCC is keyed to the signing identity).
   Verified during the v0.3.10→v0.3.11 round-trip test. **Fix:** sign the `.app`
   with the stable identity BEFORE the tarball is produced — set
   `APPLE_SIGNING_IDENTITY="$SIGN_ID"` for `tauri build`, or regenerate the tarball
   from the re-signed `.app` and re-sign it with `tauri signer sign`. Tackle with
   notarization (beta step 5), which reworks signing anyway. (The updater mechanism
   itself — check/download/verify/relaunch — works.)

2. ✅ **FIXED (2026-06-16) — Ollama truncation (`num_ctx`).** `summarizer.py`
   now sets `options={'temperature': 0, 'num_ctx': 16384}` (env `OLLAMA_NUM_CTX`,
   raise to 32768 for marathon meetings). Multi-hour map-reduce chunking is still
   a future enhancement for transcripts beyond the context budget.

3. ✅ **FIXED (2026-06-16) — Whisper compute type.** CUDA path now defaults to
   `float16` (verified: large-v3 loads on CUDA, 6.4 s audio in ~1.25 s on the
   5090). CPU fallback keeps `int8`.

4. ✅ **FIXED (2026-06-16) — grounding + structured output.** Role split + strict
   grounding in all prompts, AND Ollama structured output (`format=` the
   `MeetingNotes` schema → title + attendees + sections, rendered to Markdown).
   Default model is now `qwen3.6:35b-a3b` (configurable; reasoning `think=False`
   for speed). *Optional follow-up:* post-validate that named owners actually
   appear in the transcript.

5. ✅ **FIXED (2026-06-17) — Service URL change no longer needs a restart.**
   `HttpClient.base_url` is now an `RwLock<String>` with `set_base_url()`; each
   request reads a cloned snapshot (guard dropped before `.await`). `update_config`
   pushes the new URL into the live client, so a Settings change takes effect
   immediately.

6. ✅ **FIXED (2026-06-17) — Temp WAVs no longer leak on failure.**
   `transcribe_and_summarize` runs the fallible pipeline in an inner
   `async {…}` block, then a new `cleanup_recordings()` helper deletes both WAVs
   unconditionally (success or failure) before returning. Audio never outlives
   transcription, even when transcribe/summarize errors.

---

## 🔵🔴 Launch gates (2026-06-28 — decided; from [LAUNCH_PLAN.md](./LAUNCH_PLAN.md))

**Decision (2026-06-28):** launch **free-only** (Pro deferred ~30–60 days), paid
wedge aimed at **regulated client-facing solos** (law/health/finance/consulting)
with prosumers + Arabic/RTL as the free funnel, lead messaging with **"nothing
leaves your machine"** (not "no bot"), and **open-source the read-only MCP
server**. Rationale + the full plan: [LAUNCH_PLAN.md](./LAUNCH_PLAN.md); strategy
reconciliation: [STRATEGY.md](./STRATEGY.md) §2026-06-28. The four gates below are
hard blockers — the launch date is **soft, gated on these being green**, not the
calendar.

**The four hard gates (everything else slips until these pass):**
1. 🔴 **macOS notarized, clean-machine install — zero terminal steps.** Fresh Mac
   (no dev tools) installs, records, and summarizes end-to-end; the full TCC chain
   (ScreenCaptureKit / mic / EventKit) grants correctly or capture silently fails.
   Folds in Known-issue #1 (the ad-hoc-signing TCC reset) and the "code-sign +
   notarize" polish item below. **No pass, no launch date.**
   - 🎉 **UNBLOCKED (2026-07-16 evening) — ENROLLMENT COMPLETED** on the new
     **hamza@lagharilabs.com** (Cloudflare Email Routing → Gmail, set up the same day;
     Apple's enrollment mail was the mail path's first live proof). Two prior rejections
     (generic 406/202000) never recurred with the domain email + fresh Apple ID. Gate #1
     itself stays open until: membership activates (≤48h) → **Developer ID Application**
     cert → `notarytool` keychain profile `ADVERSARIA_NOTARY_PROFILE` → first
     RELEASE_MODE=1 notarized build → clean-machine install passes. ⚠️ Identity switch
     (NotchyPrompter Dev → Developer ID) resets TCC/keychain grants once.
   - (historical) ⛔ BLOCKED (2026-06-28) — enrollment attempted → generic failure;
     only the self-signed `NotchyPrompter Dev` identity existed. Checklist below was
     the working theory and remains useful reference for the cert/notarization phase.
   - **The error is a generic catch-all** (HTTP 406 / resultCode 202000) — Apple won't
     say which of ~6 causes fired; usually a **silent identity-verification hold**. Work
     this probability-ordered checklist (verified via a 9-agent adversarial research
     workflow, 2026-06-28; full output in the session transcript):
     1. **Add a real payment method + shipping address on the Apple ID at
        account.apple.com FIRST**, then enroll (own-name major Visa/MC — NOT
        prepaid/gift/Apple-balance; have the bank pre-authorize the intl charge). Single
        most-cited confirmed fix.
     2. **Legal name must match passport/government ID exactly** (English spelling, no
        alias/nickname/company name) AND the cardholder name. #1 silent trigger.
     3. **Apple ID consistency:** email-format (not a phone number), 2FA on, and
        **Apple-ID region == card country == phone-number country**.
     4. **Switch channel/network:** enroll on the **web** (`developer.apple.com/enroll`),
        not the app; try another browser; **VPN off**; if it fails instantly, try iPhone
        over **cellular**.
     5. **If still failing → request a PHONE CALLBACK** (`developer.apple.com/contact` →
        Membership and Account → Program Enrollment → Phone), not email (email replies
        run days→months). The rep can send the **ID-upload link** that clears an identity
        hold. Have the **Enrollment ID** ready. Also **track the $99 charge** — Apple may
        take the fee while enrollment stays stuck; demand completion or a refund.
   - ⚖️ **DECISION (founder): Individual vs Organization enrollment.** Individual = fast,
     but the **personal legal name** becomes the "identified developer" users see (app +
     every TCC prompt). **"Laghari Labs"** requires **Organization** enrollment (D-U-N-S +
     legal entity, +1–4 weeks). For a trust-led privacy product this is not cosmetic.
   - **Decouple the launch (do NOT gate the date on Apple):** run the private beta NOW via
     ad-hoc sign + each tester clearing quarantine (still works on macOS Tahoe 26; the old
     right-click→Open bypass was REMOVED in Sequoia 15.0). Good for a few **technical**
     design partners, NOT a broad/non-technical beta. ❌ Avoid the "contractor notarizes
     under THEIR Developer ID" fallback — it shows a stranger's name as the developer + on
     TCC prompts, eroding the exact trust this product sells.
     - ✅ **BUILT (2026-06-28): the interim beta installer.** `scripts/beta/Install Adversaria.command`
       (double-click → quits a running copy → `ditto` to /Applications → `xattr -dr com.apple.quarantine`
       → launch) + `scripts/beta/INSTALL.txt` (with the manual one-liner fallback). `build-dmg.sh`
       auto-bundles both into the `.dmg` for any **non-notarized** build (gated on `APPLE_SIGNING_IDENTITY`
       unset). Syntax-checked; the actual beta `.dmg` is produced by the next `build-dmg.sh` run.
   - ⚖️ **DECIDED (2026-06-28): Individual enrollment** (fastest unblock; personal legal name is the
     "identified developer"; migrate to Org/Laghari Labs later if the brand optics warrant — requires
     re-sign + re-notarize).
   - **Then** (cert in hand) rework `build-dmg.sh` + `tauri.conf.json` per
     [SPEC_DMG_PACKAGING.md](./SPEC_DMG_PACKAGING.md) §7.2–7.3 (sign + notarize via
     `tauri build`, which also fixes Known-issue #1's updater TCC reset). Verify against a
     real notary submission, not blind.
2. 🟠 **First-run wizard defaults no-GPU users straight to the Groq key path.**
   Guided first-run to a first summary with zero terminal use; note the
   `HF_HUB_DISABLE_XET=1` model-download gotcha. Supersedes/absorbs P2 #8
   (guided onboarding) for launch scope.
3. 🟠 **Groq long-meeting rate-limit (~6,000 TPM) fails LOUD, never silent.**
   Chunk/queue or show a clear message; a silent failure on the long meetings
   prosumers test with is an instant-churn, in-public death (risk P2).
4. 🔵 **Capture-path reliability proven.** A few Rust integration tests on the
   audio/storage boundary + a manual full-flow QA matrix (Intel vs Apple Silicon,
   GPU vs no-GPU, Windows vs Mac). A dropped recording is the one unrecoverable
   churn event (risk P6). Keep any future license code **away** from this path.

**Also decided for the launch (not date-blocking but on the critical path):**
5. 🔵 **Open-source the read-only MCP server** (already standalone at
   `~/Documents/Documents/MyProjects/mcp-server/`). Permissive license; the
   cheapest way to neutralize the closed-source-vs-MIT trust gap and an HN
   discovery asset. **Irreversible once public** — decided **yes** (2026-06-28).
6. 🔴 **Honesty rewrite of every privacy claim + a data-flow page.** Absolutes
   ("physically can't leak") are falsified by the updater, in-app feedback, Google
   OAuth, MCP, and the Groq path — and are a legal liability (risk P5). Publish a
   page enumerating every egress; make the updater **disclosed + disable-able** so
   the "firewall test" is genuinely true; use "your meeting content stays on your
   machine in local mode"; **never** say "HIPAA / bar-approved" — say "designed for
   confidentiality"; cite only the public docket + WaPo/NPR for competitor suits.
7. 🟠 **Positioning rewrite.** Lead with "Nothing leaves your machine" + the
   Bilzerian/Otter cold-open; demote "no bot" to the second sentence; aim the paid
   message at regulated solos. Landing-page hero + taglines drafted in
   [LAUNCH_PLAN.md](./LAUNCH_PLAN.md) §4 (awaiting build).
8. 🔵 **Private beta of 30–50** on the auto-updater before the public spike. Exit
   criteria: crash-free first run + first summary unaided on a clean Mac **and** a
   clean Windows box; Groq long-meeting degrades gracefully. Recruit from existing
   in-app sign-ups + r/macapps + r/LocalLLaMA + **3–5 friendly consultants/lawyers**
   (first compliance design-partner conversations).
9. 🔵 **Launch assets** (LAUNCH_PLAN.md §7): one-scroll landing page (dual download,
   3-second proof row, Bilzerian block, labeled Groq path, Pro **waitlist** — no
   fake checkout), 60–90s captioned demo + 10–15s silent GIF, Show HN draft, PH
   "Coming Soon", AlternativeTo/SaaSHub/PrivacyToolsList submissions (index early).
10. 🔵 **Pro path — build AFTER launch, switch on ~30–60 days later.** LemonSqueezy
    (Merchant-of-Record, not raw Stripe) + offline-verifiable Ed25519/JWT license
    (online activation once, device binding, offline grace), monetize
    entitlements/features **never inference** (local = $0, BYO-key = user pays).
    **Do NOT build hosted inference under this brand.** Capture intent via the
    waitlist at launch; **no in-binary license gating at launch.** (Resolves the
    infeasible "bill in 4 weeks" brief — risk P4.)

---

## 🟠 Assessment-driven backlog (2026-06-23)

From an external product/eng review (validated against the code: it claimed "no
Rust tests" — false, there are **22**; "App.tsx 30+ useState" — actually 18; file
sizes were accurate). Ordered by impact. Quick-wins are being **delegated to the
DeepSeek stunt worker**; check items off as merged.

**P0 — credibility quick-wins (delegating now):**
1. 🟡 **Remove the lorem-ipsum placeholder.** `WeeklyView.tsx` still ships
   `SAMPLE_RECAP` + `SamplePlaceholderCard` (lines ~31–137, rendered ~286–298).
   Replace the empty-week branch with an honest empty state; delete the sample
   constant + component. Makes the shipped product stop looking unfinished.
2. 🟠 **Friendly "LLM server is down" UX.** `AskAllView` (and `MeetingChat`)
   surface a raw `Connection refused` / `String(e)`. Detect connection failure and
   show a banner: "Your LLM server isn't running — start it with `…`" + copy button.
3. 🟠 **BYOK "Test connection" button** in `Settings.tsx` — call the provider's
   `/v1/models`, show a green check or the specific error, so key/URL setup isn't
   "paste and hope".

**P1 — thesis-protecting (do before competitive features):**
4. 🔴 **Encryption-at-rest for `meetings.db`.** Today the privacy PIN is a *UI gate
   only* — transcripts/summaries sit in plaintext SQLite on disk. This directly
   contradicts the "sovereign / compliance-grade privacy" wedge and is the first
   thing a security review flags. Use SQLCipher or an OS-keychain-derived key.
   `storage.rs`. **Higher priority than diarization** — it protects the core pitch.
5. 🟠 **Stream chat / Ask responses** token-by-token (SSE from the Python service +
   incremental render). Table-stakes chat polish; the model is fast, the UX feels slow.

**P2 — competitive gaps (post quick-wins):**
6. 🟠 **Speaker diarization** (per-person, beyond the current 2-way Me/Them dual
   capture). Behind a feature flag. `SPEC_DIARIZATION.md` exists; not built. #1 gap vs Meetily.
7. 🟠 **Kanban / task board** from the `action_items` table (the "10x workflow"
   north star) — To Do / In Progress / Done columns, drag-drop, auto-populate.
8. 🔵 **Guided first-launch onboarding** — check LLM server → offer model download →
   test recording → first note. Converts "complex setup" into a wizard.
9. 🔵 **One-click installer bundling a small quantized model** (e.g. `qwen3.6-8b-Q4`)
   so a first run needs zero terminal commands.

**P3 — strategic:**
10. 🔵 **BYOK as a finished free feature** (Settings already has the providers) —
    polish + document. Per STRATEGY: ship BYOK; **don't** build subscription infra
    until paying users ask.
11. 🟡 Multi-user / team sharing (law-firm beachhead).
12. 🟡 Calendar-driven pre-meeting prep (reuse existing Google/EventKit integration).
13. 🟡 Hybrid mode (local transcription + optional cloud summary of the transcript).
14. 🔵 Publish to Homebrew / WinGet.

**Tech-debt (track, not urgent):**
15. 🔵 Split oversized files: `commands.rs` (1193), `Settings.tsx` (1098),
    `NoteViewer.tsx` (771).
16. 🔵 Add frontend/E2E tests (Rust has 22 unit tests; the frontend has none).
17. 🟡 **Audio output dips ~1ms when recording starts** (macOS). Inherent to
    ScreenCaptureKit installing the system-audio tap (reconfigures the CoreAudio
    output). Only fix is pre-warming/keeping the SCStream alive — captures before
    the user hits record (privacy + battery), so deprioritized. Low priority.

---

## 🟠 Roadmap to Granola (ordered by impact)

The north star is the Granola experience: it's always there, it captures
everything, and the notes feel like *yours*.

### Requested next — UX batch (2026-06-18, from user)

> ✅ **ALL FIVE SHIPPED 2026-06-18** (commits `fcd4cfc` chat history+markdown,
> `beab59d` search, `3e7eb60` tags, `9479cf8` auto-category, `523331b` user-editable
> prompts) — plus the sidebar revamp (filter pillars, drag-resize, padding), inline
> click-pill rename/recolor, silence auto-stop, and the **Adversaria** rebrand + intro
> splash. Kept below for reference; see the Done section.

1. **Render markdown in Chat answers** (quick, 🟠). The `/chat` reply comes back as
   markdown but `MeetingChat.tsx` shows it raw (literal `**bold**`, `*` bullets —
   e.g. "**five new GitHub repositories**", "*   The speaker…"). Reuse the summary's
   markdown→HTML rendering (`lib/summary.ts::summaryToHtml`, or a shared renderer)
   so answers display formatted, RTL-aware.
2. **Persist chat history** (🟠). Chat is currently ephemeral (`MeetingChat.tsx` +
   `/chat`, nothing stored). Save the Q&A turns per meeting — new SQLite table
   `chat_messages(meeting_id, role, content, created_at)` (or a JSON column on
   `meetings`); load on open, append each exchange; offer a "clear chat" action.
   Threads through `storage.rs` + new IPC commands + `MeetingChat.tsx`.
3. **Search bar for meetings** (🟠). Add a search/filter input above
   `MeetingsList.tsx` to find meetings by title / transcript / summary text — today
   you scroll through everything. Client-side filter to start; move to SQLite
   `LIKE`/FTS5 if the list gets large.
4. **Colorful tags (macOS-Finder-style pills)** (🟠). Let the user attach
   user-defined, colored pill tags to a meeting (e.g. a red "YouTube" pill, a blue
   "1-on-1") — distinct from the prompt template, replacing the plain "general"
   label in the list. Needs: a per-meeting `tags` store (list of `{label, color}`),
   a tag editor (add/rename/recolor/remove), colored pill rendering in the list +
   note view, and filter-by-tag (pairs well with #3).
5. **User-editable prompt templates in Settings** (🟠). Today the 3 templates are
   hardcoded `prompts/*.md` files + hardcoded frontend lists (the `PromptTemplate`
   union, `Settings.tsx` `TEMPLATES`, `NoteViewer.tsx` `TEMPLATE_OPTIONS`). Let any
   user create/edit/delete their own named system prompts from Settings: add
   `POST`/`PUT`/`DELETE /templates/{name}` endpoints (the service already
   auto-discovers `prompts/*.md` via `GET /templates`), a Settings prompt-manager
   editor, and make the frontend template lists **dynamic** (fetch `/templates`)
   instead of the hardcoded union.

### Next frontier — the agentic loop (the 10× workflow; see [STRATEGY.md](./STRATEGY.md))

- 🟠🟠 **To-do / Kanban board fed from meetings.** Extract each meeting's action items
  into a real task board (columns/statuses, check-off), so "today's to-dos" are
  auto-deployed from yesterday's meetings. This is the killer local workflow that turns
  Adversaria from a notetaker into a command surface — and the bridge into lagharilabs OS.
- 🟠 **Cross-meeting ask (RAG over all meetings).** Chat is scoped to one meeting today;
  add "ask across everything" (FTS5/embeddings over the local store) — "what did we
  decide about X last month?". Pairs with the OS `/granola`→Adversaria bridge below.
- 🟠 **Speaker diarization** — split "Them" into named individuals (the biggest depth gap
  vs Meetily; legal/clinical buyers need who-said-what). Or explicitly position around it.

### Reimagined UI + data-model upgrades (from the `adversaria-samples` prototype, 2026-06-21)

User built an interactive prototype at `/Users/mhlaghari/Documents/Documents/MyProjects/adversaria-samples`
(`index.html`/`styles.css`/`app.js`/`widget.html`) — a glassmorphic reskin of the **existing** feature
set (Meetings/To-dos/Weekly/Ask/Settings, monthly-grid heatmap, multi-tag pills, floating record widget,
inner-sidebar settings). It's a **reskin, not a rebuild**. Decisions/analysis from reviewing it:
- ⚖️ **Storage: keep SQLite + JSON columns** (do NOT move to JSON-document storage — would lose FTS5
  search and force full in-memory scans, which is exactly what the mock does over its array). The
  multi-tag `tags=[{label,color}]` flexibility the user loves **already exists** in the schema.
- 🟠 **Structured transcript** — the prototype models `transcript` as JSON `[{speaker,text}]` turns vs
  today's flat speaker-labeled string. Migrate to JSON turns (TEXT column): enables speaker bubbles and
  slots cleanly into **diarization** (note the mock's `"Them (Sarah)"` labels).
- 🟠🟠 **First-class action items** — the prototype regex-parses to-dos out of the summary markdown
  (Assignee/Due) and **rewrites the markdown string** on checkbox toggle (fragile). Add an
  `action_items` table/JSON (`{text, assignee, due, done, meeting_id}`) so To-dos/Weekly/checkboxes
  read+write structured data. **Prerequisite for the #1 to-do/Kanban board.**
- 🟡 **Frontend reskin** to match the prototype (glass theme, monthly heatmap, inner-settings menu,
  floating widget) — separate from storage; layer on the existing backend.

1. ✅ **DONE (2026-06-17) — Your notes + AI notes merged (Granola's signature
   feature).** Live notepad (`RecordingNotes.tsx`) shown in the main area while
   recording; the text is kept verbatim (`meetings.user_notes` column, editable
   via a "My Notes" tab in NoteViewer → `update_meeting_notes`) AND fed to the
   summarizer as anchors — `summarize()` injects a `USER NOTES` directive + a
   `<user_notes>` block so the summary organizes around what the user flagged,
   still grounded in the transcript. Threads through `transcribe_and_summarize`
   (optional `user_notes`) and `resummarize_meeting` (re-uses stored notes).
   Not yet exercised live (verified via tests + compile only).

2. 🟠 **PARTIAL (2026-06-17) — Live transcription preview (rolling caption).**
   While recording, Rust snapshots the last `LIVE_WINDOW_SECS` (30s) of system
   audio every `LIVE_CHUNK_SECS` (12s) to a temp WAV → `POST /transcribe_chunk`
   (reuses the loaded model) → `live-transcript` Tauri event → live caption pane
   in the recording view (`RecordingNotes.tsx`). No new deps; faster-whisper
   decodes the WAV (no Rust resampling). The full transcript is still the
   authoritative `/transcribe` pass at stop. **MVP caveats / remaining:** it's a
   rolling-window *preview*, not a LocalAgreement-stitched accumulating transcript
   (words near window edges can wobble); ~12–30s latency; system audio only (no
   live "Me" mic caption); not yet verified live against the GPU. Follow-ups:
   LocalAgreement-2 stitching (UFAL whisper_streaming, see research) or a
   WebSocket path for lower latency; live diarization (WhisperLiveKit/Sortformer).

3. ✅ **DONE (2026-06-16) — Meeting auto-detection.** Background detector
   (`src-tauri/src/detection.rs`) polls the Windows CapabilityAccessManager
   registry for a meeting app using the mic and shows a non-blocking "Record this
   meeting?" prompt, gated by `auto_detect_meetings` (live toggle). *Future:* add
   WASAPI session-state verification and browser window-title corroboration to
   further cut false positives; calendar-based pre-meeting arming (see #7/#8).

4. **Attendee detection.** ✅ *Phase 1 done (2026-06-16):* structured extraction
   stores an `attendees` list on each meeting (SQLite column + NoteViewer chips),
   grounded so only spoken names appear. ✅ *Editable list done (2026-06-16):*
   `update_attendees` command + inline add/remove chips in NoteViewer.
   *Phase 2 (opt-in, high effort):*
   calendar integration (Google Calendar API / Microsoft Graph, read-only OAuth)
   to pull the authoritative roster like Granola — **off by default**, the most
   data-exposing feature. See [DECISIONS.md](./DECISIONS.md) ADR-002.

4b. ✅ **DONE (2026-06-17) — Arabic / multilingual summaries.** `output_language`
   threads through the service; the summarizer injects an OUTPUT-LANGUAGE directive
   (English / Arabic / "match spoken"). Per-meeting picker in the note view +
   default in Settings. RTL rendering for Arabic (section cards, title, transcript
   `dir=auto`). Transcription was already multilingual (Whisper auto-detect; MSA
   best, dialect + code-switching weaker). *Polish left:* section-icon keyword map
   for Arabic headings, and localize the "None mentioned" placeholder to "لا يوجد".

5. ✅ **DONE (2026-06-17) — Chat with a meeting.** A "Chat" tab on the note view
   (`MeetingChat.tsx`) asks grounded questions about one meeting. New
   `POST /chat` endpoint → `OllamaSummarizer.chat()` (free-text, transcript-only
   system prompt, no fabrication) → Rust `chat_with_meeting` command → typed
   `chatWithMeeting` IPC. Ephemeral Q&A (not persisted), RTL-aware answers. 7 new
   tests (67 total). *Future:* persist chat history; stream tokens. Not yet
   exercised live against Ollama (verified via tests + compile only).

5b. **Feed meeting data into Tatweer OS (ask about meetings there).** Tatweer OS
   is the "work-in-one-chat" hub — it should answer questions about meetings
   recorded here ("what did we decide in the ERDC meeting?", "action items from
   last week's client call?"). Implementation lives in **Tatweer**: a read-only
   skill over this app's SQLite store
   (`%APPDATA%\meeting-note-taker\meetings.db` — title / recorded_at / attendees /
   transcript / summary), retrieving the relevant meeting(s) and grounding the
   answer in them. Pairs with the FTS5 index in #6 (shared across app + Tatweer).
   Local-only — both apps on one machine — so the privacy guarantee holds. Extends
   or complements Tatweer's existing `/granola` skill. Both now run on the same
   Ollama `qwen3.6:35b-a3b`, so no extra model cost.

6. **Search + export.** ✅ *Copy/export done (2026-06-17):* copy-as-clean-text +
   rich HTML (RTL-aware), and Export-to-`.md` via a native save dialog. *Remaining:*
   SQLite FTS5 full-text search across transcripts.

7. **Better summaries.** ✅ Model configurable; default now `qwen3.6:35b-a3b`
   (36B MoE, vision+tools — benchmark-won, see ADR-008). Structured `MeetingNotes`
   output in place (🔴#3), and sections now render as real **UI cards**
   (collapsible, icons, action-item checkboxes) — 2026-06-17. *Remaining:*
   map-reduce chunking for multi-hour transcripts beyond the context budget.

9. 🟠 **IN PROGRESS — vLLM backend (concurrency / no blocking).** Ollama
   serializes requests (chat stalls behind summarize; ~112s cold reloads).
   ✅ *Phase 1 done (2026-06-17):* config-selectable LLM backend
   (`LLM_BACKEND=ollama|openai`, `LLM_BASE_URL`, `LLM_API_KEY`) — `_chat_openai`
   uses httpx + `response_format: json_schema` + `chat_template_kwargs`; default
   Ollama (non-breaking). See ADR-009. *Phase 2 (infra):* stand up vLLM in WSL2,
   serve `Qwen/Qwen3.6-35B-A3B-FP8`, `--gpu-memory-utilization 0.80` (HANDOFF
   runbook). *Phase 3:* apply the same backend abstraction in **Tatweer OS** (its
   own repo). Not yet exercised against a live vLLM.

8. **Optional Claude cloud fallback — privacy-preserving.** Behind a `Summarizer`
   Protocol, selected by config, **off by default**. Only call the Claude API on
   explicit per-run opt-in with a clear "this sends your transcript to Anthropic"
   confirmation. Key from env (`ANTHROPIC_API_KEY`), never committed. The
   `claude_api_key` config field is the stub for this.

---

## 🔵 Distribution / packaging

**Full milestone plan: [PACKAGING.md](./PACKAGING.md)** — "double-click installer →
working app, no terminal, clean shutdown." Covers the PyInstaller `--onedir`
sidecar, free-port spawn, deterministic shutdown, health-gating, first-run
Ollama/model setup, CSP lockdown, close-to-tray, and code-signed NSIS installer.
This is the gate to OSS adoption and any paid tier.

---

## 🟡 Polish / tech-debt

- 🟠 **LLM-backend health-gate + friendly "start your LLM server" banner** — the first `.dmg`
  summarization fails with a raw `OpenAI-compatible request failed: [Errno 61] Connection
  refused` when no LLM server is on :8000 (transcription is bundled; the LLM is external). The
  app should ping the summarizer backend (e.g. `GET {LLM_BASE_URL}/models`, or extend `/health`
  to report `llm_available`) and show a clear banner with the exact fix
  (`rapid-mlx serve qwen3.6-35b --port 8000`) instead of an errno. STATUS previously overclaimed
  the app "detects/prompts" for this — it doesn't. (Daily-use autostart is now handled by a login
  LaunchAgent, but a fresh install on another Mac still hits the raw error.) See
  [LESSONS_LEARNED.md](./LESSONS_LEARNED.md).
- 🔴 **Windows calendar: browser-open truncates the auth URL** — `calendar_connect` opens the
  Google authorize URL via `std::process::Command::new("cmd").args(["/c","start",url])`
  (`src-tauri/src/commands.rs`). `cmd start` treats `&` as a command separator, so the multi-param
  OAuth URL is cut at the first `&` and consent fails. macOS (`open url`) is correct. **Fix before any
  Windows calendar test:** use `tauri-plugin-opener`, or `Command::new("rundll32").args(["url.dll,FileProtocolHandler", url])`,
  or `cmd /c start "" "<url>"` (empty title + quoted URL). The URL is app-constructed (no injection),
  this is a correctness bug only.
- 🟠 **Calendar: Microsoft (B2)** — Phase 1 shipped **Google only** (`77af3c1`). Microsoft Graph
  (`calendarView`) replicates the proven Google pattern in `calendar/microsoft.rs`; the dispatch
  branches currently return `Err("Microsoft not yet supported")`. Do after the Google connect flow is
  live-verified. See `docs/SPEC_CALENDAR.md` §"Provider endpoints" (Graph auth + calendarView).
- 🟠 **Calendar: feed the roster into NEW recordings' names** — `transcribe_and_summarize` passes
  `known_attendees: None` (`// TODO: calendar roster`). Once a recording matches a calendar event
  (`calendar_event_at`), pass that event's attendees as `known_attendees` so the **first** summary
  already normalises to real names (today only `resummarize` uses the roster). Ties Task C → B1.
- **macOS: let the bundled app target Ollama** (low) — `default_llm_backend()` hard-picks
  `openai`/Rapid-MLX on Apple Silicon and `spawn_sidecar` (`commands.rs:87`) doesn't pass
  `LLM_BACKEND`, so a Finder-launched `.app` can't use a running Ollama without a code change.
  Either pass `LLM_BACKEND`/`LLM_BASE_URL` through to the sidecar from config, or add a
  Settings backend picker. Low priority while Rapid-MLX is the daily driver.
- **Live transcript quality** (medium) — the rolling caption is a best-effort
  preview (`/transcribe_chunk` → single-file `transcribe`, short windows, no
  speaker labels). It's rougher than the authoritative stop-time pass by design.
  Options: feed `custom_vocabulary` to chunks too; widen/overlap the window;
  dedupe repeated head/tail text. Needs live iteration to tune — don't fix blind.
- **Detection: broaden recognized apps + verify live** — `classify()` (macOS) only
  matches Zoom/Teams/Webex/Slack/browsers; add the user's actual call apps
  (e.g. WhatsApp, FaceTime, Discord) as needed. Also confirm CoreAudio detection
  actually fires once `auto_detect_meetings` is enabled (it defaults off).
- **Names in group meetings (high-level)** — `Me`/`Them` are audio *channels*, not
  identities; "Them" lumps every remote speaker. Real per-speaker names need
  diarization (split "Them" into speakers) + manual/inferred labeling. Big lift.
- **Highlight-to-correct dictionary (high-level)** — let the user select wrong text
  in the transcript, fix it, and auto-save the wrong→right pair into
  `custom_vocabulary` (plus a deterministic post-correction pass). Builds on the
  vocabulary feature shipped 2026-06-18.
- ✅ **DONE (2026-06-17)** — Detector re-prompt cooldown restored to 5 min
  (`detection.rs REPROMPT_COOLDOWN` = 300s).
- ✅ **DONE (2026-06-17)** — Arabic polish: section-icon keyword map now matches
  MSA headings; "None mentioned" placeholder localizes to "لا يوجد" in RTL cards.
- ✅ **DONE (2026-06-18)** — macOS auto-detect now fires. Root cause was a
  one-char fourcc typo (`kAudioHardwarePropertyProcessObjectList` was `'prl#'`,
  must be `'prs#'`) → CoreAudio `'who?'` (unknown property) → `process_list()`
  always `None`. Fixed in `detection.rs`; verified live (matched Microsoft Teams).
  See [LESSONS_LEARNED.md](./LESSONS_LEARNED.md). *Follow-up:* add WhatsApp/FaceTime
  to `classify()` if the user calls on those.
- **macOS: verify live (rest)** — still confirm `Them`/`Me` labeling and MLX
  transcript quality on a real call. Confirm ScreenCaptureKit delivers planar f32
  as assumed (`audio/macos.rs` interleaves on `num_buffers > 1`); log `num_buffers`
  on the first sample if labeling sounds off.
- **macOS (optional, privacy UX):** swap ScreenCaptureKit → CoreAudio process taps
  (macOS 14.4+) so system-audio capture no longer needs the *Screen Recording*
  grant (just audio-recording). Cleaner fit for "privacy is the product"; deferred
  for build-risk reasons in ADR-010.
- **macOS packaging:** code-sign + notarize so TCC grants survive rebuilds and the
  `.app` runs without Gatekeeper friction (parallels the Windows PACKAGING.md).
- Show a UI indicator for whether the mic channel was actually captured.
- Persist the selected template into config so recordings don't always default to
  `general`.
- Validate the service URL / model fields in Settings before saving.
- Add Rust tests (`src-tauri/tests/`) and frontend E2E (Playwright). Currently
  only the Python service has tests (50, ML mocked).
- Modernize Python deps per uv guidance: move `pytest`/`httpx` from
  `optional-dependencies.dev` to PEP 735 `[dependency-groups]`; refactor the
  service singletons to `app.state` + `Depends` for cleaner test injection; pin
  `nvidia-cudnn-cu12>=9,<10` and add `ctranslate2>=4.6.3` so a fresh 5090 install
  can't resolve to a pre-Blackwell CTranslate2.
- Use `AsyncClient` in the service and stream summary tokens to the frontend.
- Debounce/disable the re-summarize button while a request is in flight.

---

## Done

> **2026-08-30 — ✅ person-rename follow-ups closed (founder confirmed renaming works in daily use).** Original entry:
> **2026-08-24 — 🐛 person-rename follow-ups (founder repro, Jenna→Jena, meeting 241):**
> (1) ~~**Attendee-chip edit is Enter-only**~~ **DONE same day (post-ship):**
> blur now commits the rename instead of discarding it; Escape still cancels
> (React doesn't dispatch blur on unmount, so the Enter/Escape paths can't
> double-fire; the guards catch the rest). vitest 188 + tsc clean. (2) **One transcript occurrence survived the sweep** — after
> the rename, summary/attendees/action items were clean but `transcript` AND
> `transcript_turns` kept exactly one plain-ASCII "Jenna" ("…thank you so much
> Jenna. Bye bye."); the same `(?i)\bJenna\b` regex demonstrably cleaned the
> summary, so the sweep can't have missed it — suspect a later write clobbered
> the swept transcript (rename racing transcription/merge-speakers?). Repro
> unknown; check `rename_meeting_person` vs concurrent transcript writers
> before hunting further. UI impact today: none visible (transcript tab only).


- ✅ 2026-06-29 — **Back-to-back meetings: background-transcription queue** (compile+test-verified; pending a live test). Stop no longer blocks on transcription — it saves the recording via a new `enqueue_recording` command and a single-worker frontend queue (concurrency 1, **paused while recording** so live captions stay snappy) transcribes in the background via the existing `transcribe_meeting(id)`. `useRecording` `status` trimmed to `idle|recording|stopping`; `MeetingsList`/`NoteViewer` show **Transcribing…/Queued** badges; the NoteViewer pending banner hides "Transcribe now" while in-pipeline (no double-transcribe). Reuses the data-loss `save_pending_meeting`/`transcribe_meeting` infra (audio kept on disk, recoverable on crash). Root cause was a single global frontend `status` (confirmed by a 3-layer Understand workflow). `cargo check` + 43 tests + `tsc` green. Caveat: an in-flight transcription can't be cancelled (Python has no cancel) so it briefly shares the model with a new recording's live captions — only new jobs are paused. Follow-ups: auto-re-enqueue pending meetings on startup; a CSS pulse on the Transcribing badge.

- ✅ 2026-06-26 — **No more data loss when the ML service is down at Stop**
  (was 🔴#0). Recordings used to be deleted unconditionally even when
  transcription failed, so a meeting recorded while the Python/Whisper service
  was unreachable was lost entirely. Fix:
  - Recordings now write to `<app-data>/recordings/` (durable across restarts),
    not the system temp dir (`config::recordings_dir`, `start_recording`).
  - `transcribe_and_summarize` deletes audio **only on success**; on failure it
    saves a **pending** meeting (`audio_file_path = Some(path)`, title
    "Untranscribed recording", "Needs transcription" tag, user notes preserved)
    and keeps the WAV(s) (`save_pending_meeting`).
  - New `transcribe_meeting(id)` command retries the pipeline on the stored
    audio (deriving the `_mic.wav` sibling), updates the row in place
    (`storage::update_meeting_transcription` — also clears `audio_file_path`),
    and deletes the audio only once it succeeds.
  - `NoteViewer` shows a "Not transcribed yet" banner + **Transcribe now**
    button for pending meetings, with an on-device-audio privacy note.
  - Verified: `cargo check`, 30 cargo tests (2 new for the mic-path derivation),
    `tsc` green. Updated ADR-003 (narrowed to "deleted after a *successful*
    transcription") + SPEC. _Follow-up:_ the kept WAVs aren't themselves
    encrypted at rest; encrypting pending audio is a future enhancement.

- ✅ 2026-06-20 (post-merge, on `master`, pushed) — **Today view + FTS5 RAG.**
  - **To-dos: due dates + assignees + Today view** (`3348338`). Each action item gets a due
    date (overdue=red / today=amber) and an assignee (datalist from the meeting's attendees);
    a Today/All toggle, Today = overdue + due-today across all meetings. Persisted in
    localStorage alongside check-state (`mnt:todometa:<id>`). Frontend-only.
  - **FTS5 full-text ranking for cross-meeting Ask** (`fa950e1`). FTS5 index over meetings
    (title/summary/transcript) + sync triggers + backfill; `ask_all_meetings` ranks via FTS5,
    falls back to keyword scoring. **Non-fatal** — if SQLite lacks FTS5, init_db logs a warning
    and Ask falls back, so launch/Ask never break. _(Confirm FTS5 is active at runtime: absence
    of the "FTS5 index unavailable" warning in the service/app log.)_
  - **`.dmg` packaging spec** written: `docs/SPEC_DMG_PACKAGING.md` (macOS, PyInstaller --onedir
    sidecar + externalBin, free-port + health-gate + /shutdown, static ffmpeg resource, ad-hoc
    sign + de-quarantine for personal use; notarytool path for distributable). **Build needs the
    user's Mac.** ✅ Prereqs now done (`32464b2`): server.py has `main()` + `--host/--port` +
    `/shutdown` (additive; 75 pytest still pass); `productName` renamed to **Adversaria**.
    NOTE: renaming productName does NOT move the DB — the app-data dir is hardcoded to
    `"meeting-note-taker"` in `config.rs:15` / `storage.rs:17` (independent of productName), so
    existing `meetings.db`/`config.json` are unaffected. Still to do on the user's Mac:
    PyInstaller `--onedir` build → `externalBin` + Rust sidecar spawn/health-gate/shutdown →
    static ffmpeg resource → `tauri build` → ad-hoc sign + de-quarantine. LLM server + MLX model
    stay prerequisites.
  - Follow-up for "semantic" RAG: embeddings (needs an embed model, e.g. `nomic-embed-text` in
    Ollama) on top of FTS5. Speaker diarization: implement feature-flagged per
    `docs/SPEC_DIARIZATION.md` (needs the user's machine to verify).

- ✅ 2026-06-20 (overnight) — **Big polish batch on branch `overnight/polish-batch`
  (committed, not pushed; built by the stunt worker, reviewed + `tsc`/`cargo check`/75-pytest
  verified here).** On top of the quick-win batch below: **per-meeting tags** (reverted the
  wrong cross-meeting cascade) with filter pillars keyed by label+color + a stale-filter
  guard (fixes `No meetings match ""`); **consolidated To-dos** view (`TodosView.tsx`, action
  items across all meetings, shared localStorage check-state); **"+ add to dictionary"**
  button in NoteViewer (appends to `custom_vocabulary`); **Weekly recap** (`WeeklyView.tsx`,
  deterministic Mon–Sun digest); **privacy lock** (`locked` column + `set_meeting_locked`;
  `pin_hash` config; `src/lib/pin.ts` PBKDF2; Settings PIN section; per-meeting 🔒 + PIN-gate
  — ⚠️ UI gate, DB not encrypted at rest); **cross-meeting RAG** (`ask_all_meetings` keyword
  retrieval + `AskAllView.tsx`); **standalone notes** (`create_note` + `NewNoteButton.tsx`,
  a note = meeting with no recording). Research specs added (NOT built): `SPEC_CALENDAR.md`,
  `SPEC_DIARIZATION.md`. Follow-ups noted: privacy-lock at-rest encryption; RAG
  embeddings/FTS5; AI-narrative weekly recap.
  - **Follow-up (post-feedback):** replaced hover-only Pin/Lock/Delete with a discoverable
    **⋯ actions menu** (📌/🔒/🗑 — fixes accidental locking); added a **📅 date filter +
    month heatmap calendar** (`DateHeatmap.tsx`, white=none→dark-red=many, click a day to
    filter). **Fixed the pill filter bug** (`No meetings match your filters` even though the
    pill existed): the label+color composite filter could match nothing, so tag filtering now
    matches by **label** (one pill per label, colored by first use). **Fixed delete** —
    `window.confirm()` is a no-op in the Tauri WKWebview (returned false, silently aborting),
    so delete now uses an in-app confirm modal (pin/lock were unaffected). All verified live
    by the user: pin ✓, lock ✓, delete ✓, tag filter ✓. `tsc` green.
    _(Latent: a `window.alert` remains in the lock handler's "set a PIN first" path — also a
    webview no-op; harmless unless no PIN is set.)_

- ✅ 2026-06-20 — **Quick-win batch: meeting management + configurable auto-stop +
  post-transcription select fix** (verified `tsc --noEmit` + `cargo check`; Python
  untouched).
  - **Delete a meeting** — `storage::delete_meeting` (also clears its chat rows) +
    `delete_meeting` command + hover "Delete" in `MeetingsList` with a confirm dialog;
    clears the open-note selection if the deleted meeting was showing.
  - **Pin a meeting** — new `pinned` column + migration; `set_meeting_pinned` command;
    pin-first ordering (`ORDER BY pinned DESC, recorded_at DESC` + matching client sort);
    hover "Pin/Unpin" + a 📌 indicator on pinned rows.
  - **Editable summary** — `update_meeting_summary` command +
    `storage::update_meeting_summary_text`; Edit/Save/Cancel on the Summary tab (raw
    Markdown textarea). Lets the user merge duplicate/variant names the LLM split into
    separate people (the root cause is inconsistent Whisper spellings → the extractor
    sees them as different attendees; custom-vocabulary helps prevent it going forward).
  - **Configurable auto-stop** — new config `auto_stop_enabled` / `silence_prompt_minutes`
    / `silence_stop_minutes` (defaults true / 5 / 10, serde-defaulted for back-compat);
    a Settings "Auto-stop Recording" section; `App.tsx` reads these instead of the
    hardcoded `SILENCE_PROMPT_MS`/`SILENCE_STOP_MS` constants, and the banner text tracks
    the configured value.
  - 🔴 **Fixed: wrong meeting opened after transcription.** `useRecording.stop()` now
    captures the new meeting id returned by `transcribe_and_summarize` (`lastMeetingId`),
    and the `done` effect in `App.tsx` calls `selectMeeting(lastMeetingId)` — previously
    the returned id was discarded and the previously-selected (old) meeting stayed open.

- ✅ 2026-06-18 (evening) — **UX batch + Adversaria rebrand (delegated to DeepSeek,
  reviewed/verified/committed here).** Chat: render markdown + persist history + Clear
  (`fcd4cfc`). Meetings search bar (`beab59d`). Colorful tags + click-pill inline
  rename/recolor (`3e7eb60`, `c261c7c`). User-editable prompt templates from Settings
  (`523331b`). Auto-detect session type → colored tag with mic-bleed detection
  (`9479cf8`, `42da237`); light-pastel pill colors for the cream theme (`bc0f91b`);
  removed the redundant manual tag editor (`8741f1a`). Sidebar revamp — category-filter
  pillars, drag-resizable, more left padding, dropped the duplicate template-select +
  Record button + dead "Back to meetings" (`ff85b89`). Silence auto-stop: 5-min prompt,
  10-min hard stop (`349dcf2`). **Rebrand → "Adversaria"** with a Vane-style intro splash
  (azure `#24A0ED`, self-hosted Instrument Serif) (`379aa3a`, `7943727`). Cross-product
  **STRATEGY.md** added (`f8e7651`). All `tsc`/`cargo check`/75-pytest verified.

- ✅ 2026-06-18 — **First live macOS run + quick-win batch (delegated to DeepSeek
  via stuntman, reviewed/verified here).**
  - **Whisper `large-v3` download unblocked** — `hf_xet` is broken on this box, so
    Xet-backed large blobs hung at 0 B. Fix: `HF_HUB_DISABLE_XET=1` (now in the
    HANDOFF macOS runbook + LESSONS_LEARNED). Service runs `large-v3` again.
  - **"Your name" setting (`user_name`)** — replaces the `Me:` speaker label in new
    transcripts (server-side `relabel_me()` driven by `me_label` on `/transcribe`),
    so notes attribute the user's lines by name instead of a faceless "Me".
  - **Custom Vocabulary (`custom_vocabulary`)** — free-text glossary in Settings →
    sent to `/transcribe` as `vocabulary` → applied as the Whisper `initial_prompt`
    on both backends to bias spelling of names/terms.
  - **Auto-detect checkbox relabeled** — was misleadingly "from calendar"; it's
    mic-based. (Root cause of "no popup": `auto_detect_meetings` defaults `false`
    and was never enabled — it's a toggle, not a bug.)
  - All verified: 75 pytest + `cargo check` + `tsc --noEmit` green.

- ✅ 2026-06-17 — **macOS (Apple Silicon) port — full feature parity (ADR-010).**
  Cross-platform restructure: audio split into `audio/wasapi.rs` (Windows) +
  `audio/macos.rs` (ScreenCaptureKit system audio + cpal mic) behind a stable
  `AudioCapture` API; deps `#[cfg]`-gated in `Cargo.toml`. MLX transcription
  backend (`mlx-whisper`, `whisper-large-v3-mlx`) behind a `create_transcriber()`
  factory (auto on arm64 macOS), shipped as the platform-gated `mlx` extra.
  Meeting detection via CoreAudio process-object list. macOS bundle: `Info.plist`
  usage strings, `.icns`, `Cmd+Shift+M`, `macos-private-api` for the transparent
  card. Verified: Rust builds + links (SCK/CoreAudio/cpal), 75 Python tests pass,
  MLX transcription on synthesized speech. **Not yet exercised in a real live
  call** (needs the Screen-Recording grant + an actual meeting) — see polish list.
- ✅ 2026-06-17 — Live transcription preview MVP (rolling 30s caption via `/transcribe_chunk` + `live-transcript` event). Delegated whole-stack, reviewed + verified (73 tests, cargo check, tsc). Not yet verified live; see roadmap #2 for follow-ups.
- ✅ 2026-06-17 — Your-notes + AI-notes merge (live notepad during recording, kept verbatim + woven into the summary; `user_notes` column, "My Notes" tab). Delegated as two parallel halves (backend/data + frontend), reviewed + verified (70 tests, cargo check, tsc).
- ✅ 2026-06-17 — Chat-with-a-meeting feature (Chat tab + `/chat` endpoint + grounded `OllamaSummarizer.chat()` + Rust command). Delegated to worker, reviewed + verified (67 tests, cargo check, tsc all green).
- ✅ 2026-06-17 — Fixed both remaining 🔴 bugs: live HTTP-client URL update (no restart) + leak-free temp-WAV cleanup on failure; restored 5-min detector cooldown; Arabic section-icon map + "لا يوجد" empty state. (Delegated to worker, reviewed + verified.)
- ✅ 2026-06-17 — Default model → `qwen3.6:35b-a3b` (benchmark-won, ADR-008) + tolerant parser hardening (`_unwrap_envelope`).
- ✅ 2026-06-17 — Summary UI cards (collapsible, icons, action-item checkboxes) + copy-as-clean-text/rich-HTML + Export-to-`.md`.
- ✅ 2026-06-17 — Granola-style cream theme (inverted Tailwind gray ramp); Start/Stop pill button with live timer.
- ✅ 2026-06-17 — Auto-detect notification: native toast + Granola-style floating "Meeting detected" card (fixed the `"steam"⊂"msteams"` classify bug).
- ✅ 2026-06-17 — Arabic / multilingual summaries (toggle + default) with RTL rendering.
- ✅ 2026-06-16 — Structured LLM output (MeetingNotes schema) + attendee detection (chips); model configurable, default qwen3:8b.
- ✅ 2026-06-16 — Meeting auto-detection (registry mic-in-use → "Record this meeting?" prompt).
- ✅ 2026-06-16 — Summarizer: `num_ctx` (no more truncation) + `temperature=0` + role split.
- ✅ 2026-06-16 — Whisper CUDA `compute_type` → `float16` (correct for Blackwell).
- ✅ 2026-06-16 — Prompt overhaul: grounding (no fabrication) + speaker-label awareness + attendees.
- ✅ 2026-06-16 — Documentation suite (CLAUDE.md + ARCHITECTURE/HANDOFF/LESSONS/TODO/DECISIONS).
- ✅ 2026-06-12 — Microphone capture + speaker-labeled (`Me`/`Them`) transcripts.
- ✅ 2026-06-12 — Re-summarize a saved meeting with a different template.
- ✅ 2026-06-12 — Recording status auto-resets to idle; title markdown stripped.
- ✅ 2026-06-12 — GPU transcription working (`uv sync --extra cuda`); port/config fixes.
- ✅ 2026-06-11 — Phase 1 MVP: record → transcribe → summarize → store; tray + hotkey.
