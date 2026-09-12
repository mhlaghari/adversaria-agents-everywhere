# Core Audio process taps replace ScreenCaptureKit — decision memo (2026-08-11)

_Research spike, delivered 2026-08-11. Verdict: **hypothesis CONFIRMED —
migrate.** Evidence is primary-source: the macOS 26.5 SDK headers on this
machine, our own Cargo.lock/build artifacts, and Granola's shipped binary.
Full cited memo in the session record; this doc keeps the load-bearing facts.
Status: **PHASE 0 PASSED 2026-08-13 — GO.** Phase 1 awaits founder
scheduling. Triggering incident: DRM course video blanks for the viewer
whenever Adversaria records (TODO 2026-08-11); Granola unaffected._

## Phase-0 results (2026-08-13, live on the founder's machine, macOS 26.5.2)

- **Harness:** ~120-line Rust bin over cpal 0.18.1's tap loopback (the exact
  version in our Cargo.lock; zero SCK linked). Session scratchpad
  `tap-harness/`; recreate from this doc + cpal's `loopback.rs` if needed.
- **Capture gate PASSED:** MacBook Pro Speakers, 44.1 kHz/2 ch F32. Test
  speech captured at peak 0.77 with per-second RMS tracking the audio
  timeline exactly; WAV played back audibly.
- **DRM A/B PASSED (founder-observed):** the Krish Naik course video —
  which blanks under our SCK capture and any screen recorder — **stayed
  fully visible and playing for the whole 45 s tap capture** ("the video
  was up the entire time. It worked."). A quiet mid-capture stretch was the
  founder pausing, not the player reacting.
- **DRM-audio-through-tap: RESOLVED YES** — the tap recorded the DRM site's
  soundtrack cleanly (was listed as unverified).
- **Risk-#1 probe pattern CONFIRMED as right design:** true silence arrives
  as exact 0.0f samples, so suppressed-permission and nothing-playing are
  per-buffer indistinguishable — permission checks must probe with real
  audio, as Granola does.
- **cpal 0.18 API notes for Phase 1:** `build_input_stream` takes
  `StreamConfig` BY VALUE; `SampleRate` is a bare u32; device naming is
  `description()`. Note cpal's loopback is still device-anchored — Phase 1
  should implement Granola's GLOBAL tap shape on objc2-core-audio per the
  memo, not ship cpal's shape.
- **Not yet confirmed:** whether the purple system-audio dot appeared
  (founder didn't note it; confirm during Phase 1 QA — expected present).

## The mechanism, confirmed

- **Audio-only ScreenCaptureKit does not exist.** An `SCStream` IS a
  screen-capture session you happen to read audio from. Our
  `start_system_capture()` (audio/macos.rs:265) builds a display filter and
  starts a full capture session whose video we throw away — that session is
  what DRM players key on. Apple's own forum answer for audio-only capture:
  use `AudioHardwareCreateProcessTap` instead (thread/718279).
- **Granola uses taps — proven from its binary**: links
  `CATapDescription`/`AudioHardwareCreateProcessTap`/aggregate-device calls,
  uses `initMonoGlobalTapButExcludeProcesses:` (global, device-agnostic), and
  ships `NSAudioCaptureUsageDescription`. No capture session → DRM players
  never react → the founder's A/B fully explained.

## Why this is cheap for us specifically

- **Our `minimumSystemVersion` is already 14.4** (tauri.conf.json) — the
  practical tap floor. Clean REPLACEMENT, no Granola-style dual path.
- **Zero new crates**: cpal 0.18.1 (in our lock) has a complete tap loopback
  (`host/coreaudio/macos/loopback.rs`); `objc2-core-audio` 0.3.2 (transitive
  in our lock) binds everything incl. all `CATapDescription` inits.
  `coreaudio-sys` does NOT reach the tap headers (verified: 0 hits in our
  generated bindings). `screencapturekit` leaves Cargo.toml entirely.
- **cpal's loopback is device-anchored** (`initWithProcesses:andDeviceUID:`,
  loopback.rs:96) — the AirPods-mid-call one-sided-transcript bug
  (screenpipe #4638). **Granola's global-tap shape is the right one**;
  expect to land on ~250–350 lines over objc2-core-audio.
- **Meeting detection needs zero changes** — detection.rs already uses the
  CoreAudio process-object API (`'prs#'`/`'piri'`/`'pbid'`), not SCK, and
  creates no session. SCK's only use in the whole crate is
  `start_system_capture()`. permissions.rs's CGPreflight calls create no
  session either.
- **Format/spool unchanged**: taps deliver Float32 like SCK; read
  `kAudioTapPropertyFormat` instead of hardcoding 48k/2ch; mono mixdown
  halves the spool (we downmix for Whisper anyway).

## What we gain beyond the DRM fix

Drops `kTCCServiceScreenCapture` for `kTCCServiceAudioCapture`
("System Audio Recording Only"): the scariest onboarding prompt gone,
**no Sequoia monthly re-consent nag**, one dependency deleted — and we can
tell users to REVOKE Screen Recording. For a privacy-first product that's a
story upgrade, not just a bugfix. (`muesli` #50 made the same move for the
same friction reason.)

**CORRECTED 2026-08-11 (addendum):** a **purple system-audio dot DOES appear**
in the menu bar while a tap records (the original memo said no indicator —
over-trusted one secondary source; contradicted by Apple's Control Center
semantics + maven.de). What taps avoid is the *screen-recording* indicator
and the monthly nag. DRM keys on the capture session, not the dot — Granola
shows the dot and triggers nothing. Onboarding copy should SAY the dot will
appear; for a privacy product, a visible truthful indicator is an asset.

## The three risks that must shape the implementation

1. 🔴 **The suppressed prompt hits OUR INSTALLED BASE specifically.** Holding
   Screen Recording is exactly the state where the audio-capture prompt does
   NOT fire and the tap silently returns zeros (cpal PR #894: "silently get
   denied, record complete silence"). No public preflight exists (Apple
   forum 771864: prompt fires on first record). **Mitigation = Granola's
   pattern (visible in its strings): start tap → wait for a non-silent
   buffer → stop; treat all-zero as not-granted.** Budget `tccutil reset`
   in QA.
2. 🔴 **All-zero buffers mid-session on macOS 26.5** (up to ~16 min of exact
   0.0f while audio is audible; Apple thread 825780, unanswered since May
   2026). Indistinguishable from silence; only a full tap+aggregate rebuild
   recovers. Mitigation: RMS watchdog cross-checked against
   `kAudioProcessPropertyIsRunningOutput 'piro'` + automatic rebuild.
3. 🟠 **Aggregate lifecycle**: output-device switches mid-meeting, orphaned
   aggregates after crashes (startup cleanup needed), the `isExclusive`
   inversion footgun. Same rebuild machinery covers most of it.

Also settle in the spike: self-exclusion (Granola excludes self; screenpipe
found it broke Zoom joins — we play no audio, likely moot, test both), and
whether DRM-protected AUDIO flows through a tap (unverified; low stakes —
meeting audio isn't DRM'd — but it's the founder's trigger case).

## Addendum facts (2026-08-11, second research track — all actionable)

- 🟠 **macOS 26.0 shipped capture regressions, fixed in 26.1** (Rogue Amoeba
  2025-11-04: captures failing when a secondary output device's sample rate
  differed from the default's; Apple's release notes silent). QA needs a
  26.0 box, or detect-and-warn on 26.0.
- 🟠 **Multi-channel output attenuation, open since 14.2, present in 26.5**
  (Apple forum 806799): tapping 4-ch output = −6.02 dB, 8-ch = −12 dB.
  Direct Whisper/VAD impact for users on audio interfaces. Compensate with
  `+20·log10(N_pairs)` from the ASBD channel count — cheap, easy to miss.
- 🟠 **Apple's own sample code has a bug** (FB17411663): sets the TapList
  property on the tapID instead of the aggregateDeviceID → silent tap. Do
  not copy the sample verbatim.
- `TapAutoStart` actually means "defer start until audio exists" and
  requires `IsPrivate`; community split on necessity, ships both ways.
- **14.2 is the API floor; 14.4 is the deployment floor** because 14.4
  introduced the "System Audio Recording Only" TCC granularity (OBS #10401).
  Our 14.4 minimum is right for a documented reason.
- **No OS-version branching needed**: `AudioHardwareTapping.h` byte-identical
  across 14.5/15.5/26.5 SDKs; Sequoia's tap work was a Swift-only overlay.
  One code path from 14.4 up.
- **Docs reality:** Apple has never presented taps at WWDC; the macOS 26
  additions are documented in two one-line header abstracts. Spike time goes
  to reading headers, not docs.
- **Confidence tiering (per the researcher):** the facts table, migration
  surface, and everything above = primary-source tier. Several single-report
  failure modes (AirPods 24 kHz negotiation, default-device re-bind, orphaned
  taps wedging coreaudiod) = hypotheses to test, not established. The
  all-zero-buffer bug (risk #2) stays act-on: Apple's own forums, unanswered,
  current macOS.

## Phased plan (recommended, not yet scheduled)

| Phase | Scope | Est. |
|---|---|---|
| 0 — go/no-go spike | cpal loopback → WAV; A/B the DRM site; DRM-audio check; self-exclusion test | 0.5–1 d |
| 1 — replace | global tap on objc2-core-audio; drop screencapturekit; plist + permission plumbing | 2–3 d |
| 2 — migrate & QA | buffer-probe permission UX; silence watchdog + rebuild; device-change handling; fresh-account QA | 2–3 d |

**~1–1.5 weeks founder+agents. Phase 0 is a genuine gate: if the DRM site
still blanks with a tap running, stop.** Sequencing: post-0.3.76; competes
with graph-v2 merge and the Windows native rewrite for the next slot —
founder's call.

## Unverified (stated honestly)

The ed-tech player's exact detector (doesn't change the decision) ·
DRM-audio-through-tap (Phase 0 resolves) · Rogue Amoeba ARK internals ·
the audio-TCC dialog's exact prompt copy.
