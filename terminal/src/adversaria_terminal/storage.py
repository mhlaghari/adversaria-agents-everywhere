"""Local SQLite history for the terminal client.

The desktop app encrypts its DB with SQLCipher; the terminal keeps a plain,
terminal-local SQLite store (clearly separate table names) so it runs with
zero native dependencies. Nothing here ever touches the desktop's DB.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import ActionItem, Meeting, now_iso

_SCHEMA = """
CREATE TABLE IF NOT EXISTS meetings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL DEFAULT '',
    summary          TEXT NOT NULL DEFAULT '',
    transcript       TEXT NOT NULL DEFAULT '',
    language         TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    template_used    TEXT NOT NULL DEFAULT '',
    category         TEXT NOT NULL DEFAULT '',
    attendees        TEXT NOT NULL DEFAULT '[]',
    source           TEXT NOT NULL DEFAULT 'recorded',
    status           TEXT NOT NULL DEFAULT 'pending',
    audio_path       TEXT,
    mic_path         TEXT,
    recorded_at      TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS action_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_id  INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    text        TEXT NOT NULL DEFAULT '',
    done        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_meetings_recorded ON meetings(recorded_at);
CREATE INDEX IF NOT EXISTS idx_action_meeting ON action_items(meeting_id);
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL DEFAULT ''
);
"""


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Store:
    """Wrapper around the terminal-local meeting history DB."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        with _connect(self.db_path) as conn:
            conn.executescript(_SCHEMA)

    # -- meetings ---------------------------------------------------------

    def add_meeting(self, meeting: Meeting) -> Meeting:
        recorded_at = meeting.recorded_at or now_iso()
        with _connect(self.db_path) as conn:
            cur = conn.execute(
                """INSERT INTO meetings
                   (title, summary, transcript, language, duration_seconds,
                    template_used, category, attendees, source, status,
                    audio_path, mic_path, recorded_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    meeting.title,
                    meeting.summary,
                    meeting.transcript,
                    meeting.language,
                    meeting.duration_seconds,
                    meeting.template_used,
                    meeting.category,
                    json.dumps(meeting.attendees, ensure_ascii=False),
                    meeting.source,
                    meeting.status,
                    meeting.audio_path,
                    meeting.mic_path,
                    recorded_at,
                ),
            )
            meeting.id = int(cur.lastrowid)
            meeting.recorded_at = recorded_at
        self._set_action_items(meeting.id, _extract_action_items(meeting.summary))
        return meeting

    def update_meeting(self, meeting: Meeting) -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                """UPDATE meetings SET
                     title=?, summary=?, transcript=?, language=?,
                     duration_seconds=?, template_used=?, category=?, attendees=?,
                     source=?, status=?, audio_path=?, mic_path=?, recorded_at=?
                   WHERE id=?""",
                (
                    meeting.title,
                    meeting.summary,
                    meeting.transcript,
                    meeting.language,
                    meeting.duration_seconds,
                    meeting.template_used,
                    meeting.category,
                    json.dumps(meeting.attendees, ensure_ascii=False),
                    meeting.source,
                    meeting.status,
                    meeting.audio_path,
                    meeting.mic_path,
                    meeting.recorded_at,
                    meeting.id,
                ),
            )
        self._set_action_items(meeting.id, _extract_action_items(meeting.summary))

    def get_meeting(self, meeting_id: int) -> Meeting | None:
        with _connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,)).fetchone()
        return self._meeting_from_row(row) if row else None

    def list_meetings(self) -> list[Meeting]:
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM meetings ORDER BY recorded_at DESC, id DESC"
            ).fetchall()
        return [self._meeting_from_row(r) for r in rows]

    def delete_meeting(self, meeting_id: int) -> None:
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM meetings WHERE id=?", (meeting_id,))

    def count(self) -> int:
        with _connect(self.db_path) as conn:
            return int(conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0])

    @staticmethod
    def _meeting_from_row(row: sqlite3.Row) -> Meeting:
        try:
            attendees = json.loads(row["attendees"] or "[]")
        except json.JSONDecodeError:
            attendees = []
        return Meeting(
            id=row["id"],
            title=row["title"] or "",
            summary=row["summary"] or "",
            transcript=row["transcript"] or "",
            language=row["language"] or "",
            duration_seconds=row["duration_seconds"] or 0.0,
            template_used=row["template_used"] or "",
            category=row["category"] or "",
            attendees=attendees if isinstance(attendees, list) else [],
            source=row["source"] or "recorded",
            status=row["status"] or "pending",
            audio_path=row["audio_path"],
            mic_path=row["mic_path"],
            recorded_at=row["recorded_at"] or "",
        )

    # -- action items -----------------------------------------------------

    def set_action_items(self, meeting_id: int, items: list[ActionItem]) -> None:
        self._set_action_items(meeting_id, [i.text for i in items])

    def _set_action_items(self, meeting_id: int, texts: list[str]) -> None:
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM action_items WHERE meeting_id=?", (meeting_id,))
            for text in texts:
                conn.execute(
                    "INSERT INTO action_items (meeting_id, text, done) VALUES (?,?,0)",
                    (meeting_id, text),
                )

    def get_action_items(self, meeting_id: int) -> list[ActionItem]:
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM action_items WHERE meeting_id=? ORDER BY id", (meeting_id,)
            ).fetchall()
        return [self._action_from_row(r) for r in rows]

    def set_action_done(self, item_id: int, done: bool) -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                "UPDATE action_items SET done=? WHERE id=?", (1 if done else 0, item_id)
            )

    def list_all_action_items(self, include_done: bool = False) -> list[tuple[ActionItem, Meeting]]:
        clause = "" if include_done else "WHERE ai.done=0"
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                f"""SELECT ai.id, ai.meeting_id, ai.text, ai.done,
                           m.title, m.recorded_at
                    FROM action_items ai
                    JOIN meetings m ON m.id = ai.meeting_id
                    {clause}
                    ORDER BY ai.done ASC, m.recorded_at DESC, ai.id"""
            ).fetchall()
        result = []
        for r in rows:
            item = ActionItem(id=r["id"], meeting_id=r["meeting_id"], text=r["text"], done=bool(r["done"]))
            meeting = Meeting(id=r["meeting_id"], title=r["title"] or "", recorded_at=r["recorded_at"] or "")
            result.append((item, meeting))
        return result

    @staticmethod
    def _action_from_row(row: sqlite3.Row) -> ActionItem:
        return ActionItem(
            id=row["id"], meeting_id=row["meeting_id"], text=row["text"], done=bool(row["done"])
        )

    # -- settings ---------------------------------------------------------

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with _connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key=?", (key,)
            ).fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with _connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )


def _extract_action_items(summary: str) -> list[str]:
    """Parse to-do bullets out of a summary's action-item sections.

    Mirrors the desktop's `extract_action_items`: sections whose heading
    matches `action item|next step|to-do|deliverable|task`, bullets are
    `- ` / `* ` lines beneath the heading until the next heading.
    """
    from .util import parse_action_items

    return parse_action_items(summary)