import json

import httpx
import pytest

from adversaria_cli.config import CliError, Config
from adversaria_cli.copilot import Copilot
from adversaria_cli.engine import Engine
from adversaria_cli.main import Shell, execute, parser
from adversaria_cli.research import search
from adversaria_cli.transport import sse_events, stream
from adversaria_cli.ui import safe


def completion(text="A completed draft."):
    return (
        "data: " + json.dumps({"choices": [{"delta": {"content": text}}]}) + "\n\ndata: [DONE]\n\n"
    )


def test_cloud_defaults_and_private_keys(env):
    config, store, _ = env
    assert config.selection() == ("openrouter", "auto")
    config.save_key("openai", "synthetic-secret")
    assert config.key("openai") == "synthetic-secret"
    assert (config.directory / "openai.key").stat().st_mode & 0o777 == 0o600
    config.save(provider="openai", model="chosen")
    assert "synthetic-secret" not in config.path.read_text()
    assert config.selection("openrouter") == ("openrouter", "auto")
    assert Config(config.directory).selection() == ("openai", "chosen")
    assert store.path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize(
    "text,kind",
    [
        ("I will create a solutions architecture diagram for Wael by Monday.", "visualize"),
        ("I'll check the thresholds before Friday.", "research"),
        ("I will draft a deck.", "present"),
        ("We should write the proposal.", "write"),
        ("Action item: confirm the numbers.", "research"),
        ("I’ll draw up the system design.", "visualize"),
    ],
)
def test_commitment_contract(text, kind):
    caught, question = Copilot().feed(text)
    assert caught.kind == kind
    assert question is None


@pytest.mark.parametrize(
    "text",
    [
        "Could you send it?",
        "I will not send it.",
        "We already sent it.",
        "I wonder about tomorrow.",
    ],
)
def test_no_false_commitment(text):
    assert Copilot().feed(text)[0] is None


def test_complete_turn_and_dedup():
    copilot = Copilot()
    assert copilot.feed("I will create", boundary="forced") == (None, None)
    caught, _ = copilot.feed("a diagram by Monday.")
    assert caught.deadline == "by Monday"
    assert caught.text == "I will create a diagram by Monday."
    assert copilot.feed(caught.text.upper()) == (None, None)
    assert copilot.feed("How does it work?", source="Them")[1] == "How does it work?"


def test_approval_is_explicit_atomic_idempotent_and_paused(env):
    config, store, engine = env
    shell = Shell(config, store, engine)
    shell.ai = False
    try:
        shell.caption("I will write the proposal by Friday.")
        assert store.rows("SELECT * FROM tasks") == []
        ws = engine.workspace()
        store.configure_workspace(ws["id"], paused=True)
        shell.approve(["approve", "c1", "present", "--web"])
        shell.approve(["approve", "c1"])
        tasks = store.rows("SELECT * FROM tasks")
        assert len(tasks) == 1
        assert tasks[0]["kind"] == "present" and tasks[0]["web"] == 1
        assert tasks[0]["status"] == "queued"
        assert shell.futures == []
        shell.caption("I will send the email.")
        shell.line("dismiss c2")
        assert len(store.rows("SELECT * FROM tasks")) == 1
        with pytest.raises(CliError, match="dismissed"):
            shell.approve(["approve", "c2"])
    finally:
        shell.close()


def test_case_insensitive_workspaces_and_scoped_retrieval(env, tmp_path):
    _, store, _ = env
    first = store.workspace("Interviews")
    assert first["id"] == store.workspace("interviews")["id"]
    second = store.workspace("Private")
    store.meeting(first["id"], "Demo", "Project Omega runs on three workers.")
    store.meeting(second["id"], "Private", "Project Omega secret is 123.")
    assert "three workers" in store.context(first["id"], "Omega workers")
    assert "123" not in store.context(first["id"], "Omega")
    file = tmp_path / "facts.md"
    file.write_text("The launch date is Monday.")
    store.attach(first["id"], file)
    file.write_text("The launch date is Tuesday.")
    store.attach(first["id"], file)
    assert len(store.rows("SELECT * FROM sources")) == 1
    assert "Tuesday" in store.context(first["id"], "launch")


