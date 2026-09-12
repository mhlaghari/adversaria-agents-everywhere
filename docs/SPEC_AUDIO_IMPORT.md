# SPEC — Audio File Import (iPhone Voice Memos, .m4a/.mp3/.wav)

**Status:** ✅ Implemented 2026-07-01 (via delegated worker; verified `cargo check`
+ `tsc` + `pytest` green). Not yet re-frozen into the installed app.
**Author:** spec pass, 2026-07-01.
**Scope:** Let the user import a local audio file (`.m4a`, `.mp3`, `.wav`) —
e.g. an iPhone Voice Memo from an in-person meeting — and feed it through
Adversaria's existing transcribe→summarize pipeline to create a meeting. This is
the #1 next feature.

> **One-line summary:** Add an audio file import path that reuses the existing
> transcribe→summarize pipeline with in-process PyAV decode, producing a meeting
> from a dropped/selected audio file. Single track (no "Me"/"Them" split);
> optional diarization as a follow-on toggle.

---

## 1. Goal & non-goals

### Goal
- Let the user pick (or drag-and-drop) a local audio file — `.m4a` (AAC, incl.
  iPhone Voice Memos), `.mp3`, and `.wav` — and have Adversaria run its existing
  transcribe→summarize pipeline on it to create a fully-formed meeting.
- The imported file is decoded to 16 kHz mono via the **in-process PyAV decoder
  already present** in `transcriber.py` (`_decode_to_mono16k`, line 191) — no
  system `ffmpeg` shell-out.
- The pipeline reuses `transcribe_meeting`'s flow (transcribe → summarize →
  derive title → insert meeting → sync action items → delete audio). An imported
  file is a new *source* feeding the same pipeline.

### Non-goals (this spec)
- **No multi-track import.** An imported file is one channel (no "Me"/"Them"
  split). The dual-capture merge is for live recordings only.
- **No diarization in v1.** Optional sherpa-onnx diarization on the single track
  to split "Speaker 1/2/…" is spec'd as a follow-on toggle in Settings (§6) but
  not required for v1.
- **No cloud-upload path for imports.** The import path is local-only (on-device
  Whisper). Cloud transcription (Groq BYOK) is already available via config;
  extending it to imports is a separate toggle.
- **No batch import.** One file at a time.

### Success criteria
1. User picks an `.m4a` iPhone Voice Memo → a new meeting appears with a
   transcript, structured summary, and extracted action items.
2. `.mp3` and `.wav` inputs work identically.
3. Decode failures surface a clear error (no silent data loss).
4. `cargo check` + `npx tsc --noEmit` + `uv run pytest` all pass.
5. New Python logic has a mocked test for the import path.

---

## 2. Approach

### 2a. Architecture decision: extend `/transcribe`, not add a new endpoint

**Decision: add a `single_file` boolean to `TranscribeRequest`** (default
`false`, back-compat). When `true`, the server skips the dual-channel merge and
runs single-track transcription on the file. The Rust side decodes the import
file to 16 kHz mono WAV, writes it to a temp file, and calls `/transcribe` with
`single_file=true` and `mic_audio_path=None`.

**Why not a new `/transcribe_file` endpoint:**
- The same transcriber logic (model selection, language detection, chunking
  for long files) works for both paths. A new endpoint duplicates the request
  path (`server.py:209-268`) for a one-field difference.
- `single_file` is additive — existing callers never set it, so behavior is
  byte-identical to today.
- The `TranscribeResponse` shape is the same: `{text, language, duration_seconds}`.

### 2b. Decoding: reuse PyAV in-process

`transcriber.py` already bundles PyAV (`import av`) and a working
`_decode_to_mono16k(path)` at line 191 — written for the Groq cloud upload path
to decode 48 kHz stereo 32-bit-float WAVs to 16 kHz mono int16. That function
works for **any format PyAV can open**, including `.m4a`/AAC and `.mp3`. It
returns a numpy array ready for Whisper, or `np.zeros(0)` on failure.

The import path reuses it directly:
1. Rust reads the imported file path, passes it to `/transcribe` with
   `single_file=true`.
2. The Python service's single-track handler calls `_decode_to_mono16k(path)`
   → 16 kHz mono samples → feeds them to Whisper (as a numpy array or via a
   temp 16 kHz WAV, whichever the platform transcriber's single-track path
   expects).

No new dependency. No `ffmpeg` on PATH. No shell-out.

### 2c. Single-track transcription

