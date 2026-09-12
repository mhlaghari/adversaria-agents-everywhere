# Decisions (ADR log)

Why the architecture is shaped the way it is. Lightweight ADR format so a future
contributor understands the *why* and doesn't undo a deliberate choice. Add an
entry whenever you make a decision with real alternatives.

Format: **Decision · Context · Alternatives · Why · Status.** Newest first.

---

## ADR-019 — Live captions are two tiers: an English Moonshine PREVIEW re-decoded every 500 ms, replaced per utterance by the Whisper caption

**Status:** ACCEPTED 2026-09-01 (founder: "build item three, both Mac and Windows");
built on `feat/live-captions` the same day, uncommitted at the time of writing.

**Decision.** Keep today's VAD-gated Whisper live captions as the confirmed tier
(any language, any engine) and add a PREVIEW tier in the same `/live_feed`
round-trip: the audio after the confirmed watermark (from the first VAD speech
region, capped to the LAST 8 s) is re-decoded on every 500 ms poll by
**sherpa-onnx Moonshine v2 tiny (quantized ORT export)** and returned as
`partial`; the app shows it grey and replaces it the moment the Whisper caption
for that utterance lands. The preview runs OUTSIDE the Whisper lock, is
English-only (it self-gates on the language Whisper reports per confirmed
utterance), is a pinned ~44 MB profile `live-captions-en` downloaded once
automatically, and degrades to exactly today's behaviour when absent.

**Context.** Windows 11 Live Captions shows words while you speak; ours waited
for the utterance to end (perceived lag ≈ utterance length + 1 s). Recon
2026-09-01 (Muse + Antigravity memos in `.recon/`): Windows uses its on-device
"embedded speech" engine with no public output API, and its app-facing
`Microsoft.Windows.AI.Speech` API is MSIX + mic-device input, so nothing native
carries our loopback stream on both platforms; macOS 26 `SpeechAnalyzer` is Swift-only.
The 09-01 plan assumed sherpa-onnx hosts Moonshine as a STREAMING model; the
installed 1.13.3 exposes Moonshine v1/v2 only as OFFLINE recognizers.

**Alternatives measured (Antigravity probe, this Mac, CPU, 2 threads).**
- Streaming Zipformer transducer (`from_transducer`, true online): RTF 0.01–0.02,
  but ALL-CAPS, no punctuation, split words ("A P I", "DATE OF ACE"), ~19–23%
  rough WER on the test passage; timestamps reset per segment (`start_time`).
- Moonshine v2 tiny re-decoding the tail (chosen): ~6% rough WER, true casing +
  punctuation, 0.13 s cold load, 12 ms (2 s tail) to 49 ms (8 s tail) per decode,
  28 MB archive / 44 MB on disk. Base is no better on this passage at 2× the cost.
- Apple `SpeechAnalyzer` (macOS 26): best native option but needs a Swift sidecar;
  deferred as a future macOS-only tier behind the same contract.
- whisper-streaming / LocalAgreement on the resident Whisper: would contend for
  the Whisper lock and cost ~1 s of decode per poll on Windows CPU.

**Hard constraints discovered.** Moonshine v2's ORT export throws inside ONNX
Runtime for inputs ≥ 10 s (→ 8 s cap, matching the existing force-cut). The
download manifest rejected `.ort` weight files until the predicate learned them.
On short mid-word tails the decoder loops ("the data base to the data base to…");
the preview path trims loops to the sane prefix (`trim_repetition_loop`).

**Consequences.** `/live_feed` → `{captions, partial}`; Rust emits `live-partial`
(replace semantics, cleared on stop); `/health.live_captions_state`. Measured on
the real service: first grey words at 0.5 s, revised every poll, 60–125 ms per
round trip including VAD, Whisper line replaces the preview at each pause.
Follow-ups: LocalAgreement (show only the prefix two consecutive decodes agree
on) as a stability option; Arabic once a comparable small model exists.

## ADR-018 — Meeting projects reuse workspaces, and deleting one preserves its meetings

**Status:** ACCEPTED 2026-08-29; implemented and verified in the working tree
2026-08-30, uncommitted.

**Decision.** A Project in the Meetings tab is the meeting-facing presentation
of an existing `workspaces` row, not a second entity. Filing writes the existing
one-meeting-to-one-workspace binding. Deleting a project removes the workspace
and its bindings but never deletes meetings or action items; those meetings
become unfiled. A Project overview is cached local derived data, grounded in all
filed meetings and standing instructions, and never uses web browsing.

**Context.** The product needs one durable project memory spanning meetings and
the work they create. Separate "thread" and "workspace" concepts would force the
user to understand two containers for one real-world project and would create a
new synchronization problem. Accidental duplicate projects also made deletion
semantics a user-data safety decision rather than a cosmetic menu action.

**Alternatives.** (a) Add a separate `projects` table and synchronize it with
workspaces — rejected as duplicate identity and state. (b) Allow many project
bindings per meeting — deferred because the current product contract is one
primary project per meeting; individual action-item transfer remains the escape
hatch. (c) Cascade-delete filed meetings with a project — rejected as destructive
and inconsistent with a folder/container mental model. (d) Let the Project
overview browse when Web research is on — rejected because overview provenance
must remain the filed meetings; the toggle belongs to agent work.

