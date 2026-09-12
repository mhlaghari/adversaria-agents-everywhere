"""Multi-pane live record/replay screen (rich Live + Layout).

Attached from main.py with one hook: ``tui.attach(shell, cmd)``. It only
activates when stdout is a TTY and ``ADVERSARIA_PLAIN`` is unset; otherwise the
plain ``say(...)`` output is untouched. All transcript/model text goes through
``ui.safe`` before rendering. Nothing here changes CAUGHT/approve semantics.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from concurrent.futures import wait

from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from .ui import console, safe

SOURCE_STYLE = {"Them": "magenta", "Me": "green"}
HINT = "approve <id> · dismiss <id> · ask <question> · Ctrl-C stop & save"


class _Transcript:
    """Renders the last lines that fit the pane; newest bold, partial dim."""

    def __init__(self, screen):
        self.screen = screen

    def __rich_console__(self, console, options):
        height = options.height or console.height
        with self.screen.lock:
            lines = list(self.screen.lines)
            partial = dict(self.screen.partial)
        text = Text()
        for i, (source, body) in enumerate(lines):
            newest = i == len(lines) - 1 and not partial
            text.append(f"{source}: ", style=f"bold {SOURCE_STYLE.get(source, 'white')}")
            text.append(body, style="bold" if newest else "")
            text.append("\n")
        for source, body in partial.items():
            text.append(f"{source}: ", style=f"dim {SOURCE_STYLE.get(source, 'white')}")
            text.append(body + " …", style="dim")
            text.append("\n")
        text.rstrip()
        wrapped = text.wrap(console, max(options.max_width - 4, 10))
        keep = wrapped[-max(height - 2, 1) :]
        yield Panel(
            Text("\n").join(keep), title="LIVE TRANSCRIPT", title_align="left", height=height
        )


class RecordScreen:
    def __init__(self, title, workspace, provider_model, replay=False):
        self.title = safe(title)
        self.workspace = safe(workspace)
        self.provider_model = safe(provider_model)
        self.replay = replay
        self.lock = threading.RLock()
        self.lines = []  # (source, text) final captions
        self.partial = {}  # source -> in-progress text
        self.cards = {}  # id -> dict(id, kind, deadline, text, state, task_id)
        self.question_text = ""
        self.answer_text = ""
        self.started = time.monotonic()
        self.tick = 0
        self.live = None

    # -- public API ---------------------------------------------------------
    def start(self):
        self.started = time.monotonic()
        self.live = Live(self, console=console, refresh_per_second=4, screen=False, transient=False)
        self.live.start()
        return self

    def stop(self):
        if self.live:
            self.live.stop()
            self.live = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()

    def caption(self, source, text, final=True):
        source, text = safe(source), safe(text).strip()
        with self.lock:
            if not final:
                if text:
                    self.partial[source] = " ".join(
                        filter(None, [self.partial.get(source, ""), text])
                    )
                return
            full = " ".join(filter(None, [self.partial.pop(source, ""), text]))
            if full:
                self.lines.append((source, full))
                self.lines = self.lines[-400:]

    def commitment(self, c):
        with self.lock:
            self.cards[c.id] = {
                "id": safe(c.id),
                "kind": safe(c.kind),
                "deadline": safe(c.deadline or "no deadline"),
                "text": safe(c.text),
                "state": "caught",
                "task_id": None,
            }

    def commitment_state(self, id, state, task_id=None):
        with self.lock:
            card = self.cards.get(id)
            if card:
                card["state"], card["task_id"] = state, task_id

    def question(self, text):
        with self.lock:
            self.question_text, self.answer_text = safe(text), ""

    def answer_token(self, token):
        with self.lock:
            self.answer_text += safe(token)

    # -- rendering ----------------------------------------------------------
    def __rich__(self):
        self.tick += 1
        root = Layout(name="root")
        root.split_column(
            Layout(self._top(), name="top", size=1),
            Layout(name="body"),
            Layout(Text(HINT, style="dim", justify="center"), name="hint", size=1),
        )
        root["body"].split_row(
            Layout(_Transcript(self), name="transcript", ratio=3),
            Layout(name="side", ratio=2),
        )
        root["side"].split_column(
            Layout(self._caught(), name="caught", ratio=3),
            Layout(self._copilot(), name="copilot", ratio=2),
        )
        return root

    def _top(self):
        elapsed = int(time.monotonic() - self.started)
        clock = f"{elapsed // 60:02d}:{elapsed % 60:02d}"
        dot = "●" if self.tick % 2 else "○"
        mode = "REPLAY" if self.replay else "REC"
        bar = Text("ADVERSARIA  ", style="bold cyan")
        bar.append(f"{dot} {mode} {clock}", style="bold red" if not self.replay else "bold yellow")
        bar.append(
            f"  ·  workspace {self.workspace}  ·  {self.provider_model}  ·  Ctrl-C stop",
            style="dim",
        )
        return bar

    def _caught(self):
        with self.lock:
            cards = [c for c in self.cards.values() if c["state"] != "dismissed"]
        panels = []
        for c in cards[-4:]:
            title = f"{c['id']} · {c['kind'].capitalize()} · {c['deadline']}"
            body = Text(c["text"] + "\n")
            if c["state"] == "approved":
                body.append(f"✓ task #{c['task_id']} queued", style="green")
                style = "green"
            else:
                body.append(f"approve {c['id']} / dismiss {c['id']}", style="bold yellow")
                style = "yellow"
            panels.append(Panel(body, title=title, title_align="left", border_style=style))
        inner = Group(*panels) if panels else Text("Listening for commitments…", style="dim")
        return Panel(inner, title="CAUGHT · needs your tap", title_align="left")

    def _copilot(self):
        with self.lock:
            question, answer = self.question_text, self.answer_text
        if not question:
            inner = Text("Questions in the conversation get answered here.", style="dim")
        else:
            inner = Group(Text(f"? {question}", style="bold cyan"), Markdown(answer))
        return Panel(inner, title="COPILOT", title_align="left")


# -- main.py hook -------------------------------------------------------------


def attach(shell, cmd):
    """Route the record/replay prints of ``shell`` through a RecordScreen (TTY only)."""
    if cmd not in {"record", "replay"}:
        return
    if not sys.stdout.isatty() or os.environ.get("ADVERSARIA_PLAIN"):
        return
    from .engine import Engine

    state = {"screen": None}

    def screen():
        return state["screen"]

    orig_caption, orig_answer, orig_line = shell.caption, shell.answer, shell.line
    orig_replay, orig_record, orig_loop = shell.replay, shell.record_command, shell.loop

    def caption(text, source="Me", boundary="silence"):
        s = screen()
        if not s:
            return orig_caption(text, source, boundary)
        s.caption(source, text, final=boundary == "silence")
        with shell.lock:
            caught, question = shell.copilot.feed(text, source, boundary)
            turns = list(shell.copilot.turns)
        if caught:
            shell.commitment_workspaces[caught.id] = (
                shell.record_workspace if shell.recorder else shell.workspace
            )
            s.commitment(caught)
        if question and shell.ai:
            shell.job(shell.answer, question, turns, shell.workspace, shell.provider, shell.model)

    def answer(question, turns, workspace, provider, model, web=False):
        s = screen()
        if not s:
            return orig_answer(question, turns, workspace, provider, model, web)
        engine = Engine(shell.config, shell.store)
        s.question(question)
        tokens = engine.answer(question, workspace, turns, provider, model, web)
        try:
            for token in tokens:
                s.answer_token(token)
        finally:
            tokens.close()

    def line(text):
        result = orig_line(text)
        s = screen()
        if s:
            with shell.lock:
                for c in shell.copilot.commitments.values():
                    s.commitment_state(c.id, c.status, c.task_id)
        return result

    def open_screen(title, replay):
        provider, model = shell.config.selection(shell.provider, shell.model)
        state["screen"] = RecordScreen(title, shell.workspace, f"{provider}/{model}", replay=replay)
        state["screen"].start()

    def close_screen():
        s = screen()
        state["screen"] = None
        if s:
            s.stop()

    def loop():
        close_screen()  # the prompt loop below prints plainly again
        return orig_loop()

    def replay(file):
        open_screen(os.path.basename(str(file)), replay=True)
        try:
            orig_replay(file)
            wait([f for f in shell.futures if not f.done()])
        finally:
            close_screen()

    def record_command(args):
        shell.workspace = args.workspace or shell.workspace
        shell.provider, shell.model = shell.config.selection(args.provider, args.model)
        open_screen(args.title, replay=False)
        try:
            return orig_record(args)
        finally:
            close_screen()

    shell.caption, shell.answer, shell.line = caption, answer, line
    shell.replay, shell.record_command, shell.loop = replay, record_command, loop
