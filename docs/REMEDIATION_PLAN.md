# Adversaria Remediation Plan — Final (synthesized)

> **Provenance:** Produced 2026-08-07 from a two-stage forensic workflow: (1) a
> six-reader root-cause investigation over TODO.md, LESSONS_LEARNED.md,
> HANDOFF.md, and code reads of the sidecar lifecycle, capture/recovery, and
> release pipeline (~110 incidents, 159 findings, eight systemic causes SC1–SC8);
> (2) a grounded plan pass (32 open defects, 18 infra assets, GTM context) with
> three independent drafts (risk-first / funnel-first / capacity-first) merged by
> an adversarial judge. Status: **RATIFIED by Hamza 2026-08-08** ("Okay, go").
>
> **AMENDMENT (ratified 2026-08-08, from the Meetily research —
> [MEETILY_COMPARISON.md](./MEETILY_COMPARISON.md)):** the Phase 4 Windows bar
> is now the NATIVE REWRITE — **the frozen Python sidecar never ships on
> Windows again.** whisper-rs (Vulkan) + sherpa-rs diarization + summarizer in
> Rust replace it; ~25–33 delegable founder-days, de-risked first by a ~2-day
> whisper-rs spike. macOS launches on the current gated stack and converges on
> the same engine in a later minor. Rationale, evidence, risks: see the
> comparison doc.
>
> **EXECUTED 2026-08-08 (audited, committed):** 0.1 publish-cannot-lie +
> post-publish verifier (live-tested against v0.3.75 — macOS bytes match
> provenance, both signatures verify; sabotage drill fails loudly) · 0.2
> frozen-sidecar smoke in build-dmg.sh (live-tested, real /transcribe on a
> committed fixture) · 0.3 death certificate end-to-end · 0.4 dev de-poison ·
> 1.2 diagnostics bundle (real facts, structural redaction) · 1.3 partial
> (offline-aware UI + reset endpoint; force-re-download UI wiring still open) ·
> 1.4 Windows CI transcribe smoke + .sig warn→error. Windows provenance now
> recorded at publish time. STILL OPEN from Phase 0: 0.5 website button, 0.6
> retag sweep, 0.7 cert order + traceback + beta-capture (founder items).
> The eight causes referenced as SC1–SC8: SC1 shipped-artifact-never-tested ·
> SC2 distributed state, no owner · SC3 silent/mislabeled failure ·
> SC4 Windows never executed · SC5 transcript-quality whack-a-mole ·
> SC6 hand-assembled release pipeline · SC7 signing-identity churn vs OS trust ·
> SC8 diagnosis outruns verification.

**Date:** 2026-08-07 · **Skeleton:** Draft A (risk-first — its prioritization rule "rank by incidents generated *during a marketing push*" is the correct lens for a launch-adjacent solo founder), with Draft B's bar semantics and elapsed-time clocks and Draft C's evidence discipline grafted on. Ground truth re-verified today against the repo: `scripts/publish-release.sh` warn-and-proceeds (lines 105, 117) and ends at one unverified `gh release create`; `scripts/build-dmg.sh` (7 stages) never executes the frozen sidecars; `src-tauri/src/commands.rs:215-227` gates only the *error report* on `debug_assertions` — the spawn itself is ungated, so the dev-poisoning trap is live; `HF_HUB_DISABLE_XET=1` is **already** baked into the prod spawn env (`commands.rs:253` — verify-only, not work); sidecar stdout/stderr already land in `logs/adversaria-service.log` (`commands.rs:276`) — the missing piece is *surfacing* it; `release-windows.yml` smoke stops at `/health` and `.sig` upload is `if-no-files-found: warn` (line 207).

## Strategy

