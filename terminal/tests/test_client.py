"""Unit tests for the HTTP service client (no real network)."""

from __future__ import annotations

import contextlib
import json

import httpx

from adversaria_terminal import client as cli
from adversaria_terminal.models import HealthInfo


class _FixtureResponse:
    """Minimal stand-in for httpx.Response used by `_raise_for` / `json()`."""

    def __init__(self, status_code: int, body=None, text: str = ""):
        self.status_code = status_code
        self._body = body if body is not None else text
        self.text = text

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def json(self):
        return self._body


def test_translate_dict_detail():
    assert cli._translate({"code": "NO_MODEL", "message": "Model missing"}) == "Model missing"


def test_translate_plain_string():
    assert cli._translate("boom") == "boom"


def test_translate_validation_list():
    detail = [{"loc": ["body", "audio_path"], "msg": "field required"}]
    assert "audio_path" in cli._translate(detail)


def test_raise_for_ok():
    cli._raise_for(_FixtureResponse(200, {"ok": True}))


def test_raise_for_error_raises_service_error():
    import pytest

    with pytest.raises(cli.ServiceError) as exc_info:
        cli._raise_for(_FixtureResponse(503, {"detail": "No transcription model"}))
    assert exc_info.value.status == 503
    assert "No transcription model" in str(exc_info.value)


def test_health_parses_payload(monkeypatch):
    payload = {
        "status": "degraded",
        "whisper_model": "N/A",
        "ollama_available": True,
        "transcriber_state": "missing",
        "transcriber_detail": "No model",
        "embedder_state": "ready",
        "live_captions_state": "missing",
    }

    def fake_get(url, timeout=None):
        assert url.endswith("/health")
        return _FixtureResponse(200, payload)

    monkeypatch.setattr(httpx, "get", fake_get)
    health: HealthInfo = cli.ServiceClient("http://x:9876").health()
    assert health.status == "degraded"
    assert health.whisper_model == "N/A"
    assert health.ollama_available is True
    assert health.ready is False


def test_live_feed_payload_roundtrip(monkeypatch):
    captured = {}

    class _StreamResp:
        status_code = 200

        def iter_lines(self):
            yield "data: [DONE]"

        def json(self):
            return {}

    def fake_stream(method, url, json=None, timeout=None):
        captured["method"], captured["url"], captured["json"] = method, url, json
        return contextlib.nullcontext(_StreamResp())

    monkeypatch.setattr(cli.httpx, "stream", fake_stream)
    frames = list(cli.ServiceClient("http://x:9876").chat_stream("t", "q?"))
    assert frames == [("done", "")]
    assert captured["json"]["transcript"] == "t"
    assert captured["json"]["question"] == "q?"


def test_chat_stream_deltas_are_forwarded(monkeypatch):
    chunks = [
        {"t": "he"},
        {"t": "llo"},
        {"error": "bad thing"},
    ]

    class _Iter:
        def __iter__(self):
            for c in chunks:
                yield "data: " + json.dumps(c)
            yield "data: [DONE]"

    class _StreamResp:
        status_code = 200

        def iter_lines(self):
            return _Iter()

        def json(self):
            return {}

    def fake_stream(method, url, json=None, timeout=None):
        return contextlib.nullcontext(_StreamResp())

    monkeypatch.setattr(cli.httpx, "stream", fake_stream)
    frames = list(cli.ServiceClient("http://x:9876").chat_stream("t", "q?"))
    assert frames == [
        ("text", "he"),
        ("text", "llo"),
        ("error", "bad thing"),
        ("done", ""),
    ]