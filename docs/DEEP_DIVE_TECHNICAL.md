# Adversaria — Technical Deep Dive

> **Product:** Adversaria (formerly "Meeting Note Taker") — v0.3.14  
> **Company:** Laghari Labs  
> **Repository:** `meeting-note-taker` (private)  
> **Companion:** [DEEP_DIVE_BUSINESS.md](./DEEP_DIVE_BUSINESS.md)
> **Latest feature update:** 2026-08-30 — Meeting projects / ProjectView (working tree, uncommitted)

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Layer 1 — React Frontend](#2-layer-1--react-frontend)
3. [Layer 2 — Tauri/Rust Backend](#3-layer-2--taurirust-backend)
4. [Layer 3 — Python ML Service](#4-layer-3--python-ml-service)
5. [End-to-End Data Flow](#5-end-to-end-data-flow)
6. [Platform Isolation](#6-platform-isolation)
7. [Storage & Encryption](#7-storage--encryption)
8. [Key Features — How They Work](#8-key-features--how-they-work)
9. [Tech Stack Summary](#9-tech-stack-summary)
10. [Build & Packaging](#10-build--packaging)
11. [Testing & CI](#11-testing--ci)
12. [Knowledge Graph Internals](#12-knowledge-graph-internals)
13. [Diarization Internals](#13-diarization-internals)
14. [Export/Import Bundle System](#14-exportimport-bundle-system)
15. [Known Technical Debt](#15-known-technical-debt)
16. [Architectural Decisions (ADR Index)](#16-architectural-decisions-adr-index)

---

## 1. System Architecture

Adversaria is a **three-layer local desktop application**:

```
┌──────────────┐  invoke()   ┌────────────────────┐  HTTP :9876   ┌─────────────────────────┐
│  React UI    │ ──────────▶ │   Tauri (Rust)     │ ────────────▶ │ Python ML Service       │
│  (webview)   │ ◀────────── │   Backend          │ ◀──────────── │ (FastAPI / uvicorn)     │
└──────────────┘  Promise    └────────────────────┘  JSON         └─────────────────────────┘
                                │   │                                  │              │
                                │   └─ SQLite (%APPDATA%)              │              │
                                └────  WASAPI / SCK capture → WAV    faster-whisper  Ollama/Rapid-MLX
                                       (system + mic)                 (GPU)          (localhost)
```

**Key design properties:**
- All three layers run on one machine. The only network traffic is loopback HTTP.
- The webview (React) has **no direct network access** to the Python service — Rust proxies every call via `reqwest`.
- Platform-specific code is `#[cfg]`-gated; shared code (React UI, SQLite, config, HTTP plumbing) is identical across OSes.
- The LLM server (Ollama or Rapid-MLX) is external — the user starts it separately (or via a login LaunchAgent on macOS).

---

## 2. Layer 1 — React Frontend

**Stack:** React 18.3 · TypeScript 5.9 · Vite 6 · Tailwind 3.4 · `@tauri-apps/api` v2

### Structure

```
src/
├── App.tsx                  # Root component: view router, recording lifecycle, event wiring
├── main.tsx                 # Entry point (production right-click guard)
├── prototype.css            # Dark-glass theme system (self-hosted Inter, glass tokens, animations)
├── lib/
│   ├── tauri.ts             # Single typed IPC boundary — 1:1 mapping to Rust commands
│   ├── summary.ts           # summaryToHtml markdown renderer (RTL-aware, action-item checkboxes)
│   ├── exportDocument.ts    # buildSlideHtml — self-contained dark "Meeting Minutes" slide
│   ├── pin.ts               # PBKDF2 PIN hashing for privacy lock
│   └── errors.ts            # Friendly error messages (BYOK test, LLM-down, etc.)
├── hooks/
│   ├── useRecording.ts      # Recording lifecycle + background transcription queue
│   ├── useMeetings.ts       # List + selection + CRUD
│   └── useConfig.ts         # Load/merge/save config
└── components/
    ├── RecordingControls.tsx
    ├── MeetingsList.tsx      # Date heatmap, tag pills, ⋯ action menu, search
    ├── NoteViewer.tsx        # Summary/Transcript/MyNotes/Chat tabs
    ├── GraphView.tsx         # Knowledge Graph (cytoscape.js + d3-force)
    ├── AppShell.tsx
    ├── Settings.tsx          # AI Engine, Prompts, Data, Calendar, Feedback tabs
    ├── TodosView.tsx         # Today/All/Overdue/Completed filters
    ├── WeeklyView.tsx        # Mon–Sun meeting digest
    ├── AskAllView.tsx        # Cross-meeting Q&A with intent routing
    ├── MeetingChat.tsx       # Streaming chat with a single meeting
    ├── RecordingBubble.tsx   # Floating always-on-top widget
    ├── DateHeatmap.tsx       # Calendar heatmap by meeting count
    ├── RecordingNotes.tsx    # Live notepad while recording
    ├── ErrorBanner.tsx
    └── UpdatePrompt.tsx      # Auto-updater toast
```

### Key patterns

- **No `React.FC`** — function components with explicit prop interfaces.
- **Immutable state** — spread updates, never mutate.
- **Typed IPC boundary** — `lib/tauri.ts` every function maps to exactly one Rust `#[tauri::command]`. All return `Promise<T>` and reject with the Rust error string. No `any`.
- **Background transcription queue** (`useRecording.ts`) — stop recording enqueues a transcription job; a single-worker drain (concurrency 1, paused while recording) calls `transcribeMeeting(id)`. This enables back-to-back recordings.
- **Streaming chat** — the `/chat_stream` SSE endpoint is consumed via Rust's `reqwest::Response::chunk()` → Tauri `Channel` → event-driven incremental render in `MeetingChat.tsx`.

### Theme system

Dark-glass design language defined in `prototype.css`:
- Inverted Tailwind `gray` ramp (cream → dark for the whole app at once)
- CSS custom properties for accent (`--accent`), glass (`--glass-bg`, `--glass-border`), typography (`--font-body: 'Inter Variable'`)
- `backdrop-filter: blur()` on modals and cards
- Self-hosted Inter variable font (bundled, no CDN) via `@fontsource-variable/inter`
- Animation keyframes for the intro splash and slide export

---

## 3. Layer 2 — Tauri/Rust Backend

**Stack:** Tauri v2 · Rust 1.8x · `rusqlite` 0.31 · `reqwest` 0.12 · `tokio` 1 · `chrono` 0.4

### Structure

```
src-tauri/src/
├── lib.rs                    # App entry: plugins, AppState, setup (tray/hotkey/DB/config)
├── main.rs                   # Entry point
├── commands.rs               # 25+ IPC commands + AppState
├── audio/
│   ├── mod.rs                # Platform-agnostic surface: AudioCapture trait, RecordingPaths, write_wav_file
│   ├── wasapi.rs             # Windows dual capture (WASAPI loopback + mic)
│   └── macos.rs              # macOS dual capture (ScreenCaptureKit + cpal)
├── http_client.rs            # Typed reqwest client for all Python service endpoints
├── storage.rs                # SQLite via rusqlite (SQLCipher encrypted; FTS5; migrations)
├── config.rs                 # AppConfig JSON load/save
├── tray.rs                   # System tray + Ctrl+Shift+M global hotkey
├── types.rs                  # Shared serde types (Meeting, AppConfig, DTOs)
├── detection.rs              # Meeting auto-detect (Win: registry; macOS: CoreAudio process list)
├── calendar/
│   ├── mod.rs                # Calendar trait + dispatch
│   ├── google.rs             # Google Calendar OAuth (PKCE + loopback)
│   └── microsoft.rs          # Microsoft Graph stubbed (not yet implemented)
├── recap.rs                  # Weekly recap generation (0-LLM, from action_items table)
└── bubble.rs                 # Floating recording bubble window management
```

### AppState

```rust
pub struct AppState {
    pub capture: Mutex<Option<AudioCapture>>,
    pub recording_paths: Mutex<Option<RecordingPaths>>,
    pub client: HttpClient,                // RwLock<base_url> for live config updates
    pub sidecar_command: Mutex<Option<CommandChild>>,
    pub app_handle: AppHandle,
}
```

`AppState` is Tauri-managed (injected into every `#[tauri::command]` via `State<AppState>`). The `HttpClient.base_url` is `RwLock<String>` — each request reads a cloned snapshot (guard dropped before `.await`), so Settings URL changes take effect immediately with no restart.

### Audio capture design

**Dual capture (system "Them" + mic "Me"):**
- Two independent capture threads, writing raw float PCM to separate WAV files.
- **Windows:** WASAPI loopback on the default render device + WASAPI capture on the default input device. 32-bit float, shared mode.
- **macOS:** ScreenCaptureKit (`SCStream` held in `AudioCapture` so it survives start/stop IPC) for system audio + `cpal` for mic. Planar f32 @ 48 kHz interleaved to float-WAV. Screen Recording permission required.

Mic capture is **best-effort** on both platforms: a missing/failing/denied mic flags itself not-OK and the meeting proceeds with system audio only — never aborts.

**Rolling live caption:** while recording, a background task snapshots the last `LIVE_WINDOW_SECS` (30s) of system audio every `LIVE_CHUNK_SECS` (12s) into a temp WAV → `POST /transcribe_chunk` → `live-transcript` Tauri event → caption pane.

### SQLite / Storage

- `rusqlite` with `bundled-sqlcipher-vendored-openssl` feature (SQLCipher for encryption-at-rest).
- **Key management:** random 256-bit key stored in the OS keychain (macOS Keychain, Windows Credential Manager). Applied via `PRAGMA key` on every connection open.
- Tables: `meetings`, `chat_messages`, `action_items`, `ask_messages`
- **FTS5** (full-text search): `meetings_fts` virtual table over title/summary/transcript with sync triggers
- **Migrations:** idempotent `ALTER TABLE` / column-add pattern — no migration framework; `init_db()` adds columns if missing, drops+rebuilds FTS5 index if corrupted
- Per-request connection (no pool; fine for single-user)

### IPC Commands (25+)

```
start_recording , stop_recording , enqueue_recording , transcribe_meeting
get_meetings , get_meeting , delete_meeting , set_meeting_pinned
set_meeting_locked , set_meeting_tags , update_meeting_summary
update_meeting_notes , update_attendees , update_action_item
import_audio , pick_audio_file , transcribe_import
export_meeting , export_html , export_bundle , import_bundle
backup_all , restore_all
get_config , update_config , check_service_health
list_whisper_models , download_whisper_model
resummarize_meeting , chat_with_meeting
get_action_items , get_weekly_recap
test_llm_connection , biometric_authenticate
get_audio_level , submit_signup
bubble_start_drag , bubble_stop_recording
get_meeting_graph , get_meeting_actions_summary
update_config_key
```

---

## 4. Layer 3 — Python ML Service

**Stack:** FastAPI ≥0.115 · uvicorn ≥0.34 · Pydantic v2 · ollama (py) 0.6.x · httpx

### Structure

```
python-service/
├── src/
│   ├── server.py             # FastAPI app: 7 endpoints, lifespan singletons
│   ├── transcriber.py        # Whisper backend (faster-whisper / MLX / cloud)
│   ├── diarizer.py           # sherpa-onnx offline speaker diarization
│   ├── summarizer.py         # LLM backend abstraction (Ollama / OpenAI-compatible)
│   ├── config.py             # Prompt template discovery/loading
│   └── models.py             # Pydantic request/response models
├── prompts/
│   ├── general.md            # Default summarization template
│   ├── one-on-one.md         # 1:1 meeting template
│   └── client-meeting.md     # Client-facing meeting template
└── tests/
    └── test_*.py             # 126+ tests (ML deps mocked; <1s to run)
```

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Readiness: `{status, whisper_model, ollama_available}` |
| `GET` | `/templates` | List prompt templates |
| `GET` | `/templates/{name}` | Raw template content |
| `GET` | `/whisper_models` | List available Whisper models + download status |
| `POST` | `/whisper_download` | Initiate model download |
| `POST` | `/transcribe` | Speech-to-text (+ optional diarization) |
| `POST` | `/summarize` | Transcript → structured notes |
| `POST` | `/chat` | Grounded Q&A (non-streaming) |
| `POST` | `/chat_stream` | Streaming Q&A (SSE) |

### Transcription backend (ADR-010)

Two backends behind a `create_transcriber()` factory, selected by `WHISPER_BACKEND` env or auto-detected:

**`WhisperTranscriber`** (faster-whisper / CTranslate2) — Windows/CUDA:
- Patches Windows PATH for pip-installed `nvidia-*` CUDA DLLs
- Auto-detects CUDA → GPU (`compute_type=float16`); falls back to CPU (`int8`)
- `vad_filter=True`, `beam_size=5`
- Model: `large-v3` default (overridable via `WHISPER_MODEL`)

**`MlxWhisperTranscriber`** (mlx-whisper) — macOS Apple Silicon:
- Runs `whisper-large-v3-mlx` on Metal GPU via MLX
- Greedy decoding only (MLX doesn't support beam search)
- Silence-hallucination suppression: `no_speech_threshold`, `logprob_threshold`, `compression_ratio_threshold`, `condition_on_previous_text=False`
- Requires system `ffmpeg` CLI for audio decoding

Both share `transcribe_dual(mic_wav, system_wav, me_label, vocabulary, diarize)`:
1. Transcribe each channel separately
2. Optionally run diarization on system channel (sherpa-onnx → `Speaker 1/2/…`)
3. `merge_labeled_segments()` interleaves all segments by start time into a dialogue
4. `relabel_me()` rewrites `Me:` → the user's configured name

**Cloud transcription** (opt-in): OpenAI-compatible `/audio/transcriptions` API (e.g. Groq). Downsampled to 16 kHz mono and chunked under the 25 MB upload cap. No diarization in cloud mode.

### Summarizer backend (ADR-009)

Backend-agnostic via `default_llm_backend()`:
- **macOS:** Rapid-MLX (OpenAI-compatible, `qwen3.6-27b` on port 8000)
- **Windows:** Ollama (`qwen3.6:35b-a3b`)
- **Override:** `LLM_BACKEND` / `LLM_BASE_URL` / `LLM_API_KEY` env vars

Key behaviors:
- Loads a prompt template (e.g. `general.md`) with `{{transcript}}` substitution
- Requests structured JSON via Ollama `format=` or OpenAI `response_format: json_schema`
- `_unwrap_envelope()` handles model-specific JSON quirks (extra whitespace, reasoning tags, partial wrapping)
- `_strip_think()` / `_strip_think_stream()` remove `<think>…</think>` blocks from reasoning models (Groq, DeepSeek)
- Provider quirk adaptation: drops `chat_template_kwargs` on servers that reject it (Groq); falls back `json_schema` → `json_object` on servers that lack schema support (DeepSeek)
- `num_ctx` set to 16384 (configurable via `OLLAMA_NUM_CTX`)
- `temperature=0` for deterministic output

### Diarization (ADR-012)

**sherpa-onnx** offline speaker diarization:
- Models (~34 MB total, downloaded once): pyannote-segmentation-3.0 ONNX segmentation model + multilingual (zh+en) speaker-embedding model
- Processes only the system-channel WAV (mic stays "Me")
- Threshold-based clustering (tuned to 0.7 after a 2-person call over-segmented at 0.5)
- Returns time-stamped segments → merged by overlap → labeled `Speaker 1/2/…`
- Implemented in `diarizer.py` with `speaker_diarize(system_wav_path)` → list of `(start_sec, end_sec, speaker_label)`
- **Best-effort:** any failure (model missing, audio too short, ONNX error) falls back to flat "Them"
- **Settings toggle** (default on), best-effort, no user-facing diarization controls

---

## 5. End-to-End Data Flow

### Recording → Notes (back-to-back queue)

```
1. User presses Ctrl+Shift+M (or tray/bubble button)
   → Rust: start_recording()
   → Spawns 2 capture threads (system + mic) → temp WAVs

2. User presses Ctrl+Shift+M again
   → Rust: stop_recording() → joins threads, finalizes WAVs
   → Frontend: enqueueRecording(audioPath, template, notes)
   → Rust: save_pending_meeting() → returns pending Meeting (audio kept)
   → Status returns to idle IMMEDIATELY — next recording can start now

3. Back-transcription queue (single worker, concurrency 1, paused while recording)
   → transcribeMeeting(id)
   → Rust reads audio/template/notes from DB row
   → POST /transcribe (audio_path, mic_path, me_label, vocabulary, diarize)
   → Python: transcribe dual-channel → merge speaker labels
   → Returns {text, language, duration_seconds}

4. Rust: POST /summarize (transcript, template, model)
   → Python: LLM returns structured JSON (MeetingNotes schema)
   → Rust: derive title, update DB row in place, DELETE both WAV files

5. Frontend refreshes: meeting now has transcript + summary tabs
```

### Data safety guarantees

- Audio is **only deleted after successful transcription** (set via `config::recordings_dir` → app-data, not temp).
- If transcription fails (service down, model error, timeout), a **pending meeting** is saved with audio kept on disk.
- `NoteViewer` shows a "Not transcribed yet" banner with a **Transcribe now** button.
- Re-summarize at any time with any template — uses stored transcript, no audio needed.

---

## 6. Platform Isolation

### Windows-specific
- **Audio capture:** WASAPI loopback (render device) + WASAPI capture (input device) — `windows` crate 0.58
- **Meeting detection:** Polls Windows `CapabilityAccessManager` registry for mic-in-use
- **GPU:** NVIDIA CUDA via CTranslate2 (`uv sync --extra cuda` for cuBLAS/cuDNN)
- **LLM:** Ollama (`qwen3.6:35b-a3b`) — default path

### macOS-specific (Apple Silicon)
- **Audio capture:** ScreenCaptureKit (system audio, `screencapturekit` 7.0.1) + `cpal` 0.18 (mic)
- **Meeting detection:** CoreAudio process-object list (`coreaudio-sys` 0.2 + `core-foundation` 0.10)
- **GPU:** Apple Silicon GPU via MLX (`mlx-whisper` 0.4.3 + `mlx` 0.31)
- **LLM:** Rapid-MLX (OpenAI-compatible on `:8000/v1`, `qwen3.6-27b` model)
- **Floating bubble:** macOS private API for transparent always-on-top window
- **Calendar:** EventKit (zero sign-in, reads Mac's existing calendars)
- **Known gotcha:** `HF_HUB_DISABLE_XET=1` required for HuggingFace model downloads (broken `hf_xet` on this box; may not reproduce on other Macs)

### Shared (cross-platform)
- React UI (identical)
- SQLite storage + encryption (identical)
- HTTP client (identical)
- Config management (identical)
- MCP server (standalone project, cross-platform)

---

## 7. Storage & Encryption

### Database schema

```sql
meetings (
    id TEXT PRIMARY KEY,
    title TEXT, transcript TEXT, summary TEXT, language TEXT,
    audio_file_path TEXT, duration_seconds REAL,
    template_used TEXT, attendee_names TEXT,
    tags TEXT, -- JSON: [{label, color}]
    transcript_turns TEXT, -- JSON: [{speaker, text}]
    user_notes TEXT, recorded_at TEXT,
    pinned INTEGER DEFAULT 0, locked INTEGER DEFAULT 0,
    category TEXT, pending INTEGER DEFAULT 0
)

action_items (
    id TEXT PRIMARY KEY, meeting_id TEXT REFERENCES meetings(id),
    text TEXT, assignee TEXT, due_date TEXT, done INTEGER DEFAULT 0,
    ord INTEGER
)

chat_messages (
    meeting_id TEXT REFERENCES meetings(id),
    role TEXT, content TEXT, created_at TEXT
)

ask_messages (
    id INTEGER PRIMARY KEY, role TEXT, content TEXT,
    intent TEXT, created_at TEXT
) -- persists cross-meeting Ask history with provenance

-- FTS5 virtual table
CREATE VIRTUAL TABLE meetings_fts USING fts5(
    title, summary, transcript,
    content='meetings', content_rowid='rowid'
);

-- Sync triggers keep FTS index in sync
CREATE TRIGGER meetings_au AFTER UPDATE ON meetings BEGIN
    INSERT INTO meetings_fts(rowid, title, summary, transcript)
    VALUES (new.rowid, new.title, new.summary, new.transcript);
END;
```

### Encryption-at-rest (ADR-011, ADR-013)

- **Algorithm:** SQLCipher (256-bit AES in CBC mode with HMAC authentication)
- **Key storage:** OS-native keychain (macOS Keychain via `security` CLI, Windows Credential Manager via `winapi`)
- **Key generation:** Random 256-bit, generated once per DB
- **Per-request connect pattern:**
  ```rust
  fn connect() -> Connection {
      let conn = Connection::open(&path)?;
      if DB_ENCRYPTED {   // read once at startup
          let key = keychain_get("meeting-note-taker-db-key")?;
          conn.execute_batch(&format!("PRAGMA key = \"x'{}'\";", hex::encode(key)))?;
      }
      Ok(conn)
  }
  ```
- **Lifecycle:**
  - First launch: detect plaintext DB → backup → migrate via `ATTACH DATABASE ... KEY` → verify row count → atomic rename
  - Encryption toggle off: reverse migration (decrypt to plaintext, delete keychain key)
  - No key = DB is unreadable (not just encrypted-file-name)
- **User-toggleable** (ADR-013): Settings switch to turn encryption off (removes the macOS keychain password prompt on every launch). Default: on.

### Storage locations

| OS | Path |
|----|------|
| Windows | `%APPDATA%\meeting-note-taker\` (`meetings.db`, `config.json`) |
| macOS | `~/Library/Application Support/meeting-note-taker/` |

---

## 8. Key Features — How They Work

### Meeting Projects (`MeetingsList.tsx` + `ProjectView.tsx`)

Projects deliberately reuse the existing workspace data model. A colored folder
in the Meetings sidebar is a `workspaces` row; filing a meeting is a
`meeting_workspace_bindings` upsert, so there is no parallel project database or
sync layer. A meeting belongs to at most one project.

- `MeetingsList.tsx` provides project creation, selection, expand/collapse,
  menu/drag filing, and confirmed deletion. Deleting a project removes its
  binding rows and the workspace but preserves every meeting and action item.
- `App.tsx` owns project/binding state and chooses ProjectView, NoteViewer, or the
  empty pane. Opening a note clears project selection so navigation has one
  unambiguous content target.
- `ProjectView.tsx` uses independent responsive columns. The primary column is
  Project overview → Meetings → Standing instructions → Web research; the
  secondary column is open action items. Source meeting names sit under their
  action text rather than consuming a competing half-width column.
- `project_overview.rs` builds bounded context from every filed meeting's title,
  summary, and transcript excerpt and asks the Notes engine for a single grounded
  overview. The exact meeting count and prompt version are part of the prompt;
  ordered sources, instructions, and prompt version are hashed for staleness.
  Cached output survives transient refresh failure. The overview never browses.
- Standing instructions feed both overview generation and workspace-task briefs.
  `network_allowed` governs workspace-task research only and remains off by
  default. Attendee chips are deterministic counts from filed meetings and never
  assign roles the source data did not provide.

### Knowledge Graph (`GraphView.tsx`)

- **Data source:** Existing SQLite — zero LLM, zero network. Rust `get_meeting_graph` builds the graph from `meetings.attendee_names`, `meetings.tags`, and `action_items.assignee`.
- **Filtering:** Generic Speaker-N/Me/Them nodes filtered out (they falsely linked meetings via shared-attendee edges). Owner↔person merged (same person shown as both attendee and action-item assignee). Single-use tags dropped.
- **Rendering:** cytoscape.js (self-hosted in the bundle, no CDN) rendering meetings ↔ people ↔ tags ↔ action-owners as a force-directed layout using **d3-force** physics.
- **Physics:** Infinite drag-tug simulation (Obsidian-style, never settles). Tunable alpha/alphaDecay/velocityDecay — after the "too fluttery" report, constants were adjusted so post-drag wobble drops from 15 px/s to 0 by t=3 s.
- **Interaction:** Click a meeting node → opens that meeting. Legend toggles node visibility by type.
- **Cap:** 500 meetings (safety limit on the Rust side).

### Export/Import Bundle System

- **Bundle format:** `*.adversaria.json` — schema v1 containing `transcript`, `transcript_turns`, `summary`, `attendees`, `tags`, `user_notes`, `action_items`.
- **Export:** From the Export ▾ menu on any meeting → native save dialog → writes JSON.
- **Import:** Sidebar "Import meeting…" button → file picker → `insert_bundle_meeting` (federated re-insert under a fresh ID).
- **Backup-all / Restore-all:** Settings → Data tab. Every meeting + action items + Ask history → one JSON file. Restore re-inserts all with fresh IDs (no conflict).
- **All Rust + frontend:** 4 IPC commands, no Python changes needed.

### Slide Export (`exportDocument.ts`)

- Self-contained dark "Meeting Minutes" slide on a fixed **1280×720** stage
- ADVERSARIA reveal intro animation (pure CSS, zero JS)
- Multi-column accent cards: Key Topics / Decisions / Action Items / Follow-ups from `parseSummary()`
- Gradient title, attendee chips, on-device footer
- Arabic-RTL aware (`unicode-bidi: plaintext`)
- `@page{size:1280px 720px}` so browser Save-as-PDF = one page
- **No in-app PDF** — Tauri's WKWebView no-ops `window.print()` on macOS. PDF is produced by opening the HTML in a browser and saving as PDF.

### Streaming Chat

- Python `/chat_stream` → SSE frames: `data: {"t":"…"}\n` → `[DONE]`
- Rust `http_client.chat_stream()` → `reqwest::Response::chunk()` — multi-byte safe
- Tauri `Channel` → event emitted per chunk → React receives and appends to streaming buffer
- Dual-backend: Ollama + OpenAI-compatible (both stream)

### Cross-Meeting Ask (Intent Routing)

```
User asks: "what were my action items from last week?"

1. Intent classifier (LLM) → "todos"
2. Route to action_items table (0-LLM answer, grouped by meeting)
3. Render: "From your To-dos" provenance badge
4. On empty: fall through to transcript (labeled "not tracked yet")
```

Intents: `todos` | `recap` | `overview` | `detail`. Fail-open to `detail` (transcript-grounded RAG via FTS5).

Guardrails: off-topic/injection ("write python", "ignore instructions") refused. Follow-ups resolved via pronoun substitution before RAG ("which company is he in" → "…is Wajee in").

### Prompt Templates

- Files in `python-service/prompts/*.md` — auto-discovered at startup
- Three bundled: `general`, `one-on-one`, `client-meeting`
- User-editable from Settings (CRUD via API)
- Template syntax: `{{transcript}}` placeholder, delimited speaker-labeled transcript
- Structured output requested via `MeetingNotes` Pydantic schema → JSON → rendered Markdown

### Live Recording Bubble

- Separate always-on-top Tauri webview window shown when main window is minimized/blurred
- Shows: elapsed timer, audio-reactive waveform (RMS polled ~14 Hz via `get_audio_level`), Stop button
- Draggable (Rust `bubble_start_drag` focuses the unfocused bubble window then starts native drag)
- macOS: uses private API for transparency; macOS won't drag an unfocused window — fixed by focusing first

---

## 9. Tech Stack Summary

### Frontend
| Technology | Version | Notes |
|-----------|---------|-------|
| React | 18.3 | Function components, no React.FC |
| TypeScript | 5.9 | Explicit prop interfaces, no `any` |
| Vite | 6 | HMR, build tooling |
| Tailwind CSS | 3.4 | Inverted gray ramp for dark theme |
| cytoscape.js | (bundled) | Knowledge Graph rendering |
| d3-force | (cytoscape extension) | Force-directed graph physics |
| `@tauri-apps/api` | 2 | IPC bridge |
| `@fontsource-variable/inter` | (bundled) | Self-hosted Inter variable font |

### Backend (Rust/Tauri)
| Technology | Version | Notes |
|-----------|---------|-------|
| Tauri | 2 | Desktop shell, IPC, window management |
| `rusqlite` | 0.31 | `bundled-sqlcipher-vendored-openssl` feature |
| `reqwest` | 0.12 | HTTP client to Python service |
| `tokio` | 1 | Async runtime |
| `chrono` | 0.4 | Date/time |
| `windows` | 0.58 | WASAPI audio capture (Windows-only) |
| `screencapturekit` | 7.0.1 | System audio capture (macOS-only) |
| `cpal` | 0.18 | Mic capture (macOS-only) |
| `robius-authentication` | — | Touch ID / Windows Hello biometrics |
| `tauri-plugin-updater` | — | Auto-update |
| `tauri-plugin-oauth` | — | Calendar OAuth |
| `tauri-plugin-global-shortcut` | — | Ctrl+Shift+M hotkey |
| `directories` | 5 | Platform data-dir resolution |

### ML Service (Python)
| Technology | Version | Notes |
|-----------|---------|-------|
| FastAPI | ≥0.115 | Web framework |
| uvicorn | ≥0.34 | ASGI server |
| Pydantic | 2.13 | Request/response validation |
| faster-whisper | 1.2.1 | CUDA transcription (Windows) |
| CTranslate2 | — | GPU inference engine (Windows) |
| mlx-whisper | 0.4.3 | Metal GPU transcription (macOS) |
| mlx | 0.31 | Apple Silicon ML framework |
| sherpa-onnx | — | Speaker diarization |
| ollama (py) | 0.6.x | Local LLM client |
| httpx | — | HTTP client (for cloud/OpenAI) |
| PyAV | — | Audio decode/resample for cloud upload |
| PyInstaller | — | Sidecar bundling for .dmg |

### Models
| Model | Size | Use | Platform |
|-------|------|-----|----------|
| Whisper `large-v3` | ~3 GB | Speech transcription | Windows (CUDA) |
| Whisper `large-v3-mlx` | ~3 GB | Speech transcription | macOS (Metal) |
| Qwen 3.6-35B-A3B (MoE) | ~23 GB, ~3B active | Summarization, Chat, Ask | Windows (Ollama) |
| Qwen 3.6-27B (4-bit) | ~15 GB | Summarization, Chat, Ask | macOS (Rapid-MLX) |
| pyannote-segmentation-3.0 ONNX | ~15 MB | Speaker diarization (segmentation) | Both |
| Speaker embedding model | ~19 MB | Speaker diarization (embedding) | Both |

### Hardware (dev machine)
- **Windows:** RTX 5090 (Blackwell sm_120), 32 GB VRAM
- **macOS:** Apple M5 Max (arm64, macOS 26.5), 64 GB unified memory

---

## 10. Build & Packaging

### Development

```bash
# Terminal 1 — Python ML service
cd python-service
uv sync                       # --extra cuda (Windows) or --extra mlx (macOS)
uv run uvicorn src.server:app --host 127.0.0.1 --port 9876

# Terminal 2 — Desktop app
npm install
npm run tauri dev
```

### Production (.dmg) — one command

```bash
ADVERSARIA_SIGN_IDENTITY="NotchyPrompter Dev" ./scripts/build-dmg.sh
```

What it does:
1. **Freeze the Python ML service** via PyInstaller (`--onedir`) → a standalone `/sidecar` binary
2. **Ad-hoc sign the sidecar** with `python-service/entitlements.plist` + `disable-library-validation`
3. **`tauri build`** the `.app` (embeds the sidecar as a Tauri `externalBin`)
4. **Re-sign the `.app`** with the stable `NotchyPrompter Dev` identity (preserves TCC grants)
5. **Package the `.dmg`** via `hdiutil` (not Apple's `bundle_dmg.sh`, which fails on the large app)
6. **Auto-install** the `.dmg` to `/Applications`

**Artifacts** (gitignored): `src-tauri/target/release/bundle/macos/Adversaria.app`, `dmg/Adversaria_aarch64.dmg` (~483 MB).

### Auto-updater (ADR-014)

- Tauri v2 updater with minisign signing (`tauri signer generate`)
- Artifacts hosted in separate **public** repo: `LaghariLabs/adversaria-releases`
- `bundle.createUpdaterArtifacts: true` → `tauri build` emits signed `.app.tar.gz` + `.sig`
- `scripts/publish-release.sh` builds `latest.json` from `.sig` and cuts the GitHub release
- App auto-checks on launch → dismissible glass toast → download → minisign-verify → relaunch
- **Known issue:** updater artifact is built pre-sign, so auto-updated apps are ad-hoc-signed and lose TCC grants. Fix deferred to notarization step (which reworks signing pipeline).

---

## 11. Testing & CI

| Layer | Framework | Count | Notes |
|-------|-----------|-------|-------|
| Python service | pytest | 126+ | ML deps mocked via pytest fixtures; <1s to run |
| Rust backend | cargo test | 46 | Unit tests + integration tests for DB/storage |
| Frontend | tsc --noEmit | — | TypeScript type-check |
| Frontend E2E | Not yet built | 0 | Noted technical debt |

**CI commands:**
```bash
cd python-service && uv run pytest
cd src-tauri && cargo check    # or cargo test (46 tests)
npx tsc --noEmit               # or npx vite build
```

---

## 12. Knowledge Graph Internals

### Data pipeline

```
SQLite tables
  ├─ meetings.attendee_names → people nodes (deduped + merged with owners)
  ├─ meetings.tags            → tag nodes (single-use tags dropped)
  └─ action_items.assignee   → owner nodes (merged with person nodes when same name)

Rust: get_meeting_graph
  → Pure build_graph helper (dangling-edge-safe, 500-meeting cap)
  → Returns { nodes: [{id, label, type, count}], edges: [{source, target, relation}] }
```

### Graph model

- **Meeting nodes** — each meeting
- **Person nodes** — attendees (deduped by exact name match)
- **Tag nodes** — colorful per-meeting tags (single-use tags dropped to reduce noise)
- **Owner nodes** — action-item assignees (merged with person nodes when names match)

**Edge types:**
- `meeting ↔ person` (attended by)
- `meeting ↔ tag` (tagged with)
- `person ↔ owner` (same person, filtered) — merged in latest version
- **Generic Speaker-N/Me/Them nodes are filtered out** — they falsely linked meetings via shared-attendee edges

### Rendering

- **cytoscape.js** — graph container, layout, styling, interaction
- **d3-force** — force-directed physics simulation (infinite, never settles; Obsidian-style drag-tug)
- **Physics tuning** (v0.3.14 hotfix): alpha=1.0, alphaDecay=0.02, velocityDecay=0.3 → post-drag wobble 15 px/s → 0 by t=3 s
- **Error boundary** in `useEffect` — catches cytoscape/d3-force initialization failures instead of crashing the entire Graph tab
- **Legend** — toggle node types (meetings/people/tags) on/off

### Fix applied in v0.3.14

The linkId accessor in `cytoscape-d3-force` defaulted to `undefined`, causing a "node not found" crash during initialization. Fixed by providing an explicit `linkId: 'source'` accessor so the force simulation can resolve edge endpoints.

---

## 13. Diarization Internals

### Architecture

```
system.wav ─→ sherpa-onnx OfflineSpeakerDiarization
                ├─ pyannote-segmentation-3.0 (segmentation ONNX model)
                └─ speaker-embedding model (multilingual zh+en)
                │
                Returns: [(start_sec, end_sec, speaker_label), ...]
                │
                ▼
            Overlap merge by time: same-time segments → same label
                │
                ▼
            Speaker 1 / Speaker 2 / ... assigned by first-appearance order
```

### Key parameters

- **Clustering threshold:** 0.7 (tuned up from 0.5 after a 2-person call produced "Speaker 1/2/3" — the extra cluster was a phantom micro-segment)
- **Audio:** System channel only (mic stays "Me")
- **Merge rule:** If two segments overlap in time by >0.3s, they're assigned the same speaker label
- **Models:** Downloaded once to HF cache on first call (~34 MB total; no HuggingFace gating, no auth token needed)
- **Error handling:** `try/except` wrapping the entire pipeline — any failure (model not found, audio too short, ONNX error, OOM) falls back silently to flat "Them"

### Integration

The diarizer is called from `transcriber.py` inside `transcribe_dual()`, after individual channel transcription:
1. Transcribe both WAVs separately → system_segments, mic_segments
2. If `diarize=True`: `speaker_diarize(system_wav)` → labeled system segments
3. `merge_labeled_segments()`: interleave all segments (system + mic) by start_time → ordered dialogue
4. `relabel_me()`: rewrite `Me:` → user's configured name

### Known limitation

Diarization is **anonymous** — it produces "Speaker 1", "Speaker 2", not "Sarah", "Mike". Mapping anonymous labels to real identities is specced but not built (see `docs/SPEC_DIARIZATION.md`).

---

## 14. Export/Import Bundle System

### Bundle schema (v1)

```json
{
  "schema_version": 1,
  "exported_at": "2026-07-02T09:00:00+04:00",
  "meeting": {
    "title": "Q3 Planning",
    "transcript": "Me: Let's start...",
    "transcript_turns": [{"speaker": "Me", "text": "Let's start..."}],
    "summary": "## Key Topics\n...",
    "attendees": ["Alice", "Bob"],
    "tags": [{"label": "Planning", "color": "#3B82F6"}],
    "user_notes": "Remember to mention the budget",
    "action_items": [
      {"text": "Draft the proposal", "assignee": "Alice", "done": false}
    ]
  }
}
```

### Export flow
1. Rust reads meeting + action_items from DB
2. Constructs bundle JSON
3. Native save dialog → writes `*.adversaria.json`

### Import flow
1. Frontend file picker → reads JSON
2. Rust: `insert_bundle_meeting`:
   - Generates new UUID (no ID conflicts)
   - Inserts meeting row with `transcript_turns`, tags, user_notes preserved
   - Inserts action_items with new IDs, preserving `done`/`assignee`/`text`
   - Returns new meeting ID
3. Frontend refreshes → new meeting appears in list

### Backup/Restore
- **Backup-all:** Every meeting + action_items + ask_messages → one JSON array
- **Restore-all:** Federated re-insert with fresh IDs (handles partial failures gracefully)
- **Settings → Data** tab exposes both

---

## 15. Known Technical Debt

From TODO.md and code analysis:

| Issue | Severity | Notes |
|-------|----------|-------|
| No frontend E2E tests | 🟡 | Rust has 46, Python 126, frontend: 0 |
| `commands.rs` at 1193 lines | 🟡 | Oversized file |
| `Settings.tsx` at 1098 lines | 🟡 | Oversized file |
| `NoteViewer.tsx` at 771 lines | 🟡 | Oversized file |
| `storage.rs` at 1078 lines | 🟡 | Oversized file |
| App.tsx has ~18 useState hooks | 🟢 | Manageable for solo dev but worth decomposing |
| No Rust integration tests for audio capture | 🟡 | Storage has tests; capture path does not |
| Kept pending WAVs not encrypted at rest | 🟢 | DB is encrypted; pending audio files are not |
| Windows calendar browser-open truncates OAuth URL | 🔴 | `cmd start` treats `&` as separator — `url` breaks |
| No "LLM server down" friendly UX | 🟠 | Shows raw errno instead of a banner |
| Auto-updater ships ad-hoc-signed → TCC reset | 🔴 | Fix deferred to notarization rework |
| macOS: bundled app can't target Ollama easily | 🟢 | Hardcoded to Rapid-MLX on Apple Silicon |

---

## 16. Architectural Decisions (ADR Index)

All documented in `docs/DECISIONS.md`:

| ADR | Subject | Status |
|-----|---------|--------|
| ADR-018 | Projects reuse workspaces; deletion preserves meetings | Implemented in working tree |
| ADR-017 | Workspace staffing is per-task and fixed at queue time | Implemented in working tree |
| ADR-016 | One managed Ollama engine across platforms | Accepted; migration pending |
| ADR-015 | Collaboration shares derived artifacts, not meeting archives | Accepted; not built |
| ADR-002 | Calendar integration: read-only OAuth, off by default | Implemented (Google + EventKit) |
| ADR-003 | Audio deleted after successful transcription | Implemented + narrowed for data-loss fix |
| ADR-008 | LLM model selection: Qwen 3.6-35B-A3B (benchmark-won) | Implemented |
| ADR-009 | LLM backend abstraction (Ollama / OpenAI-compatible) | Implemented |
| ADR-010 | macOS port: ScreenCaptureKit + cpal, MLX transcription | Implemented |
| ADR-011 | SQLCipher encryption-at-rest | Implemented (+ migrator) |
| ADR-012 | Speaker diarization via sherpa-onnx, system-only | Implemented |
| ADR-013 | User-toggleable encryption, Touch ID unlock | Implemented |
| ADR-014 | Tauri v2 auto-updater, public releases repo | Implemented + round-trip verified |

---

*Written 2026-07-02 · Updated 2026-08-30 for the uncommitted Meeting projects implementation · Companion: [DEEP_DIVE_BUSINESS.md](./DEEP_DIVE_BUSINESS.md)*
