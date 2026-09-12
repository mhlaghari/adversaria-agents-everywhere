# Lessons Learned

Non-obvious problems hit while building this project and how they were resolved.
Read this before debugging — your problem may already be solved here. Add to it
whenever you burn time on something a future contributor shouldn't have to.

Each entry: **Symptom → Root cause → Fix → Prevention.** Newest first.

## 2026-09-09 — An Ollama "warm-up" with a different `num_ctx` is a wasted load: the next real request reloads the runner

- **Symptom:** after `POST /copilot/warm` returned ok and `ollama ps` showed `qwen3.6:35b` resident with a 30 min keep-alive, the first copilot answer still took 6.95 s to its first sentence instead of the expected sub-second.
- **Root cause:** the warm-up called `client.chat` with `_ollama_options(2048)` while the answer path uses `_adaptive_num_ctx(...)` (16,384 floor on this Mac). Ollama keeps one runner per (model, num_ctx, …) and reloads when `num_ctx` changes, so the warm runner was discarded on the first real request. `ollama ps` shows the loaded CONTEXT column: 2048 after the bad warm-up, 16384 after the fix.
- **Fix (`python-service/src/summarizer.py` `copilot_warm`):** warm with `_ollama_options(_adaptive_num_ctx(0, use_model, client))`, i.e. exactly the options the answer path will send. Verified: first SAY sentence 0.71 s immediately after warm-up.
- **Prevention:** any preload must replicate the real call's runner-affecting options (`num_ctx`, model tag, thinking flag); check `ollama ps` CONTEXT after warming. The same applies to the summarizer versus copilot: they use different `num_ctx` sizes, so summarizing a meeting right before an interview question evicts the copilot's runner (the 4B summarizer and the 35B copilot are different models anyway, but two 35B calls with different `num_ctx` would thrash).

## 2026-09-08 — Copilot folder sources retrieve ONE paragraph per file by keyword only; write evidence as many small single-topic files

- **Symptom:** the founder wanted "every technical detail" of Adversaria fed to the Interview copilot as a document. A single long dossier would have been nearly useless: the copilot could only ever quote one 600-char slice of it, and short questions would never reach it.
- **Root cause (verified in code):** a folder `dir` source is walked to depth 3, 200 files, 200 KB each, `.md`/`.txt` only (`src-tauri/src/folder_sources.rs:15-18`); the title is the first `# ` line (`:126-135`); `folder_fts` ranks with `bm25(title×10, body×1)` over an OR of all question words (`storage.rs:1148,4158`); the folder tier runs only when the question yields two keywords of ≥4 letters or one of ≥7 (`copilot.rs:415-423`), so "What is RAG?" yields zero keywords and retrieves nothing; `excerpt_around_keywords` keeps the **single paragraph** with the most keyword occurrences, cut at 600 chars (`copilot_provenance.rs:46-75`), cloud passages capped at 1,000 bytes (`copilot_answer.py:230`); at most 3 passages; folder FTS scores max 0.75 while live notes/meeting/attachment tiers score 0.9/0.85/0.8 (`copilot.rs:617,653,684,894`); folder docs have no semantic tier; dedup keys on `(source_kind, source_id)`.
- **Fix:** the Adversaria dossier is 25 files, one topic each, `# Adversaria: <topic with the interviewer's words>` as the title, three self-contained paragraphs of 350 to 500 chars each with number, unit, date and caveat in the same paragraph, third person, in `~/Desktop/Adversaria Copilot Sources/adversaria/`. A retrieval simulation (keyword extraction + title-weighted ranking + best paragraph) over 34 questions was used to pick titles; six titles were changed so the intended file wins.
- **Prevention:** before writing any copilot source material, run the question through the gate and the excerpt rule. Titles carry the question's words; never rely on headings inside the body; never put a metric's caveat in another paragraph. The gate, tier-score and dedup gaps are slice 2 items (`.recon/interview-copilot-20260908/CONTRACT-2-interview.md` §1). Also found on the way: CLAUDE.md, ARCHITECTURE.md and ADR-010 still described macOS capture as ScreenCaptureKit; it has been a Core Audio process tap since 2026-08-13 (`9589e8c`). Code wins over docs; the three were corrected.

## 2026-09-05 — To-dos preview accepted; latent sizing/theme bug from Laghari theme gap; Codex notify installed

- **Symptom:** To-dos lanes overflowed/budged and date badges wrapped with low contrast (1.04:1) on light theme; extra AI column worsened it.
- **Root cause:** triage grid/metadata rules `60eaf61` (Jul 18) and date pastels `6512724` (Jun 22) were not converted when Laghari theme `de89f8f` (Aug 13) shipped — latent content-vs-container sizing + missing light-theme adaptation; exact first triggering task/release unproven.
- **Fix:** scoped `src/prototype.css` fix (equal `minmax(0,1fr)`, container-width AI, wrapping, nonshrinking badges); fixture visual run 50/50 width/theme/AI passed (no overflow, contrast 5.06:1). Parent installed Codex prefs `~/.codex/config.toml` (`approval never`, `danger-full-access`, notify wrapper → Sky turn-ended + `task-complete.wav` `HCn94mNuICk` 7.11–7.84→0.73s PCM16 48kHz, byte-equal); 8 tests PASS, 3-key TOML preserved, backup 20260905T115736; new sessions needed; playback not claimed heard; one installer review round; no release/rebuild/commit/DB.
- **Prevention:** when adding a theme, grep and convert all badge/pastel rules; keep behavioral tests plus a width/theme/AI fixture visual matrix.

## 2026-09-04 — Windows CI failed one Rust test because a folder-excerpt heading used the OS path separator

