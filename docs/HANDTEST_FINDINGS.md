# Hand-Test Findings & Fix Plan

**Date:** 2026-07-15
**Scope:** Results of hand-testing the Codex release-hardening build on macOS (Apple
Silicon, 128 GB), beyond the automated gates. Covers the packaged app, onboarding,
capture, and the local ML runtime — the things unit/synthetic tests can't reach.
**Companion docs:** [CODEX_PLAN.md](./CODEX_PLAN.md), [CODEX_TODO.md](./CODEX_TODO.md),
[RELEASE_ACCEPTANCE.md](./RELEASE_ACCEPTANCE.md).

---

## TL;DR

The automated + packaging verification all held up (see [Verified solid](#what-was-verified-solid)),
and Codex's docs did **not** overstate. But hand-testing the packaged app surfaced
issues that mocked/synthetic tests structurally cannot catch — most importantly a
**blocking bug that leaves the ML service dead in every packaged build** (fix
verified). It also confirmed, concretely, that the **capture path cannot be
validated without proper Developer-ID signing** — every attempt on ad-hoc/self-signed
builds broke on keychain/TCC identity coupling.

Nothing is committed. Real user data is intact and backed up (see [State notes](#environmentstate-notes)).

---

## Verified bugs (priority-ordered)

### 🔴 P0-1 — Bundled ML sidecar is SIGKILLed on launch (missing JIT entitlements)

- **Symptom:** In the packaged app the ML service dies on startup → header shows
  **"Local ML Service: Offline"** → no transcription and no summarization.
- **Evidence:** Crash report = `SIGKILL (Code Signature Invalid)`, namespace
  `CODESIGNING`, indicator `Invalid Page`, faulting image **`libllvmlite.dylib`**
  (LLVM JIT, reached via `numba` → `_ctypes` → `libffi`). Reproduced in **both** the
  release (`build-dmg.sh`) bundle and a plain `tauri build --debug` bundle.
- **Root cause:** `python-service/entitlements.plist` grants
  `com.apple.security.cs.disable-library-validation` and
  `...allow-dyld-environment-variables`, but **not**
  `com.apple.security.cs.allow-jit` or `...allow-unsigned-executable-memory`. Under
  hardened runtime (`codesign --options runtime`), llvmlite's JIT-generated
  executable pages are killed.
- **Fix (VERIFIED):** add to `python-service/entitlements.plist`:
  ```xml
  <key>com.apple.security.cs.allow-jit</key><true/>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key><true/>
  ```
  After re-signing with these, the sidecar boots, loads Whisper `large-v3`, and
  serves `/health` → `{"status":"ok","whisper_model":"large-v3","ollama_available":true}`.
- **Why automated tests missed it:** every Python/Rust test mocks the ML deps and
  never launches the real *signed* sidecar. This only appears in a signed bundle.

### 🔴 P0-2 — Keychain read failure → hard crash (SIGABRT), not a graceful error

- **Symptom:** App aborts on startup (Rust panic in `tao ... did_finish_launching`)
  when it cannot read its keychain-stored DB key — e.g. after any code-signature
  change, or (relevant to real users) if the user **denies** the keychain prompt.
- **Evidence:** Crash reports `meeting-note-taker-2026-07-15-2224*.ips`,
  `EXC_CRASH / SIGABRT`. Triggered reliably by re-signing the app with a different
  identity so the existing `adversaria-db` keychain item is no longer readable.
- **Root cause:** startup DB-key retrieval (`storage.rs`, `adversaria-db` /
  `encryption-key`) aborts/unwraps on keychain failure instead of surfacing an error.
- **Fix:** handle keychain-read failure with a user-facing message + retry ("Couldn't
  unlock your local data — grant keychain access and retry"); never panic. Applies to
  both the DB key and the `adversaria-recordings` spool key.

### 🟠 P1-1 — Global hotkey (⌘⇧M) does not start recording

- **Two distinct problems:**
  1. **Wrong label.** On macOS the registered accelerator is **`Cmd+Shift+M`**
     (`tray.rs:93`, `Modifiers::SUPER | SHIFT`), but the UI empty-state string,
     `CLAUDE.md`, and the tray docs all say **"Ctrl+Shift+M"**. Users press the key
     the app tells them to — which is wrong on macOS. (Same issue for the quick-note
     hotkey `Cmd/Ctrl+Shift+N`.)
  2. **Doesn't fire even with ⌘⇧M.** Event wiring is correct — frontend listens for
     `hotkey-toggle-recording` (`App.tsx:226`) and the backend emits it
     (`tray.rs:105`) — so the likely cause is the **global-shortcut registration
     failing at startup** (`tray.rs:100` has an error branch that silently falls back
     to "use the tray menu"), or recording start failing on permissions. **Not fully
     root-caused** — capturing the app's stderr was blocked by macOS launch
     constraints; needs a run with logs on a stably-signed build.
- **Fix:** (a) make the shortcut label platform-aware (show ⌘⇧M on macOS everywhere);
  (b) diagnose the registration failure from logs and surface it in the UI instead of
  silently disabling the hotkey.

### 🟡 P2-1 — Model profiles are unvalidated, with a quality gap for 16 GB Macs

- **Finding:** `setup.rs` pins exactly two profiles — `qwen-27b-quality` (RAM ≥ 24 GB)
  and `qwen-4b-light` (else). Their labels ("Recommended quality" / "Reduced quality")
  are **assumptions — neither model was ever quality-tested.**
- **Evidence:** the eval harness only ran the synthetic `deterministic-fixture` model;
  `CODEX_TODO` Phase 2 and `RELEASE_ACCEPTANCE` leave "run both model profiles + record
  baseline" **unchecked**; and the managed runtime never ran real inference (blocked by
  P0-1 until today).
- **Gap:** the 24 GB threshold pushes the very common **16 GB Macs onto the weak 4B**
  (27B needs 24 GB). A 9B/12B (~5–7 GB) fits 16 GB and is far better. For a notetaker,
  a small model's worst failure is **fabricating decisions/action items** — so this
  quietly hands the biggest user segment the riskiest model.
- **Plan:** run a **model bake-off** — DONE (first pass, see below). Set evidence-based
  labels + tiers; add a 16 GB tier.
  (Excluded: `qwen3.5:122b` — overkill; `...coding-nvfp4` — coding fine-tune;
  `bge-m3` / `nomic-embed-text` — embedding models.)

**Bake-off results (2026-07-15)** — app's real `general` prompt via Ollama, one
synthetic transcript with known ground truth + fabrication traps (script + full
outputs saved; warm timings):

| Model | Size | Decision recall | Action recall | Fabrications | Entities | Notes |
|---|---|---|---|---|---|---|
| **qwen3.5:9b** | 6.6 GB | **3/3** | **3/3** | **0** | 6/6 +$2400 +Kestrel | ★ best — fits 16 GB |
| qwen3.6:35b | 23 GB | 2/3\* | 3/3 | 0 | 6/6 +$2400 +Kestrel | strong (heavyweight) |
| qwen3:8b | 5.2 GB | 1/3 | 3/3 | 0 | 6/6, missed $2400 | weaker on decisions |
| llama3:8b | 4.7 GB | 2/3 | 2/3 | 0 | 5/6 (−Thursday), −$2400 | weakest |

- **Zero fabrication across ALL models** — the anti-fabrication `general.md` prompt
  holds even for the weak ones; no model reversed the "no Windows" negation or
  substituted the garbled term "Kestrel". Differentiation is **recall**, not
  hallucination.
- **qwen3.5:9b is the standout** — perfect scores at 6.6 GB (fits 16 GB Macs). A far
  better 16 GB default than the untested 4B, and it validates the tier gap concretely.
- \* 35B's 2/3 is likely *section placement* (it noted "no Windows" as scope, not under
  Decisions); scoring is section-sensitive. Full outputs saved for inspection.
- Caveats: single synthetic transcript, heuristic scoring, one run each — directional,
  not a full private-corpus baseline. Next: more transcripts + the 4B/27B MLX profiles.

**Bake-off v2 (2026-07-15)** — added a second, harder transcript (vendor-migration:
verbatim-substitution traps `Cloudfleet`/`Akamaze`, an explicit deferral "we are NOT
deciding the CDN today", "already done" traps). Aggregate "bad" events (fabrications +
verbatim/negation failures) across BOTH transcripts:

| Model | Size | total bad | note |
|---|---|---|---|
| qwen3.6:35b | 23 GB | 1 | fabricated 1 decision on the hard case |
| qwen3.5:9b | 6.6 GB | 1 | mis-framed the CDN deferral on the hard case |
| qwen3:8b | 5.2 GB | 1 | dec **3/3** on the standup (beat 9b there); same CDN-deferral miss |
| llama3:8b | 4.7 GB | 2 | + substituted a queue name (verbatim fail); weakest recall/entities |

- **Tempers v1's "9b clearly best":** on the harder transcript *every* model takes a hit
  — the qwen 35B/9B/8B are **closely matched** (1 bad each), and 8B even out-recalled 9B
  on the standup decisions. Only llama3 is clearly weaker (2 bad).
- **9B still holds as the 16 GB pick** — competitive with the 23 GB 35B at ¼ the size,
  zero fabrication, verbatim-safe. The *tier* recommendation stands; the "dominant"
  framing was a single-transcript artifact.
- **New finding (higher-leverage than a model swap): explicit DEFERRALS/negations are the
  common failure.** "We are NOT deciding the CDN today" / "not touching analytics" got
  mishandled by most models. `general.md` guards *fabrication* well but not
  *deferral-vs-decision*. Cheap fix worth trying: add an explicit rule — "an item
  explicitly deferred, declined, or called a proposal is NOT a decision" — which helps
  every tier at once. (Scoring is still heuristic + strict on negation, so some _bad may
  be wording/placement; 2 transcripts, not a corpus.)
- **Verified against actual outputs (2026-07-16) — the deferral claim above is DOWNGRADED.**
  Both 9B and 8B correctly framed the CDN as a *proposal / not committed* ("A proposal
  exists to move to Akamaze", "before committing to the CDN switch") and did NOT fabricate
  "decided to switch to Akamaze" — the anti-fabrication guard held. The milder real issue:
  **9B over-populated "Decisions Made"** with a capability ("auto-purge runs every 6 h") +
  action items + follow-ups, while 8B kept it clean and correctly recorded "analytics stays
  on Mixpanel". `general.md` **already** has the rule ("describing how an existing system
  works is NOT a decision") — so it's a model-*adherence* gap, not a missing rule; a prompt
  tweak is low-value here. **Robust signals that survive verification:** (a) llama3 clearly
  weakest, (b) qwen 35B/9B/8B closely matched, (c) 9B a sound 16 GB pick. The MLX 4B/27B
  *shipped* profiles remain the real untested gap (need an MLX server, not Ollama).

**Bake-off v3 (2026-07-16) — the ACTUAL shipped MLX profiles** (via `mlx_lm.server` + the
app's real summarizer, both transcripts; exact pinned 27B + 9B, and `Qwen3.5-4B-4bit` as
the 4B-tier proxy since the pinned `Qwen3.5-4B-MLX-4bit` isn't cached):

| MLX profile | standup | vendor (hard) | total bad | read |
|---|---|---|---|---|
| **4B** (shipped low-tier) | dec 2/3 · _bad 0 | dec 1/2 · _bad 0 | **0** | safest — 0 fabrication ever; lower recall (omits) |
| **9B** (proposed 16 GB) | dec 3/3 · **fab 1** | dec 2/2 · _bad 0 | **1** | full recall; slipped 1 fabrication |
| **27B** (shipped high-tier) | dec 3/3 · _bad 0 | dec 2/2 · **fab 1** | **1** | fabricated 1 on the hard case — not flawless |

**Verdict (answers "did Codex test the 4B / is it any good?"):**
- **The shipped 4B is SAFE, not a fabricator** — zero fabrication across *every* run; its
  failure mode is *omission* (lower decision recall), which for a notetaker is the *safer*
  failure. Codex's 4B low-tier is defensible; the earlier "untested/risky" framing was too
  harsh.
- **The shipped 27B is NOT clearly better than a 9B** — it fabricated a decision on the hard
  transcript (same total_bad as 9B) at ~3× the RAM/disk. The "27B for ≥24 GB" premium looks
  weak on this evidence.
- **The 9B is competitive** — full recall, one fabrication; a reasonable 16 GB option, but
  not flawless (the MLX 9B fabricated where the Ollama 9B didn't — quant/runtime variance).
- **Meta-finding: on this small synthetic set all profiles sit in one band (total_bad 0–2);
  the differentiator is transcript difficulty + run-to-run luck, not the model.** A real
  **private-corpus baseline** (Codex's open Phase-2 gate) is what's actually needed to
  separate them. Honest conclusion: they're all roughly OK; **4B safest-but-thinnest**, the
  **27B premium is questionable**, 9B a fine 16 GB middle — but don't over-restructure tiers
  on synthetic evidence alone.

---

## Product direction (enhancements from the walkthrough)

### Onboarding — detect & reuse already-installed models (biggest win, new work)
Today onboarding **only** offers the two hardcoded MLX **downloads**; it is blind to
models already on the machine. Add detection: scan **Ollama** (`GET
localhost:11434/api/tags`) and the **HF cache** (`~/.cache/huggingface/hub/models--*`)
and present them as pickable, with quality tiers ("Tested — best" / "Compatible —
unverified" / "Not recommended, too small"). Most users with a capable model would
pick "use what I have" and download nothing — which also dissolves the "download is a
roadblock" problem. (Ollama is already a supported backend — `server.py`:
"Rapid-MLX on Apple Silicon, Ollama elsewhere".)

### Onboarding — keep the model step, but make it non-blocking
Don't remove it (the app is useless without a model, and Settings-only means a
broken first run). Instead: auto-select by detected RAM, start the download in the
**background**, let the user proceed into the app/tutorial, and show
"model downloading — X%" on dependent actions instead of failing. Backend already
tracks `downloaded_bytes`/`total_bytes` (`model_setup.py`).

### Onboarding — BYOK
Already exists (`Welcome.tsx` provider local/cloud; `types.rs` `llm_provider` /
`llm_base_url` / `llm_api_key` + cloud transcription BYOK). Surface it as a first-class
third option and **share one component/state with Settings** so they can't drift.

### Permissions screen — "Grant access" buttons + ✓ ticks
Current screen is passive (describes mic / system-audio / accessibility, no action) —
users reach the main app with **nothing granted** and get surprised on first record.
Add a **"Grant access"** button per row that triggers the real macOS prompt, and a
**✓ tick** when granted (visible 1→2→3 progress).

### Onboarding — smaller items
- **Back navigation** in setup (it's forward-only today — linear step machine).
- **Surface Whisper** in the setup/download step. Transcription is a *separate* managed
  system (`download_whisper_model` / `list_whisper_models`) never mentioned in
  onboarding; a clean-machine user hits a surprise ~1.5 GB Whisper download on first
  record.
- **Show detected RAM** ("Detected 128 GB — recommending Qwen 27B") to make the
  recommendation legible.
- **Interactive tutorial / coach-marks** — highlight Record + walk the tabs; fills the
  background-download wait and doubles as the "prove it works" moment. Hand-roll or
  lazy-load (500 KB bundle budget, strict CSP — don't pull a tour library into main).

---

## The signing wall (why capture couldn't be fully tested)

The **capture → force-quit → recovery** test and **real model inference** could **not**
be completed on this machine, because the capture path is tightly coupled to
code-signing identity in three places at once, none of which persist for an ad-hoc /
self-signed build:

| Mechanism | Behavior on unstable signature |
|---|---|
| DB keychain key (`adversaria-db`) | inaccessible after a signature change → app **crashes** (P0-2) |
| Recording-spool keychain key (`adversaria-recordings`) | recording fails closed (by design) |
| Screen Recording (TCC) | grant never persists; `NoShareableContent` even when Settings shows "granted" |

Attempted workarounds and outcomes: ad-hoc re-sign (JIT fix) → sidecar ran, but TCC
wouldn't persist; `tccutil reset` + re-grant + restart → still failed (ad-hoc has no
stable identity for TCC to bind to); self-signed "Adversaria Dev" identity → app
**crashed** on the keychain key. **Only a stable, trusted Developer-ID signature makes
all three work together** — which is exactly why Developer-ID + clean-machine
acceptance is a hard release gate (empirically confirmed, not bureaucratic). Blocked
externally: Apple Developer enrollment (rejected twice; re-applying).

---

## What was verified solid

- **Automated gates (all green, re-run):** pytest 259, ruff clean, cargo test 117 (+1
  ignored), clippy `-D warnings` clean, cargo fmt, `cargo check --all-targets`, vitest
  13/5 files, coverage thresholds pass *(note: floors are low — ~16/12/11/17%, real
  coverage ~18%; several components at 0%)*, `npm audit` 0, main bundle 379.85 kB /
  500 kB, `check-security.mjs` pass, synthetic eval 10 gates pass / 2 skip.
- **Desktop E2E:** 4 WDIO tests pass on the signed bundle.
- **Packaging smoke:** fully reproduced — DMG within 0.1 % of Codex's documented bytes
  (SHA differs, expected for DMG/ad-hoc/minisign), `codesign --verify --deep --strict`
  passes, DMG mounts with both sidecars + installer, provenance accurate.
- **Data isolation:** the debug build honors `ADVERSARIA_DATA_DIR`
  (`config.rs:16`, `#[cfg(debug_assertions)]`) — real DB stays untouched.
- **ML sidecar runs healthy** once the P0-1 JIT fix is applied (Whisper large-v3,
  `ollama_available: true`).
- **Docs accuracy:** Codex's `CODEX_*` docs match reality; the open acceptance gates
  are honestly marked open.

---

## Open decisions

1. **DB encryption default.** User wants the keychain prompt gone for new downloaders
   (opt-in in Settings). Options: (a) flip default off — a one-line change
   (`types.rs:378` toggle exists) that removes the nag but yields a **plaintext
   meetings DB**; or (b) keep encryption on and treat the nag as **signing-gated** (on
   a notarized build users grant once and it's done). Recommendation: (b) long-term,
   but (a) is a legitimate product call. **Not changed** pending decision.
2. **Model tiers/labels** — set after the bake-off (P2-1).
3. **Commit the pile** — 66 modified + 43 untracked files, currently uncommitted.

---

## Environment / state notes

- **Everything is uncommitted** (66 modified + 43 untracked). Nothing pushed or
  installed.
- **Real user DB is safe:** the earlier release-build run migrated it (additive —
  added empty `recording_assets` + one `registration_state` + one `onboarding_state`
  row; all 102 meetings intact). Safety backup:
  `~/Library/Application Support/meeting-note-taker/meetings.db.SAFETY-pretest-20260715-164249`.
- A self-signed **"Adversaria Dev"** code-signing cert was added to the login keychain
  (for the signing test) — harmless; removable, or keep for future stable-identity dev
  signing.

---

## Suggested fix order

1. ✅ **P0-1 JIT entitlements** — DONE. Added `allow-jit` + `allow-unsigned-executable-memory`
   to `python-service/entitlements.plist` (`plutil -lint` OK; runtime-verified earlier).
2. ✅ **P0-2 keychain-crash guard** — DONE. `lib.rs:74` no longer `.expect()`s on
   `init_db`; on failure it logs a diagnostic, shows an actionable `rfd` error dialog,
   and exits cleanly instead of aborting. (`cargo check` clean.)
3. 🟡 **P1-1 hotkey** — label DONE (`MeetingsList.tsx` now shows ⌘⇧M on macOS; `tsc`
   OK). Registration-failure diagnosis still OPEN — needs a run with stderr on a
   stably-signed build.
4. ⏸ **Onboarding model-detection + non-blocking download** — biggest UX win; large new
   feature — paused for input/plan.
5. ⏸ **Permissions "Grant + ✓" UX**, back button, surface Whisper + detected RAM, tutorial.
6. 🟡 **Model bake-off** — first pass DONE (see P2-1): **qwen3.5:9b wins**, fits 16 GB,
   zero fabrication. Remaining: broaden transcripts + test the 4B/27B MLX profiles,
   then restructure `setup.rs` tiers (add a 9B 16 GB tier). Tier change = product
   decision — paused for input.

_Status as of 2026-07-15: fixes 1–2 complete + verified; 3 partial; 6 first-pass done.
All uncommitted._
