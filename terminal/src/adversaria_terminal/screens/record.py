"""Record screen: dual capture (system + mic) with live captions."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, RichLog, Static

from ..audio import RecordingSession, available_sources
from ..models import Meeting
from .base import BaseScreen


class RecordScreen(BaseScreen):
    """Start/stop a recording and watch captions stream in live."""

    BINDINGS = [
        ("space", "toggle", "Start/Stop"),
    ]

    CSS = """
    RecordScreen {
        align: center top;
    }
    #record-top {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #record-timer {
        text-style: bold;
        color: $accent;
    }
    #record-status {
        color: $text-muted;
    }
    #source-row {
        height: 1fr;
        width: 100%;
        padding: 0 1;
    }
    .source-col {
        width: 1fr;
        height: 1fr;
        border: round $primary;
        margin: 0 1;
    }
    .source-header {
        text-style: bold;
        padding: 0 1;
    }
    .source-log {
        height: 1fr;
        border: none;
    }
    .source-partial {
        color: $text-muted;
        text-style: italic;
        height: 3;
        padding: 0 1;
        border-top: solid $primary;
    }
    #record-controls {
        width: 100%;
        height: auto;
        padding: 0 2 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Horizontal(
                Static("", id="record-timer"),
                Static("", id="record-status"),
            ),
            id="record-top",
        )
        # Controls sit right below the status row, before the caption panels,
        # so Start recording is reachable without scrolling past the (often
        # tall) live-caption area first.
        yield Horizontal(
            Button("Start recording", id="record-toggle", variant="primary"),
            Button("Back", id="record-back", variant="default"),
            id="record-controls",
        )
        yield Horizontal(
            Vertical(
                Static("System audio (Them)", classes="source-header"),
                RichLog(id="them-captions", classes="source-log", wrap=True, markup=True),
                Static("", classes="source-partial", id="them-partial"),
                id="them-col",
                classes="source-col",
            ),
            Vertical(
                Static("Microphone (Me)", classes="source-header"),
                RichLog(id="me-captions", classes="source-log", wrap=True, markup=True),
                Static("", classes="source-partial", id="me-partial"),
                id="me-col",
                classes="source-col",
            ),
            id="source-row",
        )

    def on_mount(self) -> None:
        self.recording = False
        self.session: RecordingSession | None = None
        self.recording_epoch = 0
        self._t0 = 0.0
        self._timer = None
        self._them_enabled = False
        self._me_enabled = False
        self._them_name: str | None = None
        self._me_name: str | None = None
        self.run_worker(self._refresh_sources(), name="record-sources")

    async def _refresh_sources(self) -> None:
        sources, reason = await asyncio.to_thread(available_sources)
        names = {s.kind: s.device_name for s in sources}
        self._them_name = names.get("them")
        self._me_name = names.get("me")
        self._them_enabled = self._them_name is not None
        self._me_enabled = self._me_name is not None
        if reason and not sources:
            self.notify(f"Audio capture unavailable: {reason}", severity="warning")
        self._update_headers()
        if not (self._them_enabled or self._me_enabled):
            self.query_one("#record-toggle", Button).disabled = True
            self.query_one("#record-status", Static).update(
                "No capture device found — use ctrl+i Import instead."
            )

    def _update_headers(self) -> None:
        for kind, name in (("them", self._them_name), ("me", self._me_name)):
            if name:
                self.query_one(f"#{kind}-col .source-header", Static).update(
                    f"{'System audio (Them)' if kind == 'them' else 'Microphone (Me)'}  ·  {name}"
                )
            else:
                self.query_one(f"#{kind}-col .source-header", Static).update(
                    f"{'System audio (Them)' if kind == 'them' else 'Microphone (Me)'}  ·  [red]no device[/red]"
                )

    def on_show(self) -> None:
        if not getattr(self, "recording", False):
            self.run_worker(self._refresh_sources(), name="record-sources")

    def action_toggle(self) -> None:
        toggle = self.query_one("#record-toggle", Button)
        if not toggle.disabled:
            toggle.press()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "record-toggle":
            if self.recording:
                self._stop_recording()
            else:
                self._start_recording()
        elif event.button.id == "record-back":
            self.action_back()

    # ------------------------------------------------------------------
    # Recording lifecycle
    # ------------------------------------------------------------------

    def _start_recording(self) -> None:
        if self.recording or self.session:
            return
        if not (self._them_enabled or self._me_enabled):
            self.notify("No capture device available.", severity="warning")
            return
        audio_dir = self.app.rt.data_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        self.recording_epoch += 1
        self.session = RecordingSession(
            audio_dir, them=self._them_enabled, me=self._me_enabled
        )
        warnings = self.session.start()
        self.recording = True
        self._t0 = time.time()
        self.query_one("#them-captions", RichLog).clear()
        self.query_one("#me-captions", RichLog).clear()
        self.query_one("#them-partial", Static).update("")
        self.query_one("#me-partial", Static).update("")
        self.query_one("#record-toggle", Button).label = "Stop recording"
        self.query_one("#record-status", Static).update(
            "Capturing… live captions appear as the transcription engine allows."
        )
        for w in warnings:
            self.notify(w, severity="warning")
        self._timer = self.set_interval(1.0, self._tick_timer, name="record-timer")
        # `_live_loop` is already `@work`-decorated — calling it starts the
        # worker and returns a `Worker` object. Wrapping that call in
        # `run_worker()` again (the old code) fed that `Worker` object back in
        # as the "work" for a second worker, which is neither a coroutine,
        # awaitable, nor callable — Textual raised `WorkerError("Unsupported
        # attempt to run an async worker")` the instant recording started,
        # which is why captions never appeared no matter how much you talked.
        self._live_loop()

    def _tick_timer(self) -> None:
        if not self.recording:
            return
        elapsed = int(time.time() - self._t0)
        mm, ss = divmod(elapsed, 60)
        self.query_one("#record-timer", Static).update(f"[{mm:02d}:{ss:02d}]")

    @work(exclusive=True)
    async def _live_loop(self) -> None:
        """Tail deltas of both capture streams and feed them to /live_feed."""
        them_off = 0
        me_off = 0
        audio_dir = self.app.rt.data_dir / "audio"
        them_wav = audio_dir / "live_them.wav"
        me_wav = audio_dir / "live_me.wav"
        epoch = self.recording_epoch
        while self.recording and self.recording_epoch == epoch:
            session = self.session
            if session is None:
                break
            try:
                if self._them_enabled:
                    wrote, them_off = await asyncio.to_thread(
                        session.system_buffer.snapshot_since, them_wav, them_off
                    )
                    if wrote:
                        await self._feed("them", them_wav, epoch)
                if self._me_enabled:
                    wrote, me_off = await asyncio.to_thread(
                        session.mic_buffer.snapshot_since, me_wav, me_off
                    )
                    if wrote:
                        await self._feed("me", me_wav, epoch)
                await asyncio.sleep(0.8)
            except Exception as exc:
                self.notify(f"Live captions: {exc}", severity="error")
                break

    async def _feed(self, source: str, wav: Path, epoch: int) -> None:
        def call() -> tuple[list[str], str]:
            captions, _boundaries, partial = self.app.rt.client.live_feed(
                str(wav), epoch, source
            )
            return captions, partial

        captions, partial = await asyncio.to_thread(call)
        if captions:
            log = self.query_one(f"#{source}-captions", RichLog)
            color = "#6fd" if source == "them" else "#fd9"
            stamp = datetime.now().strftime("%H:%M:%S")
            for cap in captions:
                log.write(f"[{stamp}] [{color}]{cap}[/]")
        el = self.query_one(f"#{source}-partial", Static)
        el.update(f"[dim italic]{partial}[/]" if partial else "")

    def _stop_recording(self) -> None:
        if not self.recording or self.session is None:
            return
        session = self.session
        self.recording = False
        if self._timer:
            self._timer.stop()
            self._timer = None
        session.stop()
        elapsed = time.time() - self._t0
        self.query_one("#record-toggle", Button).label = "Processing…"
        self.query_one("#record-status", Static).update("Transcribing & summarizing…")

        meeting = Meeting(
            title="Untitled",
            source="recorded",
            status="pending",
            audio_path=(
                str(session.system_path)
                if session.them and session.system_path is not None
                else None
            ),
            mic_path=(
                str(session.mic_path)
                if session.me and session.mic_path is not None
                else None
            ),
            duration_seconds=elapsed,
            recorded_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        )
        try:
            meeting = self.app.rt.store.add_meeting(meeting)
        except Exception as exc:
            self.notify(f"Could not save meeting row: {exc}", severity="error")
            return
        self.session = None
        # Same double-worker mistake as `_live_loop` above — `_process` is
        # `@work`-decorated already, so just call it.
        self._process(meeting.id)

    @work(exclusive=True)
    async def _process(self, meeting_id: int) -> None:
        """Transcribe + summarize the recorded audio, then open the meeting."""
        rt = self.app.rt
        meeting = rt.store.get_meeting(meeting_id)
        if meeting is None:
            return
        audio_path = meeting.audio_path
        mic_path = meeting.mic_path
        if rt.processing_lock.locked():
            self.query_one("#record-status", Static).update(
                "Queued — waiting for the previous recording to finish processing…"
            )
        try:
            async with rt.processing_lock:
                self.query_one("#record-status", Static).update(
                    "Transcribing & summarizing…"
                )
                result = await asyncio.to_thread(
                    rt.client.transcribe,
                    audio_path=audio_path,
                    mic_audio_path=mic_path,
                    me_label=rt.config.user_name,
                    vocabulary=rt.config.custom_vocabulary,
                    diarize=rt.config.diarize,
                )
                transcript = result.get("text", "")
                self.query_one("#record-status", Static).update(
                    "Summarizing with the local LLM…"
                )
                summary = await asyncio.to_thread(
                    rt.client.summarize,
                    transcript,
                    template_name=rt.config.default_prompt_template,
                    model=rt.config.ollama_model,
                    output_language=rt.config.summary_language,
                    meeting_date=meeting.recorded_at[:10] or None,
                )
        except Exception as exc:
            meeting.status = "needs_transcribe"
            rt.store.update_meeting(meeting)
            self.query_one("#record-status", Static).update("Transcription unavailable.")
            self.notify(str(exc), severity="error")
            self.open_meeting(meeting.id)
            return

        meeting.title = summary.get("title") or "Untitled"
        meeting.summary = summary.get("summary", "")
        meeting.transcript = transcript
        meeting.language = result.get("language", "")
        meeting.duration_seconds = result.get("duration_seconds", meeting.duration_seconds)
        meeting.template_used = summary.get("template_used") or rt.config.default_prompt_template
        meeting.category = summary.get("category") or ""
        meeting.attendees = summary.get("attendees") or []
        meeting.status = "done"
        meeting.audio_path = None
        meeting.mic_path = None
        rt.store.update_meeting(meeting)
        # audio never outlives a successful transcription
        for path in (audio_path, mic_path):
            if path:
                try:
                    Path(path).unlink(missing_ok=True)
                except OSError:
                    pass
        rt.store.set_setting("last_meeting_id", str(meeting.id))
        self.notify("Notes ready.", severity="information")
        self.open_meeting(meeting.id)

    def action_back(self) -> None:
        if self.recording:
            self._stop_recording()
            return
        if self.session is not None:
            self.session.stop()
            self.session = None
        self.app.pop_screen()