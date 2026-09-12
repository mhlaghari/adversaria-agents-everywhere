# Meetily comparison — does it solve the cross-platform hassle, and what do we take?

_Research completed 2026-08-08 (4-agent workflow over Meetily's repo, releases,
issue tracker, and the 2026 native-engine landscape). Every claim below was
verified against primary sources at research time; key links inline. Written in
answer to Hamza's question: "can you see how Meetily solves this issue?"_

**The one-line answer: Meetily solved the install/sidecar bug class by DELETING
Python from the shipped product — a ~10-week, 314-commit, multi-engineer
rewrite — and did NOT solve hassle-free operation (70% of 306 issues open).
There is no packaging trick we missed; there is a price we haven't paid yet.**

## What Meetily is

Meetily = the open-source meeting-minutes app by Zackriya Solutions
(github.com/Zackriya-Solutions/meeting-minutes; company with a closed-source
Pro tier). Same category as Adversaria: bot-free, dual-capture, on-device.

**They started with our architecture and our disease.** v0.0.1–v0.0.5
(Feb–Aug 2025): Python FastAPI backend + a whisper server users compiled
themselves. Their tracker filled with our incident classes — CMake install
failure with 21 comments still open (#110), frontend-can't-reach-backend
(#115), broken backend install (#148); "backend" appears in 95 issues.

**The rewrite (v0.1.1, 2025-10-23 → v0.2.0, 2025-12-31, "314 commits"):**
today (v0.4.0, 2026-06-05) Meetily is ONE Rust process — whisper.cpp
statically linked in-process via `whisper-rs` (Metal+CoreML on macOS, Vulkan
on the shipped Windows build, deliberately not CUDA), Parakeet via ONNX
Runtime in-process, embedded SQLite, summarization templating in Rust, LLM via
external Ollama / BYO-cloud / a small `llama-cpp-2` helper. Only sidecars: that
helper and ffmpeg, both tiny native binaries. Installers **41–66 MB** (vs our
~1.6 GB), signed (DigiCert KeyLocker on Windows since ~v0.2.1, notarized
Developer ID on macOS — earlier they shipped unsigned "Run anyway" installers
into December 2025). Models download at runtime in a 4-step onboarding.

**Feature gap in our favor:** their OSS app has no diarization, no Me/Them
dual-channel merge, no vocabulary biasing — three of our differentiators.
Linux is build-from-source; no Intel Mac build.

## The verdict, from their own tracker

**Solved — one class, by elimination:** install/packaging/EDR. Post-0.1.1 the
Python-era install complaints stop appearing; only ~5 AV-related issues in the
tracker's history (#91 the sole real hit). Mechanism: in-process static
whisper.cpp + ONNX in-process + Vulkan single-binary GPU instead of CUDA DLLs +
runtime model downloads + only tiny native sidecars. Nothing for EDR to
quarantine, no import graph to die, no installer ceiling.

**Not solved — hassle-free operation.** 306 issues, 213 open (70%), 37% of
open issues have zero comments. Post-rewrite users still hit, in native form:

- First-run model downloads failing; maintainer workaround is *manually place
  4 ONNX files* and "a VPN may also help" (#529, #662).
- A readiness-gate bug that **blocks recording entirely**, open across two
  releases, three community fix PRs unmerged (#318, #637).
- Silent process death on pre-AVX2 CPUs (#465); clean Win11 won't start for
  lack of the Vulkan runtime (#685); native crash mid-recording (#594).
- GPU silently unused — including in the **paid** build (#456, #514).
- Silent no-audio recordings (#701 + top comment on their own Reddit launch).

Their persisting failures sit exactly where we already have discipline:
readiness gating, honest recovery, signed/notarized releases from day one.

## What we take: the mechanism, not the timing

**Ratified 2026-08-08 (Hamza):** macOS launches on the current, gated stack —
that remediation is paid for. **The frozen Python sidecar never ships on
Windows again**; the Windows post-launch bar IS the native rewrite:

- `whisper-rs` in-process (Vulkan on Windows, Metal+CoreML on macOS later).
- `sherpa-rs` for diarization — the same ONNX models `diarizer.py` already
  runs, ports ~1:1. `silero_rs` for live VAD.
- Summarizer/templates/Ollama client ported to Rust (Meetily's MIT
  `src/summary/` is a working reference).
- Single-file GGML models as runtime downloads (deletes most of
  `model_setup.py`'s 507-line state machine).

**Survives:** vocabulary biasing (initial_prompt), Me/Them dual-channel merge
(engine-agnostic), diarization, live captions. **Lost:** the literal MLX
backend (→ Metal+CoreML, competitive; WhisperKit a later option) and
faster-whisper CUDA (→ Vulkan; recoverable later via a runtime engine pack —
the Jan/LM Studio pattern).

**Removes permanently:** import-time deaths, MSVC runtime dependency, the NSIS
2 GB ceiling, port/stdin/orphan lifecycle, and EDR-deletes-the-1.6GB-exe — the
friend's exact incident (`[sidecar.executable_missing]`), previously judged
"no app change fixes it." This is the app change that fixes it.

**Does NOT fix — plainly:** capture bugs (Meetily still has silent no-audio
post-rewrite; capture is Rust in both apps), state duplication, release-
pipeline discipline. The rewrite buys back the sidecar's ~35% incident share;
the rest stays ours to earn with the verification machinery.

**Cost (estimates are ours, not the reports'; calibration: Meetily took ~10
team-weeks + three releases of new-bug tail):** Windows-parity rewrite
~25–33 founder-days, heavily delegable (engine + dual-channel + model manager
5–7d · summarizer port 5–7d · sherpa-rs diarization 2–3d · live captions
3–4d · small ports 2–3d · Vulkan packaging/CI 3–4d · hardware QA bake ≥5d).
Transcribe+summarize-only cut: ~15–20d. macOS convergence later: ~5–8d.

**Risks signed up for:** (i) an in-process GGML assert aborts the whole app
(Meetily #594) — mitigated by the WAV spool as source of truth + recovery
discipline; fallback is whisper.cpp as a 5–20 MB native sidecar server if
field data shows FFI aborts; (ii) first-run download failures re-acquired
(#529-class) — simpler single-file GGML + our zero-manual-retry onboarding bar
apply; (iii) bundle the Vulkan loader or die like #685; keep a CPU fallback
for #465-class hardware; (iv) `whisper-rs` is single-maintainer and lags
upstream (0.16.0 vs whisper.cpp 1.9.2; Meetily ships happily on 0.13.2).

**De-risk first:** a ~2-day delegable spike — bare Rust harness transcribing
our committed fixture dual-channel via whisper-rs on both a Vulkan Windows box
and this Mac — before committing the 25+ days.

_Flagged as unverified: Meetily Pro's closed-source claims; meetily.ai's
requirements page is stale pre-rewrite copy; founder-day estimates are ours._
