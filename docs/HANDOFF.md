# Handoff

How to pick up this project cold. Current state, how to run it, and where to go
next. Update the **Current state** and **Last session** sections whenever you
pause or finish work.

---

> ⚠️ **HANDOFF top was stale (jumped 07-09 → 07-24).** The whole notch-pill arc
> (0.3.51→0.3.57, SHIPPED) and the 8 GB / model-tier research are recorded in
> **STATUS.md** (the current board), not here. Trust STATUS.md for current
> state; the dated sections below are historical detail.

## ⏭ NEXT SESSION STARTS HERE (2026-09-01, night) — LIVE CAPTIONS BUILT, VERIFIED, FOUNDER-SEEN; commit/merge is the next call

**COMMITTED on `feat/live-captions` and MERGED into `preview/all2` (founder
authorized, 2026-09-01 night; three commits: style fmt-normalization, feature,
docs). Not pushed; not on master. The founder used the dev app live and said
"it was super cool … the coolest thing that you've ever done."**

What shipped (5 Codex slices, Claude-specced/reviewed/verified; recon by Muse +
Antigravity — memos and specs in git-excluded `.recon/`):
1. **Transport + UI:** `/live_feed` → `{captions, partial}`; Rust `LiveFeedResult`
   + `live-partial` event (replace semantics per source, cleared on stop);
   companion renders a grey dashed-border italic partial line per source; the
   notch pill shows partials too.
