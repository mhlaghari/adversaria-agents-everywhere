"""Headless TUI smoke tests: boot the app and navigate the major screens."""

from __future__ import annotations

from pathlib import Path

import pytest

from adversaria_terminal.app import AdversariaApp, Runtime
from adversaria_terminal.config import AppConfig
from adversaria_terminal.models import HealthInfo, Meeting, TemplateInfo, WhisperModelInfo
from adversaria_terminal.store import open_store


class StubClient:
    """Minimal fake of the service client so the TUI runs fully offline."""

    def health(self) -> HealthInfo:
        return HealthInfo(
            status="degraded",
            whisper_model="N/A",
            ollama_available=True,
            transcriber_state="missing",
            transcriber_detail="Download a model first",
            embedder_state="ready",
            live_captions_state="missing",
        )

    def list_templates(self) -> list[TemplateInfo]:
        return [TemplateInfo(name="general", description="Default notes")]

    def get_template(self, name: str) -> str:
        return "# Notes\n\nPlaceholder."

    def whisper_models(self) -> list[WhisperModelInfo]:
        return [
            WhisperModelInfo(key="large-v3", label="Large v3", size="3.1 GB", downloaded=False)
        ]

    def whisper_download(self, key: str) -> None:
        return None

    def chat_stream(self, transcript: str, question: str, *, model=None):
        yield ("text", "answer ")
        yield ("done", "")

    def live_feed(self, audio_path: str, session: int, source: str):
        return [], [], "partial-here"


@pytest.mark.anyio
async def test_boot_and_navigate(tmp_path: Path):
    cfg = AppConfig(data_dir=str(tmp_path))
    store = open_store(cfg)
    rt = Runtime(config=cfg, client=StubClient(), store=store, data_dir=tmp_path)
    app = AdversariaApp(rt=rt)

    async with app.run_test() as pilot:
        await pilot.pause()
        from adversaria_terminal.screens.dashboard import DashboardScreen

        assert isinstance(app.screen, DashboardScreen)

        # open Meetings from the dashboard
        await pilot.press("ctrl+m")
        await pilot.pause()
        from adversaria_terminal.screens.meetings import MeetingsScreen

        assert isinstance(app.screen, MeetingsScreen)

        # back to dashboard
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, DashboardScreen)

        # open To-dos
        await pilot.press("ctrl+t")
        await pilot.pause()
        from adversaria_terminal.screens.todos import TodosScreen

        assert isinstance(app.screen, TodosScreen)


@pytest.mark.anyio
async def test_meeting_detail_for_existing_meeting(tmp_path: Path):
    cfg = AppConfig(data_dir=str(tmp_path))
    store = open_store(cfg)
    m = store.add_meeting(
        Meeting(
            title="Daily",
            summary="## Action Items\n- Call client",
            transcript="talk talk",
            status="done",
        )
    )
    rt = Runtime(config=cfg, client=StubClient(), store=store, data_dir=tmp_path)
    app = AdversariaApp(rt=rt)

    async with app.run_test() as pilot:
        app.open_meeting(m.id)
        await pilot.pause()
        from adversaria_terminal.screens.detail import MeetingDetailScreen

        assert isinstance(app.screen, MeetingDetailScreen)