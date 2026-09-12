"""To-dos — every open action item across all meetings."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from .base import BaseScreen


class TodosScreen(BaseScreen):
    """Toggleable action items harvested from meeting summaries."""

    CSS = """
    TodosScreen {
        align: center top;
    }
    #todos-header {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #todos-title {
        text-style: bold;
        color: $accent;
    }
    #todos-actions {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    #todos-actions Button {
        margin: 0 1;
    }
    #todos-table {
        width: 1fr;
        height: 1fr;
        margin: 0 2 1 2;
    }
    """

    def __init__(self):
        super().__init__()
        self._include_done = False

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("To-dos", id="todos-title"),
            Static("", id="todos-count"),
            id="todos-header",
        )
        yield Horizontal(
            Button("Toggle done", id="btn-toggle", variant="primary"),
            Button("Show done", id="btn-show"),
            Button("Back", id="btn-back", variant="default"),
            id="todos-actions",
        )
        yield DataTable(id="todos-table")

    def on_mount(self) -> None:
        self._load()

    @work(thread=False)
    async def _load(self) -> None:
        rows = await asyncio.to_thread(
            self.app.rt.store.list_all_action_items, self._include_done
        )
        table = self.query_one("#todos-table", DataTable)
        table.clear(columns=True)
        table.add_column("Done", key="done", width=6)
        table.add_column("Item", key="text", width=1)
        table.add_column("Meeting", key="meeting", width=1)
        table.add_column("Date", key="date", width=17)
        for item, meeting in rows:
            table.add_row(
                "✓" if item.done else "☐",
                item.text,
                meeting.title or "(untitled)",
                meeting.recorded_date(),
                key=str(item.id),
            )
        open_count = sum(1 for item, _ in rows if not item.done)
        self.query_one("#todos-count", Static).update(
            f"[dim]{len(rows)} items · {open_count} open[/dim]"
        )
        if rows:
            table.focus()

    def _toggle(self, item_id: int) -> None:
        item = next(
            (
                i
                for i, _ in self.app.rt.store.list_all_action_items(include_done=True)
                if i.id == item_id
            ),
            None,
        )
        if item:
            self.app.rt.store.set_action_done(item.id, not item.done)
            self._load()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._toggle(int(event.row_key.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-toggle":
            key = self._selected_key()
            if key:
                self._toggle(int(key))
        elif event.button.id == "btn-show":
            self._include_done = not self._include_done
            self.query_one("#btn-show", Button).label = (
                "Hide done" if self._include_done else "Show done"
            )
            self._load()
        elif event.button.id == "btn-back":
            self.action_back()

    def _selected_key(self) -> str | None:
        table = self.query_one("#todos-table", DataTable)
        try:
            return table.coordinate_to_cell_key(table.cursor_coordinate)[0].value
        except Exception:
            return None