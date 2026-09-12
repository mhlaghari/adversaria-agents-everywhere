# Adversaria Release Hardening Plan

**Status:** Implementation pass complete through Phase 4 plus Phase 5 automation; native/private/credentialed release acceptance remains open  
**Prepared:** 2026-07-14  
**Last executed:** 2026-07-15  
**Reference release:** v0.3.41  
**Primary platform:** macOS first, Windows parity after the macOS release gates pass

## Execution Handoff

This document is the source of truth for the next implementation cycle. A new
agent should read this file, `AGENTS.md`, `STATUS.md`, `HANDOFF.md`, and
`docs/LESSONS_LEARNED.md` before editing code. Then inspect `git status` and
preserve all pre-existing worktree changes. Do not reset, revert, or overwrite
unrelated user changes.

The implementation described in Phases 0–4 and the non-credentialed automation
part of Phase 5 now exists. Continue from [CODEX_TODO.md](./CODEX_TODO.md), not
from the original “start with Phase 0” instruction. Use
[RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md) for gates that require private
data, live audio, clean machines, or Apple credentials. Do not describe those
gates as complete from synthetic/unit evidence.

### 2026-07-15 execution snapshot

- Local quality gates: 259 Python tests, 117 Rust tests (+1 ignored), 13 frontend
  tests, and 4 embedded desktop tests pass; strict lint/build checks are clean.
- The main web entry is 379.85 kB and the complete npm graph has zero known
  advisories.
- Encrypted capture, the private-evaluation harness, versioned onboarding,
  resumable verified model setup, managed Rapid-MLX, CSP/capabilities,
  diagnostics, visual/a11y smoke, and release automation are implemented.
- A frozen Rapid-MLX 0.10.9 runtime served an authenticated synthetic response
  with the pinned Qwen 27B revision.
- A complete ad-hoc packaging smoke built and verified both sidecars, the app,
  updater, DMG, and multi-artifact provenance. It was not installed, notarized,
  or published.
- Remaining blockers are enumerated in the TODO: native 60-minute/forced-quit
  evidence, authorized private corpus baseline, production Formspree endpoint,
  clean-machine model/onboarding runs, remote CI, Apple signing/notarization,
  updater acceptance, and later Windows parity.

## Goal

Move Adversaria from a strong private beta to a reliable, private, installable
public beta. The release must survive process interruption during long meetings,
measure transcription and meeting-output quality against real recordings, run
locally without terminal setup, protect local data, and ship through a repeatable
notarized macOS pipeline.

This is a hardening program, not a redesign. Preserve existing user data,
meeting behavior, and the current visual identity while improving reliability,
setup, test coverage, accessibility, and distribution.

## Locked Decisions

- Deliver macOS first; implement Windows parity only after the macOS acceptance
  suite passes.
- Store the real evaluation corpus privately outside Git. CI uses only synthetic
  or redistributable public fixtures.
- Make the default experience local-first. Cloud/BYOK is an explicit fallback,
  never a silent fallback.
- Require beta registration fields before setup, but allow offline use after a
  valid name, email, and consent are entered. Queue and visibly retry submission.
- Use the same Formspree form as the public landing page for beta registration.
- Encrypt the crash-recovery recording spool at rest.
- Use outcome-based accuracy gates. Establish thresholds from a recorded baseline
  and ratchet them; do not claim a universal accuracy percentage.
- Keep the current interface and make targeted refinements rather than a broad
  visual redesign.
- Apple Developer enrollment is pending. Build and exercise the signing pipeline
  now; notarization is a final release gate once credentials are available.

## Current Baseline

The plan is based on repository and runtime inspection on 2026-07-14:

- Stack: React/Vite frontend, Tauri/Rust desktop shell, and a FastAPI/Python local
  transcription service.
- `npm run build` passes, but the primary JavaScript bundle is about 886 kB
  uncompressed and triggers Vite's chunk-size warning.
- Python tests pass: 250 tests, with one FastAPI/httpx deprecation warning.
- Rust tests pass: 105 passed and 1 ignored.
- Ruff reports 8 issues. Clippy reports one blocking approximate-PI test lint and
  additional warnings.
- There are no committed frontend tests and no GitHub Actions workflows.
- Several frontend and Rust modules are large enough to make safe testing and
  maintenance difficult.
