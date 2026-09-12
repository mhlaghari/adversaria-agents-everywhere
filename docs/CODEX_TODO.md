# Codex Release-Hardening TODO

**Updated:** 2026-07-15  
**Source of truth:** [CODEX_PLAN.md](./CODEX_PLAN.md)

This checklist separates implementation from acceptance evidence. A phase is
complete only when its exit gate has been exercised on the required data,
hardware, and distribution environment.

## Current position

- [x] Phase 0 — local baseline and quality gates implemented.
  - [x] macOS/Windows CI workflow and macOS embedded-app smoke workflow.
  - [x] Frontend workflow tests, Rust/Python strict checks, and bundle budget.
  - [x] Current local gate: 259 Python, 117 Rust (+1 ignored), 13 frontend, and
    4 embedded desktop tests pass.
  - [x] Main entry reduced from 885.71 kB to 379.85 kB; 500 kB limit enforced.
  - [x] npm production and complete dependency graphs have zero known advisories.
  - [x] Fresh macOS debug bundles are ad-hoc signed and launched through an
    isolated supervised path; two consecutive runs passed without orphaning a
    staged process or WebDriver listener.
  - [ ] Observe the macOS and Windows jobs on the published branch/PR.

- [ ] Phase 1 — crash-safe encrypted capture; implementation complete, native
  acceptance open.
  - [x] Bounded native capture queues and 15-second live-caption buffer.
  - [x] Versioned XChaCha20-Poly1305 records with AAD and monotonic nonces.
  - [x] Dedicated OS-keychain recording key; no plaintext fallback.
  - [x] Durable `recording_assets` states and verified legacy-WAV migration.
  - [x] Startup reconciliation, local auto-resume, pending/cleanup state, and retry.
  - [x] Streaming authenticated decrypt into mode-0600 WAVs plus startup janitor.
  - [x] Backpressure/writer warnings preserve committed recoverable audio.
  - [x] Automated incomplete-tail, tamper, and bounded-live-buffer tests.
  - [ ] Run real macOS force-quit tests during capture at the acceptance boundaries.
  - [ ] Record a real 60-minute capture and prove capture-related RSS stays below
    128 MB and authenticated loss is at most two seconds.
  - [ ] Run native Windows capture/recovery parity after macOS acceptance.

- [ ] Phase 2 — private accuracy and meeting-outcome evaluation; harness complete,
  private baseline open.
  - [x] Versioned corpus/result schemas and validation.
  - [x] WER, CER, DER, JER, speaker-attributed WER, silence, entity/number,
    factual-precision, decision-fabrication, and action-traceability metrics.
  - [x] Slice/model gates, baseline comparison, JSON/HTML aggregate reporting.
  - [x] Deterministic synthetic CI fixture passes without private content.
  - [ ] Add an authorized private corpus of at least 20 sessions or five hours,
    including every required language/audio slice.
  - [ ] Run both supported model profiles, store the scrubbed aggregate baseline,
    and document known limits.

- [ ] Phase 3 — no-terminal local-first onboarding; implementation and frozen
  runtime smoke complete, clean-machine acceptance open.
  - [x] Versioned registration/onboarding state and legacy migration.
  - [x] Offline-tolerant registration with bounded retry and manual retry UI.
  - [x] Seven-step restart-safe onboarding with explicit local/cloud boundaries.
  - [x] Hardware-based 27B/4B profile recommendation and immutable revisions.
  - [x] Resumable Hugging Face download with per-file SHA-256 verification.
  - [x] Bundled pinned Rapid-MLX 0.10.9 runtime and automatic lifecycle ownership.
  - [x] Dynamic loopback port, per-launch credential, telemetry/caches disabled,
    and child termination on shutdown.
  - [x] Frozen 27B runtime served a synthetic authenticated inference using the
    exact pinned model revision with no terminal-managed service.
  - [ ] Supply the production Formspree endpoint used by the landing page.
  - [ ] Test actual interrupted model download/resume on a clean supported Mac.
  - [ ] Complete the full onboarding and sample-summary path from the DMG on clean
    16 GB and 32 GB Apple-Silicon Macs.

- [ ] Phase 4 — security, privacy, accessibility, and targeted UI refinement;
  core boundaries complete, full state matrix open.
  - [x] Bundled Inter font and zero remote webview assets.
  - [x] Restrictive CSP with a tracked temporary `style-src 'unsafe-inline'`.
  - [x] Window-specific plugin capabilities for main, notification, and bubble.
  - [x] Network-boundary and local/cloud privacy documentation.
  - [x] Rotating local diagnostics with path/email/content redaction and explicit
    user-controlled export only.
  - [x] Lucide controls replace UI emoji/handwritten control SVGs; contrast,
    responsive header, focus-visible, and semantic labels improved.
  - [x] Packaged-webview assertions cover no remote requests, local font,
    accessible names, keyboard focus, and 1024px navigation/overflow.
  - [x] Retina-aware Phase 4 screenshots at minimum and wide CSS viewports.
  - [ ] Remove 149 existing inline styles so CSP can drop `unsafe-inline`.
  - [ ] Add visual/accessibility fixtures for long titles, dialogs, errors,
    loading, recovery, cleanup-pending, and onboarding states.
  - [ ] Audit and guard sensitive custom Tauri commands by invoking window label;
    plugin permissions are split, but custom commands remain globally registered.

- [ ] Phase 5 — signed/notarized beta distribution; automation and ad-hoc smoke
  complete, credentialed acceptance open.
  - [x] Separate beta/stable updater endpoints and immutable model contract.
  - [x] Release mode fails closed without Formspree, Developer ID, updater key,
    and notarization profile.
  - [x] Nested Mach-O signing, hardened runtime, validation, DMG build, optional
    notarization/stapling, and multi-artifact provenance automation.
  - [x] Updater archive is repacked after final app signing, re-signed, extracted,
    byte-compared, and deep-signature checked.
  - [x] Complete ad-hoc packaging smoke produced a 786,824,914-byte DMG, signed
    657,904,926-byte updater archive, signature, and SHA-256 provenance.
  - [x] Manual Apple-Silicon release-candidate workflow added; it uploads the exact
    candidate for acceptance and does not silently publish stable.
  - [ ] Configure Developer ID/notary credentials and a clean ARM64 release runner.
  - [ ] Produce a Developer-ID-signed, notarized, stapled Gatekeeper-accepted DMG.
  - [ ] Run the clean-machine matrix on 16 GB and 32 GB Macs.
  - [ ] Test interrupted/invalid updater behavior and data/keychain/permission/
    onboarding/pending-recording preservation across an upgrade.
  - [ ] Publish the exact accepted artifact to beta; promote the same bytes to
    stable only after the beta gate.

- [ ] Phase 6 — Windows parity. Deliberately deferred until macOS Phase 5 passes.

## Inputs that cannot be fabricated in the repository

- Production `https://formspree.io/f/...` endpoint shared with the landing page.
- Authorized private evaluation corpus and human reference annotations.
- Apple Developer ID certificate, notarization credentials, and clean test Macs.
- Published branch/PR for remote macOS and Windows CI evidence.

## Verification commands

```bash
npm run build
npm run test:coverage
npm audit --json
cd python-service && uv run --frozen ruff check . && uv run --frozen pytest -q
cd ../src-tauri && cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-targets && cargo check --all-targets --all-features
cd .. && npm run test:e2e:build && npm run test:e2e
```

Use [RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md) for evidence that requires
real recording, private data, credentials, or clean machines.
