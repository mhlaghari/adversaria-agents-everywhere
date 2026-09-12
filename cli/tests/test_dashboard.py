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
        ui.task_cancel.set()
        ui.task_worker.shutdown(wait=True)


def command(ui, text):
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.document import Document

    ui.submit_command(Buffer(document=Document(text)))


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


def test_workspace_commands_attach_context_instructions_and_restore_commitments(
    dashboard, tmp_path
):
    ui, _ = dashboard
    original = ui.workspace["name"]
    ui.copilot.feed("I will write our architecture document.", "Me", "silence")
    assert "c1" in ui.copilot.commitments
    source = tmp_path / "project context.md"
    source.write_text("Adversaria uses OpenRouter and Exa.", encoding="utf-8")
    command(ui, "workspace Hackathon")
    assert ui.config.values["workspace"] == "Hackathon"
    assert not ui.copilot.commitments
    command(ui, f'attach "{source}"')
    command(ui, "instructions Keep answers short and cite sources.")
    assert "project context.md" in ui.body.text
    assert "Keep answers short" in ui.workspace["instructions"]
    assert "OpenRouter" in ui.store.context(ui.workspace["id"], "Adversaria")
    source_id = ui.store.rows("SELECT id FROM sources")[0]["id"]
    command(ui, f"source {source_id}")
    assert ui.view == "source" and "OpenRouter and Exa" in ui.body.text
    command(ui, f"workspace {original}")
    assert "c1" in ui.copilot.commitments
    assert "project context.md" not in ui.body.text
    command(ui, f"source {source_id}")
    assert ui.error and "not in the current workspace" in ui.message
    command(ui, "approve c1")
    assert ui.store.rows("SELECT * FROM tasks")[0]["workspace_id"] == ui.workspace["id"]


def test_recording_prevents_workspace_switch_but_allows_task_browsing(dashboard):
    ui, _ = dashboard
    wid = ui.workspace["id"]

    async def scenario():
        await ui.start_recording()
        command(ui, "workspace Another workspace")
        assert ui.error and "Stop and save" in ui.message
        assert ui.workspace["id"] == wid
        assert not ui.store.rows("SELECT * FROM workspaces WHERE name='Another workspace'")
        command(ui, "new write Draft a meeting summary")
        ui.show_tasks()
        assert len(ui.tasks) == 1 and ui.recorder.started
        ui.recorder.emit("Still recording while we browse tasks.")
        assert await ui.stop_recording()
        assert ui.store.rows("SELECT * FROM meetings")[0]["workspace_id"] == wid

    asyncio.run(scenario())


def test_task_keyboard_run_revision_and_approval_keep_local_artifacts(dashboard, monkeypatch):
    ui, pipe = dashboard
    prompts = []

    def generate(self, system, prompt, provider=None, model=None):
        assert provider == "openrouter"
        prompts.append(prompt)
        yield "# Architecture draft\n"
        yield "Our audio flows through OpenRouter."

    monkeypatch.setattr("adversaria_cli.models.Models.generate", generate)
    ui.config.save(provider="codex")

    async def scenario():
        app = asyncio.create_task(
            ui.app.run_async(pre_run=lambda: ui.app.create_background_task(ui.monitor()))
        )
        await until(lambda: ui.app.is_running)
        pipe.send_text("/new write Draft the architecture\r")
        await until(lambda: ui.view == "task")
        tid = ui.selected_task
        assert ui.store.task(tid)["status"] == "queued"
        pipe.send_text("g")
        await until(lambda: ui.store.task(tid)["status"] == "awaiting_review")
        await until(lambda: "SAVED ARTIFACT" in ui.body.text)
        assert "# Architecture draft" in ui.body.text
        first = ui.store.artifact(tid)
        pipe.send_text(f"/revise {tid} Include Exa search and privacy.\r")
        await until(lambda: ui.store.task(tid)["status"] == "queued")
        pipe.send_text("g")
        await until(lambda: len(ui.store.rows("SELECT * FROM runs")) == 2 and not ui.task_active)
        await until(lambda: "SAVED ARTIFACT" in ui.body.text)
        assert "Include Exa search and privacy." in prompts[-1]
        assert ui.store.artifact(tid) != first and first.exists()
        pipe.send_text("v")
        await until(lambda: ui.store.task(tid)["status"] == "done")
        pipe.send_text("t")
        await until(lambda: ui.view == "tasks")
        assert "Approved" in ui.task_entries()[1][1]
        pipe.send_text("q")
        assert await app == "quit"

    asyncio.run(scenario())


