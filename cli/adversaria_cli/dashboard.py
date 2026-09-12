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
from prompt_toolkit.application import create_app_session, get_app, in_terminal
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
from .copilot import QUESTION, Copilot
from .engine import Engine
from .transcription import speech_key
from .ui import safe
from .workspace_dashboard import WorkspaceDashboard

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


class Dashboard(WorkspaceDashboard):
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
        self.workspace_sessions = {}
        self.workspaces = []
        self.tasks = []
        self.selected_task = None
        self.task_state = None
        self.task_has_artifact = False
        self.running_task = None
        self.task_text = ""
        self.task_future = None
        self.task_cancel = threading.Event()
        self.task_worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="workspace-task")
        self.suggestions = TextArea(
            text="Ask aloud or type a question. Exa looks up outside information automatically. Use search QUERY to force a lookup, or ask --no-web QUESTION to skip it.",
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
        self.workspace_list = ActionList(self.workspace_entries, self.select_workspace)
        self.task_list = ActionList(self.task_entries, self.open_task)
        self.workspace_panel = HSplit(
            [
                HSplit(
                    [self.workspace_list.window],
                    height=lambda: min(
                        7, len(self.workspaces) + 1, max(2, self.app.output.get_size().rows - 21)
                    ),
                ),
                Window(height=1, char="─", style="class:muted"),
                self.body,
            ]
        )
        content = HSplit(
            [
                Window(FormattedTextControl(self.heading), height=2),
                DynamicContainer(self.reader_container),
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
                Frame(content, title=self.content_title),
                side,
            ]
        )
        compact = HSplit(
            [
                Frame(content, title=self.content_title),
                VSplit(
                    [
                        Frame(self.suggestions, title="COPILOT"),
                        Frame(self.commitments, title="COMMITMENTS"),
                    ],
                    height=lambda: 5 if terminal_output.get_size().rows < 28 else 8,
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
                    self.command, title="/ Command · ask · search · new · run · approve · H Help"
                ),
                Window(
                    FormattedTextControl(self.shortcuts),
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

    def content_title(self):
        if self.view in {"workspaces", "source"}:
            return "WORKSPACE"
        if self.view in {"task", "tasks"}:
            return "TASKS · OpenRouter"
        return "MEETING"

    def reader_container(self):
        if self.view == "history" and self.meetings:
            return self.history.window
        if self.view == "workspaces":
            return self.workspace_panel
        if self.view == "tasks":
            return self.task_list.window
        return self.body

    def reader_control(self):
        if self.view == "history" and self.meetings:
            return self.history.control
        if self.view == "workspaces":
            return self.workspace_list.control
        if self.view == "tasks":
            return self.task_list.control
        return self.body.control

    def shortcuts(self):
        if self.view == "task":
            actions = {
                "queued": " G Run  E Edit brief",
                "failed": " G Retry  E Edit brief",
                "awaiting_review": " V Approve  E Revise",
                "running": " X Cancel run" if self.selected_task == self.running_task else "",
                "done": " Approved",
            }.get(self.task_state, "")
            preview = "  O Preview" if self.task_has_artifact else ""
            return actions + preview + "  T Tasks  / Command  H Help  Q Quit"
        if self.view in {"workspaces", "source"}:
            return (
                " W Spaces  F Attach  I Guide  P Pause  T Tasks  / Type  H Help  Q Quit"
                if self.app.output.get_size().columns < 90
                else " W Spaces  F Attach  I Instructions  P Pause  T Tasks  / Command  H Help  Q Quit"
            )
        return " R Record  S Save  M Meetings  W Spaces  T Tasks  N New  / Ask  H Help  Q Quit"

    def header(self):
        state = self.phase.upper() if self.phase != "idle" else "READY"
        if self.phase == "recording":
            elapsed = int(time.monotonic() - self.started_at)
            state += f"  {elapsed // 60:02}:{elapsed % 60:02}"
        if self.task_active:
            state += f"  ·  TASK {self.running_task} " + (
                "CANCELLING" if self.task_cancel.is_set() else "RUNNING"
            )
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
            "workspaces": "Workspaces",
            "tasks": "Workspace tasks",
            "task": "Task & artifact",
            "source": "Attached context",
            "help": "Keyboard & commands",
        }[self.view]
        focused = self.app.layout.has_focus(self.reader_control())
        hint = (
            "  |  Arrows + Enter to open"
            if self.view in {"history", "workspaces", "tasks"}
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
        entries = [
            ("record", "[R] Live transcript" if self.recorder else "[R] Record meeting"),
            ("stop", "[S] Stop & save" if self.recorder else "[S] Stop (inactive)"),
            ("meetings", "[M] Previous meetings"),
            ("workspaces", "[W] Workspaces"),
            ("tasks", "[T] Workspace tasks"),
            ("new_task", "[N] New task"),
        ]
        if self.view in {"workspaces", "source"}:
            entries += [
                ("attach", "[F] Attach context"),
                ("instructions", "[I] Instructions"),
                ("pause", "[P] Pause / resume"),
            ]
        if self.view == "task":
            if self.task_has_artifact:
                entries.append(("preview_task", "[O] Open preview"))
            if self.task_state in {"queued", "failed"}:
                entries.append(("run_task", "[G] Run / retry"))
            if self.task_state == "awaiting_review":
                entries.append(("approve_task", "[V] Approve draft"))
            if self.task_state in {"queued", "failed", "awaiting_review"}:
                entries.append(("revise_task", "[E] Edit / revise"))
        if self.task_active:
            entries.append(("cancel_task", "[X] Cancel task run"))
        return entries + [
            ("audio", "[A] Audio inputs"),
            ("key", "[K] Speech API key"),
            ("shell", "[:] Command shell"),
            ("help", "[H] Help"),
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
            ("w", "workspaces"),
            ("t", "tasks"),
            ("n", "new_task"),
            ("f", "attach"),
            ("i", "instructions"),
            ("p", "pause"),
            ("g", "run_task"),
            ("o", "preview_task"),
            ("v", "approve_task"),
            ("e", "revise_task"),
            ("x", "cancel_task"),
            ("h", "help"),
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
                self.reader_control(),
                self.suggestions.control,
                self.commitments.control,
                self.command.control,
            ]
            if self.view == "workspaces":
                panes.insert(1, self.body.control)
            if self.app.output.get_size().columns >= 110:
                panes.insert(0, self.menu.control)
            current = self.app.layout.current_control
            direction = -1 if event.key_sequence[0].key == "s-tab" else 1
            self.app.layout.focus(
                panes[(panes.index(current) + direction) % len(panes)]
                if current in panes
                else panes[0]
            )

        @bindings.add("escape")
        def back(event):
            if self.view == "detail":
                self.show_meetings()
            elif self.view == "task":
                self.show_tasks()
            elif self.view == "source":
                self.show_workspaces()
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
            " Workspaces & tasks\n"
            " Press W to choose a workspace and attach context.\n"
            " Press T to browse tasks, or N to create a draft, research brief or diagram.\n\n"
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
        self.app.layout.focus(self.reader_control())

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
        elif action == "workspaces":
            self.show_workspaces()
        elif action == "tasks":
            self.show_tasks()
        elif action == "help":
            self.show_help()
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
                await self.finish_workspace_task()
                self.app.exit(result=action)
            elif action == "new_workspace":
                await self.workspace_dialog()
            elif action == "attach":
                await self.attachment_dialog()
            elif action == "instructions":
                await self.instructions_dialog()
            elif action == "pause":
                self.pause_workspace()
            elif action == "new_task":
                await self.new_task_dialog()
            elif action == "run_task":
                self.run_workspace_task()
            elif action == "preview_task":
                await self.preview_task()
            elif action == "approve_task":
                self.approve_task()
            elif action == "revise_task":
                await self.revise_task_dialog()
            elif action == "cancel_task":
                self.cancel_workspace_task()
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
        mic = await self.dialog(
            radiolist_dialog,
            title="Microphone",
            text="Choose the microphone for your next meeting.",
            values=values,
            default=self.mic if self.mic is not None else "default",
        )
        if mic is None:
            self.set_status("Audio inputs unchanged.")
            return
        loopback = await self.dialog(
            radiolist_dialog,
            title="Other side of the call",
            text="Optional loopback INPUT. Route your call output to it first (e.g. BlackHole).",
            values=[("none", "Microphone only")] + values[1:],
            default=self.system_device if self.system_device is not None else "none",
        )
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
        value = await self.dialog(
            input_dialog,
            title=f"{provider} speech key",
            text="Paste your API key. Input is hidden; leave blank to keep the current key.",
            password=True,
        )
        if value and value.strip():
            self.config.save_key(provider, value.strip())
            self.set_status("Speech key saved. Press R to record a meeting.")
        else:
            self.set_status("Speech key unchanged.")

    async def dialog(self, factory, **kwargs):
        # Suspend parent rendering and input; recording and task workers keep running.
        async with in_terminal():
            with create_app_session(input=self.app.input, output=self.app.output):
                return await factory(style=self.app.style, **kwargs).run_async()

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
                + (
                    f"Task {c.task_id} · T to view"
                    if c.task_id
                    else f"approve {c.id} / dismiss {c.id}"
                )
                for c in cards
            )
            or "Spoken commitments appear here.\nApprove a commitment to queue a task.",
        )

    def ask(self, question, web=None):
        if self.assistant_future is not None and not self.assistant_future.done():
            self.pending_question = (question, web)
            self.set_status("Copilot is answering; the newest question is queued.")
            return
        generation = self.generation
        turns = list(self.copilot.turns)
        workspace_name = self.workspace["name"]
        self.events.put(("answer_start", generation, ("Exa search · " if web else "") + question))

        def answer():
            tokens = None
            try:
                tokens = Engine(self.config, self.store).answer(
                    question,
                    workspace_name,
                    turns,
                    provider="openrouter",
                    model=self.config.values.get("copilot_model", "google/gemini-2.5-flash-lite"),
                    web=web,
                    on_status=lambda status: self.events.put(
                        ("answer_status", generation, (question, status))
                    ),
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
            if self.workspace_command(command, value):
                pass
            elif command in {"ask", "search"} and value:
                web = True if command == "search" else None
                if command == "ask":
                    for flag, enabled in (("--no-web", False), ("--web", True)):
                        if value.startswith(flag + " "):
                            value, web = value[len(flag) :].strip(), enabled
                            break
                        if value.endswith(" " + flag):
                            value, web = value[: -len(flag)].strip(), enabled
                            break
                self.ask(value, web=web)
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
                        f"Task {caught.task_id} queued. Press T, open it, then G to run."
                    )
                    if self.view == "tasks":
                        self.refresh_tasks()
                self.refresh_commitments()
            elif command and (
                QUESTION.match(buffer.text.strip()) or buffer.text.rstrip().endswith("?")
            ):
                self.ask(buffer.text.strip())
            elif command:
                raise CliError(
                    "Type a question or command. H opens help; T opens tasks; W opens workspaces."
                )
        except (CliError, OSError, ValueError) as exc:
            self.set_status(str(exc), error=True)
        self.focus_reader()
        return False

    def drain_events(self):
        changed = False
        task_changed = False
        while not self.events.empty():
            kind, source, text = self.events.get_nowait()
            if self.workspace_event(kind, source, text):
                task_changed = True
                continue
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
                current = self.suggestions.text.replace("Thinking…", "").replace(
                    "Searching Exa…", ""
                )
                self.set_panel(self.suggestions, current + text)
            elif kind == "answer_status" and source == self.generation:
                question, status = text
                prefix = "Exa search · " if status == "Searching Exa…" else ""
                self.set_panel(self.suggestions, prefix + question + "\n\n" + status)
            elif kind == "answer_error" and source == self.generation:
                self.set_panel(self.suggestions, "Copilot: " + text)
            elif kind == "notice":
                self.set_status(text, error=True)
        if changed and self.view == "live":
            # Preserve the reader's place when they scroll back during a meeting.
            follow = self.body.buffer.cursor_position == len(self.body.text)
            self.set_body("\n".join(self.live_lines), follow=follow)
        if task_changed:
            if self.view == "tasks":
                self.refresh_tasks()
            elif self.view == "task" and self.selected_task == self.running_task:
                follow = self.body.buffer.cursor_position == len(self.body.text)
                self.render_task(follow=follow)

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
            self.task_cancel.set()
            # An interrupted await does not cancel a running audio thread. Join it first.
            self.worker.shutdown(wait=True, cancel_futures=True)
            self.generation += 1
            self.assistant_worker.shutdown(wait=False, cancel_futures=True)
            # EOF / terminal closure must also stop capture and retain recoverable audio.
            try:
                if self.recorder:
                    recorder = self.recorder
                    try:
                        self.finish_recording()
                    except Exception as exc:
                        raise CliError(f"{exc} Audio preserved at {recorder.directory}.") from exc
            finally:
                self.task_worker.shutdown(wait=True, cancel_futures=True)