When `single_file=true` and `mic_audio_path` is `None`, the server calls
`_transcriber.transcribe(audio_path)` (the existing single-track path at
`server.py:261`), after decoding the input file to a 16 kHz mono WAV in a temp
directory. The returned transcript has **no speaker labels** — plain text, one
paragraph per segment.

**Optionally**, if diarization is enabled (`diarize=true` in the request) AND
the feature is configured on the service, the single track can be diarized by
the existing `diarize_system_labels()` path (transcriber.py:139) — which already
runs sherpa-onnx on any audio path. Spec this as a **future toggle** (§6); v1
ships without it.

### 2d. Where the code goes (layer by layer)

| Layer | File | Change |
|-------|------|--------|
| **Frontend** | `src/types.ts` | No new types needed (reuses `TranscribeResponse`, `Meeting`). |
| **Frontend** | `src/lib/tauri.ts` | Add `importAudio(filePath: string, template?: string): Promise<Meeting>`. |
| **Frontend** | `src/components/MeetingsList.tsx` | Add "Import audio…" button in the sidebar header (near `NewNoteButton`). |
| **Frontend** | `src/App.tsx` | Wire the import result into the meeting list + select it. |
| **Rust** | `src-tauri/src/commands.rs` | New `import_audio(file_path, template)` command. |
| **Rust** | `src-tauri/src/lib.rs` | Register `import_audio` in `generate_handler!`. |
| **Python** | `python-service/src/models.py` | Add `single_file: bool = False` to `TranscribeRequest`. |
| **Python** | `python-service/src/server.py` | Branch in `/transcribe`: when `single_file=true`, decode import file → temp 16 kHz WAV → single-track transcribe. |
| **Python** | `python-service/src/transcriber.py` | Expose `_decode_to_mono16k` as a public `decode_import_file(path) → Path` helper (creates temp 16 kHz WAV, used by server). |
| **Python** | `python-service/tests/` | New mocked test: import `.m4a` decode → single-track transcribe → response. |

---

## 3. Rust command: `import_audio`

```rust
/// Import a local audio file (.m4a/.mp3/.wav), transcribe it as a single track,
/// summarize with the given template, and return the new Meeting. The imported
/// file is copied to the recordings directory, transcribed, and deleted after
/// a successful transcription (same privacy guarantee as live recordings).
#[tauri::command]
pub async fn import_audio(
    state: State<'_, AppState>,
    file_path: String,
    template: Option<String>,
) -> Result<Meeting, String> {
    // 1. Validate: the file exists and has an allowed extension.
    let src = std::path::Path::new(&file_path);
    if !src.exists() {
        return Err(format!("File not found: {file_path}"));
    }
    let ext = src.extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();
    if !matches!(ext.as_str(), "m4a" | "mp3" | "wav") {
        return Err(format!(
            "Unsupported format: .{ext}. Supported: .m4a, .mp3, .wav"
        ));
    }

    // 2. Copy the file to the recordings directory (so the transcriber finds it
    //    at a stable path, and cleanup_deletes it on success).
    let dir = crate::config::recordings_dir()
        .map_err(|e| format!("Could not prepare recordings directory: {e}"))?;
    let stem = src.file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("import");
    let dest = dir.join(format!("import_{}_{}.{}", stem, chrono::Utc::now().timestamp(), ext));
    std::fs::copy(src, &dest)
        .map_err(|e| format!("Failed to copy audio file: {e}"))?;
    let dest_path = dest.to_string_lossy().to_string();

    // 3. Transcribe as single track.
    let template = template.unwrap_or_else(|| "general".to_string());
    let transcribe_resp = state.client.transcribe_import(&dest_path).await?;

    // 4. Summarize.
    let model = configured_model();
    let language = configured_language();
    let llm_base_url = configured_llm_base_url();
    let llm_api_key = configured_llm_api_key();
    let summarize_resp = state.client.summarize(
        &transcribe_resp.text,
        &template,
        model.as_deref(),
        language.as_deref(),
        None,
        llm_base_url.as_deref(),
        llm_api_key.as_deref(),
        None,
    ).await?;

    // 5. Build + persist the meeting.
    let title = meeting_title(&summarize_resp);
    let transcript_text = transcribe_resp.text.clone();
    let meeting = Meeting {
        id: 0,
        title,
        recorded_at: chrono::Utc::now().to_rfc3339(),
        duration_seconds: transcribe_resp.duration_seconds,
        transcript: transcript_text.clone(),
        summary: summarize_resp.summary,
        template_used: summarize_resp.template_used,
        audio_file_path: None,
        attendees: summarize_resp.attendees,
        user_notes: String::new(),
        tags: category_tag(&summarize_resp.category).into_iter().collect(),
        pinned: false,
        locked: false,
        transcript_turns: crate::storage::parse_transcript_turns(&transcript_text),
    };
    let new_id = crate::storage::insert_meeting(&meeting)
        .map_err(|e| format!("Failed to save meeting: {e}"))?;
    sync_actions_for_meeting(new_id, &meeting.summary);

    // 6. Success — delete the copied audio (privacy).
    cleanup_recordings(&dest_path, None);

    Ok(Meeting { id: new_id, ..meeting })
}
```

