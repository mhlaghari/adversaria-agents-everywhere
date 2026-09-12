# Meeting Note Taker — Design Spec

**Date:** 2026-06-11
**Status:** Draft

## Overview

A cross-platform (Windows first, macOS later) desktop AI meeting note taker inspired by Granola. Captures device audio during meetings, transcribes it locally with speech-to-text, and generates structured notes using a local LLM (with optional cloud fallback). No bot joins the call — audio is captured at the OS level.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TAURI DESKTOP APP                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │
│  │  System   │  │  Global   │  │   Meeting Auto-      │  │
│  │  Tray     │  │  Hotkeys  │  │   Detection          │  │
│  └──────────┘  └──────────┘  └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Rust Backend (Tauri)                  │   │
│  │  • WASAPI loopback audio capture (Windows)        │   │
│  │  • Mic + system audio as split channels           │   │
│  │  • Saves WAV files to temp directory              │   │
│  │  • HTTP client → calls Python service             │   │
│  │  • SQLite storage for meeting history             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Web UI (React + Tailwind)            │   │
│  │  • Recent meetings list with search               │   │
│  │  • Note viewer / editor                           │   │
│  │  • Settings (hotkeys, devices, API keys)          │   │
│  │  • Prompt template selector                       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │ HTTP (localhost:9876)
┌─────────────────────────▼───────────────────────────────┐
│                PYTHON ML SERVICE (FastAPI)                │
│  ┌──────────────────┐  ┌─────────────────────────────┐  │
│  │  Transcriber      │  │  Summarizer                  │  │
│  │  faster-whisper   │  │  Ollama → local LLM          │  │
│  │  large-v3 (int8)  │  │  Cloud fallback → Claude API │  │
│  └──────────────────┘  └─────────────────────────────┘  │
│  • Audio deleted immediately after transcription         │
│  • Transcripts returned as text to Tauri                 │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. User presses hotkey (or auto-detection fires) → Rust backend starts WASAPI loopback recording
2. Audio captured in two channels: microphone + system audio output
3. On stop → WAV file(s) saved to temp directory
4. Tauri sends file path to Python service via HTTP POST
5. Python transcribes with faster-whisper, returns transcript → **audio file deleted immediately**
6. Transcript sent to Ollama (local LLM) with selected prompt template
7. If local LLM fails (timeout >30s) → falls back to Claude API (if configured)
8. Structured summary + transcript saved to SQLite, UI refreshes

## Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Desktop shell | Tauri v2 | Rust backend, ~15MB binary, system tray, global shortcuts, cross-platform |
| Frontend | React + Tailwind CSS | Lightweight, Tauri's first-class webview support |
| Audio capture (Win) | WASAPI loopback (Rust `wasapi` crate) | Zero-latency system audio capture, split mic+system channels |
| Audio capture (macOS) | BlackHole + AVAudioEngine | Same concept — deferred to post-Windows phase |
| STT engine | faster-whisper large-v3 (int8) | ~12x real-time on GPU, ~2.5GB VRAM, best accuracy |
| Local LLM runtime | Ollama | One-command model management, HTTP API, GPU acceleration out of the box |
| Local LLM model | Llama 3.1 8B or Mistral 7B | Fits in 32GB VRAM alongside whisper, strong summarization |
| Cloud fallback | Claude API (Anthropic) | Best-in-class summarization, used only when local fails or user opts in |
| Python service | FastAPI + uvicorn | Lightweight async HTTP, auto-started by Tauri |
| Storage | SQLite (via `rusqlite`) + JSON transcripts on disk | Zero-config, portable, human-readable backups |

## Meeting Auto-Detection

The Rust backend runs a polling watcher (every 3 seconds) checking two signals:

1. **Process monitor** — enumerates running processes, matches against known meeting executables: `zoom.exe`, `ms-teams.exe`, `teams.exe`, `chrome.exe` (with meeting-domain window titles), `Meet`, `discord.exe`
2. **Audio activity** — uses WASAPI session enumerator to detect active audio render streams (sound is actually playing, not just an idle device)

When both signals are positive for a configurable duration (default: 5 seconds), the app:
- Shows a notification: "Meeting detected — Start recording?"
- Or auto-starts if the user has enabled that preference

## Prompt Templates System

Users select a meeting type before or after recording. Each template is a Markdown file in `~/.meeting-note-taker/prompts/` containing the system prompt sent to the LLM.

### Built-in Templates