- Audio capture is accumulated in memory and persisted only when capture stops.
  A crash can lose an entire meeting and long sessions can consume substantial
  memory.
- The post-stop pending-meeting workflow is useful and should be retained, but
  cleanup failures can leave orphaned plaintext audio without a user-visible
  recovery state.
- SQLCipher/keychain storage is already a strong base. The webview CSP is unset,
  and CSS still references Google Fonts despite bundled local fonts.
- The existing interface is coherent and usable. The main issues are oversized
  meeting-header whitespace, clipped sidebar filters, excess toolbar rows,
  mixed icon styles, broad text buttons, and low-contrast secondary text.
- The transcription sidecar is packaged, but the local LLM still depends on an
  externally managed Rapid-MLX service.

## Implementation Program

### Phase 0: Protect the Baseline and Add Quality Gates

1. Record the starting state before changing behavior:
   - Preserve the current dirty worktree and identify which changes predate this
     plan.
   - Capture baseline build sizes, test counts, lint findings, startup time, and
     representative screenshots at 1024x720 and a wide desktop viewport.
   - Document any check that cannot run on both macOS and Windows.

2. Make existing checks clean before adding release gates:
   - Resolve all Ruff findings and the FastAPI/httpx deprecation warning.
   - Resolve the blocking Clippy lint and triage remaining warnings. Keep an
     explicit, justified allow only when a dependency or platform API requires it.
   - Keep `npm run build`, Python tests, Rust tests, and native compilation green.

3. Add GitHub Actions for macOS and Windows:
   - Install dependencies from lockfiles.
   - Run frontend type/build checks, frontend tests, Ruff, pytest, Rust formatting
     checks, Clippy with warnings denied for project code, Rust tests, and native
     compile checks.
   - Cache package-manager and compiler artifacts without caching generated release
     bundles as source artifacts.
   - Require the workflow on pull requests once it is green on the default branch.

4. Establish frontend testing:
   - Use Vitest, React Testing Library, and `user-event` for component and workflow
     tests.
   - Mock Tauri IPC with the official Tauri mock utilities at the frontend boundary.
   - Add WebdriverIO with `@wdio/tauri-service` for a small set of embedded-webview
     desktop smoke tests.
   - Cover startup, registration state, setup state, recording controls, pending
     meetings, recovery prompts, transcription completion, cleanup retry, settings,
     and update prompts.

5. Refactor only where needed for testing and bundle control:
   - Extract stateful workflows and repeated UI primitives from the largest
     components without changing behavior.
   - Lazy-load secondary views and heavyweight libraries.
   - Set an initial main-entry JavaScript budget below 500 kB uncompressed. Track
     the budget in CI so it cannot silently regress.

**Phase 0 exit gate:** all local checks and CI jobs pass; essential workflows have
frontend coverage; main bundle is below the recorded budget; no user data or
existing behavior has been intentionally changed.

### Phase 1: Crash-Safe Encrypted Capture

1. Replace full-session in-memory audio vectors with a bounded producer/consumer
   pipeline:
   - Capture callbacks write short frames into bounded queues.
   - Dedicated writer threads persist frames continuously.
   - Backpressure or writer failure must stop capture safely, preserve all completed
     encrypted chunks, and show an actionable error. Never allow unbounded growth.
   - Keep only bounded rolling/delta buffers needed by live captions.

2. Introduce a versioned encrypted spool format:
   - Encrypt each independently recoverable record with XChaCha20-Poly1305.
   - Generate a random nonce prefix per recording asset and combine it with a
     monotonically increasing chunk counter. Nonces must never repeat for a key.
   - Authenticate session ID, channel, audio format, chunk index, and format version
     as additional data.
   - Store a versioned manifest containing sample format, channel identity, time
     bounds, and last committed chunk. On recovery, validate records and discard
     only an incomplete or unauthenticated final record.
   - Flush enough metadata that a forced process termination loses no more than two
     seconds of completed audio.

3. Separate recording-key ownership:
   - Create a dedicated keychain entry such as `adversaria-recordings`; do not reuse
     the database key.
   - Never fall back to a plaintext spool if the keychain is unavailable. Fail the
     recording start with a clear remediation message.
   - Use restrictive file permissions and an application-owned spool directory.

