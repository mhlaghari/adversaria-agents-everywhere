"""Meeting detail — notes, transcript, to-dos, and actions."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Markdown,
    SelectionList,
    Static,
    TabbedContent,
    TabPane,
)

from ..models import Meeting
from ..util import safe_filename
from .base import BaseScreen, ConfirmModal


class TemplatePicker(Screen):
    """Choose a note template; the name is dismissed back to `push_screen`."""

    CSS = """
    TemplatePicker {
        align: center middle;
    }
    #picker-card {
        width: 62%;
        height: 70%;
        border: round $accent;
        background: $surface;
        padding: 1 2;
    }
    #picker-list {
        height: 1fr;
        margin: 1 0;
    }
    """

    def __init__(self, names: list[str]):
        super().__init__()
        self._names = names

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Pick a note template", classes="source-header"),
            SelectionList[str](*[(name, name) for name in self._names], id="picker-list"),
            Horizontal(
                Button("Use selection", id="picker-ok", variant="primary"),
                Button("Cancel", id="picker-cancel", variant="default"),
            ),
            id="picker-card",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "picker-ok":
            selected = self.query_one(SelectionList).selected
            if not selected:
                self.notify("Pick a template first.", severity="warning")
                return
            self.dismiss(str(selected[0]))
        elif event.button.id == "picker-cancel":
            self.dismiss(None)


class MeetingDetailScreen(BaseScreen):
    """Notes / transcript / to-dos for one meeting + actions."""

    CSS = """
    MeetingDetailScreen {
        align: center top;
    }
    #detail-meta {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #detail-title {
        text-style: bold;
        color: $accent;
    }
    #detail-actions {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    #detail-actions Button {
        margin: 0 1;
    }
    #detail-tabs {
        height: 1fr;
        margin: 0 1 1 1;
    }
    #notes-markdown {
        height: 1fr;
        padding: 0 1;
    }
    #transcript-text {
        height: 1fr;
        padding: 1 2;
        background: $surface;
    }
    #todos-table {
        height: 1fr;
    }
    """

    def __init__(self, meeting_id: int):
        super().__init__()
        self.meeting_id = meeting_id
        self.meeting: Meeting | None = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("", id="detail-title"),
            Static("", id="detail-meta"),
            id="detail-header",
        )
        yield Horizontal(
            Button("Ask", id="btn-ask", variant="primary"),
            Button("Re-summarize", id="btn-resummarize"),
            Button("Retry", id="btn-retry"),
            Button("Export .md", id="btn-export"),
            Button("Delete", id="btn-delete", variant="error"),
            Button("Back", id="btn-back", variant="default"),
            id="detail-actions",
        )
        with TabbedContent(id="detail-tabs"):
            with TabPane("Notes", id="tab-notes"):
                yield Markdown("", id="notes-markdown")
            with TabPane("Transcript", id="tab-transcript"):
                yield Static("", id="transcript-text")
            with TabPane("To-dos", id="tab-todos"):
                yield DataTable(id="todos-table")

    def on_mount(self) -> None:
        self._load()

    def _dur(self, seconds: float) -> str:
        s = round(seconds)
        mm, ss = divmod(s, 60)
        return f"{mm}m{ss:02d}s" if mm else f"{ss}s"

    @work(thread=False)
    async def _load(self) -> None:
        self.meeting = await asyncio.to_thread(
            self.app.rt.store.get_meeting, self.meeting_id
        )
        if self.meeting is None:
            self.notify("Meeting not found.", severity="error")
            self.action_back()
            return
        m = self.meeting
        dur = f" · {self._dur(m.duration_seconds)}" if m.duration_seconds else ""
        self.query_one("#detail-title", Static).update(f"{m.title or '(untitled)'}")
        self.query_one("#detail-meta", Static).update(
            f"[dim]{m.recorded_date()}{dur} · {m.category or 'meeting'} · "
            f"template: {m.template_used or '—'} · {m.source} · status: {m.status}[/dim]\n"
            f"[dim]attendees: {', '.join(m.attendees) or '—'}[/dim]"
        )
        self.query_one("#notes-markdown", Markdown).update(m.summary or "_No summary yet._")
        self.query_one("#transcript-text", Static).update(m.transcript or "_No transcript yet._")
        self.query_one("#btn-retry", Button).disabled = m.status != "needs_transcribe"
        self._render_todos()

    def _render_todos(self) -> None:
        items = self.app.rt.store.get_action_items(self.meeting_id) if self.meeting_id else []
        table = self.query_one("#todos-table", DataTable)
        table.clear(columns=True)
        table.add_column("Done", key="done", width=6)
        table.add_column("Item", key="text")
        for item in items:
            table.add_row("✓" if item.done else "☐", item.text, key=str(item.id))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if getattr(event.data_table, "id", None) == "todos-table":
            item_id = int(event.row_key.value)
            current = self.app.rt.store.get_action_items(self.meeting_id)
            item = next((i for i in current if i.id == item_id), None)
            if item:
                self.app.rt.store.set_action_done(item.id, not item.done)
                self._render_todos()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ask":
            from .ask import AskScreen

            self.app.push_screen(AskScreen(meeting_id=self.meeting_id))
        elif event.button.id == "btn-resummarize":
            self._pick_template()
        elif event.button.id == "btn-retry":
            self._retry()
        elif event.button.id == "btn-export":
            self._export()
        elif event.button.id == "btn-delete":
            self.app.push_screen(
                ConfirmModal("Delete this meeting?"), callback=self._delete_if_yes
            )
        elif event.button.id == "btn-back":
            self.action_back()

    def _pick_template(self) -> None:
        # `_pick_template_worker` is already `@work`-decorated; call it
        # directly (double-wrapping in `run_worker()` raises WorkerError —
        # see record.py's `_live_loop`).
        self._pick_template_worker()

    @work(thread=False)
    async def _pick_template_worker(self) -> None:
        try:
            templates = await asyncio.to_thread(self.app.rt.client.list_templates)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        if not templates:
            self.notify("No templates available.", severity="warning")
            return
        names = [t.name for t in templates]
        screen = TemplatePicker(names)
        self.push_screen(screen, callback=lambda n: self._resummarize(n) if n else None)

    def _resummarize(self, template_name: str) -> None:
        # `_do_resummarize` is already `@work`-decorated; call it directly.
        self._do_resummarize(template_name)

    @work(exclusive=True)
    async def _do_resummarize(self, template_name: str) -> None:
        meeting = self.meeting
        if meeting is None or not meeting.transcript:
            self.notify("This meeting has no transcript to summarize.", severity="warning")
            return
        self.notify(f"Re-summarizing with “{template_name}”…")
        rt = self.app.rt
        try:
            async with rt.processing_lock:
                summary = await asyncio.to_thread(
                    rt.client.summarize,
                    meeting.transcript,
                    template_name=template_name,
                    model=rt.config.ollama_model,
                    output_language=rt.config.summary_language,
                    meeting_date=meeting.recorded_at[:10] or None,
                )
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        meeting.summary = summary.get("summary", "")
        meeting.title = summary.get("title") or meeting.title
        meeting.template_used = summary.get("template_used") or template_name
        meeting.attendees = summary.get("attendees") or meeting.attendees
        meeting.category = summary.get("category") or meeting.category
        try:
            self.app.rt.store.update_meeting(meeting)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        self.query_one("#notes-markdown", Markdown).update(meeting.summary)
        self.query_one("#detail-title", Static).update(meeting.title)
        self.notify("Re-summarized.")

    def _retry(self) -> None:
        # `_do_retry` is already `@work`-decorated; call it directly.
        self._do_retry()

    @work(exclusive=True)
    async def _do_retry(self) -> None:
        meeting = self.meeting
        if meeting is None:
            return
        self.notify("Re-transcribing from the saved audio…")
        rt = self.app.rt
        try:
            async with rt.processing_lock:
                result = await asyncio.to_thread(
                    rt.client.transcribe,
                    audio_path=meeting.audio_path,
                    mic_audio_path=meeting.mic_path,
                    me_label=rt.config.user_name,
                    vocabulary=rt.config.custom_vocabulary,
                    diarize=rt.config.diarize,
                )
                transcript = result.get("text", "")
                summary = await asyncio.to_thread(
                    rt.client.summarize,
                    transcript,
                    template_name=rt.config.default_prompt_template,
                    model=rt.config.ollama_model,
                    output_language=rt.config.summary_language,
                    meeting_date=meeting.recorded_at[:10] or None,
                )
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        audio_path, mic_path = meeting.audio_path, meeting.mic_path
        meeting.transcript = transcript
        meeting.status = "done"
        meeting.title = summary.get("title") or meeting.title
        meeting.summary = summary.get("summary", "")
        meeting.template_used = summary.get("template_used") or rt.config.default_prompt_template
        meeting.attendees = summary.get("attendees") or meeting.attendees
        meeting.category = summary.get("category") or meeting.category
        meeting.audio_path = None
        meeting.mic_path = None
        rt.store.update_meeting(meeting)
        for path in (audio_path, mic_path):
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except OSError:
                    pass
        self.notify("Transcript ready.")
        self._load()

    def _export(self) -> None:
        m = self.meeting
        if m is None:
            return
        out = self.app.rt.data_dir / f"{safe_filename(m.title)}-{m.id}.md"
        rendered = (
            f"# {m.title or '(untitled)'}\n\n"
            f"- Recorded: {m.recorded_date()}\n"
            f"- Category: {m.category or '—'}\n"
            f"- Attendees: {', '.join(m.attendees) or '—'}\n"
            f"- Template: {m.template_used or '—'}\n\n"
            f"## Notes\n\n{m.summary}\n"
            f"\n## Transcript\n\n{m.transcript}\n"
        )
        out.write_text(rendered, encoding="utf-8")
        self.notify(f"Exported to {out}", severity="information")

    def _delete_if_yes(self, confirmed: bool) -> None:
        if not confirmed or self.meeting is None:
            return
        self.app.rt.store.delete_meeting(self.meeting.id)
        self.notify("Meeting deleted.")
        self.action_back()