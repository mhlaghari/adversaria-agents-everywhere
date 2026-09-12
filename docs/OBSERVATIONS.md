# Observations & Experiments — the lab notebook

_A **living doc**. Hamza's raw field observations from daily-driving and
clean-machine testing land here, plus the experiment queue they generate.
One dated entry per observation session; experiments get an EXP-number and a
verdict when run. Bugs graduate to [TODO.md](./TODO.md) (link them, don't
duplicate); this doc keeps the narrative and the data._

---

## Observation log

### 2026-07-18/19 — Clean-machine campaign (M1 MacBook, 8 GB)

The first-ever install on hardware other than the 128 GB dev machine. Three
rounds, ~15 findings — the most valuable testing day in the project. Bugs
live in TODO (§Setup-Wizard Churn Bundle + §Round 3); highlights:

- **Two launch-blockers found & fixed same-night (0.3.50):** system-ffmpeg
  dependency broke ALL transcription on fresh Macs; missing `audio-input`
  entitlement meant the mic permission prompt never appeared. Mic fix
  confirmed live by retest.
- **Setup churn is real:** blocking 3.1 GB model download, no progress/ETA,
  no sidecar-boot feedback (first-launch Gatekeeper verify takes minutes),
  registration retry-forever on endpoint-less builds, pre-pulled Ollama
  models neither used nor explained.
- **Permissions maze:** Gatekeeper approve-then-move resets quarantine;
  screen-recording grants need a full app restart (mic doesn't); stale TCC
  grants from moved copies silently decline capture.
- **8 GB performance:** live captions minutes behind; recording during a
  running final transcription starves live captions to zero AND false-fires
  the "is anybody there?" silence prompt (watchdog keys on captions, not
  audio energy — auto-discard hazard). Both meetings did transcribe —
  contention is queueing, not loss. → spawned the 8 GB research
  ([PERF_8GB.md](./PERF_8GB.md)) and EXP-2.
- **State desync:** "not recording" at stop while audio was actually
  spooling (orphan surfaced after relaunch). Wizard name field never lands
  in `user_name`.

---

### 2026-07-19 — "Dev Mac always at 100 GB, hot, fans up" (idle-resource check)

Measured on the spot: **Adversaria idle = ~0.3 GB RSS, 0% CPU** (Whisper not
resident until a job). The residents were Ollama's llama-server (~10.5 GB warm
model) and macOS **file cache** (the bulk of "100 GB used" — normal and
reclaimable, especially after a day of 7 freeze builds). Heat/fans attributed
to the day's build workload, not the app. Re-observe on a calm no-build day;
if idle heat persists, profile then. Reinforces the PERF_8GB policy from the
big-RAM side: load models for jobs, release after — on every tier (incl.
tuning Ollama keep-alive for the embedding model).

## Experiment queue

### EXP-1 — WAV vs MP3 input: does compressing before Whisper speed it up?

- **Hamza's hypothesis:** converting the recorded `.wav` to `.mp3` in Python
  before transcription might make Whisper faster; MP3s are good now.
- **Prior (Claude):** likely NO effect on transcription speed — Whisper
  never consumes the container: every input is decoded to the same 16 kHz
  mono PCM float array before inference, so model compute (the bottleneck)
  is identical; MP3 adds an encode step + lossy artifacts (slight WER risk),
  and only wins on DISK size (~10× smaller — genuinely useful for the
  kept-until-transcribed recordings and any future audio retention, and for
  faster file I/O on slow disks).
- **Method (A/B, on the 8 GB machine):** Hamza records one real video
  session and saves the `.wav`. Then: (A) transcribe the `.wav` as-is;
  (B) convert to 192 kbps `.mp3` (count conversion time!), transcribe that.
  Measure: total wall time A vs (convert + transcribe) B, plus a text diff
  of the two transcripts for quality drift. Repeat ×2 for stability.
- **Status:** QUEUED — waiting on Hamza's recording. Whatever the result,
  the disk-size win may justify MP3 (or better: 16 kHz mono WAV/FLAC) for
  stored recordings independently of speed.

### EXP-3 — Small-model summarization: 0.6B/4B vs the 35B (Hamza's epiphany)