- **Symptom:** `workspace_runs::tests::folder_excerpt_prioritizes_root_readme` panicked on
  `windows-latest` only (`Option::unwrap()` on `None` at `excerpt.find("## docs/guide.md")`);
  macOS green. Blocked the 0.3.83 public sync (PR #30).
- **Root cause:** the nested candidate's `relative_path` came from
  `Path::strip_prefix(..).to_string_lossy()`, which renders `docs\guide.md` on Windows.
- **Fix:** `b86e912` joins `components()` with `/` (the excerpt is LLM-facing text and
  must be identical on every OS). Cherry-picked onto `release/0.3.83`; PR #31 green.
- **Prevention:** never put an OS path into text that is compared or fed to a model;
  render with `/` explicitly. Any test that greps a path in generated text is a
  Windows-only failure waiting to happen.

## 2026-09-04 — Three worker traps in one night (Antigravity silent death, Codex repo-wide `ruff format`, Muse dynamic-import hack)

- **Symptom:** (a) the Rust worker on Antigravity exited within a minute with a 0-byte
  result and 0-byte stderr, leaving 320 lines of partial edits; (b) the Python worker
  on Codex reformatted 29 unrelated files; (c) the frontend worker on Muse replaced the
  wrappers it needed with `import("../lib/tauri")` + `as unknown as {…}` casts to dodge
  the existing `vi.mock` factories.
- **Root cause:** (a) transient agy crash (a 30 s `stunt exec "reply ok"` probe passed
  right after); (b) the spec listed `ruff format --check .` as a gate although the repo
  only enforces `ruff check`, so the worker "fixed" the tree; (c) the spec did not say
  how to satisfy the test mocks.
- **Fix:** (a) `git checkout -- <its files>`, relaunch on agy after the probe; (b)
  keep-list revert loop over `git diff --name-only python-service`, then one feedback
  round to strip formatting hunks from the in-scope files; (c) one feedback round:
  static imports + extend the mock factories.
- **Prevention:** specs name the exact gates the repo enforces ("ruff check only, do
  not run formatters"); frontend specs say "static imports; extend the `vi.mock`
  factories"; launch workers detached (`nohup … &` + a Monitor on the result file)
  because the Bash tool caps at 10 min; probe a backend before relaunching on it;
  read every diff — each review round found a real bug (egress duplication, DB I/O
  under a mutex, cloud model leaking into the local path, plaintext dev key file).

## 2026-09-03 — A stunt worker reverted uncommitted doc edits in the shared checkout

- **Symptom:** HANDOFF/STATUS/TODO edits made at 07:20–07:30 while two
  workers were building in the same checkout were gone afterwards; `git
  status` clean, no stash, no reflog entry.
- **Root cause (inferred):** a worker ran `git checkout`/`git restore` to get
  the "clean tree" its spec described, despite the "no git commands that
  write" rule. Untracked files survived; tracked, uncommitted edits did not.
- **Fix:** re-applied the edits from the session transcript.
- **Prevention:** commit docs before launching workers, or write them after
  the workers finish; never rely on uncommitted tracked edits surviving a
  worker run. Specs should say "the tree may have uncommitted docs; leave
  them" rather than "tree clean".

## 2026-09-02 — Rust unit tests silently wrote into the founder's REAL meetings database

- **Symptom:** after a worker's `cargo test` runs (and one of Claude's), the
  installed app showed 33 new meetings — "Council Meeting", "Meeting 1…4",
  "Host", "Long Meeting"… (ids 260–292) with 51 action items and 21 attachments.
- **Root cause:** the new tests called `crate::storage::init_db(false)` and
  `connect_for_sync()`, which open `db_path()` = `config::app_data_dir()/
  meetings.db` — the live app-support DB. Nothing in `storage.rs` redirects
  that path under `cfg(test)`; every existing test that needs a DB uses
  `Connection::open_in_memory()` with `_on(conn, …)` helpers instead.
- **Fix:** `_on` variants for the storage helpers the new code needs, a
  `#[cfg(test)] in_memory_db()` that runs the real `create_tables`, tests
  rewritten on it; the junk rows are deleted by id range (backup first:
  `meetings.db.bak-pre-testrow-cleanup-*`).
- **Prevention:** never call `init_db`/`connect*` from a test; run
  `ADVERSARIA_DATA_DIR=$(mktemp -d) cargo test` so any stray path-based access
  lands in a scratch dir; after a worker's cargo run, compare
  `select max(id), count(*) from meetings` on the real DB (readable with
  `sqlite3 "file:…/meetings.db?immutable=1"`).

## 2026-09-02 — An attached previous meeting did nothing visible; the 4B notes model fabricates "Resolved"

- **Symptom:** the founder attached a prior meeting while recording; the notes
  showed "Follow-ups: None mentioned" and no sign the attachment existed.
- **Root cause (two parts):** (1) `attached_context_for` sent the prior
  meeting's summary with the prompt line "NEVER treat it as something said in
  this meeting" — measured 0/6 follow-up mentions; enriching the context with
  the open items changed nothing (0/3). (2) Once instructed, `qwen3.5:4b`
  resolved explicitly-closed items but marked UNMENTIONED items "Resolved"
  with invented evidence in ~50% of runs on an unrelated transcript, dropped
  trailing items, and wrote the status after the item text
  (`[P1] <item> — Done — "…"`) with elided quotes (`"… … and the hiring
  managers"`). Probe: `.recon/recon-agy-context-probe.md` (git-excluded).
- **Fix:** structured `prior_meetings` (open `action_items` only) + an explicit
  `PRIOR MEETING FOLLOW-UP` instruction + `_ensure_followup_section`, which
  rebuilds the section deterministically: one bullet per item in order,
  status keyword found anywhere after a separator (last match wins),
  Done/Discussed kept ONLY when every ellipsis-separated fragment of the
  model's double-quoted evidence appears verbatim in the transcript, else
  "Still open"; heading "Follow-up from <title>" (generic when the title
  contains a to-do-extractor keyword). Verified on the real model: discussed
  items → "Discussed" with a grounded quote; unrelated transcript → all
  "Still open", zero fabrications.
- **Prevention:** for anything a small local model asserts about the world
  (done/not done, dates, names), require a verbatim quote and check it in
  code; never let a "background only" instruction carry a feature the user is
  supposed to see.

## 2026-09-02 — The notary credential is unreadable while the Mac is LOCKED; retry instead of rebuilding

- **Symptom:** the 0.3.83 release build passed the stage-0 credential
  pre-flight (`notarytool history` listed 0.3.82 Accepted), spent ~35 min
  freezing and signing, then stage 7 failed 4× with
  `No Keychain password item found for profile: adversaria-notary`. A direct
  `notarytool history` afterwards failed the same way, in 2 s, with no hang.
- **Cause (confirmed by the recovery):** the founder had locked the screen and
  walked away between pre-flight and stage 7 (`CGSSessionScreenIsLocked` was
  set in `CGSessionCopyCurrentDictionary`). `notarytool` keeps the profile in
  the data-protection keychain, whose items are unreadable while the session
  is locked, and it reports that as a *missing* profile. Nothing was revoked:
  a detached loop retrying every 2 min succeeded on try 132 at 07:33, the
  moment the Mac was unlocked in the morning, and the identical DMG was
  Accepted. This is the third distinct cause behind that one message (see the
  2026-08-05 and 0.3.73/0.3.75 entries): revoked password, keychain flap
  under load, and now a locked session.
- **Fix that worked:** do not rebuild. Poll `xcrun notarytool history
  --keychain-profile adversaria-notary` until it succeeds, then run the
  script's stage-7 tail by hand on the intact DMG: `notarytool submit --wait`
  → `stapler staple` → `stapler validate` → `spctl --assess --type open
  --context context:primary-signature` → `node scripts/release-provenance.mjs
  <dmg> provenance-beta.json <app.tar.gz> <app.tar.gz.sig>` → `cp` to the
  stable name `Adversaria-macos-arm64.dmg` and `stapler validate` the copy.
- **Prevention:** start a release freeze only when the Mac will stay unlocked
  for the next hour, or run the build with the founder present at stage 7.
  If the failure lands anyway, treat "No Keychain password item" as
  "unreadable right now", check the lock state, and retry before touching
  credentials.

## 2026-09-01 — "sherpa hosts Moonshine streaming" was a research assumption; the probe said otherwise

**Symptom.** The 09-01 live-captions decision named Moonshine as the streaming
engine inside sherpa-onnx. Building on it would have shipped nothing that streams.

**Root cause.** Web research conflated Moonshine's "streaming-friendly" training
with a streaming API. `sherpa_onnx 1.13.3` exposes `from_moonshine`/`from_moonshine_v2`
on `OfflineRecognizer` only; its online factories are transducer/zipformer2-CTC/
NeMo-CTC/paraformer. Verified in one line:
`python -c "import sherpa_onnx;print([n for n in dir(sherpa_onnx.OnlineRecognizer) if n.startswith('from_')])"`.

**Fix.** An empirical probe (Antigravity, `.recon/probe_streaming.py` +
`probe_offline_tail.py`, memo `recon-agy-sherpa-streaming.md`) measured both
designs on the same clips; Moonshine v2 re-decoding the unconfirmed tail won on
quality (casing, punctuation, ~6% vs ~20% WER) at 12–49 ms per decode. Two more
non-obvious findings from the same probe/build: (1) Moonshine v2's ORT export
crashes on inputs ≥ 10 s (`axis == 1 || axis == largest was false ... 3 by 800`)
— cap every decode at 8 s; (2) `model_setup._load_manifest` only counted
`.safetensors/.gguf/.bin/.onnx` as weights, so the `.ort` pin was rejected at the
manifest stage exactly as the Cohere `.onnx` pin was on 08-14 — the predicate and
`_CACHED_WEIGHT_SUFFIXES` now include `.ort`. (3) On 0.5–2 s mid-word tails the
decoder loops a phrase; `is_repetition_loop` misses loops after a sane prefix, so
the preview path trims to the prefix instead.

**Prevention.** Before committing to a model/runtime pairing, introspect the
installed API and run a 30-minute probe on real audio; put the numbers in the
ADR. Any new weight-file extension must be added to BOTH manifest predicates in
`model_setup.py` (and `transcriber._WEIGHT_SUFFIXES` if the cached check should
see it) — grep for `.onnx` to find every site.

## Public CI clippy is newer than the local toolchain (2026-08-30)

`cargo clippy --all-targets -- -D warnings` was CLEAN locally (rustc/clippy
1.96) but the public mirror's quality gate failed with three
`unnecessary use of clone to create a slice from a reference` errors in
`project_overview.rs` tests — a lint that ships in a newer clippy than this
box has. Cost: one failed sync PR (#28), a test-only fix commit (`eb6f33a`),
and a second PR (#29). Lesson: local clippy passing does not clear the public
gate; when a sync PR fails on clippy, read the CI log for the exact lines
(the suggested fix is usually verbatim-appliable) rather than chasing local
repro. Test-only lint fixes do not invalidate an in-flight release build.

## 2026-08-30 — A stale native window can make a verified frontend fix look absent

**Symptom.** Project deletion existed in code and passed its tests, but the open
Adversaria window still showed no project menu, making the feature appear broken.

**Root cause.** The Vite/Tauri development process had died during a Rust
rebuild, while its already-open native webview remained on screen. The window
looked like the running app but could no longer receive the rebuilt frontend.

**Fix.** Confirmed the dev processes were gone, restarted `npm run tauri dev`,
then exercised the real path: project `⋯` → Delete project → named in-app
confirmation. The confirmation was cancelled so user data stayed untouched.
The project `⋯` control was also made visible at rest instead of hover-only.

**Prevention.** Before declaring a native UI change absent, verify that both
Vite and the Tauri process are alive and that the window has reloaded the current
bundle. Green unit tests prove the code path; they do not prove an orphaned
window is showing that code.

## 2026-08-28 — Prompt-template commits can silently break the Python suite

**Symptom:** `uv run pytest` failing on master (test_config/test_summarizer
assertions), discovered only when a later task's verification gate ran it.
**Root cause:** commit `7353380` rewrote every template in
`python-service/prompts/` (headings `**"…"**` → numbered `1. "…"`; `Owner:`
literal → `Me:`/speaker-label rule), but the pre-commit verification ran only
`cargo test` + `vitest` + `tsc` — pytest was skipped because the change "was
just prompts". The prompt files ARE code: tests pin their exact shapes because
storage.rs's to-do extractor depends on them.
**Fix:** test assertions rewritten to pin the NEW template contract (same
coverage: actionable-heading regex match, `Me:` bullet shape, no literal
"Owner").
**Prevention:** any change under `python-service/` — prompts included — runs
`uv run pytest` before commit. The suite is ~1.4s; there is no excuse.

---

### "Apps bounce and never open" = macOS `syspolicyd` out of file descriptors — 2026-08-23

**Symptom cluster, none of which looked related:** draw.io (and any other
not-yet-running third-party app) bounced in the Dock and never showed a window;
Ollama "wedged" (its `llama-server` runner never came up; `ollama ps` empty,
embed calls hung); `uv run pytest` and `.venv/bin/ruff --version` hung while
`python -m pytest` worked; `spctl -a` failed with "Too many open files".

**Diagnosis that worked:** `sample <pid> 3` on the hung app → main thread 100 %
inside `dyld … mapSegments → fcntl`. That `fcntl` is the kernel registering the
binary's code signature (AMFI) which waits on `syspolicyd`. `log show --predicate
'process == "syspolicyd"'` showed `UNIX error exception: 24` (EMFILE) and
`Failed to generate SecStaticCode … error: 100024` on every request: the
Gatekeeper daemon had leaked its descriptors (38 % CPU, running since 04:52),
so every fresh signature assessment hung. Launching a second unrelated app and
sampling it the same way confirmed it was systemic.

**Fix (verified 2026-08-23 11:32):** `sudo killall -9 syspolicyd amfid` (launchd
respawns both); within 90 s `ruff --version` answered, draw.io opened the
`.drawio` in a window, and an Ollama embed returned in <1 s. A reboot also
works. Not fixable from a non-root session; the `!` shell in Claude Code has no
TTY for sudo, use Terminal.app.

**Update, 2.5 h later (08-23 14:05):** the restarted `syspolicyd` leaked again
(54k `exception: 24` lines in 5 min, plus `syspolicy.exec: failed to call
driver: 0x3`), so `killall` is a band-aid, not a fix. Ollama's runner launch
timed out again ("Load failed" after 5 min) and `import mlx.core` hung the
same way. **Reboot** when this recurs; if it survives a reboot, it is an OS
bug on macOS 26.5 to report with `sudo sysdiagnose`. Heavy local churn of
freshly built/installed binaries (cargo test binaries, pip/uv venvs with
thousands of dylibs) is the likely trigger on this box.

**How to recognise it next time:** any *newly executed* signed binary hangs
before printing anything (even `--version`), while already-running processes
are fine. Check `pgrep -x syspolicyd` uptime/CPU and its log before blaming the
app, the file, or the network. Do not clear app caches or reinstall first.

**Side lesson for the Workspaces runner:** a run must never block on a service
that can hang: the 8-second `tokio::time::timeout` around embed calls
(delegation 10) came out of this day.

### Holding Screen Recording SUPPRESSES the System Audio Recording prompt — the tap is silently denied — 2026-08-17
- **Symptom:** the founder's first shipped-0.3.78 recording ended with
  "No system audio reached the encrypted spool": mic committed 77 s fine,
  `system.records` never received one frame. No macOS prompt ever appeared.
  Reproduced identically on a second attempt. Nothing in our logs — the cpal
  tap stream builds, `play()` succeeds, and zero callbacks ever fire.
- **Root cause:** the Core Audio process tap needs the **System Audio
  Recording** TCC grant (`kTCCServiceAudioCapture`), and macOS **does not show
  the consent prompt to an app that already holds Screen Recording** — it
  silently denies instead (cpal PR #894 documents exactly this). Every
  SCK-era install holds Screen Recording, and until 0.3.79 the wizard
  *requested* it, manufacturing the broken state. Dev runs never hit it:
  unbundled binaries inherit the terminal's TCC identity, which had the tap
  permission from Phase-0 harness testing. Unified-log signature of the
  failure: `HALS_MultiTap::register_autostart_context` appears, but
  `IOWorkLoopInit … starting` for the `com.cpal.LoopbackRecordAggregateDevice`
  never does. (Also learned: with `TapAutoStart`, a *granted* tap delivers
  ZERO callbacks until some process plays audio — ~1.4 s after sound starts,
  proven with a rebuilt Phase-0 harness — so "denied" and "nothing was
  playing" are indistinguishable from outside. Only a probe that plays real
  audio can tell them apart; there is NO public check/request API.)
- **Fix (user):** System Settings → Privacy & Security → Screen & System
  Audio Recording → **System Audio Recording Only** → add/enable Adversaria
  (the **+** button; the app may not be listed until added manually).
  Founder-verified working. **Fix (code, 0.3.79):** real-audio probe
  (`audio::probe_system_audio`, quiet 220 Hz tone → any nonzero tapped
  sample = granted), probe-backed permission model + Settings Permissions
  card, wizard no longer requests Screen Recording, mic-only recordings
  survive as pending meetings instead of hard-failing.
- **Prevention:** never gate the tap on Screen Recording state; treat "tap
  built + playing" as meaningless — only heard-audio proves the grant. Any
  support report of "no system audio, mic fine, no prompt" on an updated
  install is this. `tccutil reset ScreenCapture <bundle-id>` does NOT reset
  the audio-capture grant; the System Settings toggle is the remedy.

### `uv sync` without `--extra dev` silently guts the dev env — and pytest falls back to miniconda — 2026-08-12
- **Symptom:** after `uv sync --extra mlx` (installing the new qwen3-asr-mlx
  runtime), `uv run pytest` failed collection with
  `ModuleNotFoundError: No module named 'faster_whisper'` even though
  faster-whisper is a main dependency and `uv run python -c "import
  faster_whisper"` WORKED. Separately, ruff jumped 0.15.21 → 0.16.2 and
  reported 41 brand-new complaints across untouched code.
- **Root cause:** the dev tools live in the `dev` *extra*
  (`[project.optional-dependencies]` in `python-service/pyproject.toml`), so a
  sync that names only `--extra mlx` REMOVES pytest/ruff/scipy/httpx2 from the
  venv. With no venv pytest, `uv run pytest` falls through PATH to
  **miniconda's global pytest**, whose interpreter has none of the project's
  packages — the giveaway is `miniconda3/` in the traceback paths. A hand
  `uv pip install ruff` then grabbed the newest ruff, not the locked one, and
  left half-pruned dist-info metadata (`iniconfig` METADATA missing).
- **Fix:** `uv sync --extra mlx --extra dev` is the canonical macOS dev sync —
  it reconciled everything in one shot (506 passed, ruff 0.15.21 clean).
- **Prevention:** always name BOTH extras when syncing on the Mac; if pytest
  ever errors with miniconda paths in the traceback, the venv lost its dev
  extra — resync, don't `uv pip install` one-offs.

### Verifying `num_ctx` really applied: `ollama ps` lies if a runner is already loaded — 2026-08-11
- **Symptom:** after wiring adaptive `num_ctx`, a live `/summarize` against
  `muse-glimmer:30b-mlx` looked like the new window was ignored — `ollama ps`
  reported `CONTEXT 131072` (the model default), not the computed 28672. It also
  took 4m17s and the repair tier fired, exactly like the pre-fix incident.
- **Root cause:** a runner loaded earlier in the day was still resident at
  131072, and Ollama **reuses a loaded runner rather than reloading it** for a
  request whose `num_ctx` is smaller. Nothing was wrong with the code.
- **Fix / how to verify properly:** `ollama stop <model>` first, then issue the
  request, then `ollama ps` immediately. With a clean runner it reported
  `CONTEXT 28672` at 22 GB / 1m52s (vs 131072 at 26 GB / 4m17s) — proof both
  that the option applied and that right-sizing is materially cheaper.
- **Prevention:** never conclude "the option was ignored" from `ollama ps`
  without unloading first. The independent check is the runner's own SIZE — a
  smaller context is a visibly smaller resident runner.

### Ollama `/api/show`: the context field is architecture-PREFIXED, and the python client hides it — 2026-08-11
- **Symptom:** reading a model's real maximum context to bound `num_ctx`. There
  is no `context_length` key, and `response["model_info"]` raises `KeyError`.
- **Root cause (verified live, Ollama 0.32.7 / ollama-python 0.6.2):** the key is
  `<architecture>.context_length`, where the architecture comes from
  `model_info["general.architecture"]` — `qwen35.context_length` (262144),
  `muse_glimmer.context_length` (131072), `llama.context_length` (8192). The
  prefix is **not derivable from the model tag**: `qwen3.5:2b` → `qwen35` but
  `qwen3.5:0.8b-mlx` → `qwen3_5`. And the python client returns a
  `ShowResponse` whose attribute is **`.modelinfo`** (no underscore), not a
  `["model_info"]` subscript.
- **Fix:** read `general.architecture` → `f"{arch}.context_length"`, fall back to
  scanning for any key ending in `.context_length`; accept both
  `.modelinfo` and a raw `{"model_info": …}` dict. Any failure returns `None` so
  the bound simply drops rather than failing the summary
  (`summarizer.py::_model_max_ctx`).
- **Prevention:** `tests/fixtures/ollama_show.json` holds real captured responses
  for three architectures, so the parser is pinned to the API's actual shape.
  Re-capture with
  `curl -s localhost:11434/api/show -d '{"model":"qwen3.5:2b"}'` if Ollama
  changes. Do not write this parser from memory — the naming is not guessable.

### The Python service never configures the root logger, so app INFO is invisible — 2026-08-11
- **Symptom:** `uvicorn … --log-level info` shows request lines and WARNINGs, but
  **no** `logger.info` from `src.*` — e.g. `Summarizing transcript: …` and the
  new `Context sizing: adaptive: … (bound by prompt)` line never appear.
- **Root cause:** nothing in `python-service/src/` calls
  `logging.basicConfig`/`dictConfig`, so the root logger sits at its WARNING
  default. `--log-level` configures uvicorn's own loggers only.
- **Workaround when you need to see them:** launch through a wrapper —
  `uv run python -c "import logging,uvicorn; logging.basicConfig(level=logging.INFO); uvicorn.run('src.server:app', host='127.0.0.1', port=9877)"`.
- **Prevention:** this silently defeats any "diagnosability without telemetry"
  logging we add. One `basicConfig` call at service startup fixes it —
  **still open** (see HANDOFF next-step list).

### A release build leaves a frozen sidecar that SHADOWS the source service in dev — 2026-08-06
- **Symptom:** a brand-new Python endpoint (`POST /generate-template`) worked
  perfectly by `curl` against the dev service on :9876, and did nothing at all
  from inside `npm run tauri dev`. The uvicorn access log showed ZERO requests
  from the app.
- **Root cause:** `launch_sidecar` (commands.rs) spawns the bundled service
  whenever `resource_dir()/adversaria-service/adversaria-service` exists, and
  repoints the HTTP client at that dynamic port. In dev the resource dir is
  `src-tauri/target/debug/`, and **the release build had populated it**. So dev
  spawned the FROZEN 0.3.74 service on a private port (`[sidecar]
  adversaria-service spawned on port 52032`) — a binary compiled before the new
  endpoint existed — and never touched the source service on :9876. The app got a
  404 from its own stale sidecar.
- **This is the freeze-vs-dev collision inverted.** The known form is that a
  re-freeze WIPES `python-service/dist/adversaria-service`, which dev's build.rs
  needs. This is the opposite: the freeze CREATES
  `target/debug/adversaria-service`, and from then on dev silently runs frozen
  Python instead of your working tree. Every Python edit appears to have no
  effect, with no error anywhere.
- **Fix:** `mv src-tauri/target/debug/adversaria-service{,.frozen-<version>}` and
  restart dev; `exe.exists()` then fails and dev falls back to the manually-run
  uvicorn per the dev runbook.
- **Prevention:** after any `build-dmg.sh` run, assume dev is talking to frozen
  Python until you prove otherwise. `grep sidecar` the dev log — a line reading
  `[sidecar] adversaria-service spawned on port …` in a DEV session means your
  Python changes are not loaded. Consider gating that spawn on
  `!cfg!(debug_assertions)` so a debug build never adopts a frozen sidecar.
- **What made it expensive:** the 404 surfaced as a message rendered ~500 px below
  the button that triggered it, past a 300 px textarea, so the user saw a button
  that did nothing. Feedback must render next to its control; see the same-day
  fix in `NotesSection`.

### The notary credential FLAPS under load, and notarytool blames the wrong thing — 2026-08-07
- **Symptom:** two release builds (0.3.73, 0.3.75) ran the full ~hour of freezing
  and signing, reached stage 7, and died with
  `Error: No Keychain password item found for profile: adversaria-notary`.
- **What it is NOT:** the credential was not missing and not revoked. Minutes after
  the 0.3.75 failure the identical command succeeded (`exit=0`, 1.0 s) with nobody
  touching the keychain. The build script never touches the keychain either — it
  only calls `notarytool submit`.
- **Root cause (best supported):** a transient failure to read the
  data-protection keychain, reported by `notarytool` with the same message it uses
  for a genuinely absent profile. Both failures landed **immediately after signing
  hundreds of nested Mach-Os**, on a machine at load average ~10 with 24 days
  uptime. The same credential works on an idle machine, which is why every
  standalone `notarytool submit` in this project has succeeded while two in-build
  submits failed.
- **Two wrong theories, recorded because both were plausible and cost time:**
  (1) *a background process cannot reach the keychain* — refuted when a foreground
  run failed too; (2) *the app-specific password was revoked* (it had been pasted in
  plaintext and revocation was advised) — refuted when the credential came back on
  its own. `notarytool`'s message invites both.
- **Fix:** `scripts/build-dmg.sh` now (a) proves the credential works at stage 0,
  before an hour of signing, and (b) **retries the submit up to 4 times with
  backoff**, because a credential that passes at stage 0 can still flap at stage 7.
  The failure message tells you the signed DMG is intact and to notarize it
  directly rather than rebuild.
- **Prevention:** never let one unlucky Keychain read discard an hour of signing.
  And when a tool's error names a *missing thing*, check whether the thing is
  actually missing before acting on the message — twice here it was present.

### A revoked app-specific password silently destroys the notary keychain profile — 2026-08-05
- **Symptom:** mid-release, `build-dmg.sh` completed all seven stages — signed
  app, signed 882 MB DMG, signed updater artifact — then died at notarization
  with `Error: No Keychain password item found for profile: adversaria-notary`.
  The same profile had worked ~40 minutes earlier in the same session
  (`notarytool history` listed 0.3.72 as Accepted).
- **Root cause:** the account's app-specific password had been revoked. Once the
  stored credential no longer validates, `notarytool` reports the profile as
  missing rather than as unauthorised — two very different-looking errors for one
  cause. `security` cannot see the item either way: notarytool stores it in the
  data-protection keychain, which `security dump-keychain` and
  `find-generic-password` do not search. So "the profile is gone" and "the
  password is dead" are indistinguishable from the outside.
- **Misdiagnosis worth avoiding:** the failure first appeared in a background
  build, so the obvious theory was that a detached process could not reach the
  login keychain. Re-running `notarytool history` in the foreground reproduced
  it, killing that theory. Then `Xcode`'s recorded Apple ID
  (`mhlaghari@gmail.com`) suggested `NOTARIZATION.md`'s
  `hamza@lagharilabs.com` was stale — also wrong; the doc was right, and Xcode
  simply holds a different personal account. Two plausible theories, both wrong,
  because the real variable was the password.
- **Fix:** generate a fresh app-specific password and re-run
  `xcrun notarytool store-credentials adversaria-notary --apple-id … --team-id
  4MY4PH5PHC --password '…'`. The interactive prompt swallows pastes silently in
  some terminals, which cost two failed attempts — pass `--password` explicitly
  when the prompt appears to do nothing, then clear it from shell history.
- **Prevention:** the release depends on a credential that expires out from under
  you with no warning and a misleading error. Prefer an **App Store Connect API
  key** (`--key/--key-id/--issuer`): a `.p8` is not revoked when the Apple
  Account password changes. And run `xcrun notarytool history --keychain-profile
  adversaria-notary` as a pre-flight BEFORE starting an hour-long build, not
  after.

### The stable-named DMG is a separate copy, so a build that dies late ships the previous version — 2026-08-05
- **Symptom:** after notarization failed, `Adversaria-macos-arm64.dmg` on disk
  was still 0.3.72 (881,689,222 bytes) while the versioned
  `Adversaria-0.3.73-beta-macos-arm64.dmg` was correct.
- **Root cause:** `build-dmg.sh` copies the versioned DMG to the stable name
  only AFTER notarization+stapling (deliberately, so the copy carries the
  ticket). A failure at stage 7 leaves the stable name pointing at the last
  successful release. `publish-release.sh` uploads that stable name, because the
  website links `…/releases/latest/download/Adversaria-macos-arm64.dmg`.
- **Fix:** regenerate the copy from the stapled artifact before publishing, and
  confirm with `xcrun stapler validate` on the copy itself.
- **Prevention:** when resuming a release by hand after a late-stage failure,
  never assume the stable-named artifact matches the version you are shipping —
  compare byte sizes against the versioned DMG. Publishing would otherwise
  advertise 0.3.73 in the manifest while serving 0.3.72 to every human visitor.

### A CI health-check gate must report why it failed, or it just blocks releases — 2026-08-05
- **Symptom:** the newly added "Smoke the frozen ML service" step failed the
  0.3.73 Windows build at 181 s with `did not answer /health within 60 seconds`,
  while its own captured log showed `Application startup complete` and
  `Uvicorn running on http://127.0.0.1:52887`.
- **Root cause of the ambiguity:** the loop was 60 attempts × (1 s sleep + 2 s
  request timeout) — a budget of ~180 s that the message described as 60 s — and
  it logged neither the port it chose, nor elapsed time, nor whether the port was
  even open. `src/server.py` filters `/health` out of the access log
  (`_ACCESS_LOG_POLL_FILTER`), so the service's own log cannot confirm whether
  requests arrived. Nothing in the evidence distinguished "booted too slowly"
  from "bound but erroring" from "wrong port".
- **Honest status:** still unexplained. The identical build on re-run answered in
  **15 s**, which refutes the slow-cold-start theory that seemed obvious. A port
  collision between the reservation being released and the service binding it is
  the leading remaining candidate.
- **Fix:** deadline-based 8-minute budget; echo the chosen port; report elapsed
  seconds on success; on failure probe the port with a `TcpClient` to separate
  "never bound" from "bound but failing" and include the last request error.
- **Prevention:** a gate that can fail a release must emit enough to diagnose
  itself on the first failure. Also note the gate passes on
  `status: degraded` — correct for CI, which has no Ollama or models, but it
  proves only that the service binds and answers, not that transcription works.

### A release workflow that has never run is a stack of latent failures — 2026-07-29
- **Symptom:** the first-ever dispatch of `release-windows.yml` (written 07-27,
  never executed) took FIVE rounds to produce an installer, ~40 min per round.
- **Root causes, in the order the runs peeled them:** (1) cargo gates before
  the sidecar freeze — tauri-build refuses on a missing bundle resource (the
  exact bug quality.yml fixed on 07-25; the fix was never mirrored); (2)
  updater-artifact signing requires TAURI_SIGNING_PRIVATE_KEY, which only
  exists on the macOS release machine; (3) a bash-syntax fallback in a step
  whose default shell is PowerShell; (4) `shell: bash` breaking openssl-sys'
  vendored build via Git-Bash's broken core_perl ("BEGIN failed" in
  IPC/Cmd.pm) — the compile only works under the default PowerShell.
- **Fix:** PRs #6–#9 on the public repo (stub before gates; installer-only
  fallback when no signing key, written in native PowerShell). Run
  30446906346 produced `adversaria-windows-beta-*` (85 MB).
- **Prevention:** dispatch every new workflow once BEFORE you need it — CI
  that has never run is untested code with a 40-minute compile loop. And on
  Windows runners, changing a step's shell changes the toolchain (perl, PATH),
  not just the syntax.

### The progress bar measured the wrong filesystem stage — 2026-07-28
- **Symptom:** model downloads showed ~5% for half an hour, then jumped to
  done. Users assumed a hang and quit — the exact churn moment of first-run
  setup.
- **Root cause:** `_downloaded_bytes()` stat'd `snapshots/<rev>/<name>`, but
  huggingface_hub streams into `blobs/<etag>[.<uuid8>].incomplete` and only
  materializes the snapshot entry when a file COMPLETES. Small config files
  finished early (the ~5%); the multi-GB weight shard contributed nothing
  until it was done. hf_hub ≥1.19 uses the process-unique `.<uuid8>.incomplete`
  form (huggingface_hub#4228); older caches hold the plain form; both were
  present in this machine's real cache.
- **Fix (`22e7e83`):** count each expected file through exactly one path,
  probing snapshot → `blobs/<sha256>` → `blobs/<sha256>*.incomplete` (largest,
  capped at manifest size). LFS blob names ARE the manifest sha256. Measured on
  a live cache: 32 MB counted → 1.77 GB counted.
- **Prevention:** when progress "sticks then jumps", suspect the measurement
  before the transfer — find where the library ACTUALLY writes bytes (read its
  source at the installed version) and measure there. A progress metric that
  only moves on completion of whole units is a completion counter, not a
  progress bar.

### "Unknown model profile: ollama:<tag>" — one id→model map, four gates, fixed one at a time — 2026-07-27
- **Symptom:** picking an Ollama model in setup failed with
  `Unknown model profile: ollama:qwen3:14b` / "The selected local model could not
  be started." This was the **fourth** consecutive failure in the same feature,
  each one a different gate rejecting the same id.
- **Root cause:** `setup::profile_alias()` is the single id→model-name mapping the
  whole app funnels through, and it knew only the three pinned MLX ids
  (`Option<&'static str>`, a `match` with `_ => None`). Four call sites gate on
  it — `registration::complete_step`, `registration::set_selected_model_profile`,
  and two "is a local model configured?" checks in `commands.rs`/`lib.rs`. Fixing
  `setup::start` and `pinned_snapshot` in earlier rounds left every one of them
  still rejecting Ollama ids.
- **Fix:** teach the **mapping itself**, not the callers. `profile_alias` returns
  `Option<String>` (an Ollama tag is discovered at runtime, so it cannot be
  `'static`) and resolves `ollama:<tag>` → `<tag>`. `downloadable_profile` then
  needs an explicit `ollama:` exclusion, since it previously inferred
  "downloadable" from `profile_alias` being `Some`. 4 new tests.
- **Prevention / notes:**
  - **When several gates reject the same value, fix the shared predicate, not the
    gates.** Three rounds were spent patching call sites of a function whose own
    domain was wrong.
  - Audit by grepping every use of the validator (`profile_alias`,
    `pinned_snapshot`, `downloadable_profile`) before declaring it fixed — all 8
    sites were checked this time, which is what should have happened in round one.
  - A predicate returning `Option<&'static str>` is a hint that its domain is a
    closed set. Widening the domain to runtime-discovered values is a **signature**
    change, and the compiler then finds the call sites for you.

### A resumed setup replays a model choice the machine can no longer honour — 2026-07-27
- **Symptom:** after installing a build that fixed the Apple-only local engine,
  setup **resumed at step 6/7 and still failed** with "Managed Rapid-MLX is
  currently available on Apple Silicon only."
- **Root cause:** the fix keyed off an `ollama:` id prefix — but onboarding
  persists `selected_model_profile` in the database, and this user had completed
  the model step on the *old* build, so their stored id was `qwen-27b-quality`.
  On resume the frontend restored it verbatim (`persisted || recommended`) and
  handed it to `setup::start`, which fell straight through the prefix check into
  the Rapid-MLX path. **A fix gated on the shape of new data does nothing for
  data already written.**
- **Fix, in two places:**
  - `setup::start()` now branches on **`rapid_mlx_supported()`**, not on the id
    prefix: where Rapid-MLX cannot run, *any* profile resolves through Ollama
    (a stale id falls back to the configured `ollama_model`).
  - `Welcome.tsx::resolveProfile()` only restores a persisted choice if it still
    appears in this machine's `setup.profiles`, else takes the recommendation.
    3 regression tests.
- **Prevention / notes:**
  - **Persisted selections are cross-platform and cross-version input — validate
    them on read.** A profile id, model name, or path stored by an earlier build
    (or another OS, via a synced config) is untrusted by the time it is used.
  - When a fix relies on a new identifier format, ask what happens to rows
    already written in the old format. Here the answer was "the bug survives,
    and only for existing users" — the worst group to leave broken.

### "Managed Rapid-MLX is currently available on Apple Silicon only" — the local engine has two shapes — 2026-07-27
- **Symptom:** with the model step finally unblocked, the setup wizard's sample
  died on *"Managed Rapid-MLX is currently available on Apple Silicon only."*
- **Root cause:** the code models "local engine" as exactly one thing — a
  **child process Adversaria spawns and supervises** (`rapid-mlx serve`). On
  Windows the local engine is **Ollama**, an external service Adversaria neither
  starts nor owns, so every step of that lifecycle rejected it:
  1. `setup::start()` → `runtime_path()` hard-errors off Apple Silicon.
  2. `set_local_model_profile` guards on `pinned_snapshot()`, which only knows HF
     snapshots, so the Settings model switch failed too.
  3. `test_local_setup` required `managed_credentials()` — the per-launch URL +
     key that only `rapid-mlx serve` produces.
- **Fix:** an `ollama:` profile id short-circuits each of those. `start()` becomes
  a **reachability check** (`ollama_ready`) that confirms the tag is actually
  served and returns a synthetic `running` status; `set_local_model_profile`
  skips the snapshot guard; `test_local_setup` passes `llm_base_url: None`,
  which is precisely how the Python summarizer selects its Ollama backend
  (`if base_url or self.backend == "openai"`).
- **Prevention / notes:**
  - **"Start the local model" is not a universal operation.** Managed-process and
    external-service engines need different lifecycles; a single code path that
    assumes the former will fail on every platform that uses the latter.
  - Failure was staged: fixing the model list only revealed the next guard, then
    the next. When porting, trace the *whole* flow (`start → verify → sample`),
    not just the step that is currently red.
  - A user who ran the old wizard has a **Rapid-MLX served-name in
    `ollama_model`** (e.g. `qwen3.6-27b-4bit`), which Ollama does not have.
    Re-running setup overwrites it; otherwise correct it by hand.

### First-run setup can never finish on Windows — the whole local path was Apple-only — 2026-07-27
- **Symptom:** setup step 6/7 sat forever on *"Your meeting model is still
  downloading — this step unlocks when it finishes · Preparing…"* with a progress
  bar at zero and **Run sample summary** permanently disabled. Earlier steps read
  *"On this Mac"* and *"Your Mac has 64 GB"*. Step 4 also claimed
  *"This build is missing the pinned local runtime … reinstall a complete build"*.
- **Root cause — four separate Apple assumptions:**
  1. `Welcome.tsx` gates the sample on `selectedInstalled`, which can only become
     true for a **pinned MLX snapshot**. `setup.rs` only ever returned
     `mlx-community/*` profiles, so on Windows it was false forever. Nothing was
     downloading; the progress bar had nothing to report.
  2. `model_setup.MODEL_PINS` pre-downloaded `mlx-community/whisper-large-v3-mlx`
     + `-turbo-q4` **unconditionally** — ~3.5 GB of weights faster-whisper cannot
     load. That is what made the step *slow* as well as impossible.
  3. `rapid_runtime_bundled: false` is **normal** off Apple Silicon (the local
     engine there is Ollama), but the UI rendered it as a broken install.
  4. User-facing copy hardcoded "Mac".
- **Fix:** `setup_status()` is now async and, when no Rapid-MLX runtime is
  bundled, returns the **models already pulled in Ollama** as profiles — all
  `installed: true`, recommended by what fits in ~70 % of RAM, embedding models
  filtered out (they cannot summarize). `model_setup` pins follow
  `transcriber.backend_is_mlx()`; on CT2 `whisper-live` deliberately points at the
  **same repo as `whisper-main`**, because `_build_live_transcriber` only builds a
  separate live model for MLX — pinning a second one downloads 1.6 GB nothing
  loads. The wizard skips the download pipeline for `ollama:` ids (Rust's
  `downloadable_profile` rejects them, which would raise "Unknown model profile"
  on every 1 s poll).
- **Prevention / notes:**
  - **`installed`/`ready` gates are load-bearing.** A gate that can only be
    satisfied by one platform's artifact is a permanent hang on every other
    platform, and it presents as a progress bar rather than an error.
  - Pre-downloading weights is only helpful if the backend that will run can
    **load** them. Pin selection must follow backend selection, always.
  - `ollama_profiles` maps `model_alias` to the Ollama tag, which
    `set_selected_model_profile` writes to `ollama_model` — the existing plumbing
    needed no change, because `default_llm_model()` was already cfg-gated to
    `qwen3.6:35b-a3b` off macOS.

### "Adversaria can't start — no such table: action_items" on an upgraded install — 2026-07-27
- **Symptom:** first launch of the Windows build on a machine with an existing
  database died at startup with
  `Adversaria couldn't open your local database. no such table: action_items`,
  and the dialog then advised allowing **keychain access when macOS asks** — on
  Windows.
- **Root cause:** `init_db` runs `migrate_plaintext_to_encrypted()` **before** it
  creates the schema. That migration verifies the copy by counting rows in
  `meetings`, `action_items`, and `chat_messages` — but a database written by a
  build that predates those tables doesn't have them. The 0.2.x Windows line
  wrote `%APPDATA%\meeting-note-taker\meetings.db` with **only** a `meetings`
  table, and the new build reads the **same path**, so every upgrader from that
  line hit it. Encryption is on by default (`encrypt_db: true`) and the old
  `config.json` has no such key, so the serde default applies and the migration
  always runs. Verified against the real file: 147 meetings, tables
  `['meetings', 'sqlite_sequence']`, no `action_items`.
- **Fix:** `storage::table_count()` returns 0 for a table that doesn't exist.
  `sqlcipher_export` copies whatever schema it finds, so absent-on-both-sides is
  a legitimate match — the verification's integrity is unchanged, it just no
  longer treats "table introduced later" as data loss. The startup dialog now
  names the right credential store per platform. Two regression tests added.
- **Prevention / notes:**
  - **Anything that runs before the `CREATE TABLE IF NOT EXISTS` batch must
    assume an arbitrarily old schema.** Today only the two encryption migrations
    do. Everything after it is safe — the ALTER migrations already gate on
    `column_exists`, and all three tables they touch (`meetings`, `people`,
    `ask_messages`) are created in that batch first.
  - **No data was lost** — the migration bails before swapping anything, and
    `meetings.db.pre-encrypt-backup` is kept regardless.
  - The macOS line never hit this because its installs postdate `action_items`.
    A cross-platform product inherits the *oldest* schema on each platform
    independently; "works on macOS" says nothing about the upgrade path here.

### A CUDA-bundled Windows sidecar cannot be packaged — NSIS has a ~2 GB ceiling — 2026-07-27
- **Symptom:** the Rust app builds fine (`Built application at: …meeting-note-taker.exe`,
  release, 7m38s) and Tauri patches it for NSIS, then `makensis` dies with
  ```
  Internal compiler error #12345: error mmapping datablock to 33565757.
  failed to bundle project `The system cannot find the file specified. (os error 2)`
  ```
  The `os error 2` is a red herring — it's Tauri failing to find the installer
  makensis never produced. **The real error is the line above it.**
- **Root cause:** the frozen sidecar built with `ADVERSARIA_BUNDLE_CUDA=1` is
  **2.4 GB**, and NSIS installers top out around 2 GB. Measured payload —
  **1.9 GB of it is 15 CUDA DLLs**:
  | DLL | Size |
  |---|---|
  | `cublasLt64_12.dll` | 638 MB |
  | `cudnn_engines_precompiled64_9.dll` | 460 MB |
  | `cudnn_adv64_9.dll` | 257 MB |
  | `cudnn_ops64_9.dll` | 101 MB |
  | `cublas64_12.dll` | 98 MB |
  | `cudnn_graph64_9.dll` | 95 MB |
  | `nvrtc64_120_0.dll` + `.alt.dll` | 86 MB each |
  For scale, the entire notarized macOS DMG is 747 MB.
- **Fix:** `adversaria-service-windows.spec` defaults to **CPU-only**
  (`ADVERSARIA_BUNDLE_CUDA=0`), which packages cleanly. Transcription still works
  — `device="auto"` falls back to int8 on CPU — and a user who has the **NVIDIA
  CUDA Toolkit** installed still gets GPU, because `_patch_cuda_path()` searches
  `C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/*/bin`, and *that* branch
  works even when frozen (the site-packages branches do not).
- **Prevention / notes:**
  - Switching to WiX/MSI does **not** buy headroom — its cab limit is the same
    order. This is a payload problem, not a bundler choice.
  - **Do not trim individual cuDNN sub-libraries by guesswork.** Dropping the
    wrong one doesn't fail loudly; CTranslate2 falls back to CPU silently, so
    you ship a "GPU" build that quietly isn't. Any trimming must be validated on
    a real GPU by asserting `transcriber.device == "cuda"` after load.
  - The coherent long-term fix is to **download the CUDA runtime on first run**,
    exactly as model weights already are (they're deliberately not in the DMG
    either) — tracked in TODO.md.
  - PyInstaller also emits `ctranslate2.dll` **twice** (56 MB each, once at
    `_internal/` and once at `_internal/ctranslate2/`). Harmless, ~56 MB.

### The Windows build dies in `openssl-sys` because Git's Perl isn't a real Perl — 2026-07-27
- **Symptom:** `cargo check` on Windows fails inside `openssl-sys` with
  `configuring OpenSSL build: 'perl' reported failure with exit code: 2` and,
  further up:
  `Can't locate Locale/Maketext/Simple.pm in @INC ... /usr/share/perl5/core_perl/Params/Check.pm line 6`.
  Every cargo command fails, so nothing in `src-tauri` can be compiled, linted,
  or tested.
- **Root cause:** `rusqlite`'s `bundled-sqlcipher-vendored-openssl` feature
  builds OpenSSL from source, and OpenSSL's `Configure` is a Perl script. The
  only `perl` on a typical dev box is the **MSYS Perl shipped inside Git for
  Windows** (`C:\Program Files\Git\usr\bin\perl.exe`), which is stripped down —
  it lacks `Locale::Maketext::Simple` — and reports POSIX paths that later
  confuse an MSVC build. It is on PATH in Git Bash, so it gets picked silently.
- **Fix:** install a **native** Windows Perl and start a new shell:
  ```powershell
  winget install --id StrawberryPerl.StrawberryPerl --source winget
  ```
  Verify the right one is being used (`(Get-Command perl).Source` must NOT be
  under `\Git\`), then `cargo test --manifest-path src-tauri/Cargo.toml` →
  149 passed.
- **Prevention / notes:**
  - **NASM is NOT needed**, despite most OpenSSL-on-Windows advice saying so —
    `openssl-src` configures with `no-asm`. Don't burn time installing it.
  - GitHub's `windows-latest` runners ship Strawberry Perl already, which is why
    CI never hit this and only a local build does.
  - `scripts/build-windows.ps1` now fails fast with this exact instruction, and
    explicitly rejects Git's MSYS perl rather than letting the build get 10
    minutes in before dying.
  - Temporarily swapping the feature to plain `bundled` is a useful way to
    compile-check everything else *without* OpenSSL — but it is not a substitute
    for a real run: the two `storage::encryption_tests` fail under it with
    `no such function: sqlcipher_export`, because plain SQLite has no SQLCipher.

### Screen Recording permission grants silently stop working after many re-signed builds — duplicate TCC rows — 2026-07-25
- **Symptom:** Recording failed with
  `NoShareableContent("Content unavailable: The user declined TCCs for application, window,…")`
  even though Adversaria was **enabled** under Privacy & Security → Screen
  Recording. Toggling it off/on, re-granting, and relaunching the app all failed,
  repeatedly.
- **Root cause:** **two TCC rows existed for `com.meetingnotetaker.app`.**
  `tccutil reset` reported "Successfully reset…" *twice* for a single bundle id.
  The System Settings toggle only ever rewrites one row, so the stale one kept
  denying. This accumulates when many differently-signed builds of the same
  bundle id are installed in a short period — ~15 were installed on 2026-07-25.
- **Fix:**
  ```bash
  tccutil reset ScreenCapture com.meetingnotetaker.app
  osascript -e 'quit app "Adversaria"'; open -a Adversaria
  ```
  Then grant when prompted. The reset makes macOS treat it as a first-time grant
  instead of reusing the broken row.
- **Prevention / notes:**
  - This is a **developer-only** hazard. A normal user installing one release
    won't reproduce it.
  - **Never launch `Adversaria.app/Contents/MacOS/meeting-note-taker` directly
    from a shell.** macOS attributes TCC to the *responsible* parent process, so
    a shell launch can register attribution against the terminal and muddy the
    app's entry. Always `open -a Adversaria`.
  - Separately, macOS **revokes Screen Recording whenever the app bundle is
    replaced** — so every *update* re-prompts. 0.3.65 makes that recoverable in
    the UI (Open Settings + Relaunch) rather than a dead end, but it cannot
    prevent the revocation.

### Notch-docked window rendered BELOW the menu bar — AppKit clamps frames unless the level is raised FIRST — 2026-07-24
- **Symptom:** First notch-dock attempt of the recording pill (Tauri window +
  raw AppKit `setFrame`/`setLevel`) rendered at y≈38 with the menu bar visible
  between the notch and the pill — macOS silently constrained the frame out of
  the menu-bar strip.
- **Root cause:** the frame overlapping the menu bar was applied while the
  window still had a normal level; AppKit clamps such frames to the visible
  area. Order matters.
- **Fix:** in `show_recording_bubble` (`src-tauri/src/commands.rs`):
  `setLevel(25 /*status bar*/)` → `setCollectionBehavior(canJoinAllSpaces |
  stationary | fullScreenAuxiliary)` → `orderFrontRegardless()` → **then**
  `setFrame_display`. Confirmed live: pill fused with the notch. This mirrors
  NotchyPrompter's proven `NotchWindow.swift` (level set in init, frame after) —
  the second brain had the answer (`teleprompter` project).
- **Prevention:** never NSPanel-convert Tauri windows (still the crash rule);
  for over-the-menu-bar placement use raw AppKit on the existing NSWindow with
  level/behavior BEFORE frame. Notch geometry = `safeAreaInsets.top` +
  `frame.width − auxiliaryTopLeftArea.width − auxiliaryTopRightArea.width`.
  Candidate polish from NotchyPrompter: `sharingType = .none` hides the overlay
  from legacy screen-capture (won't appear in Zoom shares).

### "Encrypted mic recording is too large for WAV processing" — a 16-channel virtual input device produced 7.6 GB in 45 min — 2026-07-24
- **Symptom:** A real 45-minute meeting recorded fine, but transcription failed every
  retry with `Encrypted mic recording is too large for WAV processing`. The spool
  showed `mic.records` = **7.1 GB** for 45 minutes (system track: a sane ~1 GB).
- **Root cause:** Two stacked issues. (1) The user's default macOS input device was a
  **16-channel virtual device** ("Quicktime Player", 16-in/16-out @ 44.1 kHz — left
  behind by an audio-routing tool), and `run_mic_capture`
  (`src-tauri/src/audio/macos.rs`) recorded the device's native channel count
  verbatim: 44 100 × 4 bytes × 16 ch ≈ 2.8 MB/s ≈ 7.67 GB committed plaintext.
  (2) WAV's RIFF data size is a `u32`, so `decrypt_channel`
  (`src-tauri/src/recording_spool.rs`) hard-failed on any track > 4 GiB with no
  recovery path — the recording stayed "kept" and every retry died identically.
- **Fix:** (1) mic capture now **downmixes to mono in the cpal callback** (average
  across each interleaved frame; header always mono f32). Whisper mixes to mono
  anyway — zero quality loss, 16× less disk in this incident, 2× for normal stereo
  mics. (2) `decrypt_channel` uses `wav_output_plan()`: a multi-channel float track
  whose raw size exceeds `u32::MAX` is **streamed through `downmix_f32_to_mono()`**
  (carry buffer across encrypted-chunk boundaries) into a mono WAV instead of
  erroring — which also makes previously stuck recordings transcribable on retry.
  Only a >4 GiB *mono* track (23+ hours) still errors. Unit-tested with the real
  incident numbers (7 674 593 280 bytes / 16 ch).
- **Prevention:** never trust the default input device's channel count or assume WAV
  fits any recording — cap/downmix at both capture and assembly. Averaging across
  a mostly-silent multi-channel device attenuates the one live channel (sum/N), but
  such devices are routing junk anyway; the meeting content lives in the system
  track. Users with virtual audio devices installed should set a real microphone as
  the macOS default input (System Settings → Sound → Input) — the app records the
  **default** input.

### First-run setup: "The local setup service is not ready; retry in a moment" — lifespan blocked the whole server on a model download — 2026-07-24
- **Symptom:** On a fresh Mac (first tester laptop, 0.3.59), the app launched fine
  but the setup wizard's **Download model** button errored with "The local setup
  service is not ready; retry in a moment" — for minutes, forcing manual retries.
- **Root cause:** Two layers. (1) FastAPI's `lifespan` in
  `python-service/src/server.py` built AND warmed the live-caption Whisper model
  **synchronously** — `_build_live_transcriber` → `_warm_transcriber` →
  `mlx_whisper.transcribe(path_or_hf_repo="mlx-community/whisper-large-v3-turbo-q4")`,
  which on a fresh machine **downloads that model from Hugging Face first**. Uvicorn
  does not bind its port until lifespan returns, so the entire service was
  connection-refused until the download finished (minutes; forever if offline).
  (2) `HttpClient::start_model_download` (`src-tauri/src/http_client.rs`) mapped the
  first connect error straight to the user-facing "not ready" string — no wait, no
  retry.
- **Fix (0.3.60):** (1) `lifespan` now assigns `_live_transcriber = _transcriber`
  immediately (live captions fall back to the main model, same as non-MLX platforms)
  and builds/warms the fast model on a daemon thread that holds `_WHISPER_LOCK`
  (preserves the one-model-at-a-time invariant; live endpoints already skip on a
  busy lock). (2) New `HttpClient::wait_until_ready(max_wait)` polls `GET /health`
  every 750 ms with a 5 s per-request timeout; the `start_model_download` command
  waits up to 120 s before showing the old error. (3) `Welcome.tsx` shows
  "Starting the local engine — the first launch can take a minute…" while waiting.
- **Prevention:** never do network/model work in FastAPI `lifespan` — the server
  serves NOTHING until it returns; warm in a background thread under
  `_WHISPER_LOCK`. Any Rust call on the first-run path must tolerate a booting
  sidecar (`wait_until_ready`), because on a fresh Mac boot = Gatekeeper first-run
  scan + Python imports even after the download fix. Field workaround for builds
  ≤0.3.59: wait ~2–3 min after first launch, then click Download model again.

### Notarized app crashes at LAUNCH on macOS 15 — "Symbol not found: _OBJC_CLASS_$_SCScreenshotConfiguration" — 2026-07-24
- **Symptom:** The notarized 0.3.58 DMG installed cleanly (Gatekeeper accepted) but
  the app **crashed instantly at launch** on a macOS **15.7.3** MacBook (worked on
  the macOS 26 build machine + earlier macOS-26 test Macs). Crash: `Namespace DYLD,
  Code 4 Symbol missing · Symbol not found: _OBJC_CLASS_$_SCScreenshotConfiguration
  · Expected in: ScreenCaptureKit.framework · terminated at launch`. Not a
  notarization/signing problem — dyld aborts before any code runs.
- **Root cause:** `src-tauri/Cargo.toml` had `screencapturekit = { …, features =
  ["macos_26_0"] }`. That crate's version features are **cumulative** and gate which
  API tier is compiled; `macos_26_0` binds macOS-26-only classes (e.g.
  `SCScreenshotConfiguration`) as a **STRONG** class reference (`nm -m` shows
  `(undefined) external`, vs `weak external` for its siblings). Built on the macOS
  26 SDK the symbol resolves; on macOS 15 the class doesn't exist → strong ref →
  launch abort. Our code only uses base `SCStream` audio capture (macOS 12.3–13);
  the screenshot classes are never called. Deployment target was already `minos
  14.4`, but the feature flag overrode availability-based weak-import.
- **Fix:** cap the feature at the deployment target — `features = ["macos_14_4"]`.
  Verified: `cargo check` compiles (no macOS-15/26 API in our code) and
  `nm -m target/release/meeting-note-taker | grep SCScreenshotConfiguration` is now
  **empty** (the strong ref is gone; the rest are base APIs present on 14.4+).
  Rebuilt + re-notarized as 0.3.59.
- **Prevention:** the screencapturekit feature MUST equal the deployment target
  (`macos_14_4`), never a newer tier. When building on a newer-than-target macOS
  SDK, after any release build run `nm -m <binary> | grep '_OBJC_CLASS_\$_SC' |
  grep -v weak` and confirm every strong ScreenCaptureKit class ref is one that
  exists at the deployment target. Test on a Mac at/near the minimum OS, not just
  the (newest-OS) build machine — earlier testers were all on macOS 26, which
  masked this for weeks.

### Freeze died with "syntax error near unexpected token" — a concurrent session edited build-dmg.sh WHILE bash was executing it — 2026-07-18
- **Symptom:** The 0.3.49 freeze aborted at step 3 with
  `scripts/build-dmg.sh: line 88: syntax error near unexpected token ';'` —
  on a script that had produced three clean freezes the same day.
- **Root cause:** bash reads script files INCREMENTALLY as they execute. A
  concurrent session (the Codex/release-hardening workstream editing
  notarization prep into the script) wrote `build-dmg.sh` at 18:39:39, minutes
  into the freeze — the file shifted under bash's read offset and the next
  read landed mid-construct. Not a bug in the script; a bug in running a
  freeze off a file another agent is editing.
- **Fix:** run freezes from a SNAPSHOT of the committed version — and the
  snapshot MUST live inside `scripts/` (untracked name), NOT /tmp:
  `git show HEAD:scripts/build-dmg.sh > scripts/.freeze-snap.sh && bash
  scripts/.freeze-snap.sh`. The script SELF-LOCATES its repo root from its own
  path (`ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$ROOT"`,
  lines 15-16) — a /tmp copy resolves ROOT to `/` and dies at
  `cd: python-service: No such file or directory` no matter what cwd or
  wrapper you pin (cost four failed launches to learn). The concurrent
  editor's on-disk work stays untouched either way.
- **Prevention:** ALWAYS freeze from a snapshot, never the live file; when
  unattributed changes appear in `scripts/` mid-session, assume a concurrent
  workstream is active and coordinate before committing, popping stashes onto,
  or building from that file.

### Vocab-echo came back + sentences duplicating — audio-level gates can't catch text-level failures — 2026-07-18
- **Symptom:** (1) A fresh recording's transcript STARTED with a shuffled
  glossary echo ("Tatweer OS, Echelon, Tatweer, Echelon…" = the exact
  dictionary) despite the 2026-07-16 fix; (2) the same sentence appeared twice
  in a transcript despite the June mic-bleed dedup.
- **Root cause:** both defenses judged the wrong evidence. The 07-16 echo fix
  (`16de4fb`) was **VAD-only** — it drops segments on silent audio and never
  looks at the text, so an echo coinciding with voiced audio (user narrating
  from second one; a video playing on the system track) passes whole. The
  bleed dedup matched only `SequenceMatcher >= 0.85` on the full ordered
  string with a 4-word floor — two tracks transcribing one utterance slightly
  differently fall under 0.85 and the sentence survives on both.
- **Fix (0.3.48):** `strip_glossary_echo` in `transcriber.py` — token-set
  matcher, order/repetition-independent: drops segments that are ≥80% glossary
  tokens with ≥2 distinct terms, prefix-trims leading glossary runs off mixed
  segments; applied to both channels in both dual paths after the VAD gates.
  `strip_mic_bleed` gains a multiset token-containment fallback (≥0.8 for 4+
  words, exact for 3 words; floor 4→3). 276 pytest.
- **Prevention:** hallucinations are a TEXT phenomenon — every gate needs a
  text-level check, not just an audio-level one. When a "fixed" bug returns,
  first ask what evidence the old fix actually inspected. Python fixes are
  DORMANT until a re-freeze (dev runs the frozen sidecar).

### "The app is the old version!" — `open -a Adversaria` launched a stale debug bundle, not /Applications — 2026-07-18
- **Symptom:** Right after a verified 0.3.47 install (Info.plist, codesign, chunk
  greps all ✓ on `/Applications/Adversaria.app`), the user saw the OLD UI —
  none of the day's changes present.
- **Root cause:** `open -a Adversaria` resolves through LaunchServices, which
  had `src-tauri/target/debug/bundle/macos/Adversaria.app` (a stale debug
  build) registered and picked IT. The disk verification was of one copy; the
  launched process was another. The debug app even answered `/health` (its own
  bundled sidecar), so the post-launch health check "passed" while proving
  nothing about the installed app. Both copies share the same app-data dir and
  SQLite DB.
- **Fix:** `pkill` the impostor, delete the stale debug bundle, launch by
  explicit path (`open /Applications/Adversaria.app`), and confirm with
  `ps aux | grep MacOS/meeting-note-taker` that the running binary lives under
  /Applications (the executable is `meeting-note-taker`, not `Adversaria`).
- **Prevention:** the ship ritual must verify the RUNNING process path, not
  just the installed bundle; never `open -a <name>` when multiple bundles
  exist. Three related same-day gotchas: (1) replacing the app binary
  re-prompts macOS TCC for Documents access — until Allow is clicked,
  second-brain vault sync fails silently (fail-soft) and imports look broken;
  (2) **imported bundles get re-summarized and re-titled by the app's own LLM
  queue within minutes** — don't hand-polish bundle summaries and don't judge
  import success by title greps; (3) learned by near-miss: **never automate
  destructive UI clicks** — a scripted delete raised its confirm against the
  WRONG meeting (only a missed confirm-click saved it); hand destructive steps
  to the human.

### Global hotkeys (⌘⇧M/⌘⇧N) never fired — `register()` followed by `on_shortcut()` is a same-process double registration and the handler silently never attaches — 2026-07-16
- **Symptom:** The ⌘⇧M record hotkey (and ⌘⇧N quick-note) did nothing in any build, with **zero error output** — the `register()` error branch never printed, so the failure looked like a mystery conflict or missing permission.
- **Root cause:** `tray.rs` called `app.global_shortcut().register(shortcut)` (Ok) and then `on_shortcut(shortcut, handler)`. In tauri-plugin-global-shortcut 2.3.2, `on_shortcut` **registers again** before storing the handler; macOS `RegisterEventHotKey` rejects a same-process duplicate (`eventHotKeyExistsErr -9878`), so `on_shortcut` failed **before the handler was stored** — and its `Result` was discarded with `let _ =`. The OS delivered every press to the app; the plugin dropped it (handler `None`, and `lib.rs` builds the plugin without a global `with_handler`). Windows `RegisterHotKey` rejects same-process duplicates too — broken everywhere, since the original hotkey commit.
- **Fix:** call `on_shortcut()` **only** (it registers and attaches atomically), check its `Result`, and gate the handler on `event.state() == ShortcutState::Pressed` — handlers fire on key-down *and* key-up, so an ungated toggle fires twice per press. Verified in `tauri dev`: background ⌘⇧M starts/stops real captures.
- **Prevention:** with this plugin, `register()` is only for the global-`with_handler` pattern; never pair it with `on_shortcut` on the same accelerator. Never `let _ =` a registration `Result`. And don't trust "it would have logged an error": a Carbon experiment (`RegisterEventHotKey` twice, plus against another app's hotkey) proved **cross-process conflicts return `noErr`** — a conflicting app steals the combo with no error to either side, so absence of an error message proves nothing about hotkey health.
- **Symptom:** A meeting the user "hardly spoke" in showed them at 35% talk-time / 24:44, with 79 interruptions and 71 wpm ("slow"). The other speakers looked normal.
- **Root cause:** the mic track was near-silent (the user was listening). The **MLX Whisper backend has no built-in VAD** (its own comment says so), so it transcribed the silence and **hallucinated** filler — Norwegian *"Takk for at du så på"* ("thanks for watching"), repetition loops (*"God of God of God…"*) — each landing on a ~30s segment window. Those got labeled with the user's name and counted as talk-time + interruptions. Meeting 130 in the DB: "Hamza" credited **1485s across 102 turns spanning the whole meeting**; per-turn durations summed to **4201s against a 2866s meeting** (massive overlap = the mic duplicated the room). `strip_mic_bleed` couldn't catch it — hallucinations don't match the system channel, so the ≥0.85 similarity check kept them. (This also debunked an earlier false "no `Me:` since meeting #20": the mic speaker is labeled with `user_name` — "Hamza" — not "Me", so a `LIKE '%Me:%'` search missed it. Mic capture was fine.)
- **Fix (v0.3.41):** `drop_unvoiced_mic_segments` — run Silero VAD (bundled) on the mic track and drop segments that don't overlap real voice, applied in **both** `transcribe_dual` paths (faster-whisper + MLX `_merge_dual`) right before `strip_mic_bleed`. Verified on the frozen sidecar: system-speech + 20s-silent-mic → transcript has only `Them`, no `Me`.
- **Prevention:** the MLX backend has NO VAD — any channel that will contain silence (the mic, when the user is listening) must be VAD-gated before Whisper or it invents speech. **Hallucination** (no matching audio anywhere → VAD gate) and **bleed** (matches the system channel → similarity strip) are different failure modes needing different filters. Headphones remove the bleed half entirely.

### Live transcript lagged 20–40s — the cause was the VAD 30s force-cut + sharing the heavy large-v3 model, NOT slow transcription — 2026-07-14
- **Symptom:** After the mic was fed into the live pipeline, live captions took 20–40s to appear ("worked but very slow").
- **Root cause (measured, not assumed):** warm transcription is ~0.4s and RAM was 128GB/95% free — so neither the model nor memory. Three real causes: (1) `live.py _MAX_UTTERANCE_S = 30` — an utterance only flushes after a 2s pause (`_REDEMPTION_MS = 2000`) OR a **30s force-cut**; speaking continuously (or a mic that never dips below the VAD threshold) meant a caption waited up to 30s; (2) the live path used the **same heavy large-v3 model** as the final transcript, so it also paid a lazy **cold load** (~20–40s) on first use and yielded the shared `_WHISPER_LOCK` whenever a full transcription ran; (3) 2s poll interval added latency.
- **Fix (v0.3.40):** a **dedicated fast live model** — `mlx-community/whisper-large-v3-turbo-q4` as `server.py::_live_transcriber`, **warmed synchronously at lifespan startup** so the first caption isn't a cold load (this adds a few seconds to sidecar boot — an accepted trade). VAD tuned for a *preview*: `_MAX_UTTERANCE_S` 30→8, `_REDEMPTION_MS` 2000→900; Rust `LIVE_CHUNK_SECS` 2→1. The **final** transcript stays large-v3 (turbo drops Arabic diacritics — the user records Arabic, so the accurate model must remain for the stored transcript). Measured: 0.71s/utterance on the frozen build; user-confirmed fast.
- **Prevention:** a live *preview* and the *final* transcript have different needs — fast-and-approximate vs accurate. Give them **separate models** (muesli does the same). Don't diagnose "it's slow" as "the model is slow" without measuring — here the model was fine and the latency was entirely VAD-timing + cold-load + lock-sharing. When tuning `live.py` constants, remember they are also passed into `completed_utterances`; keep logic tests decoupled by passing explicit `max_utterance_s`/`redemption_ms`.

### Ask "couldn't reach the local model" — the macOS chat/summarize backend is the MLX server on :8000, NOT Ollama; and it lazy-loads the 35B model — 2026-07-14
- **Symptom:** In the Ask tab, retrieval found the right meetings but every answer was "I found relevant meetings but couldn't reach the local model to answer. Make sure it's running and ask again." (`commands.rs:1678`). Same generic message also fires from `commands.rs:1564`/`1630`. Ollama was up (`/health` → `ollama_available:true`) and had `qwen3.6:35b`.
- **Root cause (two layers):** (1) **Wrong backend assumption** — on macOS, chat/summarize do NOT go to Ollama (11434). With `llm_provider:"local"` + empty `llm_base_url`, the sidecar posts to an **OpenAI-compatible MLX server on `http://127.0.0.1:8000/v1/chat/completions`** (Rapid-MLX, ADR-008). Its model is literally named **`qwen3.6-35b`** (hyphen) — matching `config.json`'s `ollama_model`. Ollama (11434) is used ONLY for embeddings (`bge-m3` via `/embed`). So the Ollama-style name `qwen3.6:35b` is irrelevant here and 404s on :8000. (2) **Cold lazy-load** — :8000 loads the ~21 GB model on first use. Measured: `/v1/models` answers in 12 ms while a cold `/v1/chat/completions` hangs 15 s+; warm it's ~1 s. A request during the cold-load window surfaces as the generic "couldn't reach the local model" error.
- **Fix:** the configured model name was already correct (`qwen3.6-35b`) — no change needed; verified the full path works (sidecar `/chat` → :8000 returned a correct grounded answer). ⚠️ Do NOT "correct" `ollama_model` to a colon/Ollama-style tag on macOS — that breaks it (this session did exactly that, then reverted).
- **Prevention:** the field is named `ollama_model` but on macOS-local it targets the **MLX server on :8000**, not Ollama — check what's on :8000 (`curl :8000/v1/models`) before touching model config. Proposed hardening (awaiting the user's word, TODO): surface the REAL error instead of the catch-all; retry once on first chat failure; warm-up ping to :8000 when the Ask tab opens / a recording stops.

