"""Shared data shapes for the terminal client."""

from __future__ import annotations

import dataclasses
import datetime as _dt


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


@dataclasses.dataclass
class Meeting:
    """One meeting-history row in the terminal's local store."""

    id: int = 0
    title: str = ""
    summary: str = ""
    transcript: str = ""
    language: str = ""
    duration_seconds: float = 0.0
    template_used: str = ""
    category: str = ""
    attendees: list[str] = dataclasses.field(default_factory=list)
    source: str = "recorded"  # "recorded" | "imported"
    status: str = "done"  # pending | done | needs_transcribe
    audio_path: str | None = None
    mic_path: str | None = None
    recorded_at: str = ""

    def recorded_date(self) -> str:
        try:
            dt = _dt.datetime.fromisoformat(self.recorded_at)
        except ValueError:
            return self.recorded_at
        return dt.strftime("%Y-%m-%d %H:%M")

    def short_summary(self, limit: int = 140) -> str:
        return self.summary.replace("\n", " ").strip()[:limit] if self.summary else ""


@dataclasses.dataclass
class ActionItem:
    id: int = 0
    meeting_id: int = 0
    text: str = ""
    done: bool = False


@dataclasses.dataclass
class HealthInfo:
    status: str
    whisper_model: str
    ollama_available: bool
    transcriber_state: str
    transcriber_detail: str | None
    embedder_state: str | None
    embedder_detail: str | None
    live_captions_state: str | None

    @property
    def ready(self) -> bool:
        return self.status == "ok"


@dataclasses.dataclass
class TemplateInfo:
    name: str
    description: str


@dataclasses.dataclass
class WhisperModelInfo:
    key: str
    label: str
    size: str
    downloaded: bool