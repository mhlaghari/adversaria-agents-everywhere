"""Keyboard-first meeting dashboard, using the CLI's existing audio and storage.

THESIS: Record, follow the conversation, and return to saved meetings in one place.
OWN-WORLD: Existing terminal cyan, slate panes, explicit text actions and focus.
STORY: Choose Record meeting; watch captions; Stop & save; revisit the transcript.
FIRST VIEWPORT: Persistent action menu beside a spacious reading pane and status bar.
FORM: User-requested tmux-style terminal panes; terminal-native controls and font.
"""

from __future__ import annotations

import asyncio
import queue
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime

from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.data_structures import Point
from prompt_toolkit.document import Document
from prompt_toolkit.filters import has_focus
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import DynamicContainer, HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.mouse_events import MouseEventType
from prompt_toolkit.output.defaults import create_output
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from .audio import Recorder, devices
from .config import CliError
from .copilot import Copilot
from .engine import Engine
from .transcription import speech_key
from .ui import safe

STYLE = Style.from_dict(
    {
        "": "bg:#17212b #e5edf3",
        "header": "bg:#253545 #f2f6fa bold",
        "accent": "#79d4e4 bold",
        "muted": "#b0bdc9",
        "menu": "bg:#1d2b38 #e5edf3",
        "selected": "bg:#79d4e4 #17212b bold",
        "status": "bg:#253545 #e5edf3",
        "error": "bg:#253545 #ffbcad",
        "recording": "#ffbcad bold",
        "text-area": "bg:#17212b #e5edf3",
        "scrollbar.background": "bg:#253545",
        "scrollbar.button": "bg:#79d4e4",
        "dialog": "bg:#253545 #e5edf3",
        "dialog.body": "bg:#253545 #e5edf3",
        "dialog frame.label": "#79d4e4 bold",
        "button.focused": "bg:#79d4e4 #17212b bold",
    }
)


class CopilotWorker:
    """A single daemon request worker: closing the terminal never waits on cloud I/O."""

    def __init__(self):
        self.thread = None
        self.future = None

    def submit(self, function):
        future = Future()

        def run():
            if not future.set_running_or_notify_cancel():
                return
            try:
                future.set_result(function())
            except BaseException as exc:  # noqa: BLE001 - preserve worker errors on its Future.
                future.set_exception(exc)

        self.future = future
        self.thread = threading.Thread(target=run, name="copilot-answer", daemon=True)
        self.thread.start()
        return future

    def shutdown(self, wait=False, cancel_futures=True):
        if cancel_futures and self.future:
            self.future.cancel()
        if wait and self.thread:
            self.thread.join()


class ActionList:
    """A scrollable menu: arrows move, Enter activates, mouse clicks work too."""

    def __init__(self, entries, activate):
        self.entries, self.activate = entries, activate
        self.index = 0
        bindings = KeyBindings()

        @bindings.add("up")
        def up(event):
            self.index = max(0, self.index - 1)

        @bindings.add("down")
        def down(event):
            self.index = min(len(self.entries()) - 1, self.index + 1)

        @bindings.add("enter")
        def enter(event):
            items = self.entries()
            if items:
                self.activate(items[self.index][0])

        self.control = FormattedTextControl(
            self.render,
            focusable=True,
            key_bindings=bindings,
            get_cursor_position=lambda: Point(x=1, y=self.index),
        )
        self.window = Window(self.control, style="class:menu")

    def render(self):
        result = []
        items = self.entries()
        self.index = max(0, min(self.index, len(items) - 1))
        focused = get_app().layout.has_focus(self.control)
        for index, (value, label) in enumerate(items):

            def click(event, index=index, value=value):
                if event.event_type == MouseEventType.MOUSE_UP:
                    self.index = index
                    self.activate(value)

            result.append(
                (
                    "class:selected" if focused and index == self.index else "class:menu",
                    ("> " if focused and index == self.index else "  ") + safe(label) + " \n",
                    click,
                )
            )
        return result


