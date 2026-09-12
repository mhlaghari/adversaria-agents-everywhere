#!/usr/bin/env python3
"""Summarizer model bench — EXP-3 (small-model summarization, incl. map-reduce).

Standalone harness, OUTSIDE the app: pipes real Adversaria transcripts through
Ollama models and pipelines, writes every candidate summary plus a BLIND judge
pack per meeting. Stdlib only — no installs.

Inputs: a folder of exported `.adversaria.json` bundles (Export ▸ Meeting
bundle in the app) and/or plain `.txt` transcripts.

Pipelines:
  single    — one shot: the app's production prompt + full transcript
  mapreduce — chunk transcript → faithful notes per chunk → reduce into the
              production structure (Hamza's 0.8B loop idea)

Usage:
  python3 bench.py --transcripts ./bundles --models qwen3:4b,qwen3:0.6b
  python3 bench.py --transcripts ./bundles --models llama3.1:8b \
      --pipelines single,mapreduce --ollama http://127.0.0.1:11434
"""

from __future__ import annotations

import argparse
import json
import random
import re
import string
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
PROD_PROMPT_PATH = HERE / ".." / ".." / "python-service" / "prompts" / "general.md"

MAP_PROMPT = """You are taking faithful notes on ONE CHUNK of a longer meeting transcript.
Write terse bullet notes covering: facts stated, any explicit decisions, any
tasks someone said they will do (with the speaker as owner), names mentioned.
Use ONLY what this chunk states — no inference, no invented names or numbers.
Keep specific terms exactly as written, even if they look garbled.

CHUNK:
{chunk}

BULLET NOTES:"""

REDUCE_PROMPT = """You are an expert meeting note taker. Below are faithful bullet notes taken
chunk-by-chunk over one meeting, in order. Merge them into structured meeting
notes with EXACTLY these markdown sections:
### Attendees
### Key Topics Discussed
### Decisions Made
### Action Items
### Follow-ups Needed

Rules: use ONLY facts present in the notes; for Attendees use the provided
roster if given (else the named speakers); a topic discussed is NOT a
decision; an Action Item needs an owner; write "None mentioned" for an empty
section; never invent or "clean up" names, numbers, or terms.

CHUNK NOTES:
{notes}

MEETING NOTES:"""