def test_exa_is_explicit_and_citations_survive_task_run(env, http_mock):
    config, store, engine = env
    config.save_key("exa", "test-exa")
    config.save_key("openrouter", "test-router")
    calls = []

    def handler(req):
        calls.append(req)
        if req.url.host == "api.exa.ai":
            assert req.headers["x-api-key"] == "test-exa"
            payload = json.loads(req.content)
            assert payload["query"] == "Research voice agents"
            assert payload["contents"]["text"]["maxCharacters"] == 4000
            return httpx.Response(
                200,
                json={
                    "results": [
                        {
                            "title": "Official evidence",
                            "url": "https://example.org/source",
                            "text": "Bounded queues protect latency.",
                        }
                    ]
                },
            )
        assert req.url.host == "openrouter.ai"
        assert req.headers["authorization"] == "Bearer test-router"
        assert "Bounded queues" in json.loads(req.content)["messages"][1]["content"]
        return httpx.Response(200, text=completion())

    http_mock(handler)
    task = store.add_task(engine.workspace()["id"], "Research voice agents", "research", web=True)
    assert "completed" in "".join(engine.run_task(task))
    assert store.task(task)["status"] == "awaiting_review"
    artifact = store.artifact(task).read_text()
    assert "https://example.org/source" in artifact
    assert len(calls) == 2
    store.review(task, True)
    assert store.task(task)["status"] == "done"


def test_failed_stream_retry_and_artifact_approval(env, http_mock):
    config, store, engine = env
    config.save_key("openrouter", "test-key")
    task = store.add_task(engine.workspace()["id"], "Write followup", "write")
    http_mock(
        lambda req: httpx.Response(200, text=completion("Partial").replace("data: [DONE]\n\n", ""))
    )
    with pytest.raises(CliError, match="without a complete"):
        list(engine.run_task(task))
    assert store.task(task)["status"] == "failed"
    with pytest.raises(CliError, match="No completed artifact"):
        store.artifact(task)
    http_mock(lambda req: httpx.Response(200, text=completion()))
    list(Engine(config, store).run_task(task))
    assert store.task(task)["status"] == "awaiting_review"
    with pytest.raises(CliError, match="not queued"):
        list(engine.run_task(task))
    store.review(task, False)
    assert store.task(task)["status"] == "queued"
    assert len(store.rows("SELECT * FROM runs")) == 2


def test_missing_keys_do_not_start_or_send(env, http_mock):
    config, store, engine = env
    http_mock(lambda req: pytest.fail("Unexpected network request"))
    task = store.add_task(engine.workspace()["id"], "Write it", "write")
    with pytest.raises(CliError, match="OpenRouter needs"):
        list(engine.run_task(task))
    assert store.task(task)["status"] == "queued"
    assert store.rows("SELECT * FROM runs") == []
    with pytest.raises(CliError, match="Exa needs"):
        search(config, "query")


def test_only_one_worker_can_claim_and_cancel_is_failed(env, http_mock):
    config, store, engine = env
    config.save_key("openrouter", "test-key")
    task = store.add_task(engine.workspace()["id"], "Write", "write")
    http_mock(lambda req: httpx.Response(200, text=completion()))
    run = engine.run_task(task)
    next(run)
    with pytest.raises(CliError, match="already running"):
        store.claim(task)
    run.close()
    assert store.task(task)["status"] == "failed"


def test_diagram_must_contain_a_diagram(env, http_mock):
    config, store, engine = env
    config.save_key("openrouter", "test-key")
    task = store.add_task(engine.workspace()["id"], "Architecture", "visualize")
    http_mock(lambda req: httpx.Response(200, text=completion("I would draw it.")))
    with pytest.raises(CliError, match="Mermaid"):
        list(engine.run_task(task))
    http_mock(
        lambda req: httpx.Response(200, text=completion("```mermaid\nflowchart LR\n A --> B\n```"))
    )
    list(engine.run_task(task))
    assert "flowchart" in store.artifact(task).read_text()