def test_task_runs_independently_of_audio_and_keeps_its_workspace(dashboard, monkeypatch):
    ui, _ = dashboard
    release = threading.Event()
    generating = threading.Event()

    def generate(*args, **kwargs):
        generating.set()
        assert release.wait(3)
        yield "Finished in the original workspace."

    monkeypatch.setattr("adversaria_cli.models.Models.generate", generate)
    tid = ui.add_workspace_task("Write the project brief")
    wid = ui.workspace["id"]
    ui.run_workspace_task(tid)
    assert generating.wait(3)

    async def scenario():
        await ui.start_recording()
        ui.recorder.emit("Captions continue while the task is generating.")
        ui.drain_events()
        assert "Captions continue" in ui.body.text
        assert await ui.stop_recording()
        ui.use_workspace("Other workspace")
        ui.show_tasks()
        assert not ui.tasks
        release.set()
        await asyncio.wrap_future(ui.task_future)
        ui.drain_events()
        assert ui.view == "tasks" and not ui.tasks
        assert ui.store.task(tid)["workspace_id"] == wid
        assert ui.store.task(tid)["status"] == "awaiting_review"

    try:
        asyncio.run(scenario())
    finally:
        release.set()


def test_cancel_then_retry_persists_failure_and_never_accepts_partial_output(
    dashboard, monkeypatch
):
    ui, _ = dashboard
    waiting = threading.Event()
    release = threading.Event()

    def generate(*args, **kwargs):
        yield "Partial text"
        waiting.set()
        assert release.wait(3)
        yield "must not become an artifact"

    monkeypatch.setattr("adversaria_cli.models.Models.generate", generate)
    tid = ui.add_workspace_task("Draft the README")
    ui.run_workspace_task(tid)
    try:
        assert waiting.wait(3)
        ui.cancel_workspace_task()
        release.set()
        ui.task_future.result(timeout=3)
        ui.drain_events()
        assert ui.store.task(tid)["status"] == "failed"
        assert "cancelled" in ui.message
        with pytest.raises(CliError, match="No completed artifact"):
            ui.store.artifact(tid)
        monkeypatch.setattr(
            "adversaria_cli.models.Models.generate", lambda *a, **kw: iter(["Complete draft"])
        )
        ui.run_workspace_task(tid)
        ui.task_future.result(timeout=3)
        ui.drain_events()
        assert ui.store.task(tid)["status"] == "awaiting_review"
        assert ui.store.artifact(tid).read_text() == "Complete draft\n"
    finally:
        release.set()


def test_pause_scope_and_review_guards(dashboard, monkeypatch):
    ui, _ = dashboard
    monkeypatch.setattr(
        "adversaria_cli.models.Models.generate", lambda *a, **kw: iter(["Review this draft."])
    )
    tid = ui.add_workspace_task("Draft a summary")
    command(ui, "pause")
    command(ui, f"run {tid}")
    assert ui.error and "paused" in ui.message
    assert ui.store.task(tid)["status"] == "queued"
    command(ui, "resume")
    command(ui, f"run {tid}")
    ui.task_future.result(timeout=3)
    ui.drain_events()
    ui.show_tasks()
    command(ui, f"approve {tid}")
    assert ui.view == "task"
    assert ui.store.task(tid)["status"] == "awaiting_review"
    ui.store.artifact(tid).unlink()
    command(ui, f"approve {tid}")
    assert ui.error and ui.store.task(tid)["status"] == "awaiting_review"
    ui.use_workspace("Unrelated")
    command(ui, f"run {tid}")
    assert ui.error and "another workspace" in ui.message
    command(ui, f"revise {tid} Wrong workspace")
    assert "Wrong workspace" not in ui.store.task(tid)["details"]


def test_quit_saves_audio_and_cancels_in_flight_task(dashboard, monkeypatch):
    ui, pipe = dashboard
    waiting = threading.Event()

    def generate(*args, **kwargs):
        waiting.set()
        assert ui.task_cancel.wait(3)
        yield "Cancelled output"

    monkeypatch.setattr("adversaria_cli.models.Models.generate", generate)
    tid = ui.add_workspace_task("Draft a summary")

    async def scenario():
        app = asyncio.create_task(
            ui.app.run_async(pre_run=lambda: ui.app.create_background_task(ui.monitor()))
        )
        await until(lambda: ui.app.is_running)
        ui.run_workspace_task(tid)
        await until(waiting.is_set)
        pipe.send_text("r")
        await until(lambda: ui.phase == "recording")
        pipe.send_text("q")
        assert await asyncio.wait_for(app, 3) == "quit"
        assert ui.recorder is None and not ui.task_active
        assert ui.store.task(tid)["status"] == "failed"
        assert len(ui.store.rows("SELECT * FROM meetings")) == 1

    asyncio.run(scenario())


