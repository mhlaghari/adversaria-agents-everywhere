# SPEC — Full-Fidelity Meeting Export & Import (Bundle + Backup/Restore)

**Status:** Proposed (not implemented). Implementation spec for a human + AI to
build.
**Author:** spec pass, 2026-07-01.
**Scope:** Round-trip a meeting (or all meetings) through a versioned JSON bundle
so meetings can move between laptops or be shared with a teammate. Also spec a
"backup/restore all" path.

> **One-line summary:** Export a meeting to a self-contained `*.adversaria.json`
> bundle carrying the full record (transcript, summary, action items, tags,
> attendees); import it back under a fresh id. Add "backup all" / "restore all"
> for the new-laptop use case.

---

## 1. Goal & non-goals

### Goal
- **Per-meeting export/import:** a user can export one meeting to a file and
  import it on another Adversaria install (their second laptop, or a teammate's)
  with full fidelity.
- **Backup/restore all:** export ALL meetings (and their action items, chat, Ask
  history) to a single bundle so a user moving to a new laptop doesn't lose
  anything.
- **Format:** a versioned JSON bundle (`*.adversaria.json`) — not plain `.md`
  (Markdown is lossy: it drops tags, action-item state, structured transcript
  turns, and attendees).

### Non-goals (this spec)
- **No encryption at the bundle level in v1.** The bundle is plaintext JSON.
  Passphrase-encrypt is a future add (§6).
- **No cloud sync or sharing service.** This is file-based export/import only.
- **No partial/delta backup.** Full snapshot only.
- **No conflict-resolution merge logic.** Import creates a new row; if the user
  imports a meeting they already have, it's a duplicate.

### Success criteria
1. Export a meeting → the `.json` file contains `schema_version`, `title`,
   `recorded_at`, `duration_seconds`, `language`, `template_used`, `transcript`,
   `transcript_turns`, `summary`, `attendees`, `tags`, `action_items[]` (with
   `text`, `assignee`, `done`, `due`, `ord`).
2. Import the bundle into a fresh state → a new meeting appears with the same
   transcript, summary, action items, tags, and attendees. The `id` is fresh.
3. "Backup all" → a single `.zip` (or `.json` array) holding every meeting +
   action items. "Restore all" → imports them all.
4. `cargo check` + `npx tsc --noEmit` + `uv run pytest` pass.
5. A round-trip test: insert a meeting → export → delete → import → verify
   fields match.

---

## 2. Bundle format

### 2a. Per-meeting bundle (`meeting-<title>.adversaria.json`)

A single JSON object:

```jsonc
{
  "schema_version": 1,
  "exported_at": "2026-07-01T12:00:00Z",
  "app_version": "1.2.3",
  "meeting": {
    "title": "Q3 Planning with Sarah",
    "recorded_at": "2026-06-28T14:00:00Z",
    "duration_seconds": 1847.5,
    "template_used": "client-meeting",
    "transcript": "Me: Let's talk about Q3 priorities.\nThem: I think we should focus on...",
    "transcript_turns": [
      {"speaker": "Me", "text": "Let's talk about Q3 priorities."},
      {"speaker": "Them", "text": "I think we should focus on..."}
    ],
    "summary": "**Key Topics Discussed**\n\n- Q3 roadmap priorities...",
    "attendees": ["Sarah Chen — sarah@acme.com"],
    "tags": [
      {"label": "Client Meeting", "color": "blue"}
    ],
    "action_items": [
      {"ord": 0, "text": "Draft Q3 roadmap by Friday", "assignee": "Hamza", "due": "2026-07-04", "done": false},
      {"ord": 1, "text": "Share budget spreadsheet", "assignee": "Sarah", "due": "", "done": true}
    ]
  }
}
```

**Field notes:**
- `id` is **not** exported — imports get a fresh id (federated model).
- `audio_file_path` is **not** exported — it's a local path to a deleted WAV.
- `user_notes` is exported (it's the user's own typed notes). Added to the
  schema.
- `pinned` and `locked` are **not** exported — these are per-install UI state.
- `language` is the detected transcript language (from `TranscribeResponse.language`).
  The meeting struct doesn't store it today — it's only in the transcribe
  response. **Decision:** add a `language` field to the `meetings` table (migration,
  `#[serde(default)]`) or store it in the export only. For v1, include it in the
  export from the Rust command (which has the transcribe response in hand).

### 2b. Backup-all bundle (`adversaria-backup-<date>.json` or `.zip`)

Two options; **recommend JSON array for v1** (simpler, no zip dep):

```jsonc
{
  "schema_version": 1,
  "exported_at": "2026-07-01T12:00:00Z",
  "app_version": "1.2.3",
  "type": "full_backup",
  "meetings": [ /* ...per-meeting objects as above... */ ],
  "ask_conversation": [
    {"role": "user", "content": "What are my action items?", "sources": [], "intent": ""},
    {"role": "assistant", "content": "You have 3 open to-dos...", "sources": [...], "intent": "todos"}
  ]
}
```

`ask_conversation` is optional (empty array if none).

**Future:** `.zip` containing the JSON + linked media (if we ever attach files
to meetings). Not needed for v1.

### 2c. Schema version handling

- `schema_version` is an integer starting at `1`.
- **Forward-compatible:** import ignores unknown top-level keys.
- **Backward-compatible:** import fills missing optional fields with defaults
  (empty strings, empty arrays, `false`).
- **Breaking change:** bump `schema_version` to `2`. The importer checks the
  version and rejects versions it doesn't know with a clear message: "This
  bundle requires a newer version of Adversaria (schema v2; this version
  supports v1)."

---

## 3. Rust commands

All new commands go in `src-tauri/src/commands.rs`, registered in `lib.rs`.

### 3a. Per-meeting export

```rust
/// Export a meeting as a self-contained JSON bundle. Opens a native save dialog
/// (reusing the rfd pattern from `export_summary`/`export_html`). Returns the
/// saved path or None if the user cancelled.
#[tauri::command]
pub async fn export_meeting_bundle(id: i64) -> Result<Option<String>, String> {
    let meeting = crate::storage::get_meeting(id)
        .map_err(|e| format!("Failed to load meeting: {e}"))?
        .ok_or_else(|| format!("Meeting not found: {id}"))?;

    let action_items = crate::storage::get_action_items(Some(id))
        .map_err(|e| format!("Failed to load action items: {e}"))?;

    let bundle = serde_json::json!({
        "schema_version": 1,
        "exported_at": chrono::Utc::now().to_rfc3339(),
        "app_version": env!("CARGO_PKG_VERSION"),
        "meeting": {
            "title": meeting.title,
            "recorded_at": meeting.recorded_at,
            "duration_seconds": meeting.duration_seconds,
            "template_used": meeting.template_used,
            "transcript": meeting.transcript,
            "transcript_turns": meeting.transcript_turns,
            "summary": meeting.summary,
            "attendees": meeting.attendees,
            "user_notes": meeting.user_notes,
            "tags": meeting.tags,
            "action_items": action_items.iter().map(|a| serde_json::json!({
                "ord": a.ord,
                "text": a.text,
                "assignee": a.assignee,
                "due": a.due,
                "done": a.done,
            })).collect::<Vec<_>>(),
        }
    });

    let contents = serde_json::to_string_pretty(&bundle)
        .map_err(|e| format!("Failed to serialize bundle: {e}"))?;

    let safe_name = meeting.title
        .chars()
        .map(|c| if c.is_alphanumeric() || c == '-' || c == '_' { c } else { '_' })
        .collect::<String>();
    let default_name = format!("meeting-{}.adversaria.json", safe_name);

    let path = tokio::task::spawn_blocking(move || {
        rfd::FileDialog::new()
            .set_file_name(&default_name)
            .add_filter("Adversaria Bundle", &["json"])
            .save_file()
    })
    .await
    .map_err(|e| format!("File dialog failed: {e}"))?;

    match path {
        Some(p) => {
            std::fs::write(&p, contents)
                .map_err(|e| format!("Failed to write bundle: {e}"))?;
            Ok(Some(p.to_string_lossy().into_owned()))
        }
        None => Ok(None),
    }
}
```

### 3b. Per-meeting import

```rust
/// Import a meeting from an Adversaria JSON bundle. Opens a native file picker,
/// parses the bundle, inserts a new meeting + action items under a fresh id,
/// and returns the new Meeting. Rejects unknown schema versions.
#[tauri::command]
pub async fn import_meeting_bundle() -> Result<Option<Meeting>, String> {
    let path = tokio::task::spawn_blocking(|| {
        rfd::FileDialog::new()
            .add_filter("Adversaria Bundle", &["json"])
            .pick_file()
    })
    .await
    .map_err(|e| format!("File dialog failed: {e}"))?;

    let path = match path {
        Some(p) => p,
        None => return Ok(None),
    };

    let raw = std::fs::read_to_string(&path)
        .map_err(|e| format!("Failed to read bundle: {e}"))?;

    let bundle: serde_json::Value = serde_json::from_str(&raw)
        .map_err(|e| format!("Invalid JSON bundle: {e}"))?;

    let schema_version = bundle.get("schema_version")
        .and_then(|v| v.as_i64())
        .unwrap_or(0);
    if schema_version < 1 || schema_version > 1 {
        return Err(format!(
            "Unsupported bundle schema version {schema_version}. This version of Adversaria supports schema v1."
        ));
    }

    let m = bundle.get("meeting")
        .ok_or_else(|| "Bundle is missing the 'meeting' key.".to_string())?;

    // Build the meeting record (id=0 → auto-assigned).
    let meeting = Meeting {
        id: 0,
        title: string_field(m, "title")?,
        recorded_at: string_field(m, "recorded_at")?,
        duration_seconds: m.get("duration_seconds").and_then(|v| v.as_f64()).unwrap_or(0.0),
        transcript: string_field_or(m, "transcript", ""),
        summary: string_field_or(m, "summary", ""),
        template_used: string_field_or(m, "template_used", "general"),
        audio_file_path: None,
        attendees: string_array(m, "attendees"),
        user_notes: string_field_or(m, "user_notes", ""),
        tags: parse_tags(m),
        pinned: false,
        locked: false,
        transcript_turns: parse_transcript_turns_bundle(m),
    };

    let new_id = crate::storage::insert_meeting(&meeting)
        .map_err(|e| format!("Failed to save imported meeting: {e}"))?;

    // Import action items.
    if let Some(items) = m.get("action_items").and_then(|v| v.as_array()) {
        let conn = crate::storage::connect_for_sync()
            .map_err(|e| e.to_string())?;
        for item in items {
            let ord = item.get("ord").and_then(|v| v.as_i64()).unwrap_or(0);
            let text = item.get("text").and_then(|v| v.as_str()).unwrap_or("").to_string();
            let assignee = item.get("assignee").and_then(|v| v.as_str()).unwrap_or("").to_string();
            let due = item.get("due").and_then(|v| v.as_str()).unwrap_or("").to_string();
            let done = item.get("done").and_then(|v| v.as_bool()).unwrap_or(false);
            conn.execute(
                "INSERT INTO action_items (meeting_id, ord, text, assignee, due, done)
                 VALUES (?1, ?2, ?3, ?4, ?5, ?6)",
                rusqlite::params![new_id, ord, text, assignee, due, done as i32],
            ).map_err(|e| format!("Failed to insert action item: {e}"))?;
        }
    }

    crate::storage::get_meeting(new_id)
        .map_err(|e| format!("Failed to reload imported meeting: {e}"))?
        .ok_or_else(|| "Meeting not found after import.".to_string())
}
```

Helper functions (add to `commands.rs`):

```rust
fn string_field(obj: &serde_json::Value, key: &str) -> Result<String, String> {
    obj.get(key)
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| format!("Bundle missing required field: {key}"))
}

fn string_field_or(obj: &serde_json::Value, key: &str, default: &str) -> String {
    obj.get(key)
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .unwrap_or_else(|| default.to_string())
}

fn string_array(obj: &serde_json::Value, key: &str) -> Vec<String> {
    obj.get(key)
        .and_then(|v| v.as_array())
        .map(|a| a.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_default()
}

fn parse_tags(obj: &serde_json::Value) -> Vec<crate::types::Tag> {
    obj.get("tags")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|v| {
                    Some(crate::types::Tag {
                        label: v.get("label")?.as_str()?.to_string(),
                        color: v.get("color")?.as_str()?.to_string(),
                    })
                })
                .collect()
        })
        .unwrap_or_default()
}

fn parse_transcript_turns_bundle(obj: &serde_json::Value) -> Vec<crate::types::TranscriptTurn> {
    obj.get("transcript_turns")
        .and_then(|v| v.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|v| {
                    Some(crate::types::TranscriptTurn {
                        speaker: v.get("speaker")?.as_str()?.to_string(),
                        text: v.get("text")?.as_str()?.to_string(),
                    })
                })
                .collect()
        })
        .unwrap_or_default()
}
```

### 3c. Backup all / restore all

```rust
/// Export ALL meetings + action items + Ask conversation to a single JSON file.
#[tauri::command]
pub async fn export_all_meetings() -> Result<Option<String>, String> { /* ... */ }

/// Import all meetings from a backup bundle. Each meeting gets a fresh id.
/// Returns the count of imported meetings.
#[tauri::command]
pub async fn import_all_meetings() -> Result<Option<usize>, String> { /* ... */ }
```

The backup-all format is an array of per-meeting bundles (same shape as §2a)
under a single top-level object. The restore-all iterates and inserts each
meeting.

---

## 4. Frontend

### 4a. `src/lib/tauri.ts` — typed wrappers

```ts
/** Export a meeting to a self-contained .adversaria.json bundle via save dialog. */
export function exportMeetingBundle(id: number): Promise<string | null> {
  return invoke("export_meeting_bundle", { id });
}

/** Import a meeting from a .adversaria.json bundle via file picker. */
export function importMeetingBundle(): Promise<Meeting | null> {
  return invoke("import_meeting_bundle");
}

/** Backup all meetings + action items + Ask history to a single bundle. */
export function exportAllMeetings(): Promise<string | null> {
  return invoke("export_all_meetings");
}

/** Restore all meetings from a backup bundle. Returns the count imported. */
export function importAllMeetings(): Promise<number | null> {
  return invoke("import_all_meetings");
}
```

### 4b. `src/components/NoteViewer.tsx` — Export ▾ menu

Add two new menu items to the existing Export ▾ dropdown (after the "Export
Markdown…" entry at line 800):

```tsx
<button
  className="settings-menu-item"
  role="menuitem"
  onClick={() => {
    setExportMenuOpen(false);
    handleExportBundle();
  }}
>
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7,10 12,15 17,10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
  Export bundle (.json)…
</button>
```

Where `handleExportBundle`:
```ts
const handleExportBundle = async () => {
  try {
    const path = await exportMeetingBundle(meeting.id);
    if (path) {
      setExportMsg(`Saved to ${path}`);
      setTimeout(() => setExportMsg(null), 4000);
    }
  } catch (e) {
    setExportMsg(String(e));
  }
};
```

### 4c. Import entry point — Settings or sidebar

**Recommendation:** add "Import meeting…" to the **Settings** view (a new
"Data" section alongside "Appearance" and "Calendar"), and a "Backup all…" /
"Restore all…" pair. This keeps the sidebar clean and the import action rare
enough that it doesn't need to be always visible.

Alternatively, add "Import meeting…" as a small button in the MeetingsList
sidebar header alongside `NewNoteButton` (the same spot as the audio import
button from SPEC_AUDIO_IMPORT). Both can coexist.

---

## 5. Privacy consideration: plaintext bundle

**The exported bundle is plaintext JSON.** Unlike the SQLite DB (which is
SQLCipher-encrypted at rest via `storage.rs:23-31`), the export file has no
encryption.

**Call this out in the UI** with a short note before the save dialog or in the
export menu item's tooltip: "The exported file is plaintext — anyone who can
read the file can read your meeting notes."

**Future:** optionally encrypt the bundle with a user-supplied passphrase
(AES-256-GCM, PBKDF2 key derivation). Spec this as a future enhancement, not v1.
The `schema_version` field makes it forward-compatible: v2 could add an
`encryption` block with `{"algorithm": "aes-256-gcm", "kdf": "pbkdf2-sha256",
"salt": "...", "nonce": "..."}`.

---

## 6. Deduplication

Importing a meeting that already exists creates a **duplicate** (fresh id). This
is the correct default — the user may want two copies, or may be importing into
a different install.

**Optional enhancement (not v1):** a "skip duplicates" checkbox that computes a
content hash of `(recorded_at, title, transcript[0:200])` and skips the insert
if a matching meeting exists. The simple approach is good enough for v1.

---

## 7. Edge cases

| # | Edge case | Handling |
|---|-----------|----------|
| 1 | **Schema version mismatch** | Importer rejects unknown versions with a clear message. v1 import only accepts v1. v2 (future) can accept v1 with migration. |
| 2 | **Missing optional fields** | `#[serde(default)]`-style per-field fallback: empty strings for text fields, empty arrays for lists, `false` for booleans. |
| 3 | **Large transcript** (multi-MB JSON) | The entire bundle is loaded into memory for parsing. A 2-hour transcript is ~100-200 KB of text — well within bounds. If transcripts ever exceed ~100 MB, switch to a streaming parser; not needed now. |
| 4 | **Import fails mid-way** (e.g. action items inserted but meeting fails) | The meeting insert and action-item inserts should be in a SQLite transaction so it's atomic. `storage.rs` doesn't yet expose a transaction wrapper — add one or use `conn.execute_batch("BEGIN; ...; COMMIT;")`. |
| 5 | **Importing a bundle with no action items** | The `action_items` key is optional in the import; omit or empty array → no action items created. |
| 6 | **File dialog cancelled** | Returns `None` from the Rust command; frontend does nothing. |
| 7 | **Non-JSON file selected** | `serde_json::from_str` fails → clear error message "The selected file is not a valid Adversaria bundle." |
| 8 | **Backup-all with 500+ meetings** | The JSON array could be tens of MB. Acceptable for a one-time backup. Future: stream to file or use a `.zip` to compress. |
| 9 | **Exporting a meeting with no transcript (pending)** | Export as-is — the `transcript` field will be empty. The importer handles this (empty string is valid). |
| 10 | **Arabic / RTL content** | JSON handles Unicode natively. No special handling needed. |

---

## 8. Phasing

**Phase 1 — Per-meeting export/import (the goal).**
- Rust: `export_meeting_bundle`, `import_meeting_bundle`, helper functions.
- `http_client.rs`: no changes needed (export/import doesn't touch the Python service).
- Frontend: "Export bundle (.json)" in Export ▾ menu; "Import meeting…" in Settings or MeetingsList.
- Test: round-trip test (insert → export → delete → import → assert).

**Phase 2 — Backup all / restore all.**
- Rust: `export_all_meetings`, `import_all_meetings`.
- Frontend: "Backup all…" / "Restore all…" in Settings.

**Phase 3 (future) — Passphrase encryption.**
- Add encryption to the bundle format (schema v2).
- UI: password prompt before export/import.

---

## 9. Verification commands

```bash
# Rust
cd src-tauri && cargo check

# Frontend
npx tsc --noEmit

# Python (no changes, but ensure existing tests still pass)
cd python-service && uv run pytest

# Run a round-trip test (add to src-tauri/src/commands.rs tests):
# #[test]
# fn export_import_roundtrip() { ... }
```

---

## 10. Docs to update when implementing

- `docs/ARCHITECTURE.md` — the export/import data flow (Rust-only; no Python changes).
- `docs/HANDOFF.md` — note the new Export menu items and Settings entries.
- `docs/TODO.md` — move export/import from planned to phased tasks.
