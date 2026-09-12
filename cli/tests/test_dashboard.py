import asyncio
import threading
import time

import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from adversaria_cli.config import CliError
from adversaria_cli.dashboard import Dashboard
from adversaria_cli.main import execute, parser


class FakeRecorder:
    def __init__(self, config, caption, notice, mic, system_device):
        self.caption, self.notice = caption, notice
        self.mic, self.system_device = mic, system_device
        self.directory = config.directory / "recordings" / "fake"
        self.directory.mkdir(parents=True)
        self.audio = self.directory / "me.wav"
        self.audio.write_bytes(b"recoverable audio")
        self.transcript = []
        self.errors = []
        self.stop_event = threading.Event()
        self.started = False

    def start(self):
        self.started = True

    def emit(self, text, source="Me"):
        self.transcript.append((time.monotonic(), f"{source}: {text}"))
        self.caption(text, source, "silence")

    def stop(self):
        if self.started:
            self.emit("Final words before we finish.", "Them")
        self.started = False
        self.stop_event.set()

    def cleanup(self):
        self.audio.unlink()
        self.directory.rmdir()


@pytest.fixture
def dashboard(env):
    config, store, engine = env
    config.save_key("openrouter", "synthetic-key")
    with create_pipe_input() as pipe:
        ui = Dashboard(
            config,
            store,
            engine,
            recorder_factory=FakeRecorder,
            input=pipe,
            output=DummyOutput(),
        )
        yield ui, pipe
        ui.worker.shutdown(wait=True)


async def until(predicate):
    async with asyncio.timeout(3):
        while not predicate():
            await asyncio.sleep(0.01)


def test_keyboard_record_live_transcript_stop_history_and_quit(dashboard):
    ui, pipe = dashboard

    async def scenario():
        app = asyncio.create_task(
            ui.app.run_async(pre_run=lambda: ui.app.create_background_task(ui.monitor()))
        )
        await until(lambda: ui.app.is_running)
        pipe.send_text("r")
        await until(lambda: ui.phase == "recording")
        recorder = ui.recorder
        recorder.emit("We agreed to launch on Friday.")
        await until(lambda: "launch on Friday" in ui.body.text)
        assert ui.view == "live"
        assert "Me" in ui.body.text

        # Browsing does not interrupt audio capture or lose incoming captions.
        pipe.send_text("m")
        await until(lambda: ui.view == "history")
        recorder.emit("Please include the final caption.")
        assert recorder.started
        pipe.send_text("s")
        await until(lambda: ui.phase == "idle")
        assert ui.view == "detail"
        assert "Final words before we finish." in ui.body.text
        assert "Please include the final caption." in ui.body.text
        assert not recorder.audio.exists()
        assert len(ui.store.rows("SELECT * FROM meetings")) == 1

        pipe.send_text("m")
        await until(lambda: ui.view == "history")
        pipe.send_text("\r")
        await until(lambda: ui.view == "detail")
        assert "launch on Friday" in ui.body.text
        pipe.send_text("q")
        assert await app == "quit"

    asyncio.run(scenario())


def test_quit_flushes_and_saves_active_recording(dashboard):
    ui, pipe = dashboard

    async def scenario():
        app = asyncio.create_task(ui.app.run_async())
        await until(lambda: ui.app.is_running)
        pipe.send_text("r")
        await until(lambda: ui.phase == "recording")
        pipe.send_text("q")
        assert await asyncio.wait_for(app, 3) == "quit"
        assert "Final words" in ui.store.rows("SELECT * FROM meetings")[0]["transcript"]
        assert ui.recorder is None

    asyncio.run(scenario())


def test_missing_key_never_opens_microphone(dashboard, monkeypatch):
    ui, _ = dashboard
    monkeypatch.setattr(ui.config, "key", lambda provider: "")
    with pytest.raises(CliError, match="speech key with K"):
        asyncio.run(ui.start_recording())
    assert ui.recorder is None
    assert ui.phase == "idle"


def test_partial_transcript_preserves_audio_and_labels_meeting(dashboard):
    ui, _ = dashboard

    async def scenario():
        await ui.start_recording()
        recorder = ui.recorder
        recorder.errors.append("Provider disconnected")
        assert await ui.stop_recording()
        assert recorder.audio.exists()
        assert "[partial]" in ui.store.rows("SELECT * FROM meetings")[0]["title"]
        assert ui.error and "audio preserved" in ui.message

    asyncio.run(scenario())


def test_failed_save_can_be_retried_without_losing_audio(dashboard, monkeypatch):
    ui, _ = dashboard
    save = ui.store.meeting

    async def scenario():
        await ui.start_recording()
        recorder = ui.recorder

        def fail(*args):
            raise OSError("Disk full")

        monkeypatch.setattr(ui.store, "meeting", fail)
        assert not await ui.stop_recording()
        assert recorder.audio.exists()
        assert ui.phase == "stopped"
        assert "Disk full" in ui.body.text
        monkeypatch.setattr(ui.store, "meeting", save)
        assert await ui.stop_recording()
        assert len(ui.store.rows("SELECT * FROM meetings")) == 1
        assert not recorder.audio.exists()

    asyncio.run(scenario())