### `tauri dev` dies with `resource path ../python-service/dist/adversaria-service doesn't exist` if started during a `build-dmg.sh` re-freeze — 2026-07-03
- **Symptom:** Launching `npm run tauri dev` while `scripts/build-dmg.sh` was running failed the Rust build script: `error: failed to run custom build command … resource path ../python-service/dist/adversaria-service doesn't exist` (exit 101).
- **Root cause:** the re-freeze step wipes and rebuilds `python-service/dist/adversaria-service` (the PyInstaller sidecar). Tauri's `build.rs` resolves that directory as a bundled resource at compile time — dev and release builds both read it — so any cargo build racing the freeze window sees it missing and aborts.
- **Fix:** sequence them — **freeze first, then dev** (or dev first and re-freeze after). Relaunch `tauri dev` once `build-dmg.sh` finishes; the freeze recreates the folder.
- **Prevention:** under the dev/staging discipline (dev = `tauri dev`, staging = installed app, adopted 2026-07-03) never start the two pipelines concurrently. Also quit the installed app before running dev — both processes open the same SQLCipher DB and there's no `busy_timeout` yet (2026-07-03 audit, TODO.md).

### Graph flutter was the wrapper's `alphaTarget`, not the physics constants — 2026-07-03
- **Symptom:** Graph kept "fluttering" even after the 2026-07-02 alpha/alphaDecay/velocityDecay tuning: post-drag it buzzed at constant amplitude for ~2 s then froze abruptly mid-motion, and every visit to the tab replayed the whole scatter-and-settle dance.
- **Root cause (in `cytoscape-d3-force/src/d3-force.js`, not our constants):** on every node **grab and release** the wrapper calls `simulation.alphaTarget(alpha/3).restart()` and never sets it back to 0. d3 alpha decays *toward* `alphaTarget`, never below it, so after release the sim holds ~0.167 energy until the wrapper's tick budget (`progress ≥ 1`, ~135 ticks) hard-stops it. Separately, `layout: {name:"random"}` re-scattered all nodes on every mount.
- **Fix (`GraphView.tsx`, v0.3.15):** `cy.on("free","node", …)` zeroes `alphaTarget` after the wrapper's own handler (element listeners fire before core-delegated ones), so motion decays naturally to rest; a module-scope `savedPositions` map + `preset` layout resumes settled positions across visits with a gentle `alpha: 0.12` wake-up.
- **Prevention:** with d3-force drag interactions, whatever raises `alphaTarget` on dragstart must lower it to 0 on dragend (d3's own drag examples do both halves — the wrapper only does the first). When a layout "never calms down", inspect the extension's event handlers before re-tuning physics constants.

### Graph tab black-screened the whole app — cytoscape-d3-force needs `linkId`, and an uncaught effect error unmounts the entire React tree — 2026-07-02
- **Symptom:** Clicking the new Graph tab turned the whole window black — not just the graph pane, the entire UI (sidebar, header, everything).
- **Root cause (two layered):** (1) `cytoscape-d3-force` passes edge data straight into `d3.forceLink()`, whose default id accessor resolves link endpoints by **array index**; our string node ids (`meeting-5`) made d3 throw `Error: node not found: meeting-5` during `layout.run()` (its `defaults.js` ships `linkId: undefined` — the accessor is opt-in). (2) That throw happened inside a `useEffect` with **no error boundary** — React unmounts the ENTIRE tree on an uncaught effect error, hence a black window instead of a broken graph pane.
- **Fix (`GraphView.tsx`):** pass `linkId: (d) => d.id` in the layout options, and wrap the whole cytoscape-init effect in try/catch → `setError(...)` so any future graph failure degrades to the in-pane error message. Reproduced + verified via Playwright against the live Vite server using the exact bundled modules (`/node_modules/.vite/deps/…`) — error reproduced pre-fix, simulation confirmed running post-fix.
- **Prevention:** (a) when a view's mount effect can throw (third-party init, WebGL/canvas libs), catch at the effect boundary — React has no default error isolation and one bad tab kills the app; (b) for thinly-maintained cytoscape extensions, read `src/defaults.js` — README options lists are incomplete (this same session: cola's `infinite` is source-only); (c) a dead React tree can't be revived by HMR/Fast Refresh — `touch index.html` forces a Vite full page reload in every client, including the Tauri webview.

