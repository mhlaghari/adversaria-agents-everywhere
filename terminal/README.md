# Adversaria Terminal

Meeting Note Taker, **in the terminal** — a second presentation surface next to
the Tauri desktop app. Same privacy rules, nothing leaves the machine: it talks
to the same local Python ML service (FastAPI on `:9876`), keeps its **own**
SQLite history, and records audio on-device. No bot joins calls; audio is
deleted once a meeting is transcribed.

```
React/Tauri UI ── AMAZING desktop app ─┐
                                      ├─▶ Python ML service :9876 ── Whisper + Ollama
advterm (this TUI + CLI) ─────────────┘
```

## Prerequisites

- Python 3.11+ and [uv](https://docs.astral.sh/uv/)
- The **Python ML service running** (see repo root `docs/HANDOFF.md`):
  ```
  cd python-service
  uv sync --extra cuda        # or omit --extra cuda on CPU-only machines
  uv run uvicorn src.server:app --host 127.0.0.1 --port 9876
  ```
- Ollama running with a model pulled for summaries (`ollama pull llama3.1:8b`).
- At least one Whisper model downloaded, e.g. `advterm download-model large-v3`
  (transcription fails with a clear message until then).

## Install

```powershell
cd terminal
uv sync            # creates .venv with textual, httpx, soundcard, numpy
```

## Run

```powershell
uv run advterm                 # full TUI
uv run advterm --data-dir C:\path\other-meetings   # isolated data dir
```

### TUI

- `ctrl+r` Record (system + mic, live captions), `ctrl+m` Meetings,
  `ctrl+i` Import, `ctrl+t` To-dos, `ctrl+e` Templates, `ctrl+l` Models,
  `ctrl+s` Settings, `escape` Back / Quit.

### CLI one-shots (scriptable)

```
advterm health                      check the Python service
advterm list                        browse meeting history
advterm notes [--meeting ID]        print notes (latest meeting by default)
advterm transcript [--meeting ID]   print the raw transcript
advterm ask "what was decided?"     grounded Q&A over a meeting
advterm todos                       open action items across meetings
advterm templates                   list note templates
advterm models                      list transcription models + download state
advterm download-model <key>        download a Whisper model on-device
advterm record [--seconds N]        record, transcribe, summarize → note
advterm import <audio-file>         transcribe + summarize an existing file
advterm export [--meeting ID]       write notes to markdown
```

## Where things live

| What                     | Where (`%APPDATA%\adversaria-terminal` by default) |
|--------------------------|----------------------------------------------------|
| History (SQLite)         | `meetings.db` (plain; the desktop's DB is untouched) |
| Recent audio             | `audio/` (deleted after a successful transcription)  |
| Config                   | `config.json` (own copy of the desktop's settings)   |

Override with `--data-dir` or the `ADVERSARIA_TERMINAL_DIR` env var.

## Tests

```powershell
cd terminal
uv run pytest          # unit tests (util, storage, client, audio) — no ML deps
```

## Notes

- Sound capture uses `soundcard` (WASAPI loopback for system audio + default
  input for the mic). System audio appears as a **Speaker** loopback device.
- Live captions stream in the Record screen via the service's `/live_feed`
  deltas; transcription & summarization happen after stop.
- Settings here are the terminal's own; changing the desktop app does not
  change them (and vice-versa).