def test_research_task_uses_exa_only_when_selected(dashboard, monkeypatch):
    ui, _ = dashboard
    calls = []
    ui.config.save_key("exa", "synthetic-exa")

    def search(config, query):
        calls.append(query)
        return [{"title": "Reference", "url": "https://example.com/reference", "text": "Evidence."}]

    monkeypatch.setattr("adversaria_cli.engine.search", search)
    monkeypatch.setattr(
        "adversaria_cli.models.Models.generate", lambda *a, **kw: iter(["Research brief"])
    )
    command(ui, "new research --web Compare speech services")
    tid = ui.selected_task
    ui.run_workspace_task(tid)
    ui.task_future.result(timeout=3)
    ui.drain_events()
    assert calls == ["Compare speech services"]
    assert "https://example.com/reference" in ui.body.text
    command(ui, f"revise {tid} ")
    assert ui.error and ui.store.task(tid)["status"] == "awaiting_review"


def test_terminal_eof_cancels_task_and_persists_a_retryable_state(dashboard, monkeypatch):
    ui, pipe = dashboard
    waiting = threading.Event()

    def generate(*args, **kwargs):
        waiting.set()
        assert ui.task_cancel.wait(3)
        yield "Do not save this partial draft"

    monkeypatch.setattr("adversaria_cli.models.Models.generate", generate)
    tid = ui.add_workspace_task("Draft a summary")
    ui.run_workspace_task(tid)

    def close_terminal():
        assert waiting.wait(3)
        pipe.close()

    closer = threading.Thread(target=close_terminal)
    closer.start()
    try:
        with pytest.raises(EOFError):
            ui.run()
    finally:
        ui.task_cancel.set()
        closer.join(timeout=3)
    assert not ui.task_active
    assert ui.store.task(tid)["status"] == "failed"
    assert ui.store.rows("SELECT * FROM runs WHERE status='running'") == []


def test_edit_shortcut_requires_open_task_and_dialog_names_its_target(dashboard, monkeypatch):
    ui, _ = dashboard
    tid = ui.add_workspace_task("Write the architecture brief")
    ui.show_tasks()
    with pytest.raises(CliError, match="open the task"):
        asyncio.run(ui.revise_task_dialog())
    ui.show_workspaces()
    with pytest.raises(CliError, match="open the task"):
        asyncio.run(ui.revise_task_dialog())
    assert ui.store.task(tid)["details"] == ""
    ui.open_task(tid)
    dialogs = []

    async def dialog(factory, **kwargs):
        dialogs.append(kwargs)
        return "Add Exa provenance."

    monkeypatch.setattr(ui, "dialog", dialog)
    asyncio.run(ui.revise_task_dialog())
    assert f"Task {tid}" in dialogs[0]["title"]
    assert "Write the architecture brief" in dialogs[0]["text"]
    assert "Add Exa provenance" in ui.store.task(tid)["details"]


def test_native_workspace_dialog_owns_input_and_restores_the_dashboard(dashboard, monkeypatch):
    from prompt_toolkit.shortcuts import input_dialog

    ui, pipe = dashboard
    dialogs = []

    def observe(**kwargs):
        app = input_dialog(**kwargs)
        dialogs.append(app)
        return app

    monkeypatch.setattr("adversaria_cli.workspace_dashboard.input_dialog", observe)

    async def scenario():
        app = asyncio.create_task(
            ui.app.run_async(pre_run=lambda: ui.app.create_background_task(ui.monitor()))
        )
        await until(lambda: ui.app.is_running)
        pipe.send_text("w")
        await until(lambda: ui.view == "workspaces")
        pipe.send_text("\r")
        await until(lambda: dialogs and dialogs[0].is_running)
        assert dialogs[0].input is ui.app.input
        # Enter focuses OK; the next Enter submits the dialog.
        pipe.send_text("Keyboard workspace\r\r")
        await until(lambda: ui.workspace["name"] == "Keyboard workspace")
        assert ui.view == "workspaces" and not ui.busy
        pipe.send_text("q")
        assert await app == "quit"

    asyncio.run(scenario())


def test_preview_shortcut_opens_the_selected_artifact_without_approving_it(dashboard, monkeypatch):
    from adversaria_cli.demo import seed_demo

    ui, pipe = dashboard
    _, tasks = seed_demo(ui.config, ui.store)
    task = next(t for t in tasks if t["kind"] == "visualize")
    opened = []
    monkeypatch.setattr(
        "adversaria_cli.preview.webbrowser.open", lambda url: opened.append(url) or True
    )
    ui.open_task(task["id"])
    assert ("preview_task", "[O] Open preview") in ui.menu_entries()

    async def scenario():
        app = asyncio.create_task(ui.app.run_async())
        await until(lambda: ui.app.is_running)
        pipe.send_text("o")
        await until(lambda: opened and not ui.busy)
        assert opened[0].endswith("/preview.html")
        assert ui.store.task(task["id"])["status"] == "awaiting_review"
        pipe.send_text("w")
        await until(lambda: ui.view == "workspaces")
        pipe.send_text("o")
        await until(lambda: ui.error)
        assert len(opened) == 1
        pipe.send_text("q")
        assert await app == "quit"

    asyncio.run(scenario())