- **Trigger:** informal ChatGPT judging scored 4B-with-prompt 9.6 vs 35B 9.5;
  0.8B-class raw scored ~6. Hypothesis: a small model + the production prompt
  + a map-reduce loop closes the gap → tiny LLM for the 8 GB tier.
- **Harness:** `experiments/summarizer-bench/` (blind shuffled judge packs).
- **Dry run (2026-07-19, demo transcripts):** 28/28 clean. 0.6B = 2–6 s/mtg;
  4B = 47–157 s (thinking chains). Spot-check split the verdict: 0.6B
  map-reduce caught both decisions but broke template + dropped owners; 4B
  single kept structure but MISSED both decisions and mis-owned a task.
- **Real-corpus round (2026-07-19, 5 real meetings 21–46K chars, run 3
  after two bench-bug wipes — num_ctx truncation, thinking-budget empties):**
  20/20 clean. Dev-Mac timings: 0.6B single **5.4 s** / 0.6B map-reduce
  **29.4 s** / 4B single **102 s** / 4B map-reduce **205 s** avg. Output
  character: 0.6B terse (0.5–1.4 KB), 4B verbose (~15 KB). Each judge pack
  carries FIVE blind candidates incl. the production 35B baseline.
- **FIRST BLIND VERDICT (Lead AI/ML interview, judged by Hamza via ChatGPT
  2026-07-19): the PRODUCTION 35B WON — A=baseline 8/10** · B=0.6B
  map-reduce 3/10 · C=0.6B single 1/10 (degenerate repetition = real
  long-context collapse) · D=4B single 3/10 (plain-text deliberation leak —
  partly a HARNESS bug: the bench's "markdown, not JSON" instruction
  contradicts the embedded production prompt's JSON demand; the app itself
  has no such conflict) · E=4B map-reduce UNSCORED (missed in the paste).
  Signals: the map-reduce loop DID help (B>C), direction right, floor too
  low at 0.6B on real 51-min content; the earlier "4B≈35B" informal result
  didn't reproduce on real long transcripts.
- **Harness hardened across 3 more bench bugs** (all caught on real data):
  markdown-native prompt (JSON conflict), num_ctx 32K (silent truncation),
  strip untagged reasoning preamble to first `###` (qwen3:4b/1.7b ignore
  Ollama `think:false`).
- **MODERN-LADDER RUN (2026-07-19, user directive "only qwen3.5+ / gemma4";
  gemma4 absent from this Ollama registry):** qwen3.5 **0.8b-mlx / 2b / 4b**
  × (single/mapreduce) × 5 real meetings + 35B baseline. 30/30 clean, no
  leaks. Dev-Mac timings: 0.8b-mlx 8.5s single / 17.4s MR · 2b 8.6/21.9s ·
  4b 19.9/49s (qwen3.5:4b is ~4× faster than the old qwen3:4b). **Notable:
  0.8b-mlx SINGLE-shot degenerated into a repeat-loop on the dense
  License-Plate demo (20 KB of one repeated line) — but its MAP-REDUCE run
  of the same meeting stayed clean (1.4 KB). Direct evidence the loop
  stabilizes the tiny model against long-context collapse.**
- **⭐ SECOND BLIND VERDICT — Dashboard/Sector-Mapping meeting (Hamza,
  2026-07-19). THE SMALL MODEL + LOOP BEAT THE 35B.** Unblinded ranking:
  **qwen3.5:4b MAP-REDUCE 8/10 (WINNER)** · 4b single 6 · 2b MR 6 · **35B
  production baseline 4** · 2b single 4 · 0.8b-mlx MR 4 · 0.8b-mlx single 2
  (degenerate, matches the loop finding). TWO load-bearing results:
  1. **Map-reduce lifted EVERY tier** (4b 8>6 · 2b 6>4 · 0.8b 4>2) — Hamza's
     loop thesis validated across the board.
  2. **The 35B LOST because it HALLUCINATED ATTENDEES** — invented
     "Dr.Hend / Jamshed / Alaa" (not in transcript) + gave them tasks; the
     4b-MR stuck to "Speaker N" and stayed faithful. This is a **live bug in
     the shipping product** (see TODO §attendee-hallucination), not a bench
     artifact — triggered by transcript junk (Norwegian caption credits
     "Teksting av Nicolai Winther", garbled mic-channel filler). Contrast
     meeting 1 (clean Lead-AI/ML interview): 35B won 8. Pattern (2 meetings,
     needs the other 3): **35B strong on clean transcripts, HALLUCINATES on
     junk-laden ones; 4b-map-reduce is more robust to junk.**
