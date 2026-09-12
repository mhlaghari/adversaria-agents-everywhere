# Codex Release-Hardening Strategy

**Updated:** 2026-07-15  
**Governing plan:** [CODEX_PLAN.md](./CODEX_PLAN.md)

## Execution rule

Reliability, privacy, measurable quality, zero-terminal setup, and distribution
are release gates. Code completion is not acceptance. Claims tied to private
data, real capture hardware, Gatekeeper, signing, or clean machines stay open
until matching evidence is recorded.

## Implemented architecture decisions

- Native capture callbacks perform bounded non-blocking queue writes. Dedicated
  writers persist independently authenticated chunks continuously; only the
  15-second caption/waveform tail remains in memory.
- Recording encryption has a keychain identity separate from SQLCipher. Failure
  to obtain the recording key fails closed instead of creating plaintext audio.
- The encrypted manifest is the crash authority. Database asset rows expose
  recovery and cleanup states; a warning cannot hide committed audio.
- Processing authenticates and streams records into private temporary WAVs.
  Partial plaintext is deleted on failure and stale processing files are removed
  at startup.
- Evaluation is privacy-safe by construction: CI sees deterministic synthetic
  fixtures; real recordings and content-bearing reports stay under a private
  `ADVERSARIA_EVAL_CORPUS` path outside Git.
- Registration is required but offline tolerant. Only validated identity,
  source/version/platform, and consent fields may reach Formspree. Meeting data,
  hardware inventory, and model choices never do.
- Local setup owns the pinned Rapid-MLX process. It uses a dynamic loopback port,
  an ephemeral credential, no telemetry, no prompt/KV disk cache, and is stopped
  when the app exits or the user selects cloud mode.
- Models are allowlisted by immutable repository revision. A download is ready
  only after every LFS file is hashed; interrupted snapshots resume through the
  Hugging Face cache.
- Cloud is an explicit disclosed selection, never an automatic fallback. Local
  and cloud smoke tests use synthetic text.
- The webview loads bundled assets under a restrictive CSP. Capabilities are
  split per window, diagnostics are local/redacted/rotated, and export requires
  a deliberate user action.
- Release mode fails closed. It requires a production registration endpoint,
  Developer ID identity, updater key, and notarization profile. Nested code is
  signed before the app; the updater is repacked from that final app before its
  own signature is generated.
- macOS desktop tests use a distinct bundle identifier, seal the complete debug
  app with an ad-hoc signature, and launch a temporary staged copy through
  LaunchServices. The supervisor owns teardown so a stale embedded WebDriver
  cannot satisfy a later run.
- Beta and stable are separate channels. Stable promotion reuses the accepted
  bytes rather than rebuilding them.

## Quality policy

- Ruff, Rustfmt, and Clippy warnings are errors for project code.
- The main web entry is capped at 500 kB uncompressed; secondary/heavy views are
  lazy-loaded.
- npm advisory scans cover both production and development/test dependencies.
- Accuracy is judged by slice and meeting outcome. A global average cannot hide
  Arabic, code-switching, overlap, silence, speaker, name/number, decision, or
  action-item failures.
- A supported model profile has no release-quality claim until the same private
  corpus records its result and known limits.
- macOS is the reference acceptance platform. Windows stays compiling in CI and
  receives native parity only after the notarized macOS reference passes.

## Evidence policy

Automated tests establish invariants. Native acceptance establishes OS and
hardware behavior. “60 minutes under 128 MB,” “at most two seconds lost,” “clean
install,” “notarized,” and “Windows parity” must never be inferred from unit or
synthetic tests.

The execution ledger is [CODEX_TODO.md](./CODEX_TODO.md); the operator matrix is
[RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md); current handoff is
[CODEX_HANDOFF.md](./CODEX_HANDOFF.md).