4. Add durable recording-asset state:
   - Add a `recording_assets` table linked to meetings. Use explicit states:
     `capturing`, `pending`, `processing`, and `cleanup_pending`.
   - Persist path, format version, creation/update timestamps, channel metadata,
     last committed chunk, and the last error. Do not store encryption keys.
   - Keep legacy `audio_file_path` readable during migration. New captures use the
     asset table; old pending WAV files are encrypted, verified, and only then
     deleted.

5. Recover on startup:
   - Scan the database and spool directory before normal processing begins.
   - Reconcile known assets, valid orphaned manifests, missing files, and interrupted
     processing attempts idempotently.
   - Create or restore a pending meeting for valid recoverable captures. Queue local
     transcription automatically; ask for confirmation before any cloud upload.
   - Surface recovered meetings and failed cleanup in the existing meeting UI.

6. Decrypt only for processing:
   - Stream-decrypt where the Python service can accept a stream or pipe.
   - If a temporary WAV is required, create it with mode `0600`, delete it after the
     attempt, and let a startup janitor remove stale temporary plaintext after a
     crash.
   - Do not clear the database asset reference until encrypted and temporary files
     are actually deleted. Failed deletion enters `cleanup_pending` and retries with
     visible status.

**Phase 1 exit gate:** a 60-minute capture stays below 128 MB of capture-related
memory; force-quitting the app at multiple points recovers all authenticated audio
except at most the last two seconds; no completed or recovered meeting leaves a
plaintext recording behind after successful processing and cleanup.

### Phase 2: Private Accuracy and Outcome Evaluation

1. Create an evaluation harness that reads a corpus root from
   `ADVERSARIA_EVAL_CORPUS`. Keep recordings, references, reports containing user
   content, and evaluator caches outside Git and explicitly ignored.

2. Define a versioned manifest for each evaluation session containing:
   - Audio assets and channel roles.
   - Language and acoustic-condition labels.
   - Reference transcript and speaker turns, with RTTM where applicable.
   - Reference entities, names, numbers, decisions, and action items.
   - Consent/provenance metadata and an anonymized stable session ID.

3. Build an initial private baseline of at least 20 representative sessions or five
   hours of audio, whichever is greater. Include English, Arabic, code-switching,
   silence, playback bleed, background noise, overlap, long meetings, and two- and
   three-speaker meetings.

4. Produce machine-readable JSON and human-readable HTML reports with:
   - WER for English and WER/CER for Arabic and code-switched slices.
   - DER/JER, speaker-attributed WER, and speaker-count accuracy.
   - Silence/playback hallucination rate.
   - Name, entity, date, and number preservation.
   - Summary factual precision and action-item traceability to transcript evidence.
   - Results by language, duration, noise, overlap, speaker count, model, and app
     version rather than only a global average.

5. Establish baseline-and-ratchet release policy:
   - Zero hallucinated transcript content on the silent-audio suite.
   - At least 95% speaker-count accuracy, entity/number preservation, summary factual
     precision, and action-item traceability on the agreed release set.
   - Zero critical fabricated decisions or commitments.
   - No release slice may regress by more than one absolute percentage point in
     WER, CER, DER, or speaker-attributed WER versus the accepted baseline without
     a documented product decision.
   - Pin model revisions and evaluation configuration in every report.

6. Keep CI privacy-safe. Run deterministic synthetic/public smoke fixtures in CI;
   run the private corpus locally or in an access-controlled environment and attach
   only aggregate, scrubbed release results.

**Phase 2 exit gate:** a reproducible baseline report exists, the release gates pass,
and every supported model profile has a recorded quality result and known limits.

### Phase 3: No-Terminal, Local-First Onboarding

1. Replace the current first-run flag with versioned onboarding and registration
   state. Track completion per required step so interrupted setup resumes safely.

2. Implement required but offline-tolerant registration:
   - Validate name, email, and consent locally before continuing.
   - Submit to the shared Formspree endpoint with only name, email, source, app
     version, platform, and consent timestamp/version.
   - If offline or Formspree fails, persist `pending` state, allow local setup, show
     the pending state in onboarding/settings, and retry with bounded exponential
     backoff plus a manual retry action.
   - Never send recordings, transcripts, meeting metadata, hardware inventory, or
     model choices to Formspree.

3. Make the app own the local LLM lifecycle:
   - Bundle a pinned, telemetry-disabled Rapid-MLX service as a second macOS sidecar.
   - Bind only to loopback on a dynamically selected port, pass an ephemeral
     per-launch credential, and terminate the child on app exit or failed setup.
   - Keep the service version, runtime dependencies, and model compatibility pinned
     and testable. Do not rely on the user launching a terminal server.

