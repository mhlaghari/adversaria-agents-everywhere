# SPEC — Speaker Diarization ("split Them into Speaker 1/2/3")

**Status:** Proposed (not implemented). Spec for a human + AI to build later.
**Author:** research + spec pass, 2026-06-20.
**Scope:** Add local, on-device speaker diarization so the single "Them" audio
channel is split into distinct, renameable speakers. Privacy is non-negotiable:
everything stays on the machine, no cloud diarization API.

> Read `CLAUDE.md` principle #1 first: this stack moves fast. Every version and
> model id below was verified against current 2026 sources (cited inline), but
> **re-verify before installing** — pin exact versions in `pyproject.toml` when
> you implement.

---

## 1. Goal & non-goals

### Goal
Today `POST /transcribe` returns a transcript where every line is prefixed `Me:`
(microphone channel) or `Them:` (system-audio channel). Every remote
participant is lumped into one `Them`. This spec splits `Them` into per-speaker
labels — `Speaker 1`, `Speaker 2`, … — that are:

- **Attributed in the transcript** (line prefix becomes the speaker label).
- **Carried into the summary** so notes can say who said what.
- **User-renameable** (e.g. `Speaker 2` → `Sarah`), with the rename persisted.
- **A foundation for cross-meeting RAG attribution** (out of scope to build the
  RAG here, but the data shape must not preclude it).

### Non-goals (this spec)
- **No diarization of the mic channel.** The mic *is* "Me" by construction — see
  §3. We never need to tell two local people apart on one mic.
- **No speaker *identification* across meetings** (voiceprint matching that says
  "this is the same Sarah as last week"). Diarization only separates speakers
  *within one meeting*. Cross-meeting identity is a later, harder feature.
- **No live/streaming diarization in Phase 1.** Batch-at-stop only. (Streaming
  is a documented later phase — §8.)
- **No change to the privacy model.** Audio is still deleted right after
  processing (`cleanup_recordings`, `src-tauri/src/commands.rs:167`).

### Success criteria
1. Feature flag OFF ⇒ behavior is byte-identical to today (the working
   transcription path is never put at risk — see §9).
2. Feature flag ON, Windows/CUDA ⇒ a 3-person meeting produces a transcript with
   `Me:`, `Speaker 1:`, `Speaker 2:` lines correctly time-ordered.
3. Renaming `Speaker 1` → a name updates the stored transcript and persists
   across app restarts.
4. macOS degrades gracefully (works, or cleanly falls back to plain `Them:`).

---

## 2. Recommended approach

The decision is **diarize-then-assign on the system-audio channel only**, with
**two backends behind one Python interface** mirroring the existing
`create_transcriber()` factory pattern (`python-service/src/transcriber.py:474`).

### Why diarize-then-assign (not whisperX)
whisperX bundles ASR + word-alignment (wav2vec2) + pyannote diarization into one
pipeline and would **replace** our transcriber. We already have a working,
platform-tuned transcriber (faster-whisper on Windows, mlx-whisper on macOS,
custom-vocabulary `initial_prompt`, dual-channel merge). Adopting whisperX means
ripping that out and re-validating two platforms — high blast radius for the
working path (violates §9). Instead we keep Whisper as-is and run diarization as
a **separate step that produces speaker *turns* (start, end, speaker)**, then
overlap those turns with the Whisper segments we already collect. This is the
classic "diarize-then-assign" merge and keeps each piece independently testable.

> whisperX reference (for context only — not adopted):
> <https://github.com/m-bain/whisperX>. Note it also depends on pyannote and
> hits the same Blackwell sm_120 wall as raw pyannote (§4).

### 2a. Windows / CUDA (RTX 5090, Blackwell sm_120) — primary target

**Recommended: `pyannote.audio` 4.x with the `pyannote/speaker-diarization-community-1` pipeline.**