class Dashboard:
    def __init__(
        self, config, store, engine, *, recorder_factory=Recorder, input=None, output=None
    ):
        self.config, self.store, self.engine = config, store, engine
        self.recorder_factory = recorder_factory
        self.workspace = engine.workspace()
        self.recorder = None
        self.phase = "idle"
        self.view = "home"
        self.started_at = 0.0
        self.record_title = ""
        self.live_lines = []
        self.events = queue.SimpleQueue()
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="meeting-audio")
        self.copilot = Copilot()
        self.generation = 0
        self.assistant_worker = CopilotWorker()
        self.assistant_future = None
        self.pending_question = None
        self.suggestions = TextArea(
            text="OpenRouter Copilot is on. Ask aloud, or / then ask QUESTION. Use search QUERY for Exa-backed answers.",
            read_only=True,
            scrollbar=True,
        )
        self.commitments = TextArea(
            text="Spoken commitments appear here.\nNothing runs until you approve it.",
            read_only=True,
            scrollbar=True,
        )
        self.command = TextArea(
            height=1, multiline=False, prompt=" > ", accept_handler=self.submit_command
        )
        self.busy = False
        self.message = "Ready. Choose Record meeting to begin."
        self.error = False
        self.meetings = []
        self.mic = config.values.get("input_device")
        self.system_device = config.values.get("system_device")
        self.body = TextArea(read_only=True, scrollbar=True, focus_on_click=True)
        self.menu = ActionList(self.menu_entries, self.action)
        self.history = ActionList(self.history_entries, self.open_meeting)
        content = HSplit(
            [
                Window(FormattedTextControl(self.heading), height=2),
                DynamicContainer(
                    lambda: (
                        self.history.window
                        if self.view == "history" and self.meetings
                        else self.body
                    )
                ),
            ],
            padding=0,
        )
        side = HSplit(
            [
                Frame(self.suggestions, title="COPILOT · OpenRouter"),
                Frame(self.commitments, title="COMMITMENTS · approve / dismiss"),
            ],
            width=42,
        )
        wide = VSplit(
            [
                Frame(HSplit([self.menu.window], width=25), title="ADVERSARIA"),
                Frame(content, title="MEETING"),
                side,
            ]
        )
        compact = HSplit(
            [
                Frame(content, title="MEETING"),
                VSplit(
                    [
                        Frame(self.suggestions, title="COPILOT"),
                        Frame(self.commitments, title="COMMITMENTS"),
                    ],
                    height=8,
                ),
            ]
        )
        terminal_output = output if output is not None else create_output()
        root = HSplit(
            [
                Window(FormattedTextControl(self.header), height=2, style="class:header"),
                DynamicContainer(
                    lambda: wide if terminal_output.get_size().columns >= 110 else compact
                ),
                Window(FormattedTextControl(self.status), height=2, wrap_lines=True),
                Frame(
                    self.command, title="ask QUESTION · search QUERY (Exa) · approve c1 · / to type"
                ),
                Window(
                    FormattedTextControl(
                        " R Record  S Save  M Meetings  A Audio  K Key  / Ask  Tab Pane  Q Quit"
                    ),
                    height=1,
                    style="class:muted",
                ),
            ]
        )
        self.app = Application(
            layout=Layout(
                root,
                focused_element=self.menu.control
                if terminal_output.get_size().columns >= 110
                else self.body,
            ),
            key_bindings=self.bindings(),
            style=STYLE,
            full_screen=True,
            mouse_support=True,
            refresh_interval=0.25,
            input=input,
            output=terminal_output,
        )
        self.show_home()

    def header(self):
        state = self.phase.upper() if self.phase != "idle" else "MEETINGS"
        if self.phase == "recording":
            elapsed = int(time.monotonic() - self.started_at)
            state += f"  {elapsed // 60:02}:{elapsed % 60:02}"
        return [
            ("class:accent", " ADVERSARIA"),
            ("", "  /  " + safe(self.workspace["name"]) + "\n "),
            ("class:recording" if self.phase != "idle" else "class:muted", state),
        ]

    def heading(self):
        title = {
            "home": "Your meeting companion",
            "live": "Live transcript",
            "history": "Previous meetings",
            "detail": "Saved meeting",
        }[self.view]
        focused = (
            self.app.layout.has_focus(self.history.control)
            if self.view == "history" and self.meetings
            else self.app.layout.has_focus(self.body)
        )
        hint = (
            "  |  Arrows + Enter to open"
            if self.view == "history"
            else "  |  Arrows / PgUp / PgDn to scroll"
        )
        return [("class:accent", " " + title), ("class:muted", hint if focused else ""), ("", "\n")]

    def status(self):
        return [("class:error" if self.error else "class:status", " " + safe(self.message))]

    def set_status(self, message, *, error=False):
        self.message, self.error = message, error
        self.app.invalidate()

    def set_body(self, text, *, follow=False):
        text = safe(text)
        position = len(text) if follow else min(self.body.buffer.cursor_position, len(text))
        self.body.buffer.set_document(Document(text, position), bypass_readonly=True)

    def menu_entries(self):
        return [
            ("record", "[R] Live transcript" if self.recorder else "[R] Record meeting"),
            ("stop", "[S] Stop & save" if self.recorder else "[S] Stop (inactive)"),
            ("meetings", "[M] Previous meetings"),
            ("audio", "[A] Audio inputs"),
            ("key", "[K] Speech API key"),
            ("shell", "[:] Command shell"),
            ("quit", "[Q] Quit"),
        ]

    def history_entries(self):
        return [(m["id"], f"{self.local_time(m['created'])}  {m['title']}") for m in self.meetings]

    @staticmethod
    def local_time(created):
        return datetime.fromisoformat(created).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    def bindings(self):
        bindings = KeyBindings()
        for key, action in (
            ("r", "record"),
            ("s", "stop"),
            ("m", "meetings"),
            ("a", "audio"),
            ("k", "key"),
            (":", "shell"),
            ("q", "quit"),
        ):
            bindings.add(key, filter=~has_focus(self.command))(
                lambda event, action=action: self.action(action)
            )

        @bindings.add("/", filter=~has_focus(self.command))
        def focus_command(event):
            self.app.layout.focus(self.command)

        @bindings.add("tab")
        @bindings.add("s-tab")
        def switch(event):
            panes = [
                self.history.control
                if self.view == "history" and self.meetings
                else self.body.control,
                self.suggestions.control,
                self.commitments.control,
                self.command.control,
            ]
            if self.app.output.get_size().columns >= 110:
                panes.insert(0, self.menu.control)
            current = self.app.layout.current_control
            self.app.layout.focus(
                panes[(panes.index(current) + 1) % len(panes)] if current in panes else panes[0]
            )

        @bindings.add("escape")
        def back(event):
            if self.view == "detail":
                self.show_meetings()
            else:
                self.focus_reader()

        @bindings.add("c-c")
        @bindings.add("c-d")
        def interrupt(event):
            self.action("stop" if self.recorder else "quit")

        return bindings

    def show_home(self):
        self.view = "home"
        provider = self.config.values["speech_provider"]
        self.set_body(
            "\n Record meeting\n"
            " Capture your microphone and follow the live transcript here.\n\n"
            " Previous meetings\n"
            " Read the transcripts and notes saved in this workspace.\n\n"
            " Use arrow keys + Enter, click an action, or press its shortcut.\n"
            " Tab switches panes. Arrow keys / Page Up / Page Down scroll.\n\n"
            f" Audio is sent to {provider} for transcription.\n"
            " Captions arrive after speech pauses and provider processing.\n"
            " Choose Audio inputs to change the microphone or add a loopback.\n"
            " Copilot suggests answers to spoken questions. Use / to ask or approve a commitment."
        )

    def show_live(self):
        self.view = "live"
        self.set_body(
            "\n".join(self.live_lines)
            if self.live_lines
            else "Listening… Speak into your microphone.\n\n"
            "The first caption appears after a pause and provider processing.\n"
            "Press S to stop and save. You can browse meetings while recording.",
            follow=True,
        )
        self.focus_reader()

    def focus_reader(self):
        self.app.layout.focus(
            self.history.control if self.view == "history" and self.meetings else self.body
        )

    def show_meetings(self):
        self.meetings = self.store.rows(
            "SELECT id,title,created FROM meetings WHERE workspace_id=? ORDER BY id DESC",
            (self.workspace["id"],),
        )
        self.view = "history"
        self.history.index = 0
        if self.meetings:
            self.app.layout.focus(self.history.control)
        else:
            self.set_body("\n No saved meetings yet.\n\n Press R to record your first meeting.")
            self.focus_reader()

    def open_meeting(self, mid):
        meeting = self.store.get_meeting(mid)
        self.view = "detail"
        self.body.buffer.cursor_position = 0
        self.set_body(
            f"{meeting['title']}\n{self.local_time(meeting['created'])}\n\n"
            + (f"NOTES\n{meeting['summary']}\n\n" if meeting["summary"] else "")
            + f"TRANSCRIPT\n\n{meeting['transcript']}\n\nEsc returns to Previous meetings."
        )
        self.focus_reader()

    def action(self, action):
        if action == "meetings":
            self.show_meetings()
        elif action == "record" and self.recorder:
            self.show_live()
        elif self.busy:
            self.set_status("Please wait for the current operation to finish.")
        else:
            self.busy = True
            self.app.create_background_task(self.perform(action))

    async def perform(self, action):
        try:
            if action == "record":
                await self.start_recording()
            elif action == "stop":
                if self.recorder:
                    await self.stop_recording()
                else:
                    self.set_status("No recording is active. Press R to begin.")
            elif action in {"quit", "shell"}:
                if self.recorder and self.phase != "stopped" and not await self.stop_recording():
                    return
                self.app.exit(result=action)
            elif action == "audio":
                await self.choose_audio()
            elif action == "key":
                await self.configure_key()
        except Exception as exc:  # noqa: BLE001 - keep audio running after a UI action fails.
            self.set_status(str(exc) or type(exc).__name__, error=True)
        finally:
            self.busy = False

    async def start_recording(self):
        try:
            speech_key(self.config)
        except CliError as exc:
            raise CliError(
                f"Add your {self.config.values['speech_provider']} speech key with K, then press R."
            ) from exc
        self.phase = "starting"
        self.set_status("Opening audio input…")
        # Prior capture has stopped; consume its final queued captions before resetting.
        self.drain_events()
        self.live_lines = []
        self.generation += 1
        self.pending_question = None
        self.copilot.pending.clear()
        self.copilot.turns.clear()
        self.record_title = "Meeting · " + datetime.now(UTC).astimezone().strftime(
            "%d %b %Y, %H:%M"
        )
        self.started_at = time.monotonic()
        try:
            self.recorder = self.recorder_factory(
                self.config,
                lambda text, source="Me", boundary="silence": self.events.put(
                    ("caption", source, (text, boundary))
                ),
                lambda text: self.events.put(("notice", "", text)),
                self.mic,
                self.system_device,
            )
            await self.audio_job(self.recorder.start)
        except Exception:
            self.recorder = None
            self.phase = "idle"
            raise
        self.phase = "recording"
        self.show_live()
        self.set_status("Recording. S stops and saves; Q saves before quitting.")

    def finish_recording(self):
        """Only remove audio after a nonempty transcript has been saved successfully."""
        recorder = self.recorder
        recorder.stop()
        text = "\n".join(line for _, line in sorted(recorder.transcript))
        if not text.strip():
            self.recorder = None
            raise CliError(f"No speech was transcribed. Audio preserved at {recorder.directory}.")
        mid = self.store.meeting(
            self.workspace["id"],
            self.record_title + (" [partial]" if recorder.errors else ""),
            text,
        )
        self.recorder = None
        if not recorder.errors:
            try:
                recorder.cleanup()
            except OSError as exc:
                recorder.errors.append(f"Transcript saved; could not remove audio: {exc}")
        return mid, recorder.errors, recorder.directory

    async def audio_job(self, function):
        return await asyncio.get_running_loop().run_in_executor(self.worker, function)

    async def stop_recording(self):
        recorder = self.recorder
        self.phase = "saving"
        self.set_status("Stopping capture and waiting for the final caption…")
        try:
            mid, errors, directory = await self.audio_job(self.finish_recording)
        except Exception as exc:  # noqa: BLE001 - retain the recorder so saving can be retried.
            self.phase = "stopped" if self.recorder else "idle"
            message = f"{exc}\nAudio preserved at {recorder.directory}.\n" + (
                "S retries saving; Q exits." if self.recorder else "Press R to try a new recording."
            )
            self.drain_events()
            self.view = "live"
            self.set_body("\n".join(self.live_lines) + "\n\n" + message, follow=True)
            self.set_status(
                "Could not save a complete meeting. See the transcript pane.", error=True
            )
            return False
        self.phase = "idle"
        self.drain_events()
        self.open_meeting(mid)
        self.set_status(
            f"Saved meeting {mid}."
            + (f" Partial transcript; audio preserved at {directory}." if errors else ""),
            error=bool(errors),
        )
        return True

    async def choose_audio(self):
        if self.recorder:
            self.set_status("Stop and save the recording before changing audio inputs.")
            return
        self.set_status("Looking for audio inputs…")
        inputs = await self.audio_job(devices)
        values = [("default", "System default microphone")] + [
            (d["id"], safe(d["name"])) for d in inputs
        ]
        mic = await radiolist_dialog(
            title="Microphone",
            text="Choose the microphone for your next meeting.",
            values=values,
            default=self.mic if self.mic is not None else "default",
            style=STYLE,
        ).run_async()
        if mic is None:
            self.set_status("Audio inputs unchanged.")
            return
        loopback = await radiolist_dialog(
            title="Other side of the call",
            text="Optional loopback INPUT. Route your call output to it first (e.g. BlackHole).",
            values=[("none", "Microphone only")] + values[1:],
            default=self.system_device if self.system_device is not None else "none",
            style=STYLE,
        ).run_async()
        if loopback is None:
            self.set_status("Audio inputs unchanged.")
            return
        self.mic = None if mic == "default" else mic
        self.system_device = None if loopback == "none" else loopback
        if self.mic is not None and self.mic == self.system_device:
            self.mic = self.config.values.get("input_device")
            self.system_device = self.config.values.get("system_device")
            raise CliError("Choose different microphone and loopback inputs.")
        self.config.save(input_device=self.mic, system_device=self.system_device)
        self.set_status("Audio inputs saved for your next recording.")

    async def configure_key(self):
        if self.recorder:
            self.set_status("Stop and save the recording before changing the speech key.")
            return
        provider = self.config.values["speech_provider"]
        value = await input_dialog(
            title=f"{provider} speech key",
            text="Paste your API key. Input is hidden; leave blank to keep the current key.",
            password=True,
            style=STYLE,
        ).run_async()
        if value and value.strip():
            self.config.save_key(provider, value.strip())
            self.set_status("Speech key saved. Press R to record a meeting.")
        else:
            self.set_status("Speech key unchanged.")

    @staticmethod
    def set_panel(panel, text):
        text = safe(text)
        panel.buffer.set_document(Document(text, len(text)), bypass_readonly=True)

    def refresh_commitments(self):
        cards = list(self.copilot.commitments.values())[-6:]
        self.set_panel(
            self.commitments,
            "\n\n".join(
                f"{c.id} · {c.kind} · {c.status}\n{c.text}\n"
                + (f"Task {c.task_id} queued" if c.task_id else f"approve {c.id} / dismiss {c.id}")
                for c in cards
            ),
        )

    def ask(self, question, web=False):
        if self.assistant_future is not None and not self.assistant_future.done():
            self.pending_question = (question, web)
            self.set_status("Copilot is answering; the newest question is queued.")
            return
        generation = self.generation
        turns = list(self.copilot.turns)
        self.events.put(("answer_start", generation, ("Exa search · " if web else "") + question))

        def answer():
            tokens = None
            try:
                tokens = Engine(self.config, self.store).answer(
                    question,
                    self.workspace["name"],
                    turns,
                    provider="openrouter",
                    model=self.config.values.get("copilot_model", "google/gemini-2.5-flash-lite"),
                    web=web,
                )
                for token in tokens:
                    if generation != self.generation:
                        break
                    self.events.put(("answer_token", generation, token))
            except (CliError, OSError, ValueError) as exc:
                self.events.put(("answer_error", generation, str(exc)))
            finally:
                if tokens is not None:
                    tokens.close()

        self.assistant_future = self.assistant_worker.submit(answer)

    def submit_command(self, buffer):
        command, _, value = buffer.text.strip().partition(" ")
        try:
            if command in {"ask", "search"} and value:
                self.ask(value, web=command == "search")
            elif command in {"approve", "dismiss"}:
                caught = self.copilot.commitments.get(value.strip())
                if not caught or caught.status != "caught":
                    raise CliError("Choose an unapproved commitment, for example: approve c1")
                if command == "dismiss":
                    caught.status = "dismissed"
                else:
                    caught.task_id = self.store.add_task(
                        self.workspace["id"],
                        caught.text,
                        caught.kind,
                        f"Caught live · {caught.source}",
                        False,
                        caught.origin,
                    )
                    caught.status = "approved"
                    self.set_status(
                        f"Task {caught.task_id} queued. Use Command shell → work to run it."
                    )
                self.refresh_commitments()
            elif command:
                raise CliError("Use ask QUESTION, search QUERY (Exa), approve c1, or dismiss c1.")
        except (CliError, OSError, ValueError) as exc:
            self.set_status(str(exc), error=True)
        self.focus_reader()
        return False

    def drain_events(self):
        changed = False
        while not self.events.empty():
            kind, source, text = self.events.get_nowait()
            if kind == "caption":
                text, boundary = text if isinstance(text, tuple) else (text, "silence")
                caught, question = self.copilot.feed(text, source, boundary)
                if caught:
                    self.refresh_commitments()
                if question:
                    self.ask(question)
                if not text.strip():
                    continue
                elapsed = max(0, int(time.monotonic() - self.started_at))
                self.live_lines.append(f"{elapsed // 60:02}:{elapsed % 60:02}  {source}\n{text}\n")
                changed = True
            elif kind == "answer_start" and source == self.generation:
                self.set_panel(self.suggestions, text + "\n\nThinking…")
            elif kind == "answer_token" and source == self.generation:
                current = self.suggestions.text.replace("Thinking…", "")
                self.set_panel(self.suggestions, current + text)
            elif kind == "answer_error" and source == self.generation:
                self.set_panel(self.suggestions, "Copilot: " + text)
            elif kind == "notice":
                self.set_status(text, error=True)
        if changed and self.view == "live":
            # Preserve the reader's place when they scroll back during a meeting.
            follow = self.body.buffer.cursor_position == len(self.body.text)
            self.set_body("\n".join(self.live_lines), follow=follow)

    async def monitor(self):
        while True:
            self.drain_events()
            if self.pending_question and (
                self.assistant_future is None or self.assistant_future.done()
            ):
                question, self.pending_question = self.pending_question, None
                self.ask(*question)
            if self.recorder and self.phase == "recording" and self.recorder.stop_event.is_set():
                self.action("stop")
            await asyncio.sleep(0.1)

    def run(self):
        try:
            return self.app.run(pre_run=lambda: self.app.create_background_task(self.monitor()))
        finally:
            # An interrupted await does not cancel a running audio thread. Join it first.
            self.worker.shutdown(wait=True, cancel_futures=True)
            self.generation += 1
            self.assistant_worker.shutdown(wait=False, cancel_futures=True)
            # EOF / terminal closure must also stop capture and retain recoverable audio.
            if self.recorder:
                recorder = self.recorder
                try:
                    self.finish_recording()
                except Exception as exc:
                    raise CliError(f"{exc} Audio preserved at {recorder.directory}.") from exc