4. Add model profiles and setup IPC:
   - Default to the current Qwen 27B 4-bit profile on machines with at least 24 GB
     usable memory and adequate disk space.
   - Default to the supported Rapid 4B profile below 24 GB and clearly label its
     reduced meeting-output quality.
   - Offer explicit BYOK/cloud configuration as an optional fallback. Never send
     content to it until the user selects it and accepts its disclosure.
   - Detect hardware and disk space, list installed models, support resumable model
     download with checksum verification, stream progress, start/warm the service,
     and run a structured smoke inference.

5. Use this first-run sequence:
   - Registration and consent.
   - Local/cloud data-flow disclosure.
   - Hardware and disk check with recommended profile.
   - Model download or explicit BYOK selection.
   - Microphone, system-audio, and accessibility permissions only when needed, with
     retryable status checks.
   - A local sample-summary test that must succeed before setup completes.
   - Optional short capture test.

6. Represent cold starts and model loading honestly in the UI. Disable dependent
   actions until the service is ready and provide retry/reinstall diagnostics rather
   than leaving the interface in an indefinite loading state.

**Phase 3 exit gate:** a clean macOS machine can install the DMG and complete a local
sample summary without Terminal, Homebrew, Python, or a separately launched service;
offline registration queues visibly and later submits successfully.

### Phase 4: Security, Privacy, and Targeted UI Refinement

1. Remove the Google Fonts import and all other remote webview assets. Use the
   bundled fonts and local icons only.

2. Configure a restrictive Tauri CSP and test it in packaged builds. Allow only the
   schemes and loopback endpoints the app actually needs. Because the current UI
   uses inline styles, permit the narrowest temporary style policy necessary, track
   removal of inline styles, and do not use a fully disabled CSP.

3. Split Tauri capabilities by window and workflow. Grant each window only the
   commands, file scopes, shell/sidecar access, and event permissions it uses.

4. Document every network boundary in the product and privacy text: registration,
   update checks, model download, calendar integrations, and user-selected cloud
   providers. Keep local transcription and summarization local by default.

5. Add local diagnostic logs that rotate, redact paths/emails/content, and can be
   exported deliberately by the user. Do not add automatic crash reporting in this
   program.

6. Refine the current UI without redesigning it:
   - Reduce unused meeting-header space and consolidate redundant toolbar rows.
   - Fix clipped sidebar filters and all narrow-window overflow.
   - Replace emoji and handwritten SVG controls with the existing icon library or
     Lucide icons, using icon-only buttons for familiar actions and tooltips where
     meaning is not obvious.
   - Improve secondary-text contrast, visible focus, semantic labels, and keyboard
     navigation to WCAG 2.2 AA targets.
   - Preserve stable dimensions for controls so loading, hover, and translated text
     do not shift the layout.
   - Add visual and accessibility regression checks at 1024x720 and wide desktop
     sizes, including dialogs, long titles, errors, loading, empty, recovery, and
     cleanup-pending states.

**Phase 4 exit gate:** packaged builds have no unintended remote asset requests, CSP
and capabilities are constrained, primary workflows are keyboard-accessible, and
the supported viewport matrix has no clipping, overlap, or unreadable text.

### Phase 5: Signing, Notarization, Updates, and Beta Release

1. Keep release artifacts reproducible from clean checkout and lockfiles. Generate
   provenance containing app version, commit, sidecar versions, model profiles, and
   hashes.

2. Sign nested binaries and both sidecars before signing the app bundle. Use
   Developer ID Application signing, hardened runtime, secure timestamps, and the
   required entitlements. Validate signatures before packaging.

3. Submit the final DMG with `notarytool`, wait for acceptance, retrieve the log on
   failure, staple the ticket, and verify with `codesign`, `spctl`, and Gatekeeper on
   a clean machine. Do not use the obsolete `altool` flow.

4. Maintain separate beta and stable updater channels. Promote the exact tested
   artifact and hash instead of rebuilding for stable. Test interrupted downloads,
   invalid signatures, rollback behavior, and preservation of database, keychain,
   permissions, model, onboarding, and pending recording state across updates.