def test_history_is_scoped_and_terminal_controls_are_stripped(dashboard):
    ui, _ = dashboard
    other = ui.store.workspace("Other workspace")
    ui.store.meeting(other["id"], "Not in this workspace", "Private text")
    mid = ui.store.meeting(ui.workspace["id"], "Current meeting", "hello\x1b[2Jthere")
    ui.show_meetings()
    assert [m["id"] for m in ui.meetings] == [mid]
    ui.open_meeting(mid)
    assert "\x1b" not in ui.body.text
    assert "hellothere" in ui.body.text


def test_captions_do_not_jump_when_reader_scrolls_back(dashboard):
    ui, _ = dashboard
    ui.show_live()
    ui.events.put(("caption", "Me", "First sentence."))
    ui.drain_events()
    ui.body.buffer.cursor_position = 0
    ui.events.put(("caption", "Them", "Second sentence."))
    ui.drain_events()
    assert ui.body.buffer.cursor_position == 0
    assert "Second sentence." in ui.body.text


def test_noninteractive_default_prints_help_and_tui_is_explicit(env, capsys):
    config, store, engine = env
    assert execute(parser().parse_args([]), config, store, engine) == 0
    assert "Full-screen meeting dashboard" in capsys.readouterr().out
    with pytest.raises(CliError, match="interactive terminal"):
        execute(parser().parse_args(["tui"]), config, store, engine)


def test_empty_recording_keeps_audio_and_allows_another_attempt(dashboard, monkeypatch):
    ui, _ = dashboard

    async def scenario():
        await ui.start_recording()
        recorder = ui.recorder
        monkeypatch.setattr(recorder, "stop", recorder.stop_event.set)
        assert not await ui.stop_recording()
        assert recorder.audio.exists()
        assert ui.store.rows("SELECT * FROM meetings") == []
        assert ui.phase == "idle" and ui.recorder is None
        assert "No speech was transcribed" in ui.body.text
        assert "Press R to try a new recording" in ui.body.text

    asyncio.run(scenario())


@pytest.mark.parametrize("during_construction", [False, True])
def test_microphone_start_failure_returns_to_idle(dashboard, during_construction):
    ui, _ = dashboard

    class DeniedRecorder(FakeRecorder):
        def __init__(self, *args):
            if during_construction:
                raise OSError("Microphone permission denied")
            super().__init__(*args)

        def start(self):
            raise CliError("Microphone permission denied")

    ui.recorder_factory = DeniedRecorder
    asyncio.run(ui.perform("record"))
    assert "permission denied" in ui.message
    assert ui.phase == "idle" and ui.recorder is None
    assert not ui.busy


def test_new_recording_never_receives_previous_final_captions(dashboard):
    ui, _ = dashboard

    async def scenario():
        await ui.start_recording()
        ui.recorder.emit("First meeting only.")
        # No monitor tick between stop and restart: the final caption is still queued.
        assert await ui.stop_recording()
        assert "First meeting only" in ui.body.text
        await ui.start_recording()
        ui.drain_events()
        assert "First meeting only" not in ui.body.text
        assert "Final words" not in ui.body.text
        assert ui.live_lines == []
        ui.recorder.emit("Second meeting only.")
        ui.drain_events()
        assert "Second meeting only" in ui.body.text
        assert await ui.stop_recording()
        assert len(ui.store.rows("SELECT * FROM meetings")) == 2

    asyncio.run(scenario())


def test_terminal_eof_during_startup_waits_for_audio_then_saves(dashboard):
    ui, pipe = dashboard
    opening = threading.Event()
    release = threading.Event()
    recorders = []

    class SlowRecorder(FakeRecorder):
        def start(self):
            opening.set()
            assert release.wait(3)
            super().start()
            recorders.append(self)

    ui.recorder_factory = SlowRecorder

    def close_terminal():
        assert opening.wait(3)
        pipe.close()
        release.set()

    closer = threading.Thread(target=close_terminal)
    closer.start()
    pipe.send_text("r")
    try:
        with pytest.raises(EOFError):
            ui.run()
    finally:
        release.set()
        closer.join(timeout=3)
    assert not recorders[0].started
    assert ui.recorder is None
    assert "Final words" in ui.store.rows("SELECT * FROM meetings")[0]["transcript"]


def test_copilot_answers_completed_questions_and_approval_is_explicit(dashboard, monkeypatch):
    ui, pipe = dashboard
    seen = []

    def answer(self, question, workspace=None, turns=None, **kwargs):
        seen.append((question, turns))
        yield "Start with the "
        yield "architecture and data flow."

    monkeypatch.setattr("adversaria_cli.dashboard.Engine.answer", answer)

    async def scenario():
        app = asyncio.create_task(
            ui.app.run_async(pre_run=lambda: ui.app.create_background_task(ui.monitor()))
        )
        await until(lambda: ui.app.is_running)
        ui.events.put(("caption", "Them", ("What should we", "forced")))
        ui.drain_events()
        assert seen == []
        ui.events.put(("caption", "Them", ("include?", "silence")))
        await until(lambda: "data flow." in ui.suggestions.text)
        assert seen[0][0] == "What should we include?"
        assert "Them: What should we include?" in seen[0][1]
        ui.events.put(
            ("caption", "Me", ("I will create an architecture diagram by Monday.", "silence"))
        )
        await until(lambda: "c1" in ui.commitments.text)
        assert ui.store.rows("SELECT * FROM tasks") == []
        pipe.send_text("/approve c1\r")
        await until(lambda: bool(ui.store.rows("SELECT * FROM tasks")))
        task = ui.store.rows("SELECT * FROM tasks")[0]
        assert task["status"] == "queued" and task["kind"] == "visualize"
        pipe.send_text("\x1b")
        await asyncio.sleep(0.1)
        pipe.send_text("q")
        assert await asyncio.wait_for(app, 3) == "quit"

    try:
        asyncio.run(scenario())
    finally:
        ui.assistant_worker.shutdown(wait=True)


def test_copilot_request_does_not_block_recording(dashboard, monkeypatch):
    ui, _ = dashboard
    release = threading.Event()

    def answer(*args, **kwargs):
        assert release.wait(3)
        yield "Answer"

    monkeypatch.setattr("adversaria_cli.dashboard.Engine.answer", answer)
    try:
        ui.ask("Question?")
        ui.events.put(("caption", "Me", "Caption while the model is thinking."))
        ui.show_live()
        ui.drain_events()
        assert "Caption while the model is thinking" in ui.body.text
    finally:
        release.set()
        ui.assistant_worker.shutdown(wait=True)


def test_dashboard_search_uses_exa_and_openrouter_even_if_task_provider_differs(
    dashboard, monkeypatch
):
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document

    ui, _ = dashboard
    ui.config.save(provider="codex")
    calls = []

    def answer(self, question, workspace=None, turns=None, **kwargs):
        calls.append((question, kwargs))
        yield "Grounded search answer"

    monkeypatch.setattr("adversaria_cli.dashboard.Engine.answer", answer)
    ui.submit_command(Buffer(document=Document("search latest ASR research")))
    ui.assistant_worker.shutdown(wait=True)
    ui.drain_events()
    assert calls[0][0] == "latest ASR research"
    assert calls[0][1]["web"] is True
    assert calls[0][1]["provider"] == "openrouter"
    assert "Grounded search answer" in ui.suggestions.text


def test_typed_question_automatically_searches_and_displays_sources(dashboard, monkeypatch):
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document

    ui, _ = dashboard
    ui.config.save_key("exa", "synthetic-exa-key")
    ui.store.meeting(ui.workspace["id"], "Project", "What Hamza built: an AI assistant.")
    queries = []

    def search(config, question):
        queries.append(question)
        return [
            {
                "title": "AI Tinkerers",
                "url": "https://aitinkerers.org",
                "text": "A builder community.",
            }
        ]

    monkeypatch.setattr("adversaria_cli.engine.search", search)
    monkeypatch.setattr(
        "adversaria_cli.models.Models.generate",
        lambda *args, **kwargs: iter(["AI Tinkerers is a builder community."]),
    )
    ui.submit_command(Buffer(document=Document("What is AI Tinkerers?")))
    ui.assistant_worker.shutdown(wait=True)
    ui.drain_events()
    assert queries == ["What is AI Tinkerers?"]
    assert "Exa search · What is AI Tinkerers?" in ui.suggestions.text
    assert "builder community" in ui.suggestions.text
    assert "https://aitinkerers.org" in ui.suggestions.text
    assert "Thinking…" not in ui.suggestions.text
    assert "Searching Exa…" not in ui.suggestions.text


@pytest.mark.parametrize("flag, expected", [("--web", True), ("--no-web", False)])
def test_dashboard_ask_accepts_search_override_flags(dashboard, monkeypatch, flag, expected):
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document

    ui, _ = dashboard
    calls = []

    def answer(self, question, workspace=None, turns=None, **kwargs):
        calls.append((question, kwargs["web"]))
        yield "Answer"

    monkeypatch.setattr("adversaria_cli.dashboard.Engine.answer", answer)
    ui.submit_command(Buffer(document=Document(f"ask {flag} What is AI Tinkerers?")))
    ui.assistant_worker.shutdown(wait=True)
    assert calls == [("What is AI Tinkerers?", expected)]
