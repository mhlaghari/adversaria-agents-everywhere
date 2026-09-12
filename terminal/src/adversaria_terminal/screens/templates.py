"""Templates — browse note templates and set the default."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from ..models import TemplateInfo
from .base import BaseScreen


class TemplatesScreen(BaseScreen):
    """List templates; selection shows the raw prompt for inspection."""

    CSS = """
    TemplatesScreen {
        align: center top;
    }
    #templates-header {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #templates-title {
        text-style: bold;
        color: $accent;
    }
    #templates-layout {
        height: 1fr;
        width: 100%;
    }
    #templates-list {
        width: 50%;
        height: 1fr;
        margin: 1 1 1 2;
    }
    #templates-preview {
        width: 1fr;
        height: 1fr;
        margin: 1 2 1 1;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    #templates-actions {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    #templates-actions Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Note templates", id="templates-title"),
            Static("", id="templates-default"),
            id="templates-header",
        )
        yield Horizontal(
            DataTable(id="templates-list"),
            Static("", id="templates-preview"),
            id="templates-layout",
        )
        yield Horizontal(
            Button("Set default", id="btn-set", variant="primary"),
            Button("Back", id="btn-back", variant="default"),
            id="templates-actions",
        )

    def on_mount(self) -> None:
        self._templates: list[TemplateInfo] = []
        self.query_one("#templates-default", Static).update(
            f"[dim]Current default: {self.app.rt.config.default_prompt_template}[/dim]"
        )
        self._load()

    @work(thread=False)
    async def _load(self) -> None:
        try:
            self._templates = await asyncio.to_thread(self.app.rt.client.list_templates)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        table = self.query_one("#templates-list", DataTable)
        table.clear(columns=True)
        table.add_column("Template", key="name", width=1)
        table.add_column("Description", key="desc", width=1)
        for t in self._templates:
            table.add_row(t.name, t.description or "", key=t.name)
        if self._templates:
            table.focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        name = event.row_key.value if event.row_key else None
        if name:
            self._preview(str(name))

    def _preview(self, name: str) -> None:
        # `_preview_worker` is already `@work`-decorated; call it directly
        # (double-wrapping in `run_worker()` raises WorkerError — see
        # record.py's `_live_loop`).
        self._preview_worker(name)

    @work(thread=False)
    async def _preview_worker(self, name: str) -> None:
        try:
            content = await asyncio.to_thread(self.app.rt.client.get_template, name)
        except Exception as exc:
            self.query_one("#templates-preview", Static).update(f"[red]{exc}[/red]")
            return
        if len(content) > 4000:
            content = content[:4000] + "\n…(truncated)"
        self.query_one("#templates-preview", Static).update(f"[b]{name}[/b]\n\n{content}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-set":
            self._set_default()
        elif event.button.id == "btn-back":
            self.action_back()

    def _set_default(self) -> None:
        table = self.query_one("#templates-list", DataTable)
        try:
            cell = table.coordinate_to_cell_key(table.cursor_coordinate)[0]
            name = cell.value
        except Exception:
            self.notify("Pick a template in the list first.", severity="warning")
            return
        self.app.rt.config.default_prompt_template = name
        try:
            from ..config import save_config

            save_config(self.app.rt.config)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        self.query_one("#templates-default", Static).update(
            f"[dim]Current default: {name}[/dim]"
        )
        self.notify(f"Default template set to “{name}”.")