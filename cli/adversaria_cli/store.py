"""CLI-owned SQLite data. Never opens or migrates the desktop database."""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .config import CliError, private_dir

QUERY_STOP_WORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "for",
        "from",
        "had",
        "has",
        "have",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "me",
        "my",
        "of",
        "on",
        "or",
        "our",
        "please",
        "should",
        "tell",
        "that",
        "the",
        "their",
        "them",
        "there",
        "these",
        "they",
        "this",
        "those",
        "to",
        "us",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "will",
        "with",
        "would",
        "you",
        "your",
        "about",
        "explain",
        "describe",
        "give",
        "say",
        "next",
    ]
)


def query_terms(query):
    """Keep subject terms, including short names such as AI, rather than question filler."""
    return [word for word in re.findall(r"\w{2,}", query.lower()) if word not in QUERY_STOP_WORDS]


def now():
    return datetime.now(UTC).isoformat(timespec="seconds")


class Store:
    def __init__(self, directory):
        self.directory = private_dir(Path(directory))
        self.path = self.directory / "terminal.db"
        with self.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    instructions TEXT NOT NULL DEFAULT '', paused INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL REFERENCES workspaces(id),
                    title TEXT NOT NULL, transcript TEXT NOT NULL, summary TEXT NOT NULL DEFAULT '',
                    created TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL REFERENCES workspaces(id),
                    title TEXT NOT NULL, text TEXT NOT NULL, origin TEXT NOT NULL,
                    UNIQUE(workspace_id, origin));
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY, workspace_id INTEGER NOT NULL REFERENCES workspaces(id),
                    title TEXT NOT NULL, kind TEXT NOT NULL, details TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'queued', web INTEGER NOT NULL DEFAULT 0,
                    origin TEXT UNIQUE, created TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL REFERENCES tasks(id),
                    status TEXT NOT NULL, artifact TEXT, error TEXT,
                    usage TEXT NOT NULL DEFAULT '{}', created TEXT NOT NULL);
            """)
        self.path.chmod(0o600)

    @contextmanager
    def db(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def rows(self, sql, params=()):
        with self.db() as db:
            return [dict(r) for r in db.execute(sql, params)]

    def workspace(self, name):
        if not name.strip():
            raise CliError("Workspace name cannot be blank.")
        with self.db() as db:
            db.execute("INSERT OR IGNORE INTO workspaces(name) VALUES (?)", (name.strip(),))
            return dict(
                db.execute("SELECT * FROM workspaces WHERE name=?", (name.strip(),)).fetchone()
            )

    def configure_workspace(self, workspace_id, *, paused=None, instructions=None):
        with self.db() as db:
            if paused is not None:
                db.execute("UPDATE workspaces SET paused=? WHERE id=?", (paused, workspace_id))
            if instructions is not None:
                db.execute(
                    "UPDATE workspaces SET instructions=? WHERE id=?", (instructions, workspace_id)
                )

    def meeting(self, workspace_id, title, transcript):
        if not transcript.strip():
            raise CliError("No speech/text was found; no empty meeting was saved.")
        with self.db() as db:
            return db.execute(
                "INSERT INTO meetings(workspace_id,title,transcript,created) VALUES (?,?,?,?)",
                (workspace_id, title, transcript, now()),
            ).lastrowid

    def get_meeting(self, mid):
        rows = self.rows("SELECT * FROM meetings WHERE id=?", (mid,))
        if not rows:
            raise CliError(f"Meeting {mid} does not exist.")
        return rows[0]

    def save_summary(self, mid, summary):
        with self.db() as db:
            db.execute("UPDATE meetings SET summary=? WHERE id=?", (summary, mid))

    def attach(self, workspace_id, path):
        path = Path(path).expanduser().resolve(strict=True)
        if path.stat().st_size > 2_000_000:
            raise CliError("Attach a text file smaller than 2 MB.")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise CliError(
                "Attachments must be UTF-8 text (Markdown, text, code, JSON or CSV)."
            ) from exc
        if "\x00" in text:
            raise CliError("This appears to be a binary file. Export it as text first.")
        with self.db() as db:
            db.execute(
                "INSERT INTO sources(workspace_id,title,text,origin) VALUES (?,?,?,?) "
                "ON CONFLICT(workspace_id,origin) DO UPDATE SET text=excluded.text,title=excluded.title",
                (workspace_id, path.name, text, str(path)),
            )

    def context(self, workspace_id, query, limit=16000):
        """Bounded lexical retrieval over paragraphs, including older meetings."""
        with self.db() as db:
            records = db.execute(
                "SELECT title,text,origin FROM sources WHERE workspace_id=? UNION ALL "
                "SELECT title,transcript,'meeting:'||id FROM meetings WHERE workspace_id=?",
                (workspace_id, workspace_id),
            )
            terms = query_terms(query)
            words = set(terms)
            if not words:
                return ""
            candidates = []
            for title, text, origin in records:
                for start in range(0, len(text), 1200):
                    chunk = text[start : start + 1600]
                    tokens = set(re.findall(r"\w{2,}", (title + " " + chunk).lower()))
                    score = len(words & tokens)
                    # A shared "AI" or "project" alone must not redirect a question
                    # about another subject. Also recognize names written as one word.
                    if len(terms) > 1 and "".join(terms) in tokens:
                        score = len(words)
                    if score >= min(2, len(words)):
                        candidates.append((score, f"Source: {title} ({origin})\n{chunk}"))
            candidates.sort(key=lambda r: r[0], reverse=True)
            return "\n\n".join(text for _, text in candidates[:10])[:limit]

    def add_task(self, workspace_id, title, kind, details="", web=False, origin=None):
        if not title.strip():
            raise CliError("Task title cannot be blank.")
        with self.db() as db:
            db.execute(
                "INSERT OR IGNORE INTO tasks(workspace_id,title,kind,details,web,origin,created) "
                "VALUES (?,?,?,?,?,?,?)",
                (workspace_id, title, kind, details, web, origin, now()),
            )
            if origin:
                return db.execute("SELECT id FROM tasks WHERE origin=?", (origin,)).fetchone()[0]
            return db.execute("SELECT last_insert_rowid()").fetchone()[0]

    def task(self, task_id):
        rows = self.rows(
            "SELECT t.*,w.name workspace,w.instructions,w.paused FROM tasks t "
            "JOIN workspaces w ON w.id=t.workspace_id WHERE t.id=?",
            (task_id,),
        )
        if not rows:
            raise CliError(f"Task {task_id} does not exist.")
        return rows[0]

    def claim(self, task_id):
        with self.db() as db:
            changed = db.execute(
                "UPDATE tasks SET status='running' WHERE id=? AND status IN ('queued','failed') "
                "AND workspace_id IN (SELECT id FROM workspaces WHERE paused=0)",
                (task_id,),
            ).rowcount
            if not changed:
                raise CliError(
                    "Task is not queued/failed, already running, or its workspace is paused."
                )
            return db.execute(
                "INSERT INTO runs(task_id,status,created) VALUES (?,'running',?)", (task_id, now())
            ).lastrowid

    def finish(self, task_id, run_id, *, artifact=None, error=None, usage=None):
        status = "failed" if error else "awaiting_review"
        with self.db() as db:
            db.execute(
                "UPDATE runs SET status=?,artifact=?,error=?,usage=? WHERE id=? AND status='running'",
                (
                    status,
                    str(artifact) if artifact else None,
                    error,
                    json.dumps(usage or {}),
                    run_id,
                ),
            )
            db.execute(
                "UPDATE tasks SET status=? WHERE id=? AND status='running'", (status, task_id)
            )

    def review(self, task_id, approve):
        status = "done" if approve else "queued"
        with self.db() as db:
            if not db.execute(
                "UPDATE tasks SET status=? WHERE id=? AND status='awaiting_review'",
                (status, task_id),
            ).rowcount:
                raise CliError("Only a task awaiting review can be approved or revised.")

    def artifact(self, task_id):
        rows = self.rows(
            "SELECT artifact FROM runs WHERE task_id=? AND artifact IS NOT NULL ORDER BY id DESC LIMIT 1",
            (task_id,),
        )
        if not rows:
            raise CliError("No completed artifact yet.")
        path = Path(rows[0]["artifact"]).resolve()
        if not path.is_relative_to((self.directory / "artifacts").resolve()):
            raise CliError("Artifact path is outside the CLI artifact directory.")
        return path

    def retry(self, task_id):
        with self.db() as db:
            if not db.execute(
                "UPDATE tasks SET status='queued' WHERE id=? AND status IN ('failed','awaiting_review')",
                (task_id,),
            ).rowcount:
                raise CliError("Retry requires a failed task or a draft awaiting review.")

    def recover(self, task_id):
        # Explicit recovery, never invoked at startup: another process may own the run.
        with self.db() as db:
            if not db.execute(
                "UPDATE tasks SET status='failed' WHERE id=? AND status='running'", (task_id,)
            ).rowcount:
                raise CliError("Only a stuck running task can be recovered.")
            db.execute(
                "UPDATE runs SET status='failed',error='Recovered by user after interrupted process' "
                "WHERE task_id=? AND status='running'",
                (task_id,),
            )
