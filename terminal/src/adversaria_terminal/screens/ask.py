"""Ask — grounded Q&A over one meeting's transcript (streamed answers)."""

from __future__ import annotations

import asyncio
import threading

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, RichLog, Static

from ..models import Meeting
from .base import BaseScreen


class AskScreen(BaseScreen):
    """Stream an LLM answer grounded in a meeting's transcript."""

    CSS = """
    AskScreen {
        align: center top;
    }
    #ask-context {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #ask-title {
        text-style: bold;
        color: $accent;
    }
    #ask-input-row {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    #ask-input {
        width: 1fr;
    }
    #ask-output {
        width: 1fr;
        height: 1fr;
        margin: 0 2 1 2;
        border: round $primary;
        padding: 0 1;
    }
    """

    def __init__(self, meeting_id: int | None = None):
        super().__init__()
        self.meeting_id = meeting_id
        self.meeting: Meeting | None = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Ask", id="ask-title"),
            Static("", id="ask-context"),
            id="ask-context",
        )
        yield Horizontal(
            Input(placeholder="Ask about this meeting…", id="ask-input"),
            Button("Ask", id="btn-ask", variant="primary"),
            Button("Back", id="btn-back", variant="default"),
            id="ask-input-row",
        )
        yield RichLog(id="ask-output", wrap=True, markup=True, highlight=True)

    def on_mount(self) -> None:
        self._load()

    @work(thread=False)
    async def _load(self) -> None:
        meeting = await asyncio.to_thread(self._resolve_meeting)
        self.meeting = meeting
        if meeting is None:
            self.query_one("#ask-context", Static).update(
                "[yellow]No meeting with a transcript yet — record/import one, then ask.[/yellow]"
            )
            self.query_one("#ask-input", Input).disabled = True
            self.query_one("#btn-ask", Button).disabled = True
            return
        self.query_one("#ask-context", Static).update(
            f"[dim]{meeting.title} · {meeting.recorded_date()}[/dim]"
        )

    def _resolve_meeting(self) -> Meeting | None:
        store = self.app.rt.store
        if self.meeting_id:
            return store.get_meeting(self.meeting_id)
        for m in store.list_meetings():
            if m.transcript:
                return m
        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ask":
            box = self.query_one("#ask-input", Input)
            if box.value.strip() and self.meeting is not None:
                self._ask(box.value.strip())
        elif event.button.id == "btn-back":
            self.action_back()

    def action_ask(self) -> None:
        self.on_button_pressed(Button.Pressed(self, self.query_one("#btn-ask", Button)))

    def _ask(self, question: str) -> None:
        meeting = self.meeting
        if meeting is None:
            return
        out = self.query_one("#ask-output", RichLog)
        out.write("")
        out.write(f"[bold cyan]{question}[/bold cyan]")
        out.write("")
        threading.Thread(
            target=self._stream, args=(meeting, question), daemon=True, name="ask-stream"
        ).start()

    def _stream(self, meeting: Meeting, question: str) -> None:
        try:
            for kind, value in self.app.rt.client.chat_stream(
                meeting.transcript, question, model=self.app.rt.config.ollama_model
            ):
                if kind == "text":
                    self.app.call_from_thread(self._append_token, value)
                elif kind == "error":
                    self.app.call_from_thread(self._append_token, f"\n[red]{value}[/red]")
        except Exception as exc:
            self.app.call_from_thread(self._append_token, f"\n[red]{exc}[/red]")

    def _append_token(self, token: str) -> None:
        self.query_one("#ask-output", RichLog).write(token)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "ask-input" and event.value.strip() and self.meeting is not None:
            self._ask(event.value.strip())