| Template | Use Case | Prompt Focus |
|----------|----------|-------------|
| **1-on-1** | Manager 1:1s, mentorship | Action items, personal updates, blockers, follow-ups |
| **Client meeting** | Sales, account reviews | Client needs, objections, next steps, relationship notes |
| **Team standup** | Daily syncs | Status updates, blockers, what each person is working on |
| **Brainstorming** | Design sessions, ideation | Ideas generated, decisions deferred, open questions |
| **Interview** | Hiring, user research | Candidate/research insights, key quotes, evaluation |
| **General** | Default catch-all | Balanced summary of decisions, actions, and key points |

Templates are editable. Users can add custom templates by dropping new `.md` files into the prompts directory.

## Summary Output Format

The LLM is instructed to produce structured JSON:

```json
{
  "title": "Weekly Product Sync",
  "date": "2026-06-11T10:00:00",
  "duration_minutes": 32,
  "attendees": ["Alice", "Bob", "Charlie"],
  "summary": "Discussed Q3 roadmap priorities. Alice presented...",
  "key_points": [
    "Launch date pushed to August 15",
    "Postgres selected for the new service",
    "Budget approved for two additional engineers"
  ],
  "decisions": [
    "Use Postgres for the analytics service",
    "Hire two backend engineers by July"
  ],
  "action_items": [
    {
      "task": "Draft database migration plan",
      "assignee": "Alice",
      "deadline": "2026-06-18"
    },
    {
      "task": "Post job listings for backend roles",
      "assignee": "Bob",
      "deadline": "2026-06-13"
    }
  ]
}
```

If the LLM output is not valid JSON, the raw markdown summary is saved and shown as-is. A "Regenerate" button retries with a stronger formatting instruction.

## Configuration & Storage

```
~/.meeting-note-taker/
├── config.json          # Hotkeys, auto-detect toggle, default template, audio device, API key
├── prompts/             # Prompt template .md files
│   ├── 1-on-1.md
│   ├── client-meeting.md
│   ├── standup.md
│   ├── brainstorming.md
│   ├── interview.md
│   └── general.md
├── meetings/            # SQLite DB + JSON transcript files
│   └── meeting-notes.db
└── logs/                # Application logs
```

`config.json` schema:
```json
{
  "hotkeys": {
    "start_stop": "Ctrl+Shift+M",
    "toggle_window": "Ctrl+Shift+N"
  },
  "auto_detect": {
    "enabled": true,
    "auto_start": false,
    "confidence_duration_sec": 5
  },
  "audio": {
    "input_device": null,
    "output_device": null,
    "split_channels": true
  },
  "default_prompt_template": "general",
  "cloud_fallback": {
    "enabled": false,
    "provider": "claude",
    "api_key": null
  },
  "local_llm": {
    "model": "llama3.1:8b",
    "timeout_sec": 30
  }
}
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Audio device unavailable | Show error with device name, offer settings to reconfigure |
| faster-whisper fails | Retry once, if still failing show error with option to retry later |
| Local LLM timeout (>30s) | Auto-fallback to cloud if configured, otherwise keep raw transcript with "Generate Summary" button |
| Cloud API unreachable | Save raw transcript, show error with retry button |
| Invalid LLM output (not JSON) | Save markdown output as-is, show parsed view, offer "Regenerate" |
| Recording started with no audio | Detect silence after recording ends, warn user "No audio detected in recording" |

## Privacy

- Audio files are deleted immediately after transcription completes
- No audio ever leaves the local machine
- Cloud fallback sends only the transcript text (not audio) and only when explicitly enabled
- All data stored in `~/.meeting-note-taker/` — no vendor lock-in, fully portable
- No telemetry, no analytics, no phoning home

## Scope & Phasing

### Phase 1: Windows MVP
- Tauri shell with system tray and global hotkey
- WASAPI loopback audio capture (mixed stream: mic + system)
- faster-whisper transcription (post-meeting, not real-time)
- Ollama local summarization with General + 1-on-1 + Client templates
- Basic UI: meetings list, note viewer, settings

### Phase 2: Polish & Auto-Detection
- Split channel recording (mic vs system audio)
- Meeting auto-detection (process + audio activity polling)
- All 6 prompt templates
- Cloud fallback (Claude API)
- SQLite storage with search

### Phase 3: macOS Support
- BlackHole + AVAudioEngine audio capture
- macOS system tray, permissions flow
- Platform parity with Windows

### Phase 4: Power Features
- Real-time transcription preview (optional — streaming whisper)
- Cross-meeting search ("what did 3 clients say about pricing?")
- Export to Markdown, Notion, Obsidian
- Speaker diarization (who said what)

## Non-Goals for V1

- Real-time transcription streaming
- Speaker diarization
- Calendar integration
- Cloud sync between devices
- Mobile companion app
- Meeting platform bot mode (we are deliberately bot-free)
