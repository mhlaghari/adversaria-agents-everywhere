"""Import — transcribe + summarize an existing audio file into the store."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Static

from ..models import Meeting
from .base import BaseScreen


class ImportScreen(BaseScreen):
    """Bring an existing recording in: transcribe it, summarize it, store it."""

    CSS = """
    ImportScreen {
        align: center middle;
    }
    #import-card {
        width: 80%;
        height: auto;
        border: round $primary;
        padding: 1 2;
        background: $surface;
    }
    #import-card Input {
        margin: 1 0;
    }
    #import-actions {
        height: auto;
    }
    #import-actions Button {
        margin: 0 1;
    }
    #import-status {
        color: $text-muted;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("Import audio file", id="import-title", classes="source-header")
        yield Input(placeholder="Full path to a .wav / .m4a / audio file…", id="import-path")
        yield Static(
            "[dim]Tip: even the desktop's untouched SDK recordings import this way. "
            "The service transcribes on-device and its summary template applies.[/dim]",
            id="import-status",
        )
        yield Horizontal(
            Button("Import", id="btn-import", variant="primary"),
            Button("Back", id="btn-back", variant="default"),
            id="import-actions",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-import":
            self._start()
        elif event.button.id == "btn-back":
            self.action_back()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "import-path":
            self._start()

    def _start(self) -> None:
        raw = self.query_one("#import-path", Input).value.strip()
        if not raw:
            self.notify("Enter a file path first.", severity="warning")
            return
        path = Path(raw).expanduser()
        if not path.exists():
            self.notify(f"File not found: {path}", severity="error")
            return
        self.query_one("#import-title", Static).update(
            f"Importing [bold]{path.name}[/bold]…"
        )
        # `_import` is already `@work`-decorated; call it directly (see
        # record.py's `_live_loop` for why double-wrapping in `run_worker()`
        # raises WorkerError).
        self._import(path)

    @work(exclusive=True)
    async def _import(self, path: Path) -> None:
        rt = self.app.rt
        if rt.processing_lock.locked():
            self.query_one("#import-title", Static).update(
                f"Queued [bold]{path.name}[/bold] — waiting for other processing to finish…"
            )
        try:
            async with rt.processing_lock:
                self.query_one("#import-title", Static).update(
                    f"Importing [bold]{path.name}[/bold]…"
                )
                note = await asyncio.to_thread(
                    self._pipeline, str(path.resolve())
                )
        except Exception as exc:
            self.query_one("#import-title", Static).update("Import audio file")
            self.notify(str(exc), severity="error")
            return
        meeting = Meeting(
            title=note.get("title") or path.stem,
            summary=note.get("summary", ""),
            transcript=note.get("transcript", ""),
            language=note.get("language", ""),
            duration_seconds=note.get("duration_seconds", 0.0),
            template_used=note.get("template_used") or rt.config.default_prompt_template,
            category=note.get("category") or "",
            attendees=note.get("attendees") or [],
            source="imported",
            status="done",
        )
        from ..models import now_iso

        meeting.recorded_at = now_iso()
        try:
            meeting = rt.store.add_meeting(meeting)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        self.notify("Imported.")
        self.open_meeting(meeting.id)

    def _pipeline(self, audio_path: str) -> dict:
        rt = self.app.rt
        from ..client import transcribe_and_summarize

        return transcribe_and_summarize(
            rt.client,
            audio_path=audio_path,
            mic_audio_path=None,
            me_label=rt.config.user_name,
            vocabulary=rt.config.custom_vocabulary,
            diarize=rt.config.diarize,
            whisper_model=None,
            template_name=rt.config.default_prompt_template,
            model=rt.config.ollama_model,
            output_language=rt.config.summary_language,
            single_file=True,
        )