### 3a. New HTTP client method: `transcribe_import`

Add to `src-tauri/src/http_client.rs`:

```rust
/// Transcribe a single-track import file (no mic, no dual merge). The Python
/// service decodes the file in-process and runs plain single-track Whisper.
pub async fn transcribe_import(&self, audio_path: &str) -> Result<TranscribeResponse, String> {
    #[derive(serde::Serialize)]
    struct Req {
        audio_path: String,
        single_file: bool,
    }
    let base_url = self.base_url.read().unwrap().clone();
    let resp = self.client
        .post(format!("{}/transcribe", base_url))
        .json(&Req { audio_path: audio_path.to_string(), single_file: true })
        .send().await
        .map_err(|e| format!("Transcribe request failed: {e}"))?;
    if !resp.status().is_success() {
        let body = resp.text().await.unwrap_or_default();
        return Err(format!("Transcription failed: {body}"));
    }
    resp.json::<TranscribeResponse>().await
        .map_err(|e| format!("Failed to parse transcribe response: {e}"))
}
```

---

## 4. Python changes

### 4a. `models.py` — add `single_file` field

```python
class TranscribeRequest(BaseModel):
    # … existing fields unchanged …
    single_file: bool = Field(
        default=False,
        description=(
            "When true, treat audio_path as a single-track import file (no mic, "
            "no dual merge). The file is decoded to 16 kHz mono in-process via "
            "PyAV before transcription."
        ),
    )
```

### 4b. `transcriber.py` — expose `decode_import_file`

```python
def decode_import_file(path: str) -> Path:
    """Decode any audio file (m4a/mp3/wav) to a temporary 16 kHz mono WAV.

    Uses the in-process PyAV decoder (no system ffmpeg). Returns the path to
    the temp WAV, which the caller must delete after use. Raises ValueError on
    decode failure.
    """
    samples = _decode_to_mono16k(path)
    if samples.size == 0:
        raise ValueError(f"Could not decode audio from {path} — file may be "
                         f"corrupted or in an unsupported codec.")
    import wave
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_CLOUD_TARGET_RATE)
        w.writeframes(samples.tobytes())
    return Path(tmp.name)
```

### 4c. `server.py` — branch in `/transcribe`

In the existing `/transcribe` handler (line 209), after the `audio_path` check
and before the cloud-transcription block, add:

```python
# Single-file import path: decode in-process, then transcribe as plain single-track.
if request.single_file:
    try:
        tmp_wav = decode_import_file(request.audio_path)
        try:
            result = _transcriber.transcribe(str(tmp_wav))
            return result
        finally:
            tmp_wav.unlink(missing_ok=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Import transcription failed")
        raise HTTPException(
            status_code=500, detail=f"Transcription failed: {exc}"
        ) from exc
```

---

## 5. Frontend

### 5a. `src/lib/tauri.ts` — typed wrapper

```ts
/** Import a local audio file (.m4a/.mp3/.wav), transcribe as single track,
 *  summarize, and return the new Meeting. */
export function importAudio(
  filePath: string,
  template?: string,
): Promise<Meeting> {
  return invoke("import_audio", {
    filePath,
    template: template ?? null,
  });
}
```

### 5b. `src/components/MeetingsList.tsx` — "Import audio…" button

Add an "Import audio…" button in the sidebar header, alongside the existing
`NewNoteButton` component. The button opens a native file dialog (via the
`rfd` crate — already a dependency, used by `export_summary`/`export_html`):

```rust
// New Rust command to open a file picker (invoked from the frontend):
#[tauri::command]
pub async fn pick_audio_file() -> Result<Option<String>, String> {
    let path = tokio::task::spawn_blocking(|| {
        rfd::FileDialog::new()
            .add_filter("Audio", &["m4a", "mp3", "wav"])
            .pick_file()
    }).await
    .map_err(|e| format!("File dialog failed: {e}"))?;
    Ok(path.map(|p| p.to_string_lossy().into_owned()))
}
```

