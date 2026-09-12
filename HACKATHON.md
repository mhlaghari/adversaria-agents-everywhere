# Agents, Everywhere: Adversaria at the AI Tinkerers hackathon (2026-09-12, team OOM)

## The pain point

I lead an AI/ML team. My day is client meetings, design reviews and stand-ups, and every one of them ends with research, follow-ups and drafts that eat the time I need for my own projects. The agent I want does not live in a chatbox. It lives in the meeting, catches the work as it is spoken, and has it done by the time I am back at my desk.

## Prior work (built before the hackathon, disclosed)

- **Adversaria**, the local meeting engine: on-device dual-channel capture, Whisper transcription, local-LLM notes, SQLCipher storage, macOS and Windows. Nothing leaves the machine by default.
- **Workspaces** (August 2026): a tab where meeting to-dos become tasks and agent runs (local model, Claude Code or Codex) execute them into artifacts. 26 runs completed before today.
- **Live Copilot** (September 2026): while a meeting runs, questions are detected on the live captions, passages are retrieved from folder-scoped sources, and a spoken answer is streamed from a local or cloud model.

## Built at the hackathon

_To be filled in by the team as it lands today. Keep it to what was actually built between 11:15 and 15:30._

## Demo

_Three minutes: a mock design review with one question (copilot card), two commitments caught live (workspace tasks created on the spot), one finished artifact approved before the recording stops._

## Run it

One command after the clone. It checks the toolchain (Node, Rust, uv, ffmpeg, Ollama), installs what is missing, pulls the local models, starts the Python service and launches the app in dev mode, which is the mode that shows the Workspaces tab. The Copilot tab is inside the recording companion.

```
macOS:    ./start.sh
Windows:  .\start.ps1
```

First run downloads the Whisper model and a 3 GB local LLM (set `SMALL_MODELS=0` for the 35B copilot model). Copilot cloud modes need a DeepSeek or Anthropic key in Settings › Live Copilot; Local needs nothing.