Launch on **macOS only** — the public copy already promises "macOS today, Windows in progress," so a macOS-scoped bar is honest, halves the work, and removes SC4/SC7-Windows from the critical path (unanimous across drafts). Sequence by one rule: fix first the mechanisms whose incident rate *scales with marketing activity* — more releases (SC6 pipeline, SC3 silent failure), more fresh machines and first-runs (SC1 shipped-never-tested) — and contain, rather than solve, the mechanisms with constant background rates (SC2 state, SC5 transcript quality). Machinery precedes bug-fixing because the diagnosis shows fixes made without it pay three taxes (unprovable in shipped form, unprovable non-regression, wrong diagnoses archived as fact) — but the machinery is capped at what the three physical machines can run, not what CI aspires to. Two elapsed-time clocks start day 1 at near-zero founder cost: the Windows OV cert order and eval-corpus collection. Marketable bar in **~13–15 founder-days across ~4 calendar weeks**; directories, awesome-lists, and Product Hunt Coming Soon proceed *now* (trickle traffic, low stakes); Show HN and other flood channels wait for the bar.

## Calls made — conflicts between drafts, resolved (not averaged)

| Conflict | Resolution | Why |
|---|---|---|
| Overall skeleton and budget (A: 11–12d / B: 15d / C: 21d, 6–8wk) | **A's skeleton, ~13–15d honest budget.** C's phase-1-heavy shape rejected pre-launch | C's 6–8 weeks contradicts "marketing soon" and front-loads machinery (workspace CI, CI release, corpus wiring, SC2 consolidation) whose absence does not generate *launch-scaled* incidents |
| OV cert timing (A: Phase 4 / B, C: order week 1) | **B wins: order in Phase 0** | Ordering costs ~0.25 founder-day + $200–450; the 1–2 week CA validation is pure elapsed time. Deferring serializes the entire Windows track behind launch for zero savings. It is the only class-level fix for both SmartScreen and EDR-deletes-sidecar |
| CI release factory / `release-candidate.yml` pre-launch (B W1.4, C 1.6 yes / A no) | **A wins: deferred** | The incident class is killed by *executing the frozen artifact* and *hash-verifying published bytes*, not by where the build ran. A self-hosted runner on the same dev Mac adds ceremony, not independence. Post-launch: run it once for real or delete it |
| Where the frozen-sidecar smoke runs (A: pre-sign / C: post-staple mounted DMG) | **Neither: run it on the signed binaries, after stage 3, before notarization** | Post-sign catches both import deaths (0.3.70 MLX class) *and* hardened-runtime/entitlement deaths, while still failing before the notarization hour. The stapled DMG is exercised anyway by the Phase 1 fresh-machine matrix |
| SC2 pre-launch scope (C: config per-field patching + recording-flag owner pre-bar / A, B: defer) | **A/B win: config patching deferred; recording desync is reproduce-or-retire only** | The save-race family causes annoyance, not first-hour terminals. The stop-flag desync predates the redesign and is `LOGGED ONLY` — verifying currency before fixing is SC8 discipline; fix only if it reproduces on the current build |
| SC5 pre-launch (B: capture-layer mic-present signal / C: corpus-tuned fix / A: bounded containment) | **A wins for launch: bounded text-domain containment, labeled as containment in TODO.** C's corpus *collection* starts now as a background clock; B's capture-layer signal and AEC wait for the corpus | Shipping a "class fix" with no measuring stick is the whack-a-mole pattern itself. Corpus recording is calendar-bound founder-voice work (like the cert), so start it — but gating on it is weeks |
| Eval baseline in the bar (C's B9: yes / A, B: no) | **Rejected from the bar** | Strangers measure first-run UX before WER. Baseline lands post-launch when the corpus reaches ~15 sessions |
| Rollback rehearsal (B M8: in bar / A, C: absent) | **B wins: in the bar** | A launch-day bad release is the one unrecoverable failure; an unrehearsed rollback during an HN thread is not a plan |
| Speculation quarantine (A: tag rule forward-only / C: rule + one-time retag sweep / B: Phase 4) | **C wins: rule + sweep, day 1.** B's deferral rejected | The sweep is ~0.5 day and stops launch-week firefighting from inheriting the ~dozen archived wrong diagnoses. Deferring a free fix for SC8 is strictly wrong |
| Website download URL (B: Phase 0 / A: Phase 2) | **B wins: Phase 0** | It is funnel step 1 and is actively wrong today (site pins 0.3.70; repo is at 0.3.75). Active damage belongs in stop-the-bleeding |
| Windows CI transcribe smoke + `.sig` warn→error (B/C: pre-launch / A: Phase 4) | **Pre-launch, in Phase 1** | Agent-only work, ~0.25 founder-day of review, and it protects the Windows *beta* channel that existing users depend on today. It does not gate the macOS bar |

---

## THE MARKETABLE BAR

*Every box green before Show HN, subreddit posts, or any traffic-flood channel. macOS-scoped; Windows is excluded and labeled "in progress" everywhere. Directories / awesome-lists / PH Coming Soon do not wait for this bar.*

**The pipeline cannot lie**
- [ ] `publish-release.sh` hard-fails on any failed or missing upload (asset-list diff via `gh release view --json assets`); warn-and-proceed paths replaced by explicit `--allow-*` flags — *0.1*
- [ ] Post-publish verifier green on the launch build: live `latest-<channel>.json` version + signature vs pinned pubkey, re-downloaded asset hashes vs `provenance-<channel>.json`, **both** channel manifests resolve — *0.1*
- [ ] `build-dmg.sh` executed both signed frozen sidecars (`/health` + fixture `/transcribe`) in a hygienic env for the launch build — *0.2*
- [ ] Three sabotage drills each failed loudly, once, on purpose: killed upload, broken import, wrong-channel publish — *0.1/0.2*
- [ ] Rollback rehearsed: `scripts/rollback-channel.sh` exists, was run once, a client observed downgrading/holding; executable in <30 min under stress — *2.5*

**The shipped artifact met a stranger's machine**
- [ ] Fresh-macOS-account full journey on the 8 GB MacBook, starting from the **public website URL**: download → Gatekeeper → real TCC prompts → model download → ≥10-min real two-voice meeting → transcript and notes sane → recording deleted → relaunch; filled `docs/acceptance/<version>.md` committed — *1.1*
- [ ] Updater drill: a machine on 0.3.7x demonstrably receives and applies the launch build (this also protects the existing beta users) — *1.1*
- [ ] **5 clean external first-runs** on non-founder Macs, ≥4 with zero founder intervention; any failure requiring a code change resets the streak after the fix ships — *2.6*
- [ ] Website buttons resolve to the latest notarized build via stable `releases/latest/download/` names, never a pinned version — *0.5*

**Failures are honest**
- [ ] Sidecar death certificate wired: a pre-bind crash surfaces its actual traceback/log tail in the UI, not "Local AI Offline" — *0.3*
- [ ] Diagnostics export ships (Settings button + CLI fallback for when the app won't boot), redaction-verified: no transcripts, titles, audio, or keys — *1.2*
- [ ] Stuck model download recoverable in-UI; download button self-explains when the sidecar is down; GuidedTour navigates to Settings → AI Model on failure instead of suspending — *1.3*
- [ ] 8 GB verdict rendered and reflected in copy + first-run RAM check; BYOK/Groq rate-limit failure fails loud — *2.1*
- [ ] Copy-vs-behavior audit done ("recording deleted once transcribed" updated for honest-recovery retention; every egress enumerated); public Known Issues page live — *2.2*
- [ ] HANDOFF/TODO contain no untagged causal claims (retag sweep done) — *0.6*

---

## Phase 0 — Stop the bleeding, start the clocks (Days 1–3, ~3.5 founder-days)

**Goal:** nothing in today's normal workflow can create new damage or new false beliefs, and both elapsed-time clocks are running.

**Tomorrow morning, in order:** founder does 0.6 (sweep) and 0.7 (cert order + traceback read + site button) while agents draft 0.1–0.4; founder reviews and runs the drills as they land.

| # | Workstream | Done means (provable) | FD |
|---|---|---|---|
| 0.1 | **`publish-release.sh` cannot lie** [SC3, SC6]: check `gh release create` exit; diff uploaded assets via `gh release view --json assets`; any miss → delete draft, exit non-zero. Warn-and-proceed paths (lines 105/117) become hard-fails requiring `--allow-missing-dmg` / `--allow-macos-only`. Append an un-skippable post-publish stage (also standalone as `scripts/verify-published.sh`): curl live manifest, assert version, minisign-verify the sig vs the pinned pubkey, re-download assets and diff SHA-256 against `provenance-<channel>.json` (provenance becomes a gate, not a diary), assert **both** channel manifests resolve. Structural fix in the same PR: mark beta releases `--prerelease` and re-attach the other channel's current manifest so neither endpoint can 404 | Sabotage drills: killed-network publish, wrong-key sig, beta-after-stable publish → all exit non-zero. Real publish prints PASS lines for manifest-sig, asset-hash, both-channels | 0.75 |
| 0.2 | **Frozen sidecars execute before shipping** [SC1 — the ~35% cause]: new `build-dmg.sh` stage after stage 3 (signed, pre-notarization — catches import deaths *and* entitlement deaths before the notarization hour): launch `dist/adversaria-service/adversaria-service` and `rapid-runtime/dist/rapid-mlx` under `env -i HOME=$(mktemp -d) PATH=/usr/bin:/bin`, cwd `/`, scratch app-data dir; poll `/health` distinguishing never-bound vs bound-but-unhealthy (port the pattern from `release-windows.yml:129-155`); POST a committed 5–10s real-speech WAV to `/transcribe` (persistent smoke-cache dir, smallest model); `/summarize` against local Ollama, else assert a well-formed engine-unavailable error, not a crash. On failure: print sidecar log tail, abort before notarization | Branch with a deliberately broken import fails at the new stage with the traceback printed; clean build passes with `/health` + `/transcribe` PASS lines in the log | 1 |
| 0.3 | **Death certificate** [SC1, SC3]: first statements of the frozen entrypoint (before heavy imports; heavy imports move into `main()`) log `starting: version, pid, exe`; `sys.excepthook` writes any traceback to `service-crash.txt` in app-data. Rust: when spawn/`/health` fails or `restart_exhausted` fires, read `service-crash.txt` + last 50 lines of `logs/adversaria-service.log` (capture already exists, `commands.rs:276` — this *surfaces* it) into the UI error state verbatim. Also fix the macOS-facing copy of `sidecar.restart_exhausted` (currently says "Windows Security" on both platforms) | Kill-tests: broken import, SIGKILL-after-bind → UI error contains the real traceback/log tail on macOS dev | 0.5 |
| 0.4 | **De-poison dev** [SC1]: gate the spawn itself on `!cfg!(debug_assertions)` (the `commands.rs:219` gate covers only error reporting — the trap is live); `build-dmg.sh` deletes `target/debug/adversaria-service*` as a final stage; dev logs which Python it runs | After a release build, `npm run tauri dev` + a print-statement edit in `server.py` shows the edit live | 0.25 |
| 0.5 | **Website ground truth** [funnel step 1, actively wrong]: repoint `lagharilabs-website` download buttons at the stable-named `releases/latest/download/` assets (the name `publish-release.sh` already maintains); add a redeploy checklist line | `curl -IL` on both buttons resolves to the current release | 0.25 |
| 0.6 | **Speculation quarantine + retag sweep** [SC8]: CLAUDE.md rule — every causal claim in HANDOFF/TODO carries `VERIFIED (evidence)` or `HYPOTHESIS`; agents may not build on `HYPOTHESIS` or upgrade it without a reproducing command/log line. One-time founder sweep retags the ~dozen known wrong-diagnosis entries | Rule in CLAUDE.md; grep for tags returns >0; sweep committed | 0.5 |
| 0.7 | **Windows containment, day 1** [SC4, SC7, SC8]: (a) **order the OV Authenticode cert** from a UAE-viable CA — the validation clock is the long pole; (b) read `%APPDATA%\...\logs\adversaria-service.log` on the office box and file the transcriber traceback as `VERIFIED` — diagnosis only, no fix unless it is a one-liner; (c) site Windows button → "join the Windows beta" email capture; (d) honest note to existing Windows beta users ("beta; signed build coming"); (e) interim pre-push hook running `sync-public.sh --pr` so no commit escapes the only CI that exists [SC6] | Cert order confirmation; traceback quoted in TODO with tag; button live; note sent; hook fires | 0.5 |

## Phase 1 — Verification machinery, sized to the real hardware (Week 1–2, ~4.5 founder-days)

**Goal:** every future release meets a stranger-shaped machine before strangers do, and every field failure has a voice without telemetry.

| # | Workstream | Done means | FD |
|---|---|---|---|
| 1.1 | **Clean-machine matrix** [SC1, SC6]: (a) **fresh macOS user account** on the 8 GB MacBook (scripted create/destroy via `sysadminctl`) — the only trusted environment for real TCC prompts (the 0.3.64 permissions fix has never met one), Gatekeeper on a real download, real capture, and 8 GB perf in the same pass; per release candidate. (b) **macOS VM** (Tart/UTM snapshot) on the dev Mac for repeatable install/first-launch/**updater** automation: install DMG N−1, confirm updater serves N, apply, relaunch. VMs are *not* trusted for capture QA (Virtualization.framework mic passthrough is unreliable). (c) Hyper-V Win11 checkpoint + Windows Sandbox on the office box — used when Windows work happens, Phase 4. Each pass fills a committed `docs/acceptance/<version>.md` (the evidence trail that has never existed) | One full matrix pass recorded for the current RC; updater drill (VM on 0.3.70 → receives current) passes. The 8 GB timing measurement for 2.1 is taken during this same pass — no separate session | 2 |
| 1.2 | **User-initiated diagnostics export** [SC3, privacy condition (a)] — build on the existing `src-tauri/src/diagnostics.rs` record channel. C's spec (the strongest): Settings → "Export diagnostics" zip = service log + `service-crash.txt` + Rust log tail + config with paths/keys/vocab redacted + versions + OS/RAM facts + permission states + model inventory with hashes + **sidecar binary existence + hash** (EDR deletion becomes self-diagnosing) + last `/health` results. Plus a tiny CLI fallback script linked from the site for when the app won't boot. Nothing auto-sends; the user emails it | Bundle generated on both platforms; redaction drill confirms no transcript text, titles, or audio; from a bundle alone the founder can answer "why is this sidecar dead" | 1 |
| 1.3 | **Honest-failure sweep of the first-run path** [SC3]: model-download button disabled with an explanatory state when the sidecar is down; force re-download/reset path clearing profile + `blobs/<sha>*.incomplete` (a stranger with a stuck 3.5 GB bar churns, full stop); GuidedTour on `transcription.state === "failed"` walks to Settings → AI Model instead of suspending (`App.tsx:639`). `HF_HUB_DISABLE_XET` is already in the prod spawn env (`commands.rs:253`) — check it off, no work | Drills: kill sidecar → button explains itself; truncate a blob mid-download → in-UI recovery; force engine failure → tour navigates | 0.75 |
| 1.4 | **CI sees what ships to the beta channel** [SC1, SC4, SC6]: extend `release-windows.yml` past `/health` with the fixture-WAV `/transcribe` (CPU, tiny model); flip `.sig` upload `warn` → `error` (line 207); if enabling `quality.yml` on the private workspace is one line, do it — otherwise the 0.7 hook stands | One green dispatch shows transcribed fixture text from the frozen Windows artifact; a keyless run fails instead of producing an unpublishable candidate | 0.75 |

**Background clocks running through Phases 1–2 (≈0 founder-days/day):** cert validation (elapsed); **eval-corpus collection** [SC5] — record real consenting sessions as they naturally occur (meetings, solo dictation, YouTube-no-mic, silence, echo-prone speaker calls, English/Arabic code-switch), correct reference transcripts opportunistically; wiring and gating are Phase 4. **Marketing asset prep** (Loom, PH assets, post copy) — founder-voice work that touches no code; only the *posting* of flood channels waits.

## Phase 2 — Marketable-bar defects, through the machinery (Weeks 2–4, overlaps Phase 1, ~5.5 founder-days)

**Goal:** only what a stranger hits in hour one. Every fix names the machine that proves it.

| # | Workstream | Done means | FD |
|---|---|---|---|
| 2.1 | **The 8 GB decision — decide, don't drift**: use the timed measurement from the 1.1 pass (the num_ctx fix has never been re-tested there — SC8 in miniature). Branch (a) processing ≤ ~2× meeting length → document "works, slower"; branch (b) → honest 16 GB minimum in site copy + a first-run RAM check offering the BYOK path. Verify the BYOK/Groq 6,000 TPM limit **fails loud** (replay a long transcript against the free tier). No model-orchestration build — that is the heroic path all constraints forbid | Dated measurement in the acceptance record; copy/behavior aligned with the branch taken; Groq drill produces a user-facing message | 0.75 |
| 2.2 | **Copy-behavior audit + Known Issues page** [SC3 applied to marketing]: every public claim mapped to the behavior/file that makes it true in `docs/LAUNCH_ASSETS.md` ("recording deleted once transcribed" gains the honest-recovery clause; "Windows in progress"; every egress enumerated: updater check, BYOK). Publish a short Known Issues page — honest-limits positioning is on-brand and defuses HN comments | Claims checklist committed; page live | 0.5 |
| 2.3 | **First-meeting capture honesty** [SC2, SC5 contained]: (a) reproduce-or-retire the "Not recording"-while-spooling desync against the *current* build during a 1.1 pass — fix only if it reproduces, proven by a 20× start/stop soak; (b) make the silence watchdog unable to discard a meeting whose spool shows real audio energy, and disable auto-discard while a final transcription is in flight (C's 0.25-day mitigation) — losing a stranger's first meeting is the unforgivable terminal; (c) **bounded** mic-junk containment: strip known caption-credit patterns + tighten the mic VAD gate, explicitly labeled *containment, not class fix* in TODO | Repro attempt documented with tag; loud-fixture meeting during a concurrent final job is never flagged silent; junk patterns absent from external first-run transcripts | 1.25 |
| 2.4 | **First-ten-minutes polish** (the demo/screenshot surface HN actually sees): live-transcript stick-to-bottom autoscroll; sub-1024px layout; Spotlight/`CFBundleDisplayName`. Add WDIO specs where cheap (the harness exists) | Manual check inside a bar run; 900px window holds; Spotlight finds "Adversaria" after drag-install | 1 |
| 2.5 | **Rollback rehearsal** [SC6]: `scripts/rollback-channel.sh` re-points the channel manifest at version N−1; run it once for real and watch a client downgrade-or-hold | Script exists, executed once, steps documented; <30 min under stress | 0.5 |
| 2.6 | **External first-run streak** (the stated Show-HN gate, with B's teeth): 5 clean first-runs on non-founder Macs, ≥4 unassisted, each through the acceptance checklist; failures produce diagnostics bundles (1.2), not shrugs; a failure requiring a code change resets the streak after the fix ships — *the reset is the system working*. Recruit from waitlist/LinkedIn if friends run short | 5 filled checklists on file; a hand-held first-run does not count | 1.5 |

**Bar green → launch.** Total to bar: **~13.5 founder-days, ~4 calendar weeks**, with the streak as the schedule's tail (budget a full week for it).

## Phase 3 — Launch-window containment (during marketing, ~0.5 founder-day/week)

- **Release discipline:** every release, however urgent, goes through 0.1 + 0.2 + a 1.1 fresh-account pass. During HN week: no release without it — a hotfix that breaks first-runs on launch day is the one unrecoverable failure. Rollback (2.5) is the pressure valve that makes this discipline survivable.
- **Support loop:** field failure → request diagnostics bundle → file tagged `HYPOTHESIS`/`VERIFIED` → fix only verified causes. SC8 containment under load.
- **Scope freeze:** no new features from bar-green to launch+2 weeks. Agents work Phase 4 branches that do not ship.

## Phase 4 — Post-launch sequenced backlog (class-level fixes, in order)

1. **Windows bar** (own checklist; gates flipping the site button, not the launch): signed app + sidecar with the now-arrived cert → SmartScreen/EDR drill on a Defender-default machine; fix the 0.7-verified transcriber traceback, proven by the 1.4 CI transcribe smoke; `cmd /c start "" "<url>"` OAuth fix; updater end-to-end on the office box; mic-privacy-toggle detection (probe the WASAPI open result); 3 clean journeys (office box fresh non-admin user, Defender-default friend machine, fresh Win11 VM without Ollama). (~5–6 fd)
2. **SC2 surgical consolidation** — three bounded PRs, not a rewrite: per-field config patching first (the named prerequisite for the save-race family, `commands.rs`), then a single recording-state owner in Rust with the frontend as pure subscriber, then the Rust/Python app-data-dir contract; error contracts generated, not hand-mirrored. (~4 fd)
3. **SC5 class fix:** finish the corpus started in Phase 1 (~15–20 sessions), wire `eval.cli` into `make eval-real` (metrics committed per release, never audio), record the baseline — then the mic-junk/echo/AEC ladder, judged by numbers that must move and stay moved; Insights out of Beta via its documented ladder. (~4–5 fd spread)
4. **SC6/SC7 finish:** App Store Connect API key for notarization (kills the credential-flap family) + rotate the pasted password; decide `release-candidate.yml` — dispatch it once for real or delete it (aspiration-infra is SC6's core smell); remaining yellows (import-audio ordering, notes drain, deadline-bound prompts, template naming) batched as touched.

## Do not do yet — explicitly deferred, with reasons

- **Full state-architecture rewrite** — off the table by constraint; Phase 4 item 2 is the surgical substitute.
- **Per-field config patching / save-race family** — real, but produces annoyance, not first-hour terminals; first Phase 4 code item.
- **AEC and capture-layer echo work** — without the eval corpus, "fixed" is per-symptom and the class returns (the SC5 pattern itself). Corpus first.
- **Eval gating in the bar** — strangers measure first-run UX before WER; collection runs now, gating is Phase 4.
- **CI release factory / self-hosted runner / `release-candidate.yml`** — not load-bearing once the frozen smoke (0.2) and byte-hash verifier (0.1) exist; a runner on the same dev Mac adds no independence.
- **Windows fixes beyond diagnosis + cert order + honest labeling** — no marketing points at Windows; serial fix-discovery there burns founder-days without protecting the funnel. The cert clock runs meanwhile.
- **Model-tiering / never-two-models orchestration** — the heroic path; the 8 GB question is answered with an honest minimum spec instead.
- **CUDA delivery, live-caption model tiering, map-reduce chunking, Insights out of Beta** — quality/retention tier; post-launch ladder.
- **Monetization work** — frozen per LAUNCH_ASSETS §7.
- **Telemetry of any kind** — never. Privacy is the product; diagnostics stay user-initiated and on-device.

## Standing process rules (effective on ratification, permanent)

1. **Speculation quarantine:** every causal claim in HANDOFF/TODO carries `VERIFIED (evidence)` or `HYPOTHESIS`. No agent builds on a `HYPOTHESIS`; upgrading requires the reproducing command or log line.
2. **No fix without a proof machine:** every fix names which machine demonstrates it (build smoke, publish verifier, fresh-account matrix, soak, drill, eval) before it merges.
3. **Nothing ships unsmoked or unverified:** no artifact ships unless the frozen-execution smoke ran and the post-publish verifier is green. During launch windows, add a fresh-account pass.
4. **Sabotage every new gate once:** machinery is not trusted until it has been watched failing on a deliberate fault.
5. **Warn-and-proceed is banned:** a missing input hard-fails or requires an explicit `--allow-*` flag — absence must be a stated decision.
6. **Evidence or it didn't happen:** every release candidate gets a committed `docs/acceptance/<version>.md`; doc claims cite `file:line` or exact commands.
7. **Dev never runs frozen code; releases never poison dev:** the `debug_assertions` spawn gate and the `target/debug` cleanup stay forever.
8. **Windows changes require the traceback first:** one verified diagnosis before any Windows fix.
9. **Diagnostics are user-initiated, on-device, redaction-tested** — the only observability channel this product will ever have.
10. **Docs updated in the same change** (existing repo rule, now enforced through rules 1 and 6).
