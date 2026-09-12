"""Dashboard — service status and quick actions."""

from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from ..models import HealthInfo
from .base import DashboardScreenBase


class _StatusCard(Static):
    def __init__(self, title: str, value: str = "…", tone: str = "primary"):
        super().__init__()
        self.card_title = title
        self.card_value = value
        self.tone = tone
        self.classes = "status-card"

    def compose(self) -> ComposeResult:
        yield Static(self.card_title, classes="status-title")
        yield Static(self.card_value, id="status-value", classes="status-value")

    def on_mount(self) -> None:
        self.query_one("#status-value", Static).update(self.card_value)

    def set_value(self, value: str, tone: str | None = None) -> None:
        if tone:
            self.tone = tone
        self.query_one("#status-value", Static).update(value)


class DashboardScreen(DashboardScreenBase):
    """Entry point: health snapshot + quick actions + recent meetings."""

    CSS = """
    DashboardScreen {
        align: center top;
    }
    #quick-actions {
        grid-size: 4;
        height: auto;
        margin: 0 1 1 1;
    }
    #quick-actions Button {
        margin: 0 1;
    }
    #status-grid {
        layout: horizontal;
        height: auto;
        margin: 1 1 0 1;
    }
    .status-title {
        color: $text-muted;
    }
    .status-value {
        text-style: bold;
    }
    #dashboard-tip {
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            _StatusCard("Transcriber", "checking…"),
            _StatusCard("Whisper model", "checking…"),
            _StatusCard("LLM (Ollama)", "checking…"),
            _StatusCard("Live captions", "checking…"),
            id="status-grid",
        )
        yield Vertical(
            Button("Record", id="btn-record", variant="primary"),
            Button("Import audio", id="btn-import", variant="default"),
            Button("Meetings", id="btn-meetings", variant="default"),
            Button("Ask", id="btn-ask", variant="default"),
            Button("To-dos", id="btn-todos", variant="default"),
            Button("Templates", id="btn-templates", variant="default"),
            Button("Models", id="btn-models", variant="default"),
            Button("Settings", id="btn-settings", variant="default"),
            id="quick-actions",
        )
        yield Static(
            "[dim]ctrl+r Record · ctrl+m Meetings · ctrl+i Import · ctrl+t To-dos · "
            "ctrl+e Templates · ctrl+l Models · ctrl+s Settings · escape Quit[/dim]",
            id="dashboard-tip",
        )
        yield Static("Recent meetings", classes="panel-title")
        yield DataTable(id="recent", classes="panel")

    def on_mount(self) -> None:
        self.run_worker(self._load_health(), name="dash-health")
        self.worker_meetings = self.run_worker(self._load_recent(), name="dash-recent")

    async def _load_health(self) -> None:
        try:
            health: HealthInfo = await asyncio.to_thread(self.app.rt.client.health)
            self._render_health(health)
        except Exception as exc:
            self._set_card(0, "unreachable", "error")
            self._set_card(1, "-", "error")
            self._set_card(2, "-", "error")
            self._set_card(3, "-", "error")
            self.notify(f"Python service: {exc}", severity="error")

    def _set_card(self, index: int, value: str, tone: str) -> None:
        cards = self.query(_StatusCard)
        if len(cards) > index:
            cards[index].set_value(value, tone=tone)

    def _render_health(self, health: HealthInfo) -> None:
        def tone_for(state: str | None) -> str:
            return {"ready": "success", "ok": "success", "error": "error"}.get(
                state or "", "warning"
            )

        self._set_card(0, health.transcriber_state, tone_for(health.transcriber_state))
        model = health.whisper_model if health.whisper_model != "N/A" else "—"
        self._set_card(1, model, tone_for(health.transcriber_state))
        self._set_card(
            2, "ready" if health.ollama_available else "down", tone_for("ready" if health.ollama_available else "error")
        )
        self._set_card(
            3, health.live_captions_state or "n/a", tone_for(health.live_captions_state)
        )

    async def _load_recent(self) -> None:
        meetings = await asyncio.to_thread(self.app.rt.store.list_meetings)
        table = self.query_one("#recent", DataTable)
        table.clear(columns=True)
        table.add_column("#", key="id")
        table.add_column("Title", key="title")
        table.add_column("Date", key="date")
        table.add_column("Category", key="cat")
        for m in meetings[:12]:
            table.add_row(
                str(m.id),
                m.title or "(untitled)",
                m.recorded_date(),
                m.category or "",
                key=str(m.id),
            )
        table.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn = event.button.id
        if btn == "btn-record":
            self.action_record()
        elif btn == "btn-import":
            self.action_import()
        elif btn == "btn-meetings":
            self.action_meetings()
        elif btn == "btn-ask":
            from .ask import AskScreen

            self.app.push_screen(AskScreen())
        elif btn == "btn-todos":
            from .todos import TodosScreen

            self.app.push_screen(TodosScreen())
        elif btn == "btn-templates":
            from .templates import TemplatesScreen

            self.app.push_screen(TemplatesScreen())
        elif btn == "btn-models":
            from .models import ModelsScreen

            self.app.push_screen(ModelsScreen())
        elif btn == "btn-settings":
            from .settings import SettingsScreen

            self.app.push_screen(SettingsScreen())

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.open_meeting(int(event.row_key.value))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        # Keep the table keyboard-navigable without stealing focus from buttons.
        event.stop()