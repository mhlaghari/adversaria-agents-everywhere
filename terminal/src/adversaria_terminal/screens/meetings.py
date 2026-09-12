"""Meetings browser — all history in a filterable table."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.widgets import DataTable, Input, Static

from ..models import Meeting
from .base import BaseScreen


class MeetingsScreen(BaseScreen):
    CSS = """
    MeetingsScreen {
        align: center top;
    }
    #meetings-filter {
        width: 1fr;
        margin: 0 1 1 1;
    }
    #meetings-table {
        width: 1fr;
        height: 1fr;
        margin: 0 1 1 1;
    }
    #meetings-count {
        color: $text-muted;
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="meetings-count")
        yield Input(
            placeholder="Filter by title or content…",
            id="meetings-filter",
        )
        yield DataTable(id="meetings-table")

    def on_mount(self) -> None:
        self._meetings: list[Meeting] = []
        self._query = ""
        self._load()

    @work(thread=False)
    async def _load(self, query: str = "") -> None:
        meetings = await asyncio.to_thread(self.app.rt.store.list_meetings)
        self._meetings = meetings
        self._populate(query)

    def _populate(self, query: str = "") -> None:
        table = self.query_one("#meetings-table", DataTable)
        table.clear(columns=True)
        table.add_column("#", key="id", width=5)
        table.add_column("Title", key="title", width=40)
        table.add_column("Date", key="date", width=17)
        table.add_column("Category", key="cat", width=12)
        table.add_column("Dur", key="dur", width=7)
        table.add_column("Status", key="status", width=12)

        q = (query or "").strip().lower()
        total = 0
        for m in self._meetings:
            if q and q not in (m.title or "").lower() and q not in (m.summary or "").lower():
                continue
            total += 1
            dur = ""
            if m.duration_seconds:
                s = round(m.duration_seconds)
                mm, ss = divmod(s, 60)
                dur = f"{mm}m{ss:02d}s" if mm else f"{ss}s"
            table.add_row(
                str(m.id),
                m.title or "(untitled)",
                m.recorded_date(),
                m.category or "",
                dur,
                m.status,
                key=str(m.id),
            )
        self.query_one("#meetings-count", Static).update(
            f"Meeting history — {len(self._meetings)} total"
            + (f" · {total} shown" if q else "")
        )
        if total > 0:
            table.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "meetings-filter":
            self._populate(event.value)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.open_meeting(int(event.row_key.value))