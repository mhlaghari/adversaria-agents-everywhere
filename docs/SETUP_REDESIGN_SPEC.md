# Setup & Settings Redesign — Spec

> **STATUS 2026-07-28: IMPLEMENTED — all five packages, commits
> `22e7e83`…`58726c6` (progress fix · 3-screen wizard + status strip · 5-tab
> settings · Windows managed engine + consent card · pre-meeting notification).
> All automated gates green. **Open:** the manual QA gate below (fresh macOS
> account, fresh Win11 box) and the public sync PR's Windows CI.
> One deviation from §A: hf_hub 1.19 writes `<sha256>.<uuid8>.incomplete`, not
> plain `.incomplete` — the fix globs both.
> **2026-07-31: a real Windows first-run failure exposed the V2 whisper rule as
> broken in practice — see the V3 addendum at the bottom; it supersedes V2's
> whisper-during-setup behavior and is being implemented now.**

_Decided 2026-07-27 with Hamza. One combined release: honest download progress,
a 3-screen setup, a 5-tab settings IA, a transparent managed Windows engine,
and a pre-meeting notification. Nothing ships piecemeal; one QA pass covers it._

**Why now:** the current 7-step wizard plus a progress bar that freezes at ~5%
for half an hour is exactly the moment beta users quit ("churn kills the paid
funnel"). Windows works only with an expert driving. Settings bury the user's
name under Voice Transcription and leak engine jargon ("Rapid-MLX / Ollama",
model pulls) into user-facing copy.

**Base branch:** land `feat/windows-port` first (public PR #1 is green on all
three checks), then branch this work off the merged result. This redesign
touches the same files the port touched (`Welcome.tsx`, `setup.rs`,
`model_setup.py`, `commands.rs`) — building on master would guarantee a painful
merge.

**Non-goals:** no cloud-provider changes beyond relocation to Advanced, no
Whisper-GPU work on Windows, no visual design-system overhaul, no changes to
recording/transcription internals.

---

## A. Byte-accurate download progress (the root-cause fix)

**Current defect** — `python-service/src/model_setup.py:120-131`
(`_downloaded_bytes`) stats files under `snapshots/<revision>/`. huggingface_hub
streams into `blobs/<etag>.incomplete` and only materializes a file into
`snapshots/` when that file *completes*. Result: small files finish → ~5%,
then the multi-GB weight shard shows zero movement for its entire download,
then the bar jumps to done. This is the exact reported symptom.

**Change** — for each `ExpectedFile`, count the first that exists of:
1. `snapshots/<revision>/<name>` (completed file — capped at `file.size`),
2. `blobs/<sha256>` (completed blob, not yet linked),
3. `blobs/<sha256>.incomplete` (in-flight — this is where progress lives).

For LFS files the blob filename **is** the manifest `sha256`
(`model_setup.py:109` already captures it). Non-LFS files (`sha256 = None`)
are KBs of config; counting them only on completion is fine.

**Constraints:**
- Monotonic per file: never report more than `file.size`.
- Windows: the cache is symlink-less (hf_hub copies/duplicates); the three-path
  probe above must be verified against a real Windows cache layout, not assumed.
- Keep `HF_HUB_DISABLE_XET=1` on the spawned sidecar (`commands.rs:121`) — xet
  bypasses the `.incomplete` accounting entirely *and* is the known
  hang-at-0-bytes gotcha (LESSONS_LEARNED).

**Accept when:**
- pytest: mocked cache layouts (snapshot-only, blob-only, `.incomplete`
  partial, mixed) return correct byte counts; existing 291 tests stay green.
- Live check: during a fresh ≥5 GB model download the wizard bar advances
  visibly every few seconds from ~0% to 100%, no plateau longer than ~30 s.

---

## B. Setup: 7 steps → 3 screens

**Current** — `src/components/Welcome.tsx:37-45`: registration → disclosure →
hardware → model → permissions → sample → capture.

**New flow:**

| # | Screen | Contents |
|---|--------|----------|
| 1 | **You** | Name + email + beta consent (existing registration, unchanged wire: `registration.rs:179` already persists `config.user_name`). One line of copy replaces the disclosure step: "Everything runs on this {Mac\|PC} — nothing is uploaded." Cloud-provider setup moves to Settings → AI Model → Advanced. |
| 2 | **Permissions** | The existing live mic + system-audio grants (keep as-is — it's good). **Auto-skipped on Windows** (no TCC): `completed_steps` gets `permissions` stamped automatically. |
| 3 | **Ready** | (a) One sentence, not a screen: "Recommended for your {N} GB {device}: {model}" with a quiet "Change model" link expanding the existing profile list. (b) The **single aggregate progress bar** (package A makes it honest). (c) New toggle: **"Notify me before my meetings start"** (package E). (d) Primary button **"Start using Adversaria"** — enabled immediately; downloads continue in-app. |

**Deleted as steps** (logic survives, screens don't):
- *disclosure* → one line on screen 1; `llm_provider` defaults to `local`.
- *hardware* → feeds the recommendation silently (`setup.rs::setup_status`
  already computes it); no screen.
- *model* → recommendation auto-selected; picker demoted to a disclosure.
- *sample* → runs automatically in the background once the model is ready;
  surfaces as a ✓ toast / status-strip entry, never blocks. Failure surfaces in
  the status strip with one retry button.
- *capture* → merged into Ready.

**Post-wizard download visibility:** when setup completes before downloads do,
the main app shows a slim status strip (reuse `welcome-download` styling) with
the same aggregate bar until `ready`. No terminal, no retries needed — errors
show one "Retry" button (existing `startModelDownload` retry path).

**Migration:** existing `completed_steps` values map onto the new three steps
(registration→You; permissions→Permissions; everything else → Ready). A
half-finished old wizard must resume cleanly, not restart.

**Accept when:**
- Fresh macOS user account (the ship ritual): DMG → recording-capable app in 3
  screens, no manual retries, no dead ends; quitting mid-download and
  relaunching resumes both wizard state and downloads.
- `user_name` typed on screen 1 appears in Settings → General on first open.
- vitest: step-order, Windows auto-skip, migration mapping.

---

## C. Settings: 8 tabs + 3 stowaways → 5 tabs

**Current** — `Settings.tsx` (1,773 lines): AI Engine, Prompts & Templates,
Voice Transcription (contains **Your Name** at :1240), Auto-Stop & Detection,
Security & Privacy Lock, Calendar, Data & Backup (+ Support diagnostics +
Second Brain embedded), Feedback. Engine jargon leaks: "Local (Rapid-MLX /
Ollama)" (:687).

**Research basis:** Granola exposes almost nothing — Profile (name/context)
first, then a couple of preference groups; macOS System Settings / NN-g
progressive disclosure: few primary options, advanced behind explicit
"Advanced…" disclosures.

**New IA:**

| Tab | Contents |
|-----|----------|
| **General** | **Your name** (first field), notifications (pre-meeting toggle + minutes, to-do digest), global hotkey |
| **AI Model** | One card: current model, status dot, live progress bar when downloading, "Change model" (recommended first, sizes in GB). **Advanced** disclosure: cloud provider (moved from wizard), engine details. |
| **Recording** | Transcription model/quality, meeting detection, auto-stop |
| **Templates & Calendar** | Prompt templates, calendar connection |
| **Privacy & Data** | Security lock, data & backup, diagnostics, Second Brain, feedback |

**Copy rule (enforced):** no user-facing string may contain `MLX`, `Rapid`,
`pull`, `GGUF`, `CTranslate2`, or raw repo ids. Say what happens instead:
"Downloads Qwen 9B (~6 GB), recommended for this machine." Add a vitest that
greps rendered Settings/Welcome copy for the forbidden terms — same pattern as
the existing cross-language constant-drift guard.

**Accept when:** 5 tabs; name in General; jargon test passes; every existing
setting still reachable (none silently dropped — moving ≠ removing);
`Settings.test.tsx` extended for the new tab map.

---

## D. Windows: transparent managed local engine

**Gap:** `feat/windows-port` runs the app, but local notes require the user to
install Ollama and pull a model by hand — unusable for office deployment.

**Decision (Hamza, 2026-07-27):** managed install, **transparent and
auditable** — sovereignty means the app says exactly what it will install and
download, with pinned versions and hashes in the open-source repo, and asks
first. Detect what's already there; recommend by hardware; degrade to guidance
if detection fails.

**Flow (Ready screen, Windows only):**
1. **Detect** existing runtimes: Ollama service (`setup_status` already lists
   its models on the port branch) and a previously managed llama.cpp install.
   If found → offer those models first; no new install proposed.
2. **Detect hardware:** RAM (sysinfo, existing) + GPU/VRAM (NVIDIA via
   `nvidia-smi`; otherwise report integrated/none). Detection failure ⇒ treat
   as CPU-only and say so.
3. **Propose, explicitly:** "Adversaria will install **llama.cpp server
   {version}** ({size} MB, SHA-256 shown, from github.com/ggml-org/llama.cpp
   releases) and download **{model}** ({size} GB, pinned revision shown) —
   recommended for your {RAM} GB RAM / {GPU}." Buttons: **Install** /
   **Use my own Ollama instead** / **Not now** (guidance lands in Settings →
   AI Model).
4. **Install + download** into app-data using the *same* pinned-manifest,
   checksum-verified pipeline as the Mac models (`model_setup.py` — GGUF pins
   are just new `ModelPin` entries), with the package-A progress bar covering
   engine + model together. Log the install to `diagnostics` (auditable).
5. **Run managed** — llama-server becomes a second managed-process engine
   beside Rapid-MLX (the port branch already split managed-process vs
   external-service shapes; this reuses the managed shape: loopback port,
   random API key, health poll — mirror `setup.rs::start`).

**Model tiers (GGUF, mirroring the Mac's 27B/9B/4B logic):** exact pinned
repos/revisions/quantizations chosen at implementation time from current
Hugging Face state — **per Principle #1, verify current llama.cpp release
assets and Qwen GGUF availability then; do not trust this spec's memory.**
Prefer the Vulkan llama.cpp build if current releases support it well — GPU
acceleration on NVIDIA/AMD/Intel without CUDA's multi-GB payload (the NSIS
~2 GB packaging ceiling is documented in the port commit).

**Accept when:**
- Fresh Windows 11 machine, no Ollama, non-admin user: setup completes to a
  passing background sample with zero terminal use; every installed artifact
  was named on-screen with version + hash before install.
- Machine with Ollama + pulled models: its models are offered; nothing new
  installed without consent.
- "Not now" leaves the app usable (recording + transcription) with a clear
  Settings → AI Model path to finish later.

---

## E. Pre-meeting notification (new, small)

Nothing like this exists: `detection.rs` banners when a meeting app *starts
capturing*; `reminders.rs` is the 9 a.m. to-do digest. This is calendar-based.

- Config: `meeting_reminder_enabled: bool`, `meeting_reminder_minutes: u32`
  (default 5). Set from the wizard toggle (screen 3) and Settings → General.
- A background check on the existing reminders-thread pattern reads upcoming
  events from the calendar module and fires one OS notification per event via
  `tauri_plugin_notification` (already a dependency), N minutes before start.
  Once per event, no repeats, silent when calendar isn't connected.
- Wizard toggle ON + no calendar connected ⇒ General shows a gentle "Connect
  your calendar to get meeting reminders" hint, not an error.

**Accept when:** unit tests for fire-once/window logic; manual: connected
calendar fires at T−N; toggle off fires nothing.

---

## QA gate (one pass, whole package)

1. Fresh macOS user account: full journey — DMG → 3 screens → live progress →
   background sample ✓ → name visible in General → reminder fires.
2. Fresh Windows 11 VM or office machine: journey above + transparent engine
   install; second run on an Ollama machine.
3. Existing-user upgrade: no wizard reappearance, settings migrated into new
   tabs, nothing lost.
4. Gates: cargo tests, pytest, vitest (incl. new jargon + step-order tests),
   `tsc`, clippy `-D warnings`, fmt — both platforms via public-repo CI
   (sync with `--pr`).

## Sequencing inside the combined effort

1. Merge `feat/windows-port` (workspace) after public PR #1 confirms green.
2. Package A (progress truth) — everything else displays through it.
3. Packages B + C together (they share copy, components, and the step/tab map).
4. Package D (Windows engine) — depends on A's pipeline and B's Ready screen.
5. Package E rides B's toggle and C's General tab.
6. QA gate, then one release.
---

## V2 addendum (2026-07-28, after Hamza's fresh-account test — SUPERSEDES parts of §B/§D UI)

**Verdict on v1:** auto-downloading the recommended LLM during setup was wrong
— it railroads API users and re-fetches per macOS account invisibly. Meetily's
pattern (provider dropdown; models-you-already-have listed; missing recommended
model labeled, downloaded only on click) is the model. Decisions, all Hamza's:

1. **Wizard = truly minimal.** You → Permissions (macOS) → Done. NO model UI,
   NO LLM download, ever. Only Whisper (~3 GB, no API substitute) may cache in
   the background during setup, only when absent, with one disclosure line.
2. **One-time guided tour at first app entry** (hand-rolled coach marks:
   spotlight overlay, Next/Skip): Record → meetings → to-dos → ends ON
   Settings › AI Model where the engine choice actually happens. Skippable;
   persisted via `tour_completed`; shown once to existing users too (the
   settings moved — the tour doubles as the "what changed" walkthrough).
3. **Settings › AI Model, Meetily-style:** provider dropdown FIRST (On this
   Mac / Ollama-detected / API provider with presets — API is first-class, not
   "Advanced"). Local shows a dropdown of INSTALLED models; the
   hardware-recommended model, when missing, appears as "Recommended for your
   machine (not downloaded)" with an explicit Download button + inline
   byte-accurate progress. The Windows consent card appears on that click.
4. **No-engine is a legal state.** Meeting ends with no engine → notes pane
   shows "Transcript saved — choose how notes get written → Settings" and
   notes generate retroactively once an engine exists. The wizard's background
   auto-sample dies with this: verification is the first real generation.
5. **Status strip shows in-flight downloads only** (whisper caching disclosed
   at setup + anything the user started); no sample logic.

Accept when: fresh account reaches the app in <60 s with zero LLM bytes
downloaded; tour lands on AI Model; clicking Download is the only thing that
ever starts an LLM fetch; a no-engine meeting produces the CTA, and notes
appear after configuring an engine.

---

## V3 addendum (2026-07-31, after the first real Windows user failure — SUPERSEDES V2's whisper-during-setup rule)

**Trigger:** a friend's fresh Windows 0.3.68 install produced
`Transcription failed: {"detail":"Transcriber not initialized"}`. Full trace
(file:line, live reproduction) in the 2026-07-31 session. Root cause class: the
whisper model was never part of setup — faster-whisper downloads ~3 GB
*synchronously inside the service lifespan* (`server.py:121` →
`transcriber.py:848`), the service is unreachable throughout, dies permanently
if the fetch fails, and no UI notices. The V2 "quiet background cache" kick is
a silent no-op on fresh Windows (`Welcome.tsx:131-136` fires while the port is
still unbound, error swallowed).

**Decisions (Hamza, 2026-07-31):**

1. **Nothing downloads automatically — not even Whisper.** V2's "whisper may
   cache in the background during setup" rule is dead. The app *guides* the
   user to download whichever model they need: wizard Ready screen states
   what's missing with a CTA into Settings › AI Model; a persistent chip in
   the app chrome shows "Transcription model needed — Set up" /
   "Downloading — N %" until ready; a transcribe attempt with no model opens
   the model manager. Downloads start only on an explicit click, and always
   render byte-accurate progress (Package A pipeline).
2. **Degrade-but-honest, never gate.** Recording always works. A meeting
   recorded before the model exists shows "Waiting for the transcription
   model" on its card and transcribes automatically when the model is ready.
3. **Windows default transcription model → `large-v3-turbo`**
   (`deepdml/faster-whisper-large-v3-turbo-ct2`, rev `4df90f7`, ~1.6 GB —
   verified live on HF 2026-07-31; already in `_CT2_WHISPER_MODELS`).
   `large-v3` stays as the opt-in "Precise" tier. macOS default unchanged.

**Engineering contract (the resilience layer under the UX):**

- **Service starts model-less in seconds.** Transcriber init moves out of the
  lifespan into a background thread with `local_files_only=True` — a missing
  model can never block or kill the process. New module state
  `loading | ready | missing | error`, reported by `/health` as
  `transcriber_state`. MLX's transcribe-time auto-download is also gated: a
  transcribe request whose model repo is not cached returns the structured 503
  below instead of sneaking a download.
- **Self-healing init.** `/transcribe` with a `None` transcriber re-attempts
  init if the model is now cached; a completed whisper profile download
  triggers re-init via callback. "Restart the app" is no longer a recovery
  step.
- **Structured errors.** The 503 becomes
  `{"detail": {"code": "transcriber_missing" | "transcriber_loading" |
  "transcriber_error", "message": …}}`. Rust translates codes to human
  sentences; raw response bodies never reach React (`http_client.rs:112,141`).
- **`HF_HUB_DISABLE_XET=1` on the Windows sidecar too** (was macOS-only,
  `commands.rs:126` — the known 0-byte-stall pairing ships on Windows today).
- **Sidecar watchdog + file logging.** Respawn on exit with backoff; child
  stdout/stderr go to an app-data log file (frozen builds currently log to
  devnull — the friend's machine was undiagnosable).
- **Transcript persists before summarize** (`commands.rs:1177` vs `:1204` —
  today a no-engine meeting throws the transcript away and loops). Pending
  notes generate retroactively once an engine is configured; pending
  recordings transcribe automatically once the whisper model is ready.
- **Whisper joins the pinned pipeline.** `model_setup` gains per-model whisper
  pins so every curated model downloads with byte progress, resume, checksum,
  and the four error buckets. Fix the manifest weight-file guard to accept
  `model.bin` (CT2 repos ship no `.safetensors` — the guard as written fails
  every CT2 whisper download).
- **Progress must survive navigation.** Download state lives backend-side
  only; Settings re-attaches on mount; the status strip loses its
  session-latch and shows anything in flight, by name.

**Phase B (BUILT 2026-08-01, same working tree):** tour v2 — teaches the
record → transcript → notes flow (spotlights the actual meeting list and
to-dos board, not nav buttons), replayable from Settings › General, Back/Esc/
arrow keys, never starts over Settings or a download error, and when no model
exists the final step names the consequence and ends on "Got it — I'll
download it here" — plus the Granola-style seeded demo meeting
(`src-tauri/src/demo.rs`): one ordinary, deletable meeting row with a
realistic dual-capture transcript and house-format notes whose Action Items
seed the to-dos board; fresh installs only (`demo_meeting_seeded` flag AND
empty meetings table), never re-seeded.

Accept when: a fresh Windows VM (throttled network) and a fresh macOS account
both: reach the app in <60 s with zero model bytes fetched; show the guide
chip until the transcription model is explicitly downloaded with live byte
progress; record-before-download produces a meeting that transcribes itself
once the model lands; killing the network mid-download yields a human error
with a working Retry; killing the sidecar mid-session yields an automatic
respawn; and no raw JSON ever renders in the UI. QA ritual gains the
throttled-Windows-VM and HF-blocked passes.