### Groq "Chat with a meeting" shows the model's `<think>` reasoning before the answer — 2026-06-25
- **Symptom:** With the LLM provider on Groq, chat replies streamed a long `<think>…</think>` chain-of-thought block before the actual answer (~200 of 281 deltas were reasoning). Summaries were unaffected.
- **Root cause:** Groq's `qwen/qwen3-32b` is a reasoning model and emits `<think>…</think>` in the response **content** when the reply isn't json-constrained. The local path suppresses this with `chat_template_kwargs:{enable_thinking:false}` (which Groq rejects, so it's stripped — see the summarization entry), and summaries use `json_object` (Groq puts reasoning in a separate `reasoning` field, leaving `content` clean) — but **free-text chat has neither guard**, so the reasoning leaks through.
- **Fix (`summarizer.py`):** strip `<think>…</think>` from chat replies, provider-agnostically. `_strip_think()` (regex) for the non-streaming `chat()`, and `_strip_think_stream()` — a small state machine that buffers a leading think block until `</think>`, then passes the answer through — wrapped around `chat_stream()`'s delta generator (both backends). No-op when absent (local/non-reasoning models). Verified live against Groq (clean answer); 4 new unit tests.
- **Prevention:** reasoning models leak `<think>` into **content** unless constrained (`json_object`/schema) or told not to think; the suppression knob (`enable_thinking`, `reasoning_effort`/`reasoning_format`) is provider-specific and not universally accepted, so a provider-agnostic output strip is the robust default for free-text generations. (Groq optimization for later: `reasoning_effort:"none"` would skip generating the reasoning entirely — faster — but needs the same strippable-on-400 handling as other vendor params.)

### Groq cloud transcription fails with HTTP 413 Payload Too Large — raw WAV upload — 2026-06-25
- **Symptom:** With transcription set to **Groq cloud**, `Transcription failed: Cloud transcription failed: Client error '413 Payload Too Large' for url '…/audio/transcriptions'` — often after only a minute or two of recording.
- **Root cause:** `transcribe_cloud` uploaded the **raw capture WAV** unmodified. The macOS system channel is **48 kHz / 2-channel / 32-bit float** = `48000·2·4` ≈ **23 MB per minute**, so a ~1-minute meeting already exceeds Groq's upload cap (**25 MB free tier**, 100 MB dev). (Verified the limits + accepted formats at console.groq.com/docs/speech-to-text.)
- **Fix (`transcriber.py`):** before upload, **downsample each channel to 16 kHz mono** — Whisper's native rate, so it's lossless *for ASR*, and exactly Groq's recommended preprocessing — and **split into chunks under the cap**, offsetting each chunk's segment timestamps back onto the full-recording timeline before the Me/Them merge. Decode+resample is done **in-process with PyAV** (`av.AudioResampler`), NOT by shelling out to `ffmpeg`: a packaged macOS GUI app doesn't inherit the shell `PATH`, so the Homebrew `ffmpeg` binary may be missing in the frozen sidecar — but **PyAV bundles its own ffmpeg libraries** and is already `collect_all`'d into the freeze. Chunk WAVs are written with the stdlib `wave` module (no extra deps); chunk length is sized from the raw PCM byte rate so each uncompressed file is guaranteed under the cap. `_CLOUD_MAX_UPLOAD_BYTES` (default 24 MB) is env-overridable for the dev tier. **Verified live against real Groq** (34.6 MB raw input → multi-chunk upload, no 413); 4 cloud tests (2 updated to write real WAVs since PyAV now decodes them, 2 new for chunking). 119 pytest green. **Needs a `build-dmg.sh` re-freeze** to reach the installed app.
- **Prevention:** never upload raw capture audio to a cloud ASR — **downsample to 16 kHz mono first** (huge size win, no ASR-quality loss) and **chunk** for anything long; meetings routinely exceed any single-file cap. For in-process audio decode/resample in a packaged app, prefer **PyAV** (bundled ffmpeg libs) over shelling to a system `ffmpeg` (PATH not inherited by GUI apps). Confirm a provider's size limit + accepted formats from its docs before building the upload path.

### Groq summarization fails with HTTP 400 — `chat_template_kwargs` unsupported (+ qwen has no `json_schema`) — 2026-06-25
- **Symptom:** After switching the LLM provider to **Groq** (`llm_base_url=https://api.groq.com/openai/v1`, model `qwen/qwen3-32b`), every summarize failed: `Summarization failed: OpenAI-compatible request failed: Client error '400 Bad Request' …`. The message was opaque — `raise_for_status()` only carries the status line, **not** Groq's JSON body that says why.
- **Root cause (two separate 400s, isolated by replaying the exact body with `curl`):** (1) `_chat_openai` sent `"chat_template_kwargs": {"enable_thinking": false}` on **every** request — a **vLLM/Rapid-MLX extension, not an OpenAI-API field**. Groq strictly rejects unknown params: `property 'chat_template_kwargs' is unsupported`. This fired *first*, before the older DeepSeek json_schema fallback could even run (and that fallback's error-text match — `"response_format"` — didn't match this message anyway). (2) Even past that, `qwen/qwen3-32b` on Groq doesn't support `response_format: json_schema` (`This model does not support response format json_schema`); only `json_object` returns 200 (reasoning then lands in a separate `reasoning` field, so `content` is clean).
- **Fix (`summarizer.py`):** generalized `_chat_openai` (and `_chat_openai_stream`) to **adapt to server quirks** — on a 400 naming an unsupported field, remember it **per host** and retry without it. New `_NO_CHAT_TEMPLATE_KWARGS` set mirrors `_NO_JSON_SCHEMA`; a small retry loop peels off `chat_template_kwargs` then `json_schema` in turn → lands on `json_object`. Local vLLM/Rapid-MLX is untouched (never in the no-sets, so it still gets both on the first try). Also now **surface the server's error body** in the `RuntimeError` so future failures name the real cause. Verified live against Groq (real key) — full structured summary returned; 3 new unit tests. **Python change → needs a `build-dmg.sh` re-freeze to reach the installed app's frozen sidecar.**
- **Prevention:** "OpenAI-compatible" servers reject **unknown body params** (not just unsupported `response_format`) — keep vendor-specific extensions (`chat_template_kwargs`, `enable_thinking`, …) off the cloud path, or make them strippable-on-400. When a cloud call 400s, **replay the exact request body with `curl` field-by-field** to isolate which param is rejected, and always log the response **body**, not just the status. See the related DeepSeek entry below.

### Offline speaker diarization (sherpa-onnx) — packaging + threshold gotchas — 2026-06-24
- **Goal:** add on-device diarization of the system-audio channel without breaking
  the build or the offline/easy-setup promise.
- **`uv sync` drops the native-lib companion:** `sherpa-onnx` requires
  `sherpa-onnx-core` (a wheel-only package shipping `libonnxruntime` + the
  `_sherpa_onnx` extension under `sherpa_onnx/lib/`). `uv pip install` pulls it,
  but `uv sync` silently omits it, leaving the extension unable to `dlopen` its
  runtime (`Library not loaded: @rpath/libonnxruntime…`). Fix: declare
  `sherpa-onnx-core` **explicitly** in pyproject so the lockfile keeps it.
- **`uv pip install` desyncs the env:** mixing `uv pip install` with the project
  then triggers `uv run` auto-sync churn that transiently removed base deps
  (faster-whisper). Reconcile with a clean `uv sync`; run tests via
  `.venv/bin/python -m pytest` (after `uv sync --extra dev`) to avoid the churn.
- **PyInstaller:** add `collect_all("sherpa_onnx")` to the spec (libs live in
  `sherpa_onnx/lib/`); a tiny frozen-import test (`--collect-all sherpa_onnx`)
  confirmed the dylibs bundle and load before committing to the full build.
- **Model + threshold are coupled:** the multilingual zh+en `campplus` embedding
  model gives the correct speaker count at clustering `threshold≈0.5`; the
  zh-cn-only `eres2net` model needed `0.9`. Diarizer speaker ids are sparse
  (e.g. 0,1,2,7) — remap to contiguous "Speaker 1..N" for display.
- **Prevention:** for split native-lib Python packages, declare the binary
  companion explicitly; always validate the PyInstaller freeze of a native-lib
  dependency with a standalone frozen import before the full app build.

### Encrypting `meetings.db` at rest (SQLCipher) — feature flag, FTS5, migration, and the `sqlite3.Row` trap — 2026-06-24
- **Goal:** Encrypt the database at rest without breaking FTS5 search or losing the
  user's existing plaintext data, and keep the MCP server (which reads the same file)
  working.
- **Verified facts (rusqlite 0.31):** the SQLCipher path is the
  `bundled-sqlcipher-vendored-openssl` feature (vendors OpenSSL, so the signed `.app`
  has no system-crypto dependency); **FTS5 stays enabled** (the bundled build sets
  `-DSQLITE_ENABLE_FTS5`). The key is applied with `PRAGMA key = "x'<64-hex>'"` (raw
  32-byte key, no passphrase KDF). Plaintext→encrypted migration uses
  `ATTACH … KEY … ; SELECT sqlcipher_export('encrypted');`.
- **Key safety:** generate a new key **only** when the keychain entry is *missing*
  (`NoEntry`). Any other keychain error must propagate, never silently mint a new key —
  that would make an existing encrypted DB permanently unreadable. Migration backs up
  the plaintext, verifies per-table row counts, and only then atomically swaps; on any
  mismatch it bails without touching the original.
- **The `sqlite3.Row` trap (Python/MCP):** `sqlcipher3-binary` has **no macOS-arm64
  wheel** → use `sqlcipher3` (builds from source). And assigning `sqlite3.Row` as the
  `row_factory` of a **`sqlcipher3`** connection raises `TypeError: Row() argument 1
  must be sqlite3.Cursor, not sqlcipher3.dbapi2.Cursor` — you must use `sqlcipher3.Row`.
  A "roundtrip" smoke test that doesn't set `row_factory` won't catch this; the failure
  only shows on the first real name-based row access.
- **Prevention:** when you swap a DB driver, swap its `Row`/cursor types too, and test
  the actual access pattern (`row["col"]`), not just connect+read. For keychain-backed
  keys, always distinguish "missing" (generate) from "inaccessible" (fail loudly).

---

### Action items silently dropped (Arabic + drifted headings) & chaotic Weekly Recap — 2026-06-23
- **Symptom:** (1) A meeting's action items were visible in its note but **never reached the To-Do view / Weekly "Action Items" / per-meeting checkboxes**. (2) The **Weekly Recaps** page looked chaotic — each bullet's meeting name rendered as a **big, bold, centered block** on its own line, and empty sections showed literal "None mentioned" bullets attributed to a meeting.
- **Root cause:** (1) Action items are extracted from the summary markdown by matching the **section heading** against `ACTIONABLE` — Rust `extract_action_items` (`storage.rs`) mirrored by `lib/summary.ts`. The regex was `(action item|next step|deliverable)` — **English-only and brittle**. An Arabic meeting (`**عناصر العمل**`, "Action Items") matched nothing, so its 6 items were dropped (verified: meeting id=5 had 0 stored rows). The same gap bites any LLM heading drift ("To-Build", "Tasks", "To-Do List"). Extraction was fine for standard English headings — the brainstorm template ("To-Build / Action Items", "Next Steps") already matched, so the brittleness only surfaced on non-standard/Arabic headings. (2) `WeeklyView.tsx` reused the `.btn-month-nav` button class (`display:flex; justify-content:center; font-size:15px; font-weight:bold`) for the inline meeting-attribution link, forcing each title onto its own centered/bold line; and the decisions/topics aggregation didn't filter "None mentioned" placeholder bullets.
- **Fix:** Broadened `ACTIONABLE` in **both** `storage.rs` and `summary.ts` (kept in sync) to `(action item|action point|next step|to[ -]?(?:do|build)|deliverable|task|عناصر العمل|الخطوات التالية|المهام)`. `backfill_action_items` (runs at DB init for meetings with 0 rows) recovers previously-dropped items on next launch — a re-extraction scan over the live DB confirmed **only** id=5 changes (0→6), no regressions. Added a `.weekly-meeting-link` CSS class (inline, 13px, muted) replacing `.btn-month-nav` in the recap; exported `isPlaceholderBullet()` from `summary.ts` and used it to drop "None"/"None mentioned"/"لا يوجد" bullets from the recap's Decisions/Key Topics. The screenshot's "0/0 action items" was just **timing** — that week's 4 meetings genuinely had no action items; meetings 42/43 (the dictated bug-report sessions) were recorded *after* the screenshot and *did* extract their items.
- **Prevention:** Heading-driven extraction is only as good as the heading vocabulary — local LLMs drift and multilingual output uses translated headings. Keep the Rust matcher and its TS mirror identical (comment both), and prefer a tolerant heading regex over relying on the prompt to emit exact text. Never reuse a `display:flex`/centered/bold button class for inline text attribution.

---

### DeepSeek (cloud) summarization fails — wrong-case model + `response_format: json_schema` unsupported — 2026-06-23
- **Symptom:** With the LLM provider set to DeepSeek, summarize failed — first a `404` for `http://127.0.0.1:8765/v1/chat/completions` (a **local** address, not DeepSeek), and after fixing the key it would still 400.
- **Root cause:** Three layers. (1) The `:8765` 404 was **stale** — that's the local Rapid-MLX server; the config's `llm_base_url` had pointed there earlier. `config::load_config()` reads fresh **per request**, so the cloud override *does* apply once the config is correct (it is NOT cached for the LLM path — distinct from the Python-service HTTP client). (2) The **model id was wrong-case** (`Deepseek-v4-flash`); DeepSeek's valid ids are `deepseek-v4-flash` / `deepseek-v4-pro` (all lowercase — confirm with `curl https://api.deepseek.com/v1/models -H "Authorization: Bearer <key>"`). (3) The real blocker: the app sends `response_format: {type: "json_schema"}` (local vLLM/Rapid-MLX enforces it), but **DeepSeek returns HTTP 400 "This response_format type is unavailable now"**; only `{type: "json_object"}` works (returns clean JSON).
- **Fix (`9ca9f5d`):** `summarizer._chat_openai` tries `json_schema`, and on a 400 whose body mentions `response_format` retries once with `json_object`, remembering the host (`_NO_JSON_SCHEMA`) so later calls skip the failing attempt. Safe because the prompts already contain "json" (json_object mode requires it) and `_parse_json` tolerates the output. **Python summarizer changes require a re-freeze (`build-dmg.sh`)** to reach the installed app's frozen sidecar.
- **Follow-on — empty summary (`d837b00`):** with `json_object` there's **no schema enforcement**, so DeepSeek's output shape **drifted run-to-run** — `sections` sometimes came back as **bare strings** (`["Key Topics Discussed", …]`) instead of `{heading, bullets}` objects, which `_render` shows as headings with no bullets (the "empty summary"). Fixed by **pinning the exact JSON shape in the system prompt** (sections must be `{heading, bullets}` objects, never bare strings; without hardcoding section names — the template lists them). Verified 3/3 DeepSeek runs return full bullets.
- **Prevention:** "OpenAI-compatible" ≠ OpenAI-feature-complete — `json_schema` (strict structured output) is NOT universal; fall back to `json_object`, but then **spell out the required JSON shape in the prompt** (the model has no schema to follow). Verify a provider's exact model ids via its `/v1/models` before trusting a name/case. When a **local-looking URL** shows up in a cloud-provider error, suspect a **stale config value**, not the new provider.

---

### Floating-bubble Stop "does nothing" — JS `emit` from a secondary webview doesn't reach the minimized main window — 2026-06-23
- **Symptom:** Pressing **Stop** on the floating recording bubble left recording running (it kept capturing; the app sometimes just came forward). An earlier "fix" (`await emit("tray-toggle-recording")` *then* `focusMainWindow()`) did **not** resolve it.
- **Root cause:** The bubble is a **separate webview window** (`index.html?widget=recording`). Its frontend `emit("tray-toggle-recording")` did not reliably reach the **main** window's `listen(...)` — the main window is usually **minimized** when the bubble is shown, and a minimized/occluded WKWebView's JS is suspended, so the event is missed/dropped. The tray and global hotkey work because they emit the same event from **Rust** (`app.emit(...)`), which reaches the main window's listener reliably.
- **Fix (`be57d43`):** New Rust command `bubble_stop_recording` — it `unminimize()/show()/set_focus()` the main window first (resuming its webview), then `app.emit("tray-toggle-recording", ())` **from Rust** (the proven tray/hotkey path). `RecordingBubble.tsx` now `invoke("bubble_stop_recording")` instead of a JS `emit`. The main window's existing handler runs the stop + transcribe/summarize pipeline; focusing main also hides the bubble.
- **Prevention:** For cross-window signalling in Tauri v2, **don't rely on a frontend `emit` from a secondary/often-hidden webview reaching another window** — route it through a Rust command that uses `app.emit` (or `emit_to("main", …)`). Especially when the target window may be minimized.

---

### Two "Adversaria" apps appear — leftover dev instance + stale Launch Services records from ejected DMG mounts — 2026-06-23
- **Symptom:** After installing a freshly-built `.dmg`, macOS shows **two Adversaria apps** (Dock/⌘-Tab and/or Launchpad/Spotlight).
- **Root cause:** Two independent causes. (1) A `tauri dev` instance (`target/debug/meeting-note-taker`) was **still running** alongside the just-installed `/Applications` app → two Dock icons (plus orphaned dev `adversaria-service` sidecars + the Vite server). (2) Opening/building the `.dmg` left **mounted DMG volumes** (`/Volumes/Adversaria`, `/Volumes/dmg.XXXXXX`); when ejected, **Launch Services kept stale registrations** to those gone paths, which linger as phantom apps. The build also leaves a real bundle at `…/target/release/bundle/macos/Adversaria.app` that Launch Services indexes.
- **Fix:** Kill the dev-side processes (path-scoped: `pkill -f "target/debug/meeting-note-taker"`, `… target/debug/adversaria-service`, vite/esbuild) — **not** the `/Applications` one. Unregister the dead/artifact bundles: `lsregister -u <path>` (the modern `lsregister` removed `-kill`, so a full rebuild isn't available). Eject temp mounts with `hdiutil detach /Volumes/...`. `killall Dock` to refresh.
- **Prevention:** Don't run `tauri dev` and the installed app at once (they also contend on the DB + ports). After `build-dmg.sh`, `hdiutil detach` any `/Volumes/dmg.*` and `lsregister -u` the `target/.../macos/Adversaria.app` artifact (candidate cleanup step for the script).

---

### Pin/lock/delete/add-tag fail with "database disk image is malformed" — FTS trigger over-fires + self-heal gap — 2026-06-22
- **Symptom:** In the reskinned app, pin/lock/delete/+Add-Tag did nothing. An on-screen IPC tracer revealed `set_meeting_pinned` failing with **`database disk image is malformed`**. The DB's `PRAGMA integrity_check` was **`ok`** (only the FTS index was bad; 27 meetings intact).
- **Root cause:** Two compounding issues. (1) The FTS5 keep-in-sync `meetings_fts_au` trigger was `AFTER UPDATE ON meetings` — it fired on **every** column, so `set_meeting_pinned/locked` and `update_meeting_tags` (which change only the non-indexed `pinned`/`locked`/`tags` columns) needlessly re-indexed FTS and hit the **out-of-sync external-content index** → `SQLITE_CORRUPT_VTAB`. (2) The earlier startup self-heal ([above](#a-corrupt-out-of-sync-fts5-index-bricks-startup-after-m1m2)) only ran when a **backfill performed an UPDATE** — on an already-backfilled DB the backfills are no-ops, so the corrupt index was never detected/repaired and every later meetings write failed.
- **Fix (`3098b2b`):** (1) Scope the trigger: `CREATE TRIGGER … meetings_fts_au AFTER UPDATE OF title, summary, transcript ON meetings` — pin/lock/tags no longer touch FTS at all (correct: those columns aren't indexed; also more efficient). (2) Add `repair_fts()` run **unconditionally** at startup: drop the triggers (so `setup_fts` recreates them with the current def) and `INSERT INTO meetings_fts(meetings_fts) VALUES('rebuild')` (or drop the table if unrebuildable). No content lost (the index is derived). Regression test: `pin_update_skips_fts_and_survives_a_bad_index`.
- **Prevention:** FTS keep-in-sync triggers should be `AFTER UPDATE OF <indexed columns>`, never bare `AFTER UPDATE`. Any startup FTS repair must run **independent of** whether migrations/backfills happen. The corruption was found only by surfacing the real IPC error on-screen (a tracer in the notice banner) — when a Tauri action silently fails, surface the error, don't swallow it to console.

---

### Reskinned detail-header buttons (pin/lock/delete/+Add-Tag) "don't work" — stale React Fast Refresh — 2026-06-22
- **Symptom:** After the live reskin, every control in NoteViewer's `.viewer-header` (pin, lock, delete, +Add Tag) was unresponsive in the running `tauri dev` app — clicks did nothing. Persisted across multiple HMR edits.
- **Root cause:** NOT the code. The wiring, CSS hit-testing, and handlers were all correct (verified by driving the Vite app in headless Chromium with a mocked Tauri bridge: `elementsFromPoint` showed the button on top with `pointer-events:auto`; a DOM `.click()` fired the exact `set_meeting_pinned → get_meetings → get_meeting` invoke sequence; +Add Tag opened its popup). The running app was executing **stale code**: the reskin changed NoteViewer's **props interface** (added `onTogglePin/onToggleLock/onDelete`), and React Fast Refresh **silently keeps the old component in memory when a component's props/hooks shape changes** — it doesn't remount. So the window kept the pre-wiring NoteViewer. Pure HMR never recovered.
- **Fix:** A **full reload** — restart `tauri dev` (or Cmd+R in the webview). The fresh mount runs the current code and everything works.
- **Prevention:** After HMR edits that **change a component's props interface or hooks** (not just JSX/styles), do a full reload before concluding "it's broken." When debugging "handler doesn't fire" in a Tauri app, you can drive the same frontend at `http://localhost:1420` in a real browser with a mocked `window.__TAURI_INTERNALS__.invoke` (via Playwright `addInitScript`) and use `document.elementsFromPoint(x,y)` + a recorded invoke log to isolate frontend vs backend vs stale-build.

---

### A corrupt/out-of-sync FTS5 index bricks startup after M1/M2 (fixed: self-heal) — 2026-06-22
- **Symptom:** A fresh build off `feat/reskin-phase0` **panics on launch**: `Failed to initialize
  database: database disk image is malformed / Error code 267: Content in the virtual table is
  corrupt` (`src/lib.rs:36`, `storage::init_db`). The older bundled `/Applications` app opened the
  same DB fine. The macOS `sqlite3` CLI **and** Python 3.41's `PRAGMA integrity_check` both reported
  `ok` — falsely (the CLI has no FTS5; Python's FTS5 `integrity-check` also passed).
- **Root cause:** `meetings_fts` is an **external-content** FTS5 index (`content='meetings'`). It was
  out of sync with `meetings`. The **M1 backfill `UPDATE meetings SET transcript_turns=…`** fires the
  `meetings_fts_au` keep-in-sync trigger, whose `'delete'` of old values hits the inconsistency →
  `SQLITE_CORRUPT_VTAB` (extended 267) → propagates through `init_db`'s `?` → panic. The old build had
  no such backfill, so it never fired the trigger. The app's bundled SQLite (rusqlite 0.31 /
  libsqlite3-sys 0.28 = **SQLite 3.45**) is stricter than the 3.41 CLI; the corruption surfaces only
  on the **trigger write**, not on `integrity-check` — so integrity-check is NOT a reliable detector.
- **Fix (committed `49929f9`):** `init_db` now runs the backfills, and on a corruption error
  (`is_db_corruption` → `ErrorCode::DatabaseCorrupt`) **drops the FTS index + triggers and retries**;
  `setup_fts` rebuilds a clean index. The index is derived data (rebuilt from `meetings`) — **no
  meeting content is lost**. Healthy DBs pay nothing. Manual one-off repair (what unblocked the live
  DB first): via an FTS5-capable engine, `DROP TRIGGER meetings_fts_ai/ad/au; DROP TABLE meetings_fts;`
  then relaunch (the app rebuilds it). Verified: a new unit test reproduces `CORRUPT_VTAB` + recovery
  (`init_recovers_when_fts_update_trigger_hits_corruption`), and an E2E run against the real corrupt
  DB self-heals (logs `[storage] FTS5 index corrupt; dropping…`, backfills all 27 meetings, no panic).
- **Prevention:** Don't trust the macOS `sqlite3` CLI for FTS5 integrity (no FTS5 module). To validate
  an FTS5 index, use the **same engine the app uses** or test the actual write. Any startup migration
  that `UPDATE`s a table with FTS sync triggers must tolerate a bad index (the index is rebuildable —
  drop+retry, never panic). **Never run two app instances against the same DB** — a second fresh
  connection can also report transient FTS corruption while the first holds the WAL.

---

## Environment & dev-stack

### Gatekeeper can transiently refuse ONE freshly signed sidecar lib ("library load disallowed by system policy") — 2026-08-24
- **Symptom:** the stage-3.5 sidecar smoke's `/transcribe` returns 500; the frozen
  service's stderr shows `ImportError: dlopen(..._internal/av/codec/hwaccel.abi3.so ...):
  code signature ... not valid for use in process: library load disallowed by system
  policy`. Everything else in the same freshly signed tree loads fine, and the identical
  build PASSED the same smoke earlier the same morning (0.3.81 attempts 1 vs 3).
- **What it is NOT (each ruled out):** not quarantine/provenance xattrs on the dist tree
  (PyInstaller does NOT propagate xattrs — the dist `.so` had none, even though 250 venv
  Mach-Os carry `com.apple.provenance`); not a signing race (`sign_macho_tree` is a serial
  while-loop); not a bad cert (attempt 1 passed, `codesign --verify` on the mains passed).
- **Best-supported cause:** a transient syspolicyd/AMFI trust-evaluation failure at dlopen
  time — `log show` put syspolicyd mid `SecTrustEvaluateIfNecessary` churn at the exact
  smoke timestamp, on the same box whose syspolicyd wedged twice on 08-23 (fd-leak entry
  below at the top of this file). One denied evaluation kills exactly one library load.
- **Mitigations:** `xattr -cr` both dist trees before signing (hygiene, now in
  `build-dmg.sh`); rerun the build (transient means retry usually passes); if it repeats,
  reboot — same cure as the fd-leak. Related: the same morning the build's stage-0
  `notarytool history` credential pre-check failed once and then succeeded unchanged in
  every context probed (sandboxed + unsandboxed background) — treat one-off failures from
  this machine's security daemons as retryable before digging.

### Killed freezes strand duplicate `dist` trees that wedge the NEXT build for an hour (2026-07-17)
- **Symptom:** `build-dmg.sh` appears hung at step 1/7 or 2/7 for 15+ minutes with the log
  showing `rm: dist/<name> 2/…: Directory not empty` spam. The DMG on disk is stale (from a
  previous run). `ps` shows the script alive but its `rm` child at ~0% CPU, grinding.
- **Root causes (two stacked):** (1) freeze runs killed mid-flight (e.g. the 2026-07-16
  codesign-timestamp flakes, or a TaskStop) can leave *duplicate* frozen trees —
  `dist/adversaria-service 2`, `dist/rapid-mlx 2` — multi-GB, with bundled-model dirs
  containing tens of thousands of files (one dir had ~2 MB of dirents). The next build's
  opening `rm -rf build dist` then grinds for ages. (2) On APFS, `rm -rf` over such
  gigantic directories can genuinely FAIL with `Directory not empty` **even with no
  concurrent writer** — the directory iteration misses entries; each pass deletes more.
- **What made it worse:** assuming the build was dead and running a second `rm` on the same
  tree — two+ concurrent `rm`s guarantee endless `Directory not empty` chaos. **Check
  `pgrep -f build-dmg.sh` / the rm child BEFORE touching its directories.**
- **Fix / protocol:** kill the build AND all rms → verify quiet (`pgrep -fl "rm -rf|build-dmg"`)
  → loop a SINGLE `rm -rf` until the dir is gone (`for i in 1..6; [ -d dist ] || break; rm -rf dist; done`)
  → relaunch the freeze. After ANY killed freeze, proactively check both
  `python-service/dist/` and `python-service/rapid-runtime/dist/` for `* 2`-style duplicates.

### macOS TCC grants (Screen Recording, Calendar) don't persist — ad-hoc signing churns the app identity
- **Symptom:** After granting Screen Recording (or Calendar) to a locally-built `Adversaria.app`,
  recording still fails — `NoShareableContent("The user declined TCCs for application, window, display
  capture")` — even though System Settings shows the permission **ON**. Re-granting + restarting
  doesn't help. Duplicate "Adversaria" rows pile up in System Settings → Privacy.
- **Root cause:** `tauri build` **ad-hoc** signs the `.app` ("linker-signed"). For ad-hoc code, macOS
  TCC identifies the app by its **code-directory hash (cdhash)** — it appears as
  `meeting_note_taker-<hash>` in `tccd` logs, NOT the bundle id. **Every rebuild changes the cdhash →
  a brand-new TCC identity**, so prior grants don't apply and the entry the user sees "on" belongs to
  an *old* build's hash. Running from a non-standard location (e.g. inside `~/Documents/…/target/…`)
  compounds the flakiness. Confirm with `codesign -dvv <app>` → `Signature=adhoc`,
  `Identifier=meeting_note_taker-<hash>`.
- **Fix:** Sign with a **stable certificate** so TCC keys on the bundle id + a fixed Designated
  Requirement. A **self-signed "Code Signing" cert** from Keychain Access works (no Apple account
  needed). What worked here (cert `NotchyPrompter Dev`):
  ```sh
  # inside-out: sidecar first (with the disable-library-validation entitlement), then the app
  codesign --force --sign "NotchyPrompter Dev" --entitlements python-service/entitlements.plist \
    "<app>/Contents/Resources/adversaria-service/adversaria-service"
  codesign --force --sign "NotchyPrompter Dev" "<app>"
  codesign -dvv "<app>"   # expect Identifier=com.meetingnotetaker.app, Authority=NotchyPrompter Dev (NOT adhoc)
  ```
  Then install to **/Applications** (standard location), reset the tangled state
  (`tccutil reset ScreenCapture com.meetingnotetaker.app` + `tccutil reset Calendar com.meetingnotetaker.app`),
  launch, grant **once** → grants now persist across rebuilds. **`scripts/build-dmg.sh` now takes
  `ADVERSARIA_SIGN_IDENTITY`** (default `-` ad-hoc) and signs both sidecar + app with it.
- **Prevention:** For daily use of a locally-built TCC app, always sign with the SAME stable identity:
  `ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev" ./scripts/build-dmg.sh`. Create the cert once:
  Keychain Access → Certificate Assistant → Create a Certificate → type **Code Signing**, self-signed.
  Ad-hoc is fine only for a build you never rebuild.

### macOS calendar (EventKit) permission can't be granted under `npm run tauri dev`
- **Symptom:** Settings → Calendar → "Apple Calendar (this Mac)" → Enable instantly returns
  **"Permission denied — grant Calendars in System Settings › Privacy"** with no macOS prompt ever
  appearing. The EventKit Rust code compiled and linked fine (`cargo check` + a full dev build both
  succeed).
- **Root cause:** `tauri dev` runs the **bare binary** `src-tauri/target/debug/meeting-note-taker`,
  which does **not** carry an embedded `Info.plist`. macOS TCC refuses to present the Calendars prompt
  (and `EKEventStore.requestFullAccessToEvents` returns denied / can even crash) when the process has
  no `NSCalendarsFullAccessUsageDescription` usage string. Confirmed:
  `otool -s __TEXT __info_plist target/debug/meeting-note-taker` shows **no** `NSCalendars*` key. The
  usage strings live in `src-tauri/Info.plist` and are only merged into the app's `Info.plist` when
  **bundling** (`tauri build`), not in dev. (Same reason the *installed* `.dmg` couldn't grant it — that
  bundle predates adding the calendar key.) This applies to ALL TCC-gated features (mic/screen worked
  only because they were tested in the bundled `.app`).
- **Fix:** Test calendar in a **bundled `.app`**, not `tauri dev`. Fast path when the frozen sidecar
  (`python-service/dist/adversaria-service`) already exists: `npm run tauri build` →
  `src-tauri/target/release/bundle/macos/Adversaria.app` (embeds `src-tauri/Info.plist`, so the prompt
  works). Full/current path (also re-freezes the Python sidecar): `./scripts/build-dmg.sh`. Verify the
  key made it: `PlistBuddy -c "Print :NSCalendarsFullAccessUsageDescription" <app>/Contents/Info.plist`.
- **Prevention:** Any new TCC-gated capability (calendar, contacts, etc.) needs (1) the usage string in
  `src-tauri/Info.plist` and (2) **bundle-build testing** — `tauri dev` will always deny it. (Possible
  future DX fix: embed `Info.plist` into the dev binary via a `-sectcreate __TEXT __info_plist` linker
  flag so dev can prompt too — not done yet.)

### macOS `.dmg`: summarization fails with `Connection refused` — the LLM server isn't bundled
- **Symptom:** A freshly-installed `Adversaria.dmg` transcribes fine but summarizing errors with `Summarization failed: OpenAI-compatible request failed: [Errno 61] Connection refused`. Errno 61 = `ECONNREFUSED`.
- **Root cause:** Only **transcription** (MLX) is bundled in the app. **Summarization** calls an external LLM server. On Apple Silicon `default_llm_backend()` returns `"openai"`, so the service POSTs to a Rapid-MLX OpenAI-compatible server at `http://127.0.0.1:8000/v1` (`summarizer.py:51`). If nothing is listening on :8000 → connection refused. The bundled sidecar spawn (`commands.rs:87`) passes only `PATH` + `HF_HUB_DISABLE_XET` — **not** `LLM_BACKEND` — and a Finder-launched `.app` doesn't inherit shell env, so you can't point it at a running Ollama without a code change. The macOS path is hard-committed to Rapid-MLX on :8000.
- **Fix:** Run the server the app expects: `rapid-mlx serve qwen3.6-35b --port 8000` (alias → `mlx-community/Qwen3.6-35B-A3B-4bit`, the A3B MoE — fast, low active-param GPU load). For daily use, a **login LaunchAgent** at `~/Library/LaunchAgents/com.lagharilabs.adversaria.llm.plist` (`RunAtLoad` + `KeepAlive`) autostarts it. The app's requested model lives in `config.json` `ollama_model` (sent on every request) — set it to the served alias (`qwen3.6-35b`).
- **Two gotchas hit while wiring this:**
  1. **Rapid-MLX needs `HF_HUB_DISABLE_XET=1` too** (not just the Whisper service). The 35B was half-downloaded (9.5/20 GB, 4 `.incomplete` shards) and stalling on the broken-xet path; adding the env var to the LaunchAgent made it resume cleanly via plain HTTP (`206 Partial Content`) and finish.
  2. **Qwen3.6 is a reasoning model and rambles** if you call it raw (a bare chat request returned a wall of "Thinking Process… Output: ready… Wait…"). The app avoids this — `_chat_openai` sends `temperature:0`, `chat_template_kwargs:{enable_thinking:false}`, and `response_format:{json_schema}`. **Verified Rapid-MLX honors all three**: the exact app request returned clean `{"title":…,"attendees":[…]}` with no thinking leak. So test the *app's* request shape, not a bare prompt.
- **Prevention:** Documented the LaunchAgent + model switch in [HANDOFF.md](./HANDOFF.md). The real product gap — the app should health-check the LLM backend and show a friendly "start your LLM server" banner instead of a raw errno — is logged in [TODO.md](./TODO.md).

### macOS: MLX Whisper model download wedged at 0 bytes — every transcription hung forever
- **Symptom:** First-ever transcription on macOS (live preview *and* the final pass) never returns; the service log shows `Fetching 4 files: 0%` indefinitely. `~/.cache/huggingface/hub/models--mlx-community--whisper-large-v3-mlx` holds only ~16 KB (config/README) plus one or more **0-byte `*.incomplete`** weight blobs that never grow. Network to HuggingFace is fine (small files fetch; `curl` of the weights `resolve/` URL 302-redirects to `us.aws.cdn.hf.co/xet-bridge-us/…` and returns `HTTP 200, content-length ~3.08 GB`).
- **Root cause:** `mlx-community/whisper-large-v3-mlx`'s large weight files are served from HuggingFace's **Xet** backend, and this machine's `hf_xet` package is broken (`import hf_xet` succeeds but `hf_xet.__version__` raises). `huggingface_hub` ≥1.x routes large blobs through the broken Xet client, which stalls at 0 bytes — while small (non-Xet) files and small models like `whisper-tiny` download normally. This is why earlier sessions only ever verified `whisper-tiny`. One stuck download blocks **all** transcription because the model must load before any audio is processed.
- **Fix:** Set **`HF_HUB_DISABLE_XET=1`** for the Python service — it falls back to the plain-HTTP download path (the one `curl` confirms works) and the ~3 GB model pulls at normal speed. Clear stale state first: `pkill` the wedged download, delete the 0-byte `*.incomplete` blobs and the matching `.lock` under `~/.cache/huggingface/hub/.locks/`. To unblock immediately without waiting for the 3 GB pull, launch with `MLX_WHISPER_MODEL=mlx-community/whisper-tiny` (already cached) — rough quality but instant.
- **Prevention:** Export `HF_HUB_DISABLE_XET=1` in the macOS Terminal-2 runbook (see [HANDOFF.md](./HANDOFF.md)) until `hf_xet` is repaired (`uv pip install -U hf_xet` may fix it). ⚠️ Also: **never force-kill the Python service while the app has a `/transcribe` in flight** — the app's failure-cleanup deletes the temp WAVs, so a recording in progress is lost. Copy the `*_…wav` out of the temp dir first.

### `cublas64_12.dll is not found` — transcription silently ran on CPU
- **Symptom:** `Transcription failed: Library cublas64_12.dll is not found or cannot be loaded`, or transcription working but extremely slow despite an RTX 5090 present.
- **Root cause:** The CUDA runtime DLLs (cuBLAS/cuDNN) ship as the `nvidia-cublas-cu12` / `nvidia-cudnn-cu12` packages, declared as the **`cuda` optional-dependency extra** in `pyproject.toml`. Plain `uv sync` does **not** install extras, so the DLLs were never present and faster-whisper fell back to CPU.
- **Fix:** `uv sync --extra cuda`. `transcriber.py::_patch_cuda_path()` then finds the DLLs under `site-packages/nvidia/*/bin` and prepends them to `PATH` before loading the model. Startup log should read `Whisper model loaded successfully on cuda`.
- **Prevention:** Documented in [HANDOFF.md](./HANDOFF.md) runbook and [CLAUDE.md](../CLAUDE.md) gotchas. The CUDA→CPU fallback in `_segments_with_fallback` is a safety net, not the intended path — if you're on CPU with a GPU present, the extra isn't installed.

### App showed the service as offline / "connection refused" on port 9878
- **Symptom:** `Transcribe request failed: error sending request for url (http://127.0.0.1:9878/transcribe)` even though the service was healthy on 9876.
- **Root cause:** **Config URL is cached in memory.** `AppState` builds its `HttpClient` once at startup from `config.json`. The saved config still pointed at a stale `9878`; editing it on disk (or in Settings) does not rebuild the in-memory client.
- **Fix:** Corrected `config.json` to `9876` **and restarted the app** so `AppState::new()` re-read it.
- **Prevention:** ✅ **Fixed 2026-06-17** — `HttpClient.base_url` is now an `RwLock<String>` and `update_config` calls `set_base_url()`, so a Settings service-URL change takes effect immediately (no restart). The incident above predates that fix.

### `failed to run cargo metadata: program not found`
- **Symptom:** `npm run tauri dev` fails immediately in Git Bash.
- **Root cause:** `cargo` is not on `PATH` in the Git Bash shell (it's at `~/.cargo/bin`).
- **Fix:** `export PATH="$HOME/.cargo/bin:$PATH"` before the command, or run from PowerShell.

### `Port 1420 is already in use` / `port 9876 … only one usage of each socket address`
- **Symptom:** Vite or the Python service refuses to start; sometimes the port shows a "ghost" PID that no longer exists in Task Manager.
- **Root cause:** A previous `tauri dev` / uvicorn run left an orphaned child (Vite node process, or a uvicorn multiprocessing worker) holding the port. Stopping the wrapper task doesn't always reap the child.
- **Fix:** Find and kill the holder before relaunching:
  ```powershell
  Get-NetTCPConnection -LocalPort 1420 -State Listen | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? { $_.CommandLine -match 'meeting' } | % { Stop-Process -Id $_.ProcessId -Force }
  ```
- **Prevention:** When relaunching the dev stack, kill stale `meeting-note-taker.exe`, the Vite node child, and uvicorn workers first. (A clean shutdown story is a TODO — see the sidecar item.)

---

## Meeting detection

### macOS auto-detect never fired — CoreAudio "unknown property" from a one-char fourcc typo
- **Symptom:** With `auto_detect_meetings` enabled, no "Meeting detected" card ever appeared on macOS for any call app. The detector thread ran, but `detect_meeting_app()` returned `None` every poll — silently.
- **Root cause:** `detection.rs` queried `kAudioHardwarePropertyProcessObjectList` with the wrong four-char code — `'prl#'` instead of `'prs#'`. CoreAudio returned `kAudioHardwareUnknownPropertyError` (`'who?'`, OSStatus `2003332927`) from the very first `AudioObjectGetPropertyDataSize`, so `process_list()` always returned `None` and no process was ever inspected. The failure was swallowed (`st != 0 → None`).
- **Fix:** `const PROC_LIST = fourcc(b"prs#")`. Verified against the SDK header — `AudioHardware.h:633` defines `kAudioHardwarePropertyProcessObjectList = 'prs#'` (the per-process selectors `'pbid'`/`'piri'` were already correct). After the fix the poller enumerates ~48 audio processes and matched `com.microsoft.teams2.modulehost` → "Microsoft Teams" live.
- **Prevention:** Verify CoreAudio (and any OS) four-char-code constants against the actual SDK header, never memory — one wrong char yields a silent `'who?'`. When a HAL property read fails, log the `OSStatus` as its fourcc (`(st as u32).to_be_bytes()`) to identify it in seconds. (Recognized apps live in `classify()`: Zoom/Teams/Webex/Slack/browsers — WhatsApp/FaceTime are not yet covered.)

---

## Audio capture

### Recorded transcript was missing everything the user said
- **Symptom:** Transcript only contained the *remote* participant's speech; the user's own side was absent.
- **Root cause:** The recorder originally captured **only system audio** (WASAPI loopback = what you hear). The microphone was never captured.
- **Fix:** Added a second parallel WASAPI capture stream for the default microphone (`audio/mod.rs`), transcribed separately and merged by timestamp into a `Me:` / `Them:` labeled transcript (`merge_labeled_segments` in `transcriber.py`). Mic capture is best-effort so a missing mic never breaks a recording.
- **Prevention:** Mic records the **default Windows input device** — verify the right device is default when using a headset. The UI has no indicator yet for whether the mic channel was captured (see TODO).

### Whisper "transcribed" speech from a silent recording
- **Symptom:** A recording with no real audio produced a plausible but entirely invented transcript (e.g. "A bit of a challenge for the younger generation…").
- **Root cause:** Whisper hallucinates on silent/near-silent input.
- **Fix:** `vad_filter=True`, `no_speech_threshold=0.6`, `condition_on_previous_text=False` in `transcriber.py`. Silence now yields an empty transcript.
- **Prevention:** **Test with real speech, never silence.** Recording nothing is not a valid end-to-end test.

### WASAPI capture compiled but captured nothing / wrong enum names
- **Symptom:** Build errors and silent capture failures against the `windows` crate.
- **Root cause:** `windows` crate v0.58 changed WASAPI enum/variant names and the global-shortcut API shape vs. older examples.
- **Fix:** Corrected the variant names and API calls (commit `64dac98`). Per-thread `CoInitializeEx(COINIT_MULTITHREADED)` with an RAII `ComGuard` is mandatory in each capture thread.
- **Prevention:** Pin `windows` crate version awareness — upgrading it can rename WASAPI symbols. This is exactly why [CLAUDE.md](../CLAUDE.md) principle #1 (research the current API) exists.

---

## UI state

### Record button stuck / disabled after a meeting finished
- **Symptom:** After a successful meeting, the record button and `Ctrl+Shift+M` stopped working until app restart.
- **Root cause:** The recording status went to `done` and stayed there forever; both the button and the hotkey only act from the `idle` state.
- **Fix:** `useRecording` now shows `done` for 2.5s then auto-resets to `idle`.

### App window rendered blank after a hot-reload
- **Symptom:** App showed an empty window; data appeared lost.
- **Root cause:** A React hot-reload left the webview in a broken render state. Data was intact in SQLite the whole time.
- **Fix:** Clean relaunch of the app cleared it.
- **Prevention:** A blank webview after HMR ≠ data loss — check the DB before assuming anything is gone.

### Meeting titles showed as raw markdown (e.g. `**Attendees:**`)
- **Symptom:** Sidebar titles were markdown fragments.
- **Root cause:** Title was the first line of the summary verbatim.
- **Fix:** `derive_title()` in `commands.rs` strips markdown decoration and picks the first meaningful line.

### No "record this meeting?" prompt for a second meeting right after recording a first
- **Symptom:** Record one auto-detected meeting, stop, then jump straight into another call — the floating "Meeting detected" card never appears for the second meeting.
- **Root cause:** `detection.rs` keeps a single global `last_prompt` driving `REPROMPT_COOLDOWN`. While recording, the poll loop reset `consecutive` and `prompted` but **not** `last_prompt`, so the cooldown from the first meeting's prompt survived the whole recording. With the cooldown raised to 300s (from 60s), the next meeting stayed suppressed for up to 5 minutes after you stopped. (Classic stale-state bug — the cooldown outlived the situation it was meant to throttle.)
- **Fix (2026-06-17):** Also reset `last_prompt = None` in the `!enabled || recording` branch — recording a detected meeting "resolves" the prior prompt, so the next detection is offered immediately instead of being throttled by leftover cooldown.
- **Prevention:** The cooldown's only job is to avoid re-nagging a **dismissed** prompt during continuous mic use (handled together with `prompted`); it must not carry across a recording session. When adding throttles keyed to wall-clock, scope their reset to the state transition they belong to.

---

## Frontend ↔ backend contract

### IPC calls failed with argument mismatches
- **Symptom:** Commands rejected because arguments didn't bind.
- **Root cause:** The React `invoke()` arg names didn't match the Rust command parameters (Tauri maps camelCase ↔ snake_case via serde, but the names must still correspond).
- **Fix:** Aligned the frontend arg names (`audioPath`, `template`) with the backend (commit `0f6ee89`). Keep `lib/tauri.ts` as the single typed boundary so this is caught once.

### Global hotkey crashed the app on startup
- **Symptom:** App failed to launch when the hotkey couldn't be registered.
- **Root cause:** Hotkey registration failure was treated as fatal.
- **Fix:** Made registration non-fatal and switched to `Ctrl+Shift+M` (commit `55f570d`). If the combo is taken, the app starts anyway and the tray menu is the control.

---

## Meta-lesson

The recurring theme across nearly every entry above: **a thing that "looked
fine" wasn't, because state lived somewhere stale** — a cached port, a stuck
status, an uninstalled extra, an uncaptured channel, a hallucinated transcript.
Verify behavior against reality (run it, read the DB, check the log) before
concluding it works. This is principle #3 in [CLAUDE.md](../CLAUDE.md).

---

## 2026-07-14 — Release hardening: quality gates and encrypted recovery

### Embedded Tauri tests need a deliberately pinned runtime stack

- **Symptom:** the WebdriverIO/Tauri smoke setup failed under the machine's
  default Node 26 and mismatched an upstream `@wdio/native-utils` dependency.
- **Root cause:** the current Tauri WDIO service has narrower real-world runtime
  compatibility than a loose “modern Node” assumption suggests, and its service
  release pins an older native-utils range.
- **Fix:** declare Node `>=20 <25`, use a small runner that selects installed Node
  20 LTS, and pin the compatible native-utils override. Keep the E2E app hermetic
  with a temporary data/config directory and test-only Tauri plugins.
- **Prevention:** treat the desktop-test driver, Node runtime, Rust plugins, and
  embedded app as one versioned compatibility unit. A passing browser-only test
  does not prove the Tauri boundary.

### “Encrypted at stop” is not crash-safe encryption

- **Symptom:** the old recorder retained a full meeting in RAM and only wrote a
  WAV after stop; a crash lost everything and long sessions grew without bound.
- **Root cause:** capture, retention, and final-file creation were one lifecycle.
- **Fix:** callbacks now enqueue bounded frames; writer threads commit roughly
  one-second XChaCha20-Poly1305 records with independently authenticated metadata.
  The live-caption tail is a separate 15-second ring. Tests prove that incomplete
  uncommitted tails are ignored and committed tampering is rejected.
- **Prevention:** make the committed manifest the recovery boundary and test both
  sides of it. Never infer crash safety from a clean-stop test.

### Decryption can quietly reintroduce the memory bug

- **Symptom:** an initial spool decryptor authenticated records correctly but
  accumulated the entire decoded meeting before writing a temporary WAV.
- **Root cause:** the processing path reused the convenience shape of the old
  full-buffer WAV writer.
- **Fix:** write the WAV header from manifest size, then authenticate and stream
  each committed record directly into a mode-0600 file. Delete partial plaintext
  on any error and clean stale processing WAVs at startup.
- **Prevention:** memory bounds must cover recovery and processing adapters, not
  only native capture callbacks.

### Preserve recoverable data before surfacing the error

- **Symptom:** a writer/backpressure warning could stop capture successfully but
  return an error before the normal pending-meeting path registered the spool,
  hiding committed audio until restart.
- **Fix:** recoverable writer failures return a warning alongside the finalized
  path. The command first marks the asset pending; the UI then shows the warning
  while the meeting remains visible and retryable.
- **Prevention:** error reporting is part of the durability transaction. On any
  partial success, establish the durable user-visible recovery reference first.

---

## 2026-07-15 — Release hardening: setup, privacy, UI, and packaging

### A resumable download is not verified merely because the hub client returned

- **Risk:** a resumed model snapshot can look complete while containing a
  truncated, stale, or tampered LFS file.
- **Fix:** allowlist model repository plus immutable revision, enumerate the
  resolved LFS set, and SHA-256 every file before marking setup ready. Keep
  progress aggregate-only so local paths do not leak into UI/errors.
- **Prevention:** “downloaded,” “resumable,” and “verified” are separate states.
  Only the last one may unlock a managed model.

### A frozen local server can persist private prompts even when the app does not

- **Risk:** the first real Rapid-MLX smoke showed prefix/KV cache persistence;
  transcripts or prompts could survive the process on disk.
- **Fix:** launch the managed runtime with prefix cache disabled, KV disk
  checkpoint interval zero, telemetry off, Hugging Face offline mode, loopback
  binding, and a random per-launch API key. Use `--text-only` for the pinned Qwen
  model so vision/Torch is neither required nor silently loaded.
- **Prevention:** privacy review must include dependencies' runtime caches and
  defaults, not only application-owned files and requests.

### Retina WebDriver window sizes are physical pixels, not proof of a CSS viewport

- **Symptom:** the old “1024x720” screenshot rendered a roughly 512px-wide layout
  and made header clipping look like the supported minimum behavior.
- **Fix:** measure `window.innerWidth/innerHeight`, iteratively scale the native
  window, and assert navigation bounds and document overflow in CSS pixels.
- **Prevention:** every desktop visual baseline should record the measured layout
  viewport. Screenshot pixel dimensions alone are ambiguous on HiDPI displays.

### Development-only advisories still deserve a deliberate disposition

- **Symptom:** production audit was clean, but WebdriverIO → Mocha resolved a
  vulnerable `serialize-javascript` 6.0.2.
- **Fix:** override it to the fixed 7.0.5 implementation, then rerun frontend,
  desktop, and complete npm advisory gates. The packaged dependency graph and
  the whole graph both now report zero advisories.
- **Prevention:** run both full and `--omit=dev` audits. “Not shipped” reduces
  impact but does not remove CI/supply-chain exposure.

### Updater packaging must happen after final app signing

- **Symptom:** the full packaging smoke revealed that `tauri build` created
  `Adversaria.app.tar.gz` before the build script re-signed nested binaries and
  the enclosing app. The DMG source app and updater app could therefore differ.
- **Fix:** after the final app signature, recreate the updater archive, sign it,
  extract it, byte-compare it to the app used for the DMG, and deep-verify the
  extracted signature. Provenance now hashes DMG, archive, and signature.
- **Prevention:** distribution ordering is part of the security contract:
  build → sign nested → sign app → verify app → pack updater → sign updater →
  compare/verify → pack DMG → notarize/staple.

### Tauri updater public-key files contain a base64 wrapper

- **Symptom:** a validation check initially reported a public-key mismatch after
  decoding the config value but comparing it to the raw `.pub` file.
- **Root cause:** both `tauri.conf.json` and the generated `.pub` file store the
  same base64-encoded minisign public text; decoding only one side creates a
  false mismatch.
- **Fix:** compare the two normalized stored strings. The existing local public
  pair matches the verifier key pinned in the app.
- **Prevention:** compare like representations before rotating any signing key.
  Never expose or replace a private key in response to an encoding mismatch.

### Release scripts must make smoke mode and release mode impossible to confuse

- **Risk:** an ad-hoc build with a placeholder registration endpoint can be
  technically runnable but is not a public beta candidate.
- **Fix:** explicit release mode fails closed without the production Formspree
  endpoint, Developer ID identity, updater private key, and notarization profile.
  The ad-hoc override is named and documented as packaging-smoke-only.
- **Prevention:** success output should identify what was not performed. A built
  DMG is not synonymous with a signed/notarized/accepted/published release.

### A macOS GUI E2E process needs a complete lifecycle, not just a binary path

- **Symptom:** the first run after rebuilding the desktop fixture intermittently
  aborted inside AppKit's `_RegisterApplication`; later runs could connect to an
  apparently healthy app but observe stale UI state.
- **Root causes:** `tauri build --debug` left only a linker-signed executable
  rather than a resource-sealed app bundle; direct executable spawning bypassed
  the normal LaunchServices path; failed supervisors orphaned staged apps on the
  fixed embedded-WebDriver port; and cleanup compared `/tmp/...` with macOS's
  canonical `/private/tmp/...` process path. Passing `/dev/stdout` and
  `/dev/stderr` to LaunchServices also caused launchd `EACCES` failures.
- **Fix:** use a test-only bundle identifier, whole-bundle ad-hoc sign and strict
  verify after every debug build, stage a disposable copy, launch it through
  LaunchServices without device-path redirection, explicitly forward only the
  E2E environment, canonicalize the staging path, and terminate that exact app
  before removing its directory.
- **Prevention:** after a desktop suite, assert both the process and listening
  port are gone. A green WebDriver status is insufficient if it may belong to a
  previous run. Keep release signing and test-only ad-hoc signing separate.


### Partial Python environment corruption can pass tests but break freezing (2026-09-05)
- The local install build first failed because `mlx/lib/mlx.metallib` was absent. Reinstalling MLX repaired Metal, but PyInstaller then failed because `importlib.metadata` returned a None version for `charset_normalizer`; 15 distributions had missing metadata. The earlier mocked test suite had passed.
- Preserve the broken service `.venv`, recreate it with `uv sync --project python-service --frozen --extra mlx --python /Users/mhlaghari/miniconda3/bin/python3.11`, verify metadata and a real MLX array operation, then rerun the canonical build. This repaired the environment without changing source or the lockfile. The separate Rapid runtime environment was intact. Frozen transcription and launch checks passed afterward.
- Also move aside old duplicate `dist/* 2` trees before the clean freeze. For a local rebuild at an existing version, preserve the prior release bundle: the build script regenerates stable-named DMG/updater/provenance files even when public publishing is not requested.