The button:
```tsx
<button className="btn-secondary" onClick={async () => {
  const path = await pickAudioFile();
  if (!path) return;
  try {
    const meeting = await importAudio(path);
    onSelect(meeting); // open the new meeting
  } catch (e) {
    // surface error in an ErrorBanner
  }
}}>
  Import audio…
</button>
```

### 5c. No drag-and-drop in v1

Drag-and-drop on the Tauri webview requires additional IPC plumbing (the webview
receives file paths differently). The native file dialog is the simpler, working
first step. Note drag-and-drop as a possible enhancement.

---

## 6. File handling / privacy decision

**Decision: delete the imported file after successful transcription** — same
guarantee as live recordings (`cleanup_recordings` at `commands.rs:441`).

**Reasoning:**
- The user already has the original file (on their phone, in their filesystem).
  We copy it to the recordings directory for processing; once transcribed, the
  copy has served its purpose.
- Keeping it would be a new persistent-audio path, which is a privacy regression
  (the product's core promise is "audio deleted after transcription").
- The one exception — keeping audio for pending/retry — already exists for live
  recordings (`save_pending_meeting`, `commands.rs:375`). If transcription
  fails, the import copy is kept (same pattern: `enqueue_recording`-style retry
  via `transcribe_meeting`).

**Concretely:** the import flow copies the file to the recordings dir, runs the
pipeline, and calls `cleanup_recordings()` on success. On failure, the copy
stays and the meeting is saved as "pending" (with `audio_file_path` set) so the
user can retry.

---

## 7. Edge cases

| # | Edge case | Handling |
|---|-----------|----------|
| 1 | **AAC/.m4a decode failure** (corrupted file, unsupported codec variant) | PyAV raises; `decode_import_file` catches and re-raises `ValueError`. The Rust command returns the error string — the file is NOT deleted (the original is untouched; our copy in recordings can be cleaned up). |
| 2 | **Very long recording** (2+ hour Voice Memo) | Reuse the existing chunking logic: on faster-whisper, `transcribe()` processes in 30s chunks; on MLX, the model handles long audio natively. The import path writes a temp 16 kHz WAV → feeds the platform transcriber's single-track path — no new chunking logic needed. |
| 3 | **Mono file, no diarization** | The single-track transcript has no speaker labels — just plain paragraphs. This is the expected v1 behavior. A note in the UI: "Imported audio is transcribed as a single speaker. Enable speaker separation in Settings to split multiple speakers." |
| 4 | **Very quiet / far-field phone audio** | Whisper accuracy drops on far-field audio. Set expectations in the UI: a tooltip or helper text "Best results with close-range recordings. Far-field audio may have lower accuracy." No code change — the model is what it is. |
| 5 | **File with no detectable speech** | Whisper may hallucinate on silent audio (a known limitation, mitigated in the existing transcriber). The import path inherits the same behavior. If the transcript is empty or near-empty, the summarizer produces a sparse result — let it through; the user can delete the meeting. |
| 6 | **Non-ASCII filename** | `rfd` returns a native path; Rust handles UTF-8/Unicode paths natively on macOS and Windows. PyAV opens by path via ffmpeg libraries, which handle Unicode paths. |
| 7 | **Concurrent import during a live recording** | The existing background queue serializes transcription (concurrency 1). The import runs inline (blocking), so it queues behind any in-progress transcription. This is acceptable — import is an infrequent user action. |
| 8 | **User imports a .wav that is already 16 kHz mono** | `_decode_to_mono16k` handles this gracefully — PyAV detects the input format and the resampler is a no-op when rates match. |

---

## 8. Verification commands

```bash
# Rust compiles
cd src-tauri && cargo check

# Frontend types
npx tsc --noEmit

# Python tests (existing + new import test)
cd python-service && uv run pytest

# New test (mocked) — add to python-service/tests/:
# test_import_decode_m4a: mock PyAV decode → verify TranscribeResponse
```

### Manual verification checklist
1. Import a real iPhone Voice Memo `.m4a` → meeting created with transcript.
2. Import an `.mp3` podcast clip → meeting created.
3. Import a `.wav` file → meeting created.
4. Import a corrupted/unsupported file → clear error message, no crash.
5. Check that the temp import file is deleted from the recordings dir after success.
6. Check that on failure, a "Needs transcription" pending meeting is created.

---

## 9. Docs to update when implementing

- `docs/ARCHITECTURE.md` — the import data flow (Rust → Python single-track path).
- `docs/HANDOFF.md` — runbook: note the import button location and the PyAV decode.
- `docs/LESSONS_LEARNED.md` — whatever surprises PyAV throws for unusual codecs.
- `docs/TODO.md` — move "audio import" from planned to in-progress/done.
