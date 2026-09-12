# Codex Execution Handoff

**Updated:** 2026-07-15  
**Worktree:** intentionally dirty; preserve all pre-existing user changes.  
**Release state:** implementation-heavy hardening pass complete; public beta is
not accepted or published.

## Outcome of this execution pass

The repository now contains the implementation for Phases 0–4 and the
non-credentialed automation portion of Phase 5:

- bounded encrypted crash-recovery capture and durable recovery/cleanup states;
- a privacy-safe, slice-aware accuracy/outcome evaluation harness;
- versioned offline-tolerant registration and restart-safe onboarding;
- immutable/resumable model setup and an app-owned frozen Rapid-MLX runtime;
- restrictive webview/network/diagnostic boundaries and targeted UI/a11y work;
- beta/stable release configs, nested signing/notarization automation,
  multi-artifact provenance, and a gated release-candidate workflow.

The incomplete items are evidence/input gates, not hidden “done” claims. See
[CODEX_TODO.md](./CODEX_TODO.md) and
[RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md).

## Latest verified results

- Frontend: production build passes; main entry 379.85 kB / 500 kB.
- Frontend tests: 5 files, 13 tests pass; coverage thresholds pass.
- Python: Ruff clean; 259 tests pass.
- Synthetic evaluation: all applicable release gates pass; private-corpus and
  baseline gates correctly skip.
- Rust: format and strict Clippy clean; 117 pass, 1 intentionally ignored;
  all-target native check passes.
- Embedded desktop: 4 tests pass in two consecutive clean runs; assertions cover
  startup, actual CSS minimum viewport, no remote assets, local font, accessible
  names, and keyboard focus. Fresh debug bundles are now whole-bundle ad-hoc
  signed, launched through a supervised staged LaunchServices path on macOS,
  and verified to leave no app process or port listener behind.
- npm audit: zero vulnerabilities across 829 dependencies. A vulnerable
  test-only transitive package was overridden to `serialize-javascript` 7.0.5.
- Frozen Rapid-MLX: version 0.10.9; exact Qwen 27B revision served an
  authenticated synthetic inference (`local runtime ready`) and shut down cleanly.
- Full packaging smoke: both sidecars frozen, every nested Mach-O and app
  ad-hoc-signed/verified, updater archive signed, DMG created, and provenance
  generated. Nothing was installed, notarized, or published.

## Packaging-smoke artifacts

Generated under ignored `src-tauri/target/` and reproducible via the build script:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `Adversaria_aarch64.dmg` | 786,824,914 | `e8d290b300734fb75d8f4f100a2f8d46096a7fb6151956e58fd8529b15c80500` |
| `Adversaria.app.tar.gz` | 657,904,926 | `e6b24e29c41a914fd0e14dbd4f6ae3e9a7872226f6e592f4cfbb03aaa656515f` |
| updater signature | 408 | `1223ad8e011ce9cbf7ac67f7c3badd6301449d2eb2220a52c0be316aa2f1de96` |

This is an ad-hoc smoke artifact with the incomplete-registration override. It
is not a beta candidate. The updater archive was repacked after final app
signing, extracted, byte-compared to the DMG source app, and deep-signature
verified. The local updater public-pair file matches the public key pinned in
`tauri.conf.json`.

## Important implementation map

- `src-tauri/src/recording_spool.rs`, `audio/`, `storage.rs`, `commands.rs`:
  encrypted capture, manifests, migration, recovery, processing, cleanup.
- `python-service/eval/`: schemas, metrics, runner, reports, CLI, synthetic CI.
- `src-tauri/src/registration.rs`, `setup.rs`, `python-service/src/model_setup.py`,
  `src/components/Welcome.tsx`: registration/onboarding/model/runtime flow.
- `python-service/rapid-runtime/`: pinned frozen Rapid-MLX project.
- `src-tauri/src/diagnostics.rs`, capabilities, CSP, `scripts/check-security.mjs`,
  `docs/PRIVACY_NETWORK_BOUNDARIES.md`: security/privacy boundary work.
- `scripts/build-dmg.sh`, `scripts/release-provenance.mjs`, `release/`,
  `.github/workflows/release-candidate.yml`: distribution automation.
- `scripts/sign-e2e-bundle.mjs`, `scripts/launch-e2e-macos.sh`,
  `src-tauri/tauri.e2e.conf.json`: isolated macOS desktop-test signing,
  LaunchServices startup, and teardown.
- `docs/baselines/phase-4/`: Retina-normalized minimum and wide visual evidence.

## Required external inputs / next actions

1. Create the shared production Formspree form and provide its exact
   `https://formspree.io/f/...` endpoint. Replace both landing placeholders and
   build with `ADVERSARIA_FORMSPREE_ENDPOINT`.
2. Populate an authorized private evaluation corpus, run both model profiles,
   review the aggregate report, and accept a baseline.
3. Run real 60-minute and forced-termination capture acceptance.
4. Publish the branch/PR and observe macOS/Windows CI; no remote mutation was
   performed in this pass.
5. Configure a clean ARM64 release runner and Apple Developer ID/notary secrets,
   dispatch the beta candidate workflow, then run the 16 GB/32 GB clean-machine
   and updater matrix.
6. Publish only the exact notarized artifact that passes that matrix.

## Known limitations deliberately left visible

- CSP still needs `style-src 'unsafe-inline'` because the established UI has
  roughly 149 inline style sites.
- Plugin capabilities are window-specific, but custom Rust commands are still
  globally registered; sensitive commands need explicit window-label guards.
- Phase 4 visual/a11y automation currently covers the primary empty-state shell,
  not every dialog/error/loading/recovery/onboarding state in the plan.
- The Tauri identifier ends in `.app` and emits a warning. Changing it may alter
  macOS identity/data/keychain behavior and requires a migration decision, so it
  was not silently changed during hardening.
- The full app is about 2.0 GB uncompressed because the transcription sidecar
  still contains large ML/Torch dependencies. This does not block correctness,
  but packaging-size optimization should be evaluated before public bandwidth.
- The embedded WDIO service emits harmless missing-driver/teardown diagnostics
  while its embedded provider and assertions pass.

No commit, push, release publication, Formspree creation, or Apple credential
mutation was performed.