5. Run clean-machine acceptance on at least a 16 GB and a 32 GB Apple Silicon Mac:
   install, registration, offline retry, permission denial/retry, model selection,
   model interruption/resume, sample summary, capture, forced termination, recovery,
   transcription, cleanup, relaunch, and updater installation.

6. While Apple Developer enrollment is pending, complete and test every packaging
   step that does not require notarization credentials. The public beta remains
   blocked until the final notarized artifact passes the clean-machine suite.

**Phase 5 exit gate:** the same notarized, stapled, signed DMG that passed acceptance
is published to the beta channel; Gatekeeper opens it normally; sidecars terminate
correctly; update and recovery state survive an upgrade.

### Phase 6: Windows Parity

After all macOS gates pass, implement the same bounded encrypted spool, recovery
state machine, local-service ownership, setup diagnostics, security boundaries,
tests, signing, and updater acceptance on Windows. Platform APIs may differ, but
privacy guarantees, recovery behavior, accuracy gates, and visible user states must
remain equivalent. Do not weaken the common contract to accommodate a platform
limitation; document and solve the platform-specific implementation.

## Public Interfaces and Data Contracts

Names may be adapted to existing module conventions, but the behavior and fields are
required.

### Rust domain types

- `RecordingSessionManifestV1`: session/asset IDs, format version, channel role,
  sample format/rate/channels, nonce prefix identifier, committed chunk count, start
  time, and completion marker.
- `RecordingAsset`: meeting link, encrypted path, state, format version, channel
  metadata, last committed chunk, timestamps, and last error.
- `RecordingAssetState`: `capturing | pending | processing | cleanup_pending`.
- `RecoveryResult`: recovered assets, discarded incomplete tails, missing/corrupt
  assets, and cleanup work.
- `RegistrationState`: `unregistered | pending | submitted`, validated local fields,
  consent version/time, retry metadata, and last redacted error.
- `OnboardingState`: schema version, completed steps, selected model profile, and
  setup completion.
- `ModelProfile`: stable ID, display name, model/revision, runtime version, memory and
  disk requirements, capability/quality label, and checksum metadata.
- `SetupStatus` and `SetupProgress`: current step, readiness, downloaded/total bytes,
  recoverable error code, and safe user-facing message.

### Tauri commands and events

Expose narrow commands for:

- Scanning/reconciling recovery assets and retrying cleanup.
- Reading setup status and hardware/model inventory.
- Starting, pausing/resuming, verifying, and removing model downloads.
- Starting, warming, testing, and stopping the managed LLM service.
- Reading/submitting/retrying registration state.
- Exporting redacted diagnostics.

Emit versioned events for recovery results, cleanup state, model-download progress,
service readiness, and setup progress. Event payloads must not contain transcript or
meeting content unless the existing workflow explicitly requires it.

### Database compatibility

- Add versioned migrations for `recording_assets`, registration, and onboarding
  state.
- Migrations must be transactional and idempotent under restart.
- Preserve all existing meetings, preferences, SQLCipher behavior, and readable
  legacy `audio_file_path` values.
- Verify encrypted-spool conversion before deleting legacy plaintext files.
- New binaries must tolerate a partially completed migration and resume safely.

### Evaluation contracts

The private corpus manifest and result schema are internal test interfaces, not app
database tables or telemetry. Version them independently, validate them before an
evaluation run, and record the complete configuration needed to reproduce a report.

## Required Test Scenarios

Automate where practical and keep a short manual clean-machine checklist for OS
permission and Gatekeeper behavior.

- Unit: encryption record round trips, nonce/counter rules, tampering, truncated
  tails, manifest versions, state transitions, retry backoff, registration
  validation, model selection, redaction, and migrations.
- Integration: capture to encrypted spool, dual-channel ordering, writer failure,
  startup reconciliation, legacy WAV conversion, processing retry, temporary-file
  janitor, cleanup retry, sidecar lifecycle, resumable/checksummed model download,
  and updater state preservation.
- Frontend: all onboarding branches, offline registration, denied permissions,
  model errors, pending/recovered meetings, cleanup status, recording controls,
  keyboard operation, and destructive-action confirmation.
- Native smoke: fresh startup, existing-user upgrade, full local setup, capture and
  stop, forced termination and recovery, transcription completion, settings, and
  update prompt inside the embedded Tauri webview.
- Performance: 15-, 60-, and multi-hour simulated captures with bounded memory,
  stable writer throughput, responsive live captions, and no UI event-loop stalls.
- Security: ciphertext-only spool inspection, keychain denial, modified chunks,
  swapped manifests, loopback authentication, CSP violation checks, capability
  denial, redacted logs, and no unintended network traffic.
- Accuracy: silent mic, playback-only, bleed, overlap, noisy rooms, Arabic, English,
  code-switching, long meetings, names/numbers, decisions, and action items.
- Packaging: clean install, Gatekeeper, permission persistence, app relaunch, sidecar
  termination, update interruption, invalid update signature, and retained data.

## Release Definition of Done

The public macOS beta is ready only when all of the following are true:

- CI and local lint, test, build, and native checks are clean.
- A 60-minute forced-termination test meets the two-second recovery and 128 MB
  memory limits.
- Successful processing and startup cleanup leave no plaintext recordings.
- Private accuracy and meeting-outcome gates pass with a stored aggregate report.
- A clean supported Mac completes a local sample summary without terminal setup.
- Offline registration, model interruption, permission denial, sidecar failure,
  capture interruption, transcription failure, and cleanup failure all have tested
  recovery paths.
- The packaged app has a restrictive CSP/capability set and no unintended remote
  assets or network calls.
- The exact published DMG is signed, notarized, stapled, Gatekeeper-verified, and has
  passed clean-machine and updater acceptance.
- Documentation accurately describes local/cloud boundaries, system requirements,
  known model-quality differences, recovery behavior, and support diagnostics.

## Implementation Order and Change Discipline

Use small vertical changes within each phase. Add or update tests in the same change
as behavior. Avoid mixing broad component refactors with capture, encryption, or
migration logic. For risky storage work, land the readable schema and state machine
before switching the writer, and keep backward reads until the new pipeline has
passed upgrade and recovery tests.

Recommended first implementation sequence:

1. Establish clean checks and CI.
2. Add frontend test infrastructure and baseline workflow tests.
3. Add recording-asset schema/state types without changing capture behavior.
4. Implement and fuzz/test the encrypted record format.
5. Switch one capture channel to the bounded writer behind an internal feature flag,
   then complete dual-channel capture and recovery.
6. Build the private evaluation harness and record the baseline before changing ML
   behavior further.
7. Implement registration/onboarding state and managed Rapid-MLX setup.
8. Apply security and targeted UI refinements.
9. Complete packaging, notarization, clean-machine testing, and beta promotion.
10. Begin Windows parity only after the macOS release is accepted.

## Explicit Non-Goals

- A new visual design system or landing page redesign.
- New meeting-analysis features before reliability and release gates pass.
- Automatic cloud fallback or automatic upload of recordings/transcripts.
- Committing the private evaluation corpus or private report content.
- Automatic crash-reporting telemetry.
- Supporting Windows ahead of the accepted macOS reference implementation.
- Replacing SQLCipher or the existing meeting database unless a demonstrated defect
  requires a narrowly scoped fix.

## Research Basis

The architecture and release choices above were checked against current primary
documentation on 2026-07-14:

- [Tauri Content Security Policy](https://v2.tauri.app/security/csp/)
- [Tauri capabilities](https://v2.tauri.app/security/capabilities/)
- [Tauri WebDriver testing](https://v2.tauri.app/develop/tests/webdriver/)
- [Tauri API mocking](https://v2.tauri.app/develop/tests/mocking/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Tauri GitHub Action](https://github.com/tauri-apps/tauri-action)
- [Apple notarization guidance](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- [NIST SCTK speech-recognition scoring](https://github.com/usnistgov/SCTK)
- [pyannote diarization metrics](https://github.com/pyannote/pyannote-metrics)
- [Whisper paper](https://cdn.openai.com/papers/whisper.pdf)
- [RustCrypto XChaCha20-Poly1305](https://docs.rs/chacha20poly1305/latest/chacha20poly1305/)
- [Formspree AJAX submissions](https://help.formspree.io/articles/building-your-form/submit-forms-with-javascript-ajax)
- [Rapid-MLX](https://github.com/raullenchai/Rapid-MLX)
- [MLX-LM server guidance](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md)

Re-check dependency versions and platform documentation when implementing a phase;
do not upgrade packages only because a newer release exists. Pin changes that are
needed for this plan and verify them against the relevant tests and packaged app.