def ollama_generate(base_url: str, model: str, prompt: str, timeout: int = 900) -> str:
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            # think:false — qwen3 models otherwise burn the whole num_predict
            # budget on <think> chains and return an EMPTY response (caught on
            # the first real-corpus run: 40-byte "summaries").
            "think": False,
            # num_ctx: Ollama's 4K default SILENTLY TRUNCATES long transcripts
            # (the app's old June num_ctx bug, reproduced here on the first
            # real 21K-char interview — a 3s "summary" of a cut-off input).
            # num_predict caps runaway generations on tiny models.
            "options": {"temperature": 0.2, "num_ctx": 32768, "num_predict": 4096},
        }
    ).encode()
    req = urllib.request.Request(
        f"{base_url}/api/generate", data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        text = json.loads(resp.read())["response"]
    # Thinking models (qwen3 family) emit <think>…</think> reasoning — not part
    # of the summary and unfair to judge; strip it.
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def strip_preamble(text: str) -> str:
    """Cut a leading reasoning/preamble block off a FINAL section-formatted
    output. qwen3:4b/1.7b IGNORE Ollama's think:false and emit untagged
    "Let me analyze…" prose before the notes (caught by Hamza as the
    Candidate-D chain-of-thought leak; think:false didn't fix it on this
    Ollama). The real deliverable starts at the first `###` heading, so drop
    everything before it. No `###` → return as-is (short/degenerate output)."""
    idx = text.find("###")
    return text[idx:].strip() if idx > 0 else text.strip()


def load_transcript(path: Path) -> tuple[str, str, str, str] | None:
    """Return (stem, transcript, existing_summary, attendees) from a bundle/txt.

    The app feeds its summarizer the `attendees` metadata roster, so the bench
    must too — otherwise the small models can't name speakers and the compare
    is unfair (the 2026-07-19 attendee mistake). The existing summary is the
    app's own (35B) output, joined to each judge pack as a blind baseline.
    """
    if path.suffix == ".txt":
        return path.stem, path.read_text(), "", ""
    if path.name.endswith(".json"):
        try:
            data = json.loads(path.read_text())
            meeting = data.get("meeting", data)
            transcript = meeting.get("transcript", "")
            if transcript.strip():
                return (
                    path.stem.replace(".adversaria", ""),
                    transcript,
                    meeting.get("summary", "") or "",
                    ", ".join(meeting.get("attendees", []) or []),
                )
        except (json.JSONDecodeError, AttributeError):
            pass
    return None


def chunk_text(text: str, target: int = 6000) -> list[str]:
    """Split on line boundaries into ~target-char chunks (keeps turns whole)."""
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for line in text.splitlines():
        if size + len(line) > target and current:
            chunks.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def markdown_prompt(prod_prompt: str) -> str:
    """The production prompt keeps a valuable grounding discipline but demands
    JSON output. This bench compares readable notes, so swap the JSON framing
    for markdown IN PLACE — appending "not JSON" instead created a
    contradiction that made models leak chain-of-thought (caught on the first
    real run). The app has no conflict; this is a bench-only adaptation."""
    return prod_prompt.replace(
        "as JSON matching the required schema",
        "as clean markdown with each field as a `###` section heading",
    )


def roster_line(attendees: str) -> str:
    return (
        f"\n\nKnown attendees (from the meeting roster — use these names for the "
        f"attendees list and where the transcript makes a speaker mapping clear; "
        f'otherwise use "Speaker N"): {attendees}'
        if attendees.strip()
        else ""
    )


def run_single(
    base_url: str, model: str, prod_prompt: str, transcript: str, attendees: str = ""
) -> str:
    prompt = (
        f"{markdown_prompt(prod_prompt)}{roster_line(attendees)}\n\nOutput ONLY the "
        f"notes — no preamble, reasoning, or analysis. Start directly with the first "
        f"`###` heading.\n\nTRANSCRIPT:\n{transcript}\n\nNOTES:"
    )
    return strip_preamble(ollama_generate(base_url, model, prompt))


def run_mapreduce(base_url: str, model: str, transcript: str, attendees: str = "") -> str:
    notes = []
    for i, chunk in enumerate(chunk_text(transcript), 1):
        notes.append(f"[chunk {i}]\n" + ollama_generate(base_url, model, MAP_PROMPT.format(chunk=chunk)))
    reduce = REDUCE_PROMPT.format(notes="\n\n".join(notes)) + roster_line(attendees)
    return strip_preamble(ollama_generate(base_url, model, reduce))


JUDGE_HEADER = """# Judge pack — {stem}

Blind evaluation: candidates are labeled with letters only (mapping in
labels.json — DO NOT open it until you have scored). Paste everything below,
plus the transcript file, into your judge LLM.

---

You are judging meeting summaries against their source transcript. Score each
candidate 1-10 on: COVERAGE (key content captured), FAITHFULNESS (nothing
invented — verify names/numbers/decisions against the transcript; hallucination
caps the score at 4), ACTION ITEMS (each real task captured with the right
owner, no fake ones), STRUCTURE (clean sections). Then give an OVERALL 1-10 and
a one-line verdict per candidate. Judge strictly and independently.

TRANSCRIPT: see accompanying file `transcript.txt`.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcripts", required=True, help="folder of .adversaria.json / .txt")
    ap.add_argument("--models", required=True, help="comma-separated ollama model names")
    ap.add_argument("--pipelines", default="single,mapreduce")
    ap.add_argument("--ollama", default="http://127.0.0.1:11434")
    ap.add_argument("--out", default="results", help="output dir (use results-real for real transcripts — gitignored)")
    args = ap.parse_args()

    prod_prompt = PROD_PROMPT_PATH.resolve().read_text() if PROD_PROMPT_PATH.resolve().exists() else ""
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    pipelines = [p.strip() for p in args.pipelines.split(",") if p.strip()]
    out_root = HERE / args.out

    sources = sorted(Path(args.transcripts).iterdir())
    loaded = [t for t in (load_transcript(p) for p in sources) if t]
    if not loaded:
        raise SystemExit(f"No transcripts found in {args.transcripts}")

    for stem, transcript, existing_summary, attendees in loaded:
        out = out_root / stem
        out.mkdir(parents=True, exist_ok=True)
        (out / "transcript.txt").write_text(transcript)
        (out / "attendees.txt").write_text(attendees)
        candidates: list[tuple[str, str]] = []  # (condition, summary)
        if existing_summary.strip():
            (out / "baseline__production.md").write_text(existing_summary)
            candidates.append(("baseline__production", existing_summary))
        for model in models:
            for pipeline in pipelines:
                cond = f"{model.replace(':', '_')}__{pipeline}"
                target = out / f"{cond}.md"
                if target.exists():
                    print(f"[skip] {stem} {cond} (exists)")
                    candidates.append((cond, target.read_text()))
                    continue
                t0 = time.time()
                try:
                    if pipeline == "single":
                        summary = run_single(args.ollama, model, prod_prompt, transcript, attendees)
                    else:
                        summary = run_mapreduce(args.ollama, model, transcript, attendees)
                except Exception as e:  # keep the bench going across model failures
                    summary = f"(FAILED: {e})"
                elapsed = time.time() - t0
                target.write_text(f"<!-- {cond} | {elapsed:.1f}s -->\n\n{summary}\n")
                print(f"[done] {stem} {cond} in {elapsed:.1f}s")
                candidates.append((cond, summary))

        # Blind judge pack: shuffle deterministically per meeting.
        rng = random.Random(stem)
        shuffled = candidates[:]
        rng.shuffle(shuffled)
        letters = string.ascii_uppercase
        labels = {letters[i]: cond for i, (cond, _) in enumerate(shuffled)}
        pack = [JUDGE_HEADER.format(stem=stem)]
        for i, (_cond, summary) in enumerate(shuffled):
            pack.append(f"\n## Candidate {letters[i]}\n\n{summary}\n")
        (out / "JUDGE_ME.md").write_text("\n".join(pack))
        (out / "labels.json").write_text(json.dumps(labels, indent=2))
        print(f"[pack] {out / 'JUDGE_ME.md'} ({len(candidates)} candidates)")


if __name__ == "__main__":
    main()