- **⚠️ TWO LLM JUDGES DISAGREED ON THE SAME PACK — resolved by fact-check
  (2026-07-19).** A second judge model re-scored the Dashboard pack and
  reached the OPPOSITE verdict: it ranked B (the 35B baseline) **9.5/10, "10
  faithfulness"**, and demoted E (4b-MR) to 6. But the decisive fact is
  checkable: B's listed attendees **"Dr.Hend / Jamshed / Alaa" get 0 hits in
  the transcript** (only "Mohammed" is real, 3 hits). So B DID fabricate
  people; judge 1 (Hamza) was right, judge 2 rationalized ("Alaa maps to
  context" — it isn't there). **Methodological takeaway: single-LLM-judge is
  unreliable here — the two swapped winner and loser.** Trust an OBJECTIVE
  faithfulness metric, not an LLM verdict: candidate proposed — a
  deterministic attendee-name checker (extract each candidate's attendee
  list → grep the transcript → count fabricated names; un-gameable, settles
  B-vs-E cleanly). Both judges independently confirmed the **"Me"/Hamza
  channel is hallucinated garbage** ("chicken breast", "God of God",
  Norwegian caption credits) — reinforces the mic-channel-junk +
  attendee-hallucination bugs (TODO §07-19; same family as talk-time /
  vocab-echo).
- **❌ RETRACTED — my "35B hallucinated 13 attendees" finding was WRONG
  (Hamza caught it 2026-07-19).** `faithfulness.py` v1 checked listed
  attendees against the TRANSCRIPT ONLY. But the app sources attendees from a
  separate **`attendees` metadata field** in the bundle — and Dr.Hend /
  Jamshed / Alaa (Dashboard) and Saeif/Sara/Mustafa/Mutaz/Abdulaziz/Fatma
  (License-Plate) are ALL in that metadata. They are **real attendees**, not
  hallucinations. The garbled transcript just never spells them, so a
  transcript-only check falsely flagged them. Checker fixed to count
  transcript ∪ attendees-metadata; **corrected result: 0 fabricated
  attendees for EVERY condition, 35B included.** The 35B was faithful all
  along.
- **⚠️ Bigger lesson — everyone was fooled the same way.** Both LLM judges,
  my checker, AND my analysis judged attendee faithfulness against the
  transcript, when attendees legitimately come from metadata. You cannot
  score "did the model invent people?" from the transcript alone in this app.
- **↔️ AND the model comparison was UNFAIR:** the app feeds the 35B the
  attendees metadata (so it named real people), but the bench passed the
  qwen3.5 models ONLY the transcript (so they used "Speaker N" — correctly,
  given what they had). The small models weren't "more faithful"; they were
  starved of the roster. **The tier question is NOT settled.** Fix: pass the
  attendees metadata into the bench prompts (matches what the app does), then
  re-run and re-judge — the real question is whether qwen3.5:4b USES a given
  roster as well as the 35B.
- **FAIR RE-RUN (roster passed to every model, single-shot done):** the real
  qualitative finding — given the same attendee roster the app gives the 35B:
  - **qwen3.5:4b** used the real names AND mapped them to speakers
    ("Dr.Hend (Speaker 3), Alaa (Speaker 2)") — arguably better than the 35B's
    flat list.
  - **qwen3.5:0.8b-mlx** contaminated the attendee list with **vocab-echo
    junk** ("Hira, Laghari, Echelon, Tatweer" = the user's glossary terms
    bleeding from the garbled transcript) — a genuine tiny-model weakness on
    junk input, not a metadata artifact. Reinforces: the mic-junk needs
    cleaning AND the 0.8b floor is too low.
  - map-reduce initially emitted NO attendees (REDUCE prompt lacked the
    section) — fixed (added `### Attendees` to REDUCE_PROMPT), map-reduce
    re-running.
  So the honest, defensible read: **qwen3.5:4b is the 8 GB tier candidate**
  because it USES a roster well and resists junk — NOT because "the 35B
  hallucinates" (it doesn't).
- **🏁 EXP-3 CONCLUDED — Hamza judged all 5 fair packs (2026-07-19).** His
  per-letter leaderboard couldn't be read directly (each meeting shuffles
  candidates independently, so letter≠model across samples); remapping his
  scores to the ACTUAL models gives the definitive table:

  | model | per-meeting | total | avg |
  |---|---|---|---|
  | **★35B production** | 7·6·8·7·7 | **35/50** | **7.0** |
  | **qwen3.5:4b single** | 8·6·6·7·8 | **35/50** | **7.0** |
  | qwen3.5:4b map-reduce | 7·4·6·7·7 | 31/50 | 6.2 |
  | qwen3.5:2b single | 5·4·5·5·7 | 26/50 | 5.2 |
  | qwen3.5:2b map-reduce | 5·3·4·3·3 | 18/50 | 3.6 |
  | qwen3.5:0.8b-mlx single | 3·4·3·2·4 | 16/50 | 3.2 |
  | qwen3.5:0.8b-mlx map-reduce | 5·3·2·3·3 | 16/50 | 3.2 |

  **TWO conclusions, one of them a reversal of my earlier claims:**
  1. **qwen3.5:4b single-shot TIED the production 35B (7.0 vs 7.0).** A
     ~3.4 GB model that fits 8 GB matches what the app ships today. **The
     8 GB tier is validated: qwen3.5:4b, single-shot.**
  2. **Map-reduce LOST to single-shot at every tier** (4b 35>31, 2b 26>18,
     0.8b tied). ❌ My earlier "the loop helps" claims came from
     contaminated/unfair runs — on the fair, complete, correctly-aggregated
     data the loop HURTS (loses cross-chunk context). **Drop map-reduce; use
     single-shot.** 0.8b-mlx is too weak (3.2) regardless; 2b single (5.2) is
     a lighter fallback.
