# Summarizer bench (EXP-3)

Standalone Ollama bench for the small-model summarization experiment: can a
0.6–4B model (plus prompt engineering / a map-reduce loop) match the 35B?
Born from Hamza's finding that 4B-with-prompt judged 9.6 vs the 35B's 9.5.

## Run

```bash
# any folder of exported .adversaria.json bundles (Export ▸ Meeting bundle)
# or plain .txt transcripts:
python3 bench.py --transcripts ./bundles --models qwen3:0.6b,qwen3:4b
# pipelines: single (production prompt, one shot) and/or mapreduce
# (chunk notes → merge); --ollama to point at another host.
```

Stdlib-only — copy the single file to the 8 GB Mac and run it there for
real-hardware timings.

## Judge (blind)

For each meeting, paste `results/<meeting>/JUDGE_ME.md` **plus**
`transcript.txt` into the judge LLM (ChatGPT etc.). Candidates are shuffled
and letter-labeled; score first, THEN open `labels.json` to unblind.
Rubric is embedded in the pack: coverage, faithfulness (hallucination caps
the score), action-item accuracy (owners!), structure.

## Dry-run results (2026-07-19, dev Mac, demo-meeting transcripts)

28/28 runs clean. Timings: **qwen3:0.6b = 1.5–5.6 s** per meeting (both
pipelines); **qwen3:4b = 47–106 s (mapreduce) / 119–157 s (single;
thinking-chain dominated)**. First spot-check (05-one-on-one-omar): the
0.6B map-reduce captured BOTH explicit decisions but broke the template and
dropped owners; the 4B single kept perfect structure but missed both
decisions and mis-attributed a task owner. → blind judging required;
neither wins on vibes.

Next: the definitive round on 2–3 real long exported meetings (and a run on
the 8 GB Mac itself).
