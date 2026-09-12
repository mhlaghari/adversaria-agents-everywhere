# Release-Hardening Quality Baseline

**Recorded:** 2026-07-14  
**Updated:** 2026-07-15  
**Reference:** v0.3.41 dirty development worktree

| Check | Before hardening | Current local evidence |
|---|---:|---:|
| Main frontend entry | 885.71 kB | 379.85 kB; 500 kB enforced |
| Python tests | 250 pass + warning | 259 pass; no warning |
| Ruff | 9 findings in measured run | clean |
| Rust tests | 105 pass, 1 ignored | 117 pass, 1 ignored |
| Rust format/Clippy/check | blocking warnings | clean with warnings denied |
| Frontend tests | none | 13 across 5 files; thresholds pass |
| Embedded desktop | none | 4 passing tests; two consecutive clean runs |
| npm advisories | not gated | zero production and development advisories |
| CI | none | macOS/Windows quality + macOS smoke + gated ARM64 release candidate |
| Synthetic accuracy smoke | none | all applicable gates pass |
| Packaging smoke | existing ad-hoc build | both sidecars + app + updater + DMG + provenance verified |

Phase 0 screenshots remain in `docs/baselines/phase-0/`. Phase 4 screenshots in
`docs/baselines/phase-4/` use the actual CSS viewport rather than WebDriver's
Retina physical-pixel size and assert minimum-layout overflow behavior.
The macOS harness additionally validates a sealed debug app launched through
LaunchServices and removes its staged process/listener after every run.

## Packaging smoke (not a release candidate)

- DMG: 786,824,914 bytes; SHA-256
  `e8d290b300734fb75d8f4f100a2f8d46096a7fb6151956e58fd8529b15c80500`.
- Updater archive: 657,904,926 bytes; SHA-256
  `e6b24e29c41a914fd0e14dbd4f6ae3e9a7872226f6e592f4cfbb03aaa656515f`.
- App bundle: approximately 2.0 GB uncompressed.
- Signing: ad-hoc hardened-runtime smoke only; nested and deep verification pass.
- Notarization/Gatekeeper: not run; Apple credentials are unavailable.

## Evidence still required

- Remote macOS/Windows workflow runs after publishing the changes.
- Authorized private accuracy baseline for both model profiles.
- Real 60-minute memory and forced-quit recovery acceptance.
- Clean DMG onboarding/model-resume on 16 GB and 32 GB Macs.
- Developer ID signing, notarization, stapling, Gatekeeper, and updater acceptance.

See [RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md) for the operator checklist.
