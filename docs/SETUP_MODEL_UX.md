# Setup & model-selection UX — design contract

_Hamza's directive (2026-07-20): "make setup look very simple; detect which
model the user already has; recommend a model; don't wire it in for me — I
should have the option in Settings to change the model." This is the UX
contract for the 8 GB-tiering work ([PERF_8GB.md](./PERF_8GB.md)) — recommend,
never force._

## What already exists (build on it, don't reinvent)

- `src-tauri/src/setup.rs:110` `setup_status()` detects RAM + disk and returns
  three `ModelProfile`s with a `recommended` flag + a top-level
  `recommended_profile` (three-tier since 2026-07-24):
  - `qwen-27b-quality` ("Qwen 3.6 27B", `qwen3.6-27b-4bit`, min 24 GB) —
    recommended ≥24 GB RAM and ≥20 GB free disk.
  - `qwen-9b-balanced` ("Qwen 3.5 9B", `qwen3.5-9b-4bit`,
    `mlx-community/Qwen3.5-9B-MLX-4bit`, ~6 GB, min 16 GB) — recommended
    16–23 GB RAM. Added 2026-07-24 per Hamza ("I don't want people to have
    only the 27B… like 9 billion or 8 billion").
  - `qwen-4b-light` ("Qwen 3.5 4B", `qwen3.5-4b-4bit`, min 8 GB) — recommended
    otherwise. **This IS the EXP-3-validated tier (ties the 35B, ~3.4 GB).**
  - NOTE 2026-07-24: Hamza asked for "Qwen 3.5 Plus" — that model (and 3.6
    Plus) is **API-only on Alibaba Cloud, no open weights**, so it cannot be an
    on-device profile; it IS usable via the existing "My cloud provider"
    onboarding path (OpenAI-compatible). Display names now carry the
    generation ("Qwen 3.6 27B", not "Qwen 27B") to avoid reading as "Qwen 3".
- Wizard (`Welcome.tsx`) has `hardware` + `model` steps; defaults
  `selectedProfile` to `recommended_profile`.
- Settings (`Settings.tsx:666`) already has an editable `ollama_model` field.
- Each profile has an `installed` flag (`snapshot_installed` checks the pinned
  Rapid-MLX repo on disk).

## Build status (2026-07-24)

**Reqs 1, 3, 4 BUILT** (uncommitted; `Welcome.tsx` one-recommendation +
"Change model" disclosure, `Settings.tsx` on-device model picker, Rust
`set_local_model_profile` / `registration::set_selected_model_profile`). tsc ·
cargo check · cargo test 132 · vitest 15 all green. **Req 2 (Ollama `/api/tags`
detection + reuse) DEFERRED** by user decision — it's the cross-runtime fork
below and needs the localhost≠cloud provider-warning fix. Detail in HANDOFF.md /
STATUS.md.

## The four requirements (gap analysis)

1. **Simple setup.** ✅ mostly there, but the model step should read as ONE
   clear recommendation, not a spec sheet. Show: the recommended model, one
   line of "why" (your Mac has N GB), its size, and a quiet "Change" affordance
   — not two equally-weighted option cards. Advanced/other profiles live behind
   "Change" or in Settings, not front-and-center.

2. **Detect what the user already has.** ⚠️ **GAP.** Today `installed` only
   checks the pinned Rapid-MLX repo — it does NOT see models the user already
   pulled via **Ollama** (Hamza had qwen3.5:0.8b/4b, etc.). New: query Ollama
   `/api/tags`, match against the profiles' model aliases, and if a suitable
   model is already present, say "You already have <model> — using it, no
   download" and SKIP the multi-GB download. This directly attacks the setup
   churn (blocking 3.1 GB download, no ETA — TODO §wizard bundle).

3. **Recommend, correctly by RAM.** ✅ logic exists; verify the 8 GB path picks
   `qwen-4b-light` and that the recommendation copy states the reason ("Your
   Mac has 8 GB — this model fits and runs fast"). NOTE the ≥24 GB threshold
   for the 27B is coarse — reconcile with PERF_8GB tiers (8/16/32) later.

4. **Recommend ≠ force; Settings owns the choice.** The wizard PRE-SELECTS the
   recommendation but the user can change it, and **Settings must expose a
   model picker** (the recommended one marked, others selectable, each with its
   size + a "needs N GB" caveat, and a re-download/switch action). Changing the
   model there must actually re-point the summarizer (mind the cached-config
   gotcha — service URL/config is read once at startup; a model switch may need
   a service reload or app restart, and the UI should say so).

## Interaction with the 30-min launch blocker

The 8 GB Mac ALREADY recommends the 4B-light profile, yet a meeting took ~30
min ([OBSERVATIONS.md](./OBSERVATIONS.md)). So the recommendation isn't the
whole story — the diagnostic (split transcribe-vs-summarize; confirm which
model 8 GB actually loaded; is Whisper large-v3 the bottleneck?) must run
BEFORE assuming a model swap alone fixes it. This UX work and the perf fix are
siblings: the UX makes the right model easy to choose and reuse; the perf work
makes that model actually fast.

## Out of scope here

Not building this now — this is the contract for when the 8 GB-tiering task is
implemented. No code changes yet; wire it per this doc, and leave the model
choice in the user's hands.

## Mockup

Visual mockup of this contract (3 panels: simple setup step · Settings model
picker · EXP-3 evidence): <https://claude.ai/code/artifact/4c0d949c-3702-46e7-ae86-7d19913382ef>
— direction, not final pixels.

Companion **capture-UX** mockups (setup permissions step · meeting-detected
notification popup · live recording view):
<https://claude.ai/code/artifact/8ec6fb05-8b80-492b-9044-7fb2038a3c65> — same
dark app language; grounded in detection.rs + the clean-machine findings
(permissions churn, flat-mic-bubble worry).

**Notch-pill + meeting-detected — DECIDED (Hamza 2026-07-20):**
<https://claude.ai/code/artifact/912ff9c9-d828-43a2-9c4a-aec144456f8d>
(updated to the chosen set + Settings). **Ship ALL of: A2 notch-drop + A4
pill-nudge (meeting-detected), B2 minimal + B3 expressive (notch pill) — with
a Settings control to choose, never forced.**

### Notch-pill build contract

- **Two config fields** drive it (defaults in config.rs, editable in Settings ›
  Notch & alerts):
  - `notch_pill_style`: `minimal` (B2 — dot + timer + live waveform, hugs the
    notch) · `expressive` (B3 — expands on hover into the companion: title,
    live caption, both channels, one-tap Stop) · `hidden`.
  - `meeting_alert_style`: `notch_drop` (A2 — island drops from the notch,
    Record/Dismiss) · `pill_nudge` (A4 — idle pill widens with "Record →") ·
    `off`.
- **Consent-first is invariant:** every alert only OFFERS; recording starts on
  confirm or ⌘⇧M. Never auto-record.
- **Build order / effort:** B2 minimal + A4 pill-nudge are the cheap tier
  (reuse tray.rs/⌘⇧M, a small always-on-top pill window). B3 expressive
  (hover-expand "island" with live captions) + A2 notch-drop are the bigger
  lift (new window + animation + live-feed wiring). Ship minimal first,
  expressive behind the setting.
- ⚠️ Big new surface — a notch-anchored always-on-top window is real work
  (window positioning under the notch, focus behavior, multi-display). Scope
  before building; not a quick delegation.

_Changelog: 2026-07-20 — created from Hamza's setup-simplicity + user-choice
directive; grounded in the existing setup.rs/Welcome/Settings infra. Mockup
artifact added same day._
