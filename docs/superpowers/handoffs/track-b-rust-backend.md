# Track B Handoff: Tauri Rust Backend

**Scope:** Tasks 6–10 — Config, SQLite storage, HTTP client, WASAPI audio
capture, system tray + hotkeys, IPC command handlers.

**Dependencies satisfied:** Task 1 complete — Rust types in
`src-tauri/src/types.rs`, `Cargo.toml` with all deps, `lib.rs` module map.

**Output:** A Tauri backend that records system audio, manages meeting history
in SQLite, communicates with the Python ML service, and exposes everything
through typed IPC commands.

## Files to create/modify

| File | Purpose |
|------|---------|
| `src-tauri/src/config.rs` | App config (Task 6) |
| `src-tauri/src/storage.rs` | SQLite meeting store (Task 6) |
| `src-tauri/src/http_client.rs` | Typed client for Python service (Task 7) |
| `src-tauri/src/audio/mod.rs` | WASAPI capture module (Task 8) |
| `src-tauri/src/tray.rs` | System tray + global hotkeys (Task 9) |
| `src-tauri/src/commands.rs` | Tauri IPC command handlers (Task 10) |
| `src-tauri/src/lib.rs` | Module wiring (modify — uncomment modules, register commands) |

## Task breakdown

### Task 6: Config + Storage Modules

**`src-tauri/src/config.rs`:**
- Load/save `AppConfig` from a JSON file in the user's app data dir
- Use `directories` crate for platform-appropriate path
- Default config:
  ```
  python_service_url = "http://127.0.0.1:9876"
  default_prompt_template = "general"
  auto_detect_meetings = false
  ollama_model = "llama3.1:8b"
  claude_api_key = null
  ```
- Functions: `load_config() -> AppConfig`, `save_config(&AppConfig)`

**`src-tauri/src/storage.rs`:**
- SQLite DB via `rusqlite` with bundled SQLite
- DB path: app data dir / `meetings.db`
- Table:
  ```sql
  CREATE TABLE meetings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    duration_seconds REAL NOT NULL DEFAULT 0,
    transcript TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    template_used TEXT NOT NULL DEFAULT 'general',
    audio_file_path TEXT
  );
  ```
- Functions: `init_db()`, `insert_meeting(...) -> i64`, `get_meetings() -> Vec<Meeting>`, `get_meeting(id: i64) -> Option<Meeting>`

### Task 7: HTTP Client

**`src-tauri/src/http_client.rs`:**
- Typed `reqwest` client for the Python ML service
- Functions:
  - `check_health() -> Result<HealthResponse>`
  - `transcribe(audio_path: &Path) -> Result<TranscribeResponse>` — multipart upload
  - `summarize(transcript: &str, template: &str) -> Result<SummarizeResponse>`
  - `list_templates() -> Result<Vec<TemplateInfo>>`
- Base URL from config
- Proper error type wrapping reqwest + serde errors

### Task 8: WASAPI Audio Capture

**`src-tauri/src/audio/mod.rs`:**
- Windows loopback audio capture using the `windows` crate
- Capture system audio output (what you hear) via WASAPI
- Output: WAV file, 16-bit PCM, mono 16kHz
- Struct: `AudioCapture { device, format, buffer }`
- Methods: `new()`, `start(path: &Path)`, `stop() -> Result<f64>` (returns duration)
- Audio files saved to temp dir, deleted after transcription

### Task 9: System Tray + Hotkeys

**`src-tauri/src/tray.rs`:**
- System tray icon with menu: Start Recording, Stop Recording, Show Window, Quit
- Global hotkey: Ctrl+Shift+R to toggle recording
- Uses Tauri v2 tray-icon feature and plugin
- Functions: `setup_tray(app: &App)`, `setup_hotkeys(app: &App)`
- Emit events: `recording-started`, `recording-stopped` to frontend

### Task 10: IPC Commands

**`src-tauri/src/commands.rs`:**
- Wire all Tauri command handlers — pure functions that delegate to modules
- Commands (match the TypeScript wrappers in `src/lib/tauri.ts`):
  - `start_recording(state)`
  - `stop_recording(state) -> Result<String>`
  - `transcribe_and_summarize(state, audio_path, template_name) -> Result<...>`
  - `get_meetings(state) -> Result<Vec<Meeting>>`
  - `get_meeting(state, id) -> Result<Meeting>`
  - `get_config(state) -> Result<AppConfig>`
  - `update_config(state, config) -> Result<()>`
  - `check_service_health(state) -> Result<bool>`
- Use Tauri v2 state management
- Register all commands in `lib.rs::run()`

## Execution order

Tasks 6, 7, 8, 9 can run in **any order** (they're independent).
Task 10 depends on all of 6, 7, 8, 9 — must run last.
Commit after each task.

## Module wiring (to update in `lib.rs`)

After each task, uncomment the corresponding `pub mod` line in
`src-tauri/src/lib.rs` and add the trait/commands to the builder.

After Task 10, the `lib.rs` should have all modules uncommented and
all commands registered.

## Self-review checklist (per task)

- [ ] Rust code compiles: `cargo check` in `src-tauri/`
- [ ] No `unwrap()` on fallible operations — use `?` or proper error handling
- [ ] All public functions have doc comments
- [ ] Serde derives on all types that cross IPC boundary
- [ ] Async functions use `tokio` runtime (reqwest calls, file I/O)
- [ ] Audio capture uses safe wrappers around Windows APIs
