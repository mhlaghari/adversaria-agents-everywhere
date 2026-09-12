"""The Textual application shell for Adversaria Terminal."""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

from textual.app import App
from textual.binding import Binding
from textual.widgets import Footer, Header

from .client import ServiceClient
from .config import AppConfig, load_config, service_url_env
from .storage import Store
from .store import open_store

APP_CSS = """
Screen {
    background: $background;
}

.panel {
    border: round $primary;
    padding: 1 2;
    margin: 0 1 1 1;
}

.status-grid {
    layout: horizontal;
    height: 8;
}

.status-card {
    border: round $primary;
    padding: 1 2;
    margin: 0 1;
    height: 8;
    width: 1fr;
}

.hint {
    color: $text-muted;
}

.numbers {
    text-style: bold;
}
"""


@dataclasses.dataclass
class Runtime:
    """Everything the screens need beyond the App itself."""

    config: AppConfig
    client: ServiceClient
    store: Store
    data_dir: Path


def build_runtime(data_dir: str | None = None) -> Runtime:
    config = load_config()
    if data_dir:
        config.data_dir = data_dir
    url = service_url_env() or config.python_service_url
    client = ServiceClient(url)
    store = open_store(config)
    return Runtime(config=config, client=client, store=store, data_dir=config.applied_data_dir())


class AdversariaApp(App):
    """Meeting Note Taker in the terminal — the second presentation surface."""

    TITLE = "Adversaria Terminal"
    SUB_TITLE = "Meeting Note Taker — command line edition"
    CSS = APP_CSS
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("ctrl+r", "go_record", "Record"),
        Binding("ctrl+m", "go_meetings", "Meetings"),
        Binding("ctrl+i", "go_import", "Import"),
        Binding("ctrl+t", "go_todos", "To-dos"),
        Binding("ctrl+e", "go_templates", "Templates"),
        Binding("ctrl+l", "go_models", "Models"),
        Binding("ctrl+s", "go_settings", "Settings"),
    ]

    def __init__(self, data_dir: str | None = None, rt: Runtime | None = None):
        super().__init__()
        self.rt = rt or build_runtime(data_dir)

    def compose(self):
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        from .screens.dashboard import DashboardScreen

        self.push_screen(DashboardScreen())

    def action_go_record(self) -> None:
        self.screen.action_record()

    def action_go_meetings(self) -> None:
        self.screen.action_meetings()

    def action_go_import(self) -> None:
        self.screen.action_import()

    def action_go_todos(self) -> None:
        self.screen.action_todos()

    def action_go_templates(self) -> None:
        self.screen.action_templates()

    def action_go_models(self) -> None:
        self.screen.action_models()

    def action_go_settings(self) -> None:
        self.screen.action_settings()

    def open_meeting(self, meeting_id: int) -> None:
        from .screens.detail import MeetingDetailScreen

        self.push_screen(MeetingDetailScreen(meeting_id=meeting_id))


def main_entry() -> int:
    from .cli import main

    return main(sys.argv[1:])