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


@pytest.mark.parametrize("question", ["What is AI Tinkerers?", "what is ai tinkerers"])
def test_question_about_another_organization_does_not_retrieve_hamzas_project(env, question):
    _, store, engine = env
    workspace = engine.workspace()
    store.meeting(
        workspace["id"],
        "Adversaria",
        "Here is what Hamza is building. Adversaria is Hamza's AI project at Laghari Labs.",
    )
    assert store.context(workspace["id"], question) == ""
    assert "Hamza" in store.context(workspace["id"], "What is Adversaria?")


@pytest.mark.parametrize("name", ["AI Tinkerers", "AITinkerers"])
def test_retrieval_keeps_the_named_organization_and_workspace_scope(env, name):
    _, store, engine = env
    workspace = engine.workspace()
    store.meeting(workspace["id"], "Community", f"{name} hosts demos for AI builders.")
    store.meeting(workspace["id"], "Project", "What I built: an AI meeting assistant.")
    other = store.workspace("Unrelated workspace")
    store.meeting(other["id"], "Private", "AI Tinkerers confidential planning notes.")
    context = store.context(workspace["id"], "What is AI Tinkerers?")
    assert "hosts demos" in context
    assert "meeting assistant" not in context
    assert "confidential" not in context


def test_explicit_no_web_answer_never_searches(env, monkeypatch):
    _, store, engine = env
    store.meeting(engine.workspace()["id"], "Project", "What Hamza built: an AI assistant.")
    monkeypatch.setattr(
        "adversaria_cli.engine.search", lambda *args: pytest.fail("Unexpected web search")
    )
    prompts = []

    def generate(system, prompt, *args):
        prompts.append(prompt)
        yield "AI Tinkerers is a community for people building with AI."

    monkeypatch.setattr(engine.models, "generate", generate)
    answer = "".join(engine.answer("What is AI Tinkerers?", web=False))
    assert "community" in answer
    assert "What is AI Tinkerers?" in prompts[0]
    assert "What Hamza built" not in prompts[0]


def test_external_question_searches_exa_without_sending_meeting_context(env, monkeypatch):
    config, store, engine = env
    config.save_key("exa", "synthetic-exa-key")
    ws = engine.workspace()
    store.meeting(ws["id"], "Project", "What Hamza built: an AI assistant.")
    queries, statuses = [], []

    def search(config, question):
        queries.append(question)
        return [
            {
                "title": "AI Tinkerers",
                "url": "https://aitinkerers.org",
                "text": "A community for AI builders.",
            }
        ]

    def generate(system, prompt, *args):
        assert "A community for AI builders" in prompt
        assert "What Hamza built" not in prompt
        yield "AI Tinkerers is a community for AI builders."

    monkeypatch.setattr("adversaria_cli.engine.search", search)
    monkeypatch.setattr(engine.models, "generate", generate)
    answer = "".join(
        engine.answer(
            "What is AI Tinkerers?",
            turns=["Me: Private client discussion."],
            on_status=statuses.append,
        )
    )
    assert queries == ["What is AI Tinkerers?"]
    assert statuses == ["Searching Exa…"]
    assert "https://aitinkerers.org" in answer


@pytest.mark.parametrize(
    "question",
    [
        "What did we decide about AI Tinkerers?",
        "What is my project?",
        "What should I say next?",
        "Who is in our meeting?",
    ],
)
def test_personal_and_meeting_questions_do_not_automatically_search(env, monkeypatch, question):
    config, _, engine = env
    config.save_key("exa", "synthetic-exa-key")
    monkeypatch.setattr(
        "adversaria_cli.engine.search", lambda *args: pytest.fail("Private query sent to Exa")
    )
    monkeypatch.setattr(
        engine.models, "generate", lambda *args: iter(["I need the meeting context."])
    )
    assert "meeting context" in "".join(engine.answer(question))


def test_relevant_local_evidence_avoids_unnecessary_web_search(env, monkeypatch):
    config, store, engine = env
    config.save_key("exa", "synthetic-exa-key")
    store.meeting(
        engine.workspace()["id"], "Community", "AI Tinkerers hosts demos for AI builders."
    )
    monkeypatch.setattr(
        "adversaria_cli.engine.search", lambda *args: pytest.fail("Unnecessary search")
    )
    monkeypatch.setattr(
        engine.models, "generate", lambda *args: iter(["AI Tinkerers hosts demos."])
    )
    assert "hosts demos" in "".join(engine.answer("What is AI Tinkerers?"))


def test_current_external_question_refreshes_local_evidence(env, monkeypatch):
    config, store, engine = env
    config.save_key("exa", "synthetic-exa-key")
    store.meeting(engine.workspace()["id"], "Community", "AI Tinkerers events from 2024.")
    queries = []
    monkeypatch.setattr(
        "adversaria_cli.engine.search", lambda config, question: queries.append(question) or []
    )
    monkeypatch.setattr(engine.models, "generate", lambda *args: iter(["No current events found."]))
    list(engine.answer("What are the latest AI Tinkerers events?"))
    assert queries == ["What are the latest AI Tinkerers events?"]


def test_missing_auto_search_key_is_actionable_and_does_not_guess(env, monkeypatch):
    _, _, engine = env
    monkeypatch.setattr(engine.models, "generate", lambda *args: pytest.fail("Should not guess"))
    with pytest.raises(CliError, match="Exa has no key"):
        list(engine.answer("What is AI Tinkerers?"))


def test_ask_web_flags_preserve_auto_default():
    assert parser().parse_args(["ask", "What is AI Tinkerers?"]).web is None
    assert parser().parse_args(["ask", "--web", "What is AI Tinkerers?"]).web is True
    assert parser().parse_args(["ask", "--no-web", "What is AI Tinkerers?"]).web is False
