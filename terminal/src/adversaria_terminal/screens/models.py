"""Models — transcription model catalogue + downloads."""

from __future__ import annotations

import asyncio

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Static

from ..models import WhisperModelInfo
from .base import BaseScreen


class ModelsScreen(BaseScreen):
    """List available Whisper models and let the user download them on-device."""

    CSS = """
    ModelsScreen {
        align: center top;
    }
    #models-header {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #models-title {
        text-style: bold;
        color: $accent;
    }
    #models-table {
        width: 1fr;
        height: 1fr;
        margin: 1 2;
    }
    #models-actions {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    #models-actions Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Transcription models", id="models-title"),
            Static("", id="models-status"),
            id="models-header",
        )
        yield DataTable(id="models-table")
        yield Horizontal(
            Button("Download selected", id="btn-download", variant="primary"),
            Button("Refresh", id="btn-refresh"),
            Button("Back", id="btn-back", variant="default"),
            id="models-actions",
        )

    def on_mount(self) -> None:
        self._models: list[WhisperModelInfo] = []
        self._load()

    @work(thread=False)
    async def _load(self) -> None:
        try:
            self._models = await asyncio.to_thread(self.app.rt.client.whisper_models)
        except Exception as exc:
            self.query_one("#models-status", Static).update(f"[red]{exc}[/red]")
            return
        table = self.query_one("#models-table", DataTable)
        table.clear(columns=True)
        table.add_column("Key", key="key", width=1)
        table.add_column("Label", key="label", width=1)
        table.add_column("Size", key="size", width=20)
        table.add_column("Downloaded", key="downloaded", width=12)
        for m in self._models:
            table.add_row(
                m.key,
                m.label or "",
                m.size or "",
                "[green]yes[/green]" if m.downloaded else "[dim]no[/dim]",
                key=m.key,
            )
        if self._models:
            table.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-download":
            self._download()
        elif event.button.id == "btn-refresh":
            self._load()
        elif event.button.id == "btn-back":
            self.action_back()

    def _download(self) -> None:
        table = self.query_one("#models-table", DataTable)
        try:
            key = table.coordinate_to_cell_key(table.cursor_coordinate)[0].value
        except Exception:
            self.notify("Pick a model first.", severity="warning")
            return
        model = next((m for m in self._models if m.key == key), None)
        if model is None or model.downloaded:
            self.notify("Nothing to download.", severity="warning")
            return
        # `_download_worker` is already `@work`-decorated; calling it starts
        # the worker directly. Wrapping it in `run_worker()` again feeds the
        # returned `Worker` object back in as "work" for a second worker,
        # which Textual rejects with WorkerError("Unsupported attempt to run
        # an async worker").
        self._download_worker(key)
        self.query_one("#models-status", Static).update(
            f"[yellow]Downloading {key}… (can take a while)[/yellow]"
        )

    @work(exclusive=True)
    async def _download_worker(self, key: str) -> None:
        try:
            await asyncio.to_thread(self.app.rt.client.whisper_download, key)
        except Exception as exc:
            self.query_one("#models-status", Static).update(f"[red]{exc}[/red]")
            return
        self.query_one("#models-status", Static).update(
            f"[green]Downloaded {key} — the service picks it up automatically.[/green]"
        )
        self.notify(f"Downloaded {key}.")
        self._load()