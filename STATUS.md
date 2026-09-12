# STATUS (hackathon repo)

> **Current — 2026-09-12 15:43 GST: README updates pushed through `d76292e`;
> previous memory refresh pushed as `cbfc46f`. No new slide version created.
> Latest founder deadline: 16:30 GST.**

| Work | Status | Evidence / next step |
| --- | --- | --- |
| Desktop screenshot in README | Pushed | Existing meeting-note screenshot, accurately captioned; `53bcbf1` |
| CLI built with Codex; OpenRouter and Exa AI sponsor credits | Pushed | README wording and integration table; `d76292e`; whitespace checks passed |
| Automatic Exa and AI Tinkerers answer fix | Pushed and installed | `3b4df85`; 75 CLI tests and live synthetic/public regression checks passed |
| One-sentence pain-point slide | Brainstorming | Suggested: "Every meeting leaves me with hours of follow-up, while my own projects wait." No deck edits made |
| Existing Laghari Labs presentation | Ready | Eight reviewed slides; PowerPoint, PDF, offline HTML and notes |
| Separate CLI workspace dashboard changes | In progress; uncommitted and unverified here | Dashboard imports workspace/task navigation and background review controls; store revision method and dashboard tests added. Coordinate with owning worker, then verify before publishing |
| Demo rehearsal and submission | Next | Rehearse against the latest stated 16:30 GST deadline; a repo push does not submit the entry |

> **Chat fix checkpoint — 2026-09-12 15:32 GST: automatic Exa lookup enabled at the owner's
> request. The AI Tinkerers question now returns the community's description
> with official sources, instead of Hamza's project description.**

CLI retrieval now ignores question filler and requires subject relevance.
Outside questions search when evidence is missing or current facts are needed;
`--no-web` disables lookup. The dashboard accepts plain questions and shows
search progress/sources. All 75 CLI tests, Ruff and whitespace checks pass.
The installed `adversaria` command was refreshed; existing sessions need reopening.
Live text regression evidence is in [cli/PROVIDER_CHECK.md](cli/PROVIDER_CHECK.md).

> **Publish checkpoint — 2026-09-12 15:23 GST: owner authorized committing and pushing the
> complete hackathon work to `origin/main`. Copilot/Workspaces improvements, the
> CLI, README attribution/banner and the eight-slide Laghari Labs deck are ready.**

- Fresh checks: 437 frontend tests, 58 CLI tests, 507 Rust tests passed (one
  existing Rust test ignored). Production build, bundle/security checks, Ruff
  lint/format and Rust formatting passed. Rust tests used isolated data and the
  documented test-only bundle-resource override.
- [Provider checks](cli/PROVIDER_CHECK.md) record successful OpenRouter speech,
  model and Exa requests using synthetic/public inputs. These supersede the
  earlier missing-key and unsupported-STT notes below. Real microphone/loopback
  and native desktop demo rehearsal remain separate verification tasks.
- The [presentation](marketing/adversaria-story/README.md) includes editable
  PowerPoint, PDF, offline HTML and presenter notes. All eight slides reviewed.
- Local credentials, startup logs and private presentation build output are
  excluded from the commit.

## Earlier checkpoints

> **Earlier — 2026-09-12: Adversaria terminal edition built for OpenRouter + Exa +
> Codex credits. 39 CLI tests pass; Codex task execution and OpenRouter model
> catalogs verified live. Cloud speech/Exa rehearsal awaits keys. Uncommitted.**

| Terminal workflow | State |
| --- | --- |
| Interactive companion, commands, persistent workspaces/meetings/tasks | Implemented; command/PTY tests pass |
| Cloud file/live speech, OpenRouter default, optional OpenAI Realtime | Contract/capture tests pass; paid microphone rehearsal pending |
| Copilot questions + commitment approve/dismiss + serialized jobs | Tested; no task before approval |
| OpenRouter/OpenAI streaming + installed Codex engine | Tested; one real Codex diagram artifact awaiting review |
| Exa research, retained sources, artifact review/retry | Tested with mocked provider responses; key required for live search |
| Documentation, cross-platform launchers, installable CLI package | `cli/README.md`, `adversaria`, `adversaria.ps1` |

---

> **2026-09-12 14:55 GST — CLI copilot live on OpenRouter (7 s answers); record screen TUI in; 47 tests. Blocked: OpenRouter speech path (Codex must switch to audio-input chat, recipe in `.hackathon/`), Exa key not entered. Nothing committed.**

> **2026-09-12 14:46 GST — `cli/` terminal Adversaria on cloud credits (Codex-built, 39 tests): offline path verified, cloud path awaiting keys. Desktop: unchanged, green. Nothing committed.**

> **2026-09-12 13:25 GST — Compact companion layout, inline diagram preview in Workspaces, local Visualize contract: built and gated (437/437 frontend, 507 Rust, bundle 504.62/520). Dev app relaunched 13:22. Uncommitted. Unrehearsed.**

| Work | Status | Evidence / next step |
| --- | --- | --- |
| Companion compact layout (<900 px) + wide corrections | Done | 5 layout tests; Astra §1–2 fully landed |
| Workspaces inline SVG/HTML preview + one-column ≤1120 px | Done | 4 new tests; preview shows without expanding the row |
| Detector: visualize / present + diagram verbs | Done | 507 Rust tests incl. demo sentence caught end to end |
| Local Visualize output contract (one HTML+SVG, no drawio) | Done | 3 tests; never yet executed against Ollama |
| Rehearsal at ~480 px with a live Visualize run | **Pending — the gate before commit** | Founder; see `.hackathon/demo-script.md` |
| Commit 3 + HACKATHON.md + video + submit | Pending | After rehearsal |

---

> **2026-09-12 12:42 GST — Copilot + Workspaces polish done and live in the dev app. Rust 504 passed / 1 ignored (fmt + clippy clean); frontend tsc clean, 428 tests, bundle 500.65 kB / 520 kB. Commitment cards now carry a task-type control and track their own run to "Draft ready"; the Copilot panel separates CAUGHT from ANSWERS; the Live chip shows the time it was caught. Still uncommitted, and still not rehearsed with real speech.**

| Work | Status | Evidence / next step |
| --- | --- | --- |
| Commitment card: task type + in-card run progress | Done | `CommitmentCard.tsx` rewritten; 9 card tests; polls `getLatestWorkspaceRun` every 3 s |
| Rust `Commitment.capability` | Done | 2 tests added; `copilot-commitment` payload is now 12 keys |
| Copilot panel grouping + plain-language readiness line | Done | `RecordingCompanion.tsx`; readiness test updated to new copy |
| Workspaces Live chip provenance | Done | `live · 10:30` via `caughtLiveAt()`; no schema change |
| Bundle budget 500 → 520 kB | Done, documented | Dated comment in `scripts/check-bundle-size.mjs` |
| Native three-minute demo | **Pending — the one thing left** | Real speech, both channels, approve/dismiss, paused/resumed pickup, artifact before stop |
| Commit/submission | Pending authorization | No git writes made |

---

> **2026-09-12 12:24 GST — Hackathon commitment slice: Rust DONE (502 passed, 1 existing ignored; fmt/clippy clean), frontend DONE per its worker (425 tests, 498.08 kB). Native integration rehearsal pending. Today's implementation remains uncommitted. Next: parent integration review → Local recording demo with approve/dismiss and pause/resume → record actual demo evidence.**

| Work | Status | Evidence / next step |
| --- | --- | --- |
| Rust detector, events, commands, workspace task pickup | Done | 11 added tests; five owned Rust files changed; pinned contract retained |
| Rust gates | Passed with test-only override | Missing bundled `rapid-mlx` blocks the literal gate; use `TAURI_CONFIG='{"bundle":{"resources":[]}}'` with isolated `ADVERSARIA_DATA_DIR`; see HANDOFF |
| Frontend | Done per frontend worker | 425 tests, entry 498.08 kB; not rerun by Rust executor |
| Native three-minute demo | Pending | Confirm both channels, no creation before approval, Live task, artifact before stop, dismissal, and paused/resumed pickup |
| Commit/submission | Parent follow-up | No git writes or publication by Rust executor |

---

# STATUS

_The board — a **living doc**. Where the project stands right now; refresh it
every session. Deep detail lives in [`docs/`](./docs); this is the at-a-glance view._

> **Product:** Adversaria (privacy-first, bot-free, on-device meeting notetaker;
> company = Laghari Labs). Windows + macOS/Apple-Silicon.
> **2026-09-11 01:05 GST — 🟠 Companion layout de-noised (copilot focus in the narrow window, consent sentence collapsed, duplicate helper removed, tighter cards, stale notice auto-clears); tsc and 416 tests green, bundle 495.18 kB; four spec'd tests still owed; debug bundle rebuilding, app relaunch pending (founder recording).**
> **2026-09-11 00:10 GST — 🟢 Study pack pushed to `mhlaghari/interview-dossiers` (`study/GOLDEN-QA.md` tiered checklist of 137 Q&A, `quick-cards.md`, `README.md`, commit `f7c859c`). Founder revises Tier 1 (42) today, mocks with Adversaria, then the meeting.**
> **2026-09-10 23:30 GST — 🟢 Golden interview Q&A: 137 questions (53 actually asked by Wael, Dr. Yasser, Dr. Tamer; 66 not yet asked; 14 latency and cost; 4 audit additions), written by three workers, audited by Astra (127 corrections), rewritten, checked. Founder copy in the vault (`wiki/ideas/interview-golden-qa-2026-09.md`); copilot copy in `~/Desktop/Adversaria Copilot Sources/golden/` (15 files). Source root 111 files. Next: founder rehearsal, then commit.**
> **2026-09-10 21:10 GST — 🟢 Three project dossiers in the Interviews folder sources: Adversaria 25, ERDC 33, TIS 30 files (95 total, limit 200), all in the one-paragraph-per-file format, fact-checked against the founder's code-verified dossiers, every likely interview question mapping to its file in simulation. Stale root `erdc-overview.md` archived. Next: founder starts a session (readiness line should show 95 sources, pack 3 projects) and rehearses on Local and DeepSeek Flash; then commit.**
> **2026-09-09 00:45 GST — 🟢 SLICE 2 (interview copilot) BUILT and gated: Rust 491, Python 675, frontend 416 (494.56 kB). Answer shapes (STAR for experience), DeepSeek flash setting, local warm-up (first sentence 0.71 s right after warm-up), standing pack, card memory (follow-up "what is subject hash?" resolves), folder-first retrieval with acronyms, `Folder: … · N sources indexed` readiness line. Service restarted (PID 37763), debug app rebuilt 00:17 and running. Next: founder rehearsal on Local and DeepSeek Flash with the Interviews folder, then commit (not yet authorized). Deferred: speculative start, practice runner, close-after-NEXT.**
> **2026-09-09 00:20 GST — 🟠 SLICE 2 (interview copilot) BUILDING: three workers running (Rust Codex gpt-6-astra, Python Antigravity, frontend Muse) on the pinned contract `.recon/interview-copilot-20260908/spec2-pinned.md` (answer shapes, DeepSeek flash + local warm-up, standing pack, card memory, evidence that wins, folder readiness). Practice runner and speculative start deferred to after the interview. Tree backed up; commit authorization pending. Next: gates, review, feedback round, debug bundle, founder rehearsal.**
> **2026-09-08 23:40 GST — 🟢 Copilot scoped to interviews (founder decision); Adversaria technical dossier written (25 fact-checked files, one topic each, built for the folder-docs retrieval tier) and placed in `~/Desktop/Adversaria Copilot Sources/adversaria/`; slice 2 interview contract drafted with Astra (`.recon/interview-copilot-20260908/CONTRACT-2-interview.md`), awaiting go. No code changed; gates unchanged (Rust 473, Python 666, frontend 412). Next: founder refreshes or edits the folder profile, sets purpose, voice samples and DeepSeek default, starts one recording to index the dossier, then decides on slice 2 (evidence that wins, card memory, practice runner) before the interview.**
> **2026-09-07 20:30 GST — 🟠 Slice 1.5 founder-tested with the Interviews folder (first person, ERDC-grounded, no leaks, 1 to 2 s); four defects fixed in slice 1.6 (folder fallback, CV-first profile + editable, AI-identity and mis-heard-term prompt rules, notes relevance floor, drop frames).** Gates: Rust 473, Python 666, frontend 412 (493.23 kB). Bundle rebuilding; next: swap app, founder re-test with DeepSeek + voice samples, then slice 2 (running summary, local judge, help hotkey, practice list) and slice 3 (gate harness).
> **2026-09-07 08:20 GST — 🟠 Slice 1 founder-tested ("better, not quite there"): context leaks from unrelated projects with no folder, encyclopedic voice, chatbot follow-ups. SLICE 1.5 in progress: folder sources + scoped retrieval + folder profile + voice samples + spoken/relatable prompt.** Frontend (408 tests, 492.74 kB) and Python (665 tests) accepted; Rust worker running. Next: review Rust, rebuild debug bundle, set up the Interviews folder with the founder, native re-test.
> **2026-09-07 01:40 GST — 🟠 Copilot rev 6 slice 1 BUILT (Codex GPT-6 Rust, Antigravity Python, Muse frontend), orchestrator-reviewed, gates green: Rust 437, Python 660, frontend 399, bundle 491.09 kB. Uncommitted on `feat/live-copilot-c`.** Contract/specs in `.recon/copilot-rev6/`. Service restarted on the new code; `qwen3.6:35b` streams the first say sentence in 0.28 s warm. Debug bundle rebuilt 01:14 and running (PID 79611); service PID 12193; `copilot_local_model` set to `qwen3.6:35b` and pre-loaded. Next: founder native test, then slice 2 (meeting layer, judge, voice anchors) and slice 3 (gate harness).
> **2026-09-06 23:50 GST — 🟡 Copilot rev 6 direction approved: answer first, notes as evidence (concept board published, no code changed).** Board `.recon/copilot-answer-first-20260906/index.html`, artifact https://claude.ai/code/artifact/9a06f964-edd5-40a4-99a1-940249e60bf3. Cards rewritten once after the founder called v1 "AI sloppy" (say line ≤ 20 s, specifics only, numbers from notes or [blanks], voice samples); acceptance gate = founder rates 20 real interview questions ≥ 4/5. v3 adds the meeting layer (header at record start + on-device running summary + wider Local context) and makes Local first-class with its own model (today `qwen3.5:4b`; proposed `qwen3.6:35b-a3b`). Astra (GPT-6) brainstorm done 7 Sep (`.recon/copilot-answer-first-20260906/astra-brainstorm.md`): three sample say lines had puncturable claims, so the digit rule becomes a claim rule; say-line hold contract; hybrid detector; summary-to-cloud behind opt-in; local benchmark `qwen3.6:35b`; gate freezes evidence at question time. Board v4 published 7 Sep with the corrections folded in; summary-to-cloud, detector and local model decided. Next: rev 6 spec from board v4, then multi-worker delegation and the blind gate. Rev 5 remains the running code, below.
> **2026-09-06 18:20 GST — 🟠 Realtime Copilot rev 5 answer feed + context-aware complete questions + manual DeepSeek retry correction implemented and open for native testing (uncommitted, `feat/live-copilot-c`).** Founder-approved artifact: `.recon/copilot-feed-concepts-20260906/index.html`. The Copilot tab is a flat streaming answer feed with collapsed Context and Sources. The sidecar marks forced cuts vs silence; Rust joins forced chunks into one speech turn and freezes the complete current question plus up to four recent Me/Them turns. The 18:11 screenshot exposed a completed No AI card being mistaken for in-progress work after switching to DeepSeek; manual Ask now permits a completed-question re-ask, active duplicate clicks remain blocked, and each row shows its frozen provider. Gates: frontend **383**, Rust **420 + 1 ignored**, Python **652 + 1 skipped**; build/bundle/security, fmt/clippy, Ruff and `git diff --check` green. Corrected debug app PID **21253** has one visible native window; current-tree service PID **74571** is fully ready. Installed `/Applications/Adversaria.app` remains unchanged. A DeepSeek-labelled native answer is the next test.
> **2026-09-06 13:31 GST — 🟠 DeepSeek Realtime Copilot implemented and ready for a credentialed smoke test (uncommitted, `feat/live-copilot-c`).** AI · DeepSeek uses a separate keychain credential, fixed `https://api.deepseek.com` endpoint and `deepseek-v4-pro` model, bounded context disclosure, no web search, provider-frozen retries, distinct provenance/receipts, and pre-socket endpoint validation. Gates: frontend **381**, Rust **417 + 1 ignored**, Python **651 + 1 skipped**; TypeScript/build/bundle/security, fmt/clippy, and changed-file Ruff checks green. A debug bundle containing the work is running while the healthy service listens on `127.0.0.1:9876`; no real DeepSeek request has run because the key has not been entered. Installed `/Applications/Adversaria.app` remains unchanged.
> **13:35 GST smoke correction:** the key is now saved. The first test was rejected locally because the manually launched service was older than the DeepSeek source changes; no provider call occurred. The service has been restarted from the current tree and is fully ready. Repeat the test to exercise DeepSeek itself.
> **2026-09-05 23:21 GST — 🟠 Realtime Copilot v2 implemented; final audits have no open P0/P1 (uncommitted, `feat/live-copilot-c`).** Rev 3 as-built spec: `docs/superpowers/specs/2026-09-05-realtime-copilot-v2.md`. Consent-safe Retry, complete Claude disclosure, session UUIDs, latest-intent queue, registered Local endpoints, guarded terminals and companion UI are implemented; the expressive bubble headline is deferred. Automated gates: Frontend 41 files / **377 passed**, TypeScript/build/bundle/security clean; Rust **414 passed / 1 ignored**, fmt/clippy clean; Python **645 passed / 1 skipped**, Ruff clean; focused replay **25/25**. Regenerated E1a dry run has 0 executed/passed and live replay is an honest offline skip; no model was started. Operator runbook is ready at `.recon/realtime-copilot-20260905/native-runbook.md`. Installed app remains the earlier 0.3.83 build and does not contain these final v2 changes. E1b/E3/E4 remain `pending native capture`; deterministic native queue stress needs a delayed instrumented engine; E2 remains `pending credential`.
> **2026-09-05 18:35 GST — ✅ Local build installed to `/Applications/Adversaria.app` and running.** Signed/notarized rebuild of uncommitted `feat/live-copilot-c`, version still 0.3.83; accepted To-dos CSS is now in the installed app alongside Copilot/export work. Native To-dos checked at one existing 1024×720 Laghari-theme viewport (stacked cards, readable single-line dates); transcriber, embeddings, live captions ready. DB 241 meetings / max id 298 unchanged, quick_check OK. Original release artifacts preserved separately; see [docs/HANDOFF.md](./docs/HANDOFF.md).

## Next steps

- In the open debug app, select **AI · DeepSeek**, speak one long context-dependent question that crosses live-caption lines, pause, click **Answer current question** once, and verify one fresh DeepSeek-labelled answer plus the exact Me/Them **Context** disclosure.
- Founder option: run the native operator runbook (`.recon/realtime-copilot-20260905/native-runbook.md`) for **E1b** (AI Local) and **E3** (under load); configure Anthropic separately for E2 Claude.
- Founder decides whether to commit and schedule a release build incorporating Realtime Copilot v2 and DeepSeek. Do not publish current local DMG/updater/provenance outputs as the original public 0.3.83 release; see [docs/HANDOFF.md](./docs/HANDOFF.md).

> **Historical — 2026-09-05 To-dos preview accepted ("looks good"); Codex prefs installed, no release.** `src/prototype.css` fix preview was accepted; an installed rebuild was pending then, superseded by the 18:35 GST installation. History: grid `60eaf61` Jul 18 / pastels `6512724` Jun 22 → Laghari `de89f8f` Aug 13 gap caused latent sizing/theme bug; trigger unproven. Codex: `~/.codex/config.toml` `approval never`/`danger-full-access`, notify wrapper preserves Sky turn-ended + `task-complete.wav` (`HCn94mNuICk` 7.11–7.84→0.73s); parent verified 8 tests PASS, 3-key TOML preserved, wav byte-equal; backup 20260905T115736; new sessions were needed; no rebuild/commit/DB during that earlier session; one review round.

## Historical board — Sep 4 / Sep 3 and earlier

The dated board below records earlier state and plans; current state and Next steps above supersede it.

> **09-04 (~05:00) — 🟠 SLICE C BUILT on `feat/live-copilot-c` (UNCOMMITTED; answer
> stream + consent + keychain key + provenance + receipts; gates: tsc · vitest 328 ·
> cargo 382 · pytest 586, all green on Claude's run) · 🚀 0.3.83 PUBLISHING: public
> mirror merged at 0.3.83 (+ Windows path-separator fix `b86e912`), Windows CI
> building, macOS artifacts verified; publish + manifest check pending. Live smoke
> of the copilot and an Anthropic API key are the next founder steps.** Earlier:
> **09-03 (evening) — 🔍 Competitor assessment: DoodleNote (doodlenote.ai)
> researched by three agents; verdict + gap list in
> [docs/DOODLENOTE_COMPARISON.md](./docs/DOODLENOTE_COMPARISON.md); six gap
> items added to docs/TODO.md; no code changed; founder next step unchanged
> (publish 0.3.83).** Earlier: **09-03 (09:40) — ✅ MERGED INTO MASTER `b6222c2` (not pushed): follow-up
> check, Live Copilot A+B (no model), themed exports, `.adversaria`, review
> fixes; gates green on master. Next for the founder: publish 0.3.83 (public
> is 0.3.82), fix the junk-row cleanup range (260–292 only; 293–296 are real),
> then 0.3.84 / slice C. HANDOFF top has the ordered list.** Earlier: ✅ second review round done: F3 formatting + F4
> relevance floor / title strip landed (cargo 372, vitest 306). Founder
> re-check → merge / 0.3.84 / junk-row cleanup / Claude creds decisions
> pending.** Earlier: ✅ F3 formatting landed (`f714325`: compact tabs, safe
> passage rendering, clamp + Show more; an unescaped-HTML render and a
> worker's phantom tests were caught in review). F4 relevance floor still
> building.** Earlier: 🛠 second review round in flight: compact tabs +
> readable copilot passages (Muse; an unescaped-HTML render was caught in
> review and is being redone as React nodes) and retrieval relevance floor +
> title strip (Antigravity). Layout fix confirmed by the founder ("much
> better"); copilot card works end-to-end. Earlier: ✅ Founder review fixes landed (`73fcf81` companion layout +
> PDF-opens-print flow, `1f6f701` copilot force-card fallback); themed deck
> and `.adversaria` export verified working; founder re-checking; merge /
> 0.3.84 / junk-row cleanup / Claude creds pending.** Earlier: ✅ OVERNIGHT: exports built too (`39b6782`: theme-matched
> slide/PDF, `.adversaria` document with uids/folders/open-with). Four
> feature commits on `feat/live-copilot`, unmerged, dev stack running for
> the founder's review (checklist in HANDOFF).** Earlier: ✅ LIVE COPILOT slices A+B COMMITTED on `feat/live-copilot`
> (`34d04a2`, `23ab875`), gates green, dev stack left running for the
> founder's morning review (Mac was locked → no UI drive). Next overnight:
> theme-matched slide/PDF export + `.adversaria` bundle format (Codex map in
> flight).** Earlier: 🛠 LIVE COPILOT slices A+B BUILDING on `feat/live-copilot`**
> (founder: build in Adversaria; Interview Assist = second shell later).
> Phase 1 in flight: Codex (Rust folder brief + copilot_mode) ∥ Muse
> (companion tabs Notes · Last time, record-start folder). Phase 2 next:
> Antigravity (detector + retrieval + copilot-card) ∥ frontend Copilot tab.
> Follow-up feature committed `2818ee7` on its branch, unmerged. Earlier:
> **09-02 (late) — 🧭 LIVE COPILOT direction locked (ADR-020), spec v1 +
> visual done, scouts done.** Rail beside the transcript: your notes first
> (deterministic), Claude + web after, every bullet labeled, "Not in your
> notes" over invented experience; one consent switch No AI · AI Claude · AI
> Local; local-first becomes reassurance, capability the headline. Spec:
> `docs/superpowers/specs/2026-09-02-live-copilot-design.md`. Probe done:
> confirmed caption 1.68 s, partial carries the question 0.5–2 s early,
> retrieval 32 ms, local 4B/35B card 0.5/0.8 s → sub-second cards locally;
> Claude unmeasured (no credentials on this Mac). All four scouts done; spec v1.2 carries
> the code map (hook = after de-dup in `feed_live_source`, bounded worker;
> consent enforced in Rust; folder identity at record start missing) and
> the OSS verdict (fork none, GPL; Interview Assist = second thin shell).
> Waiting on the founder's go + Claude credentials; local-under-load probe
> still needed before the local model becomes the AI default.
> **09-02 (evening) — ✅ BUILT + VERIFIED, UNCOMMITTED: attached previous
> meeting → visible follow-up check (`feat/meeting-context-followup`).**
> Founder attached a meeting while recording and the notes showed nothing.
> Now: Rust sends the attached meetings' OPEN to-dos (`prior_meetings`),
> Python renders a deterministic "Follow-up from <meeting>" section
> (Done/Discussed only with a verbatim transcript quote, else Still open),
> the note shows a "Context used" chip strip, the companion says what
> attaching does. Recon (Antigravity probe + Muse survey + Antigravity code
> map) → 3 specs → Antigravity ×2 + Muse built it; Claude verified every gate
> (pytest 579 · vitest 253 · cargo 349, all green) and a real-model run.
> ⚠️ The first Rust tests wrote 33 fixture meetings (ids 260–292) into the
> founder's REAL DB — fixed (in-memory tests) but the rows need the founder's
> delete (command in HANDOFF top). Bug triage: no live bugs in the backlog.
> **08-27/28 — 🧭 WORKSPACES DESIGN RESET (locked, build deferred).** Founder
> rejected the staffing-UI direction; workspace = artifact factory (NO repo
> writes — parked), one workspace = one project, single-column screen, transfer
> per action item, output format chosen via chips (skill follows format).
> Board (4th pass): https://claude.ai/code/artifact/3deb99ac-d9b7-481f-93be-d6ad82d85cd2
> Build order agreed, NOT started ("we will do this later"). Full ledger of
> locked decisions + Codex-verified findings in HANDOFF (08-27/28 block).
> **09-02 (night → morning) — 🚢 0.3.83 CUT on master (signed; notarization
> finishing automatically).** Founder: ship live captions now, no workspaces
> (dev-gated anyway), redesign tomorrow. `preview/all2` → master `8bfb0ef`,
> bump + CHANGELOG `95eebd1`, NOT pushed. Release build green through the
> signed DMG (Developer ID, deep-verify OK, updater sig key = pinned verifier,
> sherpa_onnx frozen). Stage 7 failed while the Mac was locked (data-protection
> keychain unreadable; LESSONS 2026-09-02); a 12 h loop retried and the
> credential came back at 07:33, submit in flight — HANDOFF top has the finish
> checklist and the public-release steps (push/sync/Windows CI/publish await
> the founder's word).
> **Workspace redesign direction (founder + Claude, 09-02):** the local model
> CURATES context (extractive, every passage cited, from meetings + vault +
> folders) and Claude Code / Codex EXECUTES; the curated brief is the exact
> payload that leaves the machine, shown before the run ("Will send: …") as the
> per-run opt-in ADR-002 promised. Keep the two panes (founder: "the split
> view … is good"); add the Bench lifecycle (bench strip, review sheet with
> source-excerpt peek, one-sentence Redo, Accept only in the sheet + undo).
> Open decision: two panes + Bench (Claude's recommendation) vs the Bench
> board's single column. Slices W1–W4 + the curation-speed probe in TODO 09-02.
> **09-01 (night) — ✅ LIVE CAPTIONS BUILT + VERIFIED + FOUNDER-SEEN LIVE +
> COMMITTED on `feat/live-captions` and MERGED into `preview/all2` (founder
> authorized; not pushed, not on master).**
> Two-tier live transcript per ADR-019: grey English preview (Moonshine v2 tiny
> via sherpa-onnx, 500 ms re-decode of the unconfirmed tail, 8 s hard cap,
> loop-trimmed, English self-gate) replaced per utterance by the confirmed
> Whisper caption; `live-captions-en` 44 MB pin auto-downloads once; Settings
> row + `/health.live_captions_state`. Recon: Muse (Windows Live Captions =
> on-device embedded speech, no public API) + Antigravity (empirical probe
> overturned "Moonshine streams in sherpa" — offline only; Zipformer ALL-CAPS
> ~20% WER rejected). Gates re-run by Claude: 566 py · 249 vitest · 344 cargo ·
> tsc/ruff/fmt/clippy clean. Real-service e2e: first grey words at 0.5 s,
> 50–125 ms/poll. Founder, using the dev app live: "it was super cool … the
> coolest thing that you've ever done." Baton: HANDOFF "NEXT SESSION (2026-09-01,
> night)".
> **09-01 — 🧭 SESSION CLOSE: live-captions DECIDED (two layers, one
> sherpa-onnx integration hosting Moonshine EN in python-service for BOTH
> platforms; layer 2 = today's pipeline as authoritative, per-utterance
> replacement); Workshop Bench board delivered (five-model open round,
> convergent) awaiting verdict; Qwen probe: quality real, 59 min, invents
> when ungrounded. All work on preview/all2, unmerged. Founder starting a
> new context — docs/HANDOFF.md "NEXT SESSION STARTS HERE" has the baton.**
> **08-31 (click-through round 2) — 🚧 E1/E2 + live-captions research.**
> Founder feedback: workspace task cards messy (want compact clickable rows:
> run button, progress circle, Reveal/Approve/Reject inline, reject = inline
> "what should change" + auto-rerun, details only on row click) and the MIQ
> diagram run produced "nothing". Diagnosis (code-confirmed; dev DB is
> SQLCipher-encrypted so no direct read): on the LOCAL engine an attached
> folder contributes only its PATH to the brief, never contents, and the new
> grounding rule then honestly declines. UPDATE: E1 ✅ `b06ea82` (compact
> clickable rows, 242/242 serial) and E2 ✅ `0423ebc` (bounded folder excerpts
> into LOCAL briefs, grounding rule counts them, receipt says "folder excerpts
> inlined"; 344 cargo, clippy clean) BOTH LANDED on preview/all2; app restarts
> with them and the MIQ diagram re-run now has real project content.
> [superseded wording:] E1 (compact rows, Codex) was in flight on
> preview/all2; E2 spec staged (`spec-folder-content-1.md`: bounded prioritized
> folder excerpts into local briefs + receipt note), launches after E1.
> Also: Windows Live Captions research done and recorded in docs/TODO
> (2026-08-31 🔬 entry, committed on preview/all2): streaming-transducer vs
> our utterance-chunked Whisper; adoption tiers (LocalAgreement partials →
> Moonshine/Zipformer live engine → Apple SpeechAnalyzer Swift sidecar);
> recommendation a-then-c, awaiting founder call.
> **08-31 (click-through round 1) — ⚖️ FOUNDER'S MODEL: FOLDERS vs WORKSPACES
> + two live fixes + 🔴 hallucination root-caused.** Founder's call (verbatim
> intent): Meetings side renames to FOLDERS (pure organization: a project, a
> meeting type, anything); WORKSPACES are the projects (coupled tasks, e.g.
> MIQ); the two are decoupled surfaces ("not connected per se").
> Fixes shipped to preview/all2 + cherry-picked to feat/workspace-rebuild:
> (1) `306b900` push-to-workspace menu never locks: workspace click STAGES
> the send, capability chip completes it, New workspace always available;
> plural keywords match ("diagrams"→visualize, regression test).
> (2) grounding fix: the MIQ hallucination happened because the run brief
> includes ONLY workspace-attached meetings, never the pushed to-do's source
> meeting; a fresh workspace briefed the model with zero meeting content.
> Now the source meeting always rides in the brief, and every brief ends
> with a Grounding rule (empty context ⇒ say so + open questions, never
> invent). Verified: 242/242 vitest · 338+1 cargo · clippy.
> IN FLIGHT: slice D1 (Codex): folders/meeting_folders/folder_overviews
> tables + one-time migration copying today's meeting-side projects into
> folders, full meetings-side rename, FolderView (no workspace coupling),
> workspaces untouched. Spec: scratchpad `spec-folders-1.md`.
> D1 UPDATE: first pass landed backend (folders/meeting_folders/
> folder_overviews + one-time migration), MeetingsList and FolderView, but the
> session capped BEFORE App.tsx converted — tree does not compile; dev app
> shows a Vite overlay until the resumed Codex session (same session id, in
> flight) finishes App.tsx + two test-fixture files and reruns the full gate.
> D1 DONE (`32f556b` on preview/all2): Codex landed backend/MeetingsList/
> FolderView; its session capped twice on the App.tsx conversion, so Claude
> finished App.tsx + test fixtures directly (workflow's take-over rule).
> Migration reviewed line-by-line: transactional, guarded, copies groups into
> folders, preserves workspaces/bindings untouched. Verified: tsc clean,
> 233/233 vitest (serial; parallel flakes were dev-app load contention),
> 339 cargo, clippy clean. NOTE: preview/all2 is now the INTEGRATION branch
> (fixes cherry-picked back to feat/workspace-rebuild, but D1 lives only on
> preview/all2); the founder's merge decision should merge preview/all2.
> Meetings sidebar now says Folders; FolderView has no workspace coupling;
> the dev app restarts into the folders world and runs the migration on the
> founder's dev DB at next launch.
> **08-31 (later) — ✅ CAPABILITY REWORK LANDED (C1 `4faad57`, C2 on branch),
> Claude-reviewed + verified (tsc · 236/236 vitest · clippy · 336 cargo);
> preview/all2 assembled (all 5 branches, one trivial import conflict
> resolved) and verified (242/242 · 337 cargo); dev app RUNNING on it for the
> founder's click-through.** The workspace now speaks capabilities end to end:
> 4 chips both surfaces, baselines never gate, ambiguity waits one click,
> two-pane screen with live drafted-task grounding preview
> (`preview_task_grounding`). Remaining, not specced: C3 durable project
> identity + validated PNG/SVG export. Merge train to master still awaits the
> founder's word after this click-through.
> **08-31 — ✅ DESIGN APPROVED ("Yeah looks good") + REWORK IN FLIGHT.**
> The debate-verdict design board (two-pane workspace, capability chips
> Research/Write/Visualize/Present, baseline-always, adapters optional,
> ambiguity waits one click, to-do auto-grounded from the vault, artifact
> lifecycle with report + exports + receipt):
> https://claude.ai/code/artifact/54c73e5a-2077-4ce1-bc81-e217ede4983d
> Rework running on `feat/workspace-rebuild`: slice C1 (Codex) converts the
> format model to capabilities (column, adapter map, catalog-independent
> suggestion with tie=ambiguity, baseline Deliverable contracts in the brief,
> run-gating removed, 4 chips everywhere incl. the To-dos menu). C2 spec is
> PRE-WRITTEN (scratchpad `spec-capability-2.md`): two-pane screen + a new
> `preview_task_grounding` command for the right pane's drafted-task card.
> Pipeline on founder request: C1 review → C2 → fresh preview merge of all
> branches → boot the dev app to show him. Nothing merged to master.
> (08-31 addendum: the design board's background checker stalled without a
> verdict; Claude re-ran the checks directly, board verified clean. C1 still
> building at this writing; the worker's uncommitted edits live on the branch.
> Progress check on founder ask: 9 files, +420/-302, final verification not
> yet started; no stall.)
> **08-30/31 — ⚖️ FOUNDER REJECTED the single-column screen + format-chip
> emphasis; THREE-MODEL DESIGN DEBATE RUN (codex/agy/muse, 2 rounds, vault's
> Bull/Bear-Judge pattern). CONVERGED VERDICT:** capability-typed tasks
> (Research / Write / Visualize / Present, Analyze folded in), an
> always-available validated HTML/SVG/Markdown baseline with PNG/SVG export,
> tool skills (draw.io, Marp) as OPTIONAL adapters that never gate ordinary
> output; block only AMBIGUOUS INTENT (one-click capability pick), never a
> missing tool; two-pane screen restored (work left, grounding/provenance
> right, thin header); durable project identity on the workspace
> (canonical_root, vault note, aliases) + read-only repo mount for grounded
> analysis; human to-dos get no badge, explicit "Ask AI to help" override.
> Shared riskiest assumption: local-model HTML/SVG quality — mitigation is a
> validated render/export step + honest run reports. Proposals + critiques in
> session scratchpad (proposal-*.md, critique-*.json). AWAITING FOUNDER CALL;
> rebuild branch slices R1/R2/R3 to be reworked to the verdict, R4 keeps.
> Also NEW: `feat/todos-done-view` — one-click Done view on the To-dos board
> (founder ask), verified 231/231.
> **08-30 (night) — 🏗 WORKSPACE REBUILD BUILT: the locked 08-27 design, all
> four slices, on branch `feat/workspace-rebuild` (4 commits, Codex-built,
> Claude-specced/reviewed/verified; dev-gated; NOT merged, NOT pushed).**
> Slice 1 `596df03` format chips (skill follows format, matcher suggests only
> at score >= 3, missing formats dashed + run-gated, per-task staffing UI
> DELETED, table/resolution kept as plumbing — also closes the 08-26 🔴
> silent-wrong-skill by construction). Slice 2 `d0a884b` single-column screen
> (knows-line header, standing instructions above the work, Needs you /
> Running / Queued / Done, engine+sources into a collapsed Project settings).
> Slice 3 `817a84a` To-dos transfer requires a format (same chips + suggestion
> in the per-item menu, both send paths). Slice 4 `b23083a` runs report what
> they did (best-effort notes-engine report stored on the run, shown above
> artifacts) + briefs state network access with a Sources-fetched demand (the
> 08-26 🔴 network-gate unblock, second half). Every slice verified by Claude:
> final state tsc clean · 231/231 vitest · clippy strict · 335 Rust tests.
> Main checkout restored to master.
> **08-30 (later) — 🤖 THREE-AGENT FLEET RUNNING (worktrees, review pending).**
> Codex → `fix/transcribe-watchdog` (per-request reqwest timeouts on
> health/transcribe/summarize + 45-min queue watchdog in useRecording; the 🔴
> queue-wedge bug). Antigravity → `feat/related-meetings` (new
> `related_meetings` command reusing embeddings + select_related_meetings;
> Summary-tab card, max 3, human reasons, click-to-open). Muse →
> `docs/readme-refresh` (accuracy pass grounded in CHANGELOG/STATUS/
> ARCHITECTURE; LinkedIn placeholder kept). Worktrees ../mnt-wt-{wedge,related,
> readme}; specs in the session scratchpad. Claude reviews each diff + runs
> verification, then merges to master ONE AT A TIME with founder's word.
> Person-rename TODO closed (founder: works in daily use); its unexplained
> transcript-occurrence note preserved under Done.
> **08-30 — 🚢 0.3.82 CUT (release in flight).** Bump committed (`b5695b2`) +
> clippy test-fix (`eb6f33a`, public CI runs a NEWER clippy than local — three
> slice-from-ref lints in overview tests; binary unaffected). Public mirror PR
> #29 all-green and MERGED, public main verified at 0.3.82. macOS: notarization
> ACCEPTED (id 667e2184), stapled + validated, stable-name DMG regenerated
> after stapling. Windows: CI run 33306628912 in progress (watcher armed).
> **SHIPPED & VERIFIED same day:** Windows CI green, artifact downloaded,
> published to adversaria-releases v0.3.82 with BOTH platforms. Post-publish
> verification PASSED (live manifest 0.3.82, both assets download + sha256
> match provenance + minisign valid, both sig key ids = the pinned verifier,
> stable-name DMG on the release, all URLs 200). Contents: projects in the Meetings tab,
> project screen with AI overview + standing instructions + network switch,
> Meeting Room, new summarization templates (first freeze that activates
> them), attendee-rename blur fix. Feature commit `635101f` reviewed by Claude
> (tsc clean · 225/225 vitest · 330 cargo tests) and pushed to origin/master.
> **08-29/30 — ✅ PROJECTS IN THE MEETINGS TAB: BUILT + VERIFIED + COMMITTED (`635101f`, pushed).**
> Founder saw the renders and said build it, so the projects surface goes FIRST
> (supersedes the 2-3-1 recommendation's order; related-meetings slice moves to
> next). Design board (6 artboards, approved "this looks sexy"):
> https://claude.ai/code/artifact/5c77498d-b19a-4b89-8c4f-15374abf81b5
> **Slice 1 ✅ landed (in `635101f`), Claude-verified:** workspaces
> gained `instructions` + `color` (idempotent migrations), 3 new IPC commands,
> sidebar Projects section (folders/counts/expand, + New project popup),
> Move-to-project menu with graph "suggested" marker, drag-to-file, note-header
> project chip, suggestion banner on unfiled notes. tsc clean · 207/207 vitest ·
> cargo check clean · 51 Rust workspace tests. Zero feedback rounds.
> **Slice 2 ✅ landed too (in `635101f`), Claude-verified:** ProjectView screen
> (standing instructions editor with explicit Save, network switch, meetings
> card, open action items with working checkboxes), sidebar selection wiring
> (row selects + expands, chevron-only toggles), "Open in Workspaces" dev-only.
> tsc clean · 214/214 vitest (25 files). Zero feedback rounds on both slices.
> **ProjectView refinement ✅ landed (UNCOMMITTED):** the project canvas now
> fills a centered 1440px responsive area with independent overview/meetings
> + project-controls and action-item columns. Action text gets the full row; its source
> meeting is clickable metadata underneath. Added a cached, source-grounded AI
> Project overview plus deterministic attendee frequency chips. Standing
> instructions now actually feed both overview generation and workspace task
> briefs; Web research copy now reflects its real scope. Follow-up 08-30: removed
> the overview's premature 65ch wrap, moved Standing instructions + Web research
> beneath Meetings, and versioned the overview prompt/cache so five filed meetings
> cannot be mislabeled as two events. Added confirmed project deletion in the
> Meetings sidebar; meetings survive unfiled and binding cleanup is tested.
> Delete ⋯ is now permanently visible (not hover-only); native click-through
> reached the named confirmation dialog after restarting a stale dev window.
> Native wide-window QA passed. Gates: tsc clean · 225/225 vitest · cargo fmt/check clean · 330 Rust
> passed (1 ignored) · layout detector clean.
> Stuntman/repo documentation contract audited 08-30: README, SPEC,
> ARCHITECTURE, TODO, DECISIONS, LESSONS_LEARNED, DEEP_DIVE_TECHNICAL,
> HANDOFF, and STATUS now reflect the project work. STRATEGY was reviewed and
> intentionally unchanged because no strategy or market direction changed.
> NEXT: founder click-through in the dev app, commit on authorization, then the
> related-meetings slice. Record-start "File under" door DEFERRED (suggestion
> engine needs title+summary; no calendar signal yet).
> **08-29 (later) — ⏭ SEQUENCING: recommended 2→3→1, awaiting founder call.**
> (1) workspace rebuild · (2) related meetings under the note · (3) projects in
> the Meetings tab. Recommendation: related-meetings first (1 slice, retrieval
> exists), then projects (surface over existing bindings + instructions field +
> network toggle), workspace rebuild LAST so its UI is built once on the
> settled container. Full reasoning: HANDOFF "NEXT SESSION STARTS HERE" block.
> **08-29 — 🧭 UNIFICATION (design only): threads + workspaces = ONE "meeting
> workspace" per project, two faces (meeting/record/live-rail · work/tasks/
> artifacts). Artifacts join the project memory and feed the next meeting's
> rail. Copilot intent articulated (retrieval-first safe, generation risky).
> Boards to merge into one on founder's call. Nothing built. Detail: TODO 08-29
> + HANDOFF 08-29 block. (08-28 attachment "bug" was NOT a bug — stop never
> completed.)
> **08-28 (later) — ✅ MEETING ROOM BUILT (Codex ×2, Claude-audited; committed+pushed `b066610`, docs `28266ef`).**
> Docked wide transcript layout + mid-meeting "+ add context" (staged during
> recording, committed at stop, folded into notes via `<attached_context>`).
> Thread rail NOT built (threads still parked). Suites: Rust 316 · Python 545 ·
> vitest 200 · tsc clean. ⚠ Audit found `7353380` had broken pytest silently —
> repaired; lesson in LESSONS_LEARNED (pytest joins the pre-commit gate).
> **08-28 — 🟣 NOTED, not executed:** in-meeting screen redesign (docked
> transcript + mid-meeting "+ add context") and meeting THREADS in the Meetings
> area (pre-meeting briefing / live highlights). Concept boards:
> https://claude.ai/code/artifact/e27c26d6-478d-4933-b89b-9c4725ead417 ·
> https://claude.ai/code/artifact/a8989fb6-b949-43ce-86fc-0a417688d00c
> **08-26 — 🔵 AUTO-STAFFING TEST-DRIVEN by the founder (6 seeded tasks).**
> Matcher picks held up. Three gaps: (1) diagrams were colourless — **fixed**,
> `addons.rs` now has a semantic palette (uncommitted); (2) 🔴 research tasks
> can't research — `workspaces.network_allowed` exists in the schema with no UI
> (**recommended next slice**); (3) 🔴 "landing page" silently ran the slide-deck
> skill — the Skill Finder case, confirmed. Detail in `docs/TODO.md`.
> **08-26 — ✅ PUSHED: 5 commits** (`c67f2ad..4bca9bf`) incl. per-workspace model.
> **08-26 — ✅ COMMITTED (not pushed): 3 commits** — prompt rewrite `7353380`,
> workspaces arc `ca3823b` (per-task staffing + drawio validation + Run setup UI),
> docs `26234b8`. 313 Rust + 190 frontend tests green. Everything marked
> "(uncommitted)" below is now IN these commits.
> **08-26 — 🔴 LIVE BUG, unfixed: a hung transcribe request wedges the background
> queue.** No HTTP timeout (`http_client.rs:281`) + no watchdog → `transcribingId`
> never clears → the drain loop is blocked for the rest of the session (the stuck
> "Transcribing…" tag is the symptom, not the problem). Restart the app to clear.
> Evidence + fix shape at the top of `docs/TODO.md`.
> **08-25 (later) — ✅ ADR-017 PER-TASK STAFFING, backend (uncommitted).**
> Staffing is per-task, resolved+persisted at queue time, two modes
> (automatic/manual); the `addons.is_empty()` trapdoor removed. Automatic runs
> unattended by founder decision. 313 tests pass. NEXT: slice B frontend —
> delete the tab catalog panel, add per-task "Run setup" + Change.
> **08-25 (later) — ⚠️ SUPERSEDED: Workspaces CATALOG PANEL (uncommitted).**
> Built then rejected by the founder (wrong location, no verb). Slice B deletes it. `+ Agent` /
> `+ Skill` now live on the Workspaces tab (custom **agents** were previously
> impossible to create — the only form hardcoded "skill"). 6 tests, 194 pass,
> seen running in the dev app. `+ MCP` is a later slice (no backend support).
> Also fixed outside the repo: `/delegate` never reached Codex (stale June-10
> `stunt` binary on PATH with no codex backend) — symlinked + `STUNTMAN_WORKER=codex`.
> **08-25 (later) — ✅ Workspaces AUTO-STAFFING (uncommitted).** A task with no
> attached addons now gets its agent + up to 2 skills chosen from the catalog
> automatically, with the reason on the run receipt; manual attachment still
> wins unchanged. 6 tests, 309 pass. Phase-3d board (8 asks, screens, build
> order): https://claude.ai/code/artifact/ccaa71e8-ca51-4138-a46e-f4ba1d6a7754
> **08-25 (later) — ✅ Draw.io workspace skill upgraded + artifact validation
> (uncommitted, Codex-built/Claude-reviewed):** `drawio-diagram` addon defers
> to the installed Agents365 drawio-skill (claude engine) with strict XML
> fallback rules (local models); `.drawio` artifacts machine-validated
> (quick-xml) with warnings in the run log; 6 new tests, 303 pass. Vault page
> 0.3.81 rewrite drafted for founder review (`…/meeting-note-taker.draft.md`);
> stuntman v0.9.1 (source) adds a vault-staleness nudge — plugin cache still
> 0.9.0 until updated. Details in HANDOFF.
> **08-25 — 🔵 read-only diagnosis:** Engine dropdown shows the same model as
> both "not downloaded" (curated tier → sidecar 27434 store, MLX-variant tag)
> and "on this computer" (user's Ollama 11434). UX-only, no functional bug;
> filed with refs + fix options at the top of `docs/TODO.md`. No code changed.
> **08-24 (late) — ✅ 0.3.81 SHIPPED + VERIFIED, both platforms.** Published to
> the beta channel ~21:55; `verify-published.sh` PASS on manifest version,
> both downloads, provenance sha256s, and minisign signatures. macOS DMG
> notarized+stapled (build attempt 6; attempts 1–5 fell to one real bug and
> a parade of machine flakes, see HANDOFF). Windows exe from public-main run
> 32686585055 with the /health fix proven on its smoke. Post-ship on master
> (NOT in 0.3.81, rides the next release): `67b4905` attendee-chip rename now
> commits on click-away instead of silently discarding (founder repro
> Jenna→Jena; the rename engine itself was already correct end-to-end).
> Original cut trail:
> **08-24 — 🚢 0.3.81 CUT; publish in progress, Mac-first (founder call).**
> Everything below is IN the release, dev-gated (users see 0.3.80 behaviour
> + two small fixes). Foreign prompt rewrite held out (stashed, uncommitted).
> ADR-016 step A included, gated; steps B (removal) + C (bundle ollama) remain.
> Publish trail: Windows CI caught a REAL 0.3.81 regression — /health stacked
> a second Ollama probe (new bge-m3 check) on a down host, blowing the smoke's
> 5 s budget → fixed `7e64431`, PR #27 merged, Windows rerun in flight. macOS
> build failed twice on MACHINE flakes (transient notary-credential check;
> Gatekeeper "library load disallowed by system policy" on 1 of ~800 freshly
> signed libs — sick syspolicyd, see LESSONS). Attempt 4 building now with a
> pre-signing `xattr -cr` (uncommitted). **Founder: ship Mac now
> (`--allow-macos-only` if Windows isn't green); Windows work resumes later.**
> Then:
> **08-22→23 — 🟣 WORKSPACES AUTOPILOT + CONTEXT ENGINE BUILT & LIVE-TESTED
> (now committed, dev-gated).** 8 Codex delegations in one day, every diff
> reviewed + every gate re-run by Claude. Live in dev: bind meeting→
> workspace (graph-suggested) · to-dos auto-pushed · autopilot (1 run per
> workspace, global Pause, crash-safe) · review queue Approve/Reject →
> to-do closed with `completed_by`/`evidence` · in-app artifact preview ·
> related meetings w/ relevance floor · local model drafts via
> `/draft_stream` · skills & agents catalog (6 skills, 4 agents, custom) ·
> **context engine: Obsidian vault + projects folder indexed, searched by
> the to-do text on every run, receipt names what was used** (first sync
> 355 notes · 56 projects). Founder ran the loop end-to-end (9 tasks, 8
> approved). Gates: cargo 292 · clippy · fmt · tsc · vitest 184 · pytest
> 175 (+1 failure from ANOTHER session's uncommitted summarizer work in
> the same tree — commit Workspaces files by path). ⚠️ Autopilot is always
> on: queued tasks start 15 s after launch. Boards: https://claude.ai/code/artifact/28a0832e-be32-4c0e-9b7b-75ed04cd6328
> · Projects https://claude.ai/code/artifact/b69dacc7-dafb-4eca-90c0-a10895cf9e74 · Share sheet https://claude.ai/code/artifact/16583952-cf7f-4ee9-8fb3-8341de9ad52b
> ⏸ 08-23 14:20: founder rebooting (macOS `syspolicyd` fd leak stalled every
> **DECIDED (ADR-016, founder 08-23 ~15:40): one local engine — a managed
> Ollama sidecar replaces Rapid-MLX (macOS) + llama.cpp (Windows).** Measured:
> Rapid-MLX ≈102 tok/s vs Ollama/Metal 98.5 tok/s on qwen3.6-35B. Next: spec
> the sidecar + removal series for Codex (plan in the ADR).
> Waiting on founder: per-project Agents switch (filing ≠ running);
> Share-sheet questions. Detail: HANDOFF.md 08-22→23 TL;DR + TODO top.**
> **08-18 — 🟣 WORKSPACES PHASES 1a+2 IN MASTER, DEV-ONLY GATED.** The
> flagship feature exists end-to-end: workspaces/tasks/context data
> layer, Send-to-workspace from the to-do board, engine detection
> (local · Claude Code · Codex), live-streamed runs with Stop, and
> artifacts with Open. Users see NOTHING (import.meta.env.DEV gate);
> founder tests in `npm run tauri dev`. Gates: cargo 234 · clippy ·
> fmt · tsc · vitest 151. Bonus fix: ⋯ menus were unreadable in
> Light/Cream (hardcoded popup bg → var(--bg-glass)). Next: founder
> run-test → Phase 3 connections layer (MCP tools, Draw.io).**
> **08-17 (evening) — 🚀 LAUNCH-PREP DAY (no engineering changes).**
> Website Windows-404 fixed+deployed (Windows CTA → D1 waitlist,
> demand now measurable) · legal posture resolved (open-source/no-rev
> framing, LAUNCH_ASSETS §7) · X founder account secured (@knubbe24_
> aged 2014: all ~190 posts wiped + following 99→2, rebrand pending)
> · **Andrew (The Next New Thing) replied INTERESTED, answers email
> sent** · Workspaces feature designed: 3 locked decisions + approved
> six-screen UX board (see TODO top block). Launch order: virgin QA →
> PH (needs demo video from founder's existing snippets) → X thread →
> Show HN last. Detail: HANDOFF.md + docs/STRATEGY_HANDOFF.md.**
> **08-17 (~4pm) — ✅ 0.3.80 SHIPPED + LIVE-VERIFIED + FOUNDER-CONFIRMED ON
> THE QA ACCOUNT.** Publish survived a mid-upload network drop (gh retried;
> ~50 min total), verifier all-PASS (manifest 0.3.80, sha256==provenance
> 949ca022…66d3, minisign valid). Then the REAL proof, founder's words
> "it worked and transcribed": on the `test` account the app
> **auto-updated 0.3.79→0.3.80** (updater path ✅ live) and the previously
> stuck qwen-only recording **transcribed** (finding-#1 fix ✅ live).
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.80
> Mirror PR #24 (7fe1599..8ff7a2b) **MERGED on green CI** (all 3 checks
> pass; merge a0c15f3, 11:26 UTC) — public main now mirrors the workspace
> through 8ff7a2b; only docs commit c4afdd0 rides the next sync.
> **(~4:30pm) ✅ `test`-account QA COMPLETE — Phases A–F ALL PASS, zero
> findings** (D recording ✅, E honest no-LLM state with transcript intact
> ✅, F relaunch/single-instance/themes/Fix-this-word ✅). That account was
> not virgin (update-path history, models pre-downloaded), so:
> REMAINING = the strict VIRGIN-account run via lagharilabs.com — the
> launch bar. Then: ASC API key · tap Phase 2 · UX batch.**
> **08-17 (~3pm) — 📦 0.3.80 BUILT+NOTARIZED (Accepted 9e7c04e7…, stapled,
> provenance clean, BUILD_EXIT=0); PUBLISH IN FLIGHT (founder ran the !
> command; DMG upload in progress, verifier runs behind it).** On verify:
> founder relaunches Adversaria on the `test` account → auto-update toast
> 0.3.79→0.3.80 (there is NO manual check button — TODO filed: add
> "Check for updates" in Settings → General) → Qwen shows ready → stuck
> recording transcribes → Phases D–F. Also TODO-filed: shared model dir
> (per-account HF caches double-download on one Mac).**
> **08-17 (~2:30pm) — 🚢 CUTTING 0.3.80 (founder rejected the
> download-a-workaround path, rightly — ship the fix instead).** Bump +
> CHANGELOG committed (= provenance), same §4 build ritual as 0.3.79 this
> morning. Plan: publish (founder runs the ! command) → fresh account
> AUTO-UPDATES 0.3.79→0.3.80 (free updater test; his downloaded Qwen then
> just works — no new model downloads) → finish Phases D–F there → strict
> virgin re-run later. ⚠️ No account switching until notarization is done.**
> **08-17 (~2pm) — 🔴→✅ FRESH-ACCOUNT QA FINDING #1 FIXED IN TREE (shipping
> as 0.3.80, see above).** Founder downloaded Qwen3-ASR on the fresh
> account and the app still said "No transcription model is downloaded
> yet" + refused to transcribe. Root cause: `_init_transcriber` counts
> ONLY whisper-engine models for readiness, and /transcribe hard-required
> the resident whisper BEFORE qwen routing (cohere already had the
> tolerant pattern; qwen didn't). Fixed server-side: qwen/cohere-only
> machines report ready (resident stays None; live captions honestly sit
> out), qwen requests tolerate a missing resident, honest 503 when the
> qwen weights truly aren't there; stale "Settings → AI Model" copy in
> http_client.rs → real section names. Gates: pytest **527** · ruff ·
> cargo 223 · clippy · fmt. Founder ask filed in TODO: optional SHARED
> model dir so two accounts on one Mac stop downloading the same weights
> twice. RECOMMENDED PATH: founder finishes the current QA pass by
> downloading a Whisper model (Turbo) on the fresh account, collecting
> any further ❌s; then one 0.3.80 cut carries all fixes; then the clean
> full re-run on a new account.**
> **08-17 (~1pm) — ✅ 0.3.79 SHIPPED + LIVE-VERIFIED (beta, macOS-only;
> founder ran the publish, verifier all-PASS).** Manifest serves 0.3.79;
> re-downloaded artifact sha256 == provenance (baebe03b…d2f2); minisign
> valid vs pinned key; release v0.3.79 undrafted with the stable-named DMG
> (897 MB — the website's Download target), updater tar.gz, and manifest.
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.79
> Aboard: probe-verified System Audio permission + Settings Permissions
> card, mic-only survival + transcription, single-instance guard, honest
> model-row copy, refreshed README. **NEXT: fresh-account QA on a NEW
> virgin account (the `test` account is spent — and quit Adversaria in its
> session, a stale 0.3.78 instance is still running there) via
> lagharilabs.com's real Download button, per docs/QA_FRESH_ACCOUNT.md —
> note Phase B step 7 is now stale (no Screen Recording request; the
> wizard runs the system-audio probe instead).** sync-public PR next.
> **08-17 (afternoon) — 📦 0.3.79 BUILT + NOTARIZED (superseded above —
> founder live-tested and published).** Full pipeline clean in one pass: freeze →
> smoke gate PASSED (frozen /transcribe on the fixture) → Developer ID
> sign → notarization **Accepted** (id fb30e0e7…) → stapled + validated →
> Gatekeeper `accepted, source=Notarized Developer ID` → provenance
> 0.3.79@1841bd3 worktree_dirty:false → stable-name copy AFTER stapling →
> de-poison. DMG: `src-tauri/target/release/bundle/dmg/
> Adversaria-0.3.79-beta-macos-arm64.dmg`. Publish + verifier run on the
> founder's pass; then fresh-account QA vs the live funnel. (Label fix
> 0e88923 and bump/CHANGELOG 1841bd3 pushed; account-switch restriction
> lifted — notarization is done.)**
> **08-17 (noon) — 🎨 model-row honesty fix in tree (COMMITTED 0e88923): Settings
> claimed a not-yet-downloaded model was "· in use" (it was merely selected —
> founder's fresh-account screenshot). Active-but-undownloaded now reads
> "· will be used once downloaded". tsc + vitest 145 green. Awaiting commit
> word; fresh-account QA remains blocked on cutting 0.3.79.**
> **08-17 (later) — ✅ 0.3.79 HOTFIX LANDED + COMMITTED (founder's word).**
> Codex-built to a zero-decision spec, orchestrator-reviewed line-by-line,
> all gates re-run green by the orchestrator (pytest 524 · ruff · cargo 223
> w/ the real single-instance plugin · clippy · fmt · tsc · vitest 145).
> Aboard: real-audio system-audio probe (no public API exists), Settings →
> Setup status → **Permissions card** (founder ask), wizard now requests the
> RIGHT permission (Screen Recording request REMOVED — it's what suppressed
> the prompt), honest ErrorBanner with Check-again, **mic-only meetings
> survive + transcribe** (audio_path optional through the whole wire),
> single-instance guard, NSScreenCaptureUsageDescription dropped. LESSONS
> has the full trap writeup. NEXT: founder live-test → cut 0.3.79 (all
> SCK-era updaters are silently broken on 0.3.78) → fresh-account QA.**
> **08-17 — 🔴 0.3.78 FIELD BUG DIAGNOSED + 0.3.79 HOTFIX IN FLIGHT.** The
> founder's first shipped-0.3.78 recording captured NO system audio ("No
> system audio reached the encrypted spool"): the Core Audio tap needs the
> **System Audio Recording** TCC grant, and apps holding Screen Recording
> (all SCK-era installs — and our wizard still requests it) get **no prompt
> and silent denial** (cpal PR #894; live log proof: tap aggregate created,
> IOWorkLoopInit never fires). Founder-verified remedy: manually add
> Adversaria under System Settings → Screen & System Audio Recording →
> System Audio Recording Only — **recording then works**. Codex worker is
> building the hotfix (spec summarized in HANDOFF): real-audio permission
> probe, Settings › Permissions card (founder ask), wizard asks the RIGHT
> permission, mic-only meetings survive + transcribe, single-instance guard
> (a stale Aug-7 instance was found still running). Commit+push authorized
> once review + all gates pass; founder live-test → cut 0.3.79. Fresh-account
> QA re-run deliberately AFTER this hotfix.
> **08-14 — ✅ 0.3.78 SHIPPED + LIVE-VERIFIED (beta, macOS-only).** The
> keychain unlocked on the founder's return; Apple had already Accepted the
> orphaned submission server-side — staple/validate/provenance (clean tree,
> d37cfa7)/stable-copy/de-poison completed manually per the script's own
> stage-7 recipe, then publish + verifier: manifest 0.3.78, re-downloaded
> sha256 == provenance (eaab1a77…2c40), minisign valid vs pinned key.
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.78
> Aboard: 5 themes incl. Laghari Labs, Cohere engine, Fix-this-word,
> button system, model typography, download pins. NEXT: the founder's
> first-ever fresh-account QA pass, against this shipped build.**
> **08-14 (~2:30am) — 0.3.78: DMG built+signed (clean tree b795df4), smoke
> passed, Apple upload done; notarization polling died on a Wi-Fi blip and
> the retries hit a LOCKED keychain — root cause found: fast-user-switching
> (the founder was creating the qa-fresh account) locks the DP keychain and
> notarytool misreports it as a missing profile. Completion is staged and
> monitored: fires the moment the founder switches back. ASC API key filed
> as the permanent fix (third documented cause of this phantom error).**
> **08-15 (~1am) — 🚢 CUTTING 0.3.78 (founder passed full re-QA and gave
> the word). Buttons normalized (176ed7b), CHANGELOG written (a15b0ab =
> provenance commit), build running with all three engines aboard, publish
> + verify automated behind it. docs/QA_FRESH_ACCOUNT.md written — the
> six-phase fresh-account onboarding proof ritual awaits the founder
> against shipped 0.3.78.**
> **08-14 (late night) — 🎉 COHERE PROVEN LIVE BY THE FOUNDER (2.7 GB
> download → real meeting → good notes) after two more pipeline fixes
> (pins + drift guard; the manifest's independent weight predicate
> learning .onnx — had vetoed at 0 bytes as fake "network"). Dictionary
> insight live-proven: phrase entries ("Claude Code") safely fix
> homophones single words can't ("cloud"); Fix-this-word on the phrase is
> the one-gesture remedy. Button-system normalization worker in flight
> (founder: Integrations buttons "don't look good").**
> **08-14 (night) — ✅ 0.3.78 CANDIDATE SET CODE-COMPLETE.** Since evening:
> download pins for Qwen/Cohere + drift guard (`4351547` — the founder's
> dead Cohere Download button; spec error owned), themes round 3
> legibility (`b5eb9c3`), and Fix-this-word (`8db3351` — select a misheard
> term, correct everywhere, dictionary remembers the TERM). Gates: pytest
> 521 · ruff · tsc · vitest 139. Awaiting founder re-QA + Cohere's first
> real download/meeting + the cut word. Notary credential ready.
> **08-14 (evening) — 🎨 THEMES 2 + LAGHARI LABS THEME LANDED (`de89f8f`),
> model-row typography founder-tuned (`c017187`), THEMES ROUND 3 in flight
> (tag chips / category pills / Record button — dark-ground pastels
> invisible on light, the round-1 leave-list). Registration verified:
> name+email delivered to Formspree, shipped binary carries the endpoint;
> founder's "queued" banner was dev-session state contamination (TODO
> filed). Formspree free-tier cap flagged as a pre-launch bottleneck.**
> **08-14 (later) — ✅ COHERE ENGINE COMMITTED (`bb8afb5`): third on-device
> engine, highest accuracy, 14 languages, works on the CURRENT Windows
> sidecar (sherpa is platform-neutral) — language auto-detected via a
> first-window Whisper pass, never silent-empty output. pytest 520 · ruff
> green. Live weight-download + real-meeting test awaits the founder.
> Themes round 2 still in flight; Laghari brand theme queued behind it.**
> **08-14 (day) — 🔨 0.3.78 CYCLE RUNNING.** Master bumped to 0.3.78
> immediately post-release (NEW RITUAL: bump right after each cut — founder
> hit the dev-labeled-0.3.77-with-more ambiguity live). Themes round 1
> merged; founder QA verdicts: light palette "decent, could be better",
> record view must follow the theme (round-1 exclusion REVERSED), sidebar
> mismatch (screenshot awaited), and MORE themes wanted. TWO CODEX WORKERS
> IN FLIGHT: (1) Cohere engine — python only; language auto-detect via a
> first-window Whisper pass (the Principle-6 answer), unsupported language
> → whole-job Whisper fallback; (2) themes round 2 — frontend only; record
> surfaces tokenized + Cream + Navy first-class themes. QUEUED behind (2):
> the LAGHARI LABS theme — real brand tokens pinned from the website repo
> (cream #F2EBDA, ink #0E0E12, fire red/coin yellow/arcade blue/mint/
> purple accents, Pixelify Sans + IBM Plex Mono, woff2 vendored). Also
> done: author attribution in package metadata + LICENSE + README (LinkedIn
> URL pending), Mac App Store CLOSED as not-viable (taps ↔ sandbox),
> README-refresh TODO filed. Founder note: he dictates via STT — read
> message artifacts charitably.
> **08-14 — ✅ 0.3.77 SHIPPED + LIVE-VERIFIED (beta, macOS-only).** The full
> hardened pipeline end-to-end: smoke gate on the first freeze carrying the
> tap capture + Qwen runtime, notarization Accepted, stapled, provenance
> 0.3.77@e855a44 clean-tree, stable copy byte-identical, publish
> draft→asset-diff→undraft, then the verifier re-downloaded the live
> artifact: sha256 == provenance (31ae0dc7…22acf), minisign valid vs the
> pinned key, manifest serves 0.3.77.
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.77
> Aboard: tap capture (DRM fix), Qwen3-ASR engine, 10 languages + directive
> fix, attendee rename, transcript paragraphs + copy, force re-download,
> offline honesty, summary cards, logging fix. All founder-live-tested
> before the cut. One build-script bug found+fixed en route (de-poison rm
> on --onedir dirs, 10adacf — failed AFTER the artifact was complete).
> Next: themes review + founder light-QA on feat/themes → 0.3.78.
> **08-14 (~2:30am) — 🚢 CUTTING 0.3.77 NOW (founder call: themes → 0.3.78,
> completed above).**
> Master PUSHED through the 0.3.77 bump (0dcf906); CHANGELOG written;
> frozen-sidecar spec now bundles qwen3-asr-mlx (lazy import — would have
> shipped a dev-only Qwen engine). Build starts when the overnight themes
> worker finishes writing (its diff parks on feat/themes for morning QA);
> then build-dmg + smoke gate → notarize → publish beta → verify.**
> **08-14 (~2am) — 🚢 EVERYTHING LANDED ON MASTER, THEMES WORKER OVERNIGHT,
> 0.3.77 CUT PLANNED FOR THE MORNING (superseded above).** Founder live-tested and passed: the
> tap capture (real recording end-to-end on the tap build — the keychain
> wall was a dev-signature artifact, fixed via debug-only file key), the
> Español fix on the 35B model (directive now closes the user prompt and
> overrides the English-headings JSON pin), and the summary cards (three
> live iterations → the app's own card language: 5% overlay, standard
> border). Landed as 6 commits: 9589e8c tap Phase 1 (SCK GONE) · b7cd395
> force re-download + offline honesty · c51e5b3 fmt cleanup · c843b79
> summary cards · f1aa4b8 dev spool key · 03558e9 language fix. THEMES
> (founder: "add themes and ship it") delegated overnight: Dark/Light/
> System picker, full light palette, token sweep with a dark-pixel-
> identical invariant. Morning: review + founder light-mode QA → cut
> 0.3.77 (check: frozen sidecar must bundle qwen3-asr-mlx).**
> **08-13 (midnight) — ✅ TAP PHASE 1 + EASY BATCH REVIEWED AND VERIFIED
> (committed 08-14, see above).**
> SCK is gone — capture is a pure Core Audio process tap; force
> re-download + honest offline Download buttons landed. Combined gates,
> orchestrator-run: cargo 218 · clippy · pytest 511 · ruff · tsc ·
> vitest 135 — green.
> **08-13 (night) — 🔨 TAP PHASE 1 LANDED IN TREE (worker-done, gates
> worker-claimed green, previously unreviewed — superseded above). screencapturekit is
> gone from the manifest per the worker's grep. Light-mode + white-label
> concept artifact published for the founder's client-branding idea:
> https://claude.ai/code/artifact/0d1f37cb-62e6-4f82-b954-ac9d9dbd540a**
> **08-13 (evening) — 🔨 TAP PHASE 1 + EASY BATCH DELEGATED (two Codex
> workers, disjoint files, in flight).** Phase 1 = SCK → cpal-loopback
> process tap in audio/macos.rs + drop screencapturekit + audio-capture
> plist key (device-anchored route, proven in Phase 0; global-tap shape
> stays the Phase-2 fallback). Easy batch = force re-download of
> corrupt-cached models + honest offline Download buttons. Logging fix
> committed `644ee25`. ⚖️ SSL.com cert DEFERRED by founder — coupled to
> the Windows rewrite ("once I'm happy the Windows version will work").
> **08-13 (later) — ✅ AUDIO-TAP PHASE-0 FULLY PASSED — MIGRATION IS GO.**
> Founder A/B: the DRM course video stayed visible and playing through a
> 45 s process-tap capture (it blanks under SCK), and the tap recorded the
> site's audio cleanly. Phase 1 (~2–3 d, global tap, kills the Screen
> Recording prompt) awaits Hamza's scheduling vs graph-v2 merge + Windows
> rewrite. Detail: docs/AUDIO_TAP_MIGRATION.md.
> **08-13 (earlier) — 🎉 AUDIO-TAP PHASE-0, AGENT HALF PASSES.** A ~120-line
> harness over cpal 0.18.1's tap loopback (no ScreenCaptureKit) captured
> real system audio on this Mac first try — peak 0.77, RMS tracking the
> test speech exactly, playable WAV. Probe-permission pattern confirmed
> (true silence = exact 0.0f). Remaining Phase-0 gate is HAMZA's DRM A/B:
> course video + `tap-harness 45` — if it doesn't blank, migration is GO
> (kills the DRM bug AND the Screen Recording prompt).
> **08-13 — ✅ QWEN3-ASR ENGINE + 10-LANGUAGE NOTES LIVE-TESTED BY HAMZA AND
> COMMITTED (`d362a9d`, `c5e4b80`).** His real-video run through the new
> engine: windowed transcript + correct notes, "super quick". Also landed:
> the logging.basicConfig fix (uncommitted, verified — field INFO
> diagnostics finally reach logs) and a LESSONS entry for the
> `uv sync --extra dev` env trap. Today: audio-tap Phase-0 spike.
> **08-12 (late night) — 🚀 QWEN3-ASR ENGINE + 10-LANGUAGE NOTES BUILT +
> VERIFIED (committed 08-13 after founder test, see above).** Two parallel Codex delegations,
> both first-pass: Qwen3-ASR 0.6B/1.7B appear in the existing model picker
> (engine follows the model, chunked 30 s timestamps, glossary via `context`,
> no hidden downloads), and notes can be written in en/ar/zh/hi/es/fr/bn/pt/
> ru/ur or Match-spoken. Combined gates: pytest **506**/1 skip · ruff · tsc ·
> vitest **134**. Morning ritual: `uv sync --extra mlx`, pick Qwen3-ASR 0.6B
> (already cached from the spike), test a real meeting — friend gets it after.
> **08-12 (night) — 🔬 BYOM SPIKE COMPLETE — GO on both founder-requested
> models.** Qwen3-ASR 0.6B (MLX): VO track 1.7 s, Arabic PERFECT with auto
> language ID, glossary `context` works. Cohere Transcribe (sherpa-onnx int8,
> CPU): word-perfect English, best punctuation, Arabic correct — but needs an
> explicit language per stream (no auto-LID/code-switch) and has no glossary
> param. Shared gap: NO local runtime emits segment timestamps yet → engine
> layer must use chunked-window times (transcribe_cloud technique).
> **Recommendation: Qwen3-ASR as first engine** — one model family on BOTH
> OSes (MLX now, `from_qwen3_asr` in the same sherpa build the Windows
> rewrite uses); Cohere second. Next: engine spec → delegate.
> Rename feature COMMITTED `e8c3b52` on Hamza's word.**
> **08-12 (evening) — ✅ ATTENDEE-RENAME FEATURE BUILT + VERIFIED (committed,
> see above).** Codex first-pass; orchestrator-reviewed; gates:
> cargo 218 (+5) · clippy · tsc · vitest 134 (+3). Rename a misheard name on
> the attendee chip and every reference follows (labels, transcript, notes,
> attendees, action items) + auto-adds the fix to the dictionary. Themes
> ask filed in TODO (sized 2–4 days; token layer exists, ~400 raw colors to
> sweep; Dark stays default, Light/System become choices). Spike so far: Qwen3-ASR MLX port is bf16-only (8-bit
> checkpoint load fails) and NO local runtime gives segment timestamps yet
> (MLX port lacks them; sherpa-onnx issue #3552) — dual-channel interleave
> needs them; chunked-window offsets are the known workaround.
> **08-12 (later) — ✅ transcript fix COMMITTED `6ee83c8` on Hamza's word.
> In flight: attendee-rename feature delegated to Codex (misheard name fixed
> once on the chip, every reference follows + auto-added to the dictionary);
> BYOM transcription Phase-0 spike running (Qwen3-ASR 0.6B-8bit via MLX —
> `context` vocab-biasing param already confirmed in the API; Cohere
> Transcribe runtime path next). TODO gained 4 founder items: BYOM engines,
> rename, executive-summary paragraph in templates (deferred), local-first
> multi-device sync → iOS/Android ambition (ADR before code).**
> **08-12 — 📜 TRANSCRIPT READABILITY + COPY BUTTON (committed, see above).** Hamza's "long meeting → a few paragraphs / blob of words"
> report root-caused and proven live: `build_labeled_turns` merged every
> consecutive same-speaker segment into ONE turn (45-min sim → 9 paragraphs;
> no mic interjections → one 16,389-char paragraph). Fixed on both sides:
> service splits turns at >3 s same-speaker gaps or 600 chars (segment
> boundaries only), display paragraph-splits existing stored mega-turns at
> sentence boundaries (Arabic-aware) so old meetings read well WITHOUT
> re-transcribing, raw-transcript fallback keeps newlines, and the Transcript
> tab gained a Copy button emitting clean `[00:00] Them: …` lines (the
> on-screen colon is CSS-generated — manual selection copied garbage).
> Executed by the FIRST true Codex delegation (spec by Claude, diff reviewed,
> gates re-run by the orchestrator): pytest **480**/1 skip · ruff · tsc ·
> vitest **131** — all green. Found + recorded a delegation trap: stale
> `~/.local/bin/stunt` silently rerouted codex → claude/free-proxy; use the
> plugin's absolute path (details in HANDOFF).
> **08-11 — 🎚️ THE CONTEXT WINDOW SIZES ITSELF (uncommitted, awaiting
> authorization).** Closes the last half of the Muse Glimmer incident: the
> robustness ladder (08-10) *recovers* a truncated note, this stops it being
> truncated. `num_ctx` is now computed per request at the options choke point —
> `max(16384 floor, min(prompt tokens + 8k output budget, RAM tier,
> the model's own max))` — with the chars-per-token divisor **measured** on the
> real tokenizer (English 5.15, Arabic 3.72, code-switched 4.13 → we use 3) and
> the model's ceiling read from Ollama `/api/show`. **No setting, no env var, no
> per-model table** — the founder requirement was "I'm not going to do anything
> in the back settings. Neither are the people who will use this. If it's Qwen,
> Gemma, or Muse, it should work for all." The two env vars remain as
> debugging-only overrides. Python suite **453 → 475 passed**, ruff clean.
> **LIVE-PROVEN 2026-08-11:** real muse-glimmer:30b-mlx on a 52k-char transcript
> → `adaptive: prompt≈20k tok + 8k budget → 28672 (bound by prompt)`, sized right
> on the FIRST attempt (no retry, no repair), `ollama ps` confirming CONTEXT
> 28672 — and 22 GB / 1m52s vs 26 GB / 4m17s at the model-default 131072.
> Surfaced follow-up: the service never calls `logging.basicConfig`, so app INFO
> (incl. this new diagnostic line) never reaches the log in the field.
> **08-11 (later) — ✅ 0.3.76 SHIPPED + LIVE-VERIFIED (beta, macOS-only).**
> First release ever published and PROVEN in one motion: draft→asset-diff→
> undraft `--latest`, then the verifier re-downloaded the live artifact —
> sha256 matches provenance exactly, minisign signature valid against the
> pinned key, manifest serves 0.3.76, website's stable link serves the new
> 895,167,455-byte DMG. Six user-visible fixes to beta users via auto-update.
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.76
> Fresh-account run was WAIVED (founder call, recorded honestly in
> docs/acceptance/0.3.76.md) — the full journey stays OWED on the marketable
> bar. Next: SSL.com order · tap Phase-0 spike · graph-v2 click-through ·
> sync-public PR · office-box traceback · retag sweep.
> **08-11 — 🚢 0.3.76 BUILT + NOTARIZED, publish gated on Hamza's
> fresh-account pass ([acceptance](./docs/acceptance/0.3.76.md)).** First
> release through the hardened pipeline: smoke gate passed, notarization
> Accepted, provenance clean, stable-name copy byte-identical. Publish =
> macOS-only (deliberate, per Windows amendment). Six user-visible fixes
> aboard. **Cert DECIDED:** SSL.com eSigner OV $180/yr
> ([CODE_SIGNING.md](./docs/CODE_SIGNING.md)) — Hamza orders, 3–5 day clock.
> **DRM blanking root-caused:** our SCK audio capture IS a screen-capture
> session; Granola uses Core Audio taps (binary-proven). Migration
> recommended ~1–1.5 wk post-0.3.76, Phase-0 spike gates it
> ([AUDIO_TAP_MIGRATION.md](./docs/AUDIO_TAP_MIGRATION.md)) — also kills the
> Screen Recording prompt entirely. SPEC gained Principle 6 (nothing
> user-touched). Open: fresh-account pass · SSL.com order · tap spike ·
> graph-v2 click-through · office-box traceback · retag sweep.
> **08-10 — 📊 GRAPH V2 ON ITS BRANCH (pushed, unmerged) + MODEL-OUTPUT
> STANDARDIZATION LANDED.** Graph v2 built per the ratified 2D spec and
> adversarially verified (223 cargo · 161 vitest · clippy clean): legible
> always-on meeting labels, time axis, cluster hulls, embeddings-driven
> related edges with pin/dismiss/undo. Awaiting Hamza's click-through +
> threshold calibration before merge (worktree `meeting-note-taker.graph-v2`).
> **Live incident diagnosed + FIXED (committed `9792fab`, audited):** a new
> reasoning model's note was truncated by num_ctx=16384 → app dumped raw JSON
> as the note and blamed "transcript too short" (wrong). The output-robustness
> ladder now normalizes any model's output (think-tags/fences/prose-embedded
> JSON), detects `done_reason=length` and retries once at doubled num_ctx
> (cap 32768), repairs a cut-off JSON tail conservatively, and replaces both
> bad behaviours with honest copy — raw JSON is never rendered, and "too short
> or sparse" only fires on a genuinely short transcript. Python suite
> 410 → **453 passed**. **LIVE-PROVEN 2026-08-10:** source service + real
> muse-glimmer:30b-mlx on a 26k-char transcript → output arrived cut with one
> unclosed scope and Ollama reported a NORMAL stop (no done_reason=length!) —
> the repair tier caught it and produced a 20.7k-char structured note, no raw
> JSON. Validates the two-tier design: detection alone would have missed this.
> **UNIVERSAL SIZING LANDED (`c0c2901`):** num_ctx adaptive per request
> (prompt + 8k budget, clamped by RAM tier and the model's declared max via
> /api/show) + num_predict always -1 (the effective default silently cut
> muse-glimmer at ~5k tokens while claiming a normal stop — discriminator
> with -1 completed 10,980 tokens). Live verdict told straight: muse-glimmer's
> bare-template packaging STILL EOSes mid-JSON on long prompts; the repair
> tier rescued 3/3 live runs — for badly-packaged models repair is the
> load-bearing layer, and users get a proper note either way. pytest 476.
> Ships in **0.3.76** with the death
> certificate + diagnostics bundle — cut it with the first fresh-account pass. Founder items still
> open: OV cert order, retag sweep, office-box traceback.
> **08-08 (later) — ✅ PLAN RATIFIED, WORK COMMITTED, 3D GRAPH PARKED.** Hamza
> ratified the plan + the Meetily amendment: macOS launches on the current
> gated stack; **the Windows bar is the native rewrite — no more frozen Python
> sidecar on Windows** (evidence: [docs/MEETILY_COMPARISON.md](./docs/MEETILY_COMPARISON.md) —
> Meetily solved the install class by deleting Python after 8 months of our
> exact pain, and still hasn't solved operation: 70% of issues open). 3D graph
> parked on `graph-3d-prototype`. Next: founder Phase-0 items (cert, sweep,
> website button, traceback) → first fresh-account acceptance pass → updater
> drill → Phase 2 + streak → launch.
> **08-08 — 🔧 REMEDIATION PHASE 0/1 CODE LANDED + AUDITED (committed same day).**
> Another agent's ~950-line drop was audited (6 critical defects found — incl.
> a smoke stage that would abort every release and a verifier that could not
> fail), then fixed by 5 model-pinned agents, each re-audited. Landed: publish
> script that cannot lie (draft→asset-diff→undraft `--latest`→verify, Windows
> hash into provenance at publish), a REAL post-publish verifier (**live
> v0.3.75: macOS bytes match provenance, both signatures verify against the
> pinned key — first end-to-end proof ever**; the one FAIL is the honest
> missing-Windows-provenance gap, fixed forward), frozen-sidecar smoke in
> build-dmg (real /transcribe on a committed fixture, live-tested), the death
> certificate wired end-to-end (`ADVERSARIA_DATA_DIR` passed by Rust; crash
> tracebacks reach the UI), dev de-poison spawn gate, real diagnostics bundle,
> honest-failure UI, Windows CI transcribe smoke + `.sig` warn→error.
> Gates: cargo 213 · pytest 410 · vitest 127 · tsc · clippy · ruff.
> **Open for Hamza: commit authorization; 3D-graph keep/park (unreviewed, now
> the default mode); cert order + retag sweep + website button; plan
> ratification.** Verified env fact: this network resets long GitHub
> transfers — the day's agent deaths and 0.3.74's DNS drop are one family.
> **08-07 (pm) — 🔬 DIAGNOSIS + REMEDIATION PLAN, awaiting Hamza's ratification.**
> Forensic workflow over the full ledgers + code: ~110 incidents → 8 systemic
> causes; #1 is "the shipped artifact is never the tested artifact" (~35%), and
> nearly every serious bug was found in production on packaged installs while
> the automated gates stayed green. Plan in
> [docs/REMEDIATION_PLAN.md](./docs/REMEDIATION_PLAN.md) (uncommitted):
> **macOS-only launch, ~13.5 founder-days / ~4 weeks to a marketable bar**
> (publish script cannot lie · frozen sidecars executed every build · fresh-
> machine matrix · 5 clean external first-runs · honest failures + diagnostics
> export); Windows gets its own post-launch bar, OV cert ordered day 1.
> **Next: ratify/veto the five calls, then Phase 0.** Verified today: the
> `commands.rs:219` debug gate covers only error reporting — the frozen-sidecar
> dev trap is STILL LIVE.
> **08-07 — 🚢 SHIPPING 0.3.75: prompt-to-template + honest recovery + cosmetics**
> (batched 08-06/07 at Hamza's request). 0.3.74 remains the shipped build. Compact toolbar
> buttons, Export/Regenerate in the logo's blue, a disabled primary keeps its
> colour; and "Describe the notes you want" → the configured LLM drafts a
> template into the editor (never to disk), shown a real template as its example
> so the to-do contract survives. Verified live: 200 in 24 s on qwen3.5:9b.
> **Dev trap found:** a release build populates
> `target/debug/adversaria-service`, so dev silently runs the FROZEN service and
> every Python edit is invisible — see LESSONS_LEARNED.
> 🔴 The missing-manifest bug is wider than one machine: Hamza's own log shows 8+
> spools failing recovery.
> **08-06 — 🚢 SHIPPED 0.3.74 TO BOTH PLATFORMS (beta), LIVE AND VERIFIED:**
> the Settings redesign, all 8 sections, old tabs deleted. Clicked through by
> Hamza in dev and signed off. Manifest reads 0.3.74 with `darwin-aarch64` +
> `windows-x86_64`, both signatures key id `e1b42bed5b7d787f`, all 4 asset URLs
> 200, macOS notarized + stapled.
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.74
> **Publish went wrong once and lied about it:** a DNS drop killed the DMG upload
> and the draft cleanup, and `publish-release.sh` STILL EXITED 0 — the release sat
> as a draft with 2 of 4 assets. Recovered by uploading the missing assets to the
> draft and undrafting it. 🔴 in TODO.
> **✅ THE FRIEND'S WINDOWS FAULT IS SOLVED — and it was none of the three Python
> defects.** His log: `[sidecar.executable_missing]`. `adversaria-service.exe` is
> not on disk; security software removed it. That also explains "can't download
> the local model" — the download is an HTTP call INTO the sidecar. Needs a
> Protection-history restore + a Defender exclusion, or company IT if it is EDR;
> no app change fixes it. That diagnostic only exists because of the 0.3.73 work —
> on 0.3.72 the same machine logged nothing. Settings becomes a readiness ledger for Record → Transcribe → Notes;
> the 899-line `AiModelTab.tsx` splits into Transcription + Notes; the notch
> pill / meeting-alert / recording-view settings get live visual previews; a new
> Notifications section gathers all four notification surfaces. Shared state
> (health + the download pipeline) is hoisted into three hooks mounted once by
> the shell, because that pipeline is ONE state machine the IA cuts across three
> sections. Gates: **tsc · vitest 115**. Verified 34/35 config keys that had UI
> still have UI (the 35th never had a control). Four defects fixed in passing,
> incl. a null `calendar_status` that blanked the entire Settings pane, and a
> near-miss where prompt-template editing was almost deleted. Contract:
> [docs/SETTINGS_REDESIGN.md](./docs/SETTINGS_REDESIGN.md). Prototype:
> https://claude.ai/code/artifact/398e713e-dd26-4a27-bbae-7f25a292133e
> **08-05 — 🚢 SHIPPED 0.3.73 TO BOTH PLATFORMS (beta), LIVE AND VERIFIED:**
> manifest reads 0.3.73 with `darwin-aarch64` + `windows-x86_64`, both signed
> (key id `e1b42bed5b7d787f`), all 4 asset URLs 200, macOS notarized + stapled
> (`source=Notarized Developer ID`).
> https://github.com/LaghariLabs/adversaria-releases/releases/tag/v0.3.73
> Ship friction worth remembering: the notary keychain profile died mid-release
> (revoked app-specific password, reported as "profile not found"); the
> stable-named DMG the website links was left at 0.3.72 by the failed build and
> had to be regenerated from the stapled artifact. **⚠️ revoke the pasted
> app-specific password; consider an App Store Connect API key.** The Windows CI
> smoke gate also failed spuriously at 181s — the re-run answered /health in
> **15s**, so the "slow cold start" theory is refuted and the cause is still
> unknown. All in LESSONS_LEARNED. Two separate reports were
> reproduced from screenshots/code.
> (1) A working self-hosted transcription engine could remain covered by a stale
> local Whisper download failure; config changes now reach the long-lived status
> UI, remote engines ignore irrelevant local weights, real transcriber readiness
> outranks a failed alias, and all Windows profile aliases backed by the same CT2
> snapshot settle ready together. (2) A friend's 0.3.72 install cannot reach the
> bundled service. The published installer was inspected and DOES contain
> `adversaria-service.exe` plus its full runtime (~480 MB installed), pointing to
> antivirus/EDR quarantine or an immediate frozen-process crash rather than a
> packaging omission. Launch failures now reach both the sidecar log and UI,
> offline chrome + Settings offer an actual restart, watchdog ownership is
> race-safe, and Windows CI must launch the frozen exe and pass `/health` before
> packaging. Gates: frontend **111**, Python **380/1 skip**, Rust **198/1
> ignored**, tsc, Ruff, clippy, fmt, workflow parse, diff-check — green. Still
> needs a real Windows release build and the affected PC's Security history/log.
> **✅ 08-05 (later) — THE THREE PYTHON DEFECTS + THE UNGATED DIGEST ARE FIXED.**
> (a) `config.py` now resolves the frozen data dir **per platform** (`%APPDATA%`
> on win32) to match `config.rs::app_data_dir`, and degrades to the read-only
> bundled templates rather than raising at import — this was also an independent
> cause of the Windows "todo template is not there" report. (b) The parent guard
> hard-exits **only on a clean stdin EOF**; any exception logs and keeps the
> service alive. (c) `faster_whisper` is imported inside `_create_model`, so a
> missing MSVC runtime now yields `transcriber_state = error` instead of a process
> that dies before binding. (d) The to-do digest is gated on `todo_digest_enabled`
> (default **true**) with a configurable hour, settable in Settings › General.
> Gates: **pytest 389 · cargo 203 · vitest 111** · tsc · clippy · fmt · ruff.
> The friend's `%APPDATA%\meeting-note-taker\logs\adversaria-service.log` still
> tells us which one was firing, but all three are closed either way. **Next: a
> Windows release build.**
> **08-05 (later) — 🎨 SETTINGS REDESIGN PROPOSED (prototype only, no code).**
> "Settings is too complicated" → reframed as a **readiness ledger** for Record →
> Transcribe → Notes: pipeline state first, then a "Needs attention" repair list,
> then destination-first configuration. Splits the 899-line `AiModelTab.tsx` into
> Transcription + Notes; gives the **notch pill / meeting-alert / recording-window
> settings live visual previews** instead of dropdowns; rescues `Your name` (the
> `me_label`), date format, sidebar layout, and retention from being dropped.
> Interactive artifact:
> https://claude.ai/code/artifact/398e713e-dd26-4a27-bbae-7f25a292133e
> **Blocked on one prerequisite:** autosave requires **per-field config patching**
> first — today `updateConfig` round-trips the whole `AppConfig`, and a
> whole-config save with `state.sidecar == None` resets the base URL to the static
> `9876` (`commands.rs:4375`). Review also produced a dedicated **Notifications**
> section: Hamza could not find the "record this meeting?" prompt, and the audit
> found FOUR notification surfaces across two tabs — including 🔴 **the to-do
> digest in `reminders.rs`, which fires twice a day with NO config gate and cannot
> be turned off** (needs `todo_digest_enabled`; small, self-contained fix).
> **08-04 — 🚢 SHIPPED 0.3.72 TO BOTH PLATFORMS (and 0.3.71 before it).** The
> first release where macOS and Windows go out together AND both auto-update —
> Windows updates had never worked before (macOS-only manifest + CI collecting
> `.nsis.zip` artifacts this build never produces; the signing secret turned out
> to have been present all along). Manifest carries `darwin-aarch64` +
> `windows-x86_64`, both signed, key id verified against the app's pinned
> verifier, both URLs 200. Contents: poll-storm fix (96% of the sidecar log),
> sidecar reaping + parent-death guard, the 16 GB Ollama runner (cause of the
> "notes never generated" timeout), vocabulary correction, rebuilt first-run
> wizard, transcription BYOK (3 engines, privacy copy gated on the REAL host),
> template display names, TL;DR + due dates, the brain-dump template, **prompt
> seeding unfrozen** (the packaged app had run a Jun-20 `general.md` for six
> weeks — verified live: 2,563 B → 6,353 B with a backup beside it), and the
> mic-bleed fix (a one-voice recording was being written up as a two-person
> meeting). 10 review-confirmed defects fixed before shipping, incl. two that
> would have put a FALSE PRIVACY CLAIM on screen. npm audit 5 high → 0.
> **Evidence note:** qwen3.6:35b (MoE) beats qwen3.5:9b on quality 2-1 in a blind
> bake-off AND is ~2x faster (only ~3B params active) — costs 23 GB vs ~7 GB.
> **OPEN:** Real-Windows validation/release of the 08-05 fixes; friend must check
> Windows Security/EDR and share the service log if no block is recorded; no
> force re-download for a genuinely corrupt cached model; fresh-account QA still
> never run. Detail: HANDOFF current session.
> **08-03 — ✅ ONBOARDING + UPDATER + TRANSCRIPTION BYOK — COMMITTED + PUSHED
> (master/0198bff, merged).** Trigger: a friend's fresh Windows install finished setup with no
> model and got "No transcription model is downloaded yet" instead of notes —
> the wizard made *skipping* the download primary. Shipped: wizard model picker
> with one-click download + live progress (nothing auto-downloads, tested);
> updater re-checks every 6 h; **transcription BYOK first-class** — three
> engines (On-device / Self-hosted / Cloud) with a `transcription_provider`
> field + tested URL migration, so Hamza's office DGX Whisper is a proper
> sovereign option instead of a scary "cloud" one. Two review rounds found
> **10 confirmed defects, all fixed** — incl. "Transcription ready ✓" shown on
> a machine whose engine can't load the model, a dead-end failure branch, and a
> self-hosted panel that could claim "never to a third party" while uploading to
> Groq (privacy copy is now gated on the real host, not the chosen label).
> Gates: tsc · vitest 97 · cargo 190 + clippy + fmt · pytest 357.
> 🔴 **BLOCKED ON HAMZA: Windows auto-update has never worked** (endpoint 404s,
> macOS-only manifest, no CI signing key) — he must add
> `TAURI_SIGNING_PRIVATE_KEY` to the public repo's Actions secrets.
> Next: review → commit → 0.3.71 → fresh-machine QA.
> **08-02 — ✅ ALL 4 ROBUSTNESS BUGS FIXED + REVIEWED, GATES GREEN
> (UNCOMMITTED, awaiting Hamza).** Same-day arc: morning diagnosis of Hamza's
> slow/hot machine (~95 GB resident model servers, swap 98% full; ~60 GB freed;
> 4 bugs filed) → afternoon fix-everything run (4 parallel agents +
> adversarial review + inline repairs). Shipped: poll storm → event-bus +
> 60 s heartbeat + access-log filter + log rotation; sidecar lifecycle →
> startup reaper + stdin parent-death guard; **16 GB Ollama runner root-caused**
> (local tags ride the OpenAI-compat `/v1` which can't carry `num_ctx` —
> summarizer now serves loopback-:11434 natively with `num_ctx=16384`);
> "Adverse Area" → deterministic vocabulary correction (review caught 2 real
> defects in v1 — word-swallowing, casing downgrade — both fixed with
> regression tests). Gates: pytest 357 · cargo 180 + clippy + fmt · vitest 57 ·
> tsc. Deferred: Windows llama-server orphan reap (needs a Windows box).
> Next: Hamza review → commit → 0.3.71 → fresh-machine QA. Detail: HANDOFF +
> TODO 2026-08-02 block.
> **08-01 — ✅ SETUP V3 "FIRST-RUN RESCUE" BUILT + REVIEWED + TUTORIAL v2
> (uncommitted, awaiting Hamza).** Trigger: a friend's fresh Windows 0.3.68
> failed with `{"detail":"Transcriber not initialized"}` — the whisper model
> downloaded *synchronously inside service startup* (unreachable port, death on
> failure, no re-init, raw JSON in the UI). Decisions (Hamza): **nothing
> downloads automatically — guide the user**; never gate setup; Windows default
> whisper → **large-v3-turbo** (~1.6 GB). ALL FOUR PACKAGES DONE: Python
> resilience (service serves model-less, `transcriber_state` in /health,
> structured 503s, self-heals on download, BYOK unblocked); Rust plumbing (xet
> fix all platforms, sidecar file log + watchdog respawn, transcript persists
> BEFORE notes, retroactive drains, error translation — raw JSON can no longer
> reach the UI); React guided flow (wizard guide card with honest per-platform
> size, persistent chrome chip, AI Model tab = model dashboard with
> remount-surviving byte progress, un-latched named status strip); tutorial v2
> (flow-teaching replayable tour + Granola-style seeded demo meeting,
> `demo.rs`). Adversarial review found 6 real defects — all fixed with tests
> (worst: Settings whisper downloads were dead on arrival behind the old Rust
> profile allowlist; partial snapshots read as "downloaded"). **Gates: pytest
> 326 · cargo 175 + clippy + fmt · vitest 50 · tsc — all green. Hamza
> dev-tested the fresh-install flow live (08-01): 8 more findings, all fixed
> same session (stale-config name clobber, endpoint-less "Registration queued"
> banners ×2, 680px Settings cap, Recording/AI-Model duplicate, tour tooltip
> off-screen on full-page spotlights, tab steps not navigating, auto-detect
> default, founder-signed welcome meeting with getting-started to-dos).
> COMMITTED + PUSHED on his word 08-01, and **🚢 SHIPPED as 0.3.70 the same
> day — BOTH PLATFORMS**: notarized DMG (Accepted, stapled, "Notarized
> Developer ID") + Windows x64 installer, published to adversaria-releases as
> Latest with the signed updater manifest (latest-beta.json serves 0.3.70 —
> installed apps get the update toast). All stable URLs 200. This also CLOSES
> THE MCP SCHEMA GAP: 0.3.70 carries 0.3.69's action_items migration, so the
> live adversaria-mcp 0.2.0 now pairs safely with the shipped app. Public repo
> synced (PR #12, CI green, squash-merged); 0 open dependabot alerts. Still
> open: the V3 QA ritual passes (fresh macOS account + fresh Windows VM,
> throttled/HF-blocked) and the four website edits.**
> See HANDOFF "Current session" + SETUP_REDESIGN_SPEC.md V3 addendum.
> **07-31 — 🤖 THE PRODUCT GREW A NEW LOOP: agents do your to-dos.** Claude (via
> the MCP server) can pick up action items from a meeting, work them, and report
> back with evidence — and **only you can mark anything done**. `action_items`
> gained status/completed_by/completed_at/evidence; an agent reaches `ai_done`
> and no further. A **With AI** lane on the board shows what it's doing and what
> it finished. `adversaria-mcp` **0.2.0 is LIVE on PyPI** with `start_task` /
> `complete_task` — one line to connect: `uvx adversaria-mcp`.
> **✅ SHIPPED: 0.3.67** (registration endpoint restored) and **0.3.68** (six QA
> fixes + **the first Windows installer**, attached to the same release as the DMG).
> **⚠️ 0.3.69 IS BUILT, NOTARIZED, INSTALLED — NOT PUBLISHED.** It carries the DB
> migration MCP 0.2.0 depends on: anyone pairing the live MCP with 0.3.68 gets
> `no such column: status`. **And the notarized DMG predates three later fixes —
> publishing needs a FRESH notarized build.**
> **⚖️ Licence → Elastic 2.0** (source-available; nobody else may host it).
> Releases ≤0.3.68 stay MIT. Repo is public.
> **🔴 Lesson: three "the feature isn't there" reports were all VISIBILITY bugs**
> — Focus view, a meeting scope filter, and a hardcoded 3-column grid that pushed
> the 4th lane below 156 items. The logic was right every time.
> **🌐 Website: don't edit `landing/index.html`** — the live page lives in the
> private `lagharilabs-website` repo. A full rewrite was drafted and rejected;
> the existing design is better. Four surgical edits needed instead.
> **07-29 — 🚢 0.3.67 SHIPPED: registration works again.** Formspree endpoint
> `xykrvprp` (verified live with a test POST BEFORE building — one test entry is
> in Hamza's dashboard to delete) is baked in and confirmed present in the
> shipped binary. Notarized/stapled, Latest, DMG URL 200, manifest 0.3.67 signed.
> **Queued signups on 0.3.66 machines deliver automatically on first launch of
> this build** — nothing was lost.
> **Also 07-29 (NOT in 0.3.67 — committed after its frontend build):** Windows
> dropdown white-on-white FIXED (`e02c37d`); the youtube-miscategorization fix
> was **attempted and reverted** — see TODO, it cannot be fixed in the
> classifier and Hamza checks the transcript at the office 07-30.
> **07-29 — 🚢 0.3.66 SHIPPED (the setup redesign, v2).** Notarized (Accepted,
> stapled, Gatekeeper `Notarized Developer ID`), published to adversaria-releases
> as **Latest**; stable DMG URL 200, latest-beta.json serves 0.3.66 with a signed
> updater artifact — existing installs get the update toast. **Ships WITHOUT a
> registration endpoint (Hamza's call):** signups queue on-device and deliver
> retroactively once an endpoint-carrying build lands (target 0.3.67).
> Context: reviewer inbound (Andrew Warner replied to Hamza's YouTube comment) —
> the link now serves the redesign, not the frozen-progress-bar 0.3.65.
> Also: Windows CI installer exists (run 30446906346 artifact, office QA pending),
> updater key now in public-repo secrets (next Windows build signs updates),
> source stays OPEN (Hamza, 07-29). Release stats at ship: ~5 DMG downloads,
> 15 manifest checks.
> **07-28 ~11am — 🔄 SETUP REDESIGN V2 (`c1237f7`), after Hamza's fresh-account
> test rejected v1's auto-download.** Nothing downloads uninvited now: wizard is
> You/Permissions/Done (whisper-only background cache), a one-time **GuidedTour**
> (coach marks) ends ON Settings › AI Model, which is Meetily-shaped — provider
> dropdown first, installed-models dropdown, "Recommended (not downloaded)" +
> explicit Download button, API fields inline. No-engine is legal: empty-summary
> meetings show "Transcript saved" + Generate notes (`engine_configured` cmd +
> `resummarize_meeting`). Spec v2 addendum in SETUP_REDESIGN_SPEC.md. Gates green
> (cargo 159 · vitest 33 · tsc · clippy · fmt). 0.3.66 test DMG rebuilding.
> **07-28 am — 🚢 THE WHOLE SETUP REDESIGN IS IMPLEMENTED AND PUSHED** (all 5
> packages of [docs/SETUP_REDESIGN_SPEC.md](./docs/SETUP_REDESIGN_SPEC.md), one
> session, commits `22e7e83`→`58726c6`): (A) byte-accurate download progress;
> (B) wizard **7 steps → 3 screens** (Windows: 2 — permissions auto-skip) with
> downloads + sample verification moved to a background status strip; (C)
> settings **8+3 tabs → 5**, Your Name first in General, jargon-guard tests;
> (D) **transparent managed llama.cpp engine for Windows** — consent card names
> engine build/hash/source + pinned GGUF before anything installs (llama.cpp
> b10155 Vulkan 33.6 MB; unsloth Qwen3.6-27B/3.5-9B/3.5-4B Q4_K_M under the same
> tier ids as macOS); (E) NEW pre-meeting notification (wizard toggle + Settings
> › General + 60 s calendar poll). Gates all green: cargo 159 · clippy · fmt ·
> pytest 301 · ruff · tsc · vitest 31. **⚠️ NOT yet verified on real hardware:**
> fresh-macOS-account run, fresh Win11 run (engine install + llama-server serve),
> live ≥5 GB download bar. Public sync PR carries Windows CI.
> **07-28 — ✅ SETUP REDESIGN PACKAGE (A) SHIPPED (`22e7e83`):** byte-accurate
> download progress. `model_setup.py::_downloaded_bytes` now counts, per expected
> file, the first of `snapshots/<rev>/<name>` → `blobs/<sha256>` →
> `blobs/<sha256>*.incomplete` (capped at the manifest size, one path per file).
> Measured on a real cache with in-flight blobs: old 32 MB → new **1.77 GB**, so
> the ~5% plateau is gone. ⚠️ hf_hub **1.19** writes `<sha256>.<uuid8>.incomplete`
> (process-unique, `file_download.py:1848`), not the `<sha256>.incomplete` the
> spec assumed — the glob covers both, and both exist in the live cache.
> 297 pytest passed/1 skipped · ruff clean. Live ≥5 GB download check still owed.
> **07-27 pm — 📐 NEXT BIG WORK ITEM SPEC'D: [docs/SETUP_REDESIGN_SPEC.md](./docs/SETUP_REDESIGN_SPEC.md)**
> — one combined release (user decision): (A) **byte-accurate download progress**
> (root cause FOUND: `model_setup.py::_downloaded_bytes` stats `snapshots/`, but
> hf_hub streams into `blobs/*.incomplete` — bar freezes at ~5% until the big
> shard completes); (B) setup **7 steps → 3 screens**; (C) settings **8 tabs → 5**,
> Your Name into General (it's buried in Voice Transcription at `Settings.tsx:1240`
> — the name↔settings wiring itself already works via `registration.rs:179`);
> (D) **Windows transparent managed engine** (auditable llama.cpp install + pinned
> GGUF, detect existing Ollama + GPU — user decision: sovereignty = say exactly
> what installs, ask first); (E) NEW pre-meeting notification (doesn't exist yet;
> wizard toggle). Build on `feat/windows-port` AFTER it merges — same files.
> **07-27 — 🪟 WINDOWS PORT BUILT + VERIFIED NATIVELY — ✅ MERGED TO MASTER 07-28**
> (was branch `feat/windows-port`; public sync PR LaghariLabs/adversaria#1 went
> green on all 3 checks — macOS + Windows quality, macOS smoke — and was merged).
> The missing pieces were a build pipeline plus five real code defects, not a
> rewrite — see [HANDOFF.md](./docs/HANDOFF.md) "Last session (2026-07-27)" for
> the full list. **Green on Windows 11:** clippy clean · `cargo test` **149
> passed/0 failed** (real SQLCipher + vendored OpenSSL) · 289 pytest · ruff · tsc.
> **📦 INSTALLER BUILT: `Adversaria_0.3.65_x64-setup.exe`, 81.8 MB**, NSIS
> `currentUser` (no admin prompt). 🔴 **CPU-only, and forced:** a CUDA-bundled
> sidecar is 2.4 GB (1.9 GB of it 15 CUDA DLLs) and **NSIS cannot package >~2 GB**
> — `makensis` ICEs. GPU still works if the NVIDIA CUDA Toolkit is installed.
> Real fix (download the CUDA runtime on first run, as model weights already are)
> is in TODO.md.
> New: `tauri.windows.conf.json`, `adversaria-service-windows.spec`,
> `scripts/build-windows.ps1`, `.github/workflows/release-windows.yml`.
> Fixed: `spawn_sidecar` silently no-opped on Windows · `shutdown_sidecar`
> orphaned the sidecar and held the port · `console=False` would have killed the
> service before it bound (uvicorn + `sys.stdout is None`) · **the Whisper picker
> was a no-op on Windows** (assigned an attribute faster-whisper never reads) ·
> **WASAPI loopback drift** — it emits *nothing* while idle, so quiet stretches
> shifted every later "Them" turn earlier and reordered the transcript.
> 🔴→✅ **THE INSTALLER WAS RUN AND FAILED ON FIRST LAUNCH — NOW FIXED.**
> `no such table: action_items`, blaming the **macOS keychain, on Windows**.
> `init_db` encrypts the DB *before* creating the schema, and the copy-verification
> counted tables the **0.2.x Windows database doesn't have** — same path
> (`%APPDATA%\meeting-note-taker\meetings.db`), real file = **147 meetings, only a
> `meetings` table**. Every upgrader from that line was dead on arrival. Fixed via
> `table_count()` + a per-platform credential-store message; **2 regression tests,
> 151 pass**; installer rebuilt. No data was ever at risk (migration bails before
> swapping, backup always kept). Rule: anything before the CREATE TABLE batch must
> assume an arbitrarily old schema.
> 🔴→✅ **SECOND FAILURE: first-run setup could NEVER finish on Windows — FIXED.**
> Step 6/7 hung on "meeting model is still downloading · Preparing…" forever. The
> sample gate needs a **pinned MLX snapshot**, and `setup_status` only returned
> `mlx-community/*` profiles — plus it was pre-downloading **3.5 GB of MLX Whisper
> weights faster-whisper cannot load**. Now: Ollama's already-pulled models are the
> local profiles (installed, RAM-ranked), Whisper pins follow the backend
> (`Systran/faster-whisper-large-v3`, already cached → instant), and the copy no
> longer says "On this Mac". 291 pytest · 151 cargo · 15 vitest · tsc · clippy green.
> 🔴→✅ **FOUR staged failures in the Windows local-engine path, all now fixed.**
> (1) setup could never finish — MLX-only profiles + 3.5 GB of unusable MLX Whisper
> pre-downloads; (2) `Managed Rapid-MLX is currently available on Apple Silicon
> only` — the local engine has two shapes (managed process vs external service);
> (3) a **resumed** setup replayed a persisted MLX profile id, so the fix missed
> existing users; (4) `Unknown model profile: ollama:<tag>` — `profile_alias()`,
> the single id→model map, knew only MLX ids and **four** gates funnel through it.
> Root-caused in `setup::profile_alias` (now `Option<String>`, resolves
> `ollama:<tag>`); **all 8 profile-id call sites audited**. 153 cargo · 291 pytest
> · 18 vitest · tsc · clippy green. **Meta-lesson: when several gates reject the
> same value, fix the shared predicate, not the gates.**
> 🔴 **SentinelOne blocks the bundled sidecar on the dev box** (`Access is denied`
> on the PyInstaller exe; AppLocker off, usermode CI off — S1 is the only
> candidate). Workaround in use: run the service from source
> (`uv run uvicorn src.server:app --port 9876`), which the app picks up via
> `python_service_url`. This is a **real user-facing risk**, not a dev quirk.
> 🔴 **Two things are NOT verified and must not be assumed:** the frozen sidecar
> has **never been executed** (this box refuses to launch the PyInstaller exe —
> `Access is denied`, likely third-party EDR; Defender is off here), and nothing
> has run in a live call. ⚠️ Also found: the public/private repo split means
> **workspace-only commits have never been linted on Windows** — one such
> `-D warnings` error was already sitting in `open_privacy_settings`. Now fixed:
> `scripts/sync-public.sh` exists (dry-run default, leak check, `--pr` mode).
> **07-27 am — 📄 DOCS ONLY: [docs/PRODUCT_OVERVIEW.md](./docs/PRODUCT_OVERVIEW.md)
> written** — one self-contained, product-level (no code) description of Adversaria
> + its full feature set, built as a **NotebookLM source for slide generation**;
> describes v0.3.65. No code touched, no version change.
> **⚠️ [docs/DEEP_DIVE_BUSINESS.md](./docs/DEEP_DIVE_BUSINESS.md) is 51 releases
> stale** (describes v0.3.14): still calls the to-do board unbuilt (shipped 0.3.45),
> notarization + first-run wizard "launch blockers" (both shipped), and the product
> closed-source (it's MIT + public). **Do not feed it to an external tool alongside
> PRODUCT_OVERVIEW.md.** `docs/STRATEGY.md` has not drifted.
> **07-26 ~12:05am — ✅ 0.3.65 PUBLISH CONFIRMED COMPLETE** — release went **Latest**
> with all three assets; the stable download URL resolves (HTTP 200) and the manifest
> serves 0.3.65. (Supersedes the in-flight warning below.)
> **07-26 ~12am — ✅ 0.3.65 NOTARIZED (publishing) + STABLE DOWNLOAD FILENAME.**
> Contains the update-path permission recovery. **`build-dmg.sh` now also emits
> `Adversaria-macos-arm64.dmg`, copied AFTER stapling** (verified byte-identical +
> independently passes `stapler validate`/`spctl` — copy it *before* stapling and it
> looks fine locally but fails Gatekeeper on a stranger's Mac), and
> **`publish-release.sh` now uploads the DMG automatically** (0.3.64's was attached
> by hand — that's how a release ships with no download). The site links to
> `releases/latest/download/<name>`, so a version-stamped filename **silently 404s**
> next release. ⚠️ **Publish was IN FLIGHT at session end — release showed as Draft
> while ~1.4 GB uploaded. Confirm it went Latest and that the download URL resolves
> before assuming it shipped.**
> **🔴 THE TIME SINK — see [LESSONS_LEARNED.md](./docs/LESSONS_LEARNED.md) top entry:**
> the user's install refused to record *with Screen Recording enabled*, through
> repeated toggle/re-grant/relaunch. Cause: **two TCC rows for one bundle id**
> (`tccutil reset` printed success twice); System Settings only rewrites one. Cure:
> `tccutil reset ScreenCapture com.meetingnotetaker.app` → quit → `open -a Adversaria`.
> Developer-only (≈15 re-signed builds in a day). Also recorded there: never launch
> the inner binary from a shell, and macOS revokes Screen Recording on every bundle
> replacement (0.3.65 makes that recoverable, not preventable).
> **07-25 ~11:30pm — 🔴 THE 0.3.64 PERMISSIONS FIX WAS INCOMPLETE → FIXED (`9875ed8`,
> needs a 0.3.65 freeze).** Moving permissions into first-run setup only helped **new**
> users. The user auto-updated to 0.3.64, pressed Record, and got a raw
> `NoShareableContent("…user declined TCCs…")` dead end: **macOS revokes Screen
> Recording whenever the app bundle is replaced**, so every *updating* user hits the
> flow setup was built to fix, and never sees the wizard again. `start_recording` now
> pre-flights `permissions::check()` (the old failure came from inside ScreenCaptureKit
> *after* a session was half-started) and the banner renders **Open Settings** +
> **Relaunch** — relaunch being the step users don't know about. The sentinel prefix
> lives in **both** Rust and TS, so a test pins them together (verified it fails on
> drift). tsc ✓ vitest 15 ✓ clippy ✓ **cargo 145** ✓. ⚠️ Still untestable here — once
> granted, the branch never runs; fresh macOS user account is the only real proof.
> **⚠️ AGENT MISTAKE TO NOT REPEAT:** launching
> `Adversaria.app/Contents/MacOS/meeting-note-taker` **directly from a shell** ignores
> `ADVERSARIA_DATA_DIR` (it's `#[cfg(debug_assertions)]`, release builds ignore it) and
> **opened the user's REAL database**; it may also disturb TCC attribution. Use
> `open -a Adversaria`; use a **debug build** for isolated demo data.
> **✅ 0.3.64 PUBLISHED** (job `9662d85e…`, DMG sha `6367c48e…`), manifest verified
> serving 0.3.64. ⚠️ `publish-release.sh` can fail once with `ReleaseAsset.name already
> exists` — gh rolls the release back; a plain retry works. ⚠️ The site's download URL
> embeds the version → **404s next release** unless build-dmg.sh emits a stable
> filename.
> **📣 MARKETING — see [LAUNCH_ASSETS.md](./docs/LAUNCH_ASSETS.md) (canonical,
> paste-ready copy + submission log).** GitHub topics added to both repos; 3
> awesome-list PRs open (awesome-mcp-servers #10922 needs a **Glama** claim by the
> user — Dockerfile done + verified; awesome-mac #2408; awesome-privacy #960).
> Do-not-submit: modelcontextprotocol/servers, awesome-selfhosted. Blocked:
> awesome-tauri (signed commits), awesome-rust (>50 stars, repo has 1). 47s
> programmatic demo video at `marketing/product-demo/`. **Decision:** keep
> `adversaria-mcp` a separate repo until `sync-public.sh` exists.
> **07-25 ~7pm — 🔴→✅ PERMISSIONS MOVED INTO SETUP (the churn bug) · MCP PUBLISHED ·
> SITE LIVE · CI GREEN.**
> **The fix that matters (`cbd8e62`, needs a 0.3.64 freeze to ship):** the wizard's
> `permissions` step was decorative text saying *"macOS asks only when a feature
> first needs access"* — no code behind it — so the first external tester pressed
> Record and only then met a permission prompt, then a forced relaunch. Open 🔴 in
> TODO.md since 07-18. New `permissions.rs` requests **mic** (`AVCaptureDevice`,
> in-process) and **Screen Recording** (`CGRequestScreenCaptureAccess`, which macOS
> honours **once per install** → denial falls back to opening the exact Settings
> pane). Screen Recording needs a **relaunch** to apply, so the step detects that
> and offers a Relaunch button; it re-polls **on window focus** since Settings
> grants fire no callback. ⚠️ **Untested against a real prompt** (this Mac holds
> both grants) — QA in a fresh macOS user account. ⚠️ Hooks gotcha: a `useEffect`
> after the early return breaks Welcome entirely.
> **✅ CI GREEN** all 3 jobs incl. Windows. Last blocker was `tauri-build` refusing
> to run because the gitignored PyInstaller sidecars are declared bundle resources
> → CI now stubs the paths; then 5 clippy lints cleared.
> **✅ `LaghariLabs/adversaria-mcp` PUBLISHED** (MIT) — all 4 tools verified against
> the real DB first. Limitation documented: plain SQLite, so it can't read an
> encrypted DB.
> **✅ Website download-first + LIVE.** ⚠️ **`git push` does NOT deploy** — Pages has
> no Git integration; use `wrangler pages deploy dist --project-name=lagharilabs`.
> Runbook: `lagharilabs-website/DEPLOY.md`.
> **✅ Public README** rebuilt around organization + 2 dead doc links fixed.
> **Marketing:** LinkedIn post published by the user. LAUNCH_PLAN.md still stands and
> today killed its two biggest risks (P1/M5 closed-source, P3 notarization). Carousel
> + org avatars on the user's Desktop. **Show HN deliberately NOT fired** — one
> external tester, and 0.3.61–0.3.63 have never run on another machine; gate it on
> ~5 clean external installs (plan's own risk P2).
> **07-25 ~4:30pm — 🚀 OPEN SOURCED (MIT) + 0.3.63 PUBLISHED. 🔴 PUBLIC CI FAILING.**
> **TWO REPOS NOW:** `LaghariLabs/adversaria` = **PUBLIC**, MIT, a *filtered copy*
> (code + README + LICENSE + CHANGELOG + only ARCHITECTURE.md and
> PRIVACY_NETWORK_BOUNDARIES.md), single squashed commit, no history ·
> `LaghariLabs/adversaria-workspace` = **PRIVATE**, this clone, full history + all
> docs. ⚠️ **No shared history — they will drift; `scripts/sync-public.sh` is
> proposed but NOT written.** Filter rule: no monetization talk, no competitor
> disparagement, **credit kept** (Meetily attribution deliberately retained —
> stripping credit while keeping their VAD constants is the riskier move).
> Verified via the contents API that STATUS/HANDOFF/STRATEGY/TODO/DECISIONS/
> DEEP_DIVE_*/marketing_strategy/CLAUDE.md all 404 publicly.
> **0.3.63 notarized + PUBLISHED** (Apple job `bead2d17…`, DMG 752 MB, sha256
> `ec3861af…`) — `publish-release.sh` run for the first time since June, so the
> auto-update toast finally has a target; user installed and confirmed it works.
> ⚠️ the `latest/download/` URL embeds the version → 404s next release.
> **🟡 CI: 6 latent bugs found + fixed, last run pending.** These workflows had
> **never executed before** (private repo's branch is `master`, trigger is `main`),
> so publishing surfaced: Windows `URL.pathname` → `D:\D:\` ENOENT in
> check-security.mjs · undeclared `scipy` (transitively present locally, absent on a
> clean runner) · cargo fmt drift · **`tauri-build` refusing to run because the two
> gitignored PyInstaller sidecars are declared bundle resources — this killed EVERY
> cargo command before compiling** (fixed with empty stub dirs in CI; verified
> locally by moving the real dirs aside; also explains why the e2e job always
> passed — `tauri.e2e.conf.json` sets `"resources": []`) · 5 clippy `-D warnings`
> lints only reachable after that (3 too-many-arguments from today's work, allowed
> with rationale since restructuring `save_person` would change the IPC shape;
> map-over-inspect; **2 Windows-only lints never linted before** — `AudioCapture`
> missing the `Default` impl macos.rs already has, plus a redundant `return`) ·
> e2e minimum-viewport test now skips when the display can't host 1024x720
> (runners are 1024x768 → ~645 px). **macOS desktop smoke now PASSES.**
> **⚠️ CORRECTION: an earlier note here blamed an org Actions quota — that was
> WRONG, don't chase it.** The cancellations were this workflow's own
> `concurrency: cancel-in-progress: true`; pushing fixes every few minutes meant
> each run killed the previous. All runs are on a PUBLIC repo = **free, nothing was
> ever billable.** Rule: push once, let it finish. Billing hardened anyway — every
> job now has `if: github.repository == 'LaghariLabs/adversaria'` so the private
> workspace can never spend minutes (macOS ×10 / Windows ×2), guarded rather than
> deleting `pull_request` so both copies stay byte-identical. ⚠️ `wasapi.rs` edits
> are **unverified locally** (cfg(windows); cross-compile blocked by openssl-sys) —
> CI is their first check. Never dispatch `release-candidate.yml` from the private
> repo. No badge in the public README, so nothing red shows on the front page.
> **POSITIONING SHIFTED:** lead with **organization** ("capture is solved, what
> happens afterward isn't"), not privacy; privacy is now a *flexibility* point
> (local by default, BYOK when the hardware isn't there) since the app really does
> support a cloud path. LinkedIn post drafted on that frame. ⚠️ Screenshots must use
> `marketing/demo-data/`, never the real workspace.
> **07-25 ~2pm — 🟣🟣🟣 CRM FOUNDATION SHIPPED (committed, unpushed, not in any
> build).** Direction shift after the user tried HeyClicky: verified it's **not a
> competitor** (cloud screen-assistant + voice agents, $20/mo, 25k users) —
> what it proves is craft + distribution + willingness to pay. Pivot toward a
> self-filling, on-device CRM. **Discovery: the foundation already existed**
> (`people` table, get/save commands, editable graph dossier, per-person Second
> Brain notes) — this extended it. Three commits: `f39bb2c` contact details
> (email/phone/LinkedIn, additive migration, in the dossier + vault frontmatter,
> deliberately manual — audio never carries an email) · `cde6d9b` graph search
> (dims non-matches, match count zooms, reuses the existing faded/highlighted
> classes so it can't fight tap-to-explore) · `1c9251c` **role/company prefill
> from the meeting** (the summarizer already asked for `role` and threw it away;
> now asks for `company` too and both reach Rust as `attendee_details` → first
> sighting of a person pre-fills their profile; **never overwrites a user-typed
> value**, matched on the bare name = the key both `people` and graph nodes use,
> wired into all 5 attendee-persisting paths). Verified: tsc ✓ vitest 15 ✓
> **cargo 144** ✓ **pytest 282** ✓. **OPEN-SOURCE PREP DONE, NOT EXECUTED:** repo
> still PRIVATE, git history secret-scanned **clean** (only placeholder Formspree
> strings); blocked on two user calls — **license** (AGPL protects the paid-sync
> plan, MIT doesn't) and **a CLA before the first external PR** (sole copyright
> today is the only reason commercial licensing is possible). Backlog + the
> monetization thinking are in TODO.md (07-25). Undesigned open question:
> **team sharing** for banks/firms/hospitals vs free solo use.
> **07-25 ~8am — ✅✅ 0.3.62 COMMITTED, PUSHED & NOTARIZED. READY TO AIRDROP.**
> The four-arc batch is no longer uncommitted: 3 commits (`c850d81` feat(recording)
> notch island + per-channel waveforms + speaker colors + live-bleed dedup ·
> `4d7100f` chore(release) 0.3.62 · `35e114c` docs) and **pushed
> `ffe6e88..35e114c` → origin/master**, which also carried the three stranded
> commits (0.3.60, its docs, 0.3.61 mic fix). master == origin, tree clean.
> Notarized build ran per NOTARIZATION.md §4 (Developer ID `4MY4PH5PHC`,
> `adversaria-notary`, RELEASE_MODE=1, channel beta,
> ALLOW_INCOMPLETE_REGISTRATION=1 as with 0.3.58–0.3.60, INSTALL=0). Apple
> **Accepted** (job `43f01891-2575-499c-a59f-5b8313fb6051`), stapled + validated,
> Gatekeeper **accepted / source=Notarized Developer ID**. Independently
> re-verified on the built artifact (not trusting the script): Info.plist
> **0.3.62** · Authority = Developer ID + TeamIdentifier 4MY4PH5PHC · `codesign
> --verify --deep --strict` valid · `SCScreenshotConfiguration` still **absent**
> (macOS-15 launch fix holds) · the Rust binary exports `get_audio_levels` +
> `set_recording_bubble_expanded` · the embedded frontend (built 07:52, linked
> 07:56) contains `notch-island`, `3d97ff`, `ff5f57`. Pre-build gates: tsc ✓ ·
> vitest 15/15 ✓ · cargo test **140/140** ✓. **DMG: 752 MB · sha256
> `1b43511ce2b901aa381517e5e8bfb25ff0ccc706684e1daa8f1b71cb16c56247`** at
> `src-tauri/target/release/bundle/dmg/Adversaria-0.3.62-beta-macos-arm64.dmg`.
> **NOT published** (deliberate — an untested build must never auto-push to beta
> testers). **NEXT (user): AirDrop to the sister's macOS-15 laptop → install over
> 0.3.60 → acceptance (launch, first-run wizard, record→summarize, notch island
> hover-expand, blue/red speakers).** On pass:
> `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh "0.3.62 — …"`.
> ⚠️ Still unaddressed: FINAL-transcript speaker bleed via `_merge_dual` (only
> the live feed is deduped) — watch the next real meeting.
> **07-24 ~10:45pm — 🔴🟣🟣 LIVE-BLEED DEDUP + DYNAMIC ISLAND + BLUE/RED SPEAKER
> SYSTEM (uncommitted, hand-built).** (1) 🔴 Live transcript duplicated lines =
> **speaker bleed**: laptop speakers → mic, same speech captioned by BOTH streams
> with wording drift ("gonna" vs "going to"). Fix: cross-source token-Jaccard
> (≥0.55, 15 s window, exact-match for <4 tokens) dedup in `feed_live_source`
> (shared `recent` ring, 3 unit tests incl. the real incident pair). NOTE: the
> FINAL transcript may bleed too (`_merge_dual`) — not yet addressed, watch for it.
> (2) 🟣 Notch is now a real dynamic island: docked expressive starts as a
> **collapsed strip** (dot + timer | me/them mini-waves — never covers app content
> like Chrome tabs, which the always-96px-tall island did); hover → new
> `set_recording_bubble_expanded` command resizes the window (frame re-anchored
> top) and the body (caption/waves/Stop) animates open; mouse-leave collapses
> after 300 ms. (3) 🟣 Color system unified: **Me = blue #3d97ff, Them = red
> #ff5f57** across the notch waves, live-transcript left bars (lines now carry
> `source` end-to-end: LiveTranscript{text,source} → App liveLines[] →
> companion), and the meeting transcript (Me pinned blue via config user_name
> match; others red-first appearance order). Verified: tsc ✓ vitest 15 ✓ cargo
> check ✓ **140** tests ✓. NEXT candidates (user asked, feasibility confirmed):
> per-meeting sovereignty toggle (App.tsx already computes full/partial/none from
> config — needs per-meeting override through summarize) and pause/resume
> recording (capture-level pause flag + elapsed bookkeeping + island button).
> **07-24 ~10:10pm — 🟣🟣 CHANNEL-AWARE WAVEFORMS + SPEAKER-COLORED TRANSCRIPT
> (uncommitted, hand-built — stuntman still 402).** (1) The pill's two waves now
> track REAL loudness: new `current_levels() -> (system "Them", mic "Me")` on both
> platform backends (the old `current_level` threw the split away with `.max()`),
> `get_audio_levels` command + 130 ms poll in RecordingBubble, `--lvl` CSS var
> scaleY-drives each wave's amplitude — Me dances only when the mic hears you.
> (2) Transcript turns now render a colored speaker chip: stable hue per speaker
> by order of first appearance (`SPEAKER_COLORS` in NoteViewer; chip gets ":" via
> CSS) — the turn view previously showed NO speaker at all. Verified: tsc ✓
> vitest 15 ✓ cargo check ✓ 137 tests ✓. Live in dev after auto-rebuild. Clicky
> researched: it's an AI cursor-assistant, NOT a notch app (the notch he admired
> is likely NotchNook); teardown of NotchNook/Alcove = possible next polish pass.
> **07-24 ~10pm — 🟣 NOTCH DOCK MADE ORGANIC (uncommitted): concave 12px fillet
> corners welding the island to the screen edge (verified in zoomed screenshot),
> spring "bloom out of the notch" entrance (460ms overshoot bezier, origin top-
> center), hover breathing (~3% scale), 18px bottom radius. Structure: transparent
> `.notch-dock` shell + `.notch-island` shape (+2×12px window width in Rust for the
> fillets). ⚠️ animation fill must be `backwards` NOT `both` (both keeps the last
> keyframe transform and kills the hover transition). Stuntman upstream (DeepSeek)
> hit 402 Insufficient Balance → implemented directly per takeover rule. tsc ✓
> vitest 15 ✓ cargo check ✓. Awaiting the user's verdict on the motion (bloom/hover
> only visible live).
> **07-24 ~9:50pm — 🟣✅ RECORDING PILL NOW DOCKS INTO THE PHYSICAL NOTCH (uncommitted;
> VISUALLY CONFIRMED live in dev).** boring.notch-style: black island fused with the
> hardware notch, over the menu bar, wings beside the cutout (dot+Recording left,
> timer right), caption+waves+Stop below, rounded bottom corners. Implementation:
> plain Tauri window (NO NSPanel — crash rule holds) + raw objc2-app-kit on the
> existing NSWindow: notch geometry from `safeAreaInsets`/auxiliary areas, wings=108,
> `setLevel(25)`+collectionBehavior+`orderFrontRegardless` **before** `setFrame`
> (ordering was round-1 bug — see LESSONS). Non-notch Macs + Windows byte-identical
> fallback. Recipe cross-checked against the user's own NotchyPrompter
> (`teleprompter` project, NotchWindow.swift) after he pointed at notchprompter.com.
> Verified: cargo check ✓ 137 tests ✓ tsc ✓ vitest 15 ✓ + live screenshot in the
> notch. Two throwaway test meetings created ~21:42/21:47 (deletable). NEXT: fold
> into the next freeze with the mic fix (0.3.61 staging is already installed but
> PRE-notch-dock; re-freeze or ship notarized 0.3.62 on "ship it").
> **07-24 ~7:35pm — 🔴→✅ "ENCRYPTED MIC RECORDING TOO LARGE" ROOT-CAUSED + FIXED
> (uncommitted; not in 0.3.60).** User's real 45-min meeting produced a **7.1 GB mic
> spool**: his default macOS input is a **16-ch virtual device** ("Quicktime Player",
> 16-in/16-out @44.1 kHz) and cpal recorded all 16 float channels; >4 GiB breaks
> WAV's u32 cap → transcription refused, retry-proof. **FIX (2 layers, stuntman,
> reviewed):** mic capture now downmixes to mono in the callback (Whisper mono-mixes
> anyway), and `decrypt_channel` streams oversized multi-channel tracks through a
> mono downmix instead of erroring — the stuck recording becomes transcribable on
> retry. **cargo test 137/137 ✓ cargo check ✓.** Full postmortem in LESSONS_LEARNED.
> **RECOVER THE STUCK MEETING:** quit the installed app → `npm run tauri dev` (shares
> app data) → retry transcription from the meeting; ships for real in the next
> freeze (0.3.61, on user's "ship it"). ⚠️ User should also set a REAL mic as the
> macOS default input — the current "Me" track likely recorded that virtual device.
> Sister's 0.3.60 is unaffected (built-in mic is 1–2 ch; the cap needs 3+ hrs).
> **07-24 ~7pm — ✅✅✅ 0.3.60 NOTARIZED + EVERY FIX VERIFIED IN THE SHIPPED ARTIFACT.
> READY TO AIRDROP.** Notary **Accepted** (job `1f5a2310-1619-49c3-a79d-8ee6cd13c24a`),
> stapled + validated, Gatekeeper **accepted / source=Notarized Developer ID**.
> Independent checks on the built app: Info.plist **0.3.60** · Developer ID authority ·
> `SCScreenshotConfiguration` still **absent** (macOS-15 fix intact) · webview loads
> `index-B6iahRu8.js` which contains the new wizard ("Unfolding the meeting model…",
> "Setting up your private engine…") · **the frozen sidecar was BOOTED from the .app
> and `/health` answered in 14 s cold** (no more multi-minute block) and
> `/setup/model_download/whisper-main` + `qwen-9b-balanced` both answer (new pins
> shipped). **DMG: 751 MB · sha256
> `be797c06b70ad6195ee4d60ac9bac6ca604f71ea891646a77681c46a4fb029f0`** at
> `src-tauri/target/release/bundle/dmg/Adversaria-0.3.60-beta-macos-arm64.dmg`.
> NOT published. **NEXT (user): AirDrop to the sister's macOS-15 laptop → install
> over 0.3.59 → wizard resumes with auto-downloads + one progress bar → sample →
> record→summarize.** After acceptance: `publish-release.sh` (user-triggered).
> **07-24 ~6:30pm — 🚢 "SHIP IT" RECEIVED → 0.3.60 FREEZE STARTED.** Version bumped
> 0.3.59 → **0.3.60** (package.json + tauri.conf.json + Cargo.toml + lock),
> CHANGELOG written, committed. Also added last-minute: animated **"Unfolding the
> meeting model into memory…"** panel with live elapsed timer on the sample step
> (the 1–3-min warm-up is no longer a dead disabled button), and the engine bar is
> indeterminate-animated while totals are unknown (tsc ✓ vitest 15/15 ✓). Notarized
> build running per NOTARIZATION.md §4 (beta channel, ALLOW_INCOMPLETE_REGISTRATION=1
> same as 0.3.59, INSTALL=0). **NEXT: verify notary Accepted + staple + Gatekeeper +
> embedded frontend asset → user QAs first-run in a fresh macOS user account →
> AirDrop to the sister's laptop.** NOT published (publish-release.sh) until
> acceptance passes.
> **07-24 ~6:15pm — 🟣🟣 SEAMLESS FIRST-RUN ENGINE SETUP (uncommitted, same pending
> batch). User verdict on the old flow: "stupid and chaotic… people will churn."**
> New behavior: NOTHING requires a manual download click or retry. The two Whisper
> models (`whisper-main` = large-v3 ~3.1 GB, `whisper-live` = turbo-q4 ~0.5 GB, now
> pinned in MODEL_PINS with fixed revisions) start downloading **the moment first-run
> setup opens** (they're needed for every provider — transcription is always
> on-device) and overlap the registration/disclosure typing. The selected LLM
> auto-starts at the model step. ONE combined progress bar ("Setting up your private
> engine — X / Y GB") covers Whisper+LLM on the model AND sample steps; "Continue —
> downloads keep running" lets the user walk ahead; only "Run sample" gates on the
> LLM being verified; errors show a single Retry-downloads button. Key enabling
> changes: `_load_manifest` accepts `weights.npz` (Whisper MLX repos have no
> safetensors); new `setup::downloadable_profile()` lets the download commands fetch
> whisper ids; Welcome.tsx rework (auto-start + combined polling). **Context: this is
> the answer to "how does Granola do it"** — Granola is instant because its ML is
> cloud-side; the on-device comparable (Superwhisper) does exactly this in-onboarding
> download UX. Tauri is NOT the problem. **Verified: 277 pytest ✓ · cargo test
> setup:: 5/5 ✓ · cargo check ✓ · tsc ✓ · vitest 15/15 ✓.** Fresh-machine QA without
> a second computer: create a new macOS user account (clean HF cache + app data) and
> run the installed app there.
> **07-24 ~5:55pm — 🟣 THIRD MODEL TIER ADDED: Qwen 3.5 9B "balanced" (uncommitted,
> same pending-0.3.60 batch).** User wanted more than the 27B/4B split ("like 9
> billion or 8 billion") and asked for "Qwen 3.5 Plus". Verified live: **Qwen
> 3.5/3.6 Plus are API-only (Alibaba Cloud), no open weights** → cannot be an
> on-device profile (usable via the existing cloud-provider path); and our 27B is
> already Qwen **3.6** (newer than 3.5). Added `qwen-9b-balanced` =
> `mlx-community/Qwen3.5-9B-MLX-4bit` @ `938d8919…` (~6 GB, min 16 GB RAM,
> recommended for 16–23 GB Macs; 27B stays ≥24 GB, 4B below 16 GB). Display names
> now carry the generation ("Qwen 3.6 27B", "Qwen 3.5 9B/4B"). Both UIs render the
> profile list dynamically — only `setup.rs` + `model_setup.py` changed (stuntman,
> reviewed). **cargo test setup:: 4/4 ✓ · cargo check ✓ · 276 pytest ✓ · tsc ✓ ·
> vitest 15 ✓.** Docs: SETUP_MODEL_UX.md updated.
> **07-24 ~5:45pm — 🔴→✅ FIRST-RUN "SERVICE NOT READY" ROOT-CAUSED + FIXED (working
> tree, uncommitted; needs a 0.3.60 re-freeze to reach testers).** Field report from
> the sister's laptop: 0.3.59 **LAUNCHED** (macOS-15 crash fix held ✅) but setup's
> "Download model" errored "The local setup service is not ready; retry in a moment."
> **CAUSE:** FastAPI `lifespan` warmed the live-caption Whisper model synchronously —
> on a fresh machine that means downloading `whisper-large-v3-turbo-q4` from HF
> **before uvicorn binds its port** → whole service connect-refused for minutes, and
> the Rust command surfaced the first connect error. **FIX (3 layers):**
> (1) `server.py` lifespan sets `_live_transcriber = _transcriber` immediately and
> warms the fast model on a daemon thread under `_WHISPER_LOCK`; (2) new
> `HttpClient::wait_until_ready` polls `/health` (750 ms interval, 5 s req timeout) and
> `start_model_download` waits up to 120 s; (3) Welcome shows "Starting the local
> engine…" while waiting. Stuntman implemented to spec, reviewed clean; **276 pytest ✓
> cargo check ✓ tsc ✓.** ⚠️ The Python half is DORMANT until a re-freeze (ship
> ritual) — the sister's DMG still has the bug; interim workaround: wait ~2–3 min
> after first launch, then click Download model again. **NEXT (user): say "ship it" →
> bump 0.3.60 → notarized build → AirDrop; continue the 0.3.59 acceptance list
> (record→summarize, Settings model picker) in the meantime.**
> **07-24 ~5:30pm — ✅✅ 0.3.59 NOTARIZED + FIX VERIFIED IN THE SHIPPED BINARY.**
> Rebuild after the macOS-15 crash fix (below). Apple notary **Accepted**, stapled,
> Gatekeeper **accepted / source=Notarized Developer ID**. **THE FIX CONFIRMED IN
> THE FINAL NOTARIZED APP:** `nm -m` on Adversaria.app's binary shows
> `SCScreenshotConfiguration` **GONE**; every remaining strong SC* ref is a base
> macOS-12.3+ class → **will launch on macOS 15.7.3**. **DMG: 751 MB · sha256
> `5ce03baf866881eec15db2e154a2c9836ae95036cfe0bcf6ad18831732054b89`** at
> `src-tauri/target/release/bundle/dmg/Adversaria-0.3.59-beta-macos-arm64.dmg`.
> NOT published yet (acceptance-test first). **NEXT (user): AirDrop the 0.3.59 DMG
> to the macOS-15 laptop → confirm it LAUNCHES (the whole point) → onboarding →
> record→summarize → verify the Settings model picker.** If it launches clean,
> then `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh` to wire the
> update toast.
> **07-24 ~5pm — 🔴🔴 0.3.58 CRASHED AT LAUNCH ON macOS 15 → ROOT-CAUSED + FIXED →
> 0.3.59.** User installed the notarized 0.3.58 DMG on the new laptop (macOS
> **15.7.3**) → **instant launch crash** (Gatekeeper was fine; this is a dyld
> error): `Symbol not found: _OBJC_CLASS_$_SCScreenshotConfiguration` (a macOS-26
> ScreenCaptureKit class). **CAUSE:** `Cargo.toml` had `screencapturekit
> features=["macos_26_0"]` → **strong** link to a macOS-26-only class; missing on
> macOS 15 → dyld aborts before any code runs. **LATENT in every recent build** —
> only surfaced now because this is the FIRST macOS-15 test machine (all earlier
> testers were on macOS 26). **FIX:** cap the feature at the deployment target →
> `features=["macos_14_4"]` (we only use base SCStream audio; no feature loss).
> **VERIFIED:** `cargo check` ✓; `nm -m` on the rebuilt binary shows
> SCScreenshotConfiguration strong-ref **GONE**, all remaining strong SC* refs are
> base APIs present on 14.4+. Bumped **0.3.58 → 0.3.59** + CHANGELOG +
> LESSONS_LEARNED. **NEXT: re-run the notarized build (0.3.59) → new DMG → retest
> launch on the macOS-15 laptop.** The broken 0.3.58 DMG is discarded (never
> published). ⚠️ RULE: screencapturekit feature MUST equal the deployment target;
> test on a min-OS Mac, not just the newest-OS build machine.
> **07-24 ~4:30pm — 🚢 PRODUCT NOTARIZATION QUEUED — machine VERIFIED release-ready;
> one blocker = the Formspree endpoint.** User wants the beta turned into a proper
> product build. Ran the read-only preflight (NOTARIZATION.md §3): ✅ Developer ID
> identity `4MY4PH5PHC` present · ✅ cert valid **→ 2027-02-01** · ✅ Tauri updater
> key present AND its pubkey **matches** the one pinned in the app · ✅
> `adversaria-notary` notary profile validates (prior Accepted submission). Nothing
> built yet. **Version staying 0.3.58** (user's call; save 1.0.0 for public launch).
> Channel undecided (Claude rec: **beta** for THIS acceptance build → promote the
> exact accepted artifact to stable at launch per NOTARIZATION.md §8). **ONLY missing
> input: the production `ADVERSARIA_FORMSPREE_ENDPOINT`** — NOT on this machine
> (0 hits in shell history, no baked release binary); user gets it from the
> **formspree.io dashboard** (Forms → Adversaria form → `https://formspree.io/f/<id>`)
> or their password manager. **NEXT (waiting on user):** (a) `! export
> ADVERSARIA_FORMSPREE_ENDPOINT=…` then Claude runs the full notarized build +
> publish; OR (b) Claude builds now with `ADVERSARIA_ALLOW_INCOMPLETE_REGISTRATION=1`
> (installs clean, notarized; only the in-app beta sign-up queues) to test on the
> new laptop today. Then clean-Mac acceptance (NOTARIZATION.md §5.3, no xattr bypass).
> **→ CORRECTION (~4:45pm): Formspree is NOT a notarization blocker.** The prior
> notarized **0.3.49/0.3.50** builds shipped with `ALLOW_INCOMPLETE_REGISTRATION=1`
> and **no endpoint baked** (verified live on the clean machine — STATUS:341 "no
> endpoint baked — verified"; freeze log STATUS:269-270). build-dmg.sh's Formspree
> gate is independent of RELEASE_MODE and bypassable, so notarization only needs the
> Developer ID + notary profile (both verified ready). **The product build is
> UNBLOCKED — Claude can run the identical notarized build now, no endpoint hunt.**
> Formspree only matters if the in-app beta sign-up should actually submit (it has
> ALWAYS just queued locally in shipped builds). Waiting only on the user's "go" +
> channel (rec: beta). NOTE: NOTARIZATION.md §4 prose overstates the endpoint as
> release-required — doc is stricter than the script; reconcile that line.
> **→ BUILD IN FLIGHT (~4:50pm):** notarized 0.3.58 beta build running (bash
> scripts/build-dmg.sh; log at scratchpad/build-0358.log). Progress: ✅ both
> sidecars frozen, ✅ all ~650 Mach-O signed (Developer ID) + updater archive
> re-signed (`Adversaria.app.tar.gz.sig`), app "valid on disk"; 🔄 stage 6/7 DMG
> packaging → 7/7 = Apple notarize+staple+Gatekeeper pending. No errors, no stuck
> keychain prompt. On success: `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/
> publish-release.sh` (writes latest-beta.json → wires the update toast) + AirDrop
> the DMG to the new laptop for clean-Mac acceptance (§5.3).
> **→ ~5pm UPDATE: reached 7/7 — DMG built (748M) + signed + UPLOADED to Apple**
> (`Adversaria-0.3.58-beta-macos-arm64.dmg`, notary submission id
> `05215225-a421-4f7d-8618-2d3b4d9872ee`), Apple status = **In Progress** (script
> is `--wait`-ing). All local stages clean. When Apple returns Accepted the script
> auto-staples + runs the final Gatekeeper check + writes provenance, then exits.
> **RESUME (if this session drops before it finishes):** check
> `xcrun notarytool info 05215225-a421-4f7d-8618-2d3b4d9872ee --keychain-profile
> adversaria-notary`; if Accepted but not stapled, `xcrun stapler staple` the DMG
> above + `stapler validate` + `spctl --assess --type open`. Then
> `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh "0.3.58 …"`, then
> AirDrop the DMG to the new laptop.
> **→ ✅✅ 0.3.58 NOTARIZED, STAPLED & VERIFIED (~5:15pm) — PRODUCT BUILD DONE.**
> Apple notary **Accepted** (job 05215225…); stapled; independent re-check: `spctl`
> = **accepted, source=Notarized Developer ID**, `stapler validate` ok, app
> CFBundleShortVersion = **0.3.58**. **DMG: 748 MB · sha256
> `6a46ddcc9513a57cc9601e13f6de714718fc8668d4fccdbea6cc3dcdb9312a45`** at
> `src-tauri/target/release/bundle/dmg/Adversaria-0.3.58-beta-macos-arm64.dmg`.
> **NOT YET PUBLISHED (deliberate):** acceptance-test on the new laptop FIRST
> (NOTARIZATION.md §5.3 — download via real path, no xattr; install → record →
> summarize → verify the new Settings model picker), THEN
> `ADVERSARIA_RELEASE_CHANNEL=beta ./scripts/publish-release.sh` so an untested
> build never auto-pushes to existing beta testers. Demo the update toast by
> installing 0.3.58 on the laptop and later publishing 0.3.59.
> **07-24 ~3:50pm — 🚢 0.3.58 RELEASE PREP (COMMITTED, awaiting user's notarized
> build).** Bundles the setup/model-UX feature below + a real auto-update bugfix.
> **🔴 FIXED — auto-update channel mismatch:** installed beta builds poll
> `latest-beta.json` (tauri.beta.conf.json) but `publish-release.sh` wrote
> `latest.json` → the "Update available" toast could NEVER fire. publish-release.sh
> now writes `latest-${CHANNEL}.json` (default beta) matching the baked endpoint.
> The rest of the auto-update chain already existed and is correct (UpdatePrompt.tsx
> toast + updater plugin + signed .app.tar.gz + LaghariLabs/adversaria-releases).
> Version bumped **0.3.57 → 0.3.58** (package.json/tauri.conf/Cargo + lock) +
> CHANGELOG (Added: Settings model picker · Changed: simpler setup · Fixed:
> channel mismatch). cargo check ✓ · publish-release.sh `bash -n` ✓. Committed
> locally (NOT pushed; parallel-session files left untouched). **NEXT — USER
> RUNS (needs Apple secrets I don't hold):** (1) notarized build via the exact
> RELEASE_MODE=1 command in the response / NOTARIZATION.md §4 (Developer ID +
> adversaria-notary + Formspree endpoint + updater key, ADVERSARIA_INSTALL=0),
> (2) `scripts/publish-release.sh "notes"` to push it, (3) install the DMG on the
> new laptop. To TEST the update toast: install 0.3.58 there, then later publish
> 0.3.59 → the laptop shows "Update available" on next launch. NOTE: the
> setup-model-UX feature has NOT been dev-smoked — the new-laptop test is its smoke.
> **→ 07-24 ~4pm — 📄 NOTARIZATION RUNBOOK now TRACKED + all work PUSHED
> (ac1ad36).** The parallel session's `docs/NOTARIZATION.md` (439-line Developer
> ID signing/notarization/stapling/Gatekeeper runbook — account 4MY4PH5PHC,
> `adversaria-notary` profile, release command, failure recovery, updater-key
> separation, CI secrets; no secrets in it) is committed + cross-linked from
> SPEC_DMG_PACKAGING.md. **All 0.3.58 + docs commits are on origin/master.** Still
> untracked (deliberate): `.github/` CI (needs `gh auth refresh -s workflow`),
> marketing/, video/. Unchanged NEXT: user runs the notarized build (NOTARIZATION.md
> §4) → publish → new-laptop test.
> **07-24 ~12:45am — 🟣 SETUP/MODEL-SELECTION UX (reqs 1+3+4) BUILT (now committed
> in 0.3.58; implemented directly by Claude, not delegated).** Per SETUP_MODEL_UX.md's
> "recommend ≠ force." **(1+3) Welcome model step** now leads with ONE
> recommended card + RAM-reasoned copy ("Your Mac has N GB, so <model> is
> recommended — it fits and runs fast"); the other profile hides behind a quiet
> **"Change model"** `<details>` (was two co-equal radio cards). **(4) NEW
> Settings › AI Engine on-device model picker** (Local engine only, gated on
> `rapid_runtime_bundled`): lists the pinned MLX profiles, marks recommended +
> "In use", per-row Use/Download/Retry with live progress. **NEW Rust
> `set_local_model_profile` cmd** (validates installed via `pinned_snapshot` →
> persists selection → restarts managed Rapid-MLX; managed base URL is read
> fresh per request, so the switch needs **NO app restart**) + a
> `registration::set_selected_model_profile` helper that — unlike
> `complete_step` — never touches `setup_complete` (so a Settings switch can't
> bounce an onboarded user back into the wizard). Files: registration.rs,
> commands.rs, lib.rs, tauri.ts, Settings.tsx, Welcome.tsx, prototype.css.
> **Verified by Claude: tsc ✓ · cargo check ✓ · cargo test 132 ✓ · vitest 15 ✓.**
> **DEFERRED (user-decided): req #2** (Ollama `/api/tags` cross-runtime reuse) —
> needs the localhost≠cloud provider fix; scoped as a follow-up. **NEXT: user
> dev-smoke** — Settings › AI Engine, switch 4B↔27B, confirm a local summary
> uses the new model without an app restart — then commit + refreeze. Sibling
> UX for the still-open 🚨 8 GB perf launch-blocker.
> **07-20 ~11pm — 🟣 NOTCH PILL TIER 1 BUILT (UNCOMMITTED):** first slice of the
> notch-pill feature (build greenlit; Option A path). Two config fields
> `notch_pill_style` (minimal|expressive|hidden) + `meeting_alert_style`
> (notch_drop|pill_nudge|off) in types.rs/config.rs + frontend types.ts/fixtures;
> new **"Notch & alerts"** Settings group (2 dropdowns, honest "not wired yet"
> copy on expressive/pill_nudge/off). **RecordingBubble restyled to the approved
> B2 "minimal" mock** (artifact 912ff9c9): pure-black notch-drop pill (square top,
> rounded bottom), red pulsing dot + mono timer left, blue live waveform right;
> inline Stop KEPT (deliberate deviation from the glance-only mock — user demos
> with it). `show_recording_bubble` now gates on `hidden`; pill window 196×44@14 →
> 210×30@0 (hugs the top). Delegated to stunt worker ($0.78, ZERO review fixes);
> cargo ✓ tsc ✓ vitest 15 ✓, all run by Claude. **NEXT: user eyeballs in dev**
> (⚠️ #1 check — a 210px pill centered under the *physical* notch may hide
> content behind it; widen/reposition if so). Remaining slices: T2 A4 pill-nudge
> + quick-hide · T3 A2 notch-drop island + multi-display notch fix (objc2-app-kit)
> · T4 B3 expressive NSPanel conversion (the real Option A). Scope+sequencing in
> docs/NOTCH_PILL_SCOPE.md.
> **→ 07-21 ~6:35am — preview artifact 713a6fb6 rendered the shipped pill 1:1
> under a to-scale notch → confirmed the "as built" y=0 centering HIDES content
> behind the ~200px physical notch. USER PICKED Fix A** (drop below the notch):
> `MARGIN 0→38` (commands.rs) + pill `border-radius: 0 0 18px 18px → 16px`
> (index.css) = a standalone rounded pill below the menu bar, visible on
> notched + non-notched displays. cargo ✓ tsc ✓. Bumped **0.3.51** (pkg/
> tauri.conf/Cargo + lock) + CHANGELOG. **🚢 FREEZING 0.3.51** (staging build
> "for me to test"): NotchyPrompter Dev identity, ALLOW_INCOMPLETE_REGISTRATION,
> INSTALL=1, from in-repo snapshot .freeze-snap-0351.sh (concurrent session
> live). **✅ 0.3.51 SHIPPED, INSTALLED & VERIFIED (~6:47am):** Info.plist
> 0.3.51 · codesign Authority=NotchyPrompter Dev (TCC preserved) · running
> binary = /Applications (built 06:45) · sidecar /health ok (large-v3 + ollama)
> · fresh dist embeds `.record-pill` + `border-radius:16px`, no stale
> `.record-bubble`. NOT committed — awaiting user's staging verdict (eyeball the
> pill below the notch during a recording), then commit/push on word. Fix B
> (flank the notch, native pixels) held for Tier 3.
> **→ 07-21 ~7:30am — 🟣 TIER 4 EXPRESSIVE + NSPanel BUILT (UNCOMMITTED),
> FREEZING 0.3.52.** User: expressive "didn't work" (it was a placeholder that
> fell back to minimal) → chose "build expressive now." Researched tauri-nspanel
> v2.1 (agent, cited): pinned `rev a3122e89`, `WebviewWindowExt::to_panel`;
> non-activating + `full_screen_auxiliary` + `can_join_all_spaces` floats over
> fullscreen WITHOUT going dockless (Accessory optional); #5566 "works-in-dev-
> fails-in-release" IS fixed by converting to an NSPanel. **KEY PIVOT:** CSS
> `pointer-events:none` does NOT click-through in Tauri → a big transparent
> hover-bloom window would block clicks to the call. So expressive v1 = a
> **persistent opaque island HUD** (title · timer · live caption via the
> `live-transcript` event · dual waveform · Stop), NOT the mock's hover-bloom
> (that's a follow-up needing native window-resize or ignores-mouse toggling).
> Built: nspanel dep (macOS), plugin init (macOS cfg), `tauri_panel!`
> RecordingPanel + `to_panel` conversion in `show_recording_bubble` (sizes
> 210×30 minimal / 330×92 expressive, `style` query param), island component +
> CSS, caption listener. cargo ✓ tsc ✓ vitest 15 ✓. Bumped 0.3.52 + CHANGELOG.
> Freeze running. **Both minimal + expressive are now non-activating panels that
> float over fullscreen.** NEXT: user tests — (a) THE GATE: pill floats over a
> FULLSCREEN Zoom and clicking it doesn't steal focus, (b) expressive shows the
> island + live captions. Then decide hover-bloom polish vs keep persistent.
> 0.3.51 + 0.3.52 both uncommitted, awaiting verdict + commit word.
> **→ 07-21 ~8am — 🔴→✅ 0.3.52 WOULDN'T LAUNCH; ROOT-CAUSED + FIXED → 0.3.53.**
> Verifying 0.3.52 found the app HUNG at startup (no window, no sidecar). `sample`
> stack: `setup()` → `recover_recordings` (line 103, SYNC) → `prepare_for_
> transcription` → `recording_key` → `keyring::get_password` — blocked on a hidden
> macOS **Keychain prompt** (re-signed build re-prompts for `adversaria-recordings/
> spool-key-v1`; pending spools exist to recover). Runs BEFORE the event loop, so
> the whole app hangs. **PRE-EXISTING latent bug, NOT the nspanel/expressive code**
> (that released-compiled clean). Fix: `recover_recordings` now runs on a
> background thread (lib.rs) — window + sidecar come up first, any Keychain prompt
> shows over the running app. cargo ✓. Bumped 0.3.53 + CHANGELOG (Fixed).
> Re-freezing 0.3.53 = the launch fix + all of 0.3.52. **✅ 0.3.53 SHIPPED,
> INSTALLED & VERIFIED (~8:20am): APP LAUNCHES** (window shows + sidecar child
> /health ok on :55134, large-v3+ollama) — the hang is GONE. Info.plist 0.3.53 ·
> NotchyPrompter Dev · process-path=/Applications · dist embeds .record-island +
> live-transcript. SecurityAgent prompt now appears OVER the running app
> (non-blocking) = fix proven. **NEXT: USER TESTS** — (1) THE GATE: pill floats
> over FULLSCREEN Zoom + click doesn't steal focus; (2) Settings→Notch pill→
> Expressive = island HUD + live captions; approve the one-time "adversaria-
> recordings" Keychain prompt (Always Allow) so recovery completes. Then hover-
> bloom polish decision. Uncommitted: 0.3.51+0.3.52+0.3.53 (one notch-pill tree),
> awaiting verdict + commit word.
> **→ 07-21 ~10:20am — 🔴 0.3.53 CRASHED DURING RECORDING → NSPANEL REVERTED →
> 0.3.54.** User: "it's been crashing." Two `.ips` crashes (08:10, 10:13), both
> during active recording, main thread, **Rust panic across the ObjC boundary
> (SIGABRT)** in tao's run-loop observer. Unified log smoking gun: `makeKeyWindow`
> on `<RecordingPanel>` returned NO from `canBecomeKeyWindow` right before the
> crash; 08:10 was mid window-close. **CAUSE: the NSPanel conversion** — once the
> pill is a non-activating panel, Tauri's `win.close()` (hide path, every focus
> toggle) and `win.set_focus()` (drag path) panic. 0.3.51 (plain window) never
> crashed. **FIX = REVERT the panel** (removed `to_panel`/macro/plugin/dep;
> cargo/tsc/vitest ✓, nspanel gone from lock). Pill (minimal + expressive island)
> is a plain floating window again = stable. KEPT: expressive island UI, live
> captions, Settings, Fix A, launch-hang fix. LOST: float-over-fullscreen —
> deferred to a properly-prototyped redo (reuse/order-out lifecycle, never
> close/set_focus the panel; docs/NOTCH_PILL_SCOPE.md). Freezing 0.3.54; verify
> launch + stable recording. Uncommitted: 0.3.51→0.3.54 (one tree).
> **→ 07-21 ~10:35am — ✅ 0.3.54 STABLE (no crash), but expressive island showed
> "Listening…" with NO live caption → FIXED → 0.3.55.** User confirmed: live
> transcript works in the MAIN window but not the pill. Root cause: Tauri 2
> **capabilities** — `capabilities/recording-bubble.json` had `permissions: []`,
> so the pill webview could call its custom commands (timer worked) but had NO
> `core:event` permission → `listen("live-transcript")` never received the
> broadcast (main window HAS `core:event:allow-listen`). Fix: granted the pill
> `core:event:allow-listen` + `allow-unlisten`. cargo check validated. Bumped
> 0.3.55 + CHANGELOG. Freezing. NEXT: user confirms the island fills with live
> captions during a recording. Uncommitted: 0.3.51→0.3.55 (one tree).
> **→ 07-21 ~10:50am — ✅ EXPRESSIVE ISLAND CONFIRMED WORKING (captions live!);
> Stop button was CLIPPED → 0.3.56.** User screenshot: island shows Recording ·
> local only · timer · live caption ("hello hello is this working…") — all good.
> But a 2-line caption pushed the waveform+Stop row below the 92px window → Stop
> rendered in the transparent area, cut at the frame. Fix: expressive window
> 92→132px (fits header + 2-line caption + wave/Stop) + `.isl-wave-row
> margin-top:auto` (pins Stop to bottom for 1- or 2-line captions). cargo ✓ tsc ✓.
> 0.3.56 freezing. Uncommitted: 0.3.51→0.3.56 (one tree). Feature now essentially
> DONE minus fullscreen-float (deferred).
> **→ 07-21 ~11am — ✅ Stop button confirmed; 🔑 recurring KEYCHAIN PROMPT fixed →
> 0.3.57.** User: "why does it always ask for password? … Recording encryption key
> is unavailable (User canceled)." = the recording-spool key (`adversaria-
> recordings/spool-key-v1`, PRE-EXISTING, separate from DB-encrypt/notch/biometric).
> Cause: `recording_key()` hit the keychain uncached on every recording start +
> transcription + per pending spool in recovery, and my 6 test builds each looked
> like a new app (Always-Allow didn't carry). Fix: **memoize the key**
> (`RECORDING_KEY_CACHE` static Mutex<Option<[u8;32]>>; success-only, retries on
> cancel) → keychain hit ≤1×/launch. User chose "just the cache fix" (keep
> encryption; declined the plaintext opt-out). cargo ✓. On a committed stable
> build + one "Always Allow" → prompts stop. Bumped 0.3.57.
> **✅ COMMITTED + PUSHED to origin/master (~11:15am) as 5 clean commits
> (20e7d5a..ce02fdd):** feat(notch-pill) dd75d9b · fix(startup) 9af77ad ·
> fix(recording) ca0b09b · docs 4a3b8fa · chore(release) 0.3.57 ce02fdd. Parallel
> session's files (SPEC_DMG_PACKAGING.md, .github/, NOTARIZATION.md, marketing/,
> video/) left untouched. **Notch-pill feature SHIPPED** (0.3.57 installed +
> verified). Only open item: NSPanel fullscreen-float (deferred, prototyped redo).
> **07-17 ~9pm — 🟣 CHAT POLISH built (UNCOMMITTED):** compact Clear/Save
> buttons (scoped off the global btn-secondary flex:1) + the breathing
> cursive-"A" thinking indicator with cycling words in meeting chat. Worker
> $1.66, zero fixes; tsc ✓ vitest 15 ✓ cargo ✓. Mockups artifact 57c74c00:
> chat-polish preview + To-dos T-A/B/C + Weekly W-A/B/C + A-illumination
> A/B (v1 breathe vs v2 TRACE — user's letterform-fill idea, built live).
> Claude rec: T-B + W-A. New ask: same indicator in the Ask tab.
> **→ ✅ ALL FOUR BUILT (UNCOMMITTED):** shared traced-A ThinkingIndicator
> (A-v2) · Ask-tab animation · T-B focus queue (TodosView, "Not mine"
> restored) · W-A Monday briefing (NEW Rust `weekly_briefing` cmd, LLM prose
> grounded on summaries + fail-open, WeeklyView rebuilt). Workers ~$11.5, 2
> review fixes (not-mine regression, ungrounded prose). tsc ✓ vitest 15 ✓
> cargo 120 ✓ pytest 268 ✓. Live dev test found 2 bugs, both fixed direct
> (double thinking-bubble — indicator now INSIDE the streaming placeholder;
> A slimmed 9→4.5 + reproportioned). T-B-with-many-items concern raised →
> scope-chips refinement proposed (chips filter queue per meeting). NEXT:
> user verdicts: W-A prose WORKS · A = v1 breathe (reverted, trace removed)
> · Weekly centered/widened (min(100%,1040px) fluid) · 🔔 ALARMS v1 built
> (reminders.rs digest thread, 2×/day max, cargo 126 ✓, worker $2.00).
> Scope chips + T-A TRIAGE LANES built (worker $1.50): chips filter both
> views; Triage|Focus toggle (default triage, Focus preserved); lanes
> Overdue/This week/Later + Done tray. tsc ✓ vitest 15 ✓. All HMR-live.
> + DRAG-AND-DROP on the lanes (drop = date edit: This week→due today,
> Later→clear date, Done tray→complete; Overdue not a target). Worker $2.03,
> tsc ✓ vitest 15 ✓, HMR-live. Toggle confirmed liked. NEXT: user drags →
> Drag CONFIRMED working (dragDropEnabled:false was it). Editable due
> dates added (hover date-pickers on triage cards, queue rows, hero).
> tsc ✓ vitest 15 ✓. "refreeze" ships everything as 0.3.45.
> GRAPH G-A DOSSIER BUILT (worker $6.45 + 1 review fix — stale upsert id):
> people table + get/save_person + right-side dossier panel (meeting notes
> preview · editable person profiles w/ aliases-as-merge · meetings-together
> · related to-dos). cargo 126 ✓ tsc ✓ vitest 15 ✓. Dev app rebuilt.
> + PEOPLE→VAULT SYNC (cargo 132 ✓). **🚢 0.3.45 SHIPPING:** docs updated
> (CHANGELOG/README/ARCHITECTURE), committed 60eaf61+1770e2b+537aef4,
> **✅ 0.3.45 SHIPPED, INSTALLED & VERIFIED (~00:40):** 0.3.45 ·
> NotchyPrompter Dev valid · /health ok · per-view chunks embedded
> (TodosView/GraphView/WeeklyView). MASTER MERGED+PUSHED (84 commits);
> both branches level. Next: daily-drive · Loom demo · phase-1 inputs ·
> Apple activation watch.
> **07-18 ~10am — 🔍 UX REVIEW DONE (no code changes):** daily-drive feedback
> on 0.3.45 investigated ×4; options artifact e1682883 delivered. Verdicts:
> Insights can only ever name the user (relabel_me is the sole real-name
> injection; others stay Speaker N) → options I-A reframe-as-your-delivery
> (rec) / I-B beta chip / I-C remove · standalone notes NOT new (Jun 20),
> premature = full meeting chrome on notes + "0 min" cards → S-A hide for
> launch (rec) / S-B finish / S-C remove · Weekly nav: middle button always
> says "This week" + no disabled styling → N-A live-label pager (rec) / N-B
> strip / N-C destination arrows · Add-to-dictionary WORKS (live+retranscribe,
> both channels; not on cloud/import paths; untested). AWAITING letter picks.
> **→ ✅ N-A BUILT (worker $0.52, zero fixes, UNCOMMITTED):** weekly nav =
> live-label pager (viewed-week label, return pill when away, disabled-dim ›,
> de-duped subtitle). tsc ✓ vitest 15 ✓. Notes gripe = the "+ New Standalone
> Note" button (S pick pending). Insights ESCALATED: talk-time itself wrong
> (user top talker while speaking least) — mic echo-bleed investigation
> running. **→ VERDICT: numbers confirmed broken** (no AEC + leaky
> strip_mic_bleed · Speaker-N fragmentation + gap-absorption favors Me ·
> VAD keeps full spans off 0.5s slivers) — logged in TODO.md §07-18.
> Artifact updated: NEW I-E hide-for-launch (rec) / I-D staged fix ladder;
> I-A demoted. **→ USER PICKED Beta+delivery-only & hide-notes → BOTH BUILT
> (UNCOMMITTED):** 🟣 Insights = Beta chip + Talk-balance (You vs Everyone
> else) + 4 owner-only delivery cards (worker $0.30) · ✅ standalone notes
> hidden (button unmounted, ⌘⇧N unregistered; My Notes/Structure-with-AI
> untouched). tsc ✓ vitest 15 ✓ cargo ✓. Day's tally: N-A pager +
> insights-beta + notes-hide, all riding the next refreeze. I-D fix ladder
> + S-B finish list open in TODO §07-18. **🚢 0.3.46 SHIPPING (~10:45am,
> "comit and push and refreeze"):** on MASTER (handtest-hardening retired),
> stray 0-byte dist dupes cleared, 0.3.46 bumped + CHANGELOG + README,
> committed d322c46+1a54b90+0365ff4 & PUSHED to origin/master. Freeze
> attempt 1 died on the new Formspree release gate → attempt 2 with
> ADVERSARIA_ALLOW_INCOMPLETE_REGISTRATION=1 (staging norm, same as
> 0.3.45; see HANDOFF gotcha). **✅ 0.3.46 SHIPPED, INSTALLED & VERIFIED
> (~11:05am):** Info.plist 0.3.46 · NotchyPrompter Dev valid · /health ok
> (large-v3 + ollama) · new chunks embedded, standalone-notes strings gone.
> Installed app: weekly pager + Insights Beta + no notes button. USER
> CONFIRMED: weekly + insights look good. Marketing baton
> (STRATEGY_HANDOFF) refreshed to 0.3.46 state; demo script re-validated —
> record as written. **🟣 ~12pm (UNCOMMITTED): sidebar now SCOPES To-dos**
> (click meeting → board filters, chip parade → single [All]+[title ×],
> worker $2.34, tsc ✓ vitest 15 ✓) + **7 synthetic demo meetings** in
> marketing/demo-data (generate.py, dates relative-to-today, import via
> sidebar Import → bundle; fills all triage lanes/graph/weekly).
> **🚢 0.3.47 SHIPPING (~12:05pm "refreeze it"):** committed
> 7c7f010+6da5859+a1d97df, pushing; freeze running (0718c log, staging
> override). 🍎 Notarization audit: pipeline READY, only the Developer ID
> cert is missing (2 user steps, see STRATEGY_HANDOFF §6.2). FIRST TESTER
> identified (meeting-hopper friend) — invite draft in marketing/beta/.
> **✅ 0.3.47 SHIPPED & INSTALLED (~12:45pm)** · authority valid ·
> sidebar-scope chunk embedded. **→ 🔴 "old version" incident:** `open -a`
> had launched a stale DEBUG bundle (its sidecar faked the /health pass) —
> impostor killed, debug bundle deleted, /Applications launched by path,
> ps+screenshot verified (LESSONS entry added). **→ ✅ 7 demo bundles
> imported via AX automation** (TCC Documents re-prompt unblocked; app
> re-summarizes/re-titles imports via LLM queue — expected; README
> updated). ONE DUP: two Jul-1 "Intake…" meetings — **USER deletes one**
> (automated delete aborted after wrong-target near-miss; rule: no
> destructive UI automation). **🔴 ~1:15pm VOCAB-ECHO REGRESSION:** fresh
> recording's transcript starts with shuffled glossary echo ("Tatweer OS,
> Echelon, Tatweer…" = the exact dictionary) — **VERDICT: the 07-16 fix
> is VAD-only (no text matcher exists)**; echo riding voiced audio (mic
> narration + YouTube on system track) passes untouched. Fix proposed:
> token-set `strip_glossary_echo` on final paths + tests. **→ ✅ BOTH
> BUILT as 0.3.48** (user also reported duplicate sentences = bleed-dedup
> 0.85-ratio hole): glossary-echo text gate (both dual paths) +
> containment fallback in strip_mic_bleed (worker $1.80, pytest 276 ✓).
> **✅ 0.3.48 SHIPPED, INSTALLED & VERIFIED BY PROCESS PATH (~3:40pm):**
> 0.3.48 · authority valid · running binary confirmed = /Applications ·
> /health ok. Echo + duplicate fixes live for new recordings; DMG =
> friend build. build-dmg.sh changes restored to tree (uncommitted,
> ownership pending).
> **🌙 SESSION CLOSED ~4pm — day's tally: 0.3.46 + 0.3.47 + 0.3.48
> shipped/installed/verified; demo data imported; four UX verdicts
> executed; 2 LESSONS + fix ladders recorded. USER QUEUE: dup delete ·
> build-dmg.sh ownership · Apple cert two-step · friend DMG+invite ·
> re-record walkthrough · Loom · phase-1 inputs. Full digest at the top
> of HANDOFF.md.**
> **→ 🚢 0.3.49 addendum (~6:35pm):** To-dos sidebar highlight now tracks
> the scope (selectedId prop switch, display-only) + tab counts fixed to
> match the visible pool (were counting raw items incl. done/not-mine —
> "Upcoming (9)" over 7 rows). tsc ✓ vitest 15 ✓ · committed+pushed.
> Freeze attempt 1 KILLED — a concurrent editor (Codex?) wrote
> build-dmg.sh mid-execution (bash reads incrementally → phantom syntax
> error; LESSONS entry added). Snapshot protocol corrected after 4 failed
> launches (script SELF-LOCATES root from BASH_SOURCE — snapshot must
> live IN scripts/, not /tmp; LESSONS fixed). **✅ 0.3.49 SHIPPED,
> INSTALLED & VERIFIED BY PROCESS PATH (~7:15pm):** 0.3.49 · authority
> valid · /health ok · new TodosView chunk embedded · snapshot deleted.
> Installed app: scope highlight + honest counts + all of today — USER
> CONFIRMED both work. **🍎 NOTARIZATION DONE (user, via the parallel
> workstream's flow):** Developer ID cert live, 0.3.49 DMG stapled +
> Gatekeeper-accepted → friend (works at Aleph Alpha) gets THE NOTARIZED
> DMG, no install friction. Website-download ask → R2 plan queued
> (STRATEGY_HANDOFF §1, awaiting go). Launch gate remaining:
> clean-machine test. build-dmg.sh foreign edits = the notarization flow —
> RESOLVED: the parallel session committed them itself (f0ec7f2 +
> 8d85ed8); tree clean; stash@{0} superseded (droppable). AUTO-UPDATE:
> full chain already built (plugin + UpdatePrompt + signed archives +
> public releases repo w/ June releases); one gap = publish-release.sh
> writes stable latest.json while today's builds poll latest-beta.json —
> patch on word, then updates pop up on the friend's Mac automatically.
> 🧪 CLEAN-MACHINE TEST live (2nd Mac, notarized DMG's first runtime):
> registration queue = EXPECTED (no endpoint baked — verified);
> "setup service not ready" = sidecar not up yet — entitlements verified
> INTACT in the DMG; sidecar came up after the first-launch deep-verify,
> download started. FULL CHURN REPORT captured → **TODO §SETUP-WIZARD
> CHURN BUNDLE** (blocking download, no %/ETA, blurred status, Ollama
> not explained, registration hide) = the next build bundle. hf_xet
> ruled out (env var baked, commands.rs:119). **ROUND 2 — TWO
> LAUNCH-BLOCKERS FOUND & FIXED → 0.3.50 (pytest 276 ✓):** ffmpeg
> dependency (MLX now decodes in-process via PyAV) + missing audio-input
> entitlement on the main app (mic prompt never appeared on fresh Macs).
> Wizard round-2 items logged (permissions step, guided first meeting,
> queued-no-button, Spotlight). **✅ 0.3.50 SHIPPED & VERIFIED (00:14,
> after one stranded-dist wedge + recovery):** audio-input entitlement
> CONFIRMED on the installed app · process-path verified · /health ok.
> DMG (00:14) ready to AirDrop to the test Mac → retest mic prompt +
> transcription. **→ ✅ NOTARIZED 0.3.50 COMPLETE (~1:15am):** staple ✓ ·
> Gatekeeper accepted ✓ · audio-input entitlement ✓ —
> Adversaria-0.3.50-beta-macos-arm64.dmg = THE friend/test build.
> Clean-machine night's haul: mic fix CONFIRMED live · ffmpeg fix
> awaiting the clean-install pass · wizard churn bundle grew to ~10
> items. Gatekeeper/TCC churn on the dev-signed copy abandoned.
> **07-19 morning — ROUND 3 (logged only, user still testing):**
> "not recording" at stop while audio actually spooled (state desync;
> orphan surfaced after relaunch) + wizard name never saved to
> `user_name` ("Me" everywhere). TODO §Round 3. PLUS: live-caption lag on
> 8 GB hardware · recording-during-transcription starves live captions +
> FALSE silence prompt (auto-discard hazard — watchdog keys on captions
> not audio energy). Both meetings DID transcribe (queueing, not loss).
> **8 GB OPTIMIZATION RESEARCH running** (deep-research workflow:
> quantized whisper tiers, whisper.cpp vs MLX, streaming captions,
> memory orchestration, competitor defaults → RAM-tier ladder).
> Research distilled → **docs/PERF_8GB.md** (8 GB: turbo-4bit shared +
> ≤3B LLM + never-two-models-resident; Arabic floor = turbo). NEW living
> lab notebook **docs/OBSERVATIONS.md** (user ask) w/ EXP-1 (WAV→MP3
> A/B, awaiting user's recording) + EXP-2 (model tiering). **EXP-3
> summarizer bench BUILT** (user finding: 4B≈35B with the prompt; testing
> 0.8B map-reduce): blind judge packs, portable, smoke-validated; small
> models pulling → DRY RUN DONE 28/28 (0.6B 2-6s vs 4B 47-157s;
> spot-check split — blind judging next; packs in
> experiments/summarizer-bench/results/) → USER CORRECTED: test the REAL
> interviews. One exported ("Technical Interview for Lead AI ML
> Engineer", 70KB) → matrix running into gitignored results-real/.
> User unlocked+exported 4 more → 5 real bundles (21-46K chars). Bench
> caught two of its own bugs on real data (num_ctx truncation ·
> qwen3 thinking emptying responses) — both fixed; run 3 done →
> **FIRST BLIND VERDICT (Lead AI/ML interview): production 35B WON 8/10**
> · 0.6B-MR 3 · 0.6B-single 1 (degenerate) · 4B-single 3 (CoT leak =
> HARNESS BUG: "not JSON" appended onto a JSON-demanding prompt). Fixed
> (markdown-native prompt). USER SPECIFIED the real model:
> **qwen3.5:0.8b-mlx** (I'd proxied 0.6b) — pulled → **clean run in flight,
> tiers 0.8b-mlx/1.7b/4b × 2 pipelines × 5 meetings + 35B baseline**.
> First run caught bench bug #3: qwen3:4b/1.7b ignore Ollama think:false
> → untagged reasoning leak (0.8b-mlx clean). Fixed (strip_preamble to
> first ###). **USER: no older models — only qwen3.5+/gemma4.** Dropped
> all qwen3.x; gemma4 not in this registry; pulled qwen3.5:2b/4b. Clean
> modern-ladder run DONE (30/30 clean; 0.8b-mlx 8.5s/17.4s · 2b · 4b
> 20/49s). Finding: 0.8b-mlx SINGLE degenerated on a dense meeting but
> its MAP-REDUCE stayed clean. **⭐ 2ND VERDICT (Dashboard): qwen3.5:4b
> MAP-REDUCE BEAT the 35B 8–4 — the 35B HALLUCINATED ATTENDEES (junk
> transcript). Map-reduce lifted every tier. NEW 🔴 product bug: shipping
> summarizer invents attendees from caption/mic junk (TODO §07-19).**
> **❌ RETRACTED (Hamza caught it): my "35B hallucinates 13 attendees"
> finding was WRONG — those names are REAL, in the bundle attendees
> METADATA; faithfulness.py v1 checked transcript only. Fixed → 0
> fabrications for ALL models incl. 35B; NO attendee bug.** Comparison was
> also unfair (35B got the roster, small models didn't) → tier question
> REOPENED; bench fixed to pass attendees → fair re-run done (single). Real
> finding: qwen3.5:4b USES the roster + maps speakers (≥ 35B); 0.8b-mlx
> pulls vocab-echo junk into attendees (tiny-model weakness). map-reduce
> 🏁 **EXP-3 DONE — Hamza judged all 5; remapped letter→model (per-meeting
> shuffle invalidated the letter leaderboard). RESULT: qwen3.5:4b SINGLE
> (7.0) TIED the production 35B (7.0) → 8GB LLM tier = qwen3.5:4b
> single-shot (PERF_8GB updated). MAP-REDUCE REJECTED (lost at every
> tier; my earlier loop-helps claim was from unfair runs).** 🚨 **8GB
> TIMING: a meeting took ~30 MIN to process on the 8GB Mac — LAUNCH
> BLOCKER (big model swapping). Fix = implement PERF_8GB tiering
> (qwen3.5:4b-single + turbo-4bit whisper + load/unload). Now top
> priority (TODO 🚨).** + SETUP-UX directive → docs/SETUP_MODEL_UX.md:
> simple setup · detect user's existing Ollama models (reuse not
> re-download) · recommend-not-force · Settings model picker (infra:
> setup.rs qwen-4b-light = EXP-3 winner). **+ 3 UX mockup artifacts
> (setup-model, capture-UX, notch-pill) — all linked in SETUP_MODEL_UX.md.
> NOTCH PILL DECIDED: ship A2 notch-drop + A4 pill-nudge + B2 minimal +
> B3 expressive, user-selectable in Settings (2 config fields).
> SCOPED → NOTCH_PILL_SCOPE.md: surface ALREADY EXISTS (recording bubble =
> top-center transparent always-on-top pill w/ live waveform; B2 ~90%
> built). **SCOPE FINALIZED (research done): tiers 1-2 (B2+A4+config+
> Settings) = pure reuse, ship now (fix built-in-screen multi-display bug);
> A2/B3 need tauri-nspanel NSPanel + Accessory-for-fullscreen. Screen-share
> visibility ✅ DECIDED: acceptable + add HIDE capability (quick-hide, folded
> into tier 2). native-vs-Tauri → HYBRID (Hamza: "integrate the Swift UI in
> Tauri?"): YES — ship the native NotchyPrompter overlay as a 3RD SIDECAR
> (same bundle+spawn+sign as Python service/Rapid-MLX); helper owns its
> NSPanel natively → sidesteps ALL Tauri notch pain; B3 = plumbing not R&D.
> **B3 plan finalized: IPC=stdin/stdout JSON (not HTTP); helper=bare Mach-O
> .accessory, ~3-4d mostly deleting NotchyPrompter code; FFI rejected.
> 💡 REAL FORK: transparency already works, only gap = non-activating clicks
> → Option A′ convert existing bubble to NSPanel (~1 day, no Swift) vs Swift
> helper (~3-4d native pixels). ✅ TRANSPARENCY VERIFIED in packaged 0.3.50
> (bubble corners transparent, no white box → #13415 doesn't bite) → Option
> A′ (~1 day) is the clear cheap path, Swift helper = optional native-pixels
> upgrade. ✅ DECIDED: OPTION A (NSPanel conversion, ~1 day) = the build now;
> OPTION B (native Swift helper, ~3-4d) = future update, recorded.** Still
> real: mic-junk. Dev-Mac
> scare = file cache (measured; app idles 0.3GB). Next build session: round-3
> fixes + ~14-item wizard bundle + 8 GB tiering.
> **2026-07-16 (11pm) — 🌙 DAY CLOSED at an all-time high.** Shipped v0.3.43 ·
> lagharilabs.com LIVE (site + /adversaria + D1 waitlist + Resend
> confirmations + inbound email, all e2e-verified) · **Apple Developer
> enrollment DONE** (hard launch gate cleared) · marketing toolkit installed
> + two-phase plan set. TOMORROW (user): Loom demo video (AFTER Claude's
> script — ask "write the demo video script") · delete the Resend setup key ·
> X/LinkedIn handles + PH account + first-10 list → "start phase 1" · watch
> for Apple activation email (→ cert → notarized build → gate #1 green).
> Full pick-up list at the top of HANDOFF.md. **NEW (07-17): marketing
> workstream baton created — docs/STRATEGY_HANDOFF.md** (funnel state, phase
> plan, toolkit, queue — read before any GTM work). ✅ Demo-video SCRIPT
> done (marketing/demo-video/SCRIPT.md — demo-is-the-meeting + Wi-Fi-OFF
> beat). Next: USER records Loom takes; phase-1 inputs still owed.
> **🟣 (evening) # TAG SEARCH built + search focus-ring fix** (mirrors
> @people; shares the pill row's single-select state; chip + keyboard nav;
> tag labels in the text haystack). Worker $1.92 + 1-line review fix; tsc ✓
> vitest 15 ✓ cargo ✓. → 🚢 SHIPPING as v0.3.44 ("refreeze then"):
> committed `e316a5d` + `cd89731`. Freeze attempts 1–2 wedged on stranded
> duplicate dist trees from the 07-16 killed builds (APFS rm quirk — new
> LESSONS entry); dists loop-rm'd clean → attempt 3 CLEAN.
> **✅ 0.3.44 SHIPPED, INSTALLED & VERIFIED (~8:15pm):** Info.plist 0.3.44 ·
> NotchyPrompter Dev valid · /health ok · tag-search in embedded chunk
> index-EUZs1oLh.js (app is code-split — grep ALL index chunks when
> verifying). Next: user smoke-test # search.
> ("Dicussion" pill = data typo, rename via tag UI.)
> **2026-07-16 (2:35pm) — 🔴→✅ PHANTOM NO-SPEECH MEETINGS now AUTO-DISCARDED
> (stunt-delegated, UNCOMMITTED).** User hit `Summarization failed:
> {"detail":"Transcript is empty."}` — post-VAD a silent/accidental recording
> transcribes to EMPTY, `/summarize` 400s, and the row strands as an
> un-retryable "Untranscribed recording" phantom. Now: empty transcript + no
> typed notes → meeting + audio + recovery state deleted automatically (amber
> notice "Recording discarded — no speech was detected."); empty transcript +
> typed notes → kept as a notes-only meeting (user content never destroyed);
> silent IMPORTS → clear error, no pending row. Also fixed the logged backlog
> bug: `delete_meeting` now removes the retained recording +
> `recording_assets` row (no more orphaned "Queued" rows from manual deletes).
> Rust+TS only — no Python change, so `tauri dev` fully exercises it; reaches
> /Applications on the next freeze. Worker `6d6c3c2f` $7.62, 1 style round;
> Claude-verified: cargo 120 ✓ (+3) · tsc ✓ · vitest 14 ✓ (+1).
> **✅ SMOKE-TESTED END-TO-END (2:50pm, real data):** the user's actual phantom
> (meeting 146, a 3.2s accidental capture from the 2:13pm error) was
> auto-discarded by the dev app on launch — meeting row, `recording_assets`
> row, and spool dir all verified gone; the user's follow-up real recording
> became meeting 147 with a clean transcript/summary. NEXT: commit word →
> ride the next freeze.
> **🔴→✅ both live-test bugs FIXED same session (~3:15pm, stunt-delegated,
> UNCOMMITTED):** atomic start guard in `AudioCapture::start()` (macOS
> compare_exchange / Windows one-lock-hold, rollback on spool failure) +
> await-safe tray/hotkey unlisten in App.tsx + "Already recording" status
> resync in useRecording + `is_repetition_loop()` gate in `/live_feed`
> (≥8 tokens ≤2 distinct, live-preview only). Worker `a8214a16` $2.01, zero
> review fixes; Claude-verified tsc ✓ · vitest 15 ✓ · cargo 120 ✓ ·
> pytest 268 ✓. Zombie spool + asset row cleaned (DB backup kept).
> **(diagnosis detail below)**
> **2026-07-16 (~3:45pm) — 🚢 v0.3.43 SHIPPING (user tested the race fix in
> dev: "works").** Committed: `734309f` fix(recording) auto-discard + atomic
> start · `add433d` fix(live) rep-loop gate · `9459c87` chore(release) 0.3.43
> · `cfbaa45` docs(baton). **PUSHED — handtest-hardening in sync with origin
> (15 commits incl. the 0.3.42 pile; master untouched).** Freeze attempt 1
> died on a transient codesign timestamp flake (1 dylib after 645 clean
> signs); attempt 2 died the same way (different dylib) → `build-dmg.sh`
> hardened with a 3-attempt `sign_file()` retry (`8d85ed8`, pushed).
> **✅ SHIPPED, INSTALLED & VERIFIED (~4:15pm):** attempt 3 clean (all 7
> steps, zero retries needed) · Info.plist **0.3.43** · NotchyPrompter Dev,
> deep-strict valid · sidecar /health ok (:55706, large-v3, ollama up) ·
> binary embeds `index-DjyDSWH6.js` w/ "Recording discarded" + "Already
> recording" · frozen PYZ carries `is_repetition_loop` (src.live + applied in
> src.server). Branch pushed through `8d85ed8`; master untouched. NEXT: user
> smoke-test on 0.3.43 (silent recording auto-discards with amber notice ·
> captions single · no rep-loop spam — first build with the gate live).
> **2026-07-16 (~4:30pm) — 🎯 LAUNCH QUESTION OPEN → ✅ DECIDED (~7:50pm): GO
> on the funnel launch.** Claude's rec accepted: waitlist + private beta now,
> public Show-HN held on the notarization gate. Plan: buy lagharilabs.com →
> main site (separate `lagharilabs-website` repo; NOT yet git) on Cloudflare
> Pages with the Adversaria landing at **/adversaria** + an Adversaria
> PROJECTS card; first-party Worker+D1 waitlist (rec over Formspree's 50/mo
> cap); Email Routing hello@ → Gmail; cookieless analytics. **WAITING ON 3
> USER-ONLY ITEMS:** Cloudflare account + domain purchase · API token
> (Pages/Workers/D1/DNS/Email scopes) for Claude · email-forward target +
> backend choice. Then Claude wires the whole stack same-day (stunt-
> delegated) and marketing execution starts. Details in HANDOFF.md.
> **→ ✅ WIRED & LIVE (~8:35pm): https://lagharilabs.com is UP.** Main site +
> `/adversaria` landing + first-party `/api/waitlist` (Pages Function → D1,
> no IP/UA stored) + Adversaria project card + og.png + DNS + Email Routing
> rules — Playwright-verified end-to-end on the real domain (signup → D1
> row; honeypot + validation work; test rows cleaned, waitlist starts at 0).
> Site repo on private GitHub (`d52c49b`). Worker `393dab59` $2.95. **Email routing: records created DIRECTLY via DNS API**
> (wizard never resurfaced — new "Email Service" UI has no enable button;
> enable endpoints stay 10000 even with added scopes): 3 MX + SPF live in
> public DNS (dig-verified), hello@ + catch-all rules restored → verified
> Gmail. **✅ Email Routing ENABLED** via the old UI's "Add records
> and enable" (new UI has no such button). API-verified: MX+SPF+DKIM live,
> hello@ + catch-all rules → verified Gmail. Test sent — no bounce, log
> still 0; likely Google negative-DNS cache retrying (self-heals ≤1h).
> 🎉 **APPLE DEVELOPER ENROLLMENT DONE on hamza@lagharilabs.com**
> — Apple's email arrived via the new routing (mail path proven end-to-end)
> and enrollment completed. THE hard external launch gate is CLEARED. Next
> once membership activates: Developer ID cert → notarytool profile →
> notarized build → clean-machine test → gate #1 green → Show HN
> schedulable. (TCC grants reset once when the identity switches.) NEXT: announce waitlist ·
> clean-machine DMG check · first 10 testers · marketing execution.
> (1) **double-start race** — one record toggle started TWO capture sessions
> 145 ms apart (twin spools/asset rows; live captions duplicated every line;
> one session stranded `capturing` = the stuck-spool generator). Two layers:
> App.tsx's tray/hotkey `listen()` cleanup races the async registration under
> React StrictMode (dev double-mount leaks the first listeners → every toggle
> fires twice), AND `start_recording`'s already-recording guard is
> check-then-act (`commands.rs:153` checks, flag stored ~25 lines later) so
> near-simultaneous calls both pass. Final transcript was UNAFFECTED (only
> the stopped session transcribes). (2) **live rep-loop hallucination** —
> "pre pre pre …" spam in live captions (turbo repetition loop on noise;
> no_speech + filler gates don't catch repetition). Both logged in
> docs/TODO.md. ⚠️ Zombie spool `faeba394…` + asset row 19 still `capturing`
> under the running dev app — clean up after quitting it. Installed
> /Applications app was QUIT for the test (relaunch when done with dev).
> **2026-07-16 (late morning) — 🟣 RECORDING COMPANION built (stunt-delegated,
> UNCOMMITTED).** Option B "balanced" default + Option C "transcript-first" via
> new Settings → "Recording view" (`recording_view` config, read fresh at each
> recording start). Companion mode hides header/sidebar (slim chrome + record
> bar + Browse escape hatch); **auto-scroll bug fixed** (6-line cap removed,
> stick-to-bottom + "Jump to latest" pill). RecordingNotes.tsx deleted. Worker
> `78cf65ec` $4.83, zero review fixes; tsc ✓ · cargo ✓ · vitest 13 ✓. The
> user's broken-looking screenshot was mid-build stale HMR — dev stack
> restarted clean after review; awaiting visual verdict + commit word.
> ⚠️ NEW: 3 orphaned recording spools loop-failing recovery ("Untranscribed
> recording · Queued" rows + `[recovery]` manifest errors in dev logs) —
> cleanup decision needed. NEXT: user verdict → commit → re-freeze · spool
> cleanup.
> **Also: 🔴→✅ live "Thank you / Thanks for watching" fillers GATED.** Saved
> instances = the system-track bug (already fixed, pending freeze; DB-verified
> all on `Them:`). Live instances = no confidence filter in `/live_feed` →
> added `drop_no_speech` on the live transcriber (no_speech_prob > 0.6) + a
> canonical-filler blocklist (live-preview only; finals untouched — a real
> spoken "thank you" still stores). pytest 266 ✓.
> **2026-07-16 (10:25) — 🚢 v0.3.42 SHIPPING (user: "commit it all and
> re-freeze").** Committed: `019f807` feat(ui) companion view · `784aa5f`
> fix(live) filler gates · `13b3986` chore(release) 0.3.42 bump + CHANGELOG
> (NOT pushed). One build carries: working ⌘⇧M/⌘⇧N hotkeys · system-track
> vocab-echo gate · live filler gates · companion view + auto-scroll fix.
> ✅ Stuck-recording cleanup DONE: 6 orphaned `recording_assets` rows + 6 dead
> spool dirs deleted (DB backup `meetings.db.bak-pre-spool-cleanup-*`); the
> `[recovery]` retry-spam source is gone. 🔵 Follow-up found: the app's
> `delete_meeting` doesn't clean its `recording_assets` row (meeting 144's
> asset was orphaned by a manual delete) — small fix, backlog. Signed freeze
> (NotchyPrompter Dev) RUNNING → log `/tmp/adversaria-build-0716b.log`
> ✅ **v0.3.42 SHIPPED, INSTALLED & VERIFIED (10:55):** DMG built 10:37
> (785 MB) · installed to /Applications · Info.plist **0.3.42** · Authority=
> NotchyPrompter Dev, `codesign --verify --deep --strict` valid · sidecar
> /health ok (:58867, large-v3, ollama up) · frozen sidecar bytecode carries
> `is_filler_hallucination` + `drop_no_speech_raw_segments` +
> `drop_unvoiced_segments` (PYZ inspected) · binary embeds
> `index-xCkE7fga.js`/`index-CFmx8VMA.css` w/ `recording_view` +
> `companion-mode`. Env cleaned during verify: 3 stale DEBUG sidecars + a
> stray debug-bundle app instance killed, 2 stale DMG mounts ejected (gotcha:
> `open -a` can resolve to a debug bundle/mounted DMG — launch
> `/Applications/Adversaria.app` explicitly and pgrep by /Applications path).
> NEXT: user smoke-test on 0.3.42 — ⌘⇧M/⌘⇧N hotkeys · companion view (+ the
> Transcript-first setting) · live captions without "thank you" fillers ·
> silent recording stays empty. Then: push on the user's word.
> **2026-07-16 (mid-morning) — ✅ ⌘⇧M ROOT-CAUSED & FIXED (dev-verified, uncommitted)
> + 🔴 new vocab-echo bug.** The hotkey never fired in ANY build: `tray.rs` registered
> twice (`register()` then `on_shortcut()`, which registers again) → macOS rejects the
> same-process duplicate (`eventHotKeyExistsErr`) → the handler was silently never
> attached (`let _ =` swallowed the error). NOT a conflict/permissions — a Carbon
> experiment proved cross-process duplicates return `noErr`, so no error was ever
> possible. Fixed in `tray.rs`: `on_shortcut()` only + gate on key-down (ungated it
> fires on down AND up = double-toggle). cargo ✓; **VERIFIED in `tauri dev`** — ⌘⇧M
> from the background starts/stops real captures (user's own presses worked too).
> ⚠️ Installed v0.3.41 still has the dead hotkey → fix rides the next freeze.
> **✅ vocab-echo bug (user report) FIXED same session:** a silent recording
> transcribed the custom vocabulary ("Tatweer OS, Echelon, Tatweer" = Whisper
> `initial_prompt` echo on silence — it even contaminated the head of real
> meeting 134); the system track lacked the v0.3.41 mic VAD gate → gate now
> generic (`drop_unvoiced_segments`) + applied to BOTH tracks in both dual
> paths; +2 wiring tests, pytest 261 ✓. Junk test meetings 136-138 deleted
> (DB backup kept). Both fixes COMMITTED to `handtest-hardening` (`4a0f023`
> tray · `16de4fb` transcriber+tests · `df74e74` docs; NOT pushed); both are in
> code only until the next re-freeze — the installed v0.3.41 still has the dead
> hotkey + ungated system track, and even `tauri dev` runs the FROZEN sidecar,
> so the vocab fix isn't live anywhere yet. NEXT: re-freeze (batch with layout
> work?) · live-transcript auto-scroll · Option B recording view.
> **2026-07-16 (morning) — ✅ WORKING DMG built + 🎯 layout decision.** DMG
> `Adversaria_aarch64.dmg` (786 MB) signed NotchyPrompter Dev + JIT fix → the ML
> sidecar runs AND TCC/keychain persist = the first build to actually test
> capture→recovery / hand to testers (un-notarized → right-click Open). Fixed a
> build-dmg.sh regression (`b9be659`: `spctl --assess` under `set -e` aborted every
> self-signed build). **Layout: user chose Option B "even split"** for the
> recording-companion view (~50% live transcript / ~50% notes + collapsed header +
> auto-scroll). Mockups artifact shared. Note: the "old white app" the user saw
> was an **ancient v0.1.0 `/Applications` install** (Jun 20), not a bug — new build
> is v0.3.41 dark, auto-install was off; install it to see the dark design. All
> baton docs (HANDOFF/STATUS/TODO/HANDTEST_FINDINGS) synced + committed on
> `handtest-hardening`. ✅ **v0.3.41 dark build now installed** to /Applications
> (NotchyPrompter Dev). Open: 🔴 **⌘⇧M record hotkey doesn't fire** (registration
> fails at startup, `tray.rs:100`; tray menu works meanwhile — now diagnosable on
> the signed build). NEXT: diagnose the hotkey · fix live-transcript auto-scroll ·
> build the balanced recording view. See HANDOFF.
> **2026-07-16 (loop) — 🔨 (committed 12b9607) small UX fix + loop paused.** Onboarding
> model step now surfaces detected RAM + the recommendation (`Welcome.tsx`, tsc ✓,
> runtime-unverified — signing wall). Last cleanly-autonomous item; the rest (back
> button, permissions Grant+✓, Whisper surfacing, model-detection) need user
> direction or app-verification. Pending the user's commit word.
> **2026-07-16 (loop) — ✅ MLX *shipped-profile* bake-off DONE.** Tested the actual
> 4B/9B/27B via mlx_lm.server + the app's real summarizer. total_bad: **4B=0 ·
> 9B=1 · 27B=1**. Verdict: the shipped **4B is SAFE** (zero fabrication ever; just
> lower recall) → Codex's 4B is defensible, not risky. The shipped **27B is NOT
> clearly better than a 9B** (fabricated on the hard case, same score, 3× the RAM)
> → the ≥24 GB premium looks weak. All profiles sit in one band on this synthetic
> set — a real **private-corpus baseline** is what actually separates them; don't
> over-restructure tiers on synthetic evidence. See HANDTEST_FINDINGS.md § v3.
> **2026-07-16 (bake-off v2) — 🔵 2nd harder transcript TEMPERS "9b is best".**
> Aggregate bad events over 2 transcripts: 35b=1 · 9b=1 · 8b=1 · llama3=2 — the
> qwen 35B/9B/8B are closely matched on hard content; only llama3 clearly worse.
> 9B still holds as the 16 GB pick (competitive with 35B at ¼ size, zero
> fabrication) — tier call stands, "dominant" framing doesn't. New: most models
> mishandle explicit DEFERRALS ("we are NOT deciding X today") → a `general.md`
> prompt-hardening opportunity that helps every tier. See HANDTEST_FINDINGS.md.
> **2026-07-15 (research) — 🔵 Fluid Voice "blazing fast" = NVIDIA Parakeet,
> not a model called "Blazing Fast".** FluidVoice runs Parakeet TDT/Flash (+
> Nemotron 3.5 / Whisper / Cohere / Apple Speech); Parakeet ≈ 10× faster than
> Whisper large-v3-turbo for English. Catch: Parakeet v3 ≈ 25 mostly-European
> languages, Arabic excluded — so at most a faster **English live-caption**
> lane, keeping Whisper large-v3 for Arabic + final. `parakeet-mlx` exists.
> Not built; awaiting the user's word. See HANDOFF.
> **2026-07-15 (hand-test + audit) — 🔍 Codex release-hardening AUDITED,
> hand-tested on macOS, 3 real bugs fixed, whole pile committed to branch
> `handtest-hardening` (master untouched).** Docs verified accurate (all gates
> re-run green; DMG smoke reproduced within 0.1%). Found + fixed: 🔴 **JIT
> entitlements** — the bundled ML sidecar is SIGKILL'd in EVERY packaged build
> (llvmlite JIT under hardened runtime) → "Local ML Service: Offline"; fix =
> `+allow-jit` in `entitlements.plist` (verified). 🔴 **keychain-denial → app
> crash** — `lib.rs` now handles it gracefully. 🟠 **hotkey label** — ⌘⇧M on
> macOS (was "Ctrl+Shift+M"). **Signing wall:** capture/recovery + real
> inference can't be tested without Developer-ID (TCC + keychain both bind to
> the code signature). **Bake-off:** qwen3.5:9b wins — perfect scores, 6.6 GB
> fits 16 GB Macs, zero fabrication across all models → evidence for a missing
> 16 GB tier (4B/27B were never quality-tested). ✅ COMMITTED & PUSHED to
> `handtest-hardening` (`646b6ba`) EXCEPT 2 CI workflow files (token lacks
> `workflow` scope). Findings + fix plan:
> [docs/HANDTEST_FINDINGS.md](./docs/HANDTEST_FINDINGS.md). NEXT: grant workflow
> scope → push workflows · wire the 9B 16 GB tier · broaden the bake-off.**
> **2026-07-15 — release-hardening implementation pass complete; acceptance is
> still open.** Encrypted crash-safe capture, evaluation harness, versioned
> onboarding/registration, managed Rapid-MLX, security/UI gates, and release
> automation are implemented and locally green. Full ad-hoc packaging smoke
> passed; the sealed macOS E2E app also passed twice consecutively with clean
> teardown. The public beta still requires real 60-minute/forced-quit capture,
> private-corpus baseline, production Formspree endpoint, clean 16/32 GB Macs,
> remote CI, Developer ID/notarization, and updater acceptance. Current ledger:
> [docs/CODEX_TODO.md](./docs/CODEX_TODO.md); handoff:
> [docs/CODEX_HANDOFF.md](./docs/CODEX_HANDOFF.md).
> **2026-07-14 (mic-hallucination) — ✅ v0.3.41 SHIPPED & VERIFIED — Insights
> no longer counts silence as you talking.** A meeting the user barely spoke in
> showed 35%/24:44 + 79 interruptions: the near-silent mic + MLX-Whisper-has-no-VAD
> made Whisper hallucinate ("thanks for watching") and label it as the user. Fix:
> VAD-gate the mic track before transcription (drop_unvoiced_mic_segments, both
> transcribe_dual paths). pytest 250; frozen build verified (silent mic → no "Me"
> turn). Applies to NEW recordings. UNCOMMITTED & NOT PUSHED.**
> **2026-07-14 (live-latency) — ✅ v0.3.40 SHIPPED & USER-CONFIRMED — live
> transcript fast again.** Was lagging 20–40s (cause: VAD 30s force-cut + heavy
> shared model, not memory/speed). Fix: dedicated fast live model
> (whisper-large-v3-turbo-q4, warmed at startup) + VAD tuning (force-cut 30→8s,
> silence 2s→0.9s) + poll 2s→1s; final transcript stays large-v3. Measured
> 0.71s/utterance; user: "worked well!!". pytest 244 · cargo ✓ · tsc ✓.
> ✅ COMMITTED & PUSHED (a339262+fdffc26+7309366; landing d8e8a1e) — master
> == origin.**
> **2026-07-14 (launch prep) — 🚀 FIRST LAUNCH = soft-public waitlist page.**
> Notarization still blocked → no public app download yet, so launch = a
> landing page collecting waitlist emails. Built `landing/index.html`
> (self-contained; app identity: dark glass + azure + serif; Formspree form,
> placeholder id) + `landing/DEPLOY.md` runbook + preview Artifact. Target
> domain: lagharilabs.com (buying). NEXT (user): Formspree id → buy domain →
> deploy (Cloudflare Pages) → og.png. Notarization = gate for the real app
> launch. UNCOMMITTED.**
> **2026-07-14 (later) — 🔵 Ask "couldn't reach the local model" diagnosed:
> on macOS chat/summarize use the MLX server on :8000 (NOT Ollama; Ollama =
> embeddings only). Config model `qwen3.6-35b` was correct — a wrong colon
> "fix" was reverted. Real cause = :8000 lazy-loads the 21 GB model (cold
> request hangs 15 s+, warm ~1 s). Verified working; retry Ask. Optional
> hardening (real error / retry / warm-up) awaiting word. See LESSONS_LEARNED.**
> **2026-07-14 — 🔴→✅ LIVE TRANSCRIPT captions the MIC now, not just system
> audio.** Root cause: the live loop only snapshotted system audio, so YouTube
> worked but the user's own speech never showed. Fix: snapshot both streams and
> feed `/live_feed` as separate VAD sessions ("them"=system, "me"=mic). pytest
> 244 (+2) · cargo ✓ · tsc ✓. User-verified in dev → **✅ v0.3.39 SHIPPED &
> VERIFIED INSTALLED** (Info.plist 0.3.39 · NotchyPrompter Dev · /health ok
> :52599 · frozen `/live_feed` schema exposes `source` = mic fix in the freeze).
> **✅ COMMITTED & PUSHED** (`ee6f210`+`81646c6` → origin/master; master ==
> origin). `SummaryView.tsx` (per-line RTL) now committed too (`5723797`) —
> git matches the shipped binary. **SESSION COMPLETE — master == origin;
> sole loose end is uncommitted `docs/TODO.md` (prior-session notes).**
> **2026-07-11 — 🔴→🔨 "Presented by Hamza" root-caused (49/99 transcript
> lines are mic-bleed under the viewer's name); TWO prompt-rule fixes failed
> live /summarize re-tests → deterministic code fix in flight: youtube
> summaries relabel viewer lines to "Viewer mic (not the presenter)" so the
> name never reaches the LLM (`viewer_label` through Rust→/summarize).
> ✅ code fix VERIFIED on the real transcript (zero Hamza mentions;
> pytest 242 · cargo 105 · tsc ✓) — ✅ v0.3.38 SHIPPED & VERIFIED
> (Info.plist 0.3.38 · NotchyPrompter Dev · /health ok · `viewer_label`
> in the frozen schema · hardened rule bundled; NOT pushed). User:
> regenerate meeting 114 to see it clean.**
> **🎯 Accuracy deep-dive DELIVERED** (sweep + ranked plan + prep design:
> <https://claude.ai/code/artifact/1c9b7964-1a5b-424f-a419-1671169ca478>;
> condensed in TODO.md). Sprint 1 proposed: eval harness → bleed-strip v2 →
> auto-roster → truncation warning. Awaiting sprint greenlight.
> **🔴 NEW discovery: recording is RAM-only until stop — a mid-meeting
> crash loses ALL audio (no recovery exists). Fix pair proposed
> (crash-safe capture + transcript-level resume); design in TODO.md;
> awaiting build word.**
> **2026-07-10 (late morning) — 🟢 COACHING METRICS GREENLIT; in motion:**
> ✅ youtube.md viewer≠presenter rule FIXED ("Presented by Hamza" bug) ·
> ✅ Build A DONE (Python keeps segment end-times; /transcribe returns timed
> turns; flat text byte-identical; pytest 227 ✓) · ✅ Meetily research
> LANDED (verdict in TODO.md: their timestamps are coarser than ours; lifts
> executed: NEW `detailed.md` template + injection guard in all 7 templates)
> · ✅ Build B DONE (Rust timed-turn storage + `compute_meeting_stats` +
> IPC; cargo 105) · ✅ Build C DONE (Insights tab: talk-time bars, pace vs
> 130–175 target, fillers vs 4%, interruptions, longest monologue;
> [MM:SS] transcript prefixes; tsc ✓) · ✅ **v0.3.36 SHIPPED, VERIFIED &
> PUSHED**: Info.plist **0.3.36** · NotchyPrompter Dev · /health ok
> (:64108) · frozen `/transcribe` exposes `turns` · `detailed` in
> `/templates` · binary embeds `index-DW6YS2rg.js` (insights +
> `get_meeting_stats`). ⚠️ Precise timing starts with NEW recordings
> (old meetings → word-based shares). · Build D (self-coaching +
> email-draft prompts) queued. · **✅ v0.3.37 SHIPPED & VERIFIED (polish):**
> sidebar date dead-gap fixed (⋯ now overlays/swaps with the date on
> hover) + Insights column centered; CSS-only; commits bcf0c54+5bd4811+verified-docs, NOT pushed — push on the user's word.
> **2026-07-10 (morning) — 🟣 THE 4 QUEUED PRODUCT ASKS EXECUTED (stunt
> delegation, all UNCOMMITTED).** ✅ Category→template auto-routing +
> bidirectional `interview.md` BUILT & VERIFIED (pytest 207 · cargo 95 ·
> tsc ✓; `auto_template` flag — manual template picks never overridden;
> fail-open; needs re-freeze to ship; →v0.3.32 on the user's word).
> ✅ Sidebar declutter BUILT & VERIFIED (user picked **C — pins +
> auto-archive**; tsc ✓ · cargo 95 · pytest 207): zoned resting view
> (Pinned / Last-N-days / collapsible Archive), selected-meeting highlight
> fix, clear-ALL-filters fix (+ search ×), `archive_after_days` Settings
> knob (Never/14/30/60/90), attendees in the search haystack.
> Frontend+Rust → live-testable in `tauri dev` NOW; re-freeze to ship.
> ✅ Find-by-person BUILT (user picked sample 1 — @person search chips:
> `@` in search → attendee autocomplete w/ counts → AND-composing chips).
> ✅ **v0.3.32 SHIPPED & VERIFIED** (user: "commit and re-freeze"):
> committed `247f7b7` + `c53e0ac` + `cce7f80` (NOT pushed), signed freeze
> installed + relaunched. Verified: Info.plist 0.3.32 · Authority=
> NotchyPrompter Dev · sidecar /health ok (large-v3, ollama up) ·
> interview.md bundled + in /templates · frozen /summarize schema has
> `auto_template` · binary embeds `index-Be7WG3A5.js` (contains
> mention-popup + archive-toggle). README feature list + config table
> refreshed same session.
> **v0.3.33 (same morning, second smoke-test round) — 🚢 SHIPPING: sidebar
> v2 + scrollable @dropdown.** Compact one-line rows (dot·title·time) with
> hover peek (date·duration·snippet·editable tags); date bins Pinned/Today/
> Yesterday/This week/Earlier this month/month/Archive (user rejected the
> one "Last 30 days" bin); **MANUAL archive** (new `archived` DB column,
> ⋯-menu Archive/Unarchive, archiving unpins) — answers "how do I
> archive?"; @person dropdown scrollable (cap removed + keyboard
> scroll-into-view). Verified pre-ship: tsc ✓ · cargo 95 · pytest 207.
> **✅ SHIPPED & VERIFIED:** committed `e886e97` + `566bdf9` (NOT pushed),
> signed freeze installed + relaunched — Info.plist **0.3.33** ·
> Authority=NotchyPrompter Dev · sidecar /health ok (:49781) · binary
> embeds `index-Df0VDziX.js` (contains mrow-peek + set_meeting_archived) ·
> clean relaunch = the `archived` migration ran on the live DB. README
> sidebar bullet updated to v2. **v0.3.34 SHIPPING (tsc ✓ · cargo 95 ·
> pytest 207): `sidebar_view` Settings toggle (Compact rows default /
> classic Full cards — same bins/archive either way, restart-to-apply) +
> @person chips moved INSIDE the search bar (new `.search-bar` wrapper
> carries the chrome + focus ring; icon static, chips wrap). Committed
> `14e57b4` + `de65a5c` (NOT pushed). ✅ SHIPPED & VERIFIED: signed
> freeze installed + relaunched — Info.plist **0.3.34** · Authority=
> NotchyPrompter Dev · sidecar /health ok (:56446) · binary embeds
> `index-gyC_Z2fY.js` (contains sidebar_view + search-bar).**
> **✅ ALL PUSHED: `c4aece1..12a17be` → origin/master (v0.3.32/33/34).**
> **✅ v0.3.35 SHIPPED & VERIFIED:** sidebar-view + archive-window
> settings apply on returning to Meetings (was restart-only — user hit
> it). Committed `abf7882` + `d34e64b` + `1f9dad1`, ALL PUSHED
> (`12a17be..1f9dad1` → origin/master — master == origin, the full
> 2026-07-10 run v0.3.32→v0.3.35 is published);
> freeze installed + relaunched: Info.plist **0.3.35** ·
> NotchyPrompter Dev · /health ok · binary embeds `index-BFbSQGr0.js`.
> ✅ read.ai research done → verdict in TODO.md § "Next up" #4 (build the
> speech-based coaching half — talk-time/pace/fillers/interruptions are
> pure arithmetic on existing diarized segments; skip the facial layer,
> it's camera+bot-based and thesis-incompatible). Awaiting greenlights.
> Details: [HANDOFF.md](./HANDOFF.md) + [docs/TODO.md](./docs/TODO.md).
> **2026-07-10 — 🟣 LAUNCH VIDEO **v4** — upbeat viral re-cut, THE current
> final (`marketing/launch-video-v4/renders/adversaria-launch-v4-final.mp4`,
> 86.25 s · 46 bars @128 BPM · beat-locked whip-pan/white-flash cuts · azure
> progress bar · filtered-intro→silence→drop music · ElevenLabs v3 VO
> regenerated with NO silence-trim (v3's chopped consonants root-fixed) +
> "Add-ver-sarr-ee-ah" respelling; softer modern SFX). v3 (108 s dramatic
> cut) kept as history. Review fixes: music drop re-timed to land exactly on
> the splash bar (9.375 s). Reproducible: `audio/build-audio-v3.sh`.
> UNCOMMITTED. Also tonight: laghari-vault second-brain upgraded (ADRs,
> archive, inbox, weekly-review op; graph 124→128) and 4 user-queued product
> asks specced in TODO.md § "Next up" (sidebar declutter · YouTube
> auto-template · category→template routing + bidirectional interview
> template · read.ai research).**
> **2026-07-09 (late) — ✅ v0.3.31 SHIPPED, VERIFIED & PUSHED (Ask source
> citations). Committed `836565d`, signed freeze installed + relaunched;
> Info.plist 0.3.31 · NotchyPrompter Dev · sidecar healthy · citation prompt
> grep-confirmed in the installed binary. All 2026-07-09 commits pushed:
> `6cbb31c..dd8f33d` → origin/master.** "Who likes black coffee?" showed 5 Reference Notes for a
> 1-meeting answer — sources were the retrieval candidates, not citations.
> Now the LLM cites `SOURCES: n` per numbered context section; Rust strips
> the line + filters (fail-open, dedup). Rust-only (`commands.rs`); cargo 95 ·
> tsc ✓. All commits through `836565d` unpushed.
> **2026-07-09 (evening) — ✅ v0.3.30 SHIPPED & VERIFIED (hybrid Ask RAG +
> chat fixes).** Committed `d363aeb` (22 files) on the user's "commit and
> re-freeze", signed freeze installed + relaunched. Verified: Info.plist
> 0.3.30 · NotchyPrompter Dev authority · sidecar /health ok · frozen /embed
> live (bge-m3, 1024-dim) · startup backfill embedded the real corpus
> (ollama ps showed bge-m3 hot right after relaunch). `a77396d`+`d363aeb`
> NOT pushed yet — push on the user's word.
> **2026-07-09 (pm) — Ask-tab HYBRID RAG BUILT in dev.** Keyword-only Ask →
> **FTS5 + bge-m3 chunk vectors + attendee/tag
> graph anchors, RRF-fused**; detail answers now ground in the MATCHED chunks,
> not the transcript's first 4000 chars. New: Python `POST /embed` (Ollama
> bge-m3, pulled on this box) · `src-tauri/src/embeddings.rs` self-healing
> chunk index (SQLCipher `meeting_chunks`) · `retrieve_meetings_hybrid`.
> Embed layer down → exact old behavior. Built per the user's directive via
> stunt-worker delegation (Claude spec'd + reviewed; 3 tasks + 1 review round,
> ~$11.5 worker cost, zero Anthropic credits). cargo 81 · pytest 187 · tsc ✓ ·
> live /embed ✓ (EN↔AR cosine 0.879). Next: dev smoke → commit (user OK) →
> re-freeze. Launch-video SOURCE committed (`a77396d`, unpushed; renders
> gitignored). Details: [docs/HANDOFF.md](./docs/HANDOFF.md).
> **Same day (later) — chat-hang root-caused + Task D fixes (uncommitted).**
> "No answer" chats = Rapid-MLX aborting 2 concurrent 15k-token requests
> (upstream batch bug, log-verified), then our `/chat_stream` silently sent
> `[DONE]` on the token-less stream. Fixed: zero-token stream → auto-retry
> once → visible error; empty `chat()` raises; grounded prompts (chat + Ask)
> now allow transcript-grounded analysis/evaluation ("how did I do?" works —
> live-verified with a cited assessment). pytest 191 · cargo 82 · tsc ✓.
> ⚠️ Reaches the installed app only after a re-freeze.
> **2026-07-09 — OWN launch video built via HyperFrames, now v2 (source now in
> git `a77396d`; renders gitignored; delivered).**
> `marketing/launch-video/renders/adversaria-launch-v2.mp4` — 63s · 1920×1080 · 60fps ·
> silent · 12.7 MB. HeyGen HyperFrames (animated HTML → local MP4); one offline
> `index.html` (vendored GSAP + local Instrument Serif, no CDN). 11 scenes, theme
> **"Sovereign First"**, no competitor names, UI recreated faithfully in HTML (the
> other agent's `video/` uses AI-generated fake screenshots — don't reuse). v2 added
> bigger fonts + Import-audio + MCP scenes + clearer Share. **Render gotcha (see
> HANDOFF):** pin `hyperframes@0.7.42` + `browser clear` if the managed Chrome
> download half-completes. OPEN: add music (silent — licensing) + git-track decision.
> **2026-07-08 (later) — doc housekeeping (`ce0888a`+`6cbb31c`, pushed to origin).**
> Committed the two DEEP_DIVE companion docs (written 2026-07-02) — CLAUDE.md's doc
> table referenced them but they were never in git. Gitignored the `/llm-council`
> artifact pattern; the stale 2026-06-26 roast files stay on disk, untracked+ignored.
> Next big initiative still awaiting user's pick: Ask-tab RAG upgrade (hybrid,
> researched) vs Windows packaging (runbook ready).
> **2026-07-06→08 — v0.3.24 → v0.3.29 shipped, committed + signed-frozen +
> pushed.** v0.3.29 slide-export intro three-line branding (Adversaria / A Laghari
> Labs Product / Nothing leaves your machine).
> v0.3.24 LLM category routing + Ask fixes (topic search, background
> answers) · v0.3.25 first-class notes (Structure with AI, templates, Cmd/⌃+Shift+N) ·
> v0.3.26/27 slide intro matches app splash (Instrument Serif azure) + Structure-note
> fix · **v0.3.28 wider Todos/Ask/Weekly layouts + configurable date format** (British
> dmy / long / iso, Settings picker). **Decisions:** keep large-v3 default (turbo
> Arabic rougher); Ask-tab RAG upgrade researched → recommend hybrid vector+graph-assisted,
> NOT GraphRAG (awaiting user's build decision). Tests green (Rust 55 · pytest 178 · tsc).
> **Windows app: build runbook WRITTEN & ready** (docs/HANDOFF.md "Building the Windows
> app") — code already cross-platform; can't build from Mac (PyInstaller no cross-compile),
> use GitHub Actions `windows-latest` or a Win11 box. Awaiting user's go + platform choice.
> 🔴 known port item: the Whisper model picker is MLX-only, needs a Windows default.
> **Earlier 2026-07-06 — three ships, all VERIFIED installed + pushed (`d15eb89`):**
> **v0.3.20** (From-Your-Notes summary section, per-meeting source links,
> service-responsiveness batch) · **v0.3.21** (VAD-gated live captions — Silero
> segments utterances, each transcribed ONCE; the Meetily "#1 steal", zero new
> deps) · **v0.3.22** (transcription-time category hint — video classification
> can't regress as transcripts get cleaner; + the full small-audit-bug sweep:
> empty-capture stop error, backslash crash, config-write race, import tempfile
> leak, Ask turn drop, UTC import sort, chat unmount, placeholder checkboxes).
> **The 2026-07-03 audit is fully closed** — remaining accepted items in
> TODO.md. 174 pytest · 49 cargo · tsc. Meetily research verdicts in TODO.md
> (captions adopted; keep our diarization; Parakeet spike later). Next candidates:
> second-brain graph export (format sign-off pending), voice-enrollment named
> speakers, Parakeet engine spike.
> **2026-07-04 (later) — partial-mic-bleed fix SHIPPED (v0.3.18, `4793fc3`, signed
> re-freeze, verified installed + healthy):** watched videos in the "mic hears a
> fraction of the playback" band classified "meeting" and their words were
> attributed to the user — added a containment bleed test (≥0.8, corpus-calibrated:
> videos ≥0.83 vs real meetings ≤0.75) in `classify_category` + `strip_mic_bleed()`
> dropping near-verbatim mic copies before merging. 157 pytest. Meeting #90's
> stored transcript deduped (19→1 turns) + retagged YouTube (DB backup kept);
> user to Regenerate Notes.
> **2026-07-04 — diarization anti-over-count bundle SHIPPED (v0.3.17, signed
> re-freeze):** A1 diarize-only-transcribed-spans + A2 embedding-similarity
> re-merge + A3 media/playback gate (reuses `classify_category`) + A4 tighter
> caps (5 speakers / 12 s / 0.5 s), plus a retroactive NoteViewer **"Merge
> speakers into 'Them'"** button (user-validated live on the 14-speaker demo
> meeting before shipping). 148 pytest · 49 cargo · tsc · cargo check green.
> Details: HANDOFF "Last session".
> **v0.3.14 COMMITTED 2026-07-02
> (`c43b774` diarization fixes · `222e76c` prompt grounding · `dc45895` the feature set:
> Export/Import bundles + backup-all, Knowledge Graph "Graph" tab with floaty infinite
> d3-force physics + declutter, recording-bubble elapsed timer, Weekly/To-dos declutter)
> — re-frozen + **VERIFIED live in `/Applications/Adversaria.app` the same morning**
> (Info.plist 0.3.14, `Authority=NotchyPrompter Dev`, sidecar `/health` ok — first
> installed build carrying the Graph tab, Export/Import, and the Python fixes).
> **Follow-up (same day, `61ec4c5` + second verified re-freeze): graph physics calmed** —
> user reported "too fluttery"; tuned alpha/alphaDecay/velocityDecay (measured post-drag
> wobble 15 px/s → 0 by t=3 s), re-frozen, and chain-verified in the installed bundle
> (`index-FvHMU_Cd.js` contains the constants; binary embeds that exact asset).**
> **2026-07-03: flutter ROOT-CAUSED + properly fixed → v0.3.15 (`fd2ab16`, local-only,
> not pushed; staging DMG build kicked off the same night, auto-installs)** — the tuning
> was symptomatic; real causes in the cytoscape-d3-force wrapper (alphaTarget never reset
> to 0 after drag + random re-layout on every tab visit). `GraphView.tsx` now zeroes
> alphaTarget on release and persists node positions across visits (tsc ✓; feel not yet
> user-confirmed). **New env discipline:** dev = `tauri dev`, staging = installed app;
> re-freeze only when happy in dev; NEVER start `tauri dev` during a re-freeze (it wipes
> the sidecar dist the dev build.rs needs). Same session: **full-codebase bug audit** → ranked open
> findings at the top of [docs/TODO.md](./docs/TODO.md) (top 3: Python service blocks
> its event loop during transcription; stale action-item checkboxes after Regenerate;
> SQLite has no busy_timeout/WAL); **diarization over-count diagnosed** (demo/TTS audio
> is OOD for campplus; quick-win bundle A1–A4 specced in HANDOFF); **graph→second-brain
> export designed** (OKF/markdown+wikilinks to a local vault folder — awaiting format
> sign-off). Highlights of the 2026-07-02 work: the
> Graph filters generic Speaker-N/Me/Them nodes (they also falsely LINKED meetings via
> shared-attendee edges), merges owner↔person, drops single-use tags, and runs an
> Obsidian-style infinite drag-tug simulation; 🔴 `classify_category` no longer counts
> `Speaker N:` as the local user (YouTube-video→"brainstorm" bug) and the diarizer merges
> phantom micro-clusters (Speaker 13/14 in a 2-person call). tsc + cargo 46 + pytest 135
> green. The whole
> Ask system (intent routing → to-dos/recap/overview/detail + conversational guardrails
> + persistence + provenance badge + spoken-to-dos→action_items prompt fix) is shipped
> and (spoken-to-dos) user-verified. **GTM is now decided (2026-06-28):** launch
> **free-only**, paid wedge = **regulated client-facing solos**, lead with "nothing
> leaves your machine", open-source the MCP server — date soft, gated on **four hard
> launch gates** ([docs/TODO.md](./docs/TODO.md) "Launch gates"). Full state:
> [docs/HANDOFF.md](./docs/HANDOFF.md); decision: [docs/STRATEGY.md](./docs/STRATEGY.md) §2026-06-28.

## Built
_Shipped and working (verified end-to-end on the Windows dev box; macOS port builds + transcribes but not yet run in a live call)._
- **Core loop:** record → on-device GPU transcription (faster-whisper CUDA / MLX) → local-LLM summary (Ollama `qwen3.6:35b-a3b` / Rapid-MLX) → SQLite → UI. Audio deleted after transcription.
- **Dual capture** (system "Them" + mic "Me"), speaker-labeled transcript.
- **Summary UI cards** (collapsible, action-item checkboxes), Copy + **Export ▾ menu: Export as Slide (HTML) / Markdown**. The slide (`src/lib/exportDocument.ts` → `buildSlideHtml`) is a self-contained dark "Meeting Minutes" presentation on a **fixed 1280×720 stage** — ADVERSARIA reveal intro, multi-column accent cards (Key Topics/Decisions/Action Items/Follow-ups), Arabic-RTL aware. Scales to fit the viewport (**single page, no scroll**) and maps to `@page{size:1280px 720px}` so a browser **Save-as-PDF = one page**. ⚠️ In-app "Save as PDF" was removed — Tauri no-ops `window.print()` on macOS.
- **🕸️ Meeting Knowledge Graph "Graph" tab (2026-07-01, implemented + verified green, live in dev, NOT committed):** a new sidebar **Graph** tab renders meetings ↔ people (attendees) ↔ tags ↔ action-owners as an interactive **cytoscape.js** graph (self-hosted, no CDN), built from existing SQLite — **zero LLM, zero network**. Click a meeting node → opens it. Rust `get_meeting_graph` (+ pure `build_graph` helper, dangling-edge-safe, 500-meeting cap) + `GraphView.tsx`. Delegated to the stunt worker ($1.71, zero Anthropic credits), 1 round; 46 cargo + tsc green; live-confirmed in `tauri dev`. This is Adversaria's *own* on-device meeting graph; a future **"Export to Obsidian vault"** (Part 2) will push meetings into the user's graphify second brain (`wiki/meetings/`) so they join the all-projects graph.
- **📤 Export / Import meeting bundles (2026-07-01, implemented + verified green, NOT committed):** per-meeting **`*.adversaria.json`** bundle (schema v1: transcript, `transcript_turns`, summary, attendees, tags, user_notes, action_items) exported from the **Export ▾** menu, re-imported under a fresh id via the sidebar **"Import meeting…"** button. Plus **Backup-all / Restore-all** (every meeting + action items + Ask history → one JSON) in a new Settings **"Data"** tab. Pure Rust + frontend (4 IPC cmds, `insert_bundle_meeting` federated re-insert); `language` omitted (not stored) and `ask_conversation` export-only (stale source ids). Delegated to the stunt worker ($2.08, zero Anthropic credits), 1 round; 45 cargo + tsc + 126 pytest green. ⚠️ Testable in `tauri dev` (no Python changes); re-freeze only to ship to the installed app.
- **Arabic / multilingual** summaries with RTL rendering; per-meeting + default language picker.
- **Auto-detect meetings** (off by default) + floating record/dismiss card.
- **Re-summarize**, **Chat with a meeting** (grounded Q&A, persisted history), **My Notes** (verbatim notepad woven into summary), **live transcription preview**.
- **Name + custom-vocabulary personalization** (relabel `Me:`, bias Whisper spelling).
- **UX batch + Adversaria rebrand (2026-06-18):** chat markdown + persistent history, meetings search, colorful auto-detected session-type tags + click-pill rename/recolor, user-editable prompt templates, sidebar revamp, silence auto-stop (5-min prompt / 10-min hard stop), intro splash.
- All known 🔴 correctness bugs fixed (2026-06-16/17). 60 pytest + `cargo check` + `tsc` green.
- **🎙️ Recording UX → v0.3.2–v0.3.4 (2026-06-24):** floating bubble is now **draggable** (Rust `bubble_start_drag` focuses the unfocused bubble window then starts the native drag — macOS won't drag an unfocused window); the recording bars are a **live audio-reactive waveform** (`get_audio_level` RMS polled ~14 Hz, flatlines on silence) and the header timer counts real elapsed; **app version shown in Settings**; `build-dmg.sh` **auto-installs to /Applications**. All pushed + installed.
- **📅 Calendar UX → v0.3.5 (2026-06-24, user-confirmed working live):** the sidebar month calendar is now a true **meeting-count heatmap** — `DateHeatmap.tsx` emits `level-1..4` by count and `prototype.css` has four blue-opacity tiers (busiest day darkest, zero-meeting days the faint base), replacing the old binary has-meetings shade. And the **tag pills are date-scoped**: selecting a day narrows the pills to only that day's categories (`MeetingsList.tsx` builds pillars from the date-filtered subset). Committed to `master`.
- **🔐 Encryption-at-rest → v0.2.0 (2026-06-24):** SQLCipher (rusqlite `bundled-sqlcipher-vendored-openssl`), transparent 256-bit key in OS keychain, in-place plaintext→encrypted migration with backup + row-count verify; FTS5 intact. Rust core (Claude) + MCP read path (DeepSeek-drafted, Claude fixed a `sqlite3.Row`-on-sqlcipher3 `TypeError`) + docs (ADR-011 + LESSONS). 24 unit tests + real-DB migration (32 meetings/51 actions/10 chats preserved) verified. Shipped v0.2.0 (signed DMG); `feat/db-encryption` merged to master. ⚠️ First launch migrates the live DB (plaintext backup kept).
- **🗣️ Speaker diarization → v0.3.0 (2026-06-24):** remote participants split into "Speaker 1/2/…" (mic stays "Me") via on-device **sherpa-onnx** (offline, no HF gating, ~34 MB models, ~17× realtime CPU). Diarizes only the system channel; per-segment time-overlap labels; Settings toggle (default on); best-effort fallback to "Them". 110 pytest + cargo + tsc green; **frozen-sidecar load validated**. ADR-012. **v0.3.1: clustering threshold tuned 0.5→0.7** after a 2-person call over-segmented into "Speaker 1/2/3" (0.7 is the max that still separates distinct speakers on the reference clip; new recordings only).
- **💬 Streaming chat → v0.2.1 (2026-06-24):** "Chat with Meeting" streams token-by-token (Python `/chat_stream` SSE → Rust `http_client.chat_stream` via `resp.chunk()`, multibyte-safe → Tauri `Channel` → live render in `MeetingChat`). Dual-backend (Ollama + OpenAI-compatible). Live-tested vs DeepSeek (19 chunks); 110 pytest + `cargo check` + `tsc` green. ⚠️ Needs DMG re-freeze to ship.
- **📦 MCP server is now standalone (2026-06-24):** mcp-server/ moved to ~/Documents/Documents/MyProjects/mcp-server/ (consumed by lagharilabs OS). The old copy in this repo was deleted. Standalone copy debugged: clean venv, pure-stdlib+mcp imports (no keyring/sqlcipher3), all 4 tools verified.
- **DeepSeek-delegated quick-wins → v0.1.3 (2026-06-23, pushed to origin):** an external review's findings are now a prioritized 16-item backlog in [docs/TODO.md](./docs/TODO.md). All 3 P0 quick-wins delegated to the DeepSeek v4-pro stunt worker (opencode), each reviewed + verified by Claude: ✅ removed the lorem-ipsum WeeklyView placeholder; ✅ friendly "AI model unreachable" message (`lib/errors.ts`) in Ask + Chat; ✅ BYOK "Test connection" button in Settings (`test_llm_connection` Rust cmd → provider `/models`). Signed `.dmg` rebuilt at v0.1.3. Next: P1 **DB encryption-at-rest** (the thesis-protecting gap the review missed), then streaming chat.
- **Ask-tab + meeting-toolbar UI fixes (2026-06-23, `v0.1.2`, committed — NOT pushed):** Ask Across Meetings now shows the asked question as a bubble above the answer and clears the input on submit (`AskAllView.tsx`); the meeting note toolbar no longer wraps tab labels / crushes the dropdowns + Regenerate button at narrow widths (`white-space: nowrap` + `flex-wrap` in `prototype.css`). Version 0.1.1 → 0.1.2; CHANGELOG updated; `tsc` green; signed release `.dmg` rebuilt.
- **Weekly Recap polish + action-item extraction hardening (2026-06-23, `v0.1.1`, committed `0f13717` — NOT pushed):** recap no longer renders meeting names as big centered bold blocks (new inline `.weekly-meeting-link`) and drops "None mentioned" placeholder bullets; broadened the action-item heading regex (Rust `storage.rs` + TS `summary.ts`, kept in sync) to match Arabic (`عناصر العمل` …) + drifted English ("To-Build"/"Tasks"/"To-Do") headings — recovers the 6 Arabic to-dos silently dropped from meeting id=5 on next launch. Version bumped 0.1.0 → 0.1.1; added `CHANGELOG.md`. `cargo test` 4/4 + `tsc` green; signed release `.dmg` rebuilt. **Pending: install the new DMG + visual confirm, then `git push`.** See [HANDOFF.md](./docs/HANDOFF.md) "Last session".
- **Overnight batch (2026-06-20, branch `overnight/polish-batch`, committed, NOT pushed):** delete + pin a meeting; editable summary; configurable auto-stop (Settings); post-transcription auto-select fix; **tags made per-meeting** + filter pillars keyed by label+color (red "Meeting"=standup vs blue=internal both show); **consolidated To-dos** view; **"+ add to dictionary"** button; **Weekly recap** view; **privacy lock** (per-meeting PIN, PBKDF2 — UI gate, DB not encrypted at rest); **cross-meeting RAG** ("Ask" across all meetings). Each `tsc`+`cargo check` verified per commit. Not yet run live — needs a clean `npm run tauri dev` rebuild.

## ✅ Relay build — MERGED to `master` + pushed (2026-06-21)
`feat/settings-providers-calendar` (28 commits: A/B0/C/B1/EK + M1/M2) fast-forward-merged into
`master` and pushed to `origin/master` (`15962ae`) after re-verifying the suite green (tsc · 18
cargo · 103 pytest). The items below are now on `master`. **Live-smoke (calendar TCC, M1/M2 UI) is
still pending** — see [HANDOFF.md](./HANDOFF.md) "Next step".

User's 3 to-dos, built via the stunt worker, each diff reviewed + verified by Claude:
- ✅ **Configurable LLM provider** (`6eca767`) — Settings Provider dropdown: **Local**[default] / xAI Grok / OpenRouter / OpenAI-compatible(custom). Cloud sends the transcript off-device (opt-in, amber-warned); local default unchanged. Lets GPU-less users run Adversaria against a cloud LLM. tsc/cargo/75 pytest green.
- ✅ **Calendar Phase 0 plumbing** (`12598aa`) — keyring (real macOS Keychain verified) + tauri-plugin-oauth, PKCE (RFC vector passes), `CalendarConfig`, credential commands. 5 calendar tests green.
- ✅ **Names fix** (`0ac424c`) — conservative attendee dedup (exact + token-subset, never fuzzy/`Me`/`Them`) + roster grounding to canonical spellings. 103 pytest (24 new).
- ✅ **Calendar Phase 1 — Google OAuth** (`77af3c1`) — PKCE+loopback connect (CSRF-validated), token refresh, Calendar v3 reads, Settings Calendar section, user-confirmed roster pre-fill after recording. Privacy verified (readonly scope, Rust-only network, keychain tokens, off by default). 7 calendar tests green. **Compile-verified only — needs the user's Google OAuth client ID to go live.** Microsoft = later B2.
- 🟡 **macOS EventKit calendar — permissions FIXED, roster test pending (2026-06-21):** Calendar **and** Screen Recording now grant + persist. Root cause of the "Enable does nothing / recording declined" was **ad-hoc signing churning the TCC identity every rebuild** (+ running from ~/Documents) — NOT the EventKit code (it works once the env is clean). Fixed by signing with the stable self-signed cert **`NotchyPrompter Dev`** + installing to **/Applications** + `tccutil reset`. `scripts/build-dmg.sh` now takes `ADVERSARIA_SIGN_IDENTITY`. **Pending:** user confirms the roster pull (record over a calendar event *with attendees* → banner). See [LESSONS_LEARNED.md](./docs/LESSONS_LEARNED.md).
- ✅ **macOS EventKit calendar (code)** (`01df912`) — zero sign-in design: reads the Mac's existing calendars (Google/iCloud/Exchange) via one permission, no OAuth/client IDs. Reuses B1's `CalendarEvent` types + commands + roster banner. Settings "Apple Calendar (this Mac)" card. Google OAuth retained as the Windows/cross-platform path. 8 calendar tests green; compile-verified (permission prompt + real events need the user's Mac).
- 📋 **Next gate (user): live-smoke.** ⚠️ **Calendar must be tested in a BUNDLED `.app` (`npm run tauri build`), not `tauri dev`** — macOS won't grant Calendars to the bare dev binary (no Info.plist → "Permission denied"; `docs/LESSONS_LEARNED.md`). Release `.app` built + EventKit links cleanly + calendar Info.plist key verified. In the bundle: Settings → Calendar → **Apple Calendar (this Mac) → Enable → Allow** → record → roster pre-fill. (Prereq: Google account in System Settings → Internet Accounts → Calendars on.) LLM provider + names dedup can smoke in `tauri dev`. Follow-ons: Microsoft B2; roster→new recordings; Windows browser-open fix; re-freeze sidecar for names-dedup in the bundle.

## ✅ `.dmg` packaging — DONE & verified end-to-end
- **`Adversaria.dmg` builds and works.** One command: **`./scripts/build-dmg.sh`** (freeze the Python ML service with PyInstaller → ad-hoc sign the sidecar with `entitlements.plist` → `tauri build` the `.app` → package the `.dmg` with `hdiutil`).
- **Verified:** launching `Adversaria.app` auto-spawns the bundled sidecar (~2s, free port) and **kills it on quit**; the embedded sidecar serves `/health`; MLX loads. New **Adversaria icon** (dark + azure "A").
- **Artifacts** (gitignored, in `src-tauri/target/release/bundle/`): `macos/Adversaria.app`, `dmg/Adversaria_aarch64.dmg` (~483 MB).
- **Gotchas baked in:** `freeze_support()`, SSL certs bundled, `mlx.metallib` at bundle root, av/ctranslate2/faster_whisper/tiktoken/hf_hub/certifi collected, `disable-library-validation` entitlement (survives `tauri build`). Tauri's own `bundle_dmg.sh` fails on the large app (AppleScript) → we use `hdiutil`. First launch slow (Metal shader compile, cached after).
- **Stays external:** LLM server (Rapid-MLX/Ollama) + MLX Whisper model (first-run download). ffmpeg currently via the user's Homebrew on PATH — bundling a static ffmpeg is a later portability polish.
  - ⚠️ **The app does NOT gracefully prompt when the LLM server is down** — summarize just fails with a raw `OpenAI-compatible request failed: [Errno 61] Connection refused`. Friendly health-gate/banner is a TODO (see [docs/TODO.md](./docs/TODO.md)).
  - ✅ **Daily-use LLM autostart configured (2026-06-20, this Mac):** a login **LaunchAgent** (`~/Library/LaunchAgents/com.lagharilabs.adversaria.llm.plist`, `KeepAlive`, `HF_HUB_DISABLE_XET=1`) runs `rapid-mlx serve qwen3.6-35b --port 8000` at every login. App config `ollama_model` switched `qwen3.6-27b → qwen3.6-35b` (A3B MoE). Verified live: server serves `qwen3.6-35b`; the app's exact request (`enable_thinking:false` + `response_format: json_schema`) returns clean structured JSON, no reasoning leak.

## Queued (per user, after `.dmg`)
- Speaker diarization (feature-flagged per `docs/SPEC_DIARIZATION.md`, needs their machine).
- Semantic embeddings on top of FTS5 (needs an embed model, e.g. `nomic-embed-text`).
- Bundle static ffmpeg for portability beyond the dev Mac.

## 🧪 Next milestone — Groq-first, registration-gated beta (decided 2026-06-24, NOT built yet)
Make Adversaria testable by **non-developer friends**: notarized DMG → drag in → paste a **free Groq key** → works (no Ollama/Python/hardware). **Decisions locked:** provider = **Groq** (groq.com — _not_ the app's "xAI Grok"; OpenAI-compatible, `whisper-large-v3` + `qwen/qwen3-32b`, free tier); **transcription → Groq cloud** (new upload path; summary-via-Groq already works config-only); user **joining the Apple Developer Program** (notarization = the hard gate for non-devs); trial = **offline signed license keys** (leaning, per-friend email + 1-yr expiry); **Tauri auto-updater** from the first DMG; first-run **beta-EULA** instead of an NDA. Groq cost to the user ≈ **$0** (each friend brings their own free key; even if paid, ~$1–2/user/mo). Real free-tier constraint = **6,000 TPM** on long-meeting summaries. **Sequence:** (1) simplified Settings + Groq preset → (2) Groq cloud transcription → (3) auto-updater → (4) license/trial gate → (5) notarized `build-dmg.sh`. **Awaiting greenlight on step 1.** Detail: [docs/HANDOFF.md](./docs/HANDOFF.md) "Last session" (#12), [docs/STRATEGY.md](./docs/STRATEGY.md).

## Planned
_Next frontier — "the agentic loop" (see [docs/STRATEGY.md](./docs/STRATEGY.md), [docs/TODO.md](./docs/TODO.md)):_
1. **To-do / Kanban board fed from meetings** — action items → task board. **User's stated #1; the killer 10× workflow.**
2. **Speaker diarization** — split "Them" into named individuals (biggest depth gap vs Meetily).
3. **Cross-meeting RAG** + real SQLite FTS5 search.
4. **OS bridge** — feed Adversaria into lagharilabs OS (retire its Granola dependency).
5. **Packaging → unsigned personal `.dmg`** (~2–4 days; PyInstaller-bundling MLX+ffmpeg sidecar is the risk). See [docs/PACKAGING.md](./docs/PACKAGING.md).

_Undecided candidate:_ **pre-meeting notes** (calendar-driven prep prompts) — user unsure of the value; clarify before building.

**Reimagined UI (2026-06-21 → DONE, MERGED to master 2026-06-22):** user prototyped a glassmorphic reskin at `MyProjects/adversaria-samples` (reskin of existing features, not a rebuild). Storage stays **SQLite + JSON columns**. The reskin, both schema migrations (M1/M2), the FTS fix, Me/Them removal, the floating bubble, and the MCP server are all on `master` (`eb3e1ee`). Status:
- ✅ **Reskin spec** written — [docs/SPEC_RESKIN.md](./docs/SPEC_RESKIN.md) (dark-glass tokens, prototype→React component map, 5-phase plan).
- ✅ **Reskin Phase 0 — dark-glass theme tokens** (`795d2b8`). Flipped the single-source Tailwind `gray` ramp cream→dark (whole app dark, **zero component edits**) + additive accent/glass/font/blur tokens + `:root` CSS vars + dark scrollbars. User confirmed the palette looks good.
- ✅ **FTS5 startup-brick fixed** (`49929f9`) — a fresh build panicked on launch (`CORRUPT_VTAB`) because the M1 backfill's `UPDATE` fires the FTS sync trigger on an out-of-sync index. `init_db` now drops+rebuilds the (derived) index and retries — no content lost. Found via the user's "still cream" launch (it was the stale `/Applications` bundle). 19 cargo tests + E2E vs the real corrupt DB. [LESSONS_LEARNED](./docs/LESSONS_LEARNED.md).
- ✅ **Reskin DONE — whole app converted to the prototype** (foundation `6512724`, all components `ce6f865`, wiring `6dbccf7`). **Inter self-hosted** (`@fontsource-variable/inter`, bundled, no CDN). Prototype `styles.css` → `src/prototype.css`; every component's JSX rewritten to its semantic classes. Done via **12 parallel agents** (one per component, presentation-only) + `App.tsx` shell by hand (always-visible `.sidebar` + swapping `.content-area`, glass modals). Header, sidebar (glass record button, monthly calendar grid, tag pills, glass cards), detail viewer (glass toolbar pin/lock/delete + Add-Tag color picker, transcript bubbles), Summary/To-dos/Weekly/Ask, Settings inner-sidebar, transcribing view — all dark-glass. tsc + vite green; runs live. **Polish remaining (non-blocking):** TodosView 2 filters not 4; NewNoteButton modal sizing; Settings calendar/cloud sub-cards still Tailwind; gray/yellow tags un-tinted; floating widget not done. See [docs/SPEC_RESKIN.md](./docs/SPEC_RESKIN.md) §4.
- ✅ **M1 — structured transcript** (`9bc57b2`) — additive `transcript_turns` JSON column, backfilled from the 26 flat transcripts; transcript tab → speaker bubbles. **Dry-run on a real-DB copy confirmed non-destructive + idempotent** (flat transcript 0 rows changed, all 26 backfilled). DB backed up WAL-safe first (`.bak-proper-*`).
- ✅ **M2 backend — first-class `action_items`** (`0271993`) — table (single source of truth) + IPC + sync-on-save + delete-cascade + idempotent backfill; **Summary-tab checkboxes now DB-backed**. ⚠️ **Caught via real-DB dry-run:** the delegated extractor assumed the prototype's `- [ ]` checkbox format, which the local LLM never emits → it extracted **0** items; rewrote it to the real format (bullets under an actionable `**Heading**`, assignee = leading `Name:`) → now **42 items across 9 meetings**. Migration verified non-destructive (summary untouched). 2 extractor tests + cargo + tsc + 103 pytest green.
- ✅ **M2 complete** (`5ed34d0`) — To-dos + Weekly rewired off localStorage onto `get_action_items`; `update_action_item` IPC (user due-dates persist + drive Today/Overdue filters; LLM emits none); `sync` preserves done/due/assignee by `ord` across re-summary. Removed 9 stale `- [ ]`-format tests. Full suite green (18 cargo + tsc + 103 pytest). **The #1 Kanban board now has its data foundation.**
- ⏸ **(c) calendar roster live-test** parked pending the user's event info (guests? in Calendar.app?). See [docs/TODO.md](./docs/TODO.md).

## Blockers
- **None blocking code.** The `.dmg` is built; transcription is bundled. The **LLM server is external** and must be running for summaries — now autostarted on this Mac via a login LaunchAgent (see the `.dmg` section).
- **macOS setup gotcha:** `HF_HUB_DISABLE_XET=1` for the Python service *and* the Rapid-MLX LaunchAgent, or HuggingFace model downloads hang/stall (Whisper *and* the LLM).

## Last updated
2026-08-10 — **🛡️ Model-output robustness ladder (Muse Glimmer incident) landed, uncommitted.** `python-service/src/summarizer.py` + new `tests/test_summarizer_robustness.py`: normalize any model's reply before parsing (think-tags, fences anywhere, prose-embedded JSON), repair a truncated JSON tail, retry once at doubled `num_ctx` on `done_reason=length`, and tell the user the truth when notes can't be built — raw JSON is never rendered as a note again. Python suite 410 → 453 passed, ruff clean. Unverified against the live model.

2026-07-02 (pm) — **📝 Deep-dive docs written: DEEP_DIVE_BUSINESS.md + DEEP_DIVE_TECHNICAL.md.**  
No code changed. Created two comprehensive, cross-referenced summaries of the entire project — one
business-oriented (market, strategy, competitive landscape, GTM, pricing, risks), one technical
(architecture layering, every feature's internals, full tech-stack table, ADR index, known debt).
Both span the full v0.3.14 scope. Added to CLAUDE.md companion-docs table. No commit needed (docs
only, user-requested).

2026-07-01 (**✅ IMPLEMENTED via delegation: Audio File Import — verified green, uncommitted**) — Delegated `SPEC_AUDIO_IMPORT.md` to the stunt worker (claude via free fcc, session `ec4f5a78`, 2 rounds, ~$4.36, zero Anthropic credits); I wrote the execution brief + reviewed. Users can now import a `.m4a`/`.mp3`/`.wav` file (e.g. an iPhone voice memo) → it runs the existing transcribe→summarize pipeline (single-track, in-process PyAV decode) → creates a meeting. 9 files (Python `single_file` branch + `decode_import_file` + 3 tests; Rust `import_audio`/`pick_audio_file`/`transcribe_import`; frontend "Import audio…" button). **Review caught + fixed** a failure-path data-loss gap (now saves a retryable pending meeting on failure via `save_pending_meeting`). Verified myself: `cargo check` ✓ · `tsc` ✓ · `pytest 126 passed` ✓. **✅ RE-FROZEN into the installed app** (v0.3.13, `NotchyPrompter Dev` — also re-fixes the ad-hoc TCC churn) and **backend API-verified on a real `.m4a`** (shipped sidecar `single_file` transcribe returned an exact transcript). **✅ Committed `4ef0300` + pushed** (feature + spec + living docs; the 3 future specs in `64fa242`; master == origin); user confirmed the UI import works. Dev lesson: `tauri dev` can't test Python changes (spawns the frozen old sidecar); use a re-freeze or a direct sidecar API curl. Next delegatable: export/import bundle, KG Phase-A (GraphRAG still needs its spike).

2026-07-01 (**📋 DELEGATED 4 feature spec docs to the free stunt worker — reviewed, untracked**) — To conserve Claude tokens, wrote an architect brief and delegated spec-drafting to the stunt worker (claude via free fcc proxy, session `39bd9cce`, $4.30, zero Anthropic credits). Produced under `docs/`: **SPEC_AUDIO_IMPORT** (voice-memo/audio import via the existing pipeline — #1 feature), **SPEC_EXPORT_IMPORT** (versioned JSON bundle + backup-all), **SPEC_KNOWLEDGE_GRAPH** (Phase-A graph from existing SQLite + cytoscape.js), **SPEC_GRAPHRAG** (research/design doc, spike-first). Reviewed: scope clean (docs only, no code touched, no git writes), references verified real, fixed one typo. Next: user reviews → delegate implementation of the 3 impl-ready specs; GraphRAG needs the spike. Uncommitted.

2026-07-01 (**🔴→🟢 FIXED ad-hoc-rebuild TCC churn — Screen Recording broke; re-signed in place, no rebuild**) — The user rebuilt the installed app **without** the stable signing identity → `Signature=adhoc` → macOS dropped the Screen Recording grant (ad-hoc cdhash changes every build) → recording failed with `NoShareableContent(… declined TCCs …)`. The rebuild otherwise worked (binary embeds the slide-export `dist`, so **Export ▾ → Export as Slide IS in the installed app**; earlier "not showing" was a pre-rebuild instance). **Fix without a 15-min freeze:** replicated build-dmg.sh's two `codesign` steps on the installed bundle (sidecar w/ `python-service/entitlements.plist` + disable-library-validation, then the `.app`) → verified `Authority=NotchyPrompter Dev`; `tccutil reset ScreenCapture com.meetingnotetaker.app`; relaunched (sidecar :55541 up). **User's step:** System Settings → Screen & System Audio Recording → enable Adversaria → quit & reopen (now persists). **⚠️ Reminder: always rebuild via `ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev" ./scripts/build-dmg.sh`** — a plain build ad-hoc-signs and re-breaks Screen Recording.

2026-06-30 pm (**🟣 BUILT dark "Meeting Minutes" SLIDE export — running live in `tauri dev`; PDF pivoted out**) — Discussed product direction and built a sharing feature. **Strategic frame:** for a *"nothing leaves your machine"* product, "share" = **export a beautiful file the user owns**, deliberately *not* a cloud share-link (Granola/Otter/Fireflies all default to server-hosted links — Granola has no export at all, our opening). **First built** a branded Save-as-PDF + HTML export; **user live-tested → PDF did nothing.** Root cause = a real macOS limitation: **Tauri's WKWebView no-ops JS `window.print()`** (works on Windows/WebView2). **Pivoted:** removed the in-app PDF (reverted `index.html`/`prototype.css` to net-zero) and turned the **HTML export into a dark, animated "Meeting Minutes" slide** (`src/lib/exportDocument.ts` → `buildSlideHtml`): ADVERSARIA reveal intro, multi-column masonry cards (Key Topics / Decisions / Action Items / Follow-ups) from `parseSummary`, accent-coded, gradient title, attendee chips, on-device footer; **pure-CSS animation, zero JS, self-contained**; Arabic-RTL aware (`unicode-bidi: plaintext`); carries an `@media print` block so a browser Cmd+P yields a clean dark-slide PDF. Saved via the Rust `export_html` command. Built to the user's lo-fi mock, more polished. Then **redone as a single fixed 1280×720 page** (no scroll, near full-width, content auto-shrinks) that maps to `@page{size:1280px 720px}` so a browser **Save-as-PDF = one page**. `tsc` ✓ · `cargo check` ✓; design + Arabic-RTL + single-page fit **visually verified** via headless-browser render. **COMMITTED `fe6c63b`** + a follow-up **PDF title fix** (gradient title printed as a white box → forced solid colour in `@media print`; **verified via a real headless `page.pdf` = 1 page, title correct**). Both **pushed to origin/master** (`ff6cd4d..a95e6be`; the expired GitHub auth was cleared via `gh auth login` + `gh auth setup-git`). **No re-freeze yet — the slide export lives only in `tauri dev`; `build-dmg.sh` is the next step to put it in the installed `/Applications` app.** Follow-ups: native macOS PDF (WKWebView `createPDF`), light print variant, redaction toggle, DOCX; Markdown free / slide+DOCX → Pro. The back-to-back queue live test (below) is still open.

2026-06-30 (**🟢 RE-FROZE v0.3.13 — the back-to-back queue is NOW in the installed app (was missing); awaiting the user's live test**) — User reported they *still* couldn't record a 2nd meeting while the 1st transcribes. **Root cause: the queue fix (`ae4a7c6`, Jun 29) was never built into the app they use** — `/Applications/Adversaria.app` was a **Jun 27 19:57 v0.3.12** build, two days older than the fix. Verified by binary mtime + the running PIDs, not assumed. Re-froze with `ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev"` (TCC grants persist) → **v0.3.13 installed + relaunched 07:16, sidecar healthy** (`/health` ok, large-v3, ollama up), signature valid. Bumped 0.3.12→0.3.13 across package.json/tauri.conf.json/Cargo.toml/Cargo.lock so the user can confirm the new build in About. **The fix has ZERO Python changes; code-reviewed sound this session but never live-tested — the user now runs the back-to-back test** (record A → Stop → Record B while A transcribes → Stop → both land). **Lesson: a committed-but-not-re-frozen fix is invisible to the user — check the installed bundle's build date vs the fix commit.** Version bump uncommitted pending the live result.

2026-06-29 (**🟢 BUILT + COMMITTED `ae4a7c6` + PUSHED — back-to-back-meeting background-transcription QUEUE (live test in progress)**) — Stop now saves the recording + **enqueues** it and frees the UI instantly; a single-worker frontend queue (concurrency 1, **paused while recording** so live captions stay snappy) transcribes in the background via the existing `transcribe_meeting(id)`. New Rust `enqueue_recording` command; `useRecording` rewritten (`status` → `idle|recording|stopping` + queue state/worker); `MeetingsList`/`NoteViewer` show **Transcribing…/Queued** badges. Root cause was purely a single global frontend `status` (confirmed by a 3-layer workflow). `cargo check` + 43 tests + `tsc` green; committed `ae4a7c6` + pushed; **dev app left running for the live back-to-back test — STILL PENDING** (user stepped away before running it). Honest caveat: an in-flight transcription can't be cancelled, so it briefly shares the model with a new recording's live captions (only new jobs are paused). (Apple enrollment still blocked on the founder: fails pre-payment → phone callback.)

2026-06-28 (**⚖️ LAUNCH DECISION MADE + codified — free-only, regulated-solo wedge, OSS MCP**) — Reviewed `docs/LAUNCH_PLAN.md` with the user and locked the GTM; the "pivot" turned out to be a *realignment to the founder's own STRATEGY.md* (the prosumer-freemium brief contradicted it). Accepted: **beachhead = regulated client-facing solos** (prosumers + Arabic/RTL = free funnel); **launch free-only**, Pro deferred ~30–60 days (LemonSqueezy MoR + offline Ed25519 license, waitlist at launch, no in-binary gating); **open-source the read-only MCP server**; lead with "nothing leaves your machine" + Bilzerian cold-open; honesty rewrite of all privacy claims; Show HN primary. Codified in `STRATEGY.md` §2026-06-28, `SPEC.md`, and a new `docs/TODO.md` **"Launch gates"** section (four hard gates: notarized clean install · Groq-default first-run wizard · loud Groq-limit failure · capture-path Rust tests). **No code.** Committed `44b7ee1` (docs + LAUNCH_PLAN.md + HTML) — **pushed to origin.** **Then: Gate 1 (macOS notarization) STARTED → ⛔ BLOCKED on Apple Developer enrollment** (`0cd1fbc`). Verified this box has only the self-signed `NotchyPrompter Dev` identity, **no Developer ID Application cert** (notarization requires it); current Tauri 2 sign+notarize flow confirmed via context7 and staged in [docs/SPEC_DMG_PACKAGING.md](./docs/SPEC_DMG_PACKAGING.md) §7.3 (also fixes Known-issue #1's updater TCC reset). **Founder must:** enroll ($99/yr, ~24–48h) → create a Developer ID Application cert → app-specific password (`APPLE_ID`/`APPLE_PASSWORD`/`APPLE_TEAM_ID`); then the `build-dmg.sh` rework happens with the cert in hand. **⛔ UPDATE: enrollment ATTEMPTED → Apple _"could not be completed at this time"_** (generic catch-all; usually a silent identity hold). **Diagnosed** (9-agent adversarial workflow): verified unblock checklist + post-enrollment gotchas now in [docs/TODO.md](./docs/TODO.md) Gate 1 + [SPEC_DMG_PACKAGING.md](./docs/SPEC_DMG_PACKAGING.md) §7.3 (add card+address on Apple ID first · exact legal-name match · region==card==phone · web-not-app, VPN off · then phone-callback support · track the $99 charge). No free notarization path. **DECIDED: Individual enrollment** (personal legal name as developer; migrate to Org later if warranted). **✅ BUILT the interim beta installer** (`scripts/beta/Install Adversaria.command` + `INSTALL.txt`; `build-dmg.sh` auto-bundles them into the `.dmg` for non-notarized builds) so the private beta can run before notarization — beta `.dmg` ships on the next `build-dmg.sh` run. Launch decoupled from Apple. **(2026-06-29) Enrollment still failing — and it fails BEFORE the payment page** (rules out the card; no $99 charged; points to Apple's pre-payment account-eligibility/identity/region gate). Advised: **phone callback** to learn if it's a fixable region/account issue (a) or a hard identity flag (b); free checks = Apple-ID region == phone-number country, VPN off, try the iPhone Apple Developer app. A fresh Apple ID *may* help (the **domain** doesn't); buy lagharilabs.com for the landing page + future Org enrollment, not as the fix. Un-notarized DMG ships to technical testers now regardless. **Unblocked meanwhile:** draft the Show HN post + landing hero (LAUNCH_PLAN.md §4/§7), or open-source the MCP server (decided yes). All three commits **pushed** (`master` == origin/master, HEAD `79c2813`).

2026-06-28 (**✅ USER-VERIFIED — spoken to-dos now show in Action Items (installed app)**) — the transcript→summary→`action_items` data-hierarchy gap is closed end-to-end. Whole session is shipped + (this part) verified in the real app. Still to confirm: Ask provenance badge. Open threads: launch-plan pivot decision (`docs/LAUNCH_PLAN.md`), blocked sign-up gate, intermittent offline "not recording" banner.

2026-06-27 (**✅ RE-FREEZE SHIPPED — entire session now live in the installed app**) — `build-dmg.sh` re-froze + signed (NotchyPrompter Dev, TCC-safe) + installed v0.3.12 to /Applications + relaunched; app + fresh sidecar verified healthy, and the broadened spoken-to-dos Action-Item prompt is confirmed in the frozen bundle. Now in the real app: data-loss fix, conversational Ask + persistence, intent routing 1–5 (todos/recap/overview/detail) + provenance badge, recap rollup, RTL fix, 3-state sovereignty dot, and the spoken-to-dos→action_items prompt fix. Increment 5 + prompt fix committed `cb1813c`. **Next:** user verifies B (re-summarize brainstorm) + A (badge) in the installed app.

2026-06-27 (**Increment 5 (Ask provenance badge) + summary-prompt fix for spoken to-dos — committed `cb1813c`**) — Each Ask answer now shows a **provenance badge** (From your To-dos / Weekly rollup / From summaries / From transcripts), persisted via a new `ask_messages.intent` column. `general.md`'s Action Item definition broadened so **spoken to-dos** ("my to-do is…", "let me list my to-dos: X, Y, Z") become `action_items` (was filed under Key Topics) — needs the re-freeze. Empty targeted to-do filter now says "none yet". `cargo test` 43 + `tsc` green. **`build-dmg.sh` re-freeze in progress** to finally ship the whole session (data-loss fix, conversational Ask + persistence, intent routing 1–5, recap, RTL/sovereignty, prompt fix) to the installed app.

2026-06-27 (**✅ COMMITTED `3fecf33` — layered Ask increments 3–4: overview→summaries + recap→weekly rollup**) — Full intent→layer routing now complete: **todos**→`action_items` (0-LLM) · **recap**→on-demand weekly digest (new `recap.rs`, 0-LLM, mirrors the Weekly tab) · **overview**→dense summaries · **detail**→transcripts. `cargo test` 43 + `tsc` green, dev app clean (1/1). Next: increment 5 (provenance badge) or the summary-prompt fix so spoken to-dos reach `action_items` (re-freeze).

2026-06-27 (**✅ COMMITTED — layered Ask increments 1–2 (intent routing; to-dos from `action_items`) + RTL & sovereignty fixes**) — The cross-meeting Ask router now classifies an **intent** (`todos|recap|overview|detail`, fail-open to `detail`). **`todos` → 0-LLM answer straight from the authoritative `action_items` table** (filtered mine/overdue/today/etc., grouped by meeting, ☐/☑ + overdue, source links; empty → transcript fall-down labeled "not tracked yet"). `recap`/`overview`/`detail` still transcript-grounded — increments 3 (overview→summaries) + 4 (recap→weekly `recap.rs`) **next**. Fixes: Ask renders `dir="auto"` (one Arabic item no longer flips the whole list RTL); header **3-state sovereignty dot** 🔵 full / 🟠 partial / 🔴 cloud. `cargo test` 40 (4 new) + `tsc` + 10-case live intent red-team. Known follow-ups: empty completed/overdue filter shouldn't fall to transcript; spoken to-dos not captured into `action_items` (summary-prompt gap, needs re-freeze).

2026-06-27 (**📋 Launch plan + 360° competitive research delivered — NO code; 2 new untracked docs**) — User asked for a complete go-to-market plan. A 20-agent background workflow (~1.6M tokens, real cited web research on Granola, Meetly, Otter, Fireflies, Fathom, tl;dv, Circleback, Supernormal, **Hyprnote**, **Meetily** + market/privacy/channels) produced **`docs/LAUNCH_PLAN.md`** (full Product Success Overview) + **`launch-plan-adversaria.html`** (styled report). **Verdict:** strong differentiated v1; **but the plan recommends a PIVOT off the briefed GTM** — launch **free-only** (Pro in ~30–60 days), keep prosumers as a free funnel but **monetize regulated client-facing solos**, lead with "Nothing leaves your machine" + the Bilzerian/Otter story, **open-source one component** (the MCP server), **Show HN primary**. Pricing: $0 generous local tier + Pro **$15/mo or $120/yr** via LemonSqueezy MoR + offline license. Beta: **yes, 30–50 private testers** to de-risk the untested Rust capture path. Four hard launch gates (notarization · Groq-default wizard · loud Groq-limit failure · capture-path tests). **⚠️ Awaiting the user's decision on the pivot** — if accepted it updates STRATEGY.md/SPEC.md (which currently say enterprise/sovereign is the business, Pro deprioritized). Nothing committed.

2026-06-27 (**✅ COMMITTED + PUSHED — conversational Ask + guardrails + persistence; 3 testing-bug fixes; provider/model fix; data-loss fix**) — Cross-meeting **Ask** is now a persisted multi-turn thread (`ask_messages` table, loads on mount → survives tab/meeting switches + restart) with a **triage+condense+guardrail router**: off-topic/injection (e.g. "write python", "ignore your instructions") are refused; follow-ups have pronouns resolved before retrieval ("which company is he in" → "…is Wajee in"). All Rust+frontend, reusing `/chat` twice — **no Python re-freeze**. Also: MeetingChat auto-scroll, TodosView newest-first + focus-refetch, Ask grounds in transcripts (not summaries), Settings provider→model auto-match (fixes the local 404). `cargo test` 36 (6 new router tests) + `tsc` green + 10-case live guardrail red-team vs `qwen3.6-35b`. **Open design thread (user, important):** the data hierarchy — transcript (primary corpus) → meeting summary → weekly summary → to-dos — and routing Ask across these layers (to-do questions should consult `action_items`, not just transcript RAG). Not built yet.

2026-06-26 (**✅ FIXED — data-loss bug (TODO #0): recordings survive an ML-service outage at Stop**) — Recordings used to be deleted even when transcription failed (service down) → the whole meeting was lost. Now: recordings write to durable `<app-data>/recordings/`; audio is deleted **only after a successful transcription**; a failed pipeline saves a **pending** meeting (audio kept, "Needs transcription" tag, notes preserved); new `transcribe_meeting(id)` retries on the stored audio and deletes it only on success; `NoteViewer` shows a "Not transcribed yet" → **Transcribe now** banner. `cargo check` + 30 cargo tests (2 new) + `tsc` green. ADR-003 narrowed ("deleted after a *successful* transcription"), SPEC updated, TODO #0 → Done. **NOT committed; no re-freeze yet** — needs `build-dmg.sh` + a live test (record with service stopped → pending meeting → start service → Transcribe). Follow-up: kept WAVs not yet encrypted at rest (DB is). The sign-up/v0.3.13 thread below is **still blocked** on the user's Google Form values.

2026-06-26 (**🚧 IN PROGRESS, UNCOMMITTED — required sign-up gate + Google Form email collection**) — After testing v0.3.12, user wants the sign-up **required** (not skippable) and emails **reliably collected** for a mailing list (mailto can't do that). Coded (compile-verified, NOT committed, 7 files): `Welcome.tsx` → required modal (no Skip, valid-email gate); new Rust `submit_signup` POSTs `{name,email}` to a **Google Form** (from Rust, per the privacy rule) → responses land in a Sheet; new `signup_synced` config retries offline sign-ups next launch. Verification = valid-format email only (no backend). ⛔ **Blocked on the user's Google Form values** (`SIGNUP_FORM_URL` + 2 `entry.<id>` are `PASTE_…` placeholders in `commands.rs`). Resume: form pre-filled link → fill 3 constants → curl-test → reset `beta_onboarded` → re-freeze **v0.3.13** + commit. Beta steps left: 4 (this finishes the lightweight gate; full license/trial still later), 5 (notarized DMG + updater signing-order fix, TODO #0).

2026-06-25 (**v0.3.12 — first-run beta sign-up + in-app feedback**) — Both privacy-clean via `mailto:` (no backend; nothing sent until the user hits send). **Sign-up:** `Welcome.tsx` modal shown once on first launch (`beta_onboarded` config) captures name + email (`user_email`), stored locally, with an optional pre-filled mailto sign-up to `mhlaghari@gmail.com`; non-blocking (Skip onboards). **Feedback:** new Settings "Feedback" tab — textarea → pre-filled `mailto` with the message + app version. `tsc`+`cargo check` green; re-froze + installed v0.3.12 (also restores the stable signature the auto-update test left ad-hoc). Channel left at v0.3.11. Lightweight MVP of **beta step 4** (full license/trial gate still pending). Beta steps left: 4 (license/trial gate — full), 5 (notarized DMG + the updater signing-order fix, TODO #0).

2026-06-25 (**v0.3.10 — auto-updater wired (beta step 3, ADR-014)**) — Tauri v2 updater so beta testers get fixes without a new DMG. Minisign signing key (in `~/.tauri/`, never committed; pubkey compiled into `tauri.conf.json`); `createUpdaterArtifacts`; `tauri-plugin-updater`+`tauri-plugin-process`; `updater`/`process` capabilities; **`UpdatePrompt.tsx`** auto-checks on launch → dismissible glass toast → download → relaunch; `build-dmg.sh` signs the `.app.tar.gz`; **`scripts/publish-release.sh`** writes `latest.json` from the `.sig` + cuts the release. **Host = new PUBLIC repo `LaghariLabs/adversaria-releases`** (source stays private). `cargo check`+`tsc` green. **ROUND-TRIP TEST ✅ PASSED:** published v0.3.10→v0.3.11 to `LaghariLabs/adversaria-releases`; the installed v0.3.10 auto-detected, downloaded, minisign-verified, installed + relaunched as **v0.3.11** (user-confirmed). The endpoint, signed-artifact pipeline, and in-app toast all work. 🔴 **Follow-up before distribution:** the auto-updated app is **ad-hoc signed** (the updater `.app.tar.gz` is built by `tauri build` BEFORE `build-dmg.sh`'s NotchyPrompter Dev re-sign) → an auto-update **resets TCC grants** (mic/screen/calendar). Fix the signing order (sign `.app` before the tarball, or `APPLE_SIGNING_IDENTITY` for `tauri build`) — bundle with notarization (step 5). [DECISIONS ADR-014]. Beta steps left: 4 (license/trial), 5 (notarized DMG + this signing fix).

2026-06-25 (**v0.3.9 — encryption-at-rest toggle + Touch ID unlock; re-froze**) — Two user-requested security UX changes (ADR-013). (1) **Encryption toggle:** `encrypt_db` config (default on) + Settings switch; turning it off decrypts the DB to plaintext at next launch (new verified/backed-up `migrate_encrypted_to_plaintext`) and deletes the keychain key, ending the macOS keychain-password prompt. (2) **Touch ID unlock:** `robius-authentication` (Touch ID / Windows Hello, OS-password fallback) via a `biometric_authenticate` command + `biometric_unlock` config/toggle; opening a 🔒 meeting tries biometrics first and **falls back to the existing PIN** — PIN retained, not replaced. `cargo check` ✓, 28 Rust tests ✓ (both encrypt/decrypt round-trips), `tsc` ✓. Re-froze + reinstalled (single clean instance); **user-confirmed working live** (Touch ID unlock + encryption toggle removes the keychain prompt). [DECISIONS ADR-013].

2026-06-25 (**Groq chat `<think>` leak — FIXED, verified live, re-froze**) — "Chat with a meeting" on Groq qwen3-32b streamed the model's `<think>…</think>` reasoning before the answer (chat is neither json-constrained nor `enable_thinking`-guarded, unlike summaries). **Fix** (`summarizer.py`): `_strip_think()` for `chat()` + `_strip_think_stream()` (buffers a leading think block until `</think>`, then passes the answer through) for `chat_stream()`. Provider-agnostic, no-op for local/non-reasoning models. Verified live against Groq; 123 pytest green; committed + pushed; re-froze. **The full BYO-Groq path — transcribe + summarize + chat — now works end-to-end.** [LESSONS_LEARNED](./docs/LESSONS_LEARNED.md) top entry.

2026-06-25 (**Groq cloud transcription 413 — FIXED, verified live, re-froze**) — With transcription set to Groq cloud, recordings failed with `413 Payload Too Large` after ~1 min: `transcribe_cloud` uploaded the **raw** capture WAV (macOS system channel = 48 kHz/2ch/32-bit ≈ **23 MB/min**) past Groq's **25 MB** cap. **Fix** (`transcriber.py`): downsample each channel to **16 kHz mono** (Whisper-native, lossless for ASR, Groq's recommended preprocessing) and **chunk under the cap**, offsetting each chunk's segment timestamps before the Me/Them merge. Decode/resample is **in-process via PyAV** (bundled ffmpeg libs — a packaged GUI app won't find a system `ffmpeg` on PATH); chunk WAVs via stdlib `wave`; `_CLOUD_MAX_UPLOAD_BYTES` default 24 MB (env-overridable for dev tier). **Verified live against real Groq** (34.6 MB raw → multi-chunk, no 413). 119 pytest green (4 cloud tests). Re-froze + reinstalled. [LESSONS_LEARNED](./docs/LESSONS_LEARNED.md) top entry.

2026-06-25 (**Groq summarization 400 — FIXED, verified live, re-froze**) — User set both LLM + transcription to Groq (`qwen/qwen3-32b`) and summarize failed with an opaque `400 Bad Request`. Two causes, isolated via `curl`: (1) the code sent `chat_template_kwargs` (a vLLM-only param) on every OpenAI-path request → Groq rejects unknown params (`property 'chat_template_kwargs' is unsupported`), firing before the old json_schema fallback; (2) `qwen/qwen3-32b` on Groq has no `json_schema` (only `json_object`). **Fix** (`summarizer.py` `_chat_openai`/`_chat_openai_stream`): adapt to server quirks **per-host** — on a 400 naming an unsupported field, drop it + retry (new `_NO_CHAT_TEMPLATE_KWARGS` mirrors `_NO_JSON_SCHEMA`); now also surfaces the server's error body. Local vLLM/Rapid-MLX unchanged. **Verified live against real Groq** (full structured summary). 3 new tests; 108 pytest green (2 transcriber-dep tests skipped — `faster_whisper` absent in base venv, pre-existing/env). Re-froze + reinstalled to ship it. ⚠️ Watch: Groq chat (non-json) may leak `<think>`. [LESSONS_LEARNED](./docs/LESSONS_LEARNED.md) top entry.

2026-06-25 (**RE-FREEZE DONE — v0.3.6+0.3.7+0.3.8 now LIVE in the installed app**) — Ran `ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev" ./scripts/build-dmg.sh` (stable cert → TCC grants persist): PyInstaller froze the Python sidecar with the new `/whisper_models`+`/whisper_download` endpoints, the cloud-transcription path, and the hardened `general` prompt; built + signed the `.app`/`.dmg`; auto-installed **v0.3.8** to `/Applications` + relaunched. **API-verified the packaged sidecar:** `/health` → `{"status":"ok","whisper_model":"large-v3","ollama_available":true}`; **`/whisper_models` returns all 3 models** with download flags (`large-v3` downloaded; `turbo`/`turbo-q4` not) — this **resolves the "only Large v3, no Download buttons" report** (it was the frozen-sidecar gate, not a bug); `/templates` carries the hardened `general`. ⚠️ v0.3.7 Groq cloud-transcription round-trip still needs a **live-key** test. No tracked source changed (artifacts gitignored). **Next: UI confirm in the installed app (Settings → Transcription shows 3 models + Download buttons), then beta steps 3–5 (auto-updater → license/trial → notarized DMG).**

2026-06-25 (**v0.3.8 — on-device Whisper model picker**) — Settings → Transcription (On-device) now lists curated MLX Whisper models with download status + a **"Download now"** button (Downloading… → Ready ✓): `large-v3` (rec, Arabic), `large-v3-turbo`, `large-v3-turbo-q4`. Chosen model threaded through `/transcribe`; MLX loads it per-call (HF auto-downloads on first use → no restart). New `whisper_model` config; Python `/whisper_models` + `/whisper_download`; Rust `list_whisper_models`/`download_whisper_model`; HF-cache detection. Verified: `tsc` ✓, `cargo check` ✓, registry logic ✓ (real cache check correctly shows large-v3 already downloaded), 2 pytest tests. **Pushed to origin (`3642041`, 8 commits).** Was dormant in dev until the re-freeze above (now live).

2026-06-25 (fix — empty Prompts tab; dev hot-reload hygiene) — User saw the Prompts tab dropdowns blank. Backend was fine (sidecar served all 4 templates); root cause = Settings fetched templates **once at mount with no retry**, losing the race against the sidecar's ~few-second Whisper boot → permanently blank until a re-mount. Fix: `loadTemplates` now **retries on empty/failure** (10× / 1.2s) since there are always ≥4 bundled templates (`Settings.tsx`; `tsc` green). Also documented (HANDOFF Gotchas) that repeated `tauri dev` hot-reloads orphan the sidecar + leave Vite on 1420 (→ empty prompts / false "Offline") and the clean-restart fix; dev relaunched clean (app 35607 / sidecar 56427). Reminder: dev uses the FROZEN sidecar, so the v0.3.6 hardened prompt + v0.3.7 cloud transcription need a `build-dmg.sh` re-freeze to be live.

2026-06-25 (**v0.3.7 — BYO-key cloud transcription**) — Settings → Transcription now has an **Engine** picker: on-device Whisper (default, sovereign, diarized) **or** Cloud — Groq (BYO key), with UI warnings that cloud is **not sovereign + no diarization**. Backend: new `transcribe_cloud()` uploads each channel to an OpenAI-compatible `/audio/transcriptions` (Groq preset, `whisper-large-v3`) and merges Me/Them by timestamp; config fields `transcription_base_url/_api_key/_model` threaded Rust→Python. Verified: `tsc` ✓, `cargo check` ✓, cloud path logic ✓ (2 pytest tests added + mocked-httpx verification) — **the real Groq round-trip needs a live key**. ⚠️ Packaged DMG needs a Python re-freeze to ship. **Next (v0.3.8): downloadable local-model picker — faster/smaller Whisper variants + NVIDIA Parakeet (10× faster English; needs a new on-device CoreML/ANE backend; keep Whisper large-v3 default for Arabic).**

2026-06-24 (**v0.3.6 committed** — Settings redesign + hardened default prompt + ⋯ SVG icons + sidecar-routing fix) — Bundled the session's verified work into v0.3.6 on master: the rebuilt Settings (Groq-first AI Engine tab, dedicated Prompts tab, consistent button/control system), the hallucination-hardened default `general` prompt (promoted from the A/B-tested strict version — fixes inverted facts, fabricated decisions, merged attendees, invented tool names on the local 35B), ⋯-menu emoji→SVG, and the `update_config` sidecar-routing bugfix. `tsc` + dev `cargo` build green; prompt A/B-verified on the local model. Private interview artifacts (`transcript.md`, `summary*.md`) gitignored. ⚠️ Packaged DMG needs a re-freeze to ship the prompt + Python-side changes. **Next: v0.3.7 — transcription engine picker (local Whisper model download + Groq BYO-key, with no-diarization/not-sovereign warnings); Parakeet as a later fast backend.**

2026-06-24 (BUGFIX — false "ML Service Offline" + summarize/transcribe broke after a Settings save — fixed in v0.3.6, verified live) — Root-caused live: the bundled sidecar auto-spawns on a **dynamic free port** (in dev too — the bundled binary exists under `target/debug`, so the "packaged-only / None in dev" comments in `commands.rs` are **stale**), and `spawn_sidecar` points the HTTP client there. But `update_config` — which runs on **every Settings save** — reset the client to config's `python_service_url` (default `127.0.0.1:9876`, nothing listening), clobbering the live port. Symptoms: red "Local ML Service: Offline" pill **and** `Summarize/transcribe request failed: …url (http://127.0.0.1:9876/…)` after any save. **Fix** (`commands.rs` `update_config`): only `set_base_url(config.python_service_url)` when `state.sidecar` is `None` (no managed sidecar). Verified: dev watcher rebuilt + relaunched, new sidecar on `:52929` healthy, pill now **Online**. ⚠️ **Beta-relevant** — would bite packaged testers the instant they save their Groq key. (Also killed an orphaned sidecar the hot-reload left behind — the watcher SIGKILLs the parent so the app's `shutdown_sidecar` cleanup doesn't run.) Fold into **v0.3.6**; needs a DMG rebuild to reach testers.

2026-06-24 (Settings redesign + UI polish — UNCOMMITTED, tsc-green, design self-verified) — Rebuilt
`Settings.tsx` into a simpler, production-grade layout: a Groq-first **"AI Engine"** tab (Groq preset
added + recommended default; the Python-service URL + health now tucked behind an "Advanced" disclosure)
and a **new dedicated "Prompts" tab** with a large editor. Root causes fixed: the prompt box was collapsed
to one line because `.settings-input-text` forces `height:38px` on a `<textarea>` (new `.settings-textarea`);
buttons were inconsistent (`.btn-primary` had no height/`nowrap` → "Set PIN" wrapped; `.btn-secondary`
had `flex:1` → mismatched Save/Delete). Fix: made `.btn-primary` consistent (38px, nowrap, no-squeeze) +
new `.btn-ghost`/`.btn-danger` (left the shared `.btn-secondary` untouched to avoid regressing other
screens). Replaced ad-hoc Tailwind callouts with semantic `.settings-note`/`.settings-subcard`/`.settings-help`.
Verified via a faithful `prototype.css` mockup screenshot (can't drive the Tauri webview here). Also
swapped the **⋯ row menu's emoji icons (📌🔒🗑) for SVGs** (`MeetingsList.tsx`; reuses `.settings-menu-item`,
lock opens when locked). Relaunched the dev app (v0.3.5 build, real data loads, no keychain re-prompt).
**Not committed; no DMG rebuilt.** Next: user click-through → commit as **v0.3.6**; then header status-pill
polish + remaining decorative emojis (🍎 etc.), and wire **Groq cloud transcription** (beta step 2).

2026-06-24 (beta strategy decided — no code yet) — Planned a **Groq-first, registration-gated beta** for
non-developer friends (see the "🧪 Next milestone" section above). Locked: provider = Groq (groq.com);
transcription → Groq cloud; user joining the Apple Developer Program (notarization is the hard gate);
trial = offline signed license keys (leaning); Tauri auto-updater from the first DMG; beta-EULA over NDA.
Groq cost to the user ≈ $0 (friends bring their own free keys). Researched + cited: Groq free-tier limits
& pricing, Tauri v2 updater, macOS notarization. **Awaiting greenlight on step 1 (simplified Settings +
Groq preset).** No beta code written.

2026-06-24 (calendar heatmap + date-scoped tag pills — **v0.3.5**, committed to master) — Two sidebar UX
changes the user asked for, both `npx tsc --noEmit` green and **user-confirmed working live**:
(1) the month calendar now grades day cells by meeting count — `DateHeatmap.tsx` `level()` → `level-1..4`
(absolute buckets 1/2/3/4+), `prototype.css` four blue-opacity tiers (`.heatmap-day-monthly.level-1..4`,
after `.has-meetings` so they win on source order) — busier days render darker (was a binary
has-meetings shade); (2) the tag/category pills now scope to the selected day (`MeetingsList.tsx` builds
the pillars from the date-filtered meetings) so clicking a day lets you filter within it. [docs/HANDOFF.md "Last session".]

2026-06-24 (competitive assessment + marketing strategy) — no code changes. Claude read the entire
codebase + docs and produced a comprehensive competitive assessment saved to
`docs/marketing_strategy.md`, covering pros, cons, competitive positioning table, BYOK vs subscription
recommendation, 15 prioritized improvements, and the strategic fork (polish into product vs. keep as
lagharilabs OS capture organ). Added to CLAUDE.md companion docs table.

2026-06-24 — **MCP server moved to standalone** (`~/Documents/Documents/MyProjects/mcp-server/`).
The old `mcp-server/` was deleted from this repo. The standalone copy was debugged (clean venv,
pure-stdlib+mcp imports, all 4 tools verified via MCP handshake). The consumer (lagharilabs OS)
points at the standalone path — no changes needed there.

## Last updated (earlier today)
2026-06-23 (DeepSeek empty-summary fixed; rebuilt & installed) — `master` `d837b00`: with the json_object fallback, DeepSeek's output shape drifted (`sections` sometimes bare strings → summary rendered as empty headings). Fixed by **pinning the exact JSON shape in the prompt** (`{heading,bullets}` objects, section names not hardcoded). Verified 3/3 DeepSeek runs return full bullets; 110 pytest green. Re-froze Python + reinstalled signed `.dmg` to /Applications (mtime Jun-23 08:47). [LESSONS updated.]

2026-06-23 (DeepSeek summarization fixed; rebuilt & installed) — `master` `9ca9f5d`: cloud summarize failed because (a) model was wrong-case (`Deepseek-v4-flash` → `deepseek-v4-flash`, fixed in config; key verified valid via `/v1/models`) and (b) **DeepSeek rejects `response_format: json_schema` (HTTP 400)** — `_chat_openai` now falls back to `json_object` (keeps strict schema for local vLLM). The `:8765` 404 was a stale prior-config artifact (`load_config` is per-request, not cached for LLM). 110 pytest green; re-froze Python + reinstalled signed `.dmg` to /Applications (mtime Jun-23 08:14). [LESSONS updated.]

2026-06-23 (bubble Stop fixed + DeepSeek 404 diagnosed; rebuilt & installed) — `master` `be57d43` (pushed): (1) **bubble Stop** now routes through Rust (`bubble_stop_recording`: focus main + `app.emit` the tray toggle) — a JS emit from the separate bubble webview wasn't reaching the minimized main window, so Stop did nothing. (2) **summarize 404** was config, not code: API-key field held the URL + model wrong-case (`Deepseek-v4-flash` → `deepseek-v4-flash`); override is read per-request, fix in Settings. Rebuilt signed `.dmg`, installed to /Applications (mtime Jun-23 07:58). tsc + cargo green. Both gotchas logged in [LESSONS](./docs/LESSONS_LEARNED.md).

2026-06-22 (2 bug fixes + dmg rebuilt & installed) — `master` `9059ad0` (pushed): (1) **sidebar meeting click now jumps to the Meetings tab** from any tab (`App.tsx` `setView("meetings")` after select; + PIN-unlock path) — was selecting silently while the tab kept rendering. (2) **interview to-dos:** data was in the DB and current code shows it — the **installed app was the stale Jun-21 build**; rebuilt the signed `.dmg` and **installed to /Applications** (replaces it, mtime Jun-22 23:55). Also hardened `TodosView` to never silently drop an item whose meeting isn't loaded. New build also carries the right-click guard + DeepSeek provider.

2026-06-22 (right-click guard + DeepSeek provider + rebuilt signed `.dmg`) — `master` `a585c07` (pushed): (1) production-only right-click guard in `main.tsx` (`import.meta.env.PROD` → `preventDefault` contextmenu) so the packaged app has no browser/Inspect menu; dev keeps it (devtools already off in release). (2) **DeepSeek** added to the Settings provider dropdown — preset `https://api.deepseek.com`, model `deepseek-v4-flash`, opt-in cloud warning; Local stays default; frontend-only passthrough. (3) Rebuilt signed `.dmg` → `src-tauri/target/release/bundle/dmg/Adversaria_aarch64.dmg` (484M, `Authority=NotchyPrompter Dev`); not yet installed to /Applications.

2026-06-22 (tag delete + OS bridge merged to lagharilabs `main`) — (1) **Delete a tag** (`master` `3895715`, pushed): each per-meeting tag pill in NoteViewer has an × (`removeTag` → `updateMeetingTags` minus that tag); frontend-only, `.tag-badge-remove` CSS; tsc green; works on existing meetings. (2) **lagharilabs-os `feat/adversaria-mcp` merged to `main` + pushed** (`main` = `049d272`) — fast-forwarded the whole 8-commit stack (Adversaria MCP + the 7 memory-evolve commits) per the user's choice; their WIP was stashed/restored to `feat/memory-evolve-slides`. lagharilabs `main` carries the memory work; ✅ its 1 failing test is now fixed on `main` (`3f11483`, suite 521 green) and the redundant `feat/adversaria-mcp` branch is deleted (local+remote). All Adversaria work pushed (`master` == origin `3895715`).

2026-06-22 (MCP local-time fix + OS bridge to lagharilabs-os) — (1) **MCP server returns LOCAL time, not UTC** (`b2a2ec1` on `master`, **committed but NOT yet pushed — origin still at `eb3e1ee`**): `_to_local_iso()` converts the stored UTC `recorded_at`→this machine's local zone in all meeting/action-item tools (DB stays UTC). Fixes meeting times reading 4h early (raw UTC) in MCP clients; verified on the live DB. ⚠️ Restart a running MCP client to drop its stale subprocess. (2) **"OS bridge" realized:** `lagharilabs-os` now consumes the Adversaria MCP server (its branch `feat/adversaria-mcp` `049d272`, not pushed) and **Granola is retired** there — wired into its Qwen-Agent (4 tools register), `/adversaria` skill added, Granola tool/client/skill/frontend/docs removed; 520 pytest pass (1 pre-existing fail). Follow-up: structured meeting-card in lagharilabs-os (MCP shape ≠ old Granola payload → text answers for now).

2026-06-22 (floating bubble Stop — MERGED; session complete) — `feat/bubble-stop` merged + pushed (`eb3e1ee`), branch deleted. The floating recording bubble now has a **working Stop** (the earlier bug — Stop just opened the app — was `emit` + `focusMainWindow` racing; fixed by `await emit` before focus) plus visual polish + a fix to the main transcribing view's stale "Stop & Summarize Note" button label. With this, the whole session's work is on `master`: full dark-glass **reskin**, **FTS5 corruption fix**, **Me/Them removal**, **floating bubble + Stop**, and the standalone **MCP server**. Suite green: tsc · 20 cargo · 108 pytest. No code work pending — forward options in [HANDOFF.md](./HANDOFF.md) "Next step" (productize for free beta / more MCP tools / calendar roster diagnostic).

2026-06-22 (MCP server — MERGED to master) — Standalone sovereign-first **MCP server** (`mcp-server/`, `ab6e8e5`): read-only, on-device access to meetings + to-dos for any MCP client (Claude Desktop/Code, OpenAI, local LLM). FastMCP/stdio; tools list_recent_meetings/search_meetings/get_meeting/get_action_items. Verified end-to-end via a real stdio MCP client (initialize→tools/list→call_tool). README + privacy note included. Pending user wiring + merge. (Earlier today, all merged to master: reskin, FTS fix, floating bubble, Me/Them cleanup.)

2026-06-22 (floating recording bubble) — Granola-style floating "Recording" bubble (`59b617f`): small always-on-top window shown while recording when the main window is minimized/blurred (click to return). Rust `AppState.recording` + main-window `Focused` handler; `RecordingBubble.tsx` via `?widget=recording`. tsc + cargo check green. SPEC_RESKIN §4 floating-widget ✅. Pending user test. Branch `feat/reskin-phase0` (NOT merged).

2026-06-22 (FIXED pin/lock/delete/tags) — They failed with "database disk image is malformed": the FTS5 `_au` trigger fired on every meetings UPDATE, so pin/lock/tags (non-indexed cols) hit the still-corrupt external-content index. Fix (`3098b2b`): scope the trigger to title/summary/transcript + `repair_fts()` rebuilds the index unconditionally at startup (the prior self-heal only ran during a backfill). Live DB integrity ok; 27 meetings intact; relaunch healed it. 20 cargo tests + tsc green. Temp click-tracer diagnostics reverted. **Pending user confirm.** Branch `feat/reskin-phase0` (NOT merged).

2026-06-22 (DEBUGGING — temp diagnostic in tree) — ⚠️ **`src/App.tsx` has a TEMP click-tracer (commit `<see git log: "TEMP">`) — REVERT before merge.** Pin/Lock/Delete/+Add-Tag still dead in the user's real Tauri WKWebView even after a full dev restart (NOT stale Fast Refresh). Identical code works in headless Chromium (Playwright + mocked invoke). Added an on-screen capture-phase click tracer to learn, from the real webview, whether clicks reach the buttons. **Waiting on the user to click each + report the amber bar.** See [HANDOFF.md](./HANDOFF.md).

2026-06-22 (live-review) — Reskin live-review in progress. Fixed: collapsible + smaller/squarer calendar; pushpin icon + pin/lock separator; lock `window.alert`→in-app notice; To-dos 4 tabs + "Not mine" assignee; Weekly sample placeholder; NoteViewer toolbar/Add-Tag + RecordingNotes stop wired. **Diagnosed the "dead header buttons" as stale React Fast Refresh** (props-interface change → old component kept in memory; code verified working via Playwright + mocked Tauri invoke) → fixed by restarting `tauri dev` (fresh build). **Pending: user re-test in the fresh window**, then remaining polish + calendar roster diagnostic (last). Commits `34d6101`, `e920898`. Branch `feat/reskin-phase0` (NOT merged).

2026-06-22 (early am) — **Verbatim reskin DONE + a critical FTS fix.** User confirmed the dark palette, then asked to reskin the app to match the prototype **verbatim** (fonts/calendar/tags/Settings/all views) by **parallel delegation**, and to fix the init self-heal first. Done: **FTS5 self-heal** (`49929f9`, fixes a startup-brick the M1/M2 backfills exposed — 19 cargo tests + E2E vs the real corrupt DB; live DB healed, 27 meetings intact, backups in `~/Library/Application Support/meeting-note-taker/*.bak*/*.safety-*/*.healthy-*`); **full reskin** — self-hosted Inter + prototype `styles.css`→`src/prototype.css` (`6512724`), then **12 parallel agents** converted every component + `App.tsx` shell by hand (`ce6f865`), then wired the cross-file controls (`6dbccf7`). tsc+vite green; app runs live (user recorded a meeting in it). Branch `feat/reskin-phase0` (NOT merged). **Next: user live-review the whole reskin → fix flagged polish (TodosView 4 filters, modal sizing, Settings sub-cards, widget) → calendar roster diagnostic (last).**

2026-06-21 (pm) — **Merged the relay branch → `master` + pushed; shipped reskin Phase 0.** Fast-forwarded `feat/settings-providers-calendar` (28 commits) into `master` (`15962ae`) after re-verifying green (tsc · cargo · 103 pytest), pushed to origin. Then on new branch `feat/reskin-phase0`: **dark-glass theme tokens** (`795d2b8`) — flipped the inverted Tailwind `gray` ramp cream→dark (re-themes the whole app from one place, zero component edits) + additive accent/glass/font tokens + `:root` CSS vars + dark scrollbars; `tsc`+`vite build` green, compiled CSS confirms the flip. **Next per the user: live-smoke (dark palette + M1/M2), then calendar roster diagnostic last.** Reskin Phases 1-4 wait on the user eyeballing Phase 0 (the de-risk gate).

2026-06-21 — **All 5 relay tasks done + Claude-verified** on `feat/settings-providers-calendar` (not pushed): A LLM-provider (`6eca767`), B0 calendar plumbing (`12598aa`), C names-fix (`0ac424c`), B1 Google-OAuth (`77af3c1`), **EK macOS-EventKit calendar (`01df912`)**. Calendar = EventKit on macOS (zero sign-in) + Google OAuth for Windows. Everything compile-verified; **next is the user's live-smoke on a clean `npm run tauri dev`** (enable Apple Calendar, grant permission; try Grok/OpenRouter; names dedup), then merge.

2026-06-20 (earlier) — **Daily-use LLM server wired up.** First real `.dmg` run failed summarization (`Connection refused` — no LLM server running). Fixed: switched app to **`qwen3.6-35b`** (A3B MoE) + created a login **LaunchAgent** that autostarts `rapid-mlx serve qwen3.6-35b --port 8000` (the half-downloaded model resumed cleanly once `HF_HUB_DISABLE_XET=1` was added). Verified the app's exact summarize request returns clean structured JSON. User action: restart the app / set Settings model to `qwen3.6-35b`, then Re-summarize. Logged the "no friendly LLM-down prompt" gap in TODO.

2026-06-20 — **`Adversaria.dmg` built and verified end-to-end** (one-command `./scripts/build-dmg.sh`; .app launches → auto-spawns bundled MLX sidecar → kills on quit). Plus today: To-dos due-dates/assignees/Today view, FTS5 Ask retrieval, Adversaria rename + new icon. All green (tsc/cargo/75 pytest). **Next (per user):** speaker diarization, then semantic embeddings, then static-ffmpeg bundling for portability.
