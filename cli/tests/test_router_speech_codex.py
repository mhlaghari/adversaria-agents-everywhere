import base64
import json
import struct

import httpx
import pytest

from adversaria_cli.config import CliError
from adversaria_cli.copilot import Copilot
from adversaria_cli.speech_turns import AudioTurns, RouterTranscriber


def speech(seconds, rate=16000):
    return struct.pack("<h", 2000) * int(rate * seconds)


def test_silence_gate_and_forced_turn_closure():
    turns = AudioTurns(16000)
    assert list(turns.feed(bytes(32000))) == []
    result = list(turns.feed(speech(1) + bytes(32000)))
    assert len(result) == 1 and result[0][1] == "silence"
    turns = AudioTurns(16000)
    result = list(turns.feed(speech(4)))
    assert result[0][1] == "forced"
    assert list(turns.feed(bytes(32000))) == [(b"", "silence")]
    copilot = Copilot()
    assert copilot.feed("I will write the draft.", boundary="forced") == (None, None)
    assert copilot.feed("", boundary="silence")[0].kind == "write"


def test_router_speech_uses_router_key_and_wav(env, http_mock):
    config, _, _ = env
    config.save_key("openrouter", "test-router-key")
    calls = []

    def handler(req):
        calls.append(req)
        assert str(req.url) == "https://openrouter.ai/api/v1/audio/transcriptions"
        assert req.headers["authorization"] == "Bearer test-router-key"
        payload = json.loads(req.content)
        assert payload["model"] == "openai/gpt-transcribe"
        assert base64.b64decode(payload["input_audio"]["data"]).startswith(b"RIFF")
        return httpx.Response(200, json={"text": "I will draft it by Friday."})

    http_mock(handler)
    emitted = []
    transcriber = RouterTranscriber(config, lambda *args: emitted.append(args))
    transcriber.start()
    transcriber.send(speech(1) + bytes(32000), 16000)
    transcriber.finish()
    assert emitted == [("I will draft it by Friday.", "silence")]
    assert len(calls) == 1


def test_router_file_upload_needs_no_openai_key(env, http_mock, tmp_path):
    config, _, engine = env
    config.save_key("openrouter", "test-router-key")
    file = tmp_path / "voice.wav"
    file.write_bytes(b"synthetic-wav")

    def handler(req):
        assert req.url.host == "openrouter.ai"
        assert b"openai/gpt-transcribe" in req.content
        return httpx.Response(200, json={"text": "Cloud transcript"})

    http_mock(handler)
    assert engine.transcribe(file)[1]["text"] == "Cloud transcript"


def test_codex_engine_uses_logged_in_cli_without_api_secrets(env, monkeypatch):
    _, store, engine = env
    from pathlib import Path

    class Process:
        returncode = 0

        def __init__(self, args, **kwargs):
            assert args[:2] == ["/fake/codex", "exec"]
            assert args[args.index("--sandbox") + 1] == "read-only"
            assert "--ignore-user-config" in args and "--ephemeral" in args
            assert not any(
                key in kwargs["env"]
                for key in ("OPENAI_API_KEY", "OPENROUTER_API_KEY", "EXA_API_KEY")
            )
            self.output = Path(args[args.index("-o") + 1])

        def communicate(self, prompt, timeout):
            assert "Do the task" in prompt
            self.output.write_text("A completed Codex draft.")
            return json.dumps({"type": "turn.completed", "usage": {"input_tokens": 12}}), ""

    monkeypatch.setattr("shutil.which", lambda name: "/fake/codex")
    monkeypatch.setattr("adversaria_cli.codex_engine.subprocess.Popen", Process)
    task = store.add_task(engine.workspace()["id"], "Do the task", "write")
    assert "Codex draft" in "".join(engine.run_task(task, "codex"))
    assert store.task(task)["status"] == "awaiting_review"
    assert engine.models.usage["input_tokens"] == 12


def test_codex_failure_does_not_accept_output(env, monkeypatch):
    _, store, engine = env

    class Process:
        returncode = 1

        def __init__(self, *a, **kw):
            pass

        def communicate(self, *a, **kw):
            return '{"type":"turn.failed","error":{"message":"secret"}}', "private stderr"

    monkeypatch.setattr("shutil.which", lambda name: "/fake/codex")
    monkeypatch.setattr("adversaria_cli.codex_engine.subprocess.Popen", Process)
    task = store.add_task(engine.workspace()["id"], "Do the task", "write")
    with pytest.raises(CliError, match="could not complete"):
        list(engine.run_task(task, "codex"))
    assert store.task(task)["status"] == "failed"


def test_complete_question_in_timed_fragment_triggers_without_silence():
    copilot = Copilot()
    text = "Hey, what's happening? What's LLM?"
    caught, question = copilot.feed(text, boundary="forced")
    assert caught is None
    assert question == text
    assert copilot.feed("", boundary="silence") == (None, None)
    assert copilot.feed(text, boundary="silence") == (None, None)


def test_asr_requests_overlap_but_captions_remain_in_order(env, monkeypatch):
    import threading

    config, _, _ = env
    config.save_key("openrouter", "test-key")
    first_started, second_started, release = (threading.Event() for _ in range(3))
    lock = threading.Lock()
    calls = []

    def transcribe(self, pcm, rate):
        with lock:
            index = len(calls)
            calls.append(index)
        if index == 0:
            first_started.set()
            assert release.wait(3)
            return "First caption"
        second_started.set()
        return "Second caption"

    monkeypatch.setattr(RouterTranscriber, "_transcribe", transcribe)
    emitted = []
    transcriber = RouterTranscriber(config, lambda *args: emitted.append(args))
    try:
        transcriber.start()
        transcriber.send(speech(4), 16000)
        assert first_started.wait(1)
        # send returned while request 1 is still in flight; request 2 can finish first.
        transcriber.send(speech(4), 16000)
        assert second_started.wait(1)
        assert emitted == []
        release.set()
        transcriber.finish()
        assert emitted == [
            ("First caption", "forced"),
            ("Second caption", "forced"),
            ("", "silence"),
        ]
    finally:
        release.set()
        transcriber.abort()