- **Status: EXP-3 answered → PERF_8GB updated (LLM tier = qwen3.5:4b
  single-shot).** Pending: 8 GB-Mac timing run (does 4b single hit acceptable
  latency on 8 GB hardware?) · gemma4 registry (optional).

### 2026-07-19 — ⏱️ 30 MINUTES to process one meeting on the 8 GB Mac

Hamza's clean-machine finding, and the answer to EXP-3's last open question:
**a single meeting took ~30 minutes end-to-end** (record → transcribe →
summarize) on the 8 GB M1. This is a **launch blocker**, not a tuning nicety —
no user waits 30 min, and the friend/Aleph-Alpha tester will churn hard.
Almost certainly memory thrashing: the installed app's summarizer model is far
too big for 8 GB (dev machine uses qwen3.6:35b = 23 GB — cannot fit in 8 GB →
catastrophic swap-to-disk), on top of Whisper large-v3 (~3 GB) and the live
model. Directly validates the whole PERF_8GB thread AND the EXP-3 result:
shipping **qwen3.5:4b single (~3.4 GB) fits and should cut this from ~30 min to
a few minutes.** DIAGNOSTIC to confirm next session: split the 30 min into
transcription vs summarization stages (which dominated?), and check WHAT model
the packaged app actually loads on 8 GB. **→ 8 GB tiering ESCALATED to
launch-critical (TODO).**

### EXP-2 — Model tiering on 8 GB: large-v3 vs large-v3-turbo-4bit

- **Hypothesis:** 4-bit large-v3-turbo (~0.5 GB) transforms the 8 GB
  experience at an acceptable Arabic quality cost (+~3.4 WER pts, unverified
  source). See [PERF_8GB.md](./PERF_8GB.md).
- **Method:** same recording transcribed by both models on the 8 GB Mac:
  wall time, peak memory (Activity Monitor), transcript diff on an
  English+Arabic sample.
- **Status:** QUEUED — needs the tiering build first (or a manual sidecar
  run with the turbo model).

---

_Changelog: 2026-07-19 — created at Hamza's request during the clean-machine
campaign; backfilled the 07-18/19 rounds; EXP-1 (his WAV→MP3 idea) and EXP-2
queued._