- **Version:** pyannote.audio **4.x** (the 4.0 line shipped alongside
  `community-1`; pin the latest 4.x at implementation time and verify on PyPI:
  <https://pypi.org/project/pyannote-audio/>).
- **Model:** `pyannote/speaker-diarization-community-1` — the current OSS model
  (launched ~Sept 2025), CC-BY-4.0, "significantly outperforming 3.1 across all
  key metrics," especially on noisy real-world audio. Benchmarks vs legacy 3.1:
  AISHELL-4 11.7% DER (was 12.2), AMI-IHM 17.0% (was 18.8), AliMeeting 20.3 (was
  24.5). Source: <https://www.pyannote.ai/blog/community-1> and the model card
  <https://huggingface.co/pyannote/speaker-diarization-community-1>.
- **Gating:** community-1 **is a gated HF model** — you must accept the user
  conditions on the model page and pass an HF token (`token=...`). See §5 for
  how this collides with this box's broken `hf_xet` and how to handle the token
  in a privacy-first app.

**Why pyannote and not NeMo Sortformer here:** NeMo's
`diar_streaming_sortformer_4spk-v2` is genuinely excellent for *streaming* and
caps cleanly at ~4 speakers (perfect for meetings), and it would be the natural
choice if/when we do live diarization (§8). But for a batch-at-stop Phase 1,
pyannote is the lower-integration-risk path: it is a single `pip` dependency, has
the widest community/Stack-Overflow coverage, takes a WAV path directly, and its
output `Annotation` maps trivially to our turn list. NeMo pulls in a much larger
framework. Keep Sortformer as the streaming-phase candidate.
(NeMo refs: <https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2>,
<https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html>.)

**⚠️ Blackwell (sm_120 / RTX 5090) caveat — verify before you build:** as of
early-2026 *stable* PyTorch wheels were compiled up to sm_90 (Hopper); on a 5090
they may throw `CUDA error: no kernel image is available for execution on the
device`. The faster-whisper path here uses CTranslate2 (not PyTorch) and is
unaffected — but **pyannote is PyTorch**. Confirm a PyTorch build with sm_120
support is installed (recent nightlies/cu128 wheels added it; re-check
<https://github.com/pytorch/pytorch/issues/159207> and the PyTorch index) before
assuming GPU diarization works. If GPU is unavailable, pyannote falls back to CPU
(slow but correct) — acceptable for batch-at-stop. **This is the single biggest
implementation risk; spike it first (§8, Phase 0).**

### 2b. macOS / Apple Silicon (M5 Max) — secondary target

Be honest: **there is no mlx-whisper-style MLX-native diarization model.** MLX
covers Whisper transcription; it does not give us diarization. Three realistic
options, in order of preference:

1. **pyannote on MPS (Metal).** pyannote/PyTorch runs on Apple's MPS backend
   (`device = torch.device("mps")`). Community reports show large speedups over
   CPU (minutes → ~20s on real meetings) though not every op is MPS-complete, so
   expect occasional CPU fallback for specific layers. **Lowest extra code —
   same Python backend as Windows, just a different device string.** Recommended
   first cut for macOS. (Ref:
   <https://github.com/pyannote/pyannote-audio/discussions/1155>.)
2. **FluidAudio (CoreML) — fastest, but native.** `FluidInference/FluidAudio` is
   a Swift SDK wrapping CoreML-converted pyannote 3.1 segmentation + WeSpeaker
   embeddings; reports ~10× (CPU) / ~20× (GPU) over stock pyannote on Apple
   hardware. It is Swift, not Python — integrating it means a sidecar/FFI, which
   doesn't fit the current Python-service shape. Note as a future macOS
   optimization, not Phase 1.
   (<https://github.com/FluidInference/FluidAudio>,
   <https://huggingface.co/FluidInference/speaker-diarization-coreml>.)
3. **`speakrs` (Rust, CoreML + CUDA, no HF token).** `avencera/speakrs`
   (Apache-2.0) is a pure-Rust diarization library using pyannote-community-1-
   style models it pulls from its *own* HF repo `avencera/speakrs-models`, so
   **no HF token and no gated-model acceptance needed** — which neatly sidesteps
   both §5 problems. Benchmarks: M4 Pro CoreML **7.1% DER @ 529× realtime**; RTX
   4090 **7.0% DER @ 59×** — matching pyannote accuracy far faster. It is a Rust
   crate (no Python/CLI bindings yet), v0.4.1 May 2026, ONNX-runtime dep still
   pre-release.
   (<https://github.com/avencera/speakrs>.)

> **Strong recommendation worth a Phase-0 spike:** because `speakrs` is Rust, is
> cross-platform (Apple Silicon **and** CUDA in one library), and **needs no HF
> token / no gated download**, it could become the *primary* backend for **both**
> OSes and let us delete the entire §5 token problem. The tradeoff: diarization
> would move from the Python service into the Rust layer (it would run in
> `src-tauri` directly on the WAV before `cleanup_recordings`, emitting a turn
> list), changing where the merge happens. Evaluate `speakrs` head-to-head with
> pyannote in Phase 0 and let the result pick the architecture. The rest of this
> spec assumes the **pyannote-in-Python** path as the conservative default; a
> sidebar (§7a) notes what changes if `speakrs` wins.

### Recommendation summary

| Platform | Phase-1 backend | Device | Model | HF token? |
|---|---|---|---|---|
| Windows | pyannote.audio 4.x | CUDA (verify sm_120) → CPU fallback | community-1 | **Yes** (§5) |
| macOS | pyannote.audio 4.x | MPS → CPU fallback | community-1 | **Yes** (§5) |
| _both, if spike wins_ | `speakrs` (Rust) | CoreML / CUDA | speakrs-models | **No** |

---

## 3. Key simplification — only diarize the "Them" channel

**This is the load-bearing simplification and must shape the whole design.**

We record two separate WAVs: a microphone WAV (the local user) and a
system-audio WAV (everyone on the call). The mic channel *is, by definition,*
the local user — that's exactly why `merge_labeled_segments()`
(`transcriber.py:27`) can label it `Me` with zero ML. Therefore:

- **Run the diarizer on the system-audio WAV only.** Never on the mic WAV.
- The diarizer's job shrinks from "separate all N people" to "separate the
  *remote* people" — fewer speakers, no need to also discover/tag "Me", and no
  risk of the diarizer splitting the local user into a phantom second speaker.
- The existing channel-based `Me` vs `Them` split stays exactly as-is; we only
  *subdivide* the `Them` side.

Concretely, the merge becomes a 3-input interleave by start-time:

```
mic segments        → "Me"            (unchanged, no diarization)
system segments     → "Speaker N"     (N from diarization of the system WAV)
```

This also means diarization failure is **non-fatal and locally contained**: if
the diarizer errors, fall back to labeling all system segments `Them` (today's
behavior) and still return a valid transcript (same best-effort discipline the
mic channel already uses, `transcriber.py:261`).

---

## 4. How diarization merges with Whisper (the assign step)

pyannote gives **speaker turns**: a list of `(start, end, speaker_id)`. Whisper
(our existing `_collect_segments`) gives **text segments**: `(start, text)` — and
we should extend it to also carry `end` (Whisper segments already have `.end`;
mlx segments have `seg["end"]`). The assign step:

1. Diarize the system WAV → `turns: list[(start, end, label)]`.
2. For each Whisper system segment, find the diarization turn with the **maximum
   temporal overlap** and adopt its label. (Simple, robust; word-level alignment
   à la whisperX is more precise but needs wav2vec2 — not worth it for v1.)
3. Map raw pyannote labels (`SPEAKER_00`, `SPEAKER_01`, …) to stable display
   labels `Speaker 1`, `Speaker 2`, … in first-appearance order.
4. Feed `[(start, "Me", text)…] + [(start, "Speaker N", text)…]` into the same
   sort-and-coalesce logic `merge_labeled_segments()` already implements
   (generalize it from two fixed labels to an arbitrary label per segment).

Edge cases to handle: segments with no overlapping turn (assign nearest turn, or
a fallback `Speaker ?`); overlapping speech (pyannote 4.x exclusive mode helps —
prefer the dominant speaker for the line).

---

## 5. Dependencies, HF gating, and the `HF_HUB_DISABLE_XET` caveat

### New dependency
Add a **new optional extra** to `python-service/pyproject.toml` (mirroring the
existing `cuda` and `mlx` extras so the working install is never disturbed):

```toml
[project.optional-dependencies]
diarization = [
    "pyannote.audio>=4.0",   # pin the exact 4.x you validated
    # pyannote pulls in torch/torchaudio; on Windows/Blackwell ensure the
    # torch wheel has sm_120 support (see §2a). On macOS torch ships MPS.
]
```

Install: `uv sync --extra diarization`. Plain `uv sync` must remain a working,
diarization-free install (§9).

### HuggingFace token / gated model
`pyannote/speaker-diarization-community-1` is **gated** (CC-BY-4.0 but you must
accept conditions on the model page) and `Pipeline.from_pretrained(..., token=…)`
requires an HF token. This is awkward for a privacy-first, offline-by-default
app. Handle it as:

- **One-time, online, user-initiated setup** — exactly like Ollama model pulls
  and the Whisper first-run download already are. Document it in the runbook.
  Downloading a *model* is fine under the privacy model; sending *audio/
  transcripts* off-device is what's forbidden, and diarization sends neither.
- Token source priority: `HF_TOKEN` env var → a value the user pastes into
  **Settings** (stored in `config.json`, surfaced to the Python service via env
  on launch). Never hard-code a token. Never log it.
- After first download the model is cached locally; subsequent runs are fully
  offline. pyannote 4.0 explicitly supports **air-gapped/offline use** once
  cached — verify and document the offline cache path.
- **If `speakrs` wins the Phase-0 spike, this entire subsection disappears** —
  its models come from a non-gated repo with no token (§2b).

### `HF_HUB_DISABLE_XET` caveat (this box specifically)
This machine's `hf_xet` is broken — HF downloads hang at 0 bytes unless launched
with `HF_HUB_DISABLE_XET=1` (already a documented gotcha for the MLX Whisper
download; see `docs/LESSONS_LEARNED.md` and the macOS runbook in
`docs/HANDOFF.md`). pyannote downloads its weights **through the same
`huggingface_hub`**, so it will hit the **same hang**. Therefore:

- The Python service must be launched with `HF_HUB_DISABLE_XET=1` for the
  diarization model download to succeed on this box (and the macOS `.dmg`
  sidecar must set it in the spawned-process env — see `docs/PACKAGING.md`).
- Treat this as a required env var wherever the service is started, not an
  afterthought. Add it next to the existing MLX-download note.

---

## 6. Python pipeline changes

All changes are additive and gated by a `DIARIZATION_ENABLED` flag (env or
config); default OFF.

### `python-service/src/transcriber.py`
- **Generalize `merge_labeled_segments()`** (line 27) to accept an arbitrary
  per-segment label rather than two hard-coded `"Them"`/`"Me"` lists. Keep a
  thin back-compat wrapper so existing tests/call-sites keep working.
- **Make `_collect_segments` carry `end`** as well as `start` (it's already
  available from both faster-whisper `seg.end` and mlx `seg["end"]`). The merge
  needs spans, not just start points.
- **Add a diarizer abstraction + factory** paralleling `create_transcriber()`:
  ```python
  class Diarizer(Protocol):
      def diarize(self, system_audio_path: str) -> list[tuple[float, float, str]]: ...

  class PyannoteDiarizer:  # device: cuda | mps | cpu, resolved like the transcriber
      ...

  def create_diarizer() -> Diarizer | None:  # None when DIARIZATION_ENABLED is off
      ...
  ```
- **Wire it into `transcribe_dual`** (line 237) and the MLX `_merge_dual`
  (line 366): after collecting system segments, if a diarizer exists, diarize
  the **system** WAV, run the overlap-assign (§4), and pass per-segment
  speaker labels into the generalized merge. Mic stays `Me`. **Wrap diarization
  in try/except → fall back to flat `Them` on any failure** (non-fatal, §3).
- Device resolution should reuse the same `auto → cuda/mps → cpu` discipline the
  transcriber already has, including a CPU fallback path.

### `python-service/src/server.py`  (`/transcribe`, line 160)
- No new endpoint needed; diarization is internal to `transcribe_dual`.
- The diarizer should be a **lifespan singleton** like `_transcriber` (line 39)
  so the (heavy) pyannote pipeline loads once, not per request.
- `/health` (line 62) should report diarization status (loaded / disabled /
  failed) so the UI can show whether speaker separation is active. Add a field
  to `HealthResponse`.

### `python-service/src/models.py`
- `TranscribeResponse` (currently `text/language/duration_seconds`) — **decide
  the response shape (see §6a)**. Minimum: a `speakers: list[str]` field listing
  the distinct speaker labels found, so the frontend can offer rename UI without
  re-parsing the transcript. Optionally a structured `segments` list (below).

### 6a. Response shape decision (important)
Two options — **pick one and write it into ARCHITECTURE.md**:

- **(A) String transcript, unchanged contract (recommended for Phase 1).** Keep
  returning the `Me:`/`Speaker N:` line-prefixed string in `text`, plus add
  `speakers: list[str]`. Smallest change; frontend rendering already shows the
  raw string (`NoteViewer.tsx:467`). Renaming = string substitution on line
  prefixes (the `relabel_me` pattern, `transcriber.py:59`, already does exactly
  this for `Me:`). **Downside:** speaker info is only in prose, weaker for RAG.
- **(B) Structured segments.** Return `segments: [{start, end, speaker, text}]`
  alongside the string. Cleaner for cross-meeting RAG attribution and for a
  richer transcript UI, but it ripples through Rust `types.rs`, `storage.rs`
  (new column / table), and the frontend renderer.

Recommend **(A) for Phase 1** (ship value fast, low risk), with the data kept in
a shape that (B) can layer on later. Note the choice and rationale in
`docs/DECISIONS.md` as an ADR.

---

## 7. Rust + frontend impact

### Rust (`src-tauri`)
- **Ordering matters:** diarization happens inside the Python `/transcribe` call,
  which already runs **before** `cleanup_recordings()` deletes the WAVs
  (`commands.rs:158`/`:167`). Good — no Rust ordering change needed, the audio
  still exists when the diarizer reads it. **Do not move cleanup earlier.**
- `src-tauri/src/types.rs` `TranscribeResponse` (line 7): add `speakers:
  Vec<String>` (option A) — `#[serde(default)]` so the field is optional and the
  old contract still deserializes.
- `src-tauri/src/http_client.rs` `transcribe()` (line 52): map the new field
  through. No new request fields needed (diarization is server-side config).
- **Speaker rename persistence:** the transcript is stored as one TEXT blob
  (`storage.rs`, `transcript` column, schema at `storage.rs:31`). Renaming a
  speaker = rewriting line prefixes in that blob and `UPDATE`-ing the row — the
  same approach as the existing `me_label` relabel. A new Tauri command
  `rename_speaker(meeting_id, from_label, to_label)` does the substitution and
  persists. (If option B is chosen later, rename updates a structured field
  instead.) Renamed speakers can also flow into the existing `attendees` list
  (`Meeting.attendees`, `types.rs`) which the summary/notes already use.

### Frontend (`src/`)
- `src/types.ts`: mirror the `speakers` field on `TranscribeResponse`.
- `src/components/NoteViewer.tsx` (transcript tab, line ~462–467): today it dumps
  `meeting.transcript` as pre-wrapped text. Enhance to **parse line prefixes**
  (`^(Me|Speaker \d+|<renamed>):`) and render each speaker with a distinct color/
  avatar chip — reuse the existing tag color palette (`Tag.color`,
  `types.rs:42`). Keep a plain-text fallback.
- **Rename UI:** a small inline control on each distinct speaker label in the
  transcript header (or the attendees area, which NoteViewer already renders at
  line ~290) that calls `rename_speaker`. Optimistic update, then persist.
- Renamed labels should be reflected in the attendees chips and carried into
  summarize/chat so notes attribute by the chosen name.
- **Settings:** add the HF-token field (§5) and a "Speaker separation" on/off
  toggle that maps to `DIARIZATION_ENABLED`. Surface `/health` diarization status
  so the user knows if it's active.

### 7a. Sidebar — what changes if `speakrs` (Rust) wins Phase 0
If the spike picks `speakrs`: diarization moves **out of Python into
`src-tauri`**. Rust diarizes the system WAV (before cleanup) into a turn list,
sends those turns to `/transcribe` *or* does the overlap-merge in Rust after
getting Whisper segments back. This deletes the §5 HF-token/gating work and the
pyannote dependency, unifies both OSes on one library, and is dramatically
faster — at the cost of doing the merge in Rust. Decide in Phase 0.

---

## 8. Performance expectations

- **When:** batch, at **stop** only (Phase 1). Diarization runs once on the
  finished system WAV, in parallel-conceptually with / right after Whisper. It
  adds latency to the "saving meeting…" step, not to live recording.
- **Cost:** pyannote on a modern CUDA GPU runs ~20–30× realtime (a 60-min
  meeting ≈ 2–3 min) and uses a few GB VRAM. **VRAM contention:** Whisper
  large-v3 + pyannote in the *same* process on a 24 GB card has caused CUDA OOM
  for others; the 5090's 32 GB has more headroom, but if OOM appears, run
  diarization **after** Whisper releases its batch, or in a separate worker.
  Source: whisperX OOM notes,
  <https://github.com/m-bain/whisperX/issues> / the WhisperX README.
- **macOS:** pyannote on MPS is far faster than CPU (community reports ~3 min →
  ~20 s on real audio) but slower than CUDA; CoreML/`speakrs` paths report
  100–500× realtime if we go native later.
- **CPU fallback** (no usable GPU): correct but slow (can approach ~1× realtime
  on long meetings). Acceptable for an optional, at-stop feature; show progress.

---

## 9. Risks & guardrails (do not break the working path)

1. **The transcription path must keep working with the feature off.** Everything
   is behind `DIARIZATION_ENABLED` (default OFF) and a new optional `diarization`
   extra. `uv sync` (no extra) installs nothing new; `cargo check` and `tsc`
   pass with the flag off; the 50 existing pytest tests stay green. Add new tests
   for the diarization path with the ML dep **mocked** (consistent with the
   repo's mocked-ML test convention).
2. **Diarization failure is non-fatal.** Any diarizer error ⇒ fall back to flat
   `Them:` labels and return a valid transcript. A meeting must never be lost
   because diarization choked.
3. **Blackwell/sm_120 PyTorch is the top risk** (§2a) — **spike Phase 0 first:**
   confirm `pyannote.audio` actually runs on the 5090 with a sm_120-capable
   torch wheel *before* committing to the pyannote path. If it's painful,
   `speakrs` (no PyTorch, CUDA-native) is the escape hatch.
4. **VRAM contention** with Whisper (§8) — measure; separate the steps if OOM.
5. **HF gating + `hf_xet`** (§5) — both must be handled or first run silently
   hangs / 401s. The `speakrs` path removes this risk entirely.
6. **Privacy:** model *download* is online and user-initiated (like Ollama/
   Whisper today); *inference* is fully local; **audio is still deleted after
   processing.** No audio/transcript ever leaves the machine. Re-state this in
   the Settings copy next to the toggle.
7. **macOS honesty:** MPS coverage is incomplete; expect partial CPU fallback.
   Don't claim CUDA-class speed on Mac.

---

## 10. Phased plan

**Phase 0 — Spike (decide the backend).** On the RTX 5090: get
`pyannote.audio` 4.x + community-1 to actually diarize one real recorded
system-audio WAV on GPU (resolve the sm_120 torch wheel, the HF token, and
`HF_HUB_DISABLE_XET=1`). In parallel, spike `speakrs` on the same WAV (no token).
Compare accuracy, speed, and integration cost. **Output: a one-paragraph ADR in
`docs/DECISIONS.md` choosing pyannote-in-Python vs speakrs-in-Rust.** Everything
below assumes pyannote won; adjust per §7a if not.

**Phase 1 — Batch diarization at stop, Windows/CUDA, feature-flagged.**
- `diarization` extra; `create_diarizer()` + `PyannoteDiarizer`; generalize
  `merge_labeled_segments`; carry segment `end`; overlap-assign; wire into
  `transcribe_dual`; non-fatal fallback. (§3, §4, §6)
- Response option A: add `speakers` to `TranscribeResponse` across Python/Rust/TS.
- Frontend: render `Speaker N` line prefixes with color; verify a 3-person
  meeting attributes correctly. Settings toggle + HF-token field + `/health`
  status.
- Tests: mocked-diarizer unit tests for the assign/merge; feature-off regression.

**Phase 2 — macOS support.** pyannote on MPS with CPU fallback; document the
honest perf. Optionally evaluate FluidAudio/`speakrs` CoreML for speed.

**Phase 3 — Renaming + persistence.** `rename_speaker` Tauri command, inline
rename UI, persist via line-prefix rewrite (or structured field if option B),
flow renamed names into attendees + summary/chat.

**Phase 4 (later) — Structured segments (option B)** if RAG needs it, and/or
**live/streaming diarization** via NVIDIA Streaming Sortformer
(`nvidia/diar_streaming_sortformer_4spk-v2`) for an in-meeting "who's talking"
indicator. Both are explicitly out of Phase 1 scope.

---

## 11. Docs to update when implementing
- `docs/ARCHITECTURE.md` — the diarizer layer + chosen response shape (§6a).
- `docs/DECISIONS.md` — the Phase-0 ADR (pyannote vs speakrs); the option-A/B ADR.
- `docs/HANDOFF.md` / `docs/PACKAGING.md` — runbook: HF token, gated-model accept,
  `HF_HUB_DISABLE_XET=1`, sm_120 torch wheel; sidecar env for the `.dmg`.
- `docs/LESSONS_LEARNED.md` — whatever Phase 0 surfaces (esp. Blackwell).
- `docs/TODO.md` — move the diarization frontier item into phased tasks.

---

## Sources (verified 2026-06-20)
- pyannote community-1 model card + gating + in-memory:
  <https://huggingface.co/pyannote/speaker-diarization-community-1>
- pyannote community-1 / 4.0 announcement (accuracy, exclusive mode):
  <https://www.pyannote.ai/blog/community-1>
- pyannote.audio releases (4.x, offline use, ffmpeg/in-memory only):
  <https://github.com/pyannote/pyannote-audio/releases> ·
  <https://pypi.org/project/pyannote-audio/>
- pyannote on MPS/Apple Silicon:
  <https://github.com/pyannote/pyannote-audio/discussions/1155>
- speakrs (Rust, CoreML+CUDA, no HF token, DER/realtime):
  <https://github.com/avencera/speakrs>
- FluidAudio (CoreML pyannote for Apple Silicon):
  <https://github.com/FluidInference/FluidAudio> ·
  <https://huggingface.co/FluidInference/speaker-diarization-coreml>
- whisperX (diarize+align reference; OOM + Blackwell notes):
  <https://github.com/m-bain/whisperX> ·
  <https://github.com/Mekopa/whisperx-blackwell>
- NVIDIA Streaming Sortformer (streaming-phase candidate):
  <https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2> ·
  <https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/asr/speaker_diarization/intro.html>
- RTX 5090 / Blackwell sm_120 PyTorch support status:
  <https://github.com/pytorch/pytorch/issues/159207>
