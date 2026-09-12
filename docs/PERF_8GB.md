# 8 GB Optimization — research note & recommendation ladder

_Distilled 2026-07-19 from a deep-research run (partially rate-limited:
4 claims adversarially CONFIRMED, the rest single-sourced with quotes —
labeled below). Trigger: the clean-machine campaign showed the current
stack (fp16 large-v3 finals + a second live model + resident LLM) thrashing
an 8 GB M1 — captions minutes behind, finals taking many minutes, live
pipeline starved during final jobs._

## Confirmed facts (2/3+ adversarial votes, cited)

1. **mlx-whisper is NOT slower than whisper.cpp on Apple Silicon** — in the
   mac-whisper-speedtest published run (M4, turbo-class), mlx-whisper beat
   whisper.cpp+CoreML (1.02 s vs 1.23 s avg). No engine migration needed.
   [github.com/anvanvan/mac-whisper-speedtest]
2. **4-bit MLX whisper-large-v3-turbo weighs 463 MB on disk** (~0.5 GB
   load-time floor) — trivially fits 8 GB.
   [huggingface.co/mlx-community/whisper-large-v3-turbo-4bit]
3. **large-v3-turbo is 809M params (vs 1550M) and MULTILINGUAL** — keeps the
   Arabic requirement. [huggingface.co/openai/whisper-large-v3-turbo]
4. **turbo = large-v3 with the decoder pruned 32→4 layers, then fine-tuned**
   (not a distillation) — encoder quality is large-v3's own.

## Key single-sourced claims (verification rate-limited; treat as likely)

- **Arabic cost of turbo: ~+3.4 WER pts** vs large-v3 (29.9%→33.3% avg over
  SADA/CommonVoice/MASC/MGB-2). **medium (39.6%) and small (52.2%) collapse
  on Arabic** — never tier below turbo for finals. [arxiv 2412.13788]
- **Streaming caption engines**: sherpa-onnx streaming Zipformer has NO
  Arabic model (En/Zh/Ko/Bn only); SimulStreaming/WhisperLiveKit (2025 SOTA
  streaming Whisper) are PyTorch/CUDA-oriented with no MLX port. → rolling-
  window Whisper stays our live approach short-term; a smaller/quantized
  live model is the lever, not a new engine.
- Rolling-window chunking degrades caption quality (context loss) — known
  tradeoff, acceptable for cosmetic live captions.

## The recommendation ladder (wire into the wizard's hardware check)

| RAM tier | Final model | Live captions | LLM | Orchestration |
|---|---|---|---|---|
| **8 GB** | **whisper-large-v3-turbo-4bit (~0.5 GB)** | **SAME resident turbo model** (one model total, rolling window, lower cadence) | **qwen3.5:4b SINGLE-shot (~3.4 GB)** — EXP-3-validated: TIED the production 35B (7.0/10) on 5 real meetings; map-reduce tested and REJECTED (loses cross-chunk context); 0.8b too weak, 2b-single is the lighter fallback | **Never two models resident**: LLM unloaded during transcription and vice versa; final jobs QUEUE while recording is live (also fixes caption starvation + false silence prompt) |
| 16 GB | large-v3-turbo 8-bit (or fp16) | shared turbo | 7–8B 4-bit | LLM may stay resident; finals still yield to live recording |
| 32 GB+ | large-v3 (current) | separate turbo | current | current behavior fine |

## Implementation notes

- The setup wizard already runs a hardware check — feed
  `sysctl hw.memsize` into a model-profile choice; the pinned-profile
  download machinery (`/setup/model_download`) already exists.
- Biggest single win on 8 GB is **orchestration, not models**: one resident
  transcription model + LLM load/unload around summarize jobs + finals
  deferred while recording. MLX exposes `mx.metal.set_cache_limit` /
  wired-limit APIs for cache discipline (single-sourced; verify at build
  time).
- The silence watchdog must key on audio energy, not caption presence
  (TODO §Round 3) — orchestration reduces but does not remove that bug.
- Re-verification: the rate-limited deep-research run can be resumed from
  cache (run id in HANDOFF) to finish adversarial votes + synthesis if
  firmer numbers are wanted before building.

_One-line pointer lives in HANDOFF; experiments tracking in
[OBSERVATIONS.md](./OBSERVATIONS.md) (EXP-2)._