**Consequences.** The Meetings and Workspaces surfaces share storage, routing,
instructions, and action items. `delete_workspace_on` must explicitly clean
`meeting_workspace_bindings` while preserving meeting rows. Overview-cache
staleness includes meeting sources, standing instructions, and prompt version.
The UI names the different network scopes so enabling task research cannot
silently change the Project overview's source boundary.

---

## ADR-017 — Workspace staffing is per-task, resolved at queue time, and automatic runs need no approval

**Status:** ACCEPTED 2026-08-25 (founder). Supersedes the `addons.is_empty()`
rule shipped earlier the same day.

**Decision.** Which agent and skills a workspace task runs with is decided
**per task**, not per workspace; it is **resolved and persisted when the task is
queued**, not when it runs; and it has exactly two mutually exclusive modes —
`automatic` (the matcher owns the whole combination) and `manual` (the user owns
it; nothing is ever silently added). **Automatic staffing does not require
review before running, including under autopilot** — founder's explicit call:
"No, it doesn't need my eye for automatic." The run receipt is the audit trail.

**Context.** `suggest_staffing` first shipped with the rule "auto-staff only when
the workspace has no addons attached." Design review (Claude + an independent
Codex pass, which converged on this without coordination) found two faults:
attaching a single skill silently disabled *all* automation for every task in
that workspace — an invisible trapdoor — and resolving at run time meant what the
user was shown was not guaranteed to be what ran, especially unattended.
Separately, the founder rejected a catalog panel on the Workspaces tab: with no
workspace selected, "add an agent" had no verb behind it, so its rows advertised
interactivity (a `:hover` background) they did not have.

**Alternatives.** (a) Keep workspace-level attachment as the override — rejected:
tasks in one workspace legitimately need different specialists, so the scope is
wrong. (b) Mixed automatic/manual (auto-fill, then hand-edit) — rejected: the
blend is what made the original rule unpredictable. (c) Gate automatic staffing
behind review — rejected by the founder; it would reintroduce the per-task
decision the automation exists to remove.

**Why.** One task, one explicit answer to "who is about to work on this", visible
before it runs and unchanged by the time it does. Manual is a deliberate act, not
a side effect of having once attached something.

**Consequences.** New `workspace_task_staffing` table (task_id, mode, agent_id,
skill_ids, reason, resolved_at). Workspace-level attach/detach is no longer
consulted for staffing. The Workspaces-tab catalog panel is removed; the
capability list becomes a read-only reference surface, and custom agent/skill
creation moves there rather than living in the task flow.

---

## ADR-016 — One local engine: a managed Ollama sidecar replaces Rapid-MLX (macOS) and the managed llama.cpp engine (Windows)

**Status:** ACCEPTED 2026-08-23 (founder). Founder's rationale, verbatim in
spirit: Ollama exists on both Windows and macOS, Rapid-MLX is messy to ship,
and day-to-day he already runs an Ollama model (`qwen3.5:4b`). The MLX
benchmark is confirmatory, not decisive. **Date:** 2026-08-23.

**Context.** The notes/drafting LLM runs through two engines today: a pinned,
PyInstaller-frozen Rapid-MLX runtime on Apple Silicon (`python-service/rapid-runtime/`,
managed by `setup.rs`, signed in `build-dmg.sh`) and a pinned llama.cpp server on
Windows (`llama_engine.rs`), plus Ollama as the detected/fallback path everywhere.
Embeddings (bge-m3) are Ollama-only, so Macs on the managed runtime have no
semantic search unless the user installs Ollama themselves. Ollama ≥ 0.19 (March
2026, labelled preview) runs MLX on Apple Silicon with > 32 GB unified memory, and
its library carries MLX/NVFP4 tags for our models (`qwen3.6:35b-a3b-nvfp4` 24 GB,
`qwen3.6:27b-mlx` 20 GB, `qwen3.6:27b-nvfp4` 19 GB).