def test_openrouter_catalog_filters_images_and_keeps_prices(env, http_mock):
    _, _, engine = env
    http_mock(
        lambda req: httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "vendor/text",
                        "architecture": {"output_modalities": ["text"]},
                        "pricing": {"prompt": "0.000001", "completion": "0.000002"},
                    },
                    {"id": "vendor/image", "architecture": {"output_modalities": ["image"]}},
                ]
            },
        )
    )
    rows = engine.models.catalog()
    assert len(rows) == 1
    assert rows[0]["input_per_million"] == 1
    assert rows[0]["output_per_million"] == 2


def test_openai_responses_and_usage(env, http_mock):
    config, _, engine = env
    config.save_key("openai", "test-openai")

    def handler(req):
        assert str(req.url) == "https://api.openai.com/v1/responses"
        body = json.loads(req.content)
        assert body["store"] is False
        assert body["model"] == "chosen-text-model"
        return httpx.Response(
            200,
            text='data: {"type":"response.output_text.delta","delta":"Hello"}\n\ndata: {"type":"response.completed","response":{"model":"chosen-text-model","usage":{"input_tokens":3,"output_tokens":1}}}\n\n',
        )

    http_mock(handler)
    assert (
        "".join(engine.models.generate("system", "prompt", "openai", "chosen-text-model"))
        == "Hello"
    )
    assert engine.models.usage["input_tokens"] == 3


@pytest.mark.parametrize(
    "body",
    [
        'data: {"error":{"message":"secret"}}\n\n',
        'data: {"choices":[{"delta":{},"finish_reason":"length"}]}\n\n',
        "data: [DONE]\n\n",
        "data: not-json\n\n",
    ],
)
def test_bad_streams_never_accepted(body, http_mock):
    http_mock(lambda req: httpx.Response(200, text=body))
    with pytest.raises(CliError) as error:
        list(stream("https://openrouter.ai/api/v1/chat/completions", {}))
    assert "secret" not in str(error.value)


def test_sse_multiline_comments_and_eof():
    assert list(sse_events([": ping", "data: {", 'data: "a":1}', "", "data: [DONE]"])) == [
        '{\n"a":1}',
        "[DONE]",
    ]


def test_terminal_controls_removed():
    assert safe("\x1b[2Jhello\x1b]52;clipboard\x07\u202eevil") == "helloevil"


def test_cli_command_flow_persists_and_exports(env, tmp_path):
    config, store, engine = env
    for command in ('workspace create "Demo project"', 'task add "Draft a proposal" --kind write'):
        import shlex

        execute(parser().parse_args(shlex.split(command)), config, store, engine)
    assert store.rows("SELECT title FROM tasks")[0]["title"] == "Draft a proposal"
    mid = store.meeting(engine.workspace()["id"], "Example", "Me: Hello")
    target = tmp_path / "meeting.md"
    execute(
        parser().parse_args(["meetings", "export", str(mid), str(target)]), config, store, engine
    )
    assert "Me: Hello" in target.read_text()
    with pytest.raises(CliError, match="target exists"):
        execute(
            parser().parse_args(["meetings", "export", str(mid), str(target)]),
            config,
            store,
            engine,
        )


def test_search_answer_retains_exa_source_urls(env, monkeypatch):
    _, _, engine = env
    monkeypatch.setattr(
        "adversaria_cli.engine.search",
        lambda *args: [
            {
                "title": "Speech docs",
                "url": "https://openrouter.ai/docs/guides/overview/multimodal/stt",
                "text": "JSON transcription endpoint.",
            }
        ],
    )
    monkeypatch.setattr(
        engine.models, "generate", lambda *args, **kwargs: iter(["It returns JSON [1]."])
    )
    answer = "".join(engine.answer("How does ASR work?", web=True))
    assert "[1] Speech docs — https://openrouter.ai/docs/guides/overview/multimodal/stt" in answer