2. **Engine:** `MoonshinePartialEngine` (sherpa-onnx `from_moonshine_v2`, Moonshine
   v2 tiny quantized ORT, English) re-decodes `unconfirmed_tail()` (watermark →
   buffer end, first-VAD-speech start, HARD 8 s cap — the ORT export crashes ≥10 s)
   on every 500 ms poll (`LIVE_CHUNK_MS`), OUTSIDE the Whisper lock; English-only
   self-gate via `note_confirmed_language` (Whisper's per-utterance language).
   Pin `live-captions-en` = HF `csukuangfj2/sherpa-onnx-moonshine-tiny-en-quantized-2026-02-27`
   @ `d1e6c309…` (~44 MB; `.ort` added to BOTH weight predicates in model_setup).
3. **Health + download:** `/health.live_captions_state`; auto one-time download in
   `useTranscriptionSetup` (only from `idle`; never re-fires after error);
   Settings › Transcription row "Live captions preview" (Download/Retry/progress/
   Active); `LIVE_CAPTIONS_ID` in `modelDownloads.ts`; Rust profile gate.
4. **Loop trim:** `trim_repetition_loop` keeps the sane prefix + one copy of a
   looped 1–4-gram (Moonshine loops on 0.5–2 s mid-word tails), applied to the
   preview only.

**Verified (my runs, not the workers' claims):** pytest 566 passed + 1 skipped ·
ruff clean · tsc clean · vitest 249/249 (25 files) · cargo fmt/clippy -D warnings
clean · cargo test 344 + 1 ignored. **End-to-end on the real service** (replaying
16 kHz deltas exactly like the Rust loop, `.recon/e2e_live_feed.py`): first grey
words at 0.5 s, revisions every 500 ms with casing+punctuation, 50–125 ms per
round trip incl. VAD, Whisper caption replaces the grey line at each ~1 s pause,
loops trimmed (before/after in `.recon` logs + LESSONS). Model fetch through the
real pinned pipeline: 44,256,550 bytes verified, engine hot-loaded via the
ready callback, health flipped missing→ready with no restart.

**Next steps, in order:**
1. ✅ DONE (2026-09-01 night): committed and merged → `preview/all2`.
2. The 08-31 baton's other two asks stand: Workshop Bench verdict; merge
   preview/all2 → master + version cut (docs on master are 4 commits ahead —
   expect a HANDOFF/STATUS conflict; keep both blocks).
3. Follow-ups already filed in TODO (09-01 entry): LocalAgreement stability
   option · Apple SpeechAnalyzer Swift sidecar as a macOS-native tier · Arabic
   preview when a model exists · low-end Windows CPU validation.

**Gotchas:** the Python service (slice-5 code) and `npm run tauri dev` are still
RUNNING from this session (pids in `.recon/service.pid` / `.recon/tauri-dev.pid`,
logs beside them). An old spool `7f3dbe5e…adversaria-spool` fails recovery at
app start with "no transcribable audio channels" — pre-existing, harmless, shows
in the dev log every launch. `.recon/` is excluded via `.git/info/exclude`
(local only). ADR-019 + LESSONS (probe assumption, ORT ≥10 s crash, `.ort`
predicates, loop trim) + ARCHITECTURE + TODO were updated this session.
## Session (2026-09-01, day) — live-captions two-layer decision, Bench awaiting verdict, Qwen probe verdict

**Everything verified lives on `preview/all2` (the INTEGRATION branch), nothing
merged to master. Founder starts fresh contexts from here.** The branch carries,
in order: the four earlier branches (transcribe watchdog, related meetings,
README refresh, workspace rebuild w/ capability model + two-pane screen +
run reports), todos done-view, D1 folders-vs-workspaces split (one-time
migration ALREADY RUN on the founder's dev DB), E1 compact task rows, E2
folder excerpts into local briefs, and the grounding fixes. Dev app runs it.

**DECIDED 2026-09-01 — live captions, two layers, both platforms:**
Layer 1 = streaming live captions via ONE cross-platform integration:
sherpa-onnx runtime inside the existing python-service (Python bindings, CPU
real-time on Win+mac), hosting Moonshine English first (Arabic later when a
good streaming model exists — sherpa is a model host, no re-plumbing).
Layer 2 = today's pipeline unchanged as the authoritative transcript (Whisper
large-v3/MLX/Qwen3-ASR, diarization, all languages); live grey word-by-word
text from layer 1 is REPLACED per utterance by layer 2 finals (the live/final
split already exists). Research ledger: docs/TODO.md 2026-08-31 🔬 entry (on
preview/all2, commit e13058b). NOT yet specced or built.

**AWAITING FOUNDER WORD:**
1. The Workshop Bench redesign of Workspaces — five-model open design round
   (codex/agy/muse/qwen3.8-local/Claude) converged on artifact-first; board
   (founder has seen it, no verdict yet):
   https://claude.ai/code/artifact/146ad588-1ced-4009-b8ca-cbf82342ca91
   Key locked-by-convergence ideas: default screen = the project's accepted
   work; thin "on the bench" strip with phase narration; Accept exists ONLY
   inside the full review sheet (kills accidental approve structurally);
   one-sentence Redo; sources strip with excerpt peek; committed-undo.
   Proposals in session scratchpad flowtext-*.md.
2. The merge train: merge preview/all2 → master (then version cut).
3. Live-captions build start (decided above, needs a spec slice).

**Qwen probe verdict (2026-09-01, closes the debate's riskiest assumption):**
qwen3.8:27b-mlx, given ONE ungrounded paragraph, produced a genuinely good
self-contained HTML with two labeled SVG diagrams incl. an unprompted
device-boundary privacy frame — but took 59 MINUTES and invented plausible
specifics where ungrounded (GGUF/ONNX, "no runtime download"). Implications:
local baseline quality is real; grounding (E2) and background-bench UX are
the answers; consider a fast drafting tier + big-model final tier for
artifacts. Output saved: scratchpad qwen-diagram.html.

**Gotchas for a cold pickup:** main checkout is ON preview/all2; three
worktrees still exist (../mnt-wt-{wedge,related,readme,todos}) with their
branches merged already — safe to `git worktree remove` when merging is done.
The founder's dev DB is SQLCipher-encrypted (no direct sqlite reads) and has
already run the folders migration. Full vitest must run
`--no-file-parallelism` while the dev app is up (load flakes otherwise).

## 🎯 Current pipeline (2026-08-31): capability rework toward the approved design

Design of record (founder: "Yeah looks good"):
https://claude.ai/code/artifact/54c73e5a-2077-4ce1-bc81-e217ede4983d
Debate verdict summary in STATUS 08-30/31 entries. Execution on
`feat/workspace-rebuild`, main checkout is ON that branch while C-slices run:
- C1 (Codex, in flight when this was written): format→capability rework —
  `capability` column, adapter_slugs_for_capability, catalog-independent
  suggest_capability (floor 3, tie = ambiguity = None), baseline
  "# Deliverable" contracts in compose_task_brief, missing-skill gating
  DELETED, four chips in the workspace create form and the To-dos menu.
  Spec: scratchpad `spec-capability-1.md`, result `result-capability-1.json`.
- C2 (spec pre-written, `spec-capability-2.md`): two-pane screen per the
  board + `preview_task_grounding` command; launch after C1 clears review.
- Then: merge wedge/related/readme/done-view/rebuild into a fresh preview
  branch, boot Python service + `npm run tauri dev`, founder click-through.
- Later (not specced): C3 durable project identity (canonical_root,
  vault_note, aliases) + transfer auto-detect; validated PNG/SVG export step.
If picking up cold mid-C1: check `git status` on the branch, read the result
JSON, review + verify (tsc / vitest / clippy / cargo test) before committing.

## 🏗 Overnight program (2026-08-30 night): the workspace rebuild is BUILT

Branch `feat/workspace-rebuild`, 4 commits (596df03 chips, d0a884b single
column, 817a84a transfer formats, b23083a run reports + network brief), built
by Codex from Claude specs (scratchpad `spec-rebuild-{1..4}.md`), each slice
reviewed + verified in the MAIN checkout (worktrees cannot run cargo; the
checkout was on the branch during the program and is back on master now).
Final gate: tsc clean, 231/231 vitest, cargo clippy -D warnings clean, 335
Rust tests + 1 ignored. All dev-gated (Workspaces tab is dev-only). NOT
merged, NOT pushed anywhere; founder reviews then merges. Review order
suggestion when merging everything: fix/transcribe-watchdog →
feat/related-meetings → docs/readme-refresh → feat/workspace-rebuild, full
suite after each (expect a trivial lib.rs/commands.rs conflict between
related-meetings and the rebuild; both add near the same registration block).
This build also closes both 08-26 🔴 workspace findings (silent wrong-skill,
network gate) — update TODO when it merges, not before.

## 🤖 In flight (2026-08-30, later): three worker branches await review/merge

Three stuntman workers ran in parallel git worktrees off `d579e4c`; if picking
up cold, check the branches and worktrees before starting anything new:
- `fix/transcribe-watchdog` (../mnt-wt-wedge, Codex): per-request timeouts in
  `http_client.rs` (health 5s, transcribe/import 30min, summarize 10min, NO
  client-wide default — model downloads stay untimed) + exported
  `raceWithWatchdog` in `useRecording.ts` wrapping the queue drain (45min),
  late-settle guard, watchdog test with fake timers.
- `feat/related-meetings` (../mnt-wt-related, Antigravity): `related_meetings`
  command (query = title + 600 chars of summary, threshold 0.55, limit 3,
  re-derives reasons from RelatedSignal without touching workspace_runs.rs),
  `RelatedMeetingRef` both sides, Summary-tab card in NoteViewer with
  `onOpenMeetingId` wired in App.
- `docs/readme-refresh` (../mnt-wt-readme, Muse): README-only accuracy pass to
  0.3.82; every claim must trace to CHANGELOG/STATUS/ARCHITECTURE; LinkedIn
  placeholder untouched.
Specs: session scratchpad `spec-{wedge,related,readme}.md`; results land in
`result-*.json` there. Process: review each worktree diff, run its verification
(specs include clippy -D warnings — see the 08-30 LESSONS entry), merge to
master one at a time with a full check after each, commit/push only with the
founder's word, then `git worktree remove` the three trees.

## ⏭ NEXT SESSION STARTS HERE — Meeting projects built; founder acceptance/commit next

**The sequencing question below is resolved by founder action (2026-08-29):** he saw
design renders for "projects in the Meetings tab", approved them, and said
"make codex work on this". So the PROJECTS surface builds first; the
related-meetings slice is NEXT after it ships. The block below this one is the
superseded recommendation, kept for the reasoning.

**Design board (approved, 6 artboards, matches the app's dark-glass tokens):**
https://claude.ai/code/artifact/5c77498d-b19a-4b89-8c4f-15374abf81b5
Meetings tab + projects sidebar · project screen · three creation doors
(+ button popup, record-start suggestion, move/drag). A project IS a
`workspaces` row; filing = `meeting_workspace_bindings` upsert. Nothing new
under the hood.

**Slice 1 — LANDED in the working tree (UNCOMMITTED), reviewed + verified:**
- Rust: `workspaces.instructions` + `workspaces.color` (guarded ALTERs in
  `storage.rs::init_db` AND the test-only `create_workspace_tables`; all 3
  CREATE TABLE copies updated), `create_workspace(name, color)`, new commands
  `set_workspace_instructions` / `set_workspace_network_allowed` /
  `set_workspace_color` (colour whitelist blue|purple|orange|green|red),
  registered in `lib.rs`. New round-trip + migration-idempotence test.
- TS: `types.ts` Workspace + wrappers in `tauri.ts`. `App.tsx` loads
  `projects` + `bindings`, `refreshProjects`, assign/create handlers, per-note
  suggestion fetch (session-dismissable). `MeetingsList.tsx`: Projects section
  (folders, counts, expand, + New project popup with colour dots),
  Move-to-project row-menu with `suggest_workspace_for_meeting` "suggested"
  marker, drag-to-file. `NoteViewer.tsx`: project chip in meta row +
  suggestion banner. Tests extended (MeetingsList, NoteViewer, fixtures).
- Verified by Claude directly: `npx tsc --noEmit` · `npm test` 207/207 ·
  `cargo check` · `cargo test workspace` 51 passed. Codex needed 0 feedback rounds.

**Slice 2 — LANDED in the working tree (UNCOMMITTED), reviewed + verified:**
new `src/components/ProjectView.tsx` (instructions editor with explicit Save +
"Saved" state + inline errors, network switch writing
`set_workspace_network_allowed`, meetings card, open action items via
`getActionItems(null)` filtered to bound meetings with working checkboxes via
`setActionItemDone`), new `ProjectView.test.tsx` (7 cases). `App.tsx`:
`selectedProjectId` state, content-pane priority project > note > empty,
ProjectView keyed by workspace id so drafts re-seed, project cleared on every
note-open path, missing-project guard effect, "Open in Workspaces" passed only
when `import.meta.env.DEV`. `MeetingsList.tsx`: row click selects + expands,
chevron is its own stop-propagation button, `mrow--selected` on the active
project. Verified by Claude directly: `npx tsc --noEmit` clean ·
`npm test` 214/214 (25 files). No Rust changes in this slice.

**ProjectView refinement — LANDED in the working tree (UNCOMMITTED), 2026-08-29/30:**
- Replaced the old 760px left-skewed content column with a centered, 1440px
  responsive canvas. Wide panes use two independent columns (overview +
  meetings + project controls / action items), so a tall action list cannot
  push Meetings down or create a fake blank row; narrow panes stack cleanly.
- Removed the overview prose's artificial 65ch cap after the founder caught
  obviously premature wrapping inside a much wider card. The prose now uses
  the available project column. Meetings, Standing instructions, and Web
  research form one left-column sequence; the right rail is action items only.
- Rebuilt action rows after the founder caught the bad two-column formatting:
  the task owns the full row and wraps naturally; its source meeting is quiet,
  clickable metadata underneath instead of a competing half-width column.
- Added a cached AI Project overview generated by the Notes engine selected in
  Settings, grounded in filed meeting summaries/transcript excerpts. It shows
  stale/update, refresh, retry, empty, and preserve-cache-on-error states and
  never uses web browsing. Attendee chips are deterministic, deduplicated, and
  show meeting frequency without inventing stakeholder roles.
- Overview prompt v2 carries the exact filed-meeting count in both context and
  instructions, begins with "Across these N meetings," and forbids confusing a
  grouped thread count with meeting count. The prompt version participates in
  the source hash, so older misleading cached summaries become stale.
- Standing instructions are no longer decorative storage: they now influence
  both Project overview generation and every workspace task brief. UI copy now
  says exactly that. The network control is named "Web research" and clarifies
  that it applies only to workspace tasks, not Project overview generation.
- Added guarded workspace overview cache columns + persistence, source hashing,
  command/type/wrapper plumbing, prompt-grounding tests, and ProjectView state/
  interaction coverage.
- Added project deletion to the Meetings sidebar: permanently visible project
  ⋯ menu → in-app
  confirmation → existing `delete_workspace` command. Meetings survive and
  become unfiled. Backend deletion now also removes `meeting_workspace_bindings`
  for that project so no orphan bindings remain; the other projects/bindings
  are preserved. This lets the founder safely remove the two accidental empty
  "Youtube" projects without deleting any meetings.
- 08-30 follow-up: the first live check was against a stale orphaned app window
  after the Vite/Tauri dev process had died, so the new menu was absent despite
  green tests. Restarted the real dev process, made ⋯ visible at rest instead
  of hover-only, and manually clicked Youtube ⋯ → Delete project → confirmation
  (then Cancel, leaving data untouched).
- Verified: `npx tsc --noEmit`; 225/225 Vitest tests
  (25 files); `cargo fmt --check`; `cargo check`; 330 Rust tests passed, 1
  ignored; Impeccable layout detector clean. Native wide-window click-through
  confirmed the five-meeting overview, full-width prose, and the requested
  Meetings → Standing instructions → Web research hierarchy.
- Documentation contract audit completed 08-30: updated root `HANDOFF.md`,
  `README.md`, `SPEC.md`,
  `STATUS.md`, `docs/ARCHITECTURE.md`, `docs/TODO.md`,
  `docs/DECISIONS.md`, `docs/LESSONS_LEARNED.md`, and
  `docs/DEEP_DIVE_TECHNICAL.md` alongside this handoff. Reviewed
  `STRATEGY.md`; no change was warranted because this implementation did not
  alter product strategy or market direction.

**Consciously deferred:** record-start "File under" chips (the suggestion
command ranks on title+summary which don't exist at record start; no calendar
signal). The post-transcription suggestion banner covers filing. Also deferred:
per-item transfer for cross-project meetings (workspace-rebuild scope).

**Release state (0.3.82, 2026-08-30):** feature commit `635101f` + bump
`b5695b2` + clippy test-fix `eb6f33a` all pushed. Public PR #29 merged (PR #28
superseded: public CI's newer clippy flagged three test-only slice-from-ref
lints local clippy 1.96 does not). macOS DMG notarized (Accepted, 667e2184),
stapled, validated; stable-name copy regenerated post-staple. Windows CI run
33306628912 dispatched (channel=beta, bundle_cuda=false). **SHIPPED & VERIFIED 2026-08-30:**
Windows CI succeeded, artifact downloaded on first try, published via
`publish-release.sh` with both platforms. Post-publish verification passed
every check (manifest 0.3.82, downloads, provenance sha256, minisign, key id
matches the pinned verifier, stable DMG asset live). Release:
https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.82

**Next steps, in order:**
1. Founder click-through in the dev app (`npm run tauri dev` + Python service):
   create project, drag a meeting in, chip on note, suggestion banner,
   project screen edits (instructions save, network toggle, action items).
2. Commit ONLY when the founder authorizes.
3. Then: the related-meetings slice (retrieval exists in `workspace_runs.rs`;
   surface in `NoteViewer.tsx`) — the old recommendation's first item.

## [superseded 08-29] The sequencing decision (recommended, awaiting founder call)

The founder named three open items and asked which to build first:
(1) fix the workspace (the locked 08-27 redesign), (2) related meetings under
each meeting note, (3) projects/folders in the Meetings tab (drag meetings in;
context-aware — the unified container's meeting face).

**Claude's recommendation, reasoned in-session: 2 → 3 → 1.**
- **First: related meetings under the note.** One Codex slice. The retrieval
  already exists — the workspace context engine computes "top 3 related via
  graph" with reasons per run; this only renders it on the meeting page. Daily
  value; also generates the "same project?" suggestion signal for item 3.
- **Second: projects in the Meetings tab.** NOT new infrastructure:
  `meeting_workspace_bindings` already maps meeting→workspace (one per meeting
  is CORRECT for meetings; only action items needed per-item routing). This is
  a surface: folders in the sidebar, assign/drag, meeting page shows its
  project. FOLD IN the standing-instructions field and the network toggle here
  ("context-aware" = exactly those two). Foundation for the copilot/live rail.
- **Third: the workspace rebuild** (format chips, single-column work face,
  per-item transfer, report-what-it-did). Deliberately last so it is built ONCE
  on the settled container — the unification reshaped the container, and
  building the workspace UI before projects land invites rework. The quality
  unlocks it would have delivered (network, instructions) ride with item 3.
- Copilot / live rail: after projects exist.

**Status: RECOMMENDED, not decided.** The founder said "let's think about it,
then update handoffs once we make a decision" and is starting a new context.
If the founder confirms 2→3→1 (or picks another order), update this block to
DECIDED and start with one Codex slice for the first item. Everything needed
to spec slice 1 is in this repo: `select_related_meetings` + `context_receipt`
in `workspace_runs.rs` (the retrieval + reasons), `NoteViewer.tsx` (the
surface), and the 08-26 🟣 TODO entry (the original related-meetings ask).

## Session (2026-08-29) — THE UNIFICATION: one "meeting workspace", two faces

**Supersedes the thread≠workspace split recorded below (08-27/28).** The founder
collapsed threads and workspaces into ONE container per project. The loop:
meeting → side quests → workspace produces artifacts → artifacts join the
project's MEMORY → the next meeting's live rail draws on prior meetings + open
items + those artifacts ("if they mention something, I can refer to my
research"). Two faces of one object: a meeting face (record, live rail,
briefings — surfaced in the Meetings area) and a work face (tasks, artifacts —
the Workspaces tab). At record start the app suggests which project the meeting
belongs to; the founder confirms. Also articulated: the in-meeting COPILOT
intent (ask meeting kind at record start; interview → surface his own history;
follow-up → where-we-left-off; client-solutioning → clearly-marked suggestions;
retrieval-first is safe, generation is the risky tier). Full entry at the top
of `docs/TODO.md` (2026-08-29). The three boards (Side-Quest Offloader /
Meeting Room / Threads) are to be MERGED into one board around this loop when
the founder calls it. **Nothing built; no code changed this session-day.**
Attachment-test follow-up: the founder's 08-28 "nothing happened" was NOT a
bug — he staged context but never completed a stop; `meeting_attachments`
correctly has no rows. Watch the first real stop-and-summarize.

## Session (2026-08-27/28) — WORKSPACES DESIGN RESET (founder-led; direction locked, build deferred)

**The founder rejected the built direction and re-explained the product.** He is a
lead AI engineer / IC across many projects; every meeting produces 2–3 side
quests that pull him off real work. Today he does each one by opening VS Code →
the right repo → Claude Code → re-explaining the meeting. The workspace exists
to collapse that to one button. The staffing machinery built on 08-25/26
(per-task Run setup, automatic/manual modes, catalog panel) was a control panel
for choosing who does the work — not the work. Treat ADR-017's UI surface as
superseded by the decisions below (the backend table + queue-time resolution
remain fine as plumbing).

**An adversarial Codex design pass (full transcript in the session; findings all
code-verified) surfaced:** (a) runs are cwd'd to a SCRATCH dir
(`config.rs::workspace_run_dir`; `commands.rs` `.current_dir(&output_dir)`), so
the product drafts documents ABOUT projects, never works inside one; (b)
`scan_output_files` recursively records EVERYTHING under cwd as artifacts — so
naively pointing cwd at a repo would register the whole codebase as run output;
(c) approve/reject only flip DB state, nothing applies/rolls back files; (d)
`workspaces` has NO curated instruction/memory field ("it accumulates
transcripts, not understanding"); (e) `meeting_workspace_bindings.meeting_id`
is the PRIMARY KEY — one meeting binds to ONE workspace, so a cross-project
stand-up cannot split its action items; (f) the staffing matcher accepts ANY
positive keyword score — which is how "build a landing page" silently produced
a Marp slide deck.

**Founder decisions, LOCKED (in order given):**
1. **No repo-touching. Parked.** Worktrees/diff-review/verification deferred
   ("working in existing repos can be destructive"). The workspace is an
   **artifact factory**: diagrams, landing pages, research, docs, decks. Code
   changes go through the companion MCP + Claude Code manually.
2. **One workspace = one project.** Context compounds (meetings, repo, design
   system, artifacts, instructions). A meeting covering 3 projects = 3
   workspaces. The `Test` grab-bag is the anti-pattern. Requires per-ITEM
   transfer (see blocker (e)).
3. **Kill the split view.** Single-column project screen: header states what
   the project knows; standing instructions above the work; tasks grouped
   Needs-you / Running / Queued / Done; sources move to Project settings.
4. **Transfer is the founder's act** from the to-dos list; app suggests after.
   Personal items ("call that guy") NEVER route — no inbox-that-runs-nothing.
5. **Output format is chosen by the founder via chips** (+ draw.io, + HTML,
   + slides, + PNG, + doc, + research). The skill follows from the format; the
   matcher only suggests. This DELETES the per-task staffing UI direction.
   Missing format = dashed chip that says so and offers to add the skill.
6. **Tasks report what they did** in plain language ("7 components confirmed in
   code; queue + auth provider undecided, marked dashed") above the files.

**Design board (4 passes, final):**
https://claude.ai/code/artifact/3deb99ac-d9b7-481f-93be-d6ad82d85cd2
Agreed build order (NOT started — founder: "we will do this later"):
format chips → standing instructions → per-item transfer → single-column
screen → report-what-it-did + network enforcement.

**NEW founder ask (08-28, noted only — do not execute):** the full-screen
in-meeting view (`RecordingCompanion.tsx`) wastes a wide window — one centered
vertical stack (transcript, divider, notes). Asks: dock the transcript to one
side; a **+ button to add context mid-meeting** (documents, previous
meetings); and — future — **"meeting projects" in the MEETINGS area, not
workspaces**: interconnected meetings that surface highlights and
things-to-talk-about live. Ties into the parked 🟣 related-meetings/pre-meeting
briefing ask (TODO). Concept artifacts made this session (links in TODO entry).

**LATER (08-28): the Meeting Room board was APPROVED and BUILT** (founder:
"looks good, do it, make codex do it too and audit its work"). Two Codex tasks,
both audited by Claude (diff review + all four suites run independently):
1. **Docked wide layout** — `RecordingCompanion.tsx` balanced variant gains
   `balanced-wide`; ≥900px the transcript docks left (`clamp(320px,34vw,460px)`)
   and notes take the rest full-height; narrow keeps the old stack; new
   `RecordingCompanion.test.tsx` (4 tests).
2. **"+ add context" mid-meeting** — `meeting_attachments` table (+ delete
   cleanup), `pick_context_file` (rfd, md/txt), add/list/remove commands;
   **staged in App state during recording, committed at stop** (no meeting row
   exists until `enqueueRecording` returns — commit is best-effort, cannot fail
   the stop); `attached_context` threaded SummarizeParams → `/summarize` →
   summarizer, mirroring the `<user_notes>` block with an explicit
   "background material, NOT things said in the meeting" instruction; caps 5
   attachments / 4k chars / unreadable → marked line; rail UI ("THIS MEETING
   KNOWS", + Add file, + Add meeting from 10 recent, staged list with ×).
   Injection at 5 real summarize sites; None at import-flow (row not yet
   created) + 2 connectivity smokes, each annotated.
   The thread-highlights rail ("From past meetings") is NOT built — it belongs
   to the parked threads arc.
Suites after audit: Rust 316 · Python 545 · vitest 200 · tsc clean.

**⚠ Audit finding on OUR OWN process:** commit `7353380` (the prompt rewrite)
had silently BROKEN the Python suite — its tests pinned the old templates'
`**"…"**` heading shape and `Owner:` literal. Nobody ran pytest before that
commit (cargo/vitest/tsc only). The Codex worker repaired the 3 test files
(coverage preserved — assertions now pin the new template contract, e.g.
`beginning \`Me:\``). Lesson recorded in LESSONS_LEARNED: the pre-commit gate
must include `uv run pytest` whenever `python-service/` (including prompts/)
is touched.

**Tree right now (uncommitted, intentionally — founder authorizes commits
explicitly):** the Meeting Room slice (21 files), the `addons.rs` drawio
palette fix, and these docs. 5 commits pushed through `4bca9bf`. Leftover test
tasks 19-22 in the Test workspace; agents PAUSED.

## Session (2026-08-25) — back to Workspaces: the founder's pending ledger

0.3.81 is out (section below); the founder redirected to Workspaces and asked
what of THEIR asks is still open. Verified against the code (no Grok wiring, no
export action, no take_group anywhere) and answered; this is the authoritative
pending list:

1. **Grok (xAI) BYOK + "Get 2 takes"** (locked decision, phase 3c) — not
   built; Grok exists only as a Settings provider hint (`types.rs:484`).
2. **Export after Approve** ("Copy into project" / "Send to vault" as a
   separate opt-in action) — second half of locked decision #4, not built.
3. **Meetings as Projects slice 1** — build blocked ONLY on the founder's
   per-project **Agents on/off switch** decision ("filing ≠ running").
4. **Share sheet** — brainstorm done (board published); founder still owes:
   paste-a-token auth OK? · Slack payload scope? · People tab before CRM?
5. **Small open calls** never ruled on: done signal (toast vs pill flash) ·
   retrieval caps (3 meetings / 5 notes) · binding threshold · per-task time
   budget (10 min?).

## Session (2026-08-26) — the day's work committed; one live 🔴 filed

**Committed to master (3 commits, NOT pushed):** `7353380` the held foreign-prompt
rewrite (~34% shorter templates; section headings renamed but "Action Items" kept
deliberately — both extractors match headings by pattern, `ACTIONABLE` in
`src/lib/summary.ts` and `re_actionable` in `storage.rs`, so extraction is
unaffected); `ca3823b` the workspaces arc (per-task staffing per ADR-017 +
`.drawio` validation + the Run setup UI + retiring `WorkspaceAddons`); `26234b8`
the docs. Code landed as ONE commit because the Draw.io and staffing work rewrite
the same call site in `execute_workspace_run_inner` — splitting by file would have
produced a non-compiling intermediate commit. 313 Rust + 190 frontend tests green
on the committed state.

**🔵 FIRST REAL TEST-DRIVE of auto-staffing (founder, six seeded tasks) — the
matcher held up; what it staffs did not.** Full detail at the top of
`docs/TODO.md`. Three findings:
1. **Diagrams came out black-and-white — FIXED, uncommitted.** The built-in
   `drawio-diagram` fallback had no `fillColor` at all, so every engine without
   the full drawio skill loaded drew grey boxes. `addons.rs` now carries a
   semantic palette (draw.io's canonical pairs: blue service, green datastore +
   `shape=cylinder3`, yellow queue, orange gateway, grey external w/ dashed
   edges, red error, purple model), rhombus decisions, swimlane grouping, and
   coloured edges. 316 Rust tests still green.
2. **🔴 The research task could not research.** Deep research correctly refused
   to use outside knowledge because network was not granted, and returned an
   honest but useless answer. **The unblock is half-built already:**
   `workspaces.network_allowed` EXISTS (`storage.rs:504`, default 0) with no UI
   and nothing feeding it into the brief. **This is my recommended next slice** —
   smallest change, makes an existing skill actually work, and unlocks porting
   LL-OS `DeepResearcher`.
3. **🔴 "Build a landing page" silently produced a Marp slide deck.** No
   front-end skill exists, so the matcher ran the nearest wrong one with full
   confidence — exactly the Skill Finder case from the board. Rule to build:
   below a score threshold, staff NOTHING and name what is missing. A silent
   wrong skill is worse than no skill.

**🟣 NEW founder asks, parked deliberately — "meetings need to know about each
other".** Two parts, filed in full at the top of `docs/TODO.md`: (a) show
**related meetings beneath the generated notes** (daily stand-ups across two or
three projects, client meetings — each note is an island today; this is mostly a
SURFACING job, the retrieval already exists via `hybrid_rank` + graph +
`select_related_meetings`), and (b) **projects/threads plus a pre-meeting
briefing** — before a client call, tell the founder what was discussed last time,
what to cover now, and which action items are still open. (b) overlaps
**Meetings as Projects** so heavily that the first question is whether it IS that
feature's slice 1. Founder wants an artifact for this once the shape is decided.
**Parked on purpose — Workspaces continues first.**

**🔴 Known, unfixed, DEPRIORITISED by the founder ("never mind this") — a hung
transcribe request wedges the background queue.**
Founder repro: changed the notes model mid-transcription; a "Transcribing…" tag
stuck on a meeting that had actually finished. Not cosmetic — while
`transcribingId` is non-null the drain effect early-returns
(`useRecording.ts:150`), so NO further background transcription runs that session.
Cause: the shared HTTP client has no timeout (`reqwest::Client::new()`,
`http_client.rs:281`) and there is no client-side watchdog, so a request the
service never answers leaves the promise unsettled and `.finally()` never clears
the id. Full analysis, evidence (meeting 247 completed and persisted; audio
deleted), and the fix shape are at the top of `docs/TODO.md`. **Careful:** the fix
is per-request timeouts, NOT a global one — `http_client.rs:388` warns the client
must not impose a short timeout because model downloads are multi-GB.
Workaround: restart the app. Check whether meeting 245 is a casualty.

**Still outside the repo:** stuntman v0.9.1 is pushed (`ae05a0e`) but the plugin
cache is still 0.9.0, so the vault nudge is NOT running until `/plugin` → update.
The 0.3.81 vault-page rewrite still awaits founder review at
`laghari-vault/wiki/projects/meeting-note-taker.draft.md`.

---

**Later same day — ADR-017 per-task staffing backend landed (Codex-built,
Claude-reviewed, uncommitted).** Founder rejected the tab-level catalog ("why a
dropdown you can't click"); design review by Claude + an independent Codex pass
converged on the same answer, now recorded as **ADR-017** in `docs/DECISIONS.md`.
Backend slice A is in: new `workspace_task_staffing` table (task_id, mode,
agent_id, skill_ids, reason, resolved_at); staffing resolved + persisted **at
queue time** (`resolve_task_staffing`, never overwrites a `manual` choice);
`execute_workspace_run_inner` now reads persisted staffing with an inline
fallback for pre-existing tasks; the `addons.is_empty()` trapdoor is **gone** —
workspace-level attach no longer influences staffing at all. New commands
`get_workspace_task_staffing` / `set_workspace_task_staffing` (mode "automatic"
re-runs the matcher = the Re-evaluate action). 4 tests, 313 pass, check clean.
Founder call, no gate needed: **automatic staffing runs unattended** ("it doesn't
need my eye for automatic") — the receipt is the audit trail.
NEXT (slice B, frontend): delete `WorkspaceCatalog.tsx` + its render in
`WorkspacesView.tsx` (wrong location, no verb, and its rows used a `:hover`
class that faked interactivity), and add a per-task "Run setup" line —
`Automatic · Diagrammer + Draw.io diagram / because the task mentions "diagram"`
with a Change panel offering Automatic (recommended) or Choose manually.
THEN (slice C): "View capabilities" read-only list of the 4 agents + 6 skills
with descriptions, with custom agent/skill creation moved inside it.
CAUTION for slice B: `WorkspaceAddons.tsx` (workspace-level attach chips) is now
vestigial for staffing — decide whether to remove it or repurpose it, don't
leave two competing controls.

**Later same day — catalog panel on the Workspaces tab (Codex-built,
Claude-reviewed, uncommitted).** New `src/components/workspaces/WorkspaceCatalog.tsx`
rendered from `WorkspacesView.tsx`: agent/skill counts, `+ Agent` / `+ Skill`
create forms, Remove on custom entries, "Built in" on the rest. Frontend-only —
`create_workspace_addon` already accepted a `kind`, but the ONLY existing create
form (`WorkspaceAddons.tsx:114`, inside a workspace) hardcodes `"skill"`, so a
custom **agent** was previously impossible to create from the UI. That form is
untouched; the new panel is catalog-level and does not attach what it creates.
6 vitest cases, full suite 194 pass, `tsc --noEmit` clean, verified running in
the dev app. `+ MCP` deliberately NOT built — it needs backend schema + engine
plumbing and is its own slice.

**Delegation routing FIXED (outside the repo, worth knowing).** `/delegate` had
never reached Codex: `command -v stunt` resolved to a stale 2026-06-10 binary at
`~/.local/bin/stunt` whose backends were only `claude|opencode` — no codex support
at all — so every delegation silently used the free-claude-code proxy. Now
`~/.local/bin/stunt` is a symlink to
`~/.claude/plugins/marketplaces/stuntman/bin/stunt` (a git checkout, so it stays
current across version bumps; the old binary is kept as `stunt.stale-2026-06-10.bak`),
and `export STUNTMAN_WORKER=codex` is in `~/.bash_profile` + `~/.zshrc`. Verified
in a clean login shell: PATH binary, no override → `{"backend": "codex"}`.

**Later same day — Workspaces auto-staffing landed (Codex-built, Claude-reviewed,
uncommitted).** Founder complaint: having to attach the Diagrammer agent + Draw.io
skill by hand before every diagram task. Now `workspace_runs::suggest_staffing`
(deterministic keyword scoring + a domain-word bonus table, no deps) picks an
agent and up to 2 skills from the catalog **only when the workspace has no addons
attached** — manual attachment stays an exact override, byte-identical to before.
Every auto-pick writes a reason line at the top of the run receipt ("Chose the
Diagrammer agent automatically — the task mentions \"diagram\"."). Also added
`suggest_workspace_staffing` (preview command for the future UI, registered in
`lib.rs`). 6 new tests, `cargo test` 309 pass, `cargo check` clean.
Design board for the whole Workspaces phase-3d arc (8 founder asks, mechanism,
screens, schema deltas, build order, verdicts on Prime Agent / DeepSeek Harness /
LL-OS Deep Research):
https://claude.ai/code/artifact/ccaa71e8-ca51-4138-a46e-f4ba1d6a7754
Next slices from that board, in order: catalog + `+ Agent`/`+ Skill`/`+ MCP` UI
(note: `create_workspace_addon` ALREADY exists in the backend — this is a UI-only
gap; MCP support does NOT exist anywhere in Rust and is genuinely new), then
per-workspace model + Integrations panel, then Skill Finder, then porting
LL-OS `DeepResearcher` behind the per-workspace network switch.

**Later same day — Draw.io skill upgraded + .drawio validation (Codex-built,
Claude-reviewed, uncommitted):** the built-in `drawio-diagram` addon produced
broken XML from small local models with no validation (founder repro: the 4B
tier failed; the claude engine succeeded but drew from a stale vault page).
Changes on the tree: (1) `addons.rs` — `drawio-diagram` instructions now defer
to the full **Agents365 drawio-skill** (installed at `~/.claude/skills/
drawio-skill`, MIT, auto-loaded by claude-engine runs since they run `claude
-p` — verified) and carry much stricter fallback XML rules for local models;
(2) `workspace_runs.rs` — new `validate_drawio` / `drawio_artifact_warnings`
(quick-xml 0.41): well-formedness, mxfile→diagram→mxGraphModel→root nesting,
≥1 vertex, compressed-payload detection, 6 new tests; (3) `commands.rs` —
both run-completion paths append per-artifact validation warnings to the run
log. `cargo test` 303 pass, `cargo check` clean. Related, outside this repo:
stuntman gained a vault-staleness Stop-hook nudge (source repo v0.9.1 — the
installed plugin cache is still 0.9.0 until the founder updates it), and a
0.3.81-accurate rewrite of the vault page awaits founder review at
`laghari-vault/wiki/projects/meeting-note-taker.draft.md`.

**Later same day (read-only):** founder asked why the Engine dropdown shows
Qwen 3.5 4B as "not downloaded" while `qwen3.5:4b` sits right below it as "on
this computer". Diagnosed, no code changed: curated tiers check the app
**sidecar** store (27434) for the *effective* tag — the MLX variant on this
Mac — while the raw rows scan the user's own Ollama (11434). Filed with
file:line refs and fix options at the top of `TODO.md` (2026-08-25 entry).
Working tree still carries only the held-out foreign-prompt rewrite (8
`python-service/prompts/*.md`, intentionally uncommitted).

Everything else the founder asked for in the Workspaces arc is BUILT and live
in dev (routing, auto-push+dedup, autopilot+pause, review queue with
done-by-agent evidence, artifact previews, context engine with receipts,
skills & agents catalog, local-model real files, needs-you triage). Proposed
sequence: Agents-switch decision → spec Meetings-as-Projects slice 1 for
Codex; Grok/2-takes and export-on-approve are one delegation each.

---

## Session (2026-08-24, publish day) — 0.3.81 SHIPPED + VERIFIED (both platforms)

**Outcome (~21:55): published to beta and independently verified** — manifest
live at 0.3.81, macOS `.app.tar.gz` + Windows setup.exe both download, sha256s
match provenance, minisign signatures valid. macOS DMG came from build attempt
6 (notarized, stapled, Gatekeeper-accepted; stable-name copy regenerated by the
script). Windows exe came from run 32686585055 (public main `95109f3`, /health
fix proven on its smoke). Late additions to the failure trail: attempt 4 died
in its first minute on the KNOWN stranded-`dist` APFS rm gotcha (LESSONS
2026-07-17); attempt 5 then ground SEVEN HOURS in the same rm because a
forgotten `rapid-mlx serve qwen3.6-35b` benchmark server (30 h resident) was
squatting on RAM — cure was: kill build + server, `mv` the stranded trees aside
(4 ms rename; NOTE the session scratchpad is a DIFFERENT volume, mv there
copies!), delete in background, relaunch. Attempt 6 then passed every gate
first try, including the 3.5 smoke, confirming the Gatekeeper refusal was a
one-off. Post-ship: `build-dmg.sh` gained a pre-signing `xattr -cr` (comment
records the honest mechanism), docs updated, foreign prompt rewrite restored
to the tree uncommitted (its own session owns it).

**TL;DR (cut phase).** 0.3.81 is committed (`9161a3f` + clippy `81a8648` +
health fix `7e64431`); public main mirrors it (PR #26, #27 merged). Publish
was **Mac-first by founder decision** ("right now I just want specifically for
Mac"): Windows happened to go green first anyway, so both shipped together.

The three publish failures and their causes (full detail in LESSONS):
1. **Windows CI run 32684423145 — real 0.3.81 regression.** The new
   `_embedding_health()` (bge-m3 catalogue check) probed the same down Ollama
   host right after `backend_available()`; stacked connect timeouts pushed
   every `/health` past the smoke's 5 s client budget. Fix `7e64431`
   (`server.py`: skip the second probe when the summarizer just found that
   exact host down; regression test proves no second connection). 543 pytest
   pass. Rerun 32686585055 dispatched from fixed main `95109f3`.
2. **macOS attempt 1 — transient notary-credential pre-check failure.** The
   identical `xcrun notarytool history --keychain-profile adversaria-notary`
   succeeded in sandboxed AND unsandboxed background probes minutes later;
   relaunch passed the check. Machine flake, not config.
3. **macOS attempt 3 — Gatekeeper refused ONE freshly signed lib**
   (`av/codec/hwaccel.abi3.so`, "library load disallowed by system policy")
   at the stage-3.5 smoke. Not quarantine (dist copies carry NO xattrs —
   PyInstaller doesn't propagate them; 250 venv Mach-Os DO carry
   `com.apple.provenance`), not a signing race (signing is serial), and the
   same smoke passed attempt 1. syspolicyd was mid trust-evaluation churn at
   the exact smoke timestamp; this box's syspolicyd wedged twice on 08-23.
   Mitigation: pre-signing `xattr -cr` added to `scripts/build-dmg.sh`
   (**uncommitted**; comment overstates the mechanism — correct it before
   committing). If the flake repeats: bounded retry of the smoke, or reboot.

**Next steps (post-ship):** (1) founder confirmation that 0.3.81 updates
cleanly on the QA account; (2) ~~attendee-chip commit-on-blur fix~~ **DONE
post-ship (`67b4905`**, blur commits the rename, Escape cancels; vitest 188 +
tsc clean; rides the NEXT release — 0.3.81's installers were already built);
(3) ADR-016 **step B**
(remove rapid-runtime/, setup.rs Rapid-MLX branches, llama_engine.rs,
build-dmg stages) and **step C** (bundle the `ollama` binary); (4) founder
decisions still open: per-project Agents on/off switch, share-sheet
auth/payload/People-tab questions; (5) 7 dependabot vulns on the public repo
(4 high).

---

## Session (2026-08-22 → 23) — Workspaces Autopilot + context engine built (uncommitted)

**TL;DR for a cold start.** In one day the Workspaces feature went from a design
board to a working, live-tested system, built by Codex in 8 reviewed delegations
(Claude spec'd every one, reviewed every diff, re-ran every gate; 3 feedback
rounds). What is live in `npm run tauri dev` right now: meeting→workspace
binding with graph suggestion · to-dos auto-pushed · autopilot (one run per
workspace, global Pause, crash-safe) · review queue with Approve/Reject ·
in-app artifact preview · related meetings with a relevance floor · a real
local-model drafting path (`/draft_stream`) · skills & agents catalog ·
**the context engine: Obsidian vault + projects folder indexed and searched
by the to-do text on every run** (first sync 355 vault notes · 56 projects;
"MIQ" and "website" lookups verified against the DB). Final gates on the
tree: **cargo 278 · clippy · fmt · tsc · vitest 183 · pytest 175 (+1 foreign
failure)**. Boards: Autopilot https://claude.ai/code/artifact/28a0832e-be32-4c0e-9b7b-75ed04cd6328
· Meetings as Projects https://claude.ai/code/artifact/b69dacc7-dafb-4eca-90c0-a10895cf9e74 · Share sheet https://claude.ai/code/artifact/16583952-cf7f-4ee9-8fb3-8341de9ad52b.
**Decisions waiting on the founder:** per-project Agents switch ("filing ≠
running") · Share-sheet auth/payload/People-tab questions. **Read the
delegation paragraphs below in order; each names its files and gates.**

**Working tree is dirty and NOT committed** (founder authorises commits). Two
halves in one day:

1. **Design.** Founder pitched "every to-do automatically lands in a workspace,
   agents work it with the meeting graph + Obsidian vault + project folder, I
   approve or reject from a progress card." Four decisions locked, annotated
   board published: https://claude.ai/code/artifact/28a0832e-be32-4c0e-9b7b-75ed04cd6328
   Recorded in the **TODO.md top block (2026-08-22)**.
2. **Build (Phase 3a, Codex via stuntman, 3 sequential delegations + 2
   feedback rounds, every diff reviewed and every gate re-run by Claude).**
   Specs live in this session's scratchpad only; the code is the spec now.

**What landed (all dev-gated like the rest of Workspaces):**
- `storage.rs`: `workspace_tasks` rebuilt (`migrate_workspace_tasks_v2`) with
  status `awaiting_review` + `action_item_id`/`attempt`/`rejection_notes`; new
  `meeting_workspace_bindings` table (row with NULL workspace = "not a
  project", no row = undecided); `approve_workspace_task` /
  `reject_workspace_task`; `push_meeting_action_items` (open, "mine" to-dos of a
  bound meeting → tasks, deduped by `action_item_id`); `sync_action_items`
  re-links tasks after re-extraction (ids change!) and pushes new items;
  `next_queued_task`, `workspace_has_running_task`,
  `requeue_orphaned_running_tasks`, `fail_task_that_could_not_start`.
- `commands.rs`: `execute_workspace_run` (shared by Run button + autopilot, log
  via `workspace_runs::LogSink`), one-run-per-workspace gate
  (`AppState.autopilot_gate`), `suggest_workspace_for_meeting` (hybrid_rank +
  shared attendees, score = 2·related + shared, ≥ 2 to suggest), binding /
  pause commands, `workspace-task-changed` Tauri event.
- `autopilot.rs` (new): `kick(app)` → drain: skip if `AppConfig.agents_paused`,
  per workspace with nothing running start the oldest queued task on the
  workspace's engine if available. Kicked by: task created, binding set, reject,
  resume, engine changed, every run end (only after a run really existed),
  every summary sync (`sync_actions_for_meeting` now takes `&AppHandle`), and
  15 s after launch. Startup also re-queues tasks left `running` by a crash.
- Frontend: card ring (approved/total) + running/awaiting/queued counts,
  Pause bar, review queue (Approve / Reject… with required note, run log,
  artifacts, attempt badge), 2 s polling panel for runs this window didn't
  start, `WorkspaceBindingBanner` on the meeting page (suggestion preselected,
  Confirm / Not a project / Change… / Unbind), `→ Workspace` chips on the to-do
  board, `Push to workspace…` menu now links `action_item_id`.

**Deviations from the board (deliberate, 3a scope):** binding lives in its own
table, not `Meeting.workspace_id`; no `rejected` / `needs_you` task statuses
(reject re-queues immediately; needs-you classification is 3b); receipt is
still the brief's own context (3b); per-task time budget unchanged (15 min).

**Verified (Claude, on the final tree):** cargo test 252 passed / 1 ignored ·
clippy `-D warnings` · cargo fmt · tsc · vitest 158/158 · `git diff --check`.
**Live-verified in `npm run tauri dev` (2026-08-22 ~17:35 local):** migration
applied on first launch; autopilot started the queued task 15 s after launch
on Claude Code (run 2 min 04 s → `awaiting_review` + `social-calendar.md`);
founder confirmed the binding banner on meeting 165 → 4 open to-dos pushed
(tasks 3–6, linked to action items 288–291); the queue drained one task at
a time. Two findings for 3b: (1) "Record 90-second demo video" was run by
an agent, i.e. the needs-you classification is needed early; (2) a task
pushed by hand before 3a (no `action_item_id`) was duplicated by the push,
so add a title-level dedup on push. Gotcha hit on launch: the single-
instance plugin makes the dev app exit silently (exit 0, no log) while the
installed Adversaria.app runs under the SAME user; an instance under the
`test` QA user does not block it.

**Delegation 4 (same evening, after the founder's first-run feedback):**
in-app artifact preview (`src/lib/markdown.ts` escape-first renderer +
`ArtifactPreview.tsx`; `read_workspace_artifact` is sandboxed to
`config::workspaces_root()`, 2 MiB cap; `reveal_workspace_artifact` = Finder
reveal) — the first artifact of every review card opens expanded, "Open in
default app" is secondary (the founder's `.md` handler is Antigravity and
fails); routing moved OFF the meeting page: the binding banner now lives on
the to-do board when scoped to a meeting, plus a "Route this meeting's
to-dos…" item in each to-do's ⋯ menu (founder: "move it to the workspace from
to-dos, not from the meeting itself"); **the meeting graph now feeds every
run**: `hybrid_rank` over all meetings (task title + source summary) → top 3
related, summaries only, under "# Related meetings (from your meeting graph)"
in the brief (`workspace_runs::select_related_meetings`), and a persisted
first log line `Context: N bound · M related via graph (titles) · K folders`
shown on the review card (`context_receipt`). Gates after it: cargo 256 ·
clippy · fmt · tsc · vitest 173.

**Delegation 5 (CSS only, `src/prototype.css`):** founder screenshots showed
titles running under badges/off the card, the preview spilling under the
Context pane, the pause bar folding, and marker-less preview lists. Cause:
column-flex `.ws-list-main` with `align-items:flex-start` (no width
constraint) + grid children with `min-width:auto` + an app-level
`list-style:none`. Fixed with `min-width:0`/`max-width:100%` on card
children, wrapping task titles, `nowrap` on the pause-bar chip/button, and
explicit `list-style` in `.md`. Hot-reloaded into the running app.
Finding: related-meeting relevance needs a floor (see TODO 🔴).

**Delegation 6 (3b-1, Rust + Python):** related meetings now come from the
to-do's own text with a floor: `embeddings::related_meetings_for_text`
(FTS hits first, then chunk-embedding cosine ≥ 0.55, 0–3 results) and the
receipt labels each one `[text match]` or `[0.71]`. The `local` engine has
its own path: `POST /draft_stream` (`DraftRequest`, `DRAFT_SYSTEM_PROMPT`,
`OllamaSummarizer.draft_stream`) instead of the meeting-chat prompt that
made it refuse to draft, and its brief caps transcripts at 4k chars
(`compose_task_brief(..., transcript_limit)`). Gates: cargo 259 · pytest
175 (+1 foreign failure, below) · vitest 175.
⚠️ **`uv run pytest` / `.venv/bin/pytest` / `.venv/bin/ruff` HANG on this
machine** (console-script launchers); `python-service/.venv/bin/python -m
pytest` runs the suite in 0.5 s. Use that form.

**Delegation 7 (3b-2, skills & agents):** `addons.rs` built-in catalog (skills:
deep-research, drawio-diagram, architecture-doc, meeting-grounded-writing,
marketing-copy, slides-deck; agents: researcher, diagrammer, tech-writer,
reviewer) seeded/upserted at init into `workspace_addons`; attachments in
`workspace_addon_links` (one agent per workspace, any skills; custom skills
via `create_workspace_addon`). Every run injects `# Agent` / `# Skills`
into the brief; Claude Code also gets `.claude/skills/<slug>/SKILL.md` +
`CLAUDE.md`, Codex gets `AGENTS.md` in the run dir
(`workspace_runs::write_native_addon_files`). UI: `WorkspaceAddons.tsx` in
the Context pane (agent radiogroup, skill chips, Add custom skill…);
`.drawio` artifacts get "Open in draw.io". Gates: cargo 271 · vitest 181.

**Brainstorm boards (not built):** Meetings as Projects https://claude.ai/code/artifact/b69dacc7-dafb-4eca-90c0-a10895cf9e74 and Share sheet &
connections https://claude.ai/code/artifact/16583952-cf7f-4ee9-8fb3-8341de9ad52b. Both in the TODO top block with their decisions.

**Delegation 8 (3b-3, context engine):** `context_index.rs` indexes the
Obsidian vault (`*.md`, skipping `.obsidian`/`graphify-out`/files with the
app's own `resource: adversaria://meeting/` marker) and one card per repo
under the projects root (README/CLAUDE.md head + package/Cargo name) into
`context_docs` + `context_chunks` + `context_fts`; sync 40 s after launch,
every 30 min, and via `reindex_context_sources`. Every run searches the
to-do text (FTS first, cosine ≥ 0.55) → top 5 vault notes as excerpts +
top 2 project folders attached read-only (`--add-dir` for Claude Code,
listed for Codex); brief sections `# From your vault` / `# Matching
projects`; receipt gains vault/projects segments. Settings → Integrations
→ "Workspace context sources" (two folder pickers, Reindex now, counts).
`AppConfig.context_vault_path` / `context_projects_root`; founder's
config.json set on 08-22 to `…/MyProjects/laghari-vault` and
`…/MyProjects`. ⚠️ The default falls back to `second_brain_path`, which is
wrong when that points at a vault SUBfolder (the meeting export dir is
skipped by the marker) — set the vault root explicitly. Gates: cargo 278 ·
vitest 183.

**Delegation 9 (3b-4, 08-23 morning; interrupted once and RESUMED in the same
Codex session via `stunt resume <id>` after the process died mid-edit):**
`task_triage::needs_you` (deterministic verb/phrase rules) sets
`workspace_tasks.agent_eligible` at push time; `next_queued_task` skips
ineligible tasks so the autopilot never runs "record the demo"-type to-dos;
`set_workspace_task_agent_eligible` + UI ("needs you" badge, "Let an agent
try" / "Mark as needs me"), card "· n need you". Push now links an existing
same-title task instead of duplicating it. `context_docs.name` (file stem /
folder name) is indexed: `context_fts` rebuilt with a `name` column so
`MIQ-Agentic.md` is found by "MIQ". Gates: cargo 283 · vitest 184.
Gotcha: a Codex worker can die silently mid-task (empty result JSON, exit 1);
check `~/.codex/sessions/<date>/` for the rollout id and `stunt resume` it
with the compile errors pasted in — it continues from its own partial edits.

**Claude's own one-liner (08-23):** `search_context_doc_ids_on` now orders by
`bm25(context_fts, 10.0, 10.0, 1.0)` (title and file name ×10) so a short to-do
like "MIQ" ranks `M|Q Agentic Intelligence` / `MIQ-Agentic` first instead of
5th; meetings FTS unchanged. Gotcha learned the hard way: editing anything
under `src-tauri/` while `npm run tauri dev` is up triggers a rebuild +
restart that kills in-flight runs (they are re-queued by the orphan
recovery, which was thereby live-tested).

**Delegation 10 (3b-5, 08-23):** the local engine now writes real files:
`local_output::split_output` parses `=== FILE: name.ext ===` blocks and the
lenient "path line + fenced block" shape the model produced live; each file
is written to the run dir, `draft.md` only for leftover prose, artifacts
registered by scanning the dir (`Wrote N file(s): …` in the run log).
`LOCAL_WORKSPACE_INSTRUCTION` and the Draw.io / Slides skills teach the
convention. Both retrieval embed calls are wrapped in an 8 s
`tokio::time::timeout` with FTS fallback (`[retrieval] embed skipped`).
Gates: cargo 292 · vitest 184. Also (Claude, CSS): task-row titles keep a
220 px minimum and the action cluster wraps under them (the founder saw
one-character-per-line titles caused by `overflow-wrap: anywhere` in a
squeezed column). First live local Diagrammer run (run 12): correct
`<mxfile>` with 6 vertices / 5 edges in 23 s, saved as draft.md before
this fix; Claude extracted `adversaria.drawio` by hand into run-12/.
**Live-verified after the fix (run 13, local model, Diagrammer + Draw.io):**
`Wrote 2 file(s): adversaria.drawio, adversaria.md` — well-formed `<mxfile>`
(5 vertices / 5 edges) plus the legend, no draft.md.

**🔁 OPEN DECISION (08-23 14:15, founder-proposed): drop Rapid-MLX, keep Ollama only.**
Premise verified: Ollama ≥ 0.19 (Mar 2026, "preview") runs MLX on Apple Silicon,
but ONLY on Macs with > 32 GB unified memory (smaller Macs stay on llama.cpp/
Metal); the library has MLX tags for our models (`qwen3.6:35b-a3b-nvfp4` 24 GB,
`qwen3.6:27b-mlx` 20 GB, `qwen3.6:27b-nvfp4` 19 GB). Founder's Ollama 0.32.7 is
currently running GGUF tags on Metal, not MLX. Proposed shape if we go: a
**managed Ollama sidecar** (bundle the MIT `ollama` binary + its ggml/mlx libs,
loopback port, `OLLAMA_MODELS` in app data) replacing BOTH the pinned Rapid-MLX
runtime (`python-service/rapid-runtime/`, `setup.rs` managed start, DMG signing
of that tree) and the Windows managed llama.cpp engine (`llama_engine.rs`); one
pull API with progress for chat AND embedding models (bge-m3 becomes trivial).
Costs: no MLX below 32 GB; lose Rapid-MLX's explicit disk-cache privacy flags
(Ollama keeps KV in RAM only — state it in PRIVACY_NETWORK_BOUNDARIES);
lose `served-model-name`/`chat_template_kwargs` control. Measured so far: the
brew Rapid-MLX on :8000 did **12.8 tok/s** on qwen3.6-35B and ignored
`max_tokens` (poor for an M5 Max). Ollama could NOT be measured: the syspolicyd
stall blocked its runner. **Decide with numbers after the reboot:**

```bash
# 1. Rapid-MLX (whatever is serving on :8000)
P='Write a 150-word summary of why local-first meeting notes matter for privacy. Plain prose, no headings.'
time curl -s http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' \
  -d "{\"model\":\"qwen3.6-35b\",\"messages\":[{\"role\":\"user\",\"content\":\"$P\"}],\"max_tokens\":220,\"temperature\":0,\"chat_template_kwargs\":{\"enable_thinking\":false}}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['usage'])"
# 2. Ollama on MLX (pull once: ~24 GB)
ollama pull qwen3.6:35b-a3b-nvfp4
curl -s http://127.0.0.1:11434/api/generate -d "{\"model\":\"qwen3.6:35b-a3b-nvfp4\",\"prompt\":\"$P\",\"stream\":false,\"think\":false,\"options\":{\"num_predict\":220,\"temperature\":0}}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('eval tok/s', round(d['eval_count']/(d['eval_duration']/1e9),1), '| prompt tok/s', round(d['prompt_eval_count']/(d['prompt_eval_duration']/1e9),1), '| load s', round(d['load_duration']/1e9,1))"
# (also run the GGUF tag qwen3.6:35b-a3b the same way to see the Metal fallback the <32 GB Macs would get)
```
If Ollama-MLX ≥ Rapid-MLX on tok/s and time-to-first-token: write **ADR-016**
("managed Ollama replaces Rapid-MLX + Windows llama.cpp"), then spec the
removal + sidecar as a Codex delegation (big: setup.rs, rapid-runtime, build-dmg,
llama_engine.rs, model_setup pins, onboarding copy, tests). If not: keep
Rapid-MLX, and finish the bge-m3 auto-download via `rapid-mlx[embeddings]` +
`--embedding-model mlx-community/bge-m3-mlx-fp16` (validated that the repo
exists and bge-m3 is XLM-RoBERTa, which mlx-embeddings supports; the local
load test could not complete because of the stall). Either way the Ollama
embedder path stays for Windows.
Dev-env note: `python-service/rapid-runtime/.venv` has `mlx-embeddings 0.1.0`
installed ad hoc for the test (bumped transformers 5.12.1→5.15.1 there);
`uv sync --frozen` in that dir restores the lock. The pinned bundle is untouched.

**✅ Rebooted 08-23 ~15:15; stall gone. A/B measured: Rapid-MLX ≈102 tok/s,
Ollama/Metal 98.5 tok/s (qwen3.6-35B), `qwen3.5:4b` 106–108 tok/s (Ollama
defaulted it to a 262k ctx = 12 GB → sidecar must always pass `num_ctx`),
Ollama-MLX engine confirmed on `muse-glimmer:30b-mlx` (30B dense, 32–36 tok/s);
`qwen3.6:35b-a3b-nvfp4` on Ollama-MLX: **128 tok/s warm, 88 cold, 2.6 s load**
(pull took 72 min). Numbers are in ADR-016. **ADR-016 ACCEPTED by the founder** (one engine: managed
Ollama sidecar; Rapid-MLX + Windows llama.cpp to be removed). **Delegation 11
(ADR-016 step A, additive) running on Codex:** `ollama_engine.rs` sidecar on
port 27434 with its own models dir, `ollama-tier:light|mid|high` profiles
(qwen3.5:4b / qwen3.5:9b / qwen3.6:27b, `-mlx`/`-nvfp4` on >32 GB Macs with
Ollama ≥ 0.19), pulls with progress through the existing setup UI, `bge-m3`
pulled after the chat model, service routes any loopback Ollama host
natively (`POST /setup/llm_host`), `/health` gains `embedder_state`, Setup
status gets a "Semantic search" row. Step B = removal (rapid-runtime,
setup.rs branches, llama_engine.rs, build-dmg, tauri.conf resources, tests,
docs); step C = bundle the `ollama` binary for macOS + Windows (signing,
size, LICENSE).

**(superseded) ⏸ Founder is rebooting now (08-23 ~14:20).** After reboot, relaunch in this
order: `cd python-service && HF_HUB_DISABLE_XET=1 uv run --no-sync uvicorn
src.server:app --host 127.0.0.1 --port 9876 --log-level info` → Ollama.app (for
embeddings) → `npm run tauri dev` (quit any installed Adversaria.app under the
same user first). Then the A/B above.

**⚠️ Foreign changes in the same working tree (NOT from this session):**
`python-service/prompts/*.md`, `python-service/src/summarizer.py`,
`python-service/tests/test_summarizer.py` were modified 17:42–17:47 local on
08-22 by something else (another Claude/Codex session of the founder's on
this machine; `fcc-claude` workers from other sessions were running). They
are summarizer work (prompt rewrites, a "From Your Notes" fallback for 4B
models). Left untouched and NOT verified here. Commit the Workspaces files by
explicit path; do not `git add -A`.

**⚠️ Gotchas for the next session:**
- **Codex delegations need Claude Code Router running** (`ccr start`; it serves
  `127.0.0.1:3456`, Codex's `model_provider = "claude-code-router"`). After
  a reboot it is NOT auto-started: `stunt exec` returns `is_error: true` with
  zero tokens and `codex exec` says "stream disconnected … 127.0.0.1:3456".
  `ccr start` brings the router back but the `default-claude-code` profile
  does not know Codex's `gpt-5.6-sol` model ("All target providers failed").
  **Working bypass:** `codex exec --json --skip-git-repo-check -s workspace-write
  -c model_provider=openai "$(cat spec.md)"` uses the native ChatGPT login
  (default model OK; `-m gpt-5.5` OK; `gpt-5.5-codex` is refused on ChatGPT
  auth). Resume with `codex exec resume <thread_id>`; the thread id is the
  `thread.started` event in the JSONL.
- **`codex exec` hangs forever in a background shell unless stdin is closed**
  (08-23: two runs, one for 7 h 23 min — 0 % CPU, no TCP connection, no
  events, no file edits; it was blocked reading "additional input from
  stdin"). Always launch as `codex exec … < /dev/null` AND wrap in a hard
  limit (`perl -e 'alarm 2700; exec @ARGV' codex exec …`). Liveness check:
  the `--json` events file grows within the first minute; `find src -mmin
  -10` shows edits after ~5–10 min.
- **08-23: every newly launched app/binary hung (draw.io, Ollama runner, ruff,
  `uv run pytest`).** Cause: `syspolicyd` leaking file descriptors; `sudo
  killall -9 syspolicyd amfid` helped for ~2.5 h, then it recurred → **reboot
  the Mac**, then relaunch: Python service → `npm run tauri dev`. Write-up in
  LESSONS_LEARNED (2026-08-23).
- **Autopilot is always on.** The next `npm run tauri dev` will start every
  queued task in every workspace on its engine (Claude Code / Codex are
  cloud-backed) 15 s after launch. Open Workspaces → "Pause all agents" first if
  that is not wanted, or set `"agents_paused": true` in config.json.
- The dev DB's `workspace_tasks` table is rebuilt on first launch; a task that
  was `done` stays `done` (it is not re-opened for review).
- Manual Run now refuses while another task runs in the same workspace.

**Next:** (1) founder decides the Projects-board Agents switch → spec Projects
slice 1 for Codex; (2) ✅ done (delegation 9); (3) Share sheet (Slack webhook → Notion)
once the founder answers the board's questions; (4) 3c Grok + "Get 2 takes".
Relaunch order after a restart: Python service (`uv run --no-sync uvicorn …`)
then `npm run tauri dev`; quit any installed Adversaria.app under the SAME
user first (single-instance).

## Current session (2026-08-05) — Windows false failure + sidecar recovery

**Uncommitted working tree.** Hamza reported two distinct Windows failures.

1. **Working self-hosted transcription still said model download failed.** The
   status hook and setup strip held stale local Whisper state and did not learn
   about a Settings config save. Worse, `whisper-main`, `whisper-live`, and the
   Windows picker profile can name the exact same immutable CT2 snapshot, but a
   successful alias did not clear a failed sibling. Fixed in
   `useTranscriptionSetup.ts`, `SetupStatusStrip.tsx`, `tauri.ts`, and
   `model_setup.py`: successful config writes notify long-lived UI, configured
   remote transcription ignores local model state, health `ready` outranks a
   stale alias, and equivalent aliases settle ready atomically. Regression tests
   cover ready-over-error, a live switch to self-hosted, strip dismissal, and
   equivalent-profile completion.
2. **Friend's Windows install shows Local AI Offline / service unreachable.**
   The actual published 0.3.72 NSIS installer was downloaded and inspected. It
   contains `adversaria-service/adversaria-service.exe` (13,876,350 B), 748
   support files, and ~480,509,923 B of installed sidecar payload. This rules
   out an omitted bundle. Leading causes are antivirus/EDR quarantine/blocking
   (the development Windows box already recorded SentinelOne `Access is denied`)
   or an immediate frozen-process crash. The old build hid both: spawn errors
   went only to stderr, missing exe returned silently, the watchdog eventually
   gave up, and “check again” only polled health.

**Implemented:** launch/missing/retry-exhausted failures are persisted to
`adversaria-service.log` and returned as safe actionable UI messages; offline
chrome and Settings call a real `restart_local_ai_service` command; a single
atomic watchdog owner prevents manual/automatic restart races; generic service-
down copy now points to Restart. Windows CI launches the exact frozen PyInstaller
exe on a free port and requires `/health` before Tauri packages it.

**Verified:** vitest **111/111**; pytest **380 passed / 1 skipped**; Rust
**198 passed / 1 ignored**; TypeScript, Ruff, cargo fmt, clippy `-D warnings`,
workflow YAML parse, and `git diff --check` clean. The focused Settings recovery
test is included in that frontend total.

**Next:** build/release on Windows so CI executes the new frozen-sidecar smoke;
on the affected 0.3.72 PC check Windows Security → Protection history (or the
company EDR) for `adversaria-service.exe`, allow/restore it, reinstall if it was
removed, fully Exit the tray app, and reopen. If no security event exists,
collect `%APPDATA%\meeting-note-taker\logs\adversaria-service.log`. Do not claim
the exact machine-level cause until that evidence arrives.

## Previous session (2026-08-02 → 08-04) — SHIPPED 0.3.71 + 0.3.72, both platforms

**Everything below is committed, pushed (`master`), publicly synced, and
RELEASED.** Working tree clean. Two releases went out; **0.3.72 is the first
release in this project's history where macOS and Windows ship together and both
can auto-update.**

### How this started
Hamza's machine was slow and permanently hot, and Adversaria was mis-transcribing
its own name. That diagnosis cascaded into everything else.

### Shipped (all verified by gates + adversarial review)

**Robustness (08-02)**
- **Poll storm:** `SetupStatusStrip` polled 8 model-download endpoints every 4 s
  FOREVER after onboarding — 35,400 of 36,681 sidecar-log lines (96%) in 13 h, on
  every install. Replaced with a download-start event bus (`modelDownloads.ts`,
  pings at start AND on settle so a poll can't race the start command); strip
  idles at 60 s; uvicorn access-log filter; sidecar log rotates at 5 MB.
- **Sidecar leaks:** orphans (~1.6 GB each) were never reaped. Startup reaper
  (name + dead-parent, pure fn + tests, live-verified) plus a stdin parent-death
  guard so the sidecar dies with the app even on force-quit.
- **16 GB Ollama runner:** local Ollama tags route through the OpenAI-compat
  `/v1`, which CANNOT carry `num_ctx`, so qwen3.5:9b loaded at its 262,144
  default. The summarizer now serves loopback `:11434` with the native client.
  **This was the cause of Hamza's "notes never generated" timeout (meeting 221).**
- **"Adversaria" → "Adverse Area":** deterministic vocabulary correction pass
  (exact-over-fuzzy at every window size, possessive-aware, lowercase entries
  impose nothing).

**Onboarding + updater (08-03)**
- Wizard rebuilt: model picker with real sizes, ONE explicit Download click, live
  progress, honest failure. **Nothing auto-downloads — encoded in tests.**
- Updater re-checks every 6 h instead of launch-only.

**Transcription BYOK (08-03)** — three engines (On-device / Self-hosted / Cloud)
via `transcription_provider` + tested URL migration, so Hamza's office DGX is
first-class. **Privacy copy is gated on the ACTUAL host, never the chosen label**
— pick self-hosted with a public URL and you get a warning, not a false promise.

**Templates (08-03/04)** — display names (slug stays the API key); `general.md`
TL;DR + due dates (needed `meeting_date` threaded Rust→Python; the summarizer had
no date context at all); new `brain-dump.md` for the morning ritual.

**STALE PROMPTS — the biggest real-world win.** The packaged app ran a
`general.md` frozen at 2026-06-20 (2,563 B vs 6,353) because seeding only copied
a MISSING template. Ownership is now explicit (`prompts/_user_templates.json`,
claimed on save/delete); unclaimed templates are refreshed; an unclaimed file
that differs is backed up to `<name>.bak-<stamp>.md` first. **Verified live after
0.3.72: general.md is now 6,353 B with `general.bak-20260804-072216.md` beside
it, and brain-dump.md landed.** Deleting a template now sticks too.

**Mic bleed (08-04).** Meeting 221 was ONE voice bleeding from the speakers but
reached the summarizer as a two-person meeting — 20/20 mic segments were
duplicates. `strip_mic_bleed` compared each mic segment against INDIVIDUAL system
segments, but the channels are transcribed independently so Whisper chunks them
at different boundaries: every mic line was the tail of one system segment plus
the head of the next, scoring 0.14-0.57 against any single one while being 100%
contained in the channel. Added a boundary-independent pass over the joined
window, using BIGRAMS (same-subject speech reuses vocabulary but not word order).
Calibrated on the real transcript: bleed 0.87-1.00, genuine same-topic speech
0.12-0.38 → threshold 0.70. Replaying the real recording strips 20/20.

**Windows auto-update — WORKS FOR THE FIRST TIME.** Three causes, two were repo
bugs: the manifest was macOS-only, and CI collected `*.nsis.zip` artifacts that
`createUpdaterArtifacts: true` never produces (it re-uses the NSIS installer, so
the pair is `-setup.exe` + `-setup.exe.sig`), so the signature was never
uploaded. **CORRECTION: the third "cause" was wrong — `TAURI_SIGNING_PRIVATE_KEY`
was ALREADY in the public repo's secrets.** That was inferred from a workflow
comment instead of checking a real run; the CI log shows `***` and a `.sig` is
produced. Always verify the signature's key id against the pubkey pinned in
`tauri.conf.json` before publishing (`e1b42bed5b7d787f`) — a mismatch fails
silently on every user's machine.

**Public sync hygiene.** A sync staged 357 files / 149,305 insertions because an
installer had written ~3.2 MB of AI-skill tooling into THREE places
(`.agents/`, `.claude/skills/`, `.github/skills/`). Excluded (scoped to
`.github/skills/`, NOT all of `.github/` — the workflows there build both
platforms). Result: 51 files / 4,178 insertions.

**Dependencies.** `npm audit` 5 high → 0, all devDependencies (none ship in the
app; exposure was the build machine). GitHub's banner went 6 → 5, confirming it
is real but shows things the local audit cannot see.

### Releases
- **0.3.71** (macOS only) — notarized Accepted + stapled.
- **0.3.72** (macOS + Windows) — notarized Accepted + stapled; manifest carries
  `darwin-aarch64` AND `windows-x86_64`, both signed, both URLs 200.

### Model choice (evidence, 2026-08-04)
Bake-off on a real transcript, judged blind by 3 agents: **qwen3.6:35b (MoE) beat
qwen3.5:9b 2-1** AND is ~2x faster (73 vs 39 tok/s, 8 s vs 96 s load) because
only ~3B params activate per token. Costs 23 GB resident vs ~7 GB. The 9B
produced the only outright fabrication (merged two sentences into a composite
claim). Both got attendees wrong — that was the mic-bleed bug, since fixed.

### OPEN — next session starts here
1. **Windows "download failed — interrupted" banner that will not clear**
   (reported 08-04, on Hamza's friend's machine; transcription works fine).
   Verified in code: `_STATES` is IN-MEMORY only and nothing auto-starts a
   download, so it CANNOT survive a real restart — suspect the app was never
   fully quit (system tray keeps it alive). Hypothesis: `whisper-live` (live
   captions) failed while the main model succeeded. **Need the profile id from
   `%APPDATA%\meeting-note-taker\logs\adversaria-service.log`** (search
   `interrupted` / `whisper-live`) before fixing.
2. **No force re-download** — `start_model_download` early-returns on a `ready`
   profile, so a corrupt-but-cached model cannot be re-fetched from the UI. This
   is likely what makes a stuck download feel permanent. Needs a `force`/reset
   path in `model_setup.py`.
3. **"My todo template is not there"** (08-04). It IS installed and served
   (`/templates` returns `brain-dump`); it displays as **"Brain dump"**, and the
   "New Note" button has a SEPARATE scaffold list (Blank / Meeting prep / Daily
   standup / Idea dump) that does not include prompt templates. Awaiting Hamza's
   confirmation of which picker he meant.
4. **Fresh-account QA never ran.** The wizard rework only manifests on a machine
   that has never run Adversaria. Hamza's friend installing 0.3.72 is the closest
   thing to that test — ask what they saw.
5. Guided tour still suspends when transcription fails (product call);
   sovereignty pill counts any remote endpoint as "not local" (product call);
   relative deadlines have no lower bound in `general.md` (unverified).

### Machine hygiene (recurring, non-code)
A Playwright-MCP Chrome renderer ran away for **2 days 11 hours / ~40 h CPU**,
which is what made the laptop hot and caused the meeting-221 notes timeout
(`kernel_task` was at 40% shedding heat, swap 98% full). Killed. Also killed a
duplicate 38 GB rapid-mlx server. If the fans roar, check `top -o cpu` for
runaway helpers BEFORE suspecting Adversaria — it was idle at 0.0% throughout.

> ℹ️ **Everything in the dated sections below that says "UNCOMMITTED" or
> "awaiting Hamza" WAS subsequently committed and shipped in 0.3.71/0.3.72
> (2026-08-04). The labels are preserved as the historical record of how the
> work progressed; trust the current-session block above for present state.**

## Previous session (2026-08-03 — onboarding + updater + transcription BYOK; COMMITTED + PUSHED as master/0198bff)

Three changesets now sit uncommitted together (08-02 robustness + today's two).
**Nothing is committed.** 27 files modified, 4 new test files. Gates after every
repair: **tsc clean · vitest 97 · cargo 190 + clippy + fmt · pytest 357 + 1
skipped**.

**Trigger:** Hamza's friend on Windows finished setup and got "No transcription
model is downloaded yet" instead of notes — because the old wizard made
*skipping* the download the primary button and the download a Settings detour.

1. **Wizard rebuilt** (`Welcome.tsx`): model picker with real sizes, ONE
   explicit "Download (size)" click, live progress, honest failure. Founder rule
   preserved and tested — nothing downloads without a click.
2. **Updater** re-checks every 6 h (`UpdatePrompt.tsx`) instead of launch-only.
   **But Windows auto-update has NEVER worked** — see the 🔴 blocked TODO item;
   it needs Hamza to add the signing secret himself.
3. **Transcription BYOK first-class**: three engines (On-device / Self-hosted /
   Cloud) + `transcription_provider` config field with a tested URL migration,
   and a wizard "use your own endpoint" path. Hamza's office DGX is now a
   first-class, correctly-labelled setup rather than a scary "not sovereign"
   cloud option.

**Two adversarial review rounds found 10 confirmed defects — all fixed.** The
worst were repeats of the same churn moment: the wizard could print
"Transcription ready ✓" on a machine whose engine couldn't load the model
(readiness ORed "weights on disk" over the service's error state), its failure
branch was a dead end (a retry that retried nothing, with the picker hidden),
and the self-hosted panel could claim "never to a third party" while still
uploading to Groq. Two agents ran out of credits mid-run; their partial work was
verified and finished by hand (the App→Welcome poller prop, and a stale test).

**Key invariants now encoded in tests — do not regress:**
- No download ever starts without an explicit click.
- Privacy copy is gated on the **actual host**, never the chosen label.
- The transcription API key is cleared on every engine switch.
- The wizard never claims "ready" for an endpoint it hasn't reached.
- The wizard reads App's single `useTranscriptionSetup()` — never mounts a second.

**Next step:** Hamza reviews → authorizes commit → 0.3.71 → fresh-machine QA on
a clean macOS account and a fresh Windows VM (that ritual is what these fixes
exist for). Then the Windows updater unblock.

## Previous session (2026-08-02 — the 4 robustness bugs FIXED, reviewed, gates green; UNCOMMITTED)

All four 2026-08-02 TODO items were implemented the same day (4 parallel
agents + adversarial review + inline repairs), on top of the morning's
diagnosis below. **Nothing is committed — waiting on Hamza.** Change set:
17 files (see `git status`; the two new test files are untracked on purpose).

- **Poll storm** (ships to every install): download-start event bus in
  `src/lib/modelDownloads.ts` — `beginModelDownload` pings at start AND on
  settle (a start-command race would otherwise park pollers on the heartbeat);
  `SetupStatusStrip` idles at 60 s, `useTranscriptionSetup` fast-polls only
  in-flight; uvicorn access-log filter (server.py) drops 2xx poll records;
  sidecar log rotates to `.old` at 5 MB (commands.rs).
- **Sidecar lifecycle**: startup reaper (`commands.rs`, sysinfo 0.39.6 —
  name match + dead parent, pure fn + tests, live-verified on a real orphan)
  and parent-death guard: Rust pipes stdin + sets `ADVERSARIA_PARENT_GUARD=1`;
  server.py hard-exits on stdin EOF only under that env var. **Contract: never
  set the env var without a piped stdin or the sidecar dies at startup.**
- **num_ctx / 16 GB runner — real root cause**: `commands.rs:1989` routes
  local Ollama tags via the OpenAI-compat `/v1` (no num_ctx possible). The
  summarizer now reroutes loopback-`:11434` base_urls to the native client
  (`_is_local_ollama_url`, lazy `_ollama_client()`, chat + stream) where
  `_ollama_options()` guarantees `num_ctx=16384` (env `OLLAMA_NUM_CTX`).
- **Vocab correction**: `apply_vocabulary_corrections` in transcriber.py —
  exact-over-fuzzy at every window size, possessive-aware, lowercase entries
  impose no casing; wired after `strip_glossary_echo` on both channels at both
  dual call sites. Review caught word-swallowing + casing-downgrade in the
  first cut; both repaired with regression tests.

**Gates (2026-08-02, final):** pytest 357 passed + 1 skipped · cargo check +
clippy -D warnings + fmt + 180 tests · tsc clean · vitest 57. Deferred:
Windows llama-server orphan reap (sysinfo `with_exe` + engine-dir path match —
compile-check needs a Windows box).

**Next step:** Hamza reviews + authorizes commit; then release as 0.3.71 and
run the fresh-machine QA ritual (the poll-storm and lifecycle fixes are
exactly what a fresh-install soak test exercises). Hamza should also
capitalize "Adversaria" in Settings → Custom vocabulary (quick win; the
post-pass now protects lowercase entries either way).

## Previous session (2026-08-02 morning — Hamza's slow/hot machine diagnosed; 4 bugs filed)

Hamza reported his personal Adversaria slow, "Adversaria" mis-transcribed, and
the laptop hot with memory maxed. Diagnosis (all verified live, no code changed):
the machine had ~95 GB of resident model servers (swap 98% full) — biggest hogs
were **non-Adversaria** (two duplicate qwen3.6-35b rapid-mlx servers, 57 GB,
idle since 07-14). Adversaria's share: sidecar 6.5 GB (normal), **Ollama runner
at 16 GB** (qwen3.5:9b loaded at model-default 262,144 ctx — some client omitted
`num_ctx`), and **4 orphaned dev sidecars ~1.6 GB each**. Also found the
**SetupStatusStrip idle poll storm** — 8 model-download endpoints every 4 s
forever, 96% of the sidecar log — which **ships to every 0.3.70 user**, and the
"Adverse Area" mis-transcription (meetings 217–219; vocab was lowercase +
list-final so the initial_prompt bias is weak).
**Done:** local cleanup (orphans, stale dev uvicorn on 9876, unused 38 GB
rapid-mlx :8000, Ollama runner unloaded — ~60 GB freed); four TODO.md entries
filed under **2026-08-02** with fix directions.
**Next step:** fix the poll-storm bug first (user-facing battery/log cost on
every install), then sidecar reaping; Hamza should capitalize "Adversaria" in
Settings → Custom vocabulary as the quick transcription win.

## Session (2026-07-31→08-01 — Setup V3 SHIPPED as 0.3.70, both platforms)

**🚢 0.3.70 IS LIVE (2026-08-01):** notarized DMG (Accepted + stapled) and the
Windows x64 installer, both on adversaria-releases v0.3.70 (Latest) with the
signed updater manifest — installed apps update themselves. The MCP 0.2.0 ↔ app
schema gap is CLOSED (0.3.70 carries the action_items migration). Public repo
synced via PR #12 (macOS+Windows CI green). Windows exe built by public CI run
30698271578; macOS built locally via the canonical release command (one hiccup:
the venv's mlx install was corrupted by an earlier resync — `uv pip install
--reinstall mlx mlx-metal mlx-whisper` healed it; watch for this after any
`uv sync`). Hub71 application SUBMITTED the same day (see STRATEGY_HANDOFF).
**Website SHIPPED same day:** lagharilabs.com/adversaria updated live
(wrangler direct-upload — remember `git push` does NOT deploy that repo):
Windows download button ×2 (direct stable URLs + SmartScreen note), waitlist
forms retired, MIT → Elastic 2.0 everywhere, NEW agents section with
`uvx adversaria-mcp` (Connect/Delegate/Approve), FAQ updated for both
platforms + guided setup. Verified on production; source committed+pushed.
**Redesign explorations:** (a) arcade-brand product page REJECTED — decision
memorized (`adversaria-brand-separation`): arcade = company brand, product
keeps its dark identity; (b) Anytype-direction preview
(scratchpad `adversaria-landing-anytype.html`) iterated to screen-perfect —
viewport-locked sections, automated fit audit (ALL FIT @1280/1440/1512),
impeccable craft-floor pass (eyebrows deleted, contrast fixed, one authored
motion moment) — **verdict pending ("okay, not better" on v1)**; NOT deployed.
**Design skills INSTALLED into this repo's `.claude/skills/`:**
`impeccable` (v4 — run its context.mjs per its SKILL.md; hooks active) and the
taste-skill family (design-taste-frontend, high-end-visual-design, …) — load
them for any future frontend/design work. **⚠️ Gotcha: the taste-skill
installer RAN A REDESIGN uninvited** — it rewrote the protected
`landing/index.html` (reverted) and dumped preview pages + stock images into
`landing/` and `design-artifacts/` (deleted). After any `npx skills add`,
check `git status` for droppings before committing.
**LANDING REPLACED (2026-08-02, Hamza's own design):** he built
"Meetings become memory" in `design-artifacts/adversaria-landing-concepts/`
(real app screenshots + compressed screen-capture videos) — audited (claims
clean, all assets resolve, no overflow), deployed to production with two
functional additions only (canonical+OG meta, SmartScreen line), verified
live, committed in the site repo (`43d4b33`). This supersedes both my
rejected redesign explorations. The concept source stays in his
`design-artifacts/` working dir (untracked, deliberately).
Still open: V3 QA ritual passes (fresh macOS account + fresh Win VM,
throttled/HF-blocked) · dependabot clean (0 open).

**Trigger:** a friend's fresh Windows 0.3.68 install failed with
`Transcription failed: {"detail":"Transcriber not initialized"}`. Root cause
(traced + live-reproduced): the whisper model was never part of setup on
Windows — faster-whisper downloaded ~3 GB *synchronously inside the service
lifespan* (port unbound throughout, process death on failure, no re-init path,
raw JSON to the UI). The wizard's V2 "background cache" kick was a silent no-op
(fired while the port was unbound, `.catch(() => {})`). Full brainstorm:
https://claude.ai/code/artifact/cd5a553f-7c04-41c8-bb68-37c911d1e886

**Decisions (Hamza):** nothing downloads automatically — the app *guides* the
user to download what they need; degrade-but-honest (never gate setup); Windows
default whisper → **large-v3-turbo** (`deepdml/faster-whisper-large-v3-turbo-ct2`).
Spec: **V3 addendum at the bottom of `docs/SETUP_REDESIGN_SPEC.md`** (supersedes
V2's whisper-during-setup rule). Phase B (tour v2 + seeded demo meeting) queued
behind this.

**State of the working tree (ALL UNCOMMITTED):**
- ✅ **Package A (Python) DONE, 321 tests green.** Service starts model-less in
  seconds; `transcriber_state` (loading/ready/missing/error) in `/health`;
  structured 503 `{"detail":{"code":"transcriber_missing"|…}}`; self-heals on
  download completion (`model_setup.on_download_ready` → re-init) and on demand;
  BYOK cloud transcription no longer blocked by a missing local model; MLX
  sneak-downloads gated; manifest guard now accepts `model.bin` (every CT2
  whisper download used to fail "no weight files"); per-model pins
  `whisper-model:<key>`; CT2 default → turbo. Live-verified: empty cache +
  offline → service serves and answers honestly (used to die).
- ✅ **Package B (Rust) DONE, cargo 169 tests green** (agent-built; structured
  report pending): `HF_HUB_DISABLE_XET=1` on ALL platforms; sidecar
  stdout/stderr → `<app_data>/logs/adversaria-service.log`; watchdog respawn
  with backoff + `shutting_down: AtomicBool` (set by `shutdown_sidecar`);
  transcript persists BEFORE summarize (no-engine meetings keep transcripts);
  retroactive drains (`meetings_awaiting_transcription`,
  `meetings_missing_summary`) — pending meetings transcribe/summarize
  themselves when a model/engine appears; error-translation layer in
  http_client.rs (raw JSON/jargon never reaches the UI); Windows fresh-config
  whisper default → turbo.
- ✅ **Package C (React) DONE, vitest 50 + tsc green:** wizard guides to
  Settings instead of auto-downloading (guide card quotes THIS machine's model
  size); persistent chrome chip (`TranscriptionSetupChip` + the
  `useTranscriptionSetup` hook — missing / downloading N% / failed / hidden;
  "unknown" renders nothing); AiModelTab = model dashboard with
  remount-surviving progress for BOTH model families; whisper picker moved
  Recording → AI Model (Recording links over); strip un-latched, names
  downloads, retries its catalogue until the sidecar answers; NoteViewer
  navigation CTA + refetch-on-rejection + honest waiting states; useMeetings
  60 s poll + focus refresh (drain tolerance); useRecording surfaces failures.
- ✅ **Adversarial review ran** (partial — the session limit killed 3 of 5
  finder legs + most verifiers; python + contract legs completed). SIX real
  findings, ALL FIXED with tests: (1) Rust `downloadable_profile` rejected the
  whole `whisper-model:*` family — Settings downloads were dead on arrival
  (setup.rs now accepts the prefix, shape-bounded); (2) `whisper_model_is_cached`
  called a partial snapshot "downloaded" — now requires actual weight files;
  (3) the download-ready callback could be dropped by an in-flight init —
  now waits for the lock; (4) one-shot `listWhisperModels` raced sidecar boot
  leaving chip/strip blind — both retry until the catalogue lands; (5) Rust
  re-serialized absent `transcriber_state` as null → permanent fast-polling —
  `skip_serializing_if` + TS normalization; (6) Welcome hardcoded "1.6 GB" on
  macOS where the default is ~3 GB — size now read from the catalogue.
  Uncovered legs (pure-Rust internals, React hooks, regressions) were walked
  manually; a fresh review pass is cheap to re-run if wanted.
- ✅ **Phase B (tutorial) DONE:** GuidedTour v2 — teaches the flow, spotlights
  real content (new `data-tour="meeting-list"` / `"todo-board"` anchors),
  Back/Esc/arrows, replayable from Settings › General, never starts over
  Settings (fixes the wizard→Settings yank) or a failed download, and the
  final step names the no-model consequence with "Got it — I'll download it
  here". Plus the seeded demo meeting (`src-tauri/src/demo.rs`): ordinary
  deletable row, realistic dual-capture transcript, house-format notes whose
  Action Items feed the to-dos board; fresh installs only
  (`demo_meeting_seeded` + empty meetings table).
- ✅ **Hamza dev-tested the full fresh-install flow live (08-01)** — the
  `HF_HOME`/`ADVERSARIA_DATA_DIR` throwaway-dirs recipe. 8 findings, all fixed
  same session: first-launch load race (fatal screen → retry + Try again);
  endpoint-less "Registration queued" banner shown forever (wizard AND
  Settings — banners now require a scheduled retry); wizard name clobbered by
  a stale-config write (never reached Settings › General); Settings capped at
  680px; Recording/AI-Model transcription duplicate (AI Model now owns engine
  + models incl. BYOK; Recording keeps behavior only); tour tooltip pinned
  off-screen on full-page spotlights (third placement: inside the spotlight);
  Weekly/Ask/Graph tour steps now actually open their views;
  `auto_detect_meetings` defaults on; the welcome meeting is Hamza's own
  walkthrough (signed, LinkedIn) with a 4-step getting-started checklist as
  its to-dos; sidebar defaults to full cards.
- ✅ **COMMITTED + PUSHED on Hamza's word, 08-01.** Next: the V3 QA ritual —
  fresh macOS account AND fresh Windows VM with throttled + HF-blocked network
  passes (acceptance list at the bottom of SETUP_REDESIGN_SPEC.md V3) — then
  release. Remember 0.3.69 (agent write-back + MCP migration) still needs its
  own fresh notarized publish first. **Final gate state: pytest 326 ·
  cargo 175 + clippy + fmt · vitest 50 · tsc — all green.**

**Gotchas hit this session:** subagents died mid-work on the 5-hour usage limit
(reset 11:50pm Dubai) — partial work was in-tree, compiled, and was resumed,
not reverted. python-service venv drifted (`uv sync --extra dev --extra mlx` +
`uv pip install --reinstall iniconfig pytest` healed it). Stray
`src-tauri/src/http_client 2.rs` (untracked dupe) still needs deleting.

---

## Last session (2026-07-29/31 — 0.3.67 + 0.3.68 shipped, agent write-back built)

**The product changed shape this session.** It is no longer only a notetaker:
an agent can now do your action items and report back for approval. That came
out of Hamza using it in a real office meeting — Claude Code completed four of
his action items via the MCP server — and it is now the headline of the
product story.

### Shipped to users
- **0.3.67** — Formspree endpoint baked in (`xykrvprp`, verified with a live
  POST before building). Queued signups on 0.3.66 machines deliver themselves
  on first launch of this build.
- **0.3.68** — the six QA fixes from Hamza's testing, **and the first Windows
  release**: `Adversaria-windows-x64-setup.exe` is attached to the same
  release tag as the DMG, so both platforms share one stable URL pattern.

### Built but NOT published — read this before releasing
- **0.3.69** is built, notarized, and installed on Hamza's Mac. **Not
  published.** It carries the agent write-back + the `action_items` migration.
- ⚠️ **MCP server 0.2.0 is ALREADY LIVE on PyPI** and writes `status`,
  `completed_by`, `completed_at`, `evidence`. Those columns are created by
  0.3.69's migration. **Anyone pairing MCP 0.2.0 with 0.3.68 gets
  `no such column: status`.** Publishing 0.3.69 closes that gap — it is the
  main reason to ship soon.
- ⚠️ **The notarized 0.3.69 DMG predates three later fixes** (Focus-view
  notice, scope-independent notice, grid fix). The build currently installed
  has them but was NOT notarized. **A publish needs a fresh notarized build.**

### The agent loop (feature detail)
`action_items` gained `status` ("todo"|"in_progress"|"ai_done"|"done"),
`completed_by`, `completed_at`, `evidence`; `done` stays the boolean
everything already uses, kept in lockstep. **The gate: an agent can reach
`ai_done` and no further** — only `accept_agent_work()` promotes to done, and
only from `ai_done`. Evidence is mandatory (`complete_task` rejects <10 chars).
Verified end-to-end against the live DB: `done` stayed 0 after the agent
claimed completion.

**MCP server** (`adversaria-mcp` 0.2.0, PyPI): `start_task` and
`complete_task` added. It writes to the SQLite DB directly (plaintext on this
machine — `encrypt_db:false`), WAL + 10s busy timeout. One line to connect:
`{"adversaria": {"command": "uvx", "args": ["adversaria-mcp"]}}`.

### 🔴 The lesson of the night: three "the feature isn't there" reports, zero logic bugs
Every one was a **visibility** bug. The write-back worked correctly from the
first test; the UI just could not show it.
1. The With AI lane renders only in **Triage** view → someone living in Focus
   would never learn an agent finished something. Fixed with a notice.
2. The board was **scoped to one meeting** and the agent item belonged to
   another → notice is now scope-independent (the lane still follows scope).
3. **`.triage-lanes` is a hardcoded 3-column grid.** The fourth lane wrapped
   to a second row under a 156-item column — rendered perfectly, thousands of
   pixels below the fold. One line of CSS caused three rounds of confusion.
**Before declaring a UI feature broken, check it is reachable.**

### Business / positioning decisions (Hamza)
- **Licence → Elastic 2.0** (source-available). Public code, free to read,
  run, modify, self-host; **may not be offered as a hosted service by anyone
  else** — which protects the hosted tier he plans. Releases ≤0.3.68 went out
  MIT and stay MIT. The repo was briefly private and is public again.
- ⚠️ ELv2 is **not OSI-approved**, so SignPath Foundation's free code signing
  for open source probably no longer applies.
- **Windows signing researched:** Azure Artifact Signing ($9.99/mo) is
  **not available in the UAE** (orgs: US/CA/EU/UK; individuals: US/CA only).
  Realistic route is an **OV cert, $150–300/yr**. **EV no longer bypasses
  SmartScreen** (Microsoft removed that in 2024), so the EV premium buys
  nothing here. Free alternative: **Microsoft Store MSIX** — Microsoft
  re-signs and users see no warning at all. Until then, put the "More info →
  Run anyway" explanation next to the Windows download.
- **Hosting:** deferred. The battery problem that motivated it is already
  solved by the BYO-key toggles (Settings › Recording for Whisper, Settings ›
  AI Model for the LLM). A real hosted tier needs a token-issuing proxy plus
  privacy policy/terms/payments — about a week of code and rather more of
  business.

### Website — do NOT edit `landing/index.html`
The live page moved (2026-07-16) to the private **`lagharilabs-website`** repo
(`public/adversaria/index.html`, Cloudflare Pages). A full rewrite was drafted
and **rejected** — the existing page is better designed (device mockup, radial
hero gradient, two-column grid, and an Otter/Fireflies/Granola versus table).
The correct job is **four surgical edits** in that repo: add the agent story
section, add the Windows download button, update the MCP line to
`uvx adversaria-mcp`, and fix the licence line to ELv2.

**⏭ NEXT**
1. Confirm the With AI lane + Accept work now the grid is fixed.
2. Fresh notarized build → publish 0.3.69 (closes the MCP/app mismatch).
3. Website: the four edits, in `lagharilabs-website`.
4. Demo video → Andrew Warner (already contacted on LinkedIn).
5. Still open from before: the Windows `youtube` mis-categorization — needs
   the transcript check (any "Me" lines?), and CANNOT be fixed in the
   classifier; see TODO.

## Prior session (2026-07-28/29 — v2 after live QA, Ollama-on-mac, Windows RC building)

**QA loop with Hamza drove three rounds on top of the redesign** (all committed
+ pushed + public-synced; PRs #3/#4-superseded/#5 all merged):

1. **v2 (`c1237f7`)** — Hamza rejected v1's setup auto-download ("what if the
   person wants an API?"). Now: minimal wizard (whisper-only background cache),
   one-time GuidedTour ending ON Settings › AI Model, Meetily-style provider +
   installed-models dropdowns, download strictly on click, no-engine empty
   state with retroactive Generate notes (engine_configured + resummarize).
   Spec v2 addendum in SETUP_REDESIGN_SPEC.md.
2. **Ollama on macOS (`57612d5`)** — his 13-model `ollama list` surfaced two
   bugs: mac setup_status ignored Ollama entirely (now detected + selectable,
   ollama: profiles serve through Ollama on every platform) and bge-m3 passed
   the embed filter (now summarization_capable(), tested with his real names).
3. **QA state:** fresh-account wizard ✅ · guided tour ✅ · main-account
   upgrade ✅ (no wizard resurrection). Still open: download-on-click progress
   watch, no-engine meeting empty state, Ollama-model switch on main account.
   Test DMG (0.3.66, Dev-ID signed, unnotarized, queued registration) installed
   at /Applications + copies on Desktop + /Users/Shared.
4. **Windows release candidate** building via the public repo's manual
   release-windows.yml (beta, CPU sidecar) — run 30421180213.

**⏭ NEXT:** (1) finish Hamza's mac QA checklist (TODO.md); (2) Windows RC exe
→ QA on the office box (managed llama.cpp engine has NEVER run on real
Windows: tar unzip, llama-server flags, Vulkan-on-CPU — plus the EDR/
PyInstaller launch risk); (3) real 0.3.66 release = rebuild with
ADVERSARIA_FORMSPREE_ENDPOINT + notarize + publish-release.sh + attach the
Windows exe (unsigned → SmartScreen caveat; a Windows cert is a later buy).

## Prior session (2026-07-28 morning — the ENTIRE setup redesign implemented)

**All five packages of [SETUP_REDESIGN_SPEC.md](./SETUP_REDESIGN_SPEC.md) are
implemented, gated, committed (`22e7e83`…`58726c6`), and pushed.** Windows-port
merged first (workspace `0a3deec`; public PR #1 squash-merged). Mixed execution:
two subagents (packages A start + C) with lead review, the rest lead-implemented
after the agent runner started failing (`fork failed: Device not configured`).

1. **A — progress truth (`22e7e83`).** `_downloaded_bytes` probes
   snapshot → blob → `*.incomplete` per file. Reality check vs spec: hf_hub
   1.19 writes `<sha256>.<uuid8>.incomplete` (PR #4228), old caches the plain
   form — glob covers both. Measured on a real in-flight cache: 32 MB → 1.77 GB
   counted. 6 new pytest layouts.
2. **B — wizard 3 screens (`d8e25ae`).** You / Permissions (macOS-only,
   auto-skipped on Windows → 2 screens) / Ready. `resolveScreen()` maps legacy
   7-step rows read-side; `ALLOWED_STEPS` += "ready" (old names stay). New
   `SetupStatusStrip` owns post-wizard downloads + the one-shot sample
   verification — **it must call `completeOnboardingStep("sample", null,
   true)`: `complete_step` OVERWRITES `setup_complete`, false would resurrect
   the wizard** (regression-tested). Cloud config left the wizard entirely.
3. **C — settings 5 tabs (`597057c`).** 1,773-line Settings.tsx → 199-line
   shell + 5 tab components under `settings/`. Zero config keys lost (verified
   by key-set diff). Your Name first in General. Jargon guard test.
4. **E — pre-meeting notification (`13acc04` + `38bee9c`).** New
   `meeting_reminders.rs` (60 s async poll over `calendar_upcoming_events`,
   fire-once per occurrence, rescheduled events fire again). Config
   `meeting_reminder_enabled` (default false) + `_minutes` (5). Asked on the
   wizard Ready screen (default ON there), editable in Settings › General.
5. **D — Windows managed engine (`58726c6`).** `llama_engine.rs` pins
   llama.cpp **b10155** Vulkan zip (33.6 MB, sha256 in-repo) + three unsloth
   Q4_K_M GGUFs under the SAME tier ids as macOS (27B 16.8 GB / 9B 5.7 GB /
   4B 2.7 GB, 40-hex revisions + sha256s). `EngineInstallCard` shows the full
   plan before consent; consent-locked tiers are excluded from every
   auto-download path (wizard AND strip). `setup::start` serves a consented
   GGUF via managed llama-server (loopback + key + health poll, alias pinned
   to `profile_alias` by test); everything else falls through to Ollama.
   Python `_qwen_pins()` resolves tier ids per backend; `allow_patterns`
   stops a GGUF repo from mirroring every quant.

**Gates (final tree):** cargo **159** · clippy `-D warnings` · fmt · pytest
**301**/1 skip · ruff · tsc · vitest **31**. Windows compile/lint runs on the
public sync PR (this box cannot execute the Windows paths).

**⏭ NEXT — the QA gate is MANUAL and still owed (spec §QA):**
1. Fresh **macOS user account**: DMG → 3 screens → live progress bar moves
   byte-by-byte on a real ≥5 GB download (no >30 s plateau) → background
   sample ✓ → name in Settings › General → reminder fires at T−5 with a
   connected calendar.
2. Fresh **Windows 11** box (no Ollama, non-admin): consent card names
   engine+model → Install → llama-server serves → sample passes. Second
   machine WITH Ollama: its models offered, nothing auto-installs.
   ⚠️ untested-on-Windows hotspots: tar.exe unzip of the engine archive,
   llama-server flag set (`-m --alias --host --port --api-key`), Vulkan on
   CPU-only boxes, symlink-less HF cache progress counting.
3. Existing-user upgrade: no wizard reappearance, settings all present in
   the new tabs, no surprise notifications (reminder defaults OFF for them).
4. ~~Merge the public sync PR~~ — **done: PR #3 merged 2026-07-28, all 3
   checks green (incl. Windows).** Remaining: the release ritual (freeze,
   notarize, publish) when Hamza calls it after QA.

## Prior session (2026-07-27 evening — setup/settings redesign spec'd; no code)

**Docs only.** User pain: setup churn during model download, a progress bar
frozen at ~5%, over-complicated settings, Windows unusable without an expert.
Product decisions taken and spec'd in **[SETUP_REDESIGN_SPEC.md](./SETUP_REDESIGN_SPEC.md)**
(one combined release, user's explicit choice over shipping the small fix first):

1. **Progress-bar root cause FOUND (not yet fixed):**
   `model_setup.py::_downloaded_bytes` (:120) stats `snapshots/<rev>/` but
   hf_hub streams into `blobs/<sha256>.incomplete` — files only appear in
   `snapshots/` on completion. Fix = also stat blob + `.incomplete` paths
   (manifest sha256 IS the blob filename for LFS). Spec §A.
2. **Setup 7→3 screens** (You / Permissions / Ready); hardware, model-pick,
   sample, capture all demoted to background or one-liners; permissions
   auto-skip on Windows. Spec §B.
3. **Settings 8+3→5 tabs**, Your Name first field in General. Fact-check:
   name wiring already works (`registration.rs:179` → `config.user_name` →
   `Settings.tsx:1240`) — it's a *placement* problem, field hides under Voice
   Transcription. Jargon ban ("MLX/Rapid/pull") with a guard test. Spec §C.
4. **Windows managed engine — user decision: transparent + auditable.** Show
   exactly what installs (llama.cpp version/hash/source) and downloads (pinned
   model, size) before consent; detect existing Ollama/llama.cpp + GPU;
   recommend by hardware; "Not now" degrades to Settings guidance. Spec §D.
5. **Pre-meeting notification is NEW** (nothing exists — detection.rs banners
   on capture start, reminders.rs is the 9am to-do digest). Wizard toggle +
   General tab, `tauri_plugin_notification`, calendar-based. Spec §E.

Also confirmed this session: **`feat/windows-port` pushed today** (3 commits,
Windows build restored, verified on Windows 11) and its public sync
**PR LaghariLabs/adversaria#1 is OPEN with all 3 CI checks green**.

**⏭ NEXT:** (1) merge `feat/windows-port` (public PR #1 + workspace) — the
redesign builds on it, same files; (2) implement SETUP_REDESIGN_SPEC.md in its
§Sequencing order (A progress → B+C setup/settings → D Windows engine → E
notification → one QA gate: fresh macOS account + fresh Win11 box). Carried
over: Glama claim, per-meeting sovereignty toggle, final-transcript bleed,
DEEP_DIVE_BUSINESS rewrite.

## Prior session (2026-07-27 afternoon — the Windows port, built and verified natively)

**The Windows build is real again.** Everything below was done and verified ON
Windows 11 (MSVC 14.44, Windows SDK 10.0.26100, rustc 1.96): **clippy clean,
`cargo test` 149 passed / 0 failed** (with the real SQLCipher + vendored
OpenSSL), **289 pytest**, **ruff clean**, **tsc clean**. The runbook in
"Building the Windows app" below was correct in outline; the corrections it
needed are recorded here.

**New files**
- `src-tauri/tauri.windows.conf.json` — NSIS target, `installMode: currentUser`.
  ⚠️ **The runbook said `"perUser"`. That value does not exist** — the serde enum
  is `CurrentUser`/`PerMachine`/`Both` under `rename_all = "camelCase"`, i.e.
  `"currentUser"`, and `NsisConfig` sets `deny_unknown_fields`, so the documented
  value would have hard-failed the build.
- ⚠️ **It also has to delete the `rapid-mlx` bundle resource**, which the runbook
  missed entirely. Tauri merges platform config with **JSON Merge Patch (RFC
  7396)** (`tauri-utils/src/config/parse.rs`), so the key is removed by setting
  it to `null`. Without that, `tauri-build` refuses to run on Windows because a
  declared resource is missing — the same failure that killed every cargo
  command in CI on 07-25.
- `python-service/adversaria-service-windows.spec` — no MLX, `console=False`,
  CUDA bundled. **The CUDA DLLs must be flattened to the bundle root**: the
  nvidia wheels lay them out at `nvidia/<pkg>/bin/*.dll`, and the Windows loader
  does not search subdirectories, so collecting them verbatim yields a GPU path
  that fails to load and **silently degrades to CPU**. The spec *discovers* the
  installed `nvidia.*` packages rather than hardcoding cublas+cudnn — the real
  install also pulls `nvidia.cuda_nvrtc` (16 libs total), which a hardcoded list
  would have dropped.
- `scripts/build-windows.ps1` — local build, the twin of `build-dmg.sh`.
- `.github/workflows/release-windows.yml` — `windows-latest` release leg,
  guarded to the public repo (GitHub-hosted Windows minutes bill at 2×).

**Code fixes**
- `commands.rs::spawn_sidecar` was macOS-only — no `.exe`, hardcoded Homebrew
  PATH, no `CREATE_NO_WINDOW`. On Windows it hit `if !exe.exists() { return; }`
  and **silently no-opped**, so the app would launch with no ML service and no
  error.
- `commands.rs::shutdown_sidecar` — `kill()` is `TerminateProcess` on Windows and
  does not touch the process tree, orphaning helpers that keep the loopback port
  bound so the *next* launch can't start its own sidecar. Now `taskkill /F /T`
  first. (PACKAGING Phase 3 called this "the whole point of the packaging gate".)
- `run_service.py` — `console=False` means `sys.stdout is None`, and uvicorn's
  log config resolves its handler to `ext://sys.stdout`; `StreamHandler(None)`
  then raises and the service dies *before binding a port*, so Rust sees a spawn
  that never answers. `_ensure_stdio()` repoints both streams at devnull; it is a
  no-op wherever they already exist, so macOS is unaffected.
- **The Whisper picker was a no-op on Windows, worse than "wrong repo ids".**
  `server.py` assigned `_transcriber.model_repo`, an attribute only
  `MlxWhisperTranscriber` has — faster-whisper never read it. The registry is now
  backend-selected (`active_whisper_models()`), CT2 repos are HF-verified
  (`Systran/faster-whisper-large-v3`, `deepdml/faster-whisper-large-v3-turbo-ct2`),
  the MLX-only 4-bit key aliases onto the turbo tier so a Mac-written config
  still resolves, and `WhisperTranscriber::ensure_model_repo()` reloads on a real
  change and keeps it (sticky — faster-whisper holds one model for the process
  lifetime, so restoring per request would reload twice).
- `wasapi.rs` — two defects, both invisible to a compiler:
  1. `state.push(data)?` returned **before `ReleaseBuffer`**, leaking the packet.
  2. **Loopback emits nothing at all while the endpoint is idle** — not silent
     packets, *no* packets. The mic stream keeps delivering, so every quiet
     stretch shortened the system stream and shifted every later "Them" turn
     earlier, which `build_labeled_turns` then interleaves in the wrong order.
     ScreenCaptureKit pads silence for us, which is why macOS has no equivalent.
     Now padded to wall clock, with `AUDCLNT_BUFFERFLAGS_SILENT` honoured.
     Threshold is 250 ms — deliberately well above the 10 ms idle sleep and
     spool-flush back-pressure, because padding at *that* scale would splice
     silence into audio that never stopped. 5 unit tests on the pure decision fn.
- `commands.rs::open_privacy_settings` had a **Windows-only `unused_variables`
  error** under the `-D warnings` gate. It is pre-existing: the private workspace
  and the public repo have no shared history, so workspace-only commits (the
  permissions work) **have never been linted on Windows at all**. Assume more of
  these until the repos are synced — `scripts/sync-public.sh` is still unwritten.

**The installer exists:**
`src-tauri/target/release/bundle/nsis/Adversaria_0.3.65_x64-setup.exe` — **81.8 MB**,
built by `npm run tauri build`. `installMode: currentUser`, so `%LOCALAPPDATA%`
and no admin prompt.

**🔴 It is CPU-only, and that is forced, not a preference.** The CUDA-bundled
sidecar is **2.4 GB** (1.9 GB of it 15 CUDA DLLs — `cublasLt64_12.dll` alone is
638 MB) and **NSIS cannot package it**: `makensis` dies with
`Internal compiler error #12345: error mmapping datablock`, and Tauri then
reports a misleading `os error 2` for the installer that was never produced.
MSI is no better. The spec now defaults to CPU-only because that is what builds.
GPU still works for anyone with the **NVIDIA CUDA Toolkit** installed
(`_patch_cuda_path()`'s Toolkit branch survives freezing; its site-packages
branches do not). The real fix — download the CUDA runtime on first run, exactly
as model weights already are — is in TODO.md.

**Verified empirically, not assumed:** `rapid-mlx` was **not** staged into
`target/release/` while `adversaria-service` was, which is direct proof the RFC
7396 `null` deletion in `tauri.windows.conf.json` does what it claims.

**🔴 First real install failed — fixed (found by running the installer):**
`Adversaria can't start — no such table: action_items`, with the dialog advising
"allow keychain access when macOS asks" **on Windows**.

`init_db` runs `migrate_plaintext_to_encrypted()` **before** creating the schema,
and that migration verified its copy by counting `meetings` / `action_items` /
`chat_messages`. The **0.2.x Windows line wrote the same path**
(`%APPDATA%\meeting-note-taker\meetings.db`) with only a `meetings` table — real
file on the dev box: **147 meetings, no `action_items`** — so every upgrader from
that line was dead on arrival. Encryption is on by default and the old
`config.json` has no `encrypt_db` key, so the default applies and the migration
always runs.

Fixed with `storage::table_count()` (0 for an absent table — `sqlcipher_export`
copies whatever schema it finds, so absent-on-both-sides is a legitimate match)
plus a per-platform credential-store message. **2 regression tests; 151 pass.**
No data was at risk: the migration bails before swapping and keeps
`meetings.db.pre-encrypt-backup` regardless. **Rule this establishes:** anything
running before the `CREATE TABLE IF NOT EXISTS` batch must assume an arbitrarily
old schema. Everything after it already gates on `column_exists`.

**🔴 Second real failure — first-run setup could never finish on Windows. Fixed.**
Step 6/7 hung on "Your meeting model is still downloading … Preparing…" with the
sample button disabled, and the copy said "On this Mac". Four Apple assumptions:
the sample gate needs a **pinned MLX snapshot** (`setup.rs` returned only
`mlx-community/*` profiles, so `installed` was false forever); `MODEL_PINS`
pre-downloaded **3.5 GB of MLX Whisper weights faster-whisper cannot load**;
`rapid_runtime_bundled: false` was rendered as a broken install rather than the
normal off-Apple case; and the copy hardcoded "Mac".

`setup_status()` is now **async** and returns **already-pulled Ollama models** as
profiles when no Rapid-MLX runtime is bundled — `installed: true`, recommended by
what fits ~70 % of RAM, embedding models filtered out. `model_setup` pins now
follow `transcriber.backend_is_mlx()`; on CT2 both Whisper pins resolve to
`Systran/faster-whisper-large-v3` (already cached on the dev box, so the step is
instant), and `whisper-live` intentionally shares it because
`_build_live_transcriber` only builds a separate live model on MLX. The existing
`ollama_model` plumbing needed no change — `model_alias` carries the Ollama tag.
291 pytest · 151 cargo · 15 vitest · tsc · clippy all green.

**🔴 Third failure — "Managed Rapid-MLX is currently available on Apple Silicon
only". Fixed.** The code models "local engine" as one thing: a child process
Adversaria spawns and supervises. On Windows it is **Ollama** — external, not
owned — so all three lifecycle points rejected it: `setup::start()` →
`runtime_path()` hard-errors off Apple Silicon; `set_local_model_profile` guards
on `pinned_snapshot()`; `test_local_setup` demands `managed_credentials()` that
only `rapid-mlx serve` produces. An `ollama:` id now short-circuits each —
`start()` is a reachability check returning a synthetic `running`, the snapshot
guard is skipped, and the sample passes `llm_base_url: None`, which is exactly
how the Python summarizer picks its Ollama backend.

**🔴 …and that fix did not reach existing users.** It keyed off an `ollama:` id
prefix, but onboarding **persists `selected_model_profile`**, so anyone who
completed the model step on an earlier build still had `qwen-27b-quality` stored.
A resumed setup restored it verbatim and failed at 6/7 with the same message.
Now fixed in two places: `setup::start()` branches on **`rapid_mlx_supported()`**
rather than the id prefix (a stale id falls back to the configured
`ollama_model`), and `Welcome.tsx::resolveProfile()` only restores a persisted
choice that still exists in this machine's `setup.profiles`. 3 regression tests.

**🔴 Fourth failure — `Unknown model profile: ollama:qwen3:14b`. Fixed at the
root.** `setup::profile_alias()` is the single id→model-name map the whole app
funnels through, and it knew only the three pinned MLX ids. **Four** call sites
gate on it (`complete_step`, `set_selected_model_profile`, and the two "is a local
model configured?" checks in `commands.rs:3680` / `lib.rs:149`), so fixing
`setup::start` and `pinned_snapshot` in earlier rounds left all of them rejecting
Ollama. It now returns `Option<String>` and resolves `ollama:<tag>` → `<tag>`;
`downloadable_profile` gained an explicit `ollama:` exclusion because it used to
infer downloadability from `profile_alias` being `Some`. **All 8 call sites
audited this round** (grep `profile_alias|pinned_snapshot|downloadable_profile|
rapid_mlx_supported`) rather than fixing one more and hoping. 153 cargo tests.

**Lessons worth keeping:** the failures were *staged* — fixing the model list only
revealed the next guard, then the next. Port by tracing the whole flow
(start → verify → sample), not the step that is currently red. And a fix gated on
a **new** identifier format does nothing for rows already written in the old one:
validate persisted selections on read, because they cross both versions and
platforms.

**⚠️ NOT verified — the honest gaps**
- **The frozen sidecar has never been executed.** This machine refuses to launch
  the PyInstaller exe (`Access is denied` from both bash and PowerShell, even
  with the sandbox off, while a trusted exe in the same tree runs fine). Defender
  is disabled here, so a third-party EDR is the likely culprit —
  PyInstaller bootloaders are routinely heuristically flagged. **This is also a
  real user-facing risk, not just a dev-box quirk, and strengthens the
  code-signing case.** Everything about the sidecar below the process boundary
  (freeze, DLL placement, size) is verified; that it *serves* is not.
- No live call: dual capture, the silence padding, registry meeting-detection,
  and the CUDA path loading from the frozen bundle are all unrun.
- **Windows live captions still use the full large-v3.** `_build_live_transcriber`
  correctly guards on `isinstance(..., MlxWhisperTranscriber)` and falls back to
  the main model, so this is a perf gap, not a bug. Giving Windows the turbo
  model would mean a second CUDA model resident — deliberately left alone rather
  than risk an OOM on a modest GPU in a path that can't be tested here.

**Next step:** run `scripts/build-windows.ps1` on a box that will actually
execute the sidecar, then work the "Windows-port verification checklist" below.

---

## Prior session (2026-07-27 morning — product overview written for slide generation; no code)

**Docs only — zero code, zero version change.** Two questions from the user, then
one artifact.

1. **"How does it detect a meeting?"** — walked `src-tauri/src/detection.rs`. The
   answer worth keeping (it's the one that lands with non-technical readers):
   detection keys on **microphone input, never audio output**, which is the whole
   reason a YouTube video doesn't trigger it while a Meet call in the same
   browser does. Windows reads the ConsentStore `LastUsedTimeStop == 0`; macOS
   reads CoreAudio `kAudioProcessPropertyIsRunningInput`. Allowlist + 2-poll
   debounce are the second and third filters, not the first.
2. **A reply to a LinkedIn comment** asking whether it integrates with Teams —
   drafted around "no integration at all, it reads the OS's own mic-indicator
   signal." Deliberately gave **no Windows date** (code path is real and CI-built;
   installer is not published).
3. **📄 NEW: [PRODUCT_OVERVIEW.md](./PRODUCT_OVERVIEW.md)** — a single
   self-contained, product-level (no code) description of Adversaria and its
   complete feature set, written as a **NotebookLM source for slide generation**.
   Built from SPEC + README + all 65 CHANGELOG entries + STATUS + STRATEGY +
   LAUNCH_ASSETS + the shipped UI surface. Describes v0.3.65.

**⚠️ STALENESS FOUND — [DEEP_DIVE_BUSINESS.md](./DEEP_DIVE_BUSINESS.md) describes
v0.3.14 and is 51 releases behind.** It still says the Kanban/to-do board is
unbuilt (shipped 0.3.45, two modes), notarization + the first-run wizard are
launch blockers (both shipped), and the product is closed-source with only the
MCP server open (repo is MIT and public). Weekly Briefing, graph dossier + person
profiles, Insights, the notch pill, and the Second Brain export all postdate it.
**Anyone feeding docs to an external tool must not include it alongside
PRODUCT_OVERVIEW.md — they contradict.** Either rewrite it against v0.3.65 or
mark it historical; `docs/STRATEGY.md` has NOT drifted and is still usable.

**⏭ NEXT (of that session):** user-side QA of the permission recovery path in a
fresh macOS user account, the Glama claim to unblock awesome-mcp-servers #10922,
per-meeting sovereignty toggle, final-transcript bleed. Optional cleanup: the
DEEP_DIVE_BUSINESS rewrite above.

## Prior session (2026-07-25 midnight — 0.3.65: update-path recovery + stable download filename)

**0.3.65 notarized** (Apple **Accepted**, stapled, Gatekeeper accepted) and
publishing. Contains the update-path permission recovery from `9875ed8`.

**🔴 THE BUG THAT COST THE MOST TIME — read the LESSONS entry.** The user's own
install kept refusing to record *even with Screen Recording enabled*, through
repeated toggle/re-grant/relaunch cycles. Cause: **two TCC rows for
`com.meetingnotetaker.app`** — `tccutil reset` printed "Successfully reset" twice
for one bundle id. The System Settings toggle only rewrites one row. Cure:
`tccutil reset ScreenCapture com.meetingnotetaker.app`, then quit and
`open -a Adversaria`. Developer-only hazard (≈15 differently-signed builds in a
day); a normal user won't reproduce it.

**Stable download filename (`dbb25e5`) — two halves, both needed:**
- `build-dmg.sh` now also emits `Adversaria-macos-arm64.dmg`, copied **after
  stapling** so it carries the notarization ticket. Verified: byte-identical to
  the versioned DMG and independently passes `stapler validate` + `spctl`. Copy
  it before stapling and it looks fine locally but fails Gatekeeper on a
  stranger's Mac.
- `publish-release.sh` now **uploads the DMG automatically**. It previously
  published only the updater tarball + manifest — the 0.3.64 DMG had to be
  attached by hand, which is how a release ships with no download at all. It
  warns loudly (with the recovery command) if the DMG is missing.
- Why it matters: the website links to `releases/latest/download/<name>`, so a
  version-stamped filename **silently 404s** the moment the next release ships.

⚠️ **Publishing was still in flight at the end of the session** — the release
showed as **Draft** while ~1.4 GB of assets uploaded. **Verify it went Latest and
that the download URL resolves** before assuming it shipped:
```bash
gh release list --repo LaghariLabs/adversaria-releases | head -2
curl -sIL https://github.com/LaghariLabs/adversaria-releases/releases/latest/download/Adversaria-macos-arm64.dmg | grep -i '^HTTP/'
```
Also: `publish-release.sh` can fail once with `ReleaseAsset.name already exists`
(gh rolls the release back); a plain retry works.

**NEXT:** (1) confirm the 0.3.65 publish + download URL; (2) **QA permissions in a
fresh macOS user account** — the recovery path has still never met a real prompt,
since once granted the branch never runs; (3) user: Glama claim (unblocks
awesome-mcp-servers #10922), directories, Reddit — copy in
[LAUNCH_ASSETS.md](./LAUNCH_ASSETS.md); (4) still open: `sync-public.sh`,
per-meeting sovereignty toggle, `_merge_dual` final-transcript bleed.

---

## Prior session (2026-07-25 late night — 0.3.64 published; update-path permission bug found + fixed)

**🔴 THE 0.3.64 FIX WAS INCOMPLETE — found live, fixed in `9875ed8` (needs a
0.3.65 freeze).** Moving permissions into first-run setup only helped **new**
users. The user auto-updated 0.3.63 → 0.3.64, pressed Record, and got
`NoShareableContent("Content unavailable: The user declined TCCs…")` with no way
out. **macOS revokes Screen Recording whenever the app bundle is replaced**, so
every updating user hits the exact flow setup was built to fix — and they never
see the wizard again.
- `start_recording` now **pre-flights** `permissions::check()` before starting a
  capture session (the old failure came from deep inside ScreenCaptureKit *after*
  a session was half-started).
- The error carries `PERMISSION_ERROR_PREFIX` (`"PERMISSION_REQUIRED:"`); the
  `ErrorBanner` renders **Open Settings** + **Relaunch** buttons. The relaunch is
  the step users don't know about — macOS won't apply the grant until restart.
- ⚠️ The prefix exists in **both** `commands.rs` and `src/lib/tauri.ts`. A Rust
  test reads the TS file and pins them together (verified it fails on drift);
  without it the banner degrades to plain text and nobody notices.
- Verified: tsc ✓ vitest 15 ✓ clippy -D warnings ✓ fmt ✓ **cargo 145** ✓.
- ⚠️ Still **untestable on this machine** — once Screen Recording is granted the
  branch never runs. Fresh macOS user account remains the only real proof.

**⚠️ MY OWN MISTAKE, WORTH NOT REPEATING:** to grab demo screenshots I launched
`/Applications/Adversaria.app/Contents/MacOS/meeting-note-taker` **directly from a
shell**. That (a) may disturb the app's TCC attribution, since macOS attributes
permission to the responsible parent process, and (b) **ignored
`ADVERSARIA_DATA_DIR` and opened the user's REAL database** — the override is
`#[cfg(debug_assertions)]` and release builds deliberately ignore it. A screenshot
of real meetings was captured and deleted. Use `open -a Adversaria`, and use a
**debug build** for isolated data.

**✅ 0.3.64 NOTARIZED + PUBLISHED.** Apple job `9662d85e-cdd0-40b9-ab3f-e4b6be02985f`.
DMG sha256 `6367c48e506145c3049a323963531d7ad719489b81759c7f26cad13b96e6cc35`.
Release carries the DMG + updater artifacts + manifest; `latest-beta.json` verified
serving 0.3.64. ⚠️ The first `publish-release.sh` attempt failed with
`ReleaseAsset.name already exists` and gh **rolled the release back** — benign and
retryable, a plain re-run worked. ⚠️ The site's download URL embeds the version in
the filename, so it **404s on the next release** unless `build-dmg.sh` also emits a
stable `Adversaria-macos-arm64.dmg`.

**Marketing (see [LAUNCH_ASSETS.md](./LAUNCH_ASSETS.md) — canonical, paste-ready):**
GitHub topics added to both repos (they had none). Three awesome-list PRs open:
awesome-mcp-servers #10922 (🟡 maintainer wants a **Glama** listing first — the
Dockerfile prerequisite is committed and verified end-to-end via a real MCP
handshake; **claiming on Glama needs the user's account**), awesome-mac #2408,
awesome-privacy #960. Deliberately **not** submitted: `modelcontextprotocol/servers`
(retired third-party listings) and `awesome-selfhosted` (scope is network services).
`awesome-tauri` blocked on **signed commits**; `awesome-rust` needs **>50 stars**
(repo has 1). A 47s programmatic demo video is at `marketing/product-demo/` —
re-render after feature changes rather than re-shooting.

**Decision recorded:** keep `adversaria-mcp` a **separate repo** for now — the
public `adversaria` repo is a hand-filtered copy with an unsolved sync problem, and
the open PR + Glama listing point at the standalone repo. Revisit after
`sync-public.sh` exists.

**NEXT:** (1) **0.3.65 freeze + publish** so the recovery path ships; (2) QA
permissions in a fresh macOS user account; (3) stable DMG filename; (4) user:
Glama claim, directories, Reddit; (5) still open — `sync-public.sh`, per-meeting
sovereignty toggle, `_merge_dual` final-transcript bleed.

---

## Prior session (2026-07-25 night — permissions moved into setup; MCP published; site live; CI green)

**🔴→✅ THE CHURN BUG IS FIXED (`cbd8e62`, NOT in any build yet — needs a 0.3.64
freeze).** The first external tester's actual failure: she downloaded, pressed
Record, and only then met a macOS permission prompt — and for Screen Recording,
one that requires **relaunching the app**. The wizard's `permissions` step was
decorative text that literally said *"macOS asks only when a feature first needs
access"*; there was **no code behind it**. This had been an open 🔴 in
[TODO.md](./TODO.md) since 07-18.
- New `src-tauri/src/permissions.rs`: live TCC state + request for both.
  **Microphone** via `AVCaptureDevice` (in-process prompt, no restart).
  **Screen Recording** via `CGRequestScreenCaptureAccess` — macOS honours that
  call **exactly once per install**, so a denial falls back to opening the exact
  System Settings pane. `CGPreflightScreenCaptureAccess` can't distinguish
  "never asked" from "denied", hence the try-then-Settings flow.
- Screen Recording **doesn't apply until relaunch** → the step detects that and
  offers a Relaunch button rather than letting the user discover it by failing
  to record. Step **re-polls on window focus** (granting in Settings fires no
  callback). Screen Recording is listed first — without it a meeting captures
  nobody but you. Windows stubs return granted.
- ⚠️ **Untested against a real prompt** — this Mac already holds both grants.
  Test in a **fresh macOS user account**.
- ⚠️ Gotcha hit while building: the new `useEffect` landed *after* the
  component's early return → "Rendered more hooks than during the previous
  render" and Welcome rendered empty. Hooks must sit above
  `if (!onboarding || …) return null;`.

**✅ CI IS GREEN** (all three jobs, Windows included — so the unverifiable
`wasapi.rs` edits were fine). The last blocker was `tauri-build` refusing to run
because the gitignored PyInstaller sidecars are declared bundle resources; CI now
`mkdir -p`s empty stubs. Then five clippy `-D warnings` lints, now cleared.

**✅ MCP SERVER PUBLISHED — `LaghariLabs/adversaria-mcp`** (MIT). It lives at
`~/Documents/Documents/MyProjects/mcp-server` and was never a git repo before.
All four tools verified against the real DB before publishing
(`list_recent_meetings`, `search_meetings`, `get_meeting`, `get_action_items`).
Documented limitation: it opens plain SQLite, so it **cannot read the DB if
encryption at rest is enabled**.

**✅ WEBSITE IS DOWNLOAD-FIRST AND LIVE.** ⚠️ **`git push` does NOT deploy it** —
the Pages project has **no Git integration** (`Git Provider: No`), it's direct
upload: `npx wrangler pages deploy dist --project-name=lagharilabs`. Full runbook
now at `lagharilabs-website/DEPLOY.md`. Waitlist demoted to Windows-only interest.

**✅ Public README** rewritten around organization (to-dos, weekly briefing,
graph, self-filling contacts, Ask, MCP) + two dead doc links fixed
(`CODEX_PLAN.md`, `HANDOFF.md` aren't in the public repo).

**Marketing:** user published the LinkedIn post. [LAUNCH_PLAN.md](./LAUNCH_PLAN.md)
is still the plan and today **killed its two biggest risks** — P1/M5
(closed-source liability → now MIT) and P3 (notarization). Assets on the user's
Desktop: `adversaria-carousel/` (10 slides + PDF + source) and
`laghari-org-avatar/`. **Deliberately NOT done: Show HN.** Only one external
tester exists and 0.3.61–0.3.63 have never run on another machine; the plan's own
P2 says a broken first run in front of an HN front page is unrecoverable. Gate it
on ~5 clean external installs.

**NEXT:** (1) **0.3.64 freeze** so the permissions fix actually ships; (2) QA it in
a fresh macOS user account; (3) directory submissions (evergreen, zero risk);
(4) Show HN once first-run is proven; (5) still open: `scripts/sync-public.sh`,
per-meeting sovereignty toggle, `_merge_dual` final-transcript bleed.

---

## Prior session (2026-07-25 evening — OPEN SOURCED + 0.3.63 published)

**Adversaria is now public and MIT licensed.** Read this before touching either repo.

**TWO REPOS NOW — this is the biggest structural change:**
- **`LaghariLabs/adversaria`** — **PUBLIC**, MIT. A *filtered copy*: code, README,
  LICENSE, CHANGELOG, and only `docs/ARCHITECTURE.md` +
  `docs/PRIVACY_NETWORK_BOUNDARIES.md`. Single squashed initial commit — no history.
- **`LaghariLabs/adversaria-workspace`** — **PRIVATE**, the working repo (this
  clone). Full ~560-commit history and every doc. `origin` points here.
- ⚠️ **They share no history.** Fixes have already been hand-copied twice and
  *will* drift. A `scripts/sync-public.sh` that re-exports the filtered tree was
  proposed and NOT written — do this before the next public change.

**Why filtered:** the user wanted no monetization talk ("greed"), no competitor
disparagement ("shades"), but **credit kept where due**. Meetily attribution in
`CHANGELOG.md` and `live.py` is deliberately RETAINED — stripping credit while
keeping their VAD constants is the riskier move. Excluded from public: STATUS,
HANDOFF, SPEC, STRATEGY, TODO, DECISIONS, CLAUDE.md, DEEP_DIVE_*,
marketing_strategy, LAUNCH_PLAN, CODEX_*, SPEC_*, `marketing/`, `experiments/`.
Verified live via the contents API that each returns 404.

**0.3.63 SHIPPED + PUBLISHED.** Notarized (Apple job
`bead2d17-6d4a-463e-81a2-9a532d4532db`), stapled, Gatekeeper accepted. **DMG 752 MB,
sha256 `ec3861af156da8efde65d8ca49e98c395d7d9d50c01a4b552675dcd8c2ace51b`.**
`publish-release.sh` run for the first time since June — v0.3.63 is now Latest on
`LaghariLabs/adversaria-releases` with the DMG *and* the updater artifacts, so the
auto-update toast finally has a target. User installed and confirmed it works.
⚠️ The `latest/download/` URL embeds the version in the filename, so it 404s on the
next release — either bump the site link each time or have `build-dmg.sh` emit a
stable `Adversaria-macos-arm64.dmg`.

**🟡 CI ON THE PUBLIC REPO — six real bugs found and fixed; last run still
pending.** These workflows had **never actually executed** before today (added
recently, against a private repo whose default branch is `master` while the
workflow triggers on `main`), so going public found six latent problems in an hour:

1. `check-security.mjs` used `URL.pathname` → on Windows `/D:/…` → `resolve()`
   prepends the cwd drive → `D:\D:\…` ENOENT. Now `fileURLToPath`.
2. `scipy` imported by `test_cloud_transcribe.py` but undeclared — present
   transitively in a full local install, absent under CI's
   `uv sync --frozen --extra dev`. Added to the dev extra + relocked.
3. `cargo fmt` drift (commands/reminders/second_brain/setup).
4. **`tauri-build` refused to run at all**: `tauri.conf.json` declares the two
   PyInstaller sidecars as bundle resources, and their `dist/` dirs are
   gitignored → `resource path '../python-service/dist/adversaria-service'
   doesn't exist` killed *every* cargo command before compiling. Fixed by a
   workflow step that `mkdir -p`s empty stubs — clippy/tests need the paths, not
   the binaries. (This is why the e2e job passed all along:
   `tauri.e2e.conf.json` sets `"resources": []`.) Verified locally by moving the
   real dirs aside and running `cargo check` against empty stubs.
5. Five clippy `-D warnings` lints, only reachable once #4 was fixed: three
   too-many-arguments (save_person / upsert_person / feed_live_source — all
   crossed the threshold from today's work; allowed with rationale, since
   restructuring `save_person` would change the IPC shape and TS cannot
   type-check an `invoke` payload), one map-over-inspect, and two **Windows-only**
   lints that had never been linted because development is on macOS
   (`AudioCapture` missing the `Default` impl `macos.rs` already has, plus a
   redundant `return`).
6. e2e minimum-viewport test now **skips** when the display can't host 1024x720 —
   GitHub macOS runners are 1024x768 → ~645 CSS px, never passable. **The desktop
   smoke job now PASSES.**

**⚠️ CORRECTION — an earlier entry in this file blamed an "org Actions quota /
runner policy". That was WRONG; do not chase it.** The mystery cancellations were
this workflow's own `concurrency: cancel-in-progress: true` — pushing fixes every
few minutes meant each run killed the previous one. Every run was on a PUBLIC repo,
where GitHub-hosted runners are free; **nothing was ever billable.** The rule is
simply: push once, then let the run finish.

**Billing hardened anyway:** every job now carries
`if: github.repository == 'LaghariLabs/adversaria'`, so the private workspace can
never spend minutes (macOS ×10, Windows ×2) even on a PR. Guarded rather than
deleting the `pull_request` trigger so both copies of the file stay byte-identical
and a future sync can't reintroduce the cost or strip PR checks from the public repo.

⚠️ **`wasapi.rs` changes are UNVERIFIED locally** — `#[cfg(windows)]`, and
cross-compiling fails here (`openssl-sys` builds from source, needs a
Windows-compatible perl). CI is their first real check.
`release-candidate.yml` is untouched: `workflow_dispatch`-only, so it cannot fire
by accident, but **never dispatch it from the private repo** — it builds a full
notarized release on macOS at ×10.

**Positioning shifted (matters for all copy).** Lead with **organization**, not
privacy: "capture is solved, what happens afterward isn't" — meetings pile up and
can't be found. Privacy became a supporting *flexibility* point (local by default,
BYOK when the hardware isn't there), because the app genuinely supports a cloud
path and shouldn't over-claim. A LinkedIn post was drafted on that frame (44 days,
560 commits, feature-led, credits the OSS it stands on, names no competitors).
⚠️ **Screenshots must use `marketing/demo-data/` (7 synthetic bundles) — the real
workspace contains actual meetings with real people.**

**NEXT:** (1) unblock CI; (2) write `scripts/sync-public.sh`; (3) website — the
live page is in the **separate `lagharilabs-website` repo** (`public/adversaria/
index.html`, Cloudflare Pages), NOT `landing/` here, which is a dead copy; swap
"Request an invite" for a Download button; (4) still queued: per-meeting
sovereignty toggle, pause/resume, People tab, `_merge_dual` final-transcript bleed.

---

## Prior session (2026-07-25 afternoon — CRM foundation + open-source prep)

**Three CRM features shipped (committed, NOT pushed, NOT in any build yet):**
- `f39bb2c` **contact details on person profiles** — email/phone/LinkedIn columns
  on the existing `people` table (additive migration, default `''`), editable in
  the graph dossier, exported into the Second Brain person-note frontmatter.
  Deliberately manual — audio never carries an email.
- `cde6d9b` **graph search** — toolbar box dims all but label matches; match
  count zooms to them (Enter same, Escape clears). Reuses the existing
  `faded`/`highlighted` classes so it can't fight tap-to-explore.
- `1c9251c` **role/company prefill from the meeting** — the summarizer already
  asked for each attendee's `role` and discarded it at render; it now also asks
  for `company` and both reach Rust as `attendee_details`. First time a person
  appears, their profile is pre-filled. **Never overwrites a user-typed value**
  (only fills blanks), matched on the bare name (the key both `people` and graph
  person nodes use), wired into all five attendee-persisting paths.
- Verified: tsc ✓ · vitest 15 ✓ · **cargo 144** (+4) ✓ · **pytest 282** (+5) ✓.

**Key discovery that reframed the work:** the CRM foundation already existed —
`people` table (`storage.rs:392`), `get_person`/`save_person`, an editable
dossier in GraphView, and per-person Second Brain notes listing shared meetings.
This was extending it, not building it.

**Open-source prep (done, NOT executed).** Repo is still **PRIVATE**; flipping it
public is a one-way door. Git history scanned for secrets across all commits —
**clean**, the only Formspree hits are placeholders (`REPLACE`, `abcdwxyz` test
fixture); no private keys/tokens/AWS keys. **Two decisions block publishing:**
(1) **license** — AGPL-3.0 protects the paid-sync plan (a hosted fork must
publish changes) while MIT/Apache does not; and (2) **CLA/DCO before the first
external PR** — the user is sole copyright holder today, which is the only reason
selling commercial licenses is possible; accepting outside contributions without
a CLA permanently forfeits that.

**Direction discussion captured in [TODO.md](./TODO.md)** (2026-07-25 section):
HeyClicky competitive read (not a competitor — cloud screen-assistant), the CRM
backlog, vertical templates, and the three thesis-compatible revenue lines. The
user's open question — **how team sharing works for banks/law firms/hospitals/
sales while solo consultants stay free** — is undesigned.

**NEXT:** (1) push these three commits; (2) the user's license + CLA calls, then
flip the repo public and update the website; (3) People tab; (4) still pending
from this morning: AirDrop the notarized 0.3.62 DMG for acceptance, and the
per-meeting sovereignty toggle ("the toggle" the user asked for).

---

## Prior session (2026-07-25 early morning — 0.3.62 committed, pushed, notarized)

**Everything below that says "UNCOMMITTED" is now shipped.** The four-arc batch
was committed, pushed, and built into a notarized DMG.

- **Committed** (tree clean): `c850d81` feat(recording) — notch dynamic island +
  per-channel waveforms + blue/red speaker system + live-bleed dedup (11 files,
  +687/−59) · `4d7100f` chore(release) 0.3.62 · `35e114c` docs.
- **Pushed** `ffe6e88..35e114c` → origin/master. That also carried the three
  previously-stranded commits (0.3.60, its docs, 0.3.61 mic fix). master == origin.
- **Notarized 0.3.62** per NOTARIZATION.md §4: Developer ID `4MY4PH5PHC` +
  `adversaria-notary`, `ADVERSARIA_RELEASE_MODE=1`, channel `beta`,
  `ALLOW_INCOMPLETE_REGISTRATION=1` (same as 0.3.58–0.3.60 — Formspree is not a
  notarization input), `ADVERSARIA_INSTALL=0`. Apple **Accepted**, job
  `43f01891-2575-499c-a59f-5b8313fb6051`; stapled + validated; Gatekeeper
  **accepted / source=Notarized Developer ID**.
  **DMG: 752 MB · sha256 `1b43511ce2b901aa381517e5e8bfb25ff0ccc706684e1daa8f1b71cb16c56247`**
  at `src-tauri/target/release/bundle/dmg/Adversaria-0.3.62-beta-macos-arm64.dmg`.
- **Verified independently on the built artifact** (not taken from the build
  script's own output): Info.plist 0.3.62 · Authority = Developer ID, Team
  4MY4PH5PHC · `codesign --verify --deep --strict` = valid + satisfies DR ·
  `SCScreenshotConfiguration` absent (the macOS-15 launch fix still holds) ·
  binary exports `get_audio_levels` + `set_recording_bubble_expanded` · the
  embedded frontend (dist built 07:52, binary linked 07:56) contains
  `notch-island`, `3d97ff`, `ff5f57`. Pre-build: tsc ✓ · vitest 15/15 ✓ ·
  cargo test 140/140 ✓.
- ⚠️ **Gotcha for verifying future builds:** Tauri 2 embeds the webview assets
  *compressed inside the binary* — `strings` on the binary will NOT find frontend
  markers, and there is no `Contents/Resources/dist/`. Grep the repo's `dist/`
  instead and check its mtime falls inside the build window.

**NEXT (user's move):** AirDrop the 0.3.62 DMG to the sister's macOS-15 laptop →
install over 0.3.60 → acceptance (launches, first-run wizard, record→summarize,
notch island hover-expand, blue/red speakers). It is **NOT published** on purpose;
on a clean pass run
`ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh "0.3.62 — …"` to
wire the update toast. Then the two queued features (per-meeting sovereignty
toggle · pause/resume recording). Still open: FINAL-transcript bleed via
`_merge_dual`; `build-dmg.sh` comment/`ADVERSARIA_INSTALL` default mismatch;
stuntman worker down (DeepSeek 402); two throwaway test meetings in the DB.

---

## Prior session (2026-07-24 LATE evening — mic fix shipped as 0.3.61 staging; notch dynamic-island arc; blue/red speaker system; live-bleed dedup — all late work now COMMITTED, see above)

**Where things stand cold (23:00):**
- **Installed on this Mac:** 0.3.61 staging (dev-signed) — contains everything
  through the mic-mono fix. The **dev app** (`npm run tauri dev` may still be
  running) additionally has the whole notch/waveform/color/dedup batch below.
- **For the sister:** the notarized **0.3.60 DMG** (sha `be797c06…`) is verified
  and ready to AirDrop — it lacks the mic fix + tonight's UI work, but she can't
  hit the mic bug (built-in 1–2 ch mic). Next notarized release = **0.3.62** on
  "ship it" (bundle: mic fix + notch island + colors + dedup).
- **UNCOMMITTED working tree** (verified: tsc ✓ vitest 15 ✓ cargo check ✓ cargo
  test **140** ✓): the four arcs below. Commit lands on user sign-off.

**A) 0.3.61 (COMMITTED + staged):** 16-ch virtual input device ("Quicktime
Player" was the macOS default input) produced a 7.6 GB/45-min mic spool → WAV
u32 cap → transcription retry-proof. Fixed: mic downmixes to mono in the cpal
callback; `decrypt_channel` streams oversized multi-channel tracks through
`downmix_f32_to_mono` (recovered the user's stuck meeting — which turned out to
contain reels audio, not a meeting). Default input restored to MacBook Pro
Microphone. LESSONS has the postmortem.

**B) Notch dynamic island (uncommitted):** pill docks INTO the physical notch —
plain Tauri window + objc2-app-kit raw calls (NO NSPanel), `setLevel(25)` +
collectionBehavior + `orderFrontRegardless` **BEFORE** `setFrame` (ordering was
a live-debugged bug: AppKit clamps frames below the menu bar otherwise; LESSONS
entry). Organic styling: 12 px concave fillet corners (window widened 2×12 px),
460 ms bloom-from-notch entrance (`backwards` fill — `both` kills the hover
transition), hover breathing. Then made truly dynamic: expressive-docked starts
as a **collapsed menu-bar-height strip** (dot + timer | blue/red mini-waves) so
it never covers app content (user hit it blocking Chrome tabs); hovering calls
new `set_recording_bubble_expanded` (Rust resizes the frame) and the body
(caption/waves/Stop) animates open; collapses 300 ms after mouse-leave.
Recipe cross-validated against the user's own NotchyPrompter
(`teleprompter/NotchyPrompter/Sources/NotchWindow.swift`).

**C) Blue/red speaker system (uncommitted):** Me = `#3d97ff`, Them = `#ff5f57`
everywhere — notch waves now amplitude-driven by real per-channel loudness
(new `current_levels()` both platforms + `get_audio_levels` command, 130 ms
poll, `--lvl` CSS scaleY), live-transcript lines carry `source` end-to-end
(`LiveTranscript{text,source}` → `App.liveLines[]` → companion left bars), and
the meeting transcript renders colored speaker chips (Me pinned blue via config
`user_name` match — turn view previously showed NO speaker at all).

**D) Live speaker-bleed dedup (uncommitted):** duplicated live lines were the
SAME speech captioned by BOTH streams (laptop speakers → mic; "gonna" vs "going
to"). Cross-source token-Jaccard (≥0.55, 15 s window, exact match under 4
tokens) in `feed_live_source` with a shared `recent` ring; 3 unit tests incl.
the real incident pair. ⚠️ The FINAL transcript may have the same bleed via
`_merge_dual` — NOT yet addressed; check the next real meeting.

**NEXT (in order):** (1) user eyeballs the dynamic island + colors in dev →
commit the batch; (2) user-requested features, feasibility confirmed, ~half-day
each: per-meeting **sovereignty toggle** (App.tsx already derives
full/partial/none from config; needs per-meeting override into summarize) and
**pause/resume recording** (capture-level pause flag + elapsed bookkeeping +
island button); (3) notarized **0.3.62** for the sister. Gotchas: stuntman
worker is DOWN (DeepSeek upstream 402 Insufficient Balance — top up or switch
`STUNTMAN_MODEL`); `build-dmg.sh` comment claims auto-install but the code
defaults `ADVERSARIA_INSTALL` to 0 (one-line fix pending); two throwaway test
meetings from ~21:42/21:47 sit in the DB.

---

## Prior session (2026-07-24 evening — first-run "service not ready" fixed + Qwen 3.5 9B tier, pending 0.3.60 freeze)

**Also in this batch: SEAMLESS FIRST-RUN ENGINE SETUP** (user: the old flow
"will churn" — no manual download clicks or retries anywhere). Whisper models
are now pinned downloads (`whisper-main` = `mlx-community/whisper-large-v3-mlx`
@ `49e6aa28…` ~3.1 GB; `whisper-live` = `…-turbo-q4` @ `660c343b…` ~0.5 GB) that
auto-start when setup opens; the selected LLM auto-starts at the model step; one
combined progress bar spans model+sample steps; "Continue — downloads keep
running" never blocks; only Run-sample gates on the LLM verifying. Enablers:
`model_setup._load_manifest` accepts `weights.npz`; `setup::downloadable_profile`
allowlists whisper ids in both download commands; Welcome.tsx rework (early-start
+ auto-start + combined polling effects). Fresh-machine QA trick: test in a new
macOS user account (clean HF cache/app data) — no second computer needed.

**Also in this batch: third on-device model tier.** `qwen-9b-balanced` =
`mlx-community/Qwen3.5-9B-MLX-4bit` @ `938d8919941c6e7efd3c7150eff7fe9d12afa631`
(~6 GB, min 16 GB RAM) added to `setup.rs` (consts, `profile_alias`,
`pinned_snapshot`, three-tier recommendation: ≥24 GB→27B, 16–23 GB→9B, else 4B)
and `model_setup.py` `MODEL_PINS`. Display names now show the generation
("Qwen 3.6 27B", "Qwen 3.5 9B/4B"). Welcome + Settings pick the new tier up
automatically (they render `setup.profiles` dynamically). ⚠️ **"Qwen 3.5 Plus"
(user's ask) is API-only on Alibaba Cloud — no open weights** — so it can't be a
local profile; it works via the cloud-provider onboarding path instead. Verified:
`cargo test setup::` 4/4 · cargo check · 276 pytest · tsc · vitest 15/15.

**Field report from the first fresh-machine tester (sister's macOS-15 laptop):**
0.3.59 launched clean (the SCScreenshotConfiguration fix held), but the setup
wizard's **Download model** step errored **"The local setup service is not ready;
retry in a moment"** for minutes. Root-caused and fixed in the working tree
(**uncommitted**, awaiting the user's "ship it" for a 0.3.60 freeze):

- **Cause:** `python-service/src/server.py` `lifespan()` built and warmed the
  live-caption Whisper model synchronously; on a fresh machine the warm-up
  downloads `mlx-community/whisper-large-v3-turbo-q4` from Hugging Face **before
  uvicorn binds the port**, so every request was connection-refused until the
  download finished. The Rust `start_model_download` then surfaced the first
  connect error as the "not ready" message with no wait.
- **Fix (4 files, stuntman-implemented to spec, reviewed):**
  `server.py` lifespan → immediate `_live_transcriber = _transcriber` fallback +
  daemon-thread warm-up holding `_WHISPER_LOCK`; `http_client.rs` → new
  `wait_until_ready(max_wait)` polling `/health`; `commands.rs` →
  `start_model_download` waits up to 120 s before erroring; `Welcome.tsx` →
  status line "Starting the local engine — the first launch can take a minute…".
- **Verified:** 276 pytest ✓ · `cargo check` ✓ · `npx tsc --noEmit` ✓.
  Full postmortem in LESSONS_LEARNED.md (same date).
- **⚠️ Dormant until re-freeze:** the Python change ships only via
  `build-dmg.sh` (0.3.60). The 0.3.59 DMG on the sister's laptop still has the
  bug — workaround there: wait ~2–3 min after first launch, click Download again.

**NEXT ("ship it" received ~6:30pm):** 0.3.60 bumped + CHANGELOG + committed;
**DONE: 0.3.60 notarized (Accepted), stapled, Gatekeeper-verified; sidecar boot-tested from the .app (health in 14 s, whisper+9B pins answer). DMG sha256 be797c06… ready to AirDrop.** Built via `build-dmg.sh` (NOTARIZATION.md §4, beta channel,
`ADVERSARIA_ALLOW_INCOMPLETE_REGISTRATION=1`, `ADVERSARIA_INSTALL=0`) running.
After Accepted: verify staple/Gatekeeper/embedded frontend asset → **QA the full
first-run in a fresh macOS user account** (clean HF cache) → AirDrop to the
laptop. The rest of the 0.3.59 acceptance list (record→summarize, Settings
model picker) still applies. Also shipped last-minute: animated "Unfolding the
meeting model into memory…" warm-up panel with elapsed timer on the sample step.

---

## Prior session (2026-07-24 — Setup/model UX + auto-update fix, 0.3.58 committed)

**Two things this session, committed as release prep for 0.3.58 (NOT pushed;
notarized build is the user's to run — needs Apple secrets):**

**A) 🔴 Auto-update channel mismatch FIXED.** The whole auto-update chain already
existed (`UpdatePrompt.tsx` toast + `@tauri-apps/plugin-updater` +
`bundle.createUpdaterArtifacts` + `scripts/publish-release.sh` +
`LaghariLabs/adversaria-releases`), but was silently broken: installed **beta**
builds poll `.../releases/latest/download/latest-beta.json`
(`src-tauri/tauri.beta.conf.json`), while `publish-release.sh` wrote **`latest.json`**
— so a published update was never seen. Fix: `publish-release.sh` now derives
`ADVERSARIA_RELEASE_CHANNEL` (default `beta`, same as build-dmg.sh) and writes
`latest-${CHANNEL}.json`. Version bumped **0.3.57 → 0.3.58** + CHANGELOG.
**To push an update:** `build-dmg.sh` (RELEASE_MODE, see NOTARIZATION.md §4) →
`scripts/publish-release.sh "notes"` → installed copies show "Update available"
on next launch. To TEST the toast: install 0.3.58 on the new laptop, later
publish 0.3.59.

**B) 🟣 The "recommend, never force" model-selection UX** (SETUP_MODEL_UX.md),
directly (not delegated). Sibling to the still-open 🚨 8 GB perf launch-blocker.
⚠️ NOT dev-smoked — the new-laptop notarized test is its live smoke.

**C) 📄 Notarization runbook tracked.** The parallel session's
`docs/NOTARIZATION.md` (full Developer ID signing/notarization/stapling runbook)
is now committed and cross-linked from `docs/SPEC_DMG_PACKAGING.md`. All of the
above (0.3.58 code + docs) is **pushed to origin/master** (through `ac1ad36`).
Still untracked by choice: `.github/` (CI — needs `gh auth refresh -s workflow`),
`marketing/`, `video/`.

**NEXT (user, needs Apple secrets):** run the notarized `build-dmg.sh`
(NOTARIZATION.md §4) with the production Formspree endpoint →
`scripts/publish-release.sh` → install the 0.3.58 DMG on the new laptop. To demo
the update toast, later publish 0.3.59.

**D) 🚢 Product-notarization readiness (2026-07-24 ~4:30pm).** User asked to turn
the beta into a product build. Preflight (read-only, NOTARIZATION.md §3) is ALL
GREEN: Developer ID `4MY4PH5PHC` present, cert valid → 2027-02-01, Tauri updater
key present with a **matching** pinned pubkey, `adversaria-notary` profile
validates (prior Accepted). Version staying **0.3.58**; channel not yet chosen
(rec: build **beta** for this acceptance run, promote the accepted artifact to
stable at public launch — §8). **The one missing input is
`ADVERSARIA_FORMSPREE_ENDPOINT`** — it is NOT on this machine (0 hits in shell
history; no baked release binary). The user must fetch it from the **formspree.io
dashboard** (Forms → Adversaria form → `https://formspree.io/f/<id>`) or their
password manager. Once exported (`! export ADVERSARIA_FORMSPREE_ENDPOINT=…`),
Claude runs the full notarized build + `publish-release.sh`. Fallback offered:
build now with `ADVERSARIA_ALLOW_INCOMPLETE_REGISTRATION=1` (clean notarized
install; only the in-app beta sign-up queues) to test the laptop today.

**→ CORRECTION + DECISION (2026-07-24 ~4:45pm): Formspree is NOT required.** The
prior notarized 0.3.49/0.3.50 builds shipped with `ALLOW_INCOMPLETE_REGISTRATION=1`
and no endpoint baked (verified live — STATUS:341). So the "fallback" IS the
established method. **User said "go" → running the notarized 0.3.58 beta build now**
(`ALLOW_INCOMPLETE_REGISTRATION=1`, Developer ID + adversaria-notary, RELEASE_MODE=1,
ADVERSARIA_INSTALL=0). Formspree stays a separate, optional product concern (wire a
real endpoint later only if beta sign-ups should actually reach the inbox).

**→ BUILD STATUS (2026-07-24 ~5pm): notarized 0.3.58 beta build IN FLIGHT at
Apple.** All local stages passed clean (both sidecars frozen, ~650 Mach-O signed
under Developer ID, app "valid on disk", DMG built + signed = **748 MB** at
`src-tauri/target/release/bundle/dmg/Adversaria-0.3.58-beta-macos-arm64.dmg`).
Uploaded to Apple notary — submission id `05215225-a421-4f7d-8618-2d3b4d9872ee`,
status **In Progress** (`build-dmg.sh` is `--wait`-ing; log at
`scratchpad/build-0358.log`). **When Apple returns Accepted**, the script
auto-staples + runs `spctl` Gatekeeper + writes provenance, then exits.
**RESUME steps if the session drops before it finishes:**
1. `xcrun notarytool info 05215225-a421-4f7d-8618-2d3b4d9872ee --keychain-profile adversaria-notary` — check Accepted/Invalid.
2. If Accepted but not stapled: `xcrun stapler staple <dmg>` → `xcrun stapler validate <dmg>` → `spctl --assess --type open --context context:primary-signature -v <dmg>` (expect `accepted / source=Notarized Developer ID`).
3. Publish so the update toast works: `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh "0.3.58 — model picker, simpler setup, update-channel fix"`.
4. AirDrop the DMG to the new laptop → clean-Mac acceptance (NOTARIZATION.md §5.3, download via real path, NO xattr bypass).
5. To demo the "Update available" toast later: publish a 0.3.59.

**→ ✅ DONE (2026-07-24 ~5:15pm): 0.3.58 notarized, stapled & Gatekeeper-verified.**
Apple **Accepted** (job 05215225…); `spctl` = accepted / source=Notarized
Developer ID; `stapler validate` ok; app version 0.3.58. **Notarized DMG (748 MB,
sha256 `6a46ddcc9513a57cc9601e13f6de714718fc8668d4fccdbea6cc3dcdb9312a45`):**
`src-tauri/target/release/bundle/dmg/Adversaria-0.3.58-beta-macos-arm64.dmg`.
**NOT published yet — on purpose:** acceptance-test on the new laptop first
(install via the real download path, no xattr; verify the Settings model picker +
record→summarize), THEN `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh`
so an untested build never auto-pushes to existing beta testers. **Next action is
the user's:** AirDrop the DMG to the new laptop and run the acceptance test.

**E) 🔴🔴 0.3.58 CRASHED AT LAUNCH ON macOS 15 → FIXED → 0.3.59 (~5pm).** The
notarized 0.3.58 installed fine (Gatekeeper accepted) but **crashed instantly** on
the new laptop (macOS 15.7.3): `Symbol not found:
_OBJC_CLASS_$_SCScreenshotConfiguration` (dyld, terminated at launch — not a
signing problem). Root cause: `src-tauri/Cargo.toml` set `screencapturekit
features=["macos_26_0"]`, which strong-links a macOS-26-only ScreenCaptureKit class
that's absent on macOS 15 → dyld aborts before any code runs. **Latent in every
recent build**; surfaced now only because this is the first macOS-15 test Mac (all
earlier testers were on macOS 26). **Fix:** capped the feature at the deployment
target — `features=["macos_14_4"]` (we only use base SCStream audio; nothing lost).
Verified: `cargo check` ✓ and `nm -m` shows the strong `SCScreenshotConfiguration`
ref is **gone**. Bumped 0.3.58 → **0.3.59** (CHANGELOG + LESSONS_LEARNED top entry).
The 0.3.58 DMG is discarded (never published). **NEXT: re-run the notarized build
for 0.3.59 → retest launch on the macOS-15 laptop.** ⚠️ Test releases on a Mac at/
near the minimum OS (14.4), never only the newest-OS build machine.

**→ ✅ 0.3.59 NOTARIZED + FIX VERIFIED (2026-07-24 ~5:30pm).** Rebuilt: Apple
**Accepted**, stapled, Gatekeeper accepted. **The fix is confirmed in the SHIPPED
binary** — `nm -m Adversaria.app/Contents/MacOS/meeting-note-taker` shows
`SCScreenshotConfiguration` gone; all remaining strong SC* refs are base macOS-12.3+
classes → launches on macOS 15.7.3. **DMG (751 MB, sha256
`5ce03baf866881eec15db2e154a2c9836ae95036cfe0bcf6ad18831732054b89`):**
`src-tauri/target/release/bundle/dmg/Adversaria-0.3.59-beta-macos-arm64.dmg`.
**Next action is the user's:** AirDrop the 0.3.59 DMG to the macOS-15 laptop and
confirm it **launches** (the thing that was broken), then run acceptance (record →
summarize → verify the Settings model picker). On pass →
`ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh` to wire the update
toast. Still NOT published.

- **Reqs 1+3 — simple setup (`Welcome.tsx`):** the local model step leads with
  ONE recommended card + RAM-reasoned copy; the other pinned profile moved
  behind a quiet "Change model" `<details>` (was two co-equal radio cards).
- **Req 4 — Settings model picker (`Settings.tsx`):** new "On-device meeting
  model" list in Settings › AI Engine, shown for the **Local** engine only and
  gated on `setup.rapid_runtime_bundled` (so Windows/Ollama users keep the
  free-text model field). Marks the recommended + the "In use" profile; per-row
  **Use / Download / Retry** with live download progress (reuses
  `start_model_download` + polling).
- **Rust:** new `set_local_model_profile` command (`commands.rs`) —
  `pinned_snapshot()` guards that the target is installed *before* stopping the
  running model → persists via new `registration::set_selected_model_profile`
  (updates `selected_model_profile` + `ollama_model=alias` + `llm_provider=local`
  but, unlike `complete_step`, **never writes `setup_complete`**) → stop+start
  managed Rapid-MLX. `configured_llm_base_url()` reads `managed_credentials()`
  fresh per request, so the switch takes effect **without an app restart**.
  Registered in `lib.rs`; TS wrapper `setLocalModelProfile` in `tauri.ts`.
- **Key architecture facts confirmed while building:** the macOS local path is
  **Rapid-MLX serving pinned MLX profiles** (`qwen-27b-quality` / `qwen-4b-light`
  = the EXP-3 8 GB winner), NOT Ollama; `complete_step` already sets
  `ollama_model` to the served alias, so the local model name always matches.
- **Verified by Claude:** `tsc` ✓ · `cargo check` ✓ · `cargo test --lib` 132 ✓ ·
  `vitest` 15 ✓. NOT live-smoked in `tauri dev` (needs the managed model +
  a real summary) and NOT committed.
- **DEFERRED (user-decided): req #2** — detect + reuse models the user already
  pulled via **Ollama** (`/api/tags`) to skip the multi-GB download. This is a
  cross-runtime fork (route the summarizer to Ollama at `127.0.0.1:11434`
  instead of Rapid-MLX) and needs the "localhost ≠ cloud" provider-warning fix.
  Scoped as the next pass.
- **NEXT:** user dev-smoke (switch 4B↔27B in Settings, confirm a local summary
  uses the new model with no restart), then commit + refreeze.

## Previous session (2026-07-09 — hybrid Ask RAG BUILT via stunt-worker delegation)

**UPDATE (same evening): ✅ SHIPPED & VERIFIED. Committed `d363aeb` (v0.3.30,
22 files, CHANGELOG + version bump per the ship ritual), then the signed
`build-dmg.sh` freeze (`ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev"`)
installed + relaunched `/Applications/Adversaria.app`. Verified live:
Info.plist **0.3.30** · `Authority=NotchyPrompter Dev` · frozen sidecar
`/health` ok (:54695, large-v3, ollama up) · frozen **`/embed` answered
(bge-m3, dim 1024)** · `ollama ps` showed bge-m3 freshly used ≈1 min after
relaunch = the startup backfill embedded the real corpus. NOT pushed
(`a77396d` + `d363aeb` local-only); push on the user's word.**

**Ask-tab retrieval upgraded keyword-only → hybrid (FTS5 + semantic vectors +
graph anchoring, RRF-fused). Implemented, all tests green** —
originally pending the user's dev smoke, then shipped directly on their call. Built exactly to the 2026-07-06 research verdict
(TODO.md §"Ask-tab RAG upgrade research"): vectors fix the synonym gap
("trading bot" ≈ "algorithmic trading agent"), the existing metadata graph
answers person/tag-scoped asks ("what did I discuss with Basim"), explicitly
NOT GraphRAG. 100% local; the UI contract is untouched (zero frontend changes).
- **How it was built:** user directive — Claude plans/specs/reviews only, the
  stunt worker codes. 3 spec'd delegations + 1 review round (~$11.5 worker
  cost, zero Anthropic credits). Every diff reviewed; every verification
  re-run by Claude, not trusted from the worker.
- **Python** (`src/embedder.py` NEW, `server.py`, `models.py`,
  `tests/test_embedder.py` NEW): `POST /embed` batch endpoint → Ollama
  **bge-m3** (1024-dim, strongest practical Arabic retrieval; `EMBED_MODEL`
  env override). 503 with an "ollama pull bge-m3" hint when missing. The
  embedder is independent of the summarizer backend (this Mac: LLM =
  Rapid-MLX/openai, embeddings = Ollama :11434). **187 pytest.**
- **Rust index** (`embeddings.rs` NEW; `storage.rs`, `http_client.rs`,
  `types.rs`, `lib.rs`): meetings chunked (~1.5 KB — grouped transcript turns
  + summary sections, title-prefixed, char-boundary-safe for Arabic) →
  embedded → LE-f32 BLOBs in new `meeting_chunks` + `chunk_index_state`
  tables (SQLCipher, delete-cascade wired). `sync_index` is **self-healing**
  (fingerprint + model-probe staleness, AtomicBool+RAII concurrency guard)
  and fires: at startup (3 attempts, 20 s/90 s/90 s), after every
  transcribe / import / re-summarize / structure-note, and on each Ask.
- **Rust retrieval** (`commands.rs`): new `retrieve_meetings_hybrid` = RRF
  (k=60) fusing FTS5 (w 1.0) + per-chunk cosine (w 1.0, ≥ 0.30 gate) +
  attendee/tag graph anchors (w 1.5, "me/them/speaker N" + generic tag labels
  stoplisted); falls back to the legacy keyword ranking when every layer
  misses. `build_grounded_context` now grounds **detail** answers in the
  MATCHED chunks (joined with `[…]`) instead of the transcript's first
  4 000 chars. Todos fall-down path deliberately unchanged.
- **Verified:** cargo **81** · pytest **187** · `tsc` clean · live `/embed`
  over HTTP on a throwaway :9877 service (bge-m3, dim 1024) · cross-lingual
  sanity: cosine("hello world", "مرحبا بالعالم") = **0.879**. NOT yet
  smoke-tested inside `tauri dev` (needs both processes + a real Ask).
- **Prereq on any box: `ollama pull bge-m3`** (~1.2 GB — DONE on this Mac).
  Without it the vector layer silently stays off and Ask behaves exactly as
  before (by design, not an error).
- **NEXT STEP:** (1) user smoke in dev — Terminal 1 `uv run uvicorn
  src.server:app --port 9876`, Terminal 2 `npm run tauri dev`; ask a
  synonym-flavored question + a person-scoped one; watch stderr for
  `[embeddings] indexed N meeting(s)` (first backfill embeds the whole
  corpus, ~seconds). (2) Commit on the user's OK (13 files). (3) Re-freeze
  via `ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev" ./scripts/build-dmg.sh`
  to ship it into /Applications — the frozen sidecar must be rebuilt for
  `/embed` to exist there.
- **Also this session:** committed the launch-video SOURCE per the user's
  pick — `a77396d` (local, NOT pushed): `marketing/launch-video/index.html`
  + vendored assets tracked; `renders/`, `snapshots/`, `render.log`
  gitignored. Stray untracked `src-tauri/src/http_client 2.rs` (Finder-dup,
  gitignored by pattern) noticed — left alone, safe to delete manually.
  Correction to the 2026-07-08 note below: `ce0888a` IS on origin (a later
  session pushed it).

**Later same day — "Chat with meeting" incident root-caused + Task D fixes
(uncommitted, same stunt-worker flow).** User's chat about a ~15.4k-token
interview transcript: Q1 ("how did Hamza do?") got a grounded refusal; Q2
(re-ask) and Q3 ("what questions were asked") got NO answer at all.
Diagnosis from `/tmp/adversaria-llm.log`: **Rapid-MLX 0.6.11 aborted both
in-flight requests** ("[generation_error_recovery] aborted 2 running
requests" at `running=2` — Q3 fired while Q2 was still prefilling; switching
tabs mid-stream keeps a request running server-side, so overlap is easy).
NOT truncation — the full 15.4k prompt prefilled fine. The identical Q2
"answer" was just the persisted Q1 message re-read from history
(temperature 0.0 → deterministic). Two product gaps fixed as **Task D**:
1. **Silent empty stream:** an aborted SSE that closes token-less made
   `/chat_stream` emit a clean `[DONE]` → empty bubble, no error. Now:
   zero-token stream → **one automatic retry** (the LLM server recovers right
   after clearing its batch) → still empty → SSE `error` frame ("returned an
   empty answer… please try again"), which the UI already renders. Non-stream
   `chat()` raises on empty answers too.
2. **Evaluative questions:** the grounded prompts (single-chat
   `_chat_messages` + Ask `build_answer_question`) now permit
   analysis/evaluation/opinion **grounded solely in the transcript**,
   presented as a reading, not fact. Live-verified on a synthetic interview
   via `/chat` on :9877 — model returned a cited assessment ("technically
   strong but behaviorally underdeveloped") instead of "I don't know".
- Worker D: 1 exec, $1.46, zero iterations. pytest **191** · cargo **82** ·
  tsc ✓ (all re-run by Claude).
- ⚠️ **None of this reaches the installed app until a signed re-freeze** —
  the chat prompt + stream retry live in the FROZEN sidecar. Until then:
  don't fire a second chat while one is generating; a hung question can just
  be re-asked (the server self-recovers).
- Upstream (user's call): the rapid-mlx batch-abort is an upstream bug;
  `brew trust raullenchai/rapid-mlx && brew upgrade rapid-mlx` may pick up a
  fix (tap is untrusted since brew's trust change, so Claude left it).

**Task E (2026-07-09, late) — Ask sources now cite what the answer USED.
✅ SHIPPED & VERIFIED as v0.3.31: committed `836565d` (version bump +
CHANGELOG per ritual), signed freeze installed + relaunched. Verified:
Info.plist 0.3.31 · Authority=NotchyPrompter Dev · sidecar /health ok · the
SOURCES-citation prompt string grep-confirmed inside the installed binary.
✅ PUSHED on the user's word: `6cbb31c..dd8f33d` → origin/master (the whole
day's seven commits — video source, v0.3.30, docs, README, rationale,
v0.3.31, finalizer). master == origin.**
User hit it live: "who likes black coffee?" answered from ONE meeting but
showed FIVE "📄 Reference Note" sources. Cause: `sources` was always the full
top-5 retrieval candidate list, never a citation — and the new semantic layer
reliably fills all 5 slots (pre-hybrid FTS often matched fewer, hiding the
padding). Fix (stunt worker, spec'd/reviewed by Claude, `commands.rs` only):
context sections numbered `## [n] title (date)`; answer prompt requires a
trailing `SOURCES: 1,3` / `SOURCES: none` line; `split_cited_sources` strips
+ parses it (tolerant, and strips even garbage payloads);
`filter_sources_by_citation` dedupes and filters — **failing open to the full
list** when the model ignores the instruction or miscounts, so behavior can
never get worse. Applied to the two grounded-answer paths only (todos/recap
sources are already authoritative). cargo **95** · pytest 191 · tsc ✓.
NOTE: the trailing-SOURCES protocol only works reliably at temperature 0
with the fail-open guard — the frozen sidecar does NOT need changes (this is
all Rust), so a `tauri dev` smoke works for this one; still needs a
re-freeze only because the .app binary embeds the Rust code.

**Embedding-backend rationale (user asked "why Ollama, not Rapid-MLX/MLX?",
2026-07-09 late):** Ollama never left the stack — it's the Windows LLM
backend, a stated prerequisite, and the `ollama` client was already a service
dep, so /embed added ZERO new deps / freeze risk and works identically on
both OSes; bge-m3 runs 100% GPU (Metal) under Ollama anyway. **Live-probed
correction:** Rapid-MLX DOES expose `/v1/embeddings`, but only with the
optional extra (`pip install 'rapid-mlx[embeddings]'` — replied exactly that;
not installed in the brew-managed instance). Consolidating embeddings onto
Rapid-MLX later is a two-way door: everything sits behind the service's
`POST /embed` + `EMBED_MODEL`, and the Rust index's model-probe staleness
auto-reindexes the corpus on any backend/model switch. Declined for now
(consolidation aesthetics only, no perf win; Windows would still need the
Ollama path).

## Previous session (2026-07-08, later #2 — launch video via HyperFrames)

**Built our OWN product launch video from scratch** (user is A/B-testing agents —
another session's attempt lives in untracked `video/`; DO NOT reuse it). Current
output: `marketing/launch-video/renders/adversaria-launch-v2.mp4` — **63s,
1920×1080, 60fps, silent, 12.7 MB** (v1 `adversaria-launch.mp4` = the earlier 51s
cut). Delivered to the user; not committed.
- **v2 changes (user feedback):** bigger fonts throughout + TWO new scenes —
  **Import audio** (`import_audio` cmd: drop a .m4a/.mp3/.wav → transcribed locally;
  "inserting audio clips" meant THIS, not the video's soundtrack) and **MCP for AI
  agents** (the read-only open-source MCP server — an agent asks "what did we decide
  in the client call?" answered on-device) + a clearer **Share** scene (export
  slides + hand a teammate a `.adversaria.json` bundle). Now 11 scenes.
- **⚠️ RENDER-BROWSER GOTCHA (burned ~1h):** `npx hyperframes` auto-updated
  0.7.42→0.7.44 mid-session; 0.7.44 insists on a managed `chrome-headless-shell`
  download that hung at ~98 MB. Interrupting it left a PARTIAL cache (folder exists,
  exe missing) which then made even a pinned `hyperframes@0.7.42 render` fail with
  "Chrome not found" instead of falling back to system Chrome. **Fix:**
  `npx hyperframes@0.7.42 browser clear` (nukes the partial) → `browser ensure`
  reports `Source: system → /Applications/Google Chrome.app` → render works. Also:
  a stale `hyperframes preview` server (the other agent's, on port 3003) blocked
  renders by holding the shared Chrome profile — `hyperframes preview --kill-all`.
  Pin the version (`hyperframes@0.7.42`) to avoid the auto-update.
- **Tool:** HeyGen **HyperFrames** (`npx hyperframes`, v0.7.42, Apache-2.0) — writes
  animated HTML → deterministic MP4 via headless Chrome + FFmpeg, **fully local**.
  Env was already ready (Node 26, FFmpeg 8.1, Chrome). CLI works without installing
  the agent "skill". Contract: root needs `data-composition-id/-start/-width/-height/-fps`;
  duration comes from a paused GSAP timeline at `window.__timelines[id]`.
- **Source:** `marketing/launch-video/index.html` (single file, hand-written CSS +
  GSAP, **no CDN** — vendored `assets/gsap.min.js` + local Instrument Serif from
  `public/fonts/`, so the render is offline/on-brand). 8 scenes anchored on
  **"Sovereign First"**, positive, **no competitor names**: brand intro → Sovereign-First
  + on-device architecture → record→smart-notes card → Ask (single + cross-meeting) →
  to-do compiler → knowledge graph → slides + team-share → outro. UI is **recreated
  faithfully in legible HTML** using the app's real tokens (`src/index.css`: azure
  `#24A0ED` wordmark, `#007aff/#af52de/#34c759/#ff9500`) — NOT screenshots.
- **⚠️ The other agent's `video/` screenshots are AI-generated fakes** with garbled
  text ("descuss ornen meeting noeting contacles"). Don't use them anywhere.
- **Workflow that worked:** `hyperframes lint` (caught GSAP/CSS transform conflicts,
  missing `data-start`, overlapping tweens) → `hyperframes validate` (headless-Chrome
  JS/asset check) → `hyperframes snapshot --at <times>` (writes a `contact-sheet.jpg`
  to eyeball all scenes) → `hyperframes render`. Render = 1m9s (6 workers, static-dedup).
- **OPEN — two user decisions:** (1) **Music** — cut is silent; drop a track at
  `assets/music.mp3` and re-render, OR source a CC0 track (licensing matters — it's a
  publishable asset). HyperFrames `beats` can sync cuts to music. (2) **Git** — the
  whole `marketing/launch-video/` tree is untracked; commit only on user's say-so.

## Last session (2026-07-08, later — housekeeping)

**Doc housekeeping only, no code.** Committed as `ce0888a` (local, NOT pushed).
- Committed `docs/DEEP_DIVE_BUSINESS.md` + `docs/DEEP_DIVE_TECHNICAL.md` — these
  companion docs (written 2026-07-02) are listed in CLAUDE.md's doc table but had
  never been added to git, so the table pointed at phantom files. Now tracked.
- Gitignored the `/llm-council` output pattern (`council-report-*.html`,
  `council-transcript-*.md`) in root `.gitignore`. The stale 2026-06-26 roast
  artifacts remain on disk (untracked + ignored); safe to delete anytime.
- **Next step unchanged:** awaiting the user's pick between the two teed-up
  initiatives — Ask-tab RAG upgrade (hybrid vector+graph+FTS, researched, verdict
  recorded) and Windows packaging (runbook ready in "Building the Windows app"
  below; carries the 🔴 MLX-only Whisper-picker port fix). `ce0888a` is unpushed.

## Previous session (2026-07-08)

**SHIPPED v0.3.29 — slide-export intro three-line branding.** `exportDocument.ts`:
added `.intro-sub` "A Laghari Labs Product" between the "Adversaria" wordmark
and the accent rule (muted uppercase, matches the app splash's subtitle), and
changed the tagline "Nothing left your machine" → "Nothing leaves your machine".
Verified the three lines + styling via a headless DOM check. tsc green.

## Previous session (2026-07-06, late evening)

**SHIPPED v0.3.28 — UI polish the user asked for.** tsc · cargo · 55 tests.
- **Wider layouts:** `.todos-layout`/`.weekly-layout` 900→1400px,
  `.ask-layout` 760→1200px (padding 30px→30px 48px) in `prototype.css` — the
  three tabs were narrow+centered with big blank side margins on wide displays.
- **Date format setting:** new `date_format` config (`system|dmy|mdy|long|iso`,
  default system) + Settings dropdown with live preview. New
  `src/lib/dateFormat.ts` (`setDateFormat`/`formatDate`/`formatDateTime`/
  `dateLocale`, module-level preference set on config load in App.tsx + on
  Settings change/save). Converted display sites: MeetingsList card date,
  NoteViewer header, Settings token-expiry, slide export (`exportDocument.ts`),
  TodosView due badge + recorded date, WeeklyView range. Internal `en-CA`
  date-KEYS (heatmap, filters) left untouched. dmy=06/07/2026, long=6 July 2026.

## Previous session (2026-07-06, evening #2)

**SHIPPED v0.3.27 — two fixes.** (1) **"Structure with AI" bug** (`commands.rs`
`structure_note`): a note's `template_used` is the pseudo-value "note", passed
straight through → "Prompt template not found: note". Now filtered → falls back
to "brainstorm". (2) **Slide intro reworked to match the APP splash** (the
cursive v0.3.26 looked stretched): wordmark is now "Adversaria" in Instrument
Serif italic, solid azure #24A0ED — the app's exact splash font/colour — with a
gentle fade-up (no cursive, no gradient, no stretch). Font embedded as base64
(`src/lib/instrumentSerifFont.ts`, 71 KB TTF → data URI in `@font-face`) so the
self-contained slide HTML/PDF renders it identically offline. Verified via a
headless Playwright render of the frozen state. tsc + cargo green.

## Previous session (2026-07-06, evening)

**SHIPPED v0.3.26 — slide-export intro splash reworked (tsc green; verified via
Playwright render).** `exportDocument.ts`: the "ADVERSARIA" reveal (white "ADVER"
+ azure "SARIA" sliding in) is now the single wordmark "Adversaria" in a flowing
cursive script (Snell Roundhand → Apple Chancery → Georgia-italic fallback) that
writes itself in left-to-right via a `clip-path` inset reveal (A first), filled
with one dark→light blue gradient (`#1f6fe0 → #5b9bff → #d0e4ff`) via
background-clip:text. Screen-only (hidden in print, unchanged). Rendered the
frozen state headless to confirm the cursive + gradient before shipping.
**Also investigated (no code change) — slide "squishing":** it's content-driven,
not a regression. The `fitContent()` script shrinks the body font from 15px down
toward 8px until it fits the fixed 1280×720 one-page frame, so a long YouTube
summary (~30 bullets, esp. a 15-bullet Key Points section that can't split across
columns — `break-inside:avoid`) renders smaller/denser and lopsided. Risk noted:
past the 8px floor content clips (overflow:hidden). Fix deferred (user asked to
investigate only).

## Previous session (2026-07-06, midday)

**SHIPPED v0.3.25 — note-feature enhancements (user picked "Structure with AI" +
"Templates & quick capture").** 55 cargo · 178 pytest · tsc.
- **Structure with AI** (`commands.rs::structure_note` + `tauri.ts` +
  NoteViewer button, shown when `template_used=="note"` or the meeting has a
  "Note" tag): runs the note body through `summarize` (brainstorm template
  default), preserves raw text in `transcript`, writes structured notes to
  `summary` via `update_meeting_transcription`, extracts action items
  (`sync_actions_for_meeting`) and re-exports second-brain. Notes now feed
  To-dos/graph/Ask like meetings. Keeps existing tags (doesn't recategorize).
- **Note templates** (`NewNoteButton.tsx`): Blank / Meeting prep / Daily
  standup / Idea dump starter scaffolds pre-fill title+body.
- **Quick capture** (`tray.rs`): global **Cmd/Ctrl+Shift+N** focuses the window
  and emits `hotkey-new-note`; NewNoteButton listens and opens the modal.

## Previous session (2026-07-06, late morning)

**SHIPPED v0.3.24 — three enhancements the user asked for (committed + signed freeze).**
55 cargo · 178 pytest · tsc.
1. **LLM-driven category** — `MeetingNotes` schema gained a `category` field;
   the summarizer LLM classifies from content (meeting/one_on_one/interview/
   standup/brainstorm/youtube/other). `resolve_category(hint, llm, heuristic)`
   precedence: mic-bleed youtube hint > LLM > ratio heuristic. Rust
   `category_tag` extended (1:1 green, Interview orange, Standup yellow).
2. **Ask "trading bot" refusal fixed** — router prompt now treats a bare
   topic/name as a search (not a coding command) + example; `looks_like_injection`
   guard + FTS retrieval safety net in `ask_all_meetings`: a refused query that
   full-text-matches a real meeting is answered as detail (injections still refuse).
3. **Ask background processing** — the Rust command already runs to completion
   after the tab unmounts and persists both turns; AskAllView now RECONNECTS on
   mount (detects a dangling user turn, polls getAskConversation ~90 s) so a
   returning user sees the background answer. Main + todos answer paths persist a
   friendly assistant turn on LLM error (no more hang-forever).

**Parakeet spike → SKIP** (no Arabic; slower than whisper-large-v3-turbo which we
already have). Actionable free win recorded in TODO.md: flip macOS default to
`whisper-large-v3-turbo` (~7-8× faster, 100 langs) — needs the user's Arabic
quality check first.

**Item still OPEN — note-feature enhancements (user asked me to SUGGEST):**
current `create_note` is a plain text box (body stored as summary, "Note" tag),
disconnected from the app's AI/to-dos/graph. Recommended: a "Structure with AI"
button that runs the note through the summarizer → structured notes + extracted
action items (makes notes first-class in To-dos/graph/Ask). Awaiting user's pick.

## Previous session (2026-07-06, morning ctd)

**Second-Brain export SHIPPED as v0.3.23.** New `src-tauri/src/second_brain.rs`:
mirrors meetings into a user-chosen local folder as markdown notes — OKF-style
YAML frontmatter (`type/title/timestamp/tags/attendees/link/resource`) +
`[[wikilinks]]` for attendees/tags — plus `index.md` and `graph.json`
(the Graph tab's exact `build_graph` output). Scope decisions: meetings-only,
SUMMARY-only (raw transcripts never leave the app), locked meetings excluded,
off by default. Orphan sweep only deletes files containing the
`adversaria://meeting/` marker — user-authored notes are untouchable. Auto-sync
(`sync_async`, background thread, config-gated) hooked into every meeting
mutation (transcribe both paths, resummarize, create_note, imports, tag/
attendee/notes/link/summary edits, lock, delete, merge-speakers); manual
`export_second_brain` command + Settings → Data → "Second Brain" (path field,
auto toggle, Export now). Config: `second_brain_path` / `second_brain_enabled`.
4 new Rust unit tests (filename slugging incl. Arabic, transcript-never-exported,
YAML escaping). **Parakeet spike** running in a background agent (benchmark
vs mlx-whisper, scratch-dir only) — report lands separately.

## Previous session (2026-07-06, night)

**SHIPPED as v0.3.22 (2026-07-06 morning, committed + signed re-freeze):** the
category-hint chain below PLUS the full small-audit-bug sweep (empty-capture
stop error, backslash relabel lambda, `update_config_with` serialized config
cycles, mkstemp import tempfile, Ask user-turn persisted up front, UTC-normalized
import timestamps, MeetingChat unmount guards, placeholder-bullet checkbox fix).
174 pytest · 49 cargo · tsc. Remaining accepted items listed in TODO.md.

**Round 2 on video classification:** a new watched
video (meeting #97) classified "meeting" — containment scored **0.79 vs the 0.8
threshold**, because v0.3.18's own `strip_mic_bleed` removed the verbatim bleed
lines that used to push videos to ≥0.9; the survivors were partial fragments +
a vocab hallucination ("Tatweer OS, Claude, Hira" as a mic line — noted, not yet
fixed). Threshold games are over: **classification now happens at TRANSCRIPTION
time, pre-strip** — new `playback_hint()` in `transcriber.py` runs
`classify_category` on the raw channels (bleed intact → signal overwhelming) and
the verdict travels as `category_hint` through `TranscribeResponse` →
`commands.rs` → `/summarize` → `summarizer.summarize(category_hint=…)`, which
overrides transcript-based classification. A "youtube" hint also skips
diarization directly. Meeting #97 retagged YouTube in the DB. 173 pytest ·
49 cargo · tsc green. Also queued-but-paused: the small-audit-bug sweep
(backslash relabel crash, empty-capture dangling WAV, config race, import
tempfile leak, ask-turn drop, non-UTC sort, MeetingChat unmount, placeholder
checkbox shift) — interrupted by this regression.



**VAD-gated live captions BUILT (UNCOMMITTED, pending ship as v0.3.21) — the
"#1 steal" from the Meetily research, adapted to our architecture.** tsc ·
49 cargo · **168 pytest (8 new)**. Replaces the rolling 30 s window
re-transcribed every 12 s (redundant compute, mid-word cuts) with
**transcribe-each-utterance-once**:
- **Python** — new `src/live.py`: `LiveCaptionSession` buffers 16 kHz mono
  audio across delta feeds; **Silero VAD** (bundled with faster-whisper 1.2.1,
  `silero_vad_v6.onnx`, already `collect_all`'d into the freeze — zero new
  deps) segments it with Meetily's field-tuned constants (threshold .5 /
  neg .35 / redemption 2000 ms / min-speech 250 ms / pad 300 ms); pure
  `completed_utterances()` picks utterances with ≥2 s trailing silence or
  force-cuts at 30 s (monologues still caption); each is transcribed ONCE
  under `_WHISPER_LOCK` (non-blocking: busy → watermark holds, captions catch
  up next feed, nothing lost). New `/live_feed` endpoint (`session` = Rust
  recording epoch; new epoch resets state).
- **Rust** — `audio::snapshot_since` (append-only buffer ⇒ stable byte
  offsets) streams only NEW audio; caption loop polls every **2 s** (was 12),
  sends deltas, emits one `live-transcript` event **per finished utterance**;
  epoch doubles as the service session id. Orphaned `snapshot_tail` removed.
- **Frontend** — captions APPEND (last 6 lines, `pre-line`) instead of
  replacing; panel relabeled.
⚠️ Dormant until a re-freeze (frozen-sidecar rule) — ship as v0.3.21 to test
live. Latency now = utterance end + ~2 s redemption + inference (vs up to 12 s
before), and silence costs zero Whisper inference.

**Also saved (user-directed):** the Meetily research verdicts live in TODO.md —
VAD captions (this work), audio-mixing hygiene (persistent resampler /
ring-buffer alignment / soft-clip; mostly N/A to us until we mix or resample in
Rust — revisit if artifacts appear), Parakeet spike later, diarization: keep ours.

---

## Previous session (2026-07-04)

**2026-07-05/06 additions (same pending v0.3.20 batch):** (1) **"From Your
Notes" summary section** — user's jotted notes reached the model but dissolved
invisibly (verified on meeting #92: title + one takeaway were influenced, but
nothing visibly theirs); the USER NOTES prompt directive now demands a
dedicated final section, one bullet per note, transcript detail only where it
exists (`summarizer.py` + prompt test). (2) **Per-meeting source link** —
`link` column (migration + insert/select/update `update_meeting_link`),
`Meeting.link` both sides, in export/import bundles, NoteViewer row under
attendees ("+ Add link" → paste → clickable 🔗, opens via the shell plugin;
auto-capturing the browser URL was ruled out: needs per-browser Automation
permission, brittle). (3) **Header font mismatch** — "Local ML Service" line
now `fontWeight: 600` matching the sovereignty pill (both were fontSize 11,
weight differed).

**Late-morning batch (2026-07-04 ~11am) — the 4 biggest remaining audit bugs
FIXED, SHIPPED with the additions above as v0.3.20 (2026-07-06, committed +
signed re-freeze).** tsc · 49 cargo · **160 pytest (3 new)**.
- **Event-loop blocking (the #1 audit item, `server.py`):** `/health`, `/chat`,
  `/transcribe`, `/transcribe_chunk`, `/summarize` are now sync `def`
  (threadpooled); local Whisper inference + the per-request transcriber
  mutation (vocab prompt, MLX model repo) are serialized by a module
  `_WHISPER_LOCK`; `/transcribe_chunk` skips (empty text) instead of queueing
  when the lock is busy. Regression tests include an end-to-end "/health
  responds while /transcribe is blocked mid-inference". Live captions, chat,
  and the health pill stay responsive during long jobs now.
- **Live-caption task leak (`commands.rs`):** `LIVE_CAPTION_EPOCH` atomic —
  stale loops from a stop→start-within-one-poll-window exit at next wake;
  per-epoch temp filenames end the shared-file race.
- **Wrong-meeting race (`useMeetings.ts`):** latest-wins ref guard on
  `selectMeeting`; superseded fetches dropped.
- **Auto-stop silence clock (`App.tsx`):** no longer resets on tab switches
  (autoStop object identity preserved when values unchanged).

**Morning batch (~10:30am) — UX fixes + YouTube template SHIPPED as v0.3.19
(committed + signed re-freeze).** tsc · 49 cargo · 157 pytest green.
- **Browse meetings while recording** (`App.tsx`): the content pane no longer
  hard-locks to RecordingNotes — selecting a meeting shows it with a red
  "● Recording in progress — back to live notes" strip (clears selection to
  return). Recording start clears the selection so the live pad appears.
- **Auto-relock** (`App.tsx`): `unlockedIds` was session-scoped — once unlocked,
  a locked meeting stayed open until app restart. A new effect keeps only the
  currently-open meeting unlocked; navigating away re-arms the lock.
- **New `youtube` prompt template** (`python-service/prompts/youtube.md`):
  What It's About / Key Points / Tools & References / Takeaways; attendees
  forced empty (video presenters must not pollute the graph). Discovered
  dynamically — appears in dropdowns after re-freeze.
- **Two audit quick-fixes:** resummarize now reloads action items (stale
  dead-row checkboxes), and `open_keyed` sets a 5 s SQLite busy timeout
  (kills "database is locked" races). Both were 🔴 in the 2026-07-03 audit.

**Follow-up (~1:45am) — mic-bleed misclassification FIXED, SHIPPED as v0.3.18
(committed + signed re-freeze; meeting #90's stored transcript deduped + retagged
YouTube in the DB with a backup, user to Regenerate Notes):** user's watched
video (meeting #90, "AIS Live: Building and Sharing
LLM Wikis", recorded pre-v0.3.17) classified "meeting" and attributed the
video's words to Hamza. Root causes, verified against the real stored
transcript: (1) the mic caught only ~29% of the playback, so the bleed check's
**Jaccard** overlap maxed at 0.33 (<0.5) — switched to **containment**
(|me∩them|/|me| ≥ 0.8, ≥8 words; corpus-calibrated over all 90 meetings: every
known video ≥0.83, highest real meeting 0.75) in `classify_category`;
(2) new `strip_mic_bleed()` in `transcriber.py` drops mic segments that are
near-verbatim copies (SequenceMatcher ≥0.85, ±10 s, ≥4 words) of system
segments BEFORE merging — kills the duplicated lines and the "user said the
video's words" attribution at the source (both dual paths). Meeting #90's
transcript now classifies "youtube" (reproduced + verified). 157 pytest (9 new).

**Diarization anti-over-count bundle SHIPPED as v0.3.17** (committed + signed
re-freeze; the freeze activates the Python half). User validated the merge
button live in dev on the 14-speaker demo meeting before shipping. All
verified: 148 pytest (13 new) · 49 cargo tests (2 new) · cargo check · tsc.

- **A1 (`diarizer.py`)** `drop_unvoiced_turns()` — turns overlapping no
  Whisper-transcribed segment start (±1 s slack) are dropped before speaker
  counting (kills music/SFX phantom clusters; fail-open).
- **A2 (`diarizer.py`)** `merge_similar_speakers()` + `_speaker_embeddings()` —
  per-speaker campplus embeddings (sherpa `SpeakerEmbeddingExtractor`, same
  model file, ≤20 s of longest turns), union-find merge at cosine ≥0.60. This is
  the merge `merge_minor_speakers` can't do (one voice split into two long
  clusters). Best-effort try/except; skipped when <2 speakers.
- **A3 (`transcriber.py`)** media gate in `diarize_system_labels(…, mic_segments)`
  — builds the flat transcript and reuses `classify_category`; "youtube"
  (playback/mic-bleed) → no diarization at all (the demo-video case). Both
  faster-whisper + MLX call sites pass mic_segments.
- **A4 (`diarizer.py`)** caps tightened: `_MIN_SPEAKER_SECONDS` 8→12,
  `_MAX_SPEAKERS` 8→5, `min_duration_on` 0.3→0.5.
- **Retroactive cleanup (Rust+TS, works in dev NOW):** `storage.rs`
  `collapse_speaker_turns()` (pure) + `merge_meeting_speakers(id)` rewrite
  transcript/turns to flat "Them" + scrub "Speaker N" attendees (FTS trigger
  re-indexes); command registered in `lib.rs`; `tauri.ts` wrapper; NoteViewer
  Transcript tab shows a two-click-confirm **"Merge speakers into 'Them'"**
  button only when `Speaker N` labels exist. For old meetings (e.g. the
  14-speaker "Hamza Demonstrates Sovereign AI" demo) whose audio is gone.

**Next:** commit (needs user OK) → re-freeze (v0.3.17) with
`ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev"` to activate the Python half →
record a real multi-party call + a playback video to validate live.

---

## Previous session (2026-07-03 ~1:00am)

**Audit + research session; graph fix COMMITTED as v0.3.15 (`fd2ab16`, local-only,
NOT pushed); staging DMG build launched (auto-installs to /Applications).**

**New environment discipline (user-decided):** *development* = `npm run tauri dev`
(iterate here), *staging* = the frozen installed `/Applications/Adversaria.app`
(user's daily driver). Only re-freeze dev → staging (`scripts/build-dmg.sh`) once
the user is happy in dev. ⚠️ **Sequencing gotcha (hit live this session):**
`build-dmg.sh`'s re-freeze wipes `python-service/dist/adversaria-service`, which
`tauri dev`'s build.rs needs as a bundled resource — starting both at once kills
the dev build with `resource path … doesn't exist`. **Freeze first, then dev**
(see LESSONS_LEARNED). Also quit the installed app before running dev — they share
the SQLCipher DB and there's no busy_timeout yet (see the audit list in TODO.md).
⚠️ **Signing gotcha (hit + fixed this session):** `build-dmg.sh` reads
`ADVERSARIA_SIGN_IDENTITY` and silently falls back to **ad-hoc** when unset (it is
in NO shell profile — export it every run: `export ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev"`).
The v0.3.15 build went out ad-hoc and was re-signed in place afterwards (sidecar
with `python-service/entitlements.plist` first, then the outer bundle) — installed
app verified `Authority=NotchyPrompter Dev`, TCC grants preserved. The packaged
`Adversaria_aarch64.dmg` still contains the ad-hoc copy; rebuild it (with the env
var set) before handing the DMG to anyone.

- **Graph flutter ROOT-CAUSED and fixed** (`src/components/GraphView.tsx`, `tsc` ✓,
  committed v0.3.15; in the staging build; user has NOT yet confirmed the feel
  live). The 2026-07-02 alpha/decay tuning treated symptoms;
  the actual causes live in the `cytoscape-d3-force` wrapper
  (`node_modules/cytoscape-d3-force/src/d3-force.js:223-246`): (1) on every node
  grab AND release it restarts the sim with `alphaTarget = alpha/3` and never
  lowers it → post-drag the graph buzzes at constant energy ~2s then hard-freezes
  mid-motion; (2) `layout:{name:"random"}` re-scattered + re-settled the whole
  graph on every tab visit. Fix: `cy.on("free","node", …)` zeroes `alphaTarget`
  (smooth decay to rest); module-scope `savedPositions` map + `preset` layout
  resumes settled positions across visits (gentle `alpha: 0.12` wake-up; legend
  toggles no longer re-scatter either).
- **Full-codebase bug audit** (3 review agents, findings verified against code):
  ranked list now at the top of [TODO.md](./TODO.md) "2026-07-03 full-codebase
  bug audit". Top three: Python service blocks its event loop during any
  transcription (`server.py` async-def-with-sync-body endpoints), stale
  action-item checkboxes after Regenerate Notes (`NoteViewer.tsx`), no SQLite
  `busy_timeout`/WAL (`storage.rs`).
- **Diarization over-count researched** (the "Hamza Demonstrates Sovereign AI"
  many-speakers case): the demo plays TTS/media voices through the system channel;
  campplus embeddings are OOD on synthetic audio and splinter; `num_clusters=-1`
  is unbounded; `merge_minor_speakers()` merges by duration only. Recommended
  quick-win bundle (pure Python, offline, no new models): (A1) diarize only
  Whisper-transcribed spans, (A2) embedding-similarity re-merge of clusters,
  (A3) media/playback gate reusing `classify_category`, (A4) tighten caps.
  Model swap (WeSpeaker ResNet293 / TitaNet-large — English-only trade-off) and
  pyannote community-1 paths documented in the session report. Needs re-freeze.
- **Export-graph-to-second-brain feature designed** (user request): Settings gets
  a vault folder + toggle; on meeting save/delete re-export markdown files with
  YAML frontmatter + wikilinks (OKF-compatible — see Google's Open Knowledge
  Format spec, github.com/GoogleCloudPlatform/knowledge-catalog `okf/SPEC.md`) to
  a local folder consumed by laghari-vault/graphify/Obsidian. Not built —
  awaiting user's format/trigger choices.

---

## Previous session (2026-07-02 9:57am)

**No code changed.** Wrote two comprehensive deep-dive documents covering the full project
(v0.3.14 scope):

- **[DEEP_DIVE_BUSINESS.md](./DEEP_DIVE_BUSINESS.md)** — business-oriented: market analysis,
  competitive landscape (Granola/Meetily/Fireflies vs Adversaria across 15 dimensions),
  strategic wedge (regulated-client solos), pricing model (free-only at launch → Pro → Enterprise),
  go-to-market plan, 10× workflow vision, risk assessment, and why-this-matters for 4 audiences.
- **[DEEP_DIVE_TECHNICAL.md](./DEEP_DIVE_TECHNICAL.md)** — technical: full 3-layer architecture,
  every feature's internals (Knowledge Graph quad-tree → d3-force physics tuning, Export/Import
  bundle schema v1, slide export rendering, streaming-chat SSE → Channel pipeline, cross-meeting
  Ask intent routing, diarization threshold tuning), complete tech-stack table with versions,
  SQLCipher key management, build/packaging pipeline, ADR index, known debt.

Both docs added to CLAUDE.md companion-docs table. STATUS.md and HANDOFF.md updated. No commit
needed — user asked for these as reference documents, they're not checked into a feature branch.

---

## Current state (2026-06-19)

**Product renamed → "Adversaria"** (Latin: a notebook of jottings). Was "Meeting
Note Taker" / working-name "VANE". The header wordmark + a **Vane-style intro splash**
use azure `#24A0ED` in self-hosted **Instrument Serif** (`public/fonts/`, offline — no
font CDN). `productName` in `tauri.conf.json` is still "Meeting Note Taker" (bundle/
app-data dir unchanged on purpose). A cross-product **[STRATEGY.md](./STRATEGY.md)** now
frames Adversaria as the *sovereign capture organ* of **lagharilabs OS** (the bigger
agentic command center at `~/Documents/Documents/MyProjects/lagharilabs-os`) — **read
STRATEGY.md first**, it reframes the whole product. Repo synced on `master` (`b29970c`).

**Now cross-platform (Windows + macOS).** A full macOS/Apple-Silicon port landed
2026-06-17 (ADR-010): ScreenCaptureKit + cpal capture, MLX (`whisper-large-v3-mlx`)
transcription, CoreAudio meeting-detection. Verified building/linking + MLX
transcription on macOS 26.5 / M5 Max; **not yet run in a real live call** (needs
the Screen-Recording grant). Runbook below. The state below describes the mature
Windows build; all of it is shared cross-platform except the OS layers.

**Working end-to-end on the dev machine** (Windows 11, RTX 5090, Ollama with
**`qwen3.6:35b-a3b`** — a 36B MoE, vision+tools, ~23 GB, Q4_K_M):

- Record → GPU transcription → local summarization → SQLite → UI. ✅
- **Microphone + system audio** both captured; transcript is speaker-labeled
  `Me:` / `Them:`. ✅
- **Summary UI cards** — sections render as collapsible cards with icons +
  action-item checkboxes; **Copy** (clean text + rich HTML) and **Export `.md`**. ✅
- **Granola-style cream theme** (inverted Tailwind gray ramp); Start/Stop **pill
  button** with a live elapsed timer. ✅
- **Arabic / multilingual summaries** — per-meeting language picker + Settings
  default (English / Arabic / match-spoken), with **RTL** rendering. ✅
- **Auto-detect + floating card** — registry mic-in-use poll fires a native toast
  *and* a frameless always-on-top "Meeting detected — Record/Dismiss" card. ✅
- **Re-summarize** a saved meeting with a different template/language. ✅
- **Chat with a meeting** — a "Chat" tab asks grounded questions answered only
  from that meeting's transcript (local Ollama). Ephemeral Q&A, RTL-aware. ✅
  *(Verified via tests + compile; not yet exercised live against Ollama.)*
- **Your notes + AI notes** — live notepad while recording; notes are kept
  verbatim ("My Notes" tab, `user_notes` column) AND woven into the AI summary
  as anchors. ✅ *(Verified via tests + compile; not yet exercised live.)*
- **Live transcription preview** — rolling ~30s caption while recording
  (`/transcribe_chunk` + `live-transcript` event → caption pane). MVP preview,
  not the authoritative transcript (that's still the `/transcribe` pass at stop).
  ✅ *(Compile/test-verified; NOT yet verified live on the GPU — see TODO #2.)*
- **Name + vocabulary personalization (2026-06-18)** — `user_name` relabels `Me:`
  lines by the user's name (server-side `relabel_me`, driven by the `/transcribe`
  `me_label` param); `custom_vocabulary` biases Whisper spelling via `initial_prompt`
  on both backends. Settings has "Your Name" + "Custom Vocabulary" fields. ✅
  *(75 pytest + cargo check + tsc green; not yet exercised live.)*
- **UX batch + Adversaria rebrand (2026-06-18 evening)** ✅ — Chat renders markdown +
  **persists history** (+Clear); meetings **search bar**; **colorful tags** with
  **auto-detected session type** (Meeting=blue / YouTube=red / Brainstorm=purple,
  mic-bleed-aware via channel word-overlap) + **click-a-pill to rename/recolor**;
  **user-editable prompt templates** in Settings (PUT/DELETE `/templates/{name}`,
  dynamic dropdowns); **sidebar revamp** (category-filter pillars, drag-resize, more
  left padding, dropped the duplicate template-select/Record + the dead "Back to
  meetings"); **silence auto-stop** (5-min "meeting over?" prompt, 10-min hard stop —
  kills the runaway-recording bug, uses "no live-transcript event" as the signal, no
  Rust audio changes). All delegated to DeepSeek (stuntman), reviewed + `tsc`/`cargo
  check`/75-pytest verified here, committed + pushed. **Verified live in the running
  app** (tags/colors/sidebar/splash); silence-auto-stop + chat-persistence not yet
  exercised through a full real recording.

**Shared GPU with Tatweer OS:** Tatweer OS now also points at this Ollama +
`qwen3.6:35b-a3b`, so the two apps share **one** loaded copy (~23 GB of 32 GB)
and run together. (Tatweer changes are on its own repo, `main` commit `2dd6c8e`.)

**Not yet done:** the app is **dev-only** (manually-started Python service; no
bundled sidecar/installer) — see the **packaging milestone**
[PACKAGING.md](./PACKAGING.md). The two minor 🔴 bugs are now **fixed**
(2026-06-17): live HTTP-client URL update (no restart) and leak-free temp-WAV
cleanup on failure — no known correctness bugs remain in [TODO.md](./TODO.md).

Repo: `github.com/mhlaghari/meeting-note-taker` (branch `master`, synced).
Untracked dev artifacts (`tauri_dev.log`, `python-service/bench_results.json`)
are gitignored.

---

## Run the dev stack

Two processes. See [CLAUDE.md](../CLAUDE.md) for the condensed version.

**Terminal 1 — Python ML service** (port **9877**, matching `config.json`):
```powershell
cd python-service
uv sync --extra cuda      # installs cuBLAS/cuDNN for GPU. Omit --extra cuda on a CPU-only box.
uv run uvicorn src.server:app --host 127.0.0.1 --port 9877 --log-level info
# Or just: ..\start_python_service.bat  (launches via conda python on :9877)
```
Note: launch the service in its **own** terminal / `Start-Process` (detached).
Running it as a piped background job can let `uv` exit and kill it.
First run downloads the Whisper `large-v3` model (~3 GB). Watch for
`Whisper model loaded successfully on cuda` — if it says `cpu` while a GPU is
present, the `cuda` extra isn't installed.

**Terminal 2 — desktop app:**
```powershell
npm install
npm run tauri dev         # if cargo isn't found in Git Bash: export PATH="$HOME/.cargo/bin:$PATH"
```

**Prerequisite:** Ollama running with the model pulled: `ollama pull qwen3.6:35b-a3b`.

**Verify connectivity:**
```powershell
curl http://127.0.0.1:9877/health
# {"status":"ok","whisper_model":"large-v3","ollama_available":true}
```
Or open **Settings** in the app — the service indicator should be green.

---

## Run the dev stack — macOS (Apple Silicon)

Ported 2026-06-17 (ADR-010). On macOS the stack is **all Apple-GPU**:
transcription via **MLX** (`whisper-large-v3-mlx`) and the summarization LLM via
**Rapid-MLX** (`qwen3.6-27b`), instead of CUDA-Whisper + Ollama. Both backends
auto-select on Apple Silicon — no env vars needed. Verified building/linking +
MLX transcription + a real `/summarize` through Rapid-MLX on macOS 26.5 / M5 Max;
not yet exercised in a real live *call*. Config lives at
`~/Library/Application Support/meeting-note-taker/`; default service URL
`http://127.0.0.1:9876`.

**Prerequisites (one-time):**
```bash
# Rust (the Tauri backend won't build without it):
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# ffmpeg — mlx-whisper decodes audio through it:
brew install ffmpeg
# Rapid-MLX — the OpenAI-compatible LLM server for Apple Silicon:
brew install raullenchai/rapid-mlx/rapid-mlx
```

**Terminal 1 — Rapid-MLX LLM server** (summarization, OpenAI-compatible on :8000):
```bash
rapid-mlx serve mlx-community/Qwen3.6-27B-4bit \
  --served-model-name qwen3.6-27b --port 8000 --no-thinking
```
The model is ~15 GB (auto-downloads to `~/.cache/huggingface/` on first serve).
`--served-model-name` MUST match the app's model field (`qwen3.6-27b`), since the
app passes that string as the OpenAI `model`. To use Ollama instead, set
`LLM_BACKEND=ollama` (+ pull the model) before launching Terminal 2.

**Terminal 2 — Python ML service** (Apple-GPU transcription; auto-routes the LLM
to Rapid-MLX on macOS):
```bash
cd python-service
uv sync --extra mlx       # installs mlx-whisper (arm64 macOS only; no-op elsewhere)
export HF_HUB_DISABLE_XET=1   # REQUIRED while hf_xet is broken, or the model download hangs at 0 bytes (see LESSONS_LEARNED)
uv run uvicorn src.server:app --host 127.0.0.1 --port 9876 --log-level info
```
First transcription downloads `whisper-large-v3-mlx` (~3 GB). The factory
auto-selects MLX on arm64 macOS; override with `WHISPER_BACKEND=mlx|faster-whisper`.
The model is on HuggingFace's Xet backend; without `HF_HUB_DISABLE_XET=1` the
download wedges at 0 bytes (broken `hf_xet`) and **every transcription hangs**.
For an instant (rough) start before the 3 GB pull finishes, add
`MLX_WHISPER_MODEL=mlx-community/whisper-tiny`.
The summarizer auto-selects the `openai` backend (Rapid-MLX) on arm64 macOS;
override with `LLM_BACKEND` / `LLM_BASE_URL`.

**Terminal 3 — desktop app:**
```bash
npm install
npm run tauri dev
```

**macOS permissions (the gotcha):**
- **Screen Recording** — required for ScreenCaptureKit system-audio capture.
  Grant *Meeting Note Taker* (or your terminal, in dev) under **System Settings →
  Privacy & Security → Screen & System Audio Recording**, then **restart the app**
  (TCC grants are read at launch).
- **Microphone** — prompted on first record. **Launch `tauri dev` from a
  standalone terminal** (Terminal/iTerm), not an IDE's integrated terminal, or the
  prompt can be silently swallowed.
- If prompts get stuck: `tccutil reset ScreenCapture com.meetingnotetaker.app`
  and `tccutil reset Microphone com.meetingnotetaker.app`, then relaunch.
- Hotkey is **Cmd+Shift+M** on macOS.

```bash
curl http://127.0.0.1:9876/health
# {"status":"ok","whisper_model":"large-v3","ollama_available":true}
```

---

## Building the Windows app (packaging runbook — researched 2026-07-06)

**Verdict: you CANNOT build the Windows app from the Mac.** PyInstaller does not
cross-compile (the Windows sidecar `.exe` must be frozen *on Windows*), and
`.msi`/WiX is Windows-only. Cross-building just the Tauri shell buys nothing —
it'd wrap a macOS/MLX sidecar it can't run. So build the whole thing on Windows:
a **GitHub Actions `windows-latest` runner (recommended for a Mac-based solo
dev)**, a Windows 11 PC (the RTX 5090 dev box), or a cloud Windows VM.

**The app CODE is already cross-platform** (Windows was the original platform:
`#[cfg(windows)]` WASAPI capture + registry detection + faster-whisper CUDA→CPU).
This is a *build-pipeline + a few port fixes* job, not a rewrite. Scope also in
[PACKAGING.md](./PACKAGING.md).

### Path 1 — GitHub Actions (recommended)
One tagged release builds both OSes. Add a `windows-latest` matrix leg beside the
existing macOS build; `windows-latest` already ships MSVC + Windows SDK + WebView2.
```yaml
# .github/workflows/release.yml  (Windows leg; add your macos-14 leg to the matrix)
on: { push: { tags: ['v*'] } }
jobs:
  build:
    strategy: { matrix: { include: [
      { platform: windows-latest, args: "--bundles nsis" },
      { platform: macos-14,       args: "" } ] } }
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4 with: { node-version: 20 }
      - uses: dtolnay/rust-toolchain@stable      # MSVC is default on windows-latest
      - uses: astral-sh/setup-uv@v6
      - run: npm ci
      - if: matrix.platform == 'windows-latest'  # freeze the sidecar ON Windows
        working-directory: python-service
        run: |
          uv sync --extra cuda
          uv run --with pyinstaller pyinstaller adversaria-service-windows.spec --noconfirm
      - uses: tauri-apps/tauri-action@v0
        env: { GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }},
               TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_UPDATER_KEY }},
               TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_UPDATER_KEY_PW }} }
        with: { tagName: v__VERSION__, args: ${{ matrix.args }} }
```

### Path 2 — a Windows 11 box / VM
One-time: Rust via rustup (**MSVC host, NOT `-gnu`**) · "VS Build Tools 2022 →
Desktop development with C++" · Node 20 · `uv` · WebView2 (preinstalled on Win11).
Then:
```powershell
cd python-service; uv sync --extra cuda
uv run --with pyinstaller pyinstaller adversaria-service-windows.spec --noconfirm
cd ..; npm ci; npm run tauri build -- --bundles nsis
# -> src-tauri\target\release\bundle\nsis\Adversaria_x.y.z_x64-setup.exe
```

### Config: `src-tauri/tauri.windows.conf.json` (Tauri auto-merges it on Windows)
Do NOT add `"msi"`/`"nsis"` to the shared `tauri.conf.json` `targets` (a mac build
would then try to cross-build it and fail). Instead:
```jsonc
{ "bundle": { "targets": ["nsis"],
    "windows": { "nsis": { "installMode": "perUser" } } } }  // %LOCALAPPDATA%, no admin
```
**NSIS, `perUser`** is the pick (no admin prompt; installs to `%LOCALAPPDATA%`,
matching the per-user app-data model). MSI later only if an enterprise asks.
WebView2: leave default `downloadBootstrapper` (preinstalled on Win11).

### The Windows sidecar spec (`adversaria-service-windows.spec` — NEW, mac spec won't work)
- **Drop** `mlx`/`mlx_whisper` + the `mlx.metallib` copy (Apple-only). **Keep**
  `av`, `ctranslate2`, `faster_whisper`, `tiktoken`, `huggingface_hub`, `certifi`,
  `sherpa_onnx`.
- **GPU:** bundle CUDA 12 DLLs via `collect_all("nvidia.cublas")` +
  `collect_all("nvidia.cudnn")` (from `uv sync --extra cuda` wheels). ⚠️ CTranslate2
  ≥4.5 needs **cuDNN 9 + CUDA ≥12.3** (Blackwell/5090 sm_120) or the GPU path throws
  `CUBLAS_STATUS_NOT_SUPPORTED`. **CPU-only** alt: skip the nvidia collect (code's
  `device="auto"` falls back to int8) — ~300–500 MB smaller installer.
- `console=True` → **`console=False`** (else a black terminal flashes each launch).
- Drop `target_arch="arm64"` (Windows is x86_64). Output:
  `dist\adversaria-service\adversaria-service.exe` — existing `bundle.resources`
  mapping copies it fine, no change.
- `_patch_cuda_path()` (`transcriber.py`) hunts site-packages → **no-op when frozen**;
  the DLLs MUST be baked in by the spec, don't rely on it.

### Rust spawn fix (`commands.rs` `spawn_sidecar`, ~line 73) — `#[cfg]`-gate
Append `.exe`; on Windows skip the Homebrew-PATH + `HF_HUB_DISABLE_XET` macOS-isms
and add `.creation_flags(0x08000000 /*CREATE_NO_WINDOW*/)` so no console flashes.

### Code signing (2026)
Unsigned = **SmartScreen "Windows protected your PC"** warning (no macOS-style
right-click bypass; user clicks *More info → Run anyway*). Runs, but deters
non-technical users. Options:
- **Azure Artifact Signing** (ex-"Trusted Signing", GA Apr 2026) — **~$9.99/mo**,
  **instant** SmartScreen reputation, first-class Tauri support (`signCommand` with
  `trusted-signing-cli`). ⚠️ **ELIGIBILITY (check before betting on it):** limited to
  US/CA/EU/UK businesses + self-employed individuals verifying to a **US/Canada
  address** — likely NOT usable from outside those regions. *(User must confirm.)*
- **OV cert** ~$200–450/yr (reputation ramps over time). **EV** ~$300–700/yr (instant,
  HSM hassle). **Unsigned** = fine for a technical beta (document the Run-anyway step,
  like the macOS `xattr` beta note).
- The minisign **updater** key you already have is SEPARATE — it signs the update
  payload, does nothing for SmartScreen. You need both.

### Windows-port verification checklist (build on Win11, then verify each)
1. **🔴 Whisper model picker is MLX-only.** `transcriber.py` `WHISPER_MODELS` maps to
   `mlx-community/*` repos (Apple-only); Windows/faster-whisper needs CTranslate2 ids
   (`large-v3`, `Systran/faster-whisper-large-v3`). The Settings picker +
   `list/download_whisper_model` need a Windows registry/default — **its own fix.**
2. Sidecar spawn `.exe` + env + `CREATE_NO_WINDOW` (above).
3. **Clean shutdown** — verify via Task Manager / `netstat -ano` that no
   `adversaria-service.exe` and no held port remain after quit (add `taskkill /F /T`
   fallback per PACKAGING Phase 3). The whole point of the packaging gate.
4. WASAPI dual capture (system+mic both in the WAV) — smoke-test on Win11.
5. Registry meeting-detection (`detection.rs`/`winreg`) still fires on Win11.
6. CUDA path loads from the FROZEN bundle (not silently CPU); AND CPU-only fallback
   works on a GPU-less VM (installer must serve both).
7. Ollama native Windows (assumed installed) or the cloud BYO-key escape hatch.
8. Audit other file-path handling on Windows (a `decode_import_file` handle leak was
   already found/fixed 2026-07-06; treat WAV cleanup + HF cache as suspect until run).

---

## LLM backend: Ollama (default) or vLLM via WSL2

The summarizer/chat backend is env-selected (ADR-009). **Default is Ollama** —
nothing to do. To switch to **vLLM** (concurrent, non-blocking; fixes the
chat-stalls-behind-summarize + cold-reload pain):

**1. One-time: stand up vLLM in WSL2** (vLLM has no native Windows build):
```bash
# In Windows PowerShell (admin), if WSL isn't installed:
wsl --install -d Ubuntu        # reboot if prompted; ensure a recent NVIDIA driver (WSL CUDA)
# Inside WSL2 Ubuntu:
python3 -m venv ~/vllm && source ~/vllm/bin/activate
pip install --upgrade pip
pip install "vllm>=0.23"        # CUDA 12.8/13.0 wheel; Blackwell/5090 needs CUDA >= 12.8
export VLLM_NO_USAGE_STATS=1 DO_NOT_TRACK=1   # keep it offline/telemetry-free
vllm serve Qwen/Qwen3.6-35B-A3B-FP8 \
  --host 127.0.0.1 --port 8000 \
  --tensor-parallel-size 1 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.80 \   # leaves ~7 GB for faster-whisper on the 32 GB 5090
  --reasoning-parser qwen3
# WSL2 forwards 127.0.0.1:8000 to Windows automatically.
```
Notes: re-pull **FP8 safetensors** (the Ollama Q4_K_M GGUF is NOT reusable on
vLLM). If attention errors on Blackwell, try `VLLM_FLASH_ATTN_VERSION=2`.

**2. Point the ML service at it** — set these env vars before launching uvicorn:
```powershell
$env:LLM_BACKEND  = "openai"
$env:LLM_BASE_URL = "http://127.0.0.1:8000/v1"
$env:LLM_API_KEY  = "EMPTY"
uv run uvicorn src.server:app --host 127.0.0.1 --port 9877 --log-level info
```
**3. Set the model in the app** — Settings → model = `Qwen/Qwen3.6-35B-A3B-FP8`
(the `ollama_model` config field is passed through as the model name for either
backend). To revert: unset `LLM_BACKEND` (or set `ollama`) and restart the service.

> Cheaper alternative if you don't want WSL2: leave Ollama and set
> `OLLAMA_NUM_PARALLEL=2` + `keep_alive=-1` (keeps the model resident). The
> installer-friendly native option is `llama.cpp llama-server` (also OpenAI-API;
> `LLM_BACKEND=openai` points at it unchanged). See ADR-009.

## Test it

1. Start recording (record button, tray menu, or `Ctrl+Shift+M`).
2. **Play / speak real speech for 30+ seconds** — and talk back, so both
   `Me:` and `Them:` lines appear. (Recording silence produces nothing useful —
   see [LESSONS_LEARNED.md](./LESSONS_LEARNED.md).)
3. Stop. Within seconds the meeting appears with transcript + summary tabs.
4. Mic records the **default Windows input device** — set the right one if using
   a headset.
5. **Auto-detect is OFF by default.** To use it: Settings → tick "Auto-detect
   meetings" → **Save Settings** (ticking alone doesn't apply it — you must Save;
   no restart needed). A floating "Meeting detected" card then offers to record
   when Zoom/Teams/Webex/Slack/a browser meeting uses your mic for ~4–6 s. macOS
   14.4+; WhatsApp/FaceTime not recognized. Detection needs no permission, but
   *recording* (clicking Record) needs the Screen-Recording + Microphone grants.
6. Set **Your Name** in Settings so your lines read as your name, and add
   **Custom Vocabulary** so names/jargon transcribe correctly.

**Automated checks:**
```powershell
cd python-service; uv run pytest     # 60 tests, ML mocked, <3s
cd src-tauri;      cargo check       # Rust compiles
npx tsc --noEmit                     # frontend type-check
```

---

## If something's broken

Check [LESSONS_LEARNED.md](./LESSONS_LEARNED.md) first — most failure modes are
documented with fixes. The fast triage:

| Symptom | Likely cause | First move |
|---------|--------------|------------|
| App says service offline / wrong port | URL cached in memory | Fix `config.json` (port **9877**), **restart app** |
| `cargo … program not found` | PATH | `export PATH="$HOME/.cargo/bin:$PATH"` |
| `Port 1420 / 9877 in use` | orphaned socket (dead PID still LISTENING) | find the inheriting child & kill it (see LESSONS_LEARNED) |
| Transcribing on CPU with a GPU | `cuda` extra missing | `uv sync --extra cuda`, restart service |
| Empty/garbage transcript | recorded silence | record real speech |
| Long meeting, short summary | `num_ctx` truncation (🔴 bug) | see TODO.md #1 |

---

## Where to go next

All known 🔴 bugs are fixed and the 2026-06-18 UX batch shipped (see Done in
[TODO.md](./TODO.md)). The next frontier (TODO "Next frontier — the agentic loop"):

1. **To-do / Kanban board fed from meetings** — extract each meeting's action items into
   a real task board so "today's to-dos" auto-deploy from yesterday's meetings. The
   killer 10× workflow ([STRATEGY.md](./STRATEGY.md)) and the bridge into lagharilabs OS.
   **The user's stated #1.**
2. **Speaker diarization** — split "Them" into named individuals (biggest depth gap vs
   Meetily; needed for legal/clinical credibility). Or position around its absence.
3. **Cross-meeting ask (RAG over all meetings)** + real SQLite FTS5 search.
4. **The OS bridge** — feed Adversaria into lagharilabs OS, retiring its Granola
   dependency → a fully sovereign capture→memory→action loop.
5. **Packaging → unsigned personal `.dmg`** (~2–4 focused days; PyInstaller-bundling the
   MLX + ffmpeg Python sidecar is the risk; Rapid-MLX/Ollama stays a prerequisite; see
   the recording/packaging research notes the user can paste from this session).

**Candidate — UNDECIDED — pre-meeting notes (calendar prep).** The user wants the app to
read the calendar (Google Calendar, Microsoft Graph/Teams, etc.) and, *before* a meeting,
**prompt them with prep — what to ask, context pulled from prior related meetings.** The
user is **unsure whether to build it** — clarify the exact value (suggested questions?
agenda? attendee/topic history?) before committing. It pairs with #3 (context from past
meetings) and calendar integration (TODO roadmap #4 Phase 2 / ADR-002: read-only OAuth,
**off by default** — the most data-exposing feature, so it must honor the privacy stance).

---

## Last session

**2026-06-25 #17 (v0.3.8 — on-device Whisper model picker, built).** Implemented the picker from #16's
plan. Settings → Transcription (On-device engine) lists curated MLX models with per-model download status
+ a **"Download now"** button (Downloading… → Ready ✓): `large-v3` (rec; 99 langs incl. Arabic),
`large-v3-turbo`, `large-v3-turbo-q4` (HF-verified repo ids). Layers: `WHISPER_MODELS` registry +
`whisper_repo_for`/`list_whisper_models`/`whisper_model_is_cached`/`download_whisper_model` in
`transcriber.py`; `/whisper_models` + `/whisper_download` endpoints; `whisper_model` threaded
`AppConfig`→`http_client.transcribe`→`/transcribe` (MLX swaps `model_repo` per request, restored after —
faster-whisper/Windows ignores it); Rust `list_whisper_models`/`download_whisper_model` commands (registered
in `lib.rs`); `lib/tauri.ts` wrappers + `WhisperModelInfo` type; Settings picker UI. Verified: `tsc` ✓,
`cargo check` ✓, 2 pytest + a mocked logic check (key→repo mapping, fallback, list schema, and the real
HF-cache check correctly reports large-v3 as already downloaded). **NOT yet committed when this note was
written → committed as v0.3.8.** ⚠️ Same frozen-sidecar caveat: needs a `build-dmg.sh` re-freeze to go live.

⏰ **MORNING TODO — re-freeze, then verify the model picker.** **User observed in dev:** the Whisper model
picker shows **only "Large v3" and no Download buttons** — they couldn't download the other models. This is
**NOT a code bug**: `tauri dev` runs the **frozen** sidecar, which lacks the new `/whisper_models` +
`/whisper_download` endpoints, so `listWhisperModels()` 404s → `whisperModels` stays empty → the dropdown
falls back to the single configured model and the status/Download block renders nothing. The fix is the
re-freeze (it rebuilds the PyInstaller sidecar with the new Python). **Steps:** run `build-dmg.sh` → open
the packaged app → confirm all 3 models list with sizes, "Download now" fetches `large-v3-turbo` /
`large-v3-turbo-q4` and flips to "Ready ✓", and the chosen model transcribes. Same re-freeze also activates
v0.3.6 hardened prompt + v0.3.7 cloud transcription — verify those too (cloud needs a Groq key).

**Status:** `master` **pushed to origin** (`3642041`, 8 commits). Re-freeze deferred to the morning (user's
call). After it: beta steps 3–5 (Tauri auto-updater → offline license/trial gate → notarized DMG); later,
NVIDIA Parakeet as a fast CoreML/ANE local backend.

**2026-06-25 #16 (fix: empty Prompts tab; + v0.3.8 model-picker plan locked).** Fixed (`075e90a`) the
blank Prompts dropdowns: Settings fetched `/templates` once at mount with no retry, losing the race
against the sidecar's Whisper boot → permanently blank. `loadTemplates` now **retries on empty/failure**
(10×/1.2s; there are always ≥4 bundled templates, so empty = not-ready). Also documented the `tauri dev`
hot-reload **sidecar-orphan / stale-1420** gotcha + clean-restart fix (HANDOFF Gotchas). Dev relaunched
clean (app 35607 / sidecar 56427).

**v0.3.8 NEXT — on-device Whisper model picker (Meetily-style).** Feasibility CONFIRMED by reading
`transcriber.py`: the **MLX backend loads the model per-call** (`mlx_whisper.transcribe(...,
path_or_hf_repo=self.model_repo)`, ~line 536) and HF auto-downloads on first use — so switching/downloading
a model is just changing a string, **no restart** (macOS/MLX path; faster-whisper/Windows loads once at
`__init__` and would need a reload). Plan: add `whisper_model` (friendly key) to AppConfig → a curated
picker (`large-v3` [rec, 99 langs incl. Arabic] / `large-v3-turbo` / `medium` / `small`) with
**✓ downloaded / ⬇ will-download** status → thread the key through `/transcribe` (exactly like `vocabulary`)
→ MLX maps key→repo per-call → auto-download + auto-load. New endpoints: `/whisper_models` (curated list +
HF-cache status) and `/whisper_download` (proactive "Download now"). **Pending user decision — download UX:**
lazy (on first use) vs **"Download now" button** (recommended) vs full streamed progress bar.

**⚠️ SEQUENCING (important):** `tauri dev` runs the **FROZEN** sidecar, so the v0.3.6 hardened prompt,
v0.3.7 cloud transcription, AND a future v0.3.8 picker are ALL dormant until a **`build-dmg.sh` re-freeze**
— unverified Python is piling up. Recommended order: **re-freeze now** (makes v0.3.6 + v0.3.7 live/testable
+ fresh installable) → build v0.3.8 → one more re-freeze ships all three. Also still pending: **push** the
5 commits (`master` local-only: v0.3.5 `8dda7f6` → v0.3.6 `ea96e4d` → v0.3.7 `1eac1e2` → docs → fix `075e90a`).

**2026-06-25 #15 (v0.3.7 — BYO-key cloud transcription).** For testers without local-Whisper
hardware (and Intel Macs / speed), Settings → Transcription gained an **Engine** picker: *On-device
Whisper* (default; sovereign; diarized) or *Cloud — Groq (BYO key)*. Cloud path: new module-level
`transcribe_cloud()` in `transcriber.py` uploads each channel to `{base_url}/audio/transcriptions`
(`response_format=verbose_json`, Groq preset `https://api.groq.com/openai/v1`, `whisper-large-v3`) and
reuses `merge_labeled_segments` to interleave Me/Them by timestamp (no diarization in cloud mode). Wired
`transcription_base_url/_api_key/_model` through `AppConfig` (types.rs/config.rs) → `http_client.transcribe`
→ `commands.rs` (3 `configured_*` helpers) → `models.py` TranscribeRequest → `server.py /transcribe`
cloud branch. UI warns: **not sovereign + no diarization** in cloud mode. Verified: `tsc` ✓, `cargo check`
✓, 2 pytest tests + a mocked-httpx logic check (`transcribe_cloud` builds the right endpoint/model/auth
and merges) — **only the real Groq round-trip is unverified (needs a live key + recording)**. ⚠️ Packaged
DMG needs a Python re-freeze to ship. **Next (v0.3.8):** downloadable local-model picker — faster/smaller
Whisper variants now (same backend) + **NVIDIA Parakeet** as a fast CoreML/ANE backend (10× faster English,
would also enable better real-time; keep Whisper large-v3 the default for Arabic).

**2026-06-24 #14 (BUGFIX — false "ML Service Offline" + summarize/transcribe broke after a Settings save).**
Discovered while investigating the red status pill (and confirmed by a live `Summarize request failed: …
http://127.0.0.1:9876/summarize`). Root cause: the app auto-spawns the bundled Python sidecar on a
**dynamic free port** and `spawn_sidecar` points the HTTP client there — but `update_config` (runs on
every Settings **save**) reset the client to config's `python_service_url` (default `:9876`, dead),
clobbering the live port. So saving any setting silently broke transcription + summary and showed a false
"Offline". **Fix** (`commands.rs:update_config`): only honor the configured URL when `state.sidecar` is
`None` (i.e., we're not managing our own sidecar). Verified live via the dev watcher — new sidecar on
`:52929`, pill now **Online**. Notes: (1) the `commands.rs` comments calling the sidecar "packaged-only /
None in dev" are **stale** — `target/debug/adversaria-service/` exists, so `tauri dev` spawns it too; (2)
the dev hot-reload SIGKILLs the app so `shutdown_sidecar` doesn't run → it leaks an orphaned sidecar
(stale-port holder) on each Rust edit; kill it manually. ⚠️ **Beta-relevant** — packaged testers would hit
this the instant they save their Groq key. Goes in **v0.3.6** + needs a DMG rebuild.

**2026-06-24 #13 (Settings redesign + button/UI polish — UNCOMMITTED, tsc-green, design self-verified).**
The user called the Settings buttons/controls "AI sloppy / not Apple-grade" (screenshots) and asked to
simplify Settings + fix the cramped prompt box. Root causes found and fixed:
- **Prompt box collapsed to one line** because `.settings-input-text` hard-sets `height:38px` and was
  applied to the `<textarea>`. New `.settings-textarea` (auto height, `resize:vertical`); the prompt
  editor moved to its **own new "Prompts" tab** with a 300px editor (also fixes the vocabulary box).
- **Inconsistent buttons:** `.btn-primary` had no height/`white-space` (so "Set PIN" wrapped) and
  `.btn-secondary` carries `flex:1` (so Save/Delete mismatched). Fix: made `.btn-primary` consistent
  (38px tall, `nowrap`, `flex-shrink:0`) and added `.btn-ghost` / `.btn-danger`. **Left `.btn-secondary`
  untouched** — it's used by MeetingChat/NewNoteButton/NoteViewer and its `flex:1` may be load-bearing.
- **Ad-hoc Tailwind callouts** (`bg-amber-900/30`, `bg-green-900/15`, `text-xs text-gray-500`) replaced
  with semantic `.settings-note` (info/warn/ok) / `.settings-subcard` / `.settings-help`.
- **Simplified AI Engine tab:** added a **Groq** preset (`https://api.groq.com/openai/v1`, recommended
  default, with a "get a free key" link) — summary-via-Groq works config-only; the Python-service URL +
  health moved under an **Advanced** `<details>`. All existing providers (local/deepseek/openrouter/grok/
  custom) kept so no saved config breaks.

Files: `src/components/Settings.tsx` (full rewrite of the render; handlers/IPC unchanged), `src/prototype.css`
(new UI-kit classes + `.btn-primary` fix). Also **swapped the ⋯ row-menu emojis (📌🔒🗑) for SVG icons**
in `src/components/MeetingsList.tsx` (reuses `.settings-menu-item`; the padlock opens when the meeting is
locked). `npx tsc --noEmit` green. Settings **verified via a `prototype.css` mockup screenshot**; the app
was then **relaunched** (`npm run tauri dev`, v0.3.5 build) and loads real data with no keychain re-prompt
(the Tauri webview can't be click-driven from here, so the ⋯ menu / Settings need the user's eyes). **Not
committed; no DMG rebuilt.** Next: user click-through → commit as **v0.3.6**; then header status-pill polish
+ remaining decorative emojis (🍎 in the calendar card etc.), and Groq cloud transcription (beta step 2).

**2026-06-24 #12 (Calendar heatmap + date-scoped tag pills — v0.3.5, committed, user-confirmed live).**
Two sidebar UX changes the user asked for, both `npx tsc --noEmit` green, **committed to `master` as
v0.3.5:**
- **Meeting-count heatmap on the month calendar.** `DateHeatmap.tsx` was a *binary* shade (every day
  with ≥1 meeting got the same blue). Added a `level(count)` helper emitting `level-1..4` (absolute
  buckets: 1, 2, 3, 4+) and four increasing blue-opacity tiers in `prototype.css`
  (`.heatmap-day-monthly.level-1..4`, listed **after** `.has-meetings` so they win on source order).
  Busiest day (the user's 22nd) renders darkest; zero-meeting days stay the faint base; hover still
  flashes solid accent blue. Chose absolute buckets over relative-to-busiest scaling (told the user;
  easy to switch).
- **Date-scoped tag pills.** In `MeetingsList.tsx` the pills were built from *all* meetings, ignoring
  the date selection. Moved the pill computation below the `dateFilter` state and sourced it from a new
  `dateScoped` subset, so clicking a day narrows the pills to only that day's categories
  (Brainstorm / Meeting / YouTube…). The existing stale-filter guard already falls back to "All" if the
  active tag isn't present on the selected day. No new stats UI — the user clarified "statistics" just
  meant that day's categories, not a panel.

✅ **User-confirmed working live** in `npm run tauri dev` (the heatmap gradient and the date-scoped pills
both behave as intended). _Note for next time: the `tauri dev` launch first hit the SQLCipher /
encryption-at-rest keychain prompt ("meeting-note-taker wants to use … 'adversaria-db'") — the unsigned
dev binary is a new keychain identity so it re-prompts; approve with **Always Allow** and the encrypted
DB unlocks. A Tauri webview can't be driven programmatically from this environment (no `cliclick`/Quartz;
not browser-attachable), so live confirmation came from the user, not an automated screenshot._

Committed to `master` as **v0.3.5** (version bumped in `package.json` / `tauri.conf.json` / `Cargo.toml`
+ CHANGELOG). ARCHITECTURE/TODO/DECISIONS left untouched (UI-only change, below their altitude). No DMG
rebuilt yet (frontend-only — would only matter for a packaged release).

**Next (big thread opened 2026-06-24 pm): a Groq-first, registration-gated beta for non-developer friends.**
Goal: hand a manager-type a notarized DMG, they drag it in, paste a **free Groq API key**, and it just
works — no Ollama, no Python, no hardware. **Decisions locked this session:**
- **Provider = Groq** (groq.com, the LPU host — **NOT** the app's existing "xAI Grok" entry; different
  company). OpenAI-compatible at `https://api.groq.com/openai/v1`; models `whisper-large-v3` (audio) +
  `qwen/qwen3-32b` (summary/chat). Free tier, no credit card.
- **Transcription → Groq cloud (decided).** Today it's local-only (MLX/faster-whisper); the one new
  backend path is uploading the WAV to Groq's `audio/transcriptions`. Summary-via-Groq already works
  (config-only — the OpenAI-compatible path). After this a tester needs **nothing** local.
- **Code signing → user is joining the Apple Developer Program** ($99/yr). **Notarization is the HARD
  gate** — an un-notarized DMG is Gatekeeper-blocked ("app is damaged") for everyone but us. Wire
  Developer ID signing + notarization into `build-dmg.sh` once the cert exists (current cert is the
  local-only self-signed `NotchyPrompter Dev`).
- **Trial/activation → leaning offline signed license keys** (per-friend key: email + 1-yr expiry,
  verified offline with an embedded public key; zero server). True remote enable/disable/revoke needs a
  small hosted online check — defer unless leakage actually happens. _(User hadn't final-confirmed; they
  conflated this with Groq's cost. Clarified: each friend brings their **own free** key → Groq cost to
  the user ≈ **$0**; even if the user paid it's **~$1–2/user/mo**, Whisper-dominated. The real free-tier
  constraint is the **6,000 tokens/min** limit choking long-meeting summaries, not money.)_
- **Auto-update → Tauri v2 updater + GitHub Releases**, shipped in the **first** tester DMG (pre-updater
  installs can never auto-update). Needs a separate update-signing keypair (distinct from the Apple cert).
- **Legal → a first-run beta-EULA click-accept** (no-redistribute, confidential, 1-yr, no warranty)
  instead of a formal NDA; the license-key + activation deters passing-around more than a signature.

**Proposed sequence (smallest-risk first):** (1) simplified Settings + Groq preset (mostly frontend) →
(2) Groq cloud transcription (the new path; after this a working cloud build exists to self-test) →
(3) Tauri auto-updater → (4) offline license/trial gate + EULA screen → (5) notarized `build-dmg.sh`
when the cert lands. **No beta code written yet — awaiting the user's greenlight on step 1.** This
realizes Path A (free beta) from [marketing_strategy.md](./marketing_strategy.md) and directly lowers
the hardware barrier [STRATEGY.md](./STRATEGY.md) flags as the TAM limit.

---

**2026-06-24 #11 (Competitive assessment + marketing strategy).** No code changes
— deep analytical session. Claude read the entire codebase + docs and produced a
comprehensive competitive assessment saved to `docs/marketing_strategy.md`, covering:
- Pros (architecture, privacy story, docs discipline, 10× workflow thesis, shipping discipline)
- Cons (sovereign-first TAM limit, hardware barrier, missing diarization vs Meetily,
  UX maturity gaps, setup complexity, no team features, growing technical debt)
- Competitive positioning table (Adversaria vs Granola/Meetily/Fireflies/Otter)
- BYOK vs subscription recommendation: start with BYOK (free, zero liability)
- 15 prioritized improvements across immediate/short-term/medium-term/strategic timeframes
- The strategic fork: polish into product vs. keep as lagharilabs OS capture organ
Also added `marketing_strategy.md` to the companion docs table in CLAUDE.md.

**Next:** nothing from this session — review `marketing_strategy.md` and decide which
path to take.

**2026-06-24 #10 (Live recording waveform → v0.3.4; Groq STT queued next).**
- **Waveform:** replaced the canned bar animation with a real audio-reactive one. New shared
  `audio::current_rms` (RMS of last ~120 ms, float32/int16) + `AudioCapture::current_level()`
  (louder of system+mic ×12, clamped) on **both** macOS + Windows; `get_audio_level` command
  polled ~14 Hz by `RecordingNotes`, bars scale to it + flatline on silence (inline `height` +
  `animation:none`). 3 RMS unit tests green. Also fixed the hardcoded `00:00:00` header timer.
  The ×12 gain is a reasonable default (untested on live audio) — tune if bars are too flat/hot.
- **NEXT — Groq transcription option** (signed off: opt-in + clear "audio leaves device" warning):
  Settings transcription provider Local|Groq + groq key; Python `/transcribe` routes to Groq
  `whisper-large-v3` (`/openai/v1/audio/transcriptions`, `verbose_json` segments) when groq,
  keeping the Me/Them split + LOCAL diarization; 16 kHz-mono WAV upload (~13 min/stream under
  Groq's 25 MB cap, clear error beyond; chunking is a follow-up).
- v0.3.4 auto-installs on rebuild. **Also still queued: the lagharilabs-OS command-center plan.**

**2026-06-24 #9 (Bubble drag REALLY fixed → v0.3.3; + version display + auto-install).**
- v0.3.2's drag was a **no-op**: Tauri/macOS won't drag a window that isn't focused, and the
  bubble is created `focused(false)`. Real fix — new Rust `bubble_start_drag` command does
  `set_focus()` then `start_dragging()` **atomically** (focus only on the user's drag, so it
  still doesn't steal focus when it appears); `RecordingBubble` invokes it on mousedown.
- **Root meta-bug (why nothing seemed to work):** the user was running **v0.3.0 the whole time** —
  DMGs build to `target/`, never installed to `/Applications`. Fixed two ways: (1) `build-dmg.sh`
  now auto-installs to /Applications + relaunches (`ADVERSARIA_INSTALL=0` to skip); (2) the **app
  version is now shown in the Settings sidebar** (`getVersion()` + `core:app:allow-version`), so
  the running build is always visible.
- `tsc` + `cargo check` green. The rebuild auto-installs v0.3.3.

**2026-06-24 #8 (Floating bubble drag attempt → v0.3.2 — DID NOT WORK, superseded by #9).**
- **Bubble couldn't be moved:** it's a frameless window with no drag region. Fixed with the
  native OS drag — `getCurrentWindow().startDragging()` on the pill's `onMouseDown`
  (`RecordingBubble.tsx`); a <5px click still returns to the app, and the Stop button still
  stops (its `onMouseDown` stopPropagation keeps a press on it from starting a drag). Required
  adding `"recording"` to the capability `windows` + `core:window:allow-start-dragging`
  (`capabilities/default.json`) — core window commands are ACL-gated (custom commands like the
  Stop button aren't, which is why Stop worked but drag silently didn't). `tsc` + `cargo check` green.
- **Audio dips for ~1ms when recording starts (NOT fixed — deprioritized by user):** inherent to
  ScreenCaptureKit — installing the system-audio tap momentarily reconfigures the CoreAudio
  output device. The only real fix is pre-warming/keeping the SCStream alive, which means
  capturing before the user hits record (privacy + battery cost), so it's not worth it. Logged
  in [TODO.md](./TODO.md) as low priority.
- Needs the DMG rebuild (capability + frontend changes).

**2026-06-24 #7 (Diarization over-segmentation fix → v0.3.1 + a runtime LLM-routing diagnosis).**
- **Over-segmentation:** a 2-person call (1 remote = Basim) showed "Speaker 1/2/3" — short/
  compressed call audio over-segments a single speaker at clustering threshold 0.5. Swept the
  reference clip: distinct speakers stay separate up to **0.7**, merge at 0.8. Raised
  `_DEFAULT_THRESHOLD` 0.5 → **0.7** (the safe ceiling). ⚠️ Applies to NEW recordings only —
  audio is deleted after transcription, so already-saved transcripts keep their labels.
- **"Chat failed → :8765" (NOT a code bug):** a stale **5-day dev uvicorn** squatting on `:9876`
  + an old app instance whose sidecar inherited `LLM_BASE_URL=:8765` made chat fall back to the
  local server (404). The app spawns its sidecar on a dynamic port and `set_base_url`s the client
  to it (`commands.rs:80,108`). Fix: killed the stale service + relaunched → the fresh v0.3.0
  sidecar honors the DeepSeek override — verified `/chat` (`{"answer":"Tuesday."}`) and
  `/chat_stream` both route to DeepSeek. (User has a stray `LLM_BASE_URL=:8765` export somewhere;
  harmless while the cloud override is sent, but worth removing.)
- Shipped: v0.3.1 DMG rebuilt (518 MB, signed `NotchyPrompter Dev`) + pushed to origin. Install
  over /Applications + relaunch to apply the threshold to **new** recordings.

**2026-06-24 #6 (Speaker diarization → v0.3.0; committed + pushed).** Remote participants split
into "Speaker 1/2/…" (mic stays "Me").
- **Engine:** sherpa-onnx `OfflineSpeakerDiarization` (pyannote-segmentation-3.0 ONNX +
  multilingual zh+en campplus embedding) — offline, no HF gating, cross-platform; chosen over
  pyannote (PyTorch/macOS-only + gated). Models ~34 MB download once to
  `~/.cache/adversaria/diarization`. Validated: 57s clip in 3.3s (~17× realtime); threshold 0.5.
- **Architecture:** diarize ONLY the system-audio WAV ("Me" already isolated via mic). New
  `diarizer.py`; `transcribe_dual`/`_merge_dual` relabel system segments by time-overlap (sparse
  speaker ids remapped to contiguous 1..N); `merge_labeled_segments` takes per-segment labels.
  Best-effort — falls back to "Them" on any failure.
- **Plumbing:** `diarize` flag AppConfig (default true) → `configured_diarize()` → transcribe
  request → `TranscribeRequest.diarize` → `transcribe_dual`. Settings toggle (DeepSeek), default on.
- **Packaging (see LESSONS):** declared `sherpa-onnx-core` explicitly (`uv sync` drops it);
  `collect_all("sherpa_onnx")` in the PyInstaller spec — **frozen-import validated (FROZEN_SHERPA_OK)**.
- Verified: 110 pytest + `cargo check` + `tsc` green; end-to-end diarization (Speaker 1/2/3).
- **Next:** the **batched DMG** (streaming v0.2.1 + diarization v0.3.0 — both touch the Python
  sidecar) re-freeze, then push.

**2026-06-24 #5 (Streaming chat → v0.2.1; committed on `master`, pushed).**
"Chat with Meeting" now streams the answer token-by-token:
- **Python:** `summarizer.chat_stream` + dual-backend `_chat_openai_stream` (SSE) /
  `_chat_ollama_stream`; new `/chat_stream` endpoint returns a `StreamingResponse` of SSE
  frames (`data:{"t":…}`, terminated by `[DONE]`; errors as `{"error":…}`).
- **Rust:** `http_client.chat_stream` reads the SSE via `resp.chunk()` into a BYTE buffer
  (multibyte-safe for Arabic), forwarding each token through a Tauri `Channel<String>`;
  `chat_with_meeting_stream` command persists the exchange + returns the full answer.
- **Frontend (DeepSeek-delegated):** `chatWithMeetingStream` (Channel) + `MeetingChat`
  appends tokens live, finalizes with the full answer, removes the placeholder on error.
- Verified: live DeepSeek stream (19 chunks), 110 pytest, `cargo check`, `tsc` all green.
  ⚠️ Python sidecar changed → needs the `build-dmg.sh` re-freeze to ship. **Next:** P2
  diarization (research + design + sign-off before any code).

**2026-06-24 (MCP server standalone — repo cleanup).** The `mcp-server/` directory was
moved to `~/Documents/Documents/MyProjects/mcp-server/` (a standalone repo consumed by
lagharilabs OS as a stdio MCP server). The old copy in this repo was deleted. The standalone
copy was fixed:
- Removed `keyring` + `sqlcipher3` imports (the encryption-aware MCP was on `feat/db-encryption`;
  the standalone pure-stdlib+mcp version is the stable path).
- Clean venv: `rm -rf .venv && uv sync` → exactly one `_editable_impl_adversaria_mcp.pth`.
- Import audit: all non-stdlib imports match `pyproject.toml` deps (`mcp>=1.2` only).
- Verified: `uv run adversaria-mcp </dev/null` exits clean, import resolves to standalone
  source, MCP handshake returns all 4 tools.

**2026-06-24 #4 (P1 DB encryption-at-rest — IN PROGRESS on branch `feat/db-encryption`,
NOT on master).** Decisions: **transparent keychain key** (random 256-bit in OS keychain,
no passphrase) + **fast-follow MCP update**. Done + verified (Claude's half of the split):
- `Cargo.toml`: `rusqlite` `bundled` → **`bundled-sqlcipher-vendored-openssl`** (self-contained;
  FTS5 preserved — confirmed via research + tests). Compiles clean (openssl-sys vendored, ~27s).
- `storage.rs`: key module (`get_or_create_db_key` via `keyring`, service `adversaria-db` /
  account `encryption-key`; **only `NoEntry` mints a key** — other keychain errors propagate so
  an existing encrypted DB is never orphaned); `open_keyed()` applies `PRAGMA key` at all 3 open
  sites (`init_db`, `connect`, `connect_for_sync`), key cached in a `OnceLock`; **in-place
  migration** (`migrate_plaintext_to_encrypted`: backup → `sqlcipher_export` → verify per-table
  row counts → atomic swap; bails without touching the original on any mismatch).
- Tests: 24 unit tests green incl. new `migrate_plaintext_roundtrip` + `migrate_noop_when_missing`;
  an `#[ignore]` `migrate_real_db` (env `ADV_REAL_DB`) ran against a copy of the **real** DB —
  **32 meetings / 51 actions / 10 chats preserved**, result requires the key.
- **MCP server (DeepSeek-delegated, DONE + reviewed):** `_connect()` now opens via `sqlcipher3`
  (built from source — `sqlcipher3-binary` has no macOS-arm64 wheel) + reads the key from the
  keychain via Python `keyring`, applying `PRAGMA key`; still reads a legacy plaintext DB.
  **Review caught a real bug:** the spec said `sqlite3.Row` but that raises `TypeError` on a
  sqlcipher3 cursor — fixed to `sqlcipher3.Row` (verified `row["title"]` works end-to-end). Note:
  reading the key from another process may trigger a one-time macOS keychain "Allow" prompt.
- **Docs (DeepSeek-delegated, DONE + reviewed):** ADR-011 in `DECISIONS.md` + a SQLCipher
  entry in `LESSONS_LEARNED.md` (the `sqlite3.Row` trap, key safety, FTS5). Review fixed the
  worker's over-escaped `\"` quotes + removed a stray `LESSONS_LEARNED 2.md` it created.
- **Released v0.2.0:** version bumped (0.1.3 → 0.2.0), CHANGELOG `[0.2.0]`, signed `.dmg`
  rebuilt; branch `feat/db-encryption` merged to `master` + pushed. ⚠️ First launch
  of the new build migrates the live `meetings.db` (backup kept) — user should confirm notes look
  right, then delete `meetings.db.pre-encrypt-backup`.

**2026-06-23 #3 (Assessment backlog + DeepSeek-delegated P0 quick-wins → v0.1.3; committed
on `master`, pushed; `tsc` + `cargo check` ✓; signed `.dmg` rebuilt).**
- Added an external product/eng review's findings as a prioritized backlog in
  `docs/TODO.md` (16 items). Verified its claims against the code first: "no Rust tests"
  was **false** (22 exist); "App.tsx 30+ useState" was 18; file sizes were accurate. The
  review under-weighted **DB-not-encrypted-at-rest**, which I rank P1 (it protects the
  sovereign-privacy thesis, above diarization).
- Started delegating P0 quick-wins to the **DeepSeek v4-pro stunt worker** (`opencode`
  backend, `STUNTMAN_WORKER=opencode STUNTMAN_MODEL=deepseek/deepseek-v4-pro`). Each
  planned by me → executed by the worker → diff-reviewed → `tsc`-verified by me. Done:
  1. Removed the lorem-ipsum `SAMPLE_RECAP`/`SamplePlaceholderCard` from `WeeklyView.tsx`.
  2. Friendly "AI model unreachable" message — new `src/lib/errors.ts::friendlyError`,
     wired into `AskAllView` + `MeetingChat`. Provider-agnostic (the app supports local
     AND cloud LLMs), so **no** hardcoded server command (unlike the review's suggestion).
- **DONE — quick-win #3 + v0.1.3 release.** Delegated the BYOK "Test connection" button to
  the DeepSeek worker (4 files: new Rust `test_llm_connection` command in `commands.rs` that
  does `GET {base_url}/models` with the key, registered in `lib.rs`; `testLlmConnection`
  wrapper in `tauri.ts`; button + result UI in `Settings.tsx`, shown for cloud providers).
  Reviewed + `tsc` + `cargo check` clean. Bumped 0.1.2 → **0.1.3**, moved CHANGELOG entries
  under [0.1.3], rebuilt the signed `.dmg`. All 3 P0 quick-wins shipped.
- **Next:** P1 **DB encryption-at-rest** (thesis-protecting; plan carefully — SQLCipher vs
  keychain-derived key + migrate the existing plaintext `meetings.db`). Then P1 streaming
  chat, then P2 (diarization → Kanban → installer). Backlog in [TODO.md](./TODO.md).

**2026-06-23 #2 (Ask-tab + meeting-toolbar UI fixes → v0.1.2; committed on `master`, NOT
pushed; signed `.dmg` rebuilt; `tsc` ✓).** Two more user-reported UI bugs:
- **Ask Across Meetings dropped the question.** Only the AI answer rendered and the question
  stayed stuck in the input. Fix (`AskAllView.tsx`): new `asked` state renders the submitted
  question as a right-aligned `.ask-chat-msg user` bubble *above* the answer, and the input is
  cleared (`setQuestion("")`) the moment the question is sent.
- **Meeting toolbar wrapped/cramped when the window is narrow.** Tab labels ("Chat with
  Meeting", "Personal Notes") broke onto 2–3 lines and the template/language selects +
  "Regenerate Notes" got squeezed. Fix (`prototype.css`): `.tab-link { white-space: nowrap }`
  so labels stay on one line, and `flex-wrap: wrap` on `.viewer-tabs-row` / `.viewer-tabs` /
  `.tab-actions` so the action controls reflow to their own line instead of being crushed.
- Version 0.1.1 → 0.1.2 + `CHANGELOG.md` entry. **Next:** install the new `.dmg`, confirm the
  Ask flow shows Q-above-A and that the toolbar reflows cleanly when narrowed; then `git push`.

**2026-06-23 (Weekly Recap polish + action-item extraction hardening — committed `0f13717`
on `master`, NOT pushed; version bumped 0.1.0 → 0.1.1 + new `CHANGELOG.md`; release `.dmg`
rebuilt via `build-dmg.sh` signed `NotchyPrompter Dev`; `cargo test` ✓ 4/4, `tsc` ✓).**
Two user-reported bugs:
- **Weekly Recap looked chaotic.** Root cause: `WeeklyView.tsx` reused `.btn-month-nav`
  (flex/centered/bold/15px) for the inline meeting-attribution link → each title became a
  big centered bold block; and "None mentioned" placeholder bullets were rendered as real
  decisions/topics. Fix: new `.weekly-meeting-link` class (inline/13px/muted, `--strong`
  variant for the Meetings list) + filter placeholders via new `isPlaceholderBullet()`
  (`summary.ts`). The "0/0 action items" in the screenshot was **timing**, not a bug —
  that week's 4 meetings truly had none; meetings 42/43 came after the screenshot.
- **Action items not populating (brainstorm/Arabic).** Extraction works for standard English
  (brainstorm id=26 → 10 items, id=42 → 4, all stored). Real drop found: Arabic meeting
  **id=5** had 6 items under `**عناصر العمل**` that the English-only `ACTIONABLE` regex
  missed → 0 stored. Broadened the regex in **both** `storage.rs` and `summary.ts` (must stay
  in sync) to also match `to-do`/`to-build`/`task` + Arabic headings. `backfill_action_items`
  (DB-init, fills meetings with 0 rows) recovers id=5 on next launch; data scan confirmed only
  id=5 changes (0→6), no regressions.
- **Done this session:** committed `0f13717`, bumped to **0.1.1**, added `CHANGELOG.md`,
  and ran a full signed release build (`build-dmg.sh` → `Adversaria.app` +
  `Adversaria_aarch64.dmg` under `src-tauri/target/release/bundle/`).
- **Next:** (1) install the new `.dmg` (drag to /Applications, replacing the old copy) and
  visually confirm the recap is de-cluttered and that id=5's Arabic to-dos now appear in the
  To-Do view (recovered by the startup backfill). (2) `git push` `master` when satisfied.
  See [LESSONS_LEARNED.md](./LESSONS_LEARNED.md) (top entry) for full detail.

**2026-06-20 (overnight, autonomous delegate+relay on branch `overnight/polish-batch`,
committed but NOT pushed).** Each item specced by Claude, built by the cheap stunt worker,
reviewed + `tsc`/`cargo check` verified before commit. Full branch green: `tsc` ✓,
`cargo check` ✓, **75 pytest** ✓ (Python untouched). Shipped, in order:
delete a meeting (chat-row cleanup + confirm) · pin a meeting (`pinned` column + migration,
pin-first sort, 📌) · editable summary (Edit/Save on Summary tab) · configurable auto-stop
(Settings; was hardcoded 5/10) · post-transcription auto-select fix · **tags made
per-meeting** + filter pillars keyed by label+color + stale-filter guard (fixes both the
"only one color shows" pillar bug and the `No meetings match ""` click bug) · consolidated
**To-dos** view · **"+ add to dictionary"** button · **Weekly recap** view · **privacy
lock** (per-meeting PIN, PBKDF2 — ⚠️ UI gate, DB not encrypted at rest) · **cross-meeting
RAG** ("Ask" tab) · **standalone notes** (note = meeting with no recording).
Plus two research specs (NOT built): `SPEC_CALENDAR.md`, `SPEC_DIARIZATION.md`.
**Next:** live smoke-test (full `npm run tauri dev` restart rebuilds Rust for the new
commands), then merge `overnight/polish-batch` → `master`. The earlier "pin/delete not
working" was a stale Rust binary, fixed by rebuilding. The 2026-06-18→19 entry below stands.

**2026-06-18 → 19:** Big UX + branding + strategy session; everything committed & pushed
to `master` (latest `b29970c`):
- **Shipped the full UX batch** (each specced here, built by DeepSeek via stuntman, then
  reviewed + `tsc`/`cargo check`/75-pytest verified + committed here): chat markdown +
  **persistent history**, meetings **search**, **colorful tags** + **auto-detected
  session type** (Meeting/YouTube/Brainstorm, mic-bleed-aware) + **click-a-pill
  rename/recolor**, **user-editable prompt templates**, **sidebar revamp** (filter
  pillars, drag-resize, padding; dropped the duplicate controls + dead back button),
  **silence auto-stop** (5/10-min). Commit refs in TODO.md "Done".
- **Renamed to Adversaria** + a Vane-style **intro splash** (azure `#24A0ED`, self-hosted
  Instrument Serif). NOTE: "VANE" was only a *style* reference (its color + serif), never
  the name; final product name = **Adversaria**, company = **Laghari Labs**.
- **STRATEGY.md** added — honest competitive/market read (Granola isn't sovereign; the
  local niche is crowded — Hyprnote/Meetily; demand is a *compliance* wedge, not a
  consumer one) + the reframe: **Adversaria = the sovereign capture organ of lagharilabs
  OS**. The next agent should read STRATEGY.md before proposing direction.

**Next up:** the **to-do board** (user's #1), then **diarization**; the **`.dmg`** track
whenever the user wants to install it daily; and **decide on pre-meeting notes** (see
"Where to go next"). The bigger play is **lagharilabs OS** (`~/Documents/Documents/
MyProjects/lagharilabs-os`) — but the user said **focus on Adversaria; don't deviate**
into the OS repo unless explicitly asked.

(Earlier 2026-06-18: macOS Xet model-download fix `HF_HUB_DISABLE_XET=1`; auto-detect
fourcc `'prl#'→'prs#'`; name/vocabulary; Brainstorm template. 2026-06-17: macOS port,
default model `qwen3.6:35b-a3b`, cream theme, Arabic — see git log.)

> ⚠️ If you change the Ollama model in Settings, pick one you actually have
> (`ollama list`). The app passes it straight through; an unavailable model
> makes `/summarize` fail.

> When you finish a session, replace this block with: what you changed, what's
> verified working, what's left, and anything the next person needs to know.
