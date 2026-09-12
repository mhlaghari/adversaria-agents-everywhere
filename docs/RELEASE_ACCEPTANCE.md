# Adversaria Release Acceptance Record

Use this document for evidence that cannot be established by synthetic/unit
tests. Attach only redacted aggregate results; never commit recordings,
transcripts, emails, local paths, credentials, or private evaluation reports.

## Candidate identity

- [ ] Version/tag:
- [ ] Commit SHA and clean-worktree status:
- [ ] DMG filename, bytes, SHA-256:
- [ ] Updater archive filename, bytes, SHA-256:
- [ ] Updater signature SHA-256:
- [ ] Provenance reviewed and matches all artifacts:
- [ ] Beta endpoint references this exact updater archive/signature:

## Phase 1 — capture and recovery

Run with a synthetic/non-confidential source. Record peak capture-related RSS,
spool duration, last authenticated timestamp, recovery time, final cleanup, and
result. Repeat force quit at least during initial capture, steady-state capture,
record commit, stop/finalize, transcription preparation, and cleanup.

- [ ] 60-minute capture: peak capture-related RSS <128 MB.
- [ ] Every recovered asset loses at most the final two seconds.
- [ ] Incomplete tails are discarded; authenticated chunks are retained.
- [ ] Recovered meeting becomes visible and retryable exactly once.
- [ ] Successful processing removes spool and temporary plaintext.
- [ ] Forced cleanup failure shows `cleanup_pending`; retry succeeds.
- [ ] Keychain denial fails closed without plaintext audio.

## Phase 2 — private quality gate

- [ ] Corpus contains at least 20 sessions or five hours.
- [ ] Required slices present: English, Arabic, code-switching, silence,
  playback-only, bleed, overlap, noise, long meeting, names/numbers, decisions,
  and action items.
- [ ] References were reviewed by authorized humans.
- [ ] 27B profile aggregate/slices pass release gates.
- [ ] 4B profile aggregate/slices pass its documented supported gates.
- [ ] No critical fabricated decisions; silence hallucination gate passes.
- [ ] Scrubbed aggregate report and accepted baseline ID recorded outside Git.

## Phase 3 — clean onboarding

Run once on a clean 16 GB Apple-Silicon Mac with the 4B recommendation and once
on a clean 32 GB Mac with the 27B recommendation.

- [ ] DMG drag-install; no Terminal, Homebrew, Python, or external server.
- [ ] Online registration submits only allowlisted fields.
- [ ] Offline registration visibly queues; backoff and manual retry submit later.
- [ ] Local/cloud disclosure is understood before provider selection.
- [ ] Hardware/disk recommendation is correct and low-disk error is actionable.
- [ ] Model download progress is accurate.
- [ ] Interrupted download resumes and checksums pass.
- [ ] Tampered/incomplete snapshot fails verification.
- [ ] Permission denial and retry work for microphone/system audio/accessibility.
- [ ] Synthetic sample summary succeeds with managed local runtime.
- [ ] Optional short capture test completes and cleans audio.
- [ ] Relaunch resumes the correct onboarding step and managed runtime state.

## Phase 4 — security and UX

- [ ] No unintended remote webview asset or network request.
- [ ] CSP violation test blocks unexpected script/style/connect targets.
- [ ] Auxiliary windows cannot call sensitive main-window commands.
- [ ] Diagnostics contain no email, absolute path, transcript, prompt, or key.
- [ ] Keyboard-only primary workflows complete.
- [ ] Screen-reader labels and focus order reviewed.
- [ ] 1024x720 and wide: empty, long title, dialogs, error, loading, recovery,
  cleanup-pending, and onboarding states show no clipping/overlap.

## Phase 5 — signed distribution and updater

- [ ] Developer ID signs every nested Mach-O, both launchers, and the app.
- [ ] `codesign --verify --deep --strict` passes.
- [ ] Notary submission accepted; log retained by release operator.
- [ ] Ticket stapled and validated.
- [ ] Gatekeeper opens the quarantined DMG/app normally on both clean Macs.
- [ ] Sidecars bind only as designed and terminate with app exit.
- [ ] Valid beta update installs and preserves DB/keychain/permissions/models/
  onboarding/pending recording state.
- [ ] Interrupted update resumes or fails safely.
- [ ] Invalid signature is rejected.
- [ ] Rollback/relaunch behavior is documented and safe.
- [ ] Exact accepted bytes are published to beta.
- [ ] Stable promotion reuses those bytes; no rebuild occurs.

## Sign-off

- Product/engineering:
- Privacy/security:
- Release operator:
- Acceptance date:
- Known limitations approved for beta:
