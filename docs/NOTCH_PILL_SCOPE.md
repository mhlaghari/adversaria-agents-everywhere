# Notch pill + meeting-detected alerts — build scope

_Scoping the DECIDED design (A2 notch-drop · A4 pill-nudge · B2 minimal · B3
expressive, user-selectable — [SETUP_MODEL_UX.md](./SETUP_MODEL_UX.md), mockup
artifact 912ff9c9). Written 2026-07-20 after a codebase survey. **Headline: the
floating-window surface already exists — this is mostly restyle + config + one
new capability, NOT new windowing infrastructure.** My earlier "real new
surface, scope carefully" caveat was overcautious.)_

## What already exists (proven, in production)

| Piece | Where | Reuse |
|---|---|---|
| Frameless, transparent, always-on-top windows | `commands.rs:205` (recording), `detection.rs:105` (meeting card) | Both use `WebviewWindowBuilder` · `decorations(false)` · `always_on_top(true)` · `transparent(true)` · `skip_taskbar(true)` · `focused(false)` — the exact pill recipe |
| **Top-center positioning by the notch** | `commands.rs:231` `x=(mw-W)/2.0; y=MARGIN` | The recording bubble is ALREADY anchored top-center at the notch |
| Monitor + scale math | both files, `primary_monitor()` + `scale_factor()` | reuse verbatim |
| Live audio waveform feed | `get_audio_level` (`commands.rs:273`, RMS, polled ~15 Hz) | B2/B3 waveform already has its data source |
| Drag + click-to-focus-main | `bubble_start_drag`, `focus_main_window` (`commands.rs:247-269`) | reuse |
| Frontend widget routing | `main.tsx` `?widget=recording` / `?card=meeting` | add pill states here |
| Components to restyle | `RecordingBubble.tsx`, `MeetingCard.tsx`, `RecordingCompanion.tsx` | the actual UI work |
| String-config pattern | `recording_view` (`types.rs:452`, `default_recording_view`) | copy for the two new fields |
| `macos-private-api` (transparent windows) | `Cargo.toml` | already enabled |

**So B2-minimal is ~90% built** (the recording bubble IS a top-center pill with
a live waveform); the real work is restyling and the two genuinely-new bits:
B3's hover-expand + live captions, and A2's reposition of the meeting card to
the notch.

## Per-variant delta

- **B2 minimal pill** — restyle `RecordingBubble.tsx` to the mock (dot · timer ·
  waveform, hug the notch); tighten position. **~S.**
- **A4 pill-nudge** — when a meeting is detected but not recording, show the
  recording-window pill in a "Meet started · Record →" state (new frontend
  state + a Rust show call reusing `show_recording_bubble`'s plumbing).
  **~S.**
- **A2 notch-drop** — move `MeetingCard` from bottom-right (`detection.rs:142`)
  to top-center-under-notch + restyle to the island (title, Record/Dismiss).
  Reposition is a 2-line change; restyle is frontend. **~M.**
- **B3 expressive** — hover-expand the pill into the island (title + LIVE
  CAPTIONS + both channels + Stop). NEW: (a) resize the window on hover
  (mouse-enter/leave → Rust resize), (b) feed live captions into the pill
  (the live-caption stream exists for the in-app companion — route it to the
  pill window too). **~M/L** — the only part that's real new work.
- **Config + Settings** — two string fields `notch_pill_style`
  (minimal/expressive/hidden) + `meeting_alert_style` (notch_drop/pill_nudge/
  off), defaults in `config.rs`, a "Notch & alerts" group in `Settings.tsx`
  (segmented controls per the mock). **~S.** Consent-first stays invariant
  (alerts only offer; ⌘⇧M or confirm records).

## Recommended build order

1. **Config + Settings fields** (S) — the switch, wired to no-op reads first.
2. **B2 minimal + A4 pill-nudge** (S+S) — pure reuse of the recording window;
   ships the cheap tier, testable immediately.
3. **A2 notch-drop** (M) — reposition + restyle the meeting card.
4. **B3 expressive** (M/L) — hover-expand + live-caption routing; behind the
   `expressive` setting so it can land later without blocking the rest.

Tiers 1–2 are a small delegation. Tier 4 is the one to plan carefully.

## Technical findings — RESOLVED (research 2026-07-20, cited in the research log)

The macOS specifics, verified against current (2026) Tauri 2 / objc2-app-kit
0.3.x, not memory:

1. **Notch geometry — APIs exist, and there's an EXISTING BUG to fix.**
   `objc2-app-kit` `NSScreen` exposes `safeAreaInsets` (top ≈ notch/menu-bar
   height; **0 = no notch**, the detector), `auxiliaryTopLeftArea` /
   `auxiliaryTopRightArea` (strips beside the notch; notch spans the gap),
   `frame.midX` (center), all macOS 12+. **⚠️ current code keys off
   `primary_monitor()` — WRONG: the notch is only on the BUILT-IN display,
   which isn't primary when an external monitor is set primary. Select the
   screen with `safeAreaInsets.top > 0`.** This is a real multi-display bug in
   the existing bubble already. Non-notched Macs → top-center below the menu
   bar (fallback the code already does). Tauri position is top-left origin,
   NSScreen bottom-left — mind the flip.
2. **Non-activating focus — use the `tauri-nspanel` plugin, don't hand-roll.**
   Only an **NSPanel** with `NonactivatingPanel` (1<<7) can be clicked without
   activating the app; OR-ing the mask onto a plain NSWindow **crashes**
   (needs a real class-swap). `tauri-nspanel` (branch `v2.1`, ahkohd — pin a
   **commit SHA**, it's a git dep) does the swap correctly and exposes
   `no_activate` + `becomes_key_only_if_needed` + `level` +
   `collection_behavior`. **Only A2 (click Record mid-call) and B3
   (hover-interact) need this — B2/A4 are passive status displays and work on
   the EXISTING window approach.**
3. **Over a FULLSCREEN Zoom call — needs Accessory app policy + panel.** A
   plain always-on-top window will NOT overlay a fullscreen app
   (tauri #11488, and #5566: level/collectionBehavior work in dev, fail in
   release). The reliable combo: NSPanel + `collectionBehavior =
   canJoinAllSpaces | fullScreenAuxiliary | stationary` + level ≥ 25 +
   **`ActivationPolicy::Accessory` / `LSUIElement` (menubar-only, no Dock
   icon)**, set AFTER build()+show(). **This is an app-shape decision:** does
   the pill need to show over fullscreen calls? If yes, the app (or at least
   the panel) goes menubar-only. Defer this until B3.
4. **Hover-expand — never resize the native window** (transparent windows grey-
   flash on macOS resize, incl. release — tauri #2970/#8255). Create the panel
   at the EXPANDED size, render the collapsed pill as an inner element, animate
   the inner content with CSS on JS `mouseenter/leave`, and gate
   `pointer-events` so the transparent padding doesn't eat clicks meant for the
   menu bar. Buttery, flicker-free.
5. **⚠️ Transparency after `tauri build` — OPEN bug (tauri #13415, 2.5.1).**
   `.transparent(true)` can render solid white in packaged builds. **BUT the
   app already ships transparent always-on-top windows (the recording bubble)
   in production — so FIRST verify whether that bubble actually renders
   transparent in the installed app.** If it does, we're clear; if it's been
   solid/pill-filled all along, that's the known limitation. Mitigation if it
   bites: set `ns_window.setOpaque(false)` + clear `backgroundColor` via objc2
   after panel creation. (For a pill design where the content fills the window,
   transparency only matters at the rounded corners — lower stakes than a
   spotlight overlay.)
6. **✅ SCREEN-SHARE VISIBILITY — DECIDED (Hamza 2026-07-20): acceptable, give
   a HIDE capability.** ScreenCaptureKit captures the pill (no public opt-out),
   so it's visible when the user shares — that's fine; the answer is **let the
   user hide it.** Requirements: (a) the `notch_pill_style: hidden` setting
   already covers a persistent hide; (b) add a **quick-hide affordance** — a
   fast dismiss on the pill itself (and/or ⌘⇧-hotkey / tray toggle) so the user
   can drop it out of view before/during a share and bring it back after,
   without digging into Settings; recording continues while hidden. (c)
   OPTIONAL later: auto-hide when a screen-share is detected (needs share
   detection — a nice-to-have, not required).

## 🔑 HYBRID: native Swift notch helper as a THIRD sidecar (Hamza's idea, 2026-07-20)

**"Can we integrate the rich Swift UI in Tauri?" — YES, and it's the recommended
B3 path.** It's not native-vs-Tauri; it's Tauri-main-app + native-Swift-overlay-
helper. **The app already does this exact pattern twice.** A Swift notch helper
slots into the SAME three mechanisms already in production:

| Mechanism | Existing (Python + Rapid-MLX) | Swift helper = 3rd sidecar |
|---|---|---|
| Bundle | `tauri.conf.json` `bundle.resources` → Contents/Resources | add the built `NotchHelper.app`/binary |
| Spawn + reap | `spawn_sidecar` (`commands.rs:87`) `std::process::Command` from `resource_dir()`, child stashed in AppState, killed on exit | same launcher, tied to recording state |
| Sign | `build-dmg.sh` `sign_macho_tree "$APP/Contents/Resources/..."` | sign the nested helper the same way |

**Why this WINS for B3:** the native helper owns its own NSPanel/notch window
**natively** — so it SIDESTEPS every Tauri pain point at once (transparency-
after-build #13415, NSPanel-from-webview, non-activating focus, fullscreen
overlay). None of that touches a Tauri window because there is no Tauri window
for the pill. And it reuses Hamza's existing `NotchyPrompter` SwiftUI code
rather than rebuilding the notch UI. **The work becomes plumbing, not notch
R&D:** bundle + spawn + sign (all precedented) + IPC.

### Finalized B3 plan (research 2026-07-20, cited)

- **IPC = stdin/stdout newline-delimited JSON, NOT HTTP.** Rust writes state
  lines to the helper's `child.stdin` (`{"kind":"caption","text":"…",
  "elapsed":42}`) at 15 Hz; a Rust thread reads button events from its
  `child.stdout` (`{"kind":"event","action":"stop"}`) and calls the same
  internal fns the `#[tauri::command]`s call. **The pipe's lifecycle IS the
  process lifecycle you already manage, and reverse IPC is free** — no ports,
  no sockets, no second listener. (HTTP was the wrong instinct here: it's for
  the Python request/response service; the notch feed is a one-way tiny-state
  stream a pipe models better.)
- **Helper shape:** a **bare Mach-O** (SwiftPM `swift build -c release`, no
  `.app`/Info.plist needed), bundled via `bundle.resources` next to
  `adversaria-service`, calling `NSApp.setActivationPolicy(.accessory)` at
  launch → no Dock icon, absent from Cmd-Tab, still draws its NSPanel. Resident
  (spawned once at startup, show/hide via a pipe message — no cold-launch
  flicker), reaped by the existing `shutdown_sidecar`.
- **Sign** it in `build-dmg.sh` with the SAME identity (`sign_macho_tree` +
  `sign_file`, hardened runtime, ~empty entitlements — unlike the Python
  sidecar it needs no JIT), re-signed inside `Contents/Resources` after
  `tauri build`. Same pipeline already in place.
- **Effort ≈ 3-4 focused days, mostly DELETING code from NotchyPrompter:** strip
  SCStream/WhisperKit/LLM (Tauri owns capture/transcription/summary), keep
  `NotchWindow`+`OverlayView`+`OverlayViewModel`, replace `@main` with a tiny
  `main.swift` (accessory policy + stdin reader → @MainActor view-model
  updates + stdout event writer). Then bundle (0.5d) + Rust glue
  `spawn_notch_helper` (1d) + signing (0.5d).
- **FFI/dylib route REJECTED:** `tao`/`winit` owns the `NSApplication` run loop
  and panics on a foreign `NSApplicationDelegate` (winit #4260/#4015, tao #470);
  `swift-rs` is stale (v1.0.6, 2023) and forbids structs. ~1-2 weeks fragile
  for no benefit over the helper process.

### ⚠️ POST-MORTEM (2026-07-21): Option A was built, CRASHED, and REVERTED

Option A (convert the recording webview window to a non-activating NSPanel via
`tauri-nspanel` v2.1) was implemented in 0.3.52/0.3.53 and **crashed the app
during recording** (two `SIGABRT` crash reports; a Rust panic across the ObjC
boundary in tao's run-loop observer). **Root cause:** the pill window is
`close()`d and recreated on every main-window focus toggle (`hide_recording_bubble`)
and `set_focus()`ed on drag (`bubble_start_drag`) — both are illegal on a
non-activating NSPanel (`makeKeyWindow` returns NO; closing a converted panel
tears down through incompatible state) and panic. Reverted fully in 0.3.54 (pill
is a plain always-on-top window again; expressive island kept as a plain window).

**Re-do rules for the next attempt (do NOT skip):**
1. **Reuse, never close.** Create the panel ONCE per session; show with
   `order_front`/`show`, hide with `order_out` — never `WebviewWindow::close()` +
   recreate. That means refactoring the show/hide lifecycle (currently
   close-on-hide) to keep a single hidden panel around.
2. **Never `set_focus()` the panel** (it can't become key). For drag, use the
   drag region / `start_dragging` WITHOUT the preceding `set_focus`, or drop drag.
3. **Prototype in isolation first** against `ahkohd/tauri-macos-spotlight-example`
   — confirm the full show→hide→show + drag + fullscreen-float cycle is
   crash-free in a PACKAGED build before touching `show_recording_bubble`.
4. Add a `std::panic::set_hook` that records to `diagnostics` — this crash left no
   panic message anywhere; diagnosis needed `sample`/`.ips`/`log show`.

### ✅ DECIDED (Hamza 2026-07-20): Option A now, Option B is a future update

- **Option A (NSPanel conversion) = THE BUILD NOW.** Convert the existing
  recording-bubble webview window to a non-activating NSPanel (details below).
  ~1 day, no Swift, no second process, transparency verified safe.
- **Option B (native Swift helper) = RECORDED FOR A FUTURE UPDATE.** The full
  ~3-4-day plan (Finalized B3 plan above) stays on file; ship it later if/when
  NotchyPrompter's exact native notch pixels are worth the upgrade. Not now.

### 💡 The fork (for reference) — Option A vs Option B

The research found the transparency argument is weaker than assumed and the
**only** capability the current webview pill lacks is **non-activating clicks**
(the recording bubble already ships transparent + always-on-top; #13415 may not
even bite this build — VERIFY, 5 min). So:

- **Option B (FUTURE) — NotchyPrompter's exact polished notch pixels** → Swift
  helper (Finalized B3 plan above), ~3-4 days. Recorded, not now.
- **Option A (NOW) — "a clickable pill that doesn't steal focus from Zoom"** →
  convert the EXISTING recording-bubble webview window to a non-activating
  NSPanel — `tauri-nspanel` or ~30 lines of `objc2-app-kit` in Rust (set the
  panel style mask + floating level + collectionBehavior). **~1 day, NO second
  process, NO Swift**, reuses the HTML/CSS pill you already have. Transparency
  verified safe (below). This is the build.

**Consequence for sequencing:** B2/A4 stay Tauri reuse (recording bubble works).
For the interactive/B3 tier, the decision is Option A′ (~1 day, keep webview,
just add non-activating) vs the Swift helper (~3-4 days, native pixels). Hamza
picks based on how much the polished native notch UI matters.

### ✅ TRANSPARENCY VERIFIED (2026-07-20, packaged 0.3.50)

**#13415 does NOT affect this build.** Triggered the recording bubble in the
installed `/Applications/Adversaria.app` (started a recording, blurred main,
screenshotted the notch): the pill's **rounded corners render transparent —
the dark background/desktop shows through, NO white box.** If #13415 were
biting, the window would show a solid white rectangle around the rounded pill;
it doesn't. **So Option A′ carries NO transparency risk** — converting the
existing webview bubble to a non-activating NSPanel keeps the working
transparency AND gains the one missing capability (non-activating clicks). This
makes **Option A′ (~1 day) the clear cheap path**; the Swift helper is now
purely a "do we want NotchyPrompter's exact native pixels" upgrade, not a
transparency-risk mitigation.

## ⚖️ Honest build-vs-reuse consideration (surfaced by the research)

Every serious notch app is native Swift/SwiftUI — Boring Notch, NotchNook, and
**Hamza's OWN `NotchyPrompter`** (in the vault: Swift/SwiftUI NSWindow overlay
pinned at the notch, incl. the ScreenCaptureKit-capture caveat already learned
there). Tauri *can* do this, but swims upstream on the two hard parts
(transparency-in-release, non-activating focus over fullscreen). **The call
depends on ambition:**
- **B2 minimal + A4 pill-nudge = pure status chrome** → Tauri reuse is clearly
  right (the recording bubble already IS this; ~S work, no NSPanel, no
  Accessory).
- **B3 rich interactive HUD over fullscreen calls** → this is where Tauri costs
  real time (NSPanel + Accessory + transparency-release + fullscreen). If B3
  grows ambitious, weigh reusing/porting the native NotchyPrompter overlay
  Hamza already built, embedded as a helper, vs fighting Tauri. **Flag for
  Hamza — a genuine fork in the road, not a given.**

## Bottom line + recommended sequencing

The floating surface exists and B2/A4 are trivial reuse. The cost is
concentrated in the interactive-over-fullscreen tier.

1. **Tier 1 — config + Settings (S).** Two string fields + "Notch & alerts"
   segmented controls. No native risk.
2. **Tier 2 — B2 minimal + A4 pill-nudge + quick-hide (S).** Restyle
   `RecordingBubble.tsx`; add the pill-nudge state; add a **quick-hide
   affordance** (dismiss on the pill + hotkey/tray toggle; recording keeps
   going — decided §6); **fix the built-in-screen selection bug** while here.
   EXISTING window approach — no NSPanel, no Accessory. **Ship this first +
   verify the transparency-in-release question on real hardware.**
3. **Tier 3 — A2 notch-drop (M).** Reposition + restyle `MeetingCard` to the
   notch island. If clicking Record mid-call steals focus in testing, adopt
   `tauri-nspanel` for this window.
4. **Tier 4 — B3 expressive (M/L, GATE).** NSPanel (`tauri-nspanel`, pinned
   SHA) + hover-bloom (fixed window, CSS content) + live-caption routing to the
   pill + the Accessory/fullscreen decision + the screen-share behavior.
   **Prototype against ahkohd's `tauri-macos-spotlight-example` FIRST** to
   confirm non-activating + fullscreen-float on this macOS before writing
   pill-specific code. This is the one to plan, not delegate blind.

**Do NOT bundle tier 4 with tiers 1–3.** Ship 1–2 as one small delegation now
(genuine reuse), decide A2's focus behavior from real testing, and treat B3 as
its own scoped mini-project with the native-vs-Tauri question answered up front.

## Key sources (research 2026-07-20)

- `tauri-nspanel` (ahkohd, branch v2.1) — the non-activating NSPanel path; pin a SHA.
- Reference apps: `ahkohd/tauri-macos-spotlight-example`, `ahkohd/tauri-macos-menubar-app-example` — clone & confirm behavior FIRST.
- `objc2-app-kit` 0.3.x `NSScreen` (`safeAreaInsets`, `auxiliaryTop{Left,Right}Area`); Tauri v2 Window Customization docs.
- Open Tauri bugs to budget for: #13415 (transparency after build), #11488 (fullscreen overlay), #5566 (dev vs release level), #2970/#8255 (resize flicker).
- Native prior art: Hamza's own `NotchyPrompter` (vault `wiki/projects/teleprompter.md`) + Boring Notch — every serious notch app is native.

_Changelog: 2026-07-20 — created from the codebase survey; macOS-risk section
finalized from the research agent's cited report (NSPanel via tauri-nspanel,
Accessory-for-fullscreen, transparency-release verify, screen-share visibility,
native-vs-Tauri consideration)._