**Measured 2026-08-23 on the founder's M5 Max / 128 GB, same prompt, 220-token
cap, temperature 0:** Rapid-MLX (qwen3.6-35B, brew 0.12.x on :8000) ≈ 102 tok/s
and ignores `max_tokens` (uncapped thinking chain); Ollama 0.32.7 with the GGUF
`qwen3.6:35b` on llama.cpp/Metal 98.5 tok/s generation, 64 tok/s prompt, 15 s
load; `qwen3.5:4b` (founder's daily model) 106–108 tok/s, 3.9 s load — but Ollama
defaulted it to a 262,144-token context (12 GB for a 4B model), so the sidecar
MUST always pass `num_ctx` per RAM tier as the service already does. Ollama's
MLX engine confirmed engaged on this machine (`muse-glimmer:30b-mlx`, a 30B
dense model: 32–36 tok/s, 3.7 s load; server log "MLX engine initialized").
**Ollama-MLX on `qwen3.6:35b-a3b-nvfp4`: 128 tok/s warm (88 cold), prompt
2,900 tok/s warm, 2.6 s load; server log "MLX engine initialized".** That is
+25 % over Rapid-MLX on the same model class, with a 24 GB pull (72 min at
~6.5 MB/s on the founder's connection — budget for it in onboarding copy). A first measurement of 12.8 tok/s for
Rapid-MLX was an artefact of the macOS `syspolicyd` stall (LESSONS 2026-08-23),
not the engine.

**Decision (proposed).** Ship ONE engine on both platforms: a **managed Ollama
sidecar**. Bundle the MIT-licensed `ollama` binary with its ggml + mlx libraries
(≈ 560 MB on disk in the current Ollama.app), run it as an app-owned process on a
loopback port with `OLLAMA_HOST=127.0.0.1:<port>` and `OLLAMA_MODELS` inside the
app-data dir, never ask the user to install anything. Model tiers become Ollama
tags chosen by RAM: MLX/NVFP4 tags on > 32 GB Macs, q4_K_M GGUF below, the same
GGUF tags on Windows (CUDA/Vulkan via Ollama). Chat, drafting, and embeddings
(`bge-m3`) all pull through one API with progress, so "semantic search off" on
new installs disappears. Remove `rapid-runtime/`, the Rapid-MLX branch of
`setup.rs`, its DMG signing, and `llama_engine.rs`.

**Alternatives considered.** (a) Keep Rapid-MLX and add `rapid-mlx[embeddings]`
+ `--embedding-model mlx-community/bge-m3-mlx-fp16` (repo exists; bge-m3 is
XLM-RoBERTa, supported by mlx-embeddings) — keeps MLX on sub-32 GB Macs but keeps
two engines, the frozen-runtime build/sign pipeline, and a Windows engine that
differs from the Mac one. (b) Keep both and add Ollama as a third option — the
worst of both. (c) Ollama-only but require the user to install Ollama — violates
the seamless-onboarding rule (LESSONS: churn kills the paid funnel).

**Consequences.** + One engine, one pull API, one set of tiers, embeddings for
everyone, far less release surface (no PyInstaller runtime, no runtime signing,
no llama.cpp pin on Windows). − No MLX below 32 GB (those Macs run llama.cpp/
Metal, measured within 4 % on the 35B-A3B MoE; small tiers to be re-measured).
− Lose Rapid-MLX's explicit disk-cache privacy flags: Ollama keeps KV cache in
memory only; state that in PRIVACY_NETWORK_BOUNDARIES. − Lose
`served-model-name` / `chat_template_kwargs`; thinking is controlled with
Ollama's `think:false`. − Ollama-MLX is "preview": gate the MLX tags behind a
version check and fall back to GGUF. − Bundle grows by ~0.5 GB vs the frozen
runtime (to be measured against the current DMG).

**Implementation plan (when approved).** One Codex delegation series: (1) sidecar
lifecycle in Rust (spawn/health/stop, port + models dir, version pin, SHA-256 of
the bundled binary in the install plan, like `llama_engine.rs` does today);
(2) tiers → Ollama tags by RAM, pull with progress through the existing setup UI,
`bge-m3` pulled alongside the chat model; (3) service: `LLM_BACKEND=ollama`
everywhere, embedder unchanged; (4) delete Rapid-MLX + llama.cpp code, bundle
scripts, and tests; (5) docs: ARCHITECTURE, HANDOFF runbook, PRIVACY boundaries.
Keep the Ollama-detected path (`ollama:` profiles) for power users who run their
own.

## ADR-015 — Team collaboration: share derived artifacts, never the archive; ship shared-folder, sell self-hosted, defer E2E sync
- **Context (2026-07-25):** Team collaboration is the leading candidate for the
  paid tier — the free/paid line has to fall somewhere, and "more than one
  person" is the only split that doesn't cripple the free product. But
  collaboration means data moves between machines, and "nothing leaves your
  machine" *is* the product. Three buyer shapes: regulated orgs (law, health,
  finance, government — the moat, since cloud notetakers are forbidden there),
  sales teams, and solo consultants who must stay free.
- **The asymmetry the whole design rests on:** what must never leave is the
  **audio and the full transcript**. What a team actually needs is far less —
  the summary, the action items, and the person/client record. The codebase
  already encodes this instinct: `second_brain.rs` exports summaries only and
  refuses to write raw transcripts. Team mode is that rule applied over a
  network: **share derived artifacts, never the archive.**
- **Decision (proposed, sequenced — these are stages, not competitors):**
  1. **Shared folder (ship first, near-zero cost).** The Second Brain export
     already mirrors meetings to a user-chosen folder. Point it at a share the
     team already has (SharePoint, on-prem NAS, network drive) and team sharing
     works with **no infrastructure from us**, on storage the customer's
     compliance team has already approved. Limits: one-way mirror, no conflict
     resolution, no permissions. Its real job is **evidence** — whether teams
     want this at all, and what they reach for first.
  2. **Self-hosted team server (the enterprise product, where the money is).**
     Ship a server binary the firm runs inside its own network: real sync,
     shared people/CRM records, access control. Sold as a commercial license +
     support contract.
  3. **End-to-end encrypted sync (defer).** We host, clients encrypt locally,
     the server only ever stores ciphertext we cannot decrypt (Obsidian Sync
     model), ~$5–10/seat/mo for small teams with no IT. Build only on
     demonstrated demand.
- **Alternatives rejected:** (a) **Hosted cloud freemium** competing with
  Granola/Otter on convenience — surrenders the one thing they structurally
  cannot copy, to fight funded incumbents on their own turf with worse
  economics. (b) **Us holding regulated customers' data**, at any tier: a
  one-person company must not own breach liability, BAAs, incident response,
  and subpoena exposure for hospitals and law firms. Self-hosting moves all of
  it to customers who already staff for it — and those buyers *prefer* it, so
  it isn't even a concession.
- **Trade-off accepted:** stage 1 is deliberately weak (read-mostly, no ACLs)
  and we ship it anyway, because the alternative is designing sync against
  imagined requirements. Stage 3's hard part is **key management** — adding and
  removing members, rotation when someone leaves, and recovery, where the honest
  answer is "the data is unrecoverable."
- **⚠️ Open risk — consent, which is larger than the architecture.** Adversaria
  records bot-free, so the other party often does not know. Defensible for
  private personal notes (you are a participant taking notes); **sharing those
  notes across a firm builds a system that distributes recordings of people who
  never consented**, which lands hardest in exactly the regulated verticals we
  are targeting (two-party-consent jurisdictions, GDPR, privilege). Answerable —
  per-meeting opt-in sharing rather than automatic, a visible shared indicator,
  retention limits, an audit trail of who saw what — but it must be designed
  deliberately, before the first enterprise security review, not after.
- **Status:** **Proposed** (2026-07-25). No code, no ratified pricing. Nothing
  here is committed to; the sequencing and the consent risk are the parts worth
  keeping. Backlog in [TODO.md](./TODO.md) (2026-07-25 section).

## ADR-014 — Auto-update via the Tauri v2 updater, served from a separate PUBLIC releases repo
- **Context:** The Groq-first beta needs to push fixes to non-developer friends
  without re-sending a DMG each time (beta step 3). The Tauri v2 updater fetches a
  `latest.json` manifest + a signed `.app.tar.gz` over plain HTTP — but the source
  repo (`mhlaghari/meeting-note-taker`) is **private**, and private GitHub release
  assets require an auth token, which can't be embedded in a distributed app.
- **Decision:** Wire `tauri-plugin-updater` (+ `tauri-plugin-process` for relaunch).
  Updates are **signed with a minisign key** (`tauri signer generate`; private key
  lives in `~/.tauri/`, never committed; public key compiled into
  `tauri.conf.json`). `bundle.createUpdaterArtifacts: true` makes `tauri build` emit
  the signed `.app.tar.gz` + `.sig`. Host the manifest + artifacts in a **separate
  PUBLIC repo, `LaghariLabs/adversaria-releases`**, so the source stays private; the
  endpoint is `…/releases/latest/download/latest.json`. The app **auto-checks on
  launch** and shows a dismissible toast (`UpdatePrompt.tsx`) → download → relaunch.
  `scripts/build-dmg.sh` signs the artifact when the key is present;
  `scripts/publish-release.sh` builds `latest.json` from the `.sig` and cuts the
  GitHub release.
- **Alternatives:** (a) make the source repo public — rejected (exposes all source).
  (b) embed a GitHub token to read private releases — rejected (extractable from the
  app). (c) static host (S3/R2/Pages) — viable but more setup/cost; deferred.
- **Why:** A dedicated public releases repo is free, keeps source private, and the
  Tauri updater's static-JSON GitHub pattern works out of the box. Minisign signing
  means a stolen release host still can't push a malicious update without the
  private key.
- **Consequences:** new minisign key to safeguard (lose it → can't ship updates to
  installed apps). Releases are a 2-artifact upload (`.app.tar.gz` + `latest.json`).
  **Notarization (beta step 5) is still required** for friends' Gatekeeper to accept
  a downloaded update — until then the updater mechanism works on the dev Mac
  (self-signed) but not unnotarized on others.
- **Status:** Implemented + **round-trip VERIFIED (2026-06-25)** — published v0.3.10
  then v0.3.11 to `LaghariLabs/adversaria-releases`; the installed v0.3.10 detected
  v0.3.11, downloaded, minisign-verified, installed, and relaunched as v0.3.11. ⚠️
  **Known issue:** the updater artifact (`.app.tar.gz`) is produced by `tauri build`
  from the **ad-hoc-signed** app, *before* `build-dmg.sh`'s NotchyPrompter Dev
  re-sign — so an auto-updated app is **ad-hoc signed and loses its TCC grants**
  (mic/screen/calendar reset). Fix: sign the `.app` with the stable identity BEFORE
  the tarball is created (e.g. `APPLE_SIGNING_IDENTITY` for `tauri build`, or
  regenerate + `tauri signer sign` the tarball after re-signing). Resolve alongside
  notarization (step 5), which reworks the signing pipeline regardless.

## ADR-013 — Encryption-at-rest is user-toggleable; biometric (Touch ID) unlock with PIN fallback
- **Context:** Two related security UX problems. (1) ADR-011's encryption-at-rest
  keeps the SQLCipher key in the OS keychain, which makes macOS prompt for the
  login/keychain password on launch (and re-prompt after each re-signed rebuild) —
  the user found this prompt intrusive and wanted control over it. (2) The
  per-meeting privacy lock used a numeric **PIN** (ADR-011's UI gate); the user
  wanted to unlock with their **fingerprint** instead.
- **Decision:** (a) Add `encrypt_db` config (default **true**) and a Settings
  toggle. Off → `init_db` decrypts the DB to plaintext at next launch (a verified,
  backed-up reverse of the forward migration) and deletes the keychain key, ending
  the prompt. The mode is read once at startup (`DB_ENCRYPTED`), so per-request
  `connect()` applies the key only when encrypted; changing it needs a restart
  (same pattern as the cached service URL). (b) Add `biometric_unlock` config
  (default true) + a native `biometric_authenticate` command via the
  **`robius-authentication`** crate (Touch ID on macOS, Windows Hello on Windows,
  OS password fallback). Opening a 🔒 meeting tries biometrics first and **falls
  back to the existing PIN** on failure / no sensor — the PIN is retained, not
  replaced.
- **Alternatives:** *Encryption:* (i) remove encryption entirely — rejected,
  weakens the privacy-first promise. (ii) move the key to a file beside the DB —
  rejected, defeats at-rest encryption (a thief gets both). (iii) gate the key
  behind Touch ID — deferred (more complex, recovery risk). *Biometrics:*
  `objc2-local-authentication` (macOS-only) — rejected in favor of
  `robius-authentication` because the app targets Windows + macOS and the latter
  gives Windows Hello for free.
- **Why:** Keeps encryption **on by default** (privacy preserved) while giving the
  user an explicit, reversible escape hatch for the keychain prompt. Biometrics
  improve the lock UX without dropping the cross-platform PIN fallback. Both
  migrations are non-destructive (backup + row-count verify + atomic swap), mirror
  the proven ADR-011 forward path, and are covered by round-trip unit tests.
- **Consequences:** new Rust dep (`robius-authentication` → objc2 LocalAuthentication
  on macOS; needs `NSFaceIDUsageDescription` in Info.plist and a code-signed app).
  Toggling encryption requires a restart and (turning off) one final keychain
  prompt during the decrypt. No-biometric devices silently use the PIN.
- **Status:** Implemented (v0.3.9) — migration round-trip tests green and
  **user-confirmed working live**: Touch ID unlocks locked meetings, and turning
  the encryption toggle off removes the keychain prompt.

## ADR-012 — Speaker diarization via sherpa-onnx, system-channel only
- **Context:** Multi-party meetings showed every remote participant as a flat
  "Them" — legal/clinical/multi-party buyers need who-said-what (the #1 depth gap
  vs Meetily). The app already isolates the local user ("Me", mic) from the remote
  audio ("Them", system), so only the *system* channel needs diarizing.
- **Decision:** Diarize only the system-audio WAV with **sherpa-onnx**
  (`OfflineSpeakerDiarization`: pyannote-segmentation-3.0 ONNX + a multilingual
  zh+en speaker-embedding model), relabelling system segments "Speaker 1/2/…" by
  time-overlap (mic stays "Me"). Models (~34 MB) download once to a local cache;
  fully offline. Settings toggle, default on. Best-effort — any failure falls
  back to "Them".
- **Alternatives:** (a) **pyannote.audio** — SOTA accuracy, but PyTorch
  (macOS/Linux only, not Windows), gated HuggingFace models needing a token, and
  heavier; rejected. (b) **WhisperX** — wraps pyannote, same gating.
- **Why:** sherpa-onnx is cross-platform (incl. Windows), needs no HF gating,
  is ONNX/lightweight (~34 MB, ~17x realtime on CPU), and freezes cleanly into the
  PyInstaller sidecar. Diarizing only the system channel is simpler and more
  accurate because the user is already separated out. v1 uses numbered speakers;
  renaming is a later enhancement.
- **Consequences:** new runtime dep (sherpa-onnx + its native-lib companion
  sherpa-onnx-core, declared explicitly so `uv sync` keeps it; `collect_all` in
  the PyInstaller spec). Adds a diarization pass per meeting, skippable via the
  toggle. The clustering threshold (0.5 with this embedding model) is the key
  accuracy knob.
- **Status:** Implemented (v0.2.x) — validated end-to-end and confirmed loading
  from the frozen sidecar.

## ADR-011 — Encryption at rest: SQLCipher with a transparent keychain key
- **Context:** Privacy is the product, but `meetings.db` (transcripts, summaries,
  to-dos) was stored as **plaintext** on disk — the per-meeting PIN was only a UI
  gate. Plaintext-at-rest is the first thing a security review flags and directly
  undercuts the "sovereign / compliance-grade privacy" pitch.
- **Decision:** Encrypt the whole database with **SQLCipher** (rusqlite
  `bundled-sqlcipher-vendored-openssl`; FTS5 stays enabled). A random **256-bit key
  is stored in the OS keychain** and applied via `PRAGMA key` on every connection.
  Existing plaintext databases are **migrated in place on first launch** (backup →
  `sqlcipher_export` → verify per-table row counts → atomic swap).
- **Alternatives:** (a) **Passphrase-derived key** (KDF from a user secret) — the
  strongest sovereign claim (DB is useless without the secret, even to the logged-in
  user), but adds a launch unlock prompt and permanent data-loss risk if forgotten;
  **deferred** as a future opt-in "app lock". (b) **Plaintext + rely on FileVault** —
  no protection if the file is copied off, synced, or read by another OS user.
  (c) **App-level field encryption** — partial, complex, and breaks FTS5 search.
- **Why:** The transparent keychain key closes the plaintext-on-disk hole with
  **zero UX change and no lockout risk**, which fits a local-first tool whose users
  have no cloud backup. SQLCipher is the standard for transparent full-DB encryption
  and preserves FTS5. A passphrase tier can layer on later.
- **Consequences:** The MCP server (reads the same file) now needs the key +
  `sqlcipher3` (done, ADR-aligned); reading the key from another process may prompt
  macOS keychain once. **Threat model:** protects against device theft (with
  FileVault), other OS users, and file exfiltration / backup leakage; does **not**
  protect against malware running as the logged-in user.
- **Status:** Implemented on `feat/db-encryption` (v0.2.0) — Rust core + in-place
  migration + MCP read path; 24 Rust tests + a real-data migration (32 meetings
  preserved) verified.

---

## ADR-010 — macOS port: ScreenCaptureKit + cpal capture, MLX transcription, CoreAudio detection
- **Context:** The app was Windows-only (WASAPI loopback, registry mic-detection,
  CUDA Whisper). Porting it to macOS 26 / Apple Silicon (M5 Max) means replacing
  every OS-specific layer while keeping the React UI, SQLite, config, and HTTP
  client untouched. The public `AudioCapture` API (`start`/`stop`/
  `snapshot_system_tail`/`RecordingPaths`) is held stable so `commands.rs` is
  platform-agnostic; only the capture mechanism is `#[cfg]`-gated
  (`audio/wasapi.rs` vs `audio/macos.rs`, deps gated in `Cargo.toml`).
- **System audio — alternatives:** (a) **ScreenCaptureKit** — mature Rust crate
  (`screencapturekit` 7.0.1), pure-Rust, but needs the *Screen Recording* TCC
  grant; (b) **CoreAudio process taps** (macOS 14.4+) — only an audio-recording
  grant (cleaner for a privacy app) but thin/undocumented bindings → likely a
  Swift helper and more build risk; (c) **BlackHole virtual device** — least code
  but forces every user to install a driver and route audio. **Chose (a)** for
  the lowest-risk working port; the Screen-Recording grant is the accepted cost.
  SCK delivers planar f32 @ 48 kHz; the handler interleaves it and reuses the
  existing float-WAV writer (`format_tag = 3`).
- **Microphone — alternatives:** SCK's own `captureMicrophone` (one stream, both
  signals) vs **cpal** (separate stream). **Chose cpal** — capturing the mic on
  an independent thread isolates failures, so a missing/denied mic falls back to
  system-audio-only and never aborts the meeting (mirrors the Windows two-stream
  design and ADR-006).
- **Transcription — alternatives:** faster-whisper on CPU (works, but CTranslate2
  has no Metal backend → slow), whisper.cpp+CoreML (ANE, but a C++/binary
  integration with an AOT model-compile step), **mlx-whisper** (Apple-GPU via MLX,
  pure-`pip`, openai-whisper-compatible result dict). **Chose mlx-whisper**
  (`mlx-community/whisper-large-v3-mlx`) behind a `create_transcriber()` factory:
  auto-selects MLX on arm64 macOS, faster-whisper elsewhere (`WHISPER_BACKEND`
  overrides). It is greedy-only (no `beam_size`) and has no VAD, so
  hallucination-on-silence is suppressed with decoder thresholds
  (`no_speech_threshold`/`logprob_threshold`/`compression_ratio_threshold` +
  `condition_on_previous_text=False`). Shipped as an optional, platform-gated
  `mlx` extra so Windows installs are unaffected. Requires the `ffmpeg` CLI
  (mlx-whisper decodes via ffmpeg; faster-whisper used bundled PyAV).
- **LLM (summarization) — alternatives:** keep Ollama on macOS vs **Rapid-MLX**
  (the user's existing "vLLM-for-Apple" — OpenAI-compatible, runs HF Qwen MLX
  weights). **Chose Rapid-MLX** on macOS: it reuses the ADR-009 backend
  abstraction with *zero new request code* (its default `:8000/v1` already matched
  `LLM_BASE_URL`). `default_llm_backend()` auto-selects `openai` on Apple Silicon
  (Ollama elsewhere; `LLM_BACKEND` overrides), and the default model is
  `qwen3.6-27b` (`mlx-community/Qwen3.6-27B-4bit`, served via `--served-model-name`).
  Verified Rapid-MLX honors `response_format` json_schema (structured notes) and
  `enable_thinking=false`. The module-level `LLM_BACKEND` constant stays `ollama`
  so the Ollama-coupled unit tests are untouched; the service passes the resolved
  backend into `OllamaSummarizer(backend=…)`. Also fixed a stale default-model
  mismatch — the Rust config default was `qwen3:8b` while the service default was
  `qwen3.6:35b-a3b`; non-macOS now uses `qwen3.6:35b-a3b` (ADR-008) and macOS uses
  `qwen3.6-27b`.
- **Meeting detection — alternatives:** process-name polling (`sysinfo`) — coarse,
  "running ≠ in a call" — vs the **CoreAudio process-object list**
  (`kAudioHardwarePropertyProcessObjectList` → per-process
  `kAudioProcessPropertyIsRunningInput` + `kAudioProcessPropertyBundleID`,
  macOS 14.4+). **Chose the CoreAudio list** — it's the precise analog of the
  Windows ConsentStore read (which process is *actively capturing input now*),
  read-only and needs no TCC permission. Hand-rolled FourCC selectors over
  `coreaudio-sys` + `core-foundation`.
- **Why:** Maximize reuse and keep Windows the untouched primary target. The hard
  problem was always system-audio capture; everything else (UI, storage, config,
  Ollama summarization, tray, hotkey) ports for free or with a one-line `#[cfg]`.
- **Status:** Accepted (2026-06-17). Implemented and verified on macOS 26.5 /
  M5 Max: Rust builds + links (ScreenCaptureKit/CoreAudio/cpal), 75 Python tests
  pass, MLX transcription verified on synthesized speech. Transparent meeting
  card needs the `macos-private-api` Tauri feature (+ `app.macOSPrivateApi`).
  Not yet exercised: a real live meeting (needs the Screen-Recording grant + a
  call). See [HANDOFF.md](./HANDOFF.md) for the macOS runbook.

## ADR-009 — LLM behind a config-selectable backend; vLLM (via WSL2) as the concurrency target
- **Context:** Ollama serializes requests on one loaded model — an interactive
  chat stalls behind a running summarization, and an evicted model triggers a
  ~112s cold reload (reproduced: a "HI" chat took 111.6s). We want concurrent,
  non-blocking local inference while staying 100% local and Windows-bound.
- **Alternatives:** (a) just raise `OLLAMA_NUM_PARALLEL`/`keep_alive` — cheapest,
  zero code, likely sufficient, but KV-cache multiplies per slot on 32 GB; (b)
  **vLLM** — best continuous-batching concurrency + guided JSON, but **no native
  Windows** (needs WSL2/Docker; verified against vLLM 0.23.0 docs, 2026-06), which
  collides with the double-click-installer goal; (c) **llama.cpp `llama-server`**
  (CUDA 12.8) — native Windows `.exe`, continuous batching, best-in-class
  JSON-schema, reuses GGUF, installer-friendly.
- **Why:** Decoupled the *decision* from the *wiring*. The summarizer now selects
  a backend by env (`LLM_BACKEND=ollama|openai`, `LLM_BASE_URL`, `LLM_API_KEY`),
  defaulting to Ollama (non-breaking). vLLM/llama-server/LM Studio all speak the
  same OpenAI `/v1/chat/completions` API, so one `_chat_openai` path (httpx,
  `response_format: json_schema`, `chat_template_kwargs.enable_thinking=false`)
  serves any of them. **User chose vLLM via WSL2** as the runtime target despite
  the WSL2 dependency; the abstraction keeps `llama-server` (the
  installer-friendly fallback) and Ollama one env var away. Same change applies to
  Tatweer OS so both apps share the server.
- **Status:** Accepted (2026-06-17). Phase 1 (the backend abstraction) done +
  tested (mock); Phase 2 (stand up vLLM in WSL2, serve `Qwen/Qwen3.6-35B-A3B-FP8`,
  `--gpu-memory-utilization 0.80` to coexist with Whisper) and Phase 3 (Tatweer)
  pending. Note: **GGUF is not reusable on vLLM** — re-pull FP8 safetensors; a
  Blackwell MMQ crash also affects Ollama GGUF on some 5090 setups (background
  risk, not yet hit here). See [HANDOFF.md](./HANDOFF.md) for the WSL2 runbook.

## ADR-008 — Default summarization model is `qwen3.6:35b-a3b`
- **Context:** Needed to pick the local Ollama model that produces the best
  meeting notes. Benchmarked 7 installed models on a real 5,241-word meeting
  transcript (DB meeting #8) via `python-service/bench_models.py`, judged against
  a Notion-AI reference summary of the same meeting.
- **Alternatives:** qwen3:8b (prior default), qwen3:14b, gemma4:31b, gpt-oss:20b,
  mistral-small3.2:24b, llama3.1:8b.
- **Why:** `qwen3.6:35b-a3b` (a sparse MoE — 35B total, ~3B active) gave the best
  note depth and owner attribution — the only model to capture the
  "Phase-1 extraction module already exists but is untested" nuance and to flag
  the domain/subdomain decision as critical — *and* the fastest warm latency
  (~5s vs qwen3:8b's ~200s, gemma4:31b's ~337s). The MoE also loads in ~5s, so it
  avoids the cold-load timeout dense models hit on the first request after a
  reboot. gemma4:31b matched it on quality but is ~60× slower — impractical for a
  near-live tool. Set in `summarizer.py:DEFAULT_MODEL` and the app's
  `config.json:ollama_model`.
- **Status:** Accepted (2026-06-16). Caveats:
  - **Schema drift (handled):** qwen3.6 does *not* strictly honor the `format=`
    JSON schema on long transcripts — it keys sections as `title` instead of
    `heading`, and under a weak prompt nests everything under a single
    `{"meeting_notes": {...}}` wrapper. The tolerant `_render` already aliases
    `title`→`heading`; `summarizer._unwrap_envelope` was added to descend into a
    single-key wrapper so it can't produce empty notes. Net: best-quality model,
    made robust by the parser rather than by the model honoring the schema. See
    `test_summarize_unwraps_nested_envelope`.
  - **Attendees vs ASR:** attendee extraction is limited by ASR quality — names
    garbled in the transcript (e.g. "Alaa", "Mohammed") were missed by every
    model; this is an upstream transcription issue, not the LLM.

## ADR-007 — Documentation lives in `docs/` with a lean `CLAUDE.md` hub
- **Context:** The project needed durable cross-session memory (handoff, lessons,
  todo) and an agent guide.
- **Alternatives:** One giant README; everything in CLAUDE.md; a wiki.
- **Why:** `CLAUDE.md` loads into context every session, so it must stay small —
  it's a hub that links to focused companion docs (one concern each). The README
  stays user-facing; `docs/` is contributor/agent-facing.
- **Status:** Accepted (2026-06-16).

## ADR-006 — Microphone captured as a separate stream, merged by timestamp
- **Context:** System-audio-only recording missed everything the local user said.
- **Alternatives:** (a) mix mic + system into one WAV before transcription;
  (b) a single shared-mode capture; (c) a diarization model on one mixed track.
- **Why:** Two separate WASAPI streams (render-loopback + capture) transcribed
  independently give **free, reliable speaker labels** (`Me` vs `Them`) by
  interleaving segments on start time — no diarization model needed. Mic is
  best-effort so a missing/failed mic never breaks a recording.
- **Status:** Accepted (2026-06-16). Edge case: very short clips may merge
  imperfectly. See [ARCHITECTURE.md](./ARCHITECTURE.md).

## ADR-005 — Re-summarize stored transcripts on demand
- **Context:** Users pick the wrong template at record time and want to redo it.
- **Why:** The transcript is the durable asset; summaries are cheap to regenerate
  locally. A `resummarize_meeting(id, template)` command re-runs summarization and
  replaces the stored summary/title/template — no re-recording.
- **Status:** Accepted (2026-06-16).

## ADR-004 — Audio passed to the Python service by file path, not uploaded
- **Context:** Rust captures audio; Python transcribes it; both on one machine.
- **Alternatives:** multipart upload of WAV bytes over HTTP.
- **Why:** Same-machine, so a path avoids copying multi-MB audio over loopback
  and keeps the contract trivial. Reinforces the local-only model.
- **Status:** Accepted. (`transcribe_bytes` exists for the upload path but isn't
  the primary flow.)

## ADR-003 — Recordings deleted after a *successful* transcription
- **Context:** Privacy-first positioning.
- **Why:** Audio is the most sensitive artifact; transcript + summary are enough
  to keep. Deleting the WAVs right after a successful save minimizes the on-disk
  footprint and is a concrete, demonstrable privacy guarantee.
- **Revision (2026-06-26):** The original rule was "deleted *immediately* after
  save," but `cleanup_recordings` ran unconditionally — so a recording whose
  transcription *failed* (e.g. the ML service was unreachable at stop time) was
  deleted with no meeting saved → **total data loss of the recording**. The rule
  is now narrowed to **"deleted after a *successful* transcription."** On failure
  the audio is **kept** (in `<app-data>/recordings/`, durable across restarts —
  no longer the system temp dir) and a "pending" meeting is saved with
  `audio_file_path = Some(path)` and a "Needs transcription" tag; a **Transcribe**
  button (`transcribe_meeting`) retries the pipeline and deletes the audio only
  once it succeeds. Audio therefore lives on disk **only** while a recording is
  waiting to be transcribed — a deliberate, narrow, UI-surfaced exception.
  *Follow-up:* the kept WAVs are not themselves encrypted at rest (the SQLite DB
  is); encrypting pending audio is a future enhancement.
- **Status:** Accepted (revised 2026-06-26). The old failure-path data-loss bug
  ([TODO.md](./TODO.md) 🔴#0) is fixed.

## ADR-002 — Local models by default; cloud only as explicit opt-in
- **Context:** Privacy is the product. But local 8B models summarize less well
  than frontier cloud models.
- **Why:** Everything (Whisper transcription, Ollama summarization) runs
  on-device with no network egress. A cloud fallback (Claude API) is allowed only
  behind a per-run, clearly-surfaced opt-in — never automatic, never on error.
  The `claude_api_key` config field is the stub.
- **Status:** Accepted; cloud fallback not yet implemented (TODO 🟠#7).

## ADR-001 — Three-layer split: React UI · Tauri/Rust · Python ML service
- **Context:** Need native Windows audio capture, a good UI, and a mature ML
  ecosystem (Whisper, LLMs) — no single language does all three well.
- **Alternatives:** Pure Electron + JS ML (weak native audio + ML); pure Rust ML
  (immature Whisper/LLM bindings); Python desktop GUI (poor UX, packaging).
- **Why:** Rust/Tauri gives native WASAPI capture, a small footprint, and a web
  UI; Python owns ML where the libraries actually live (faster-whisper, Ollama).
  They communicate over localhost HTTP, a clean process boundary.
- **Trade-off accepted:** two runtimes to ship → the sidecar packaging work in
  [TODO.md](./TODO.md) 🔵.
- **Status:** Accepted (Phase 1). See
  [`superpowers/specs/2026-06-11-meeting-note-taker-design.md`](./superpowers/specs/2026-06-11-meeting-note-taker-design.md).
