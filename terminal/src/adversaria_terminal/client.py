"""HTTP client for the existing Python ML service (FastAPI on :9876).

The terminal talks to the SAME service the desktop app uses — no new backend.
All endpoints mirror `python-service/src/server.py`; error bodies are
translated to human sentences exactly like the Rust `http_client.rs` does.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence

import httpx

from .models import HealthInfo, TemplateInfo, WhisperModelInfo


class ServiceError(RuntimeError):
    """A non-recoverable service error with a human message."""

    def __init__(self, message: str, *, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.code = code
        self.status = status


def _translate(detail) -> str:
    """Turn FastAPI `detail` (string, or `{code, message}` dict) into a sentence."""
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail") or str(detail)
        return f"{message}"
    if isinstance(detail, (list, tuple)) and detail:
        parts = []
        for item in detail:
            loc = ".".join(str(p) for p in item.get("loc", [])) if isinstance(item, dict) else ""
            msg = item.get("msg", str(item)) if isinstance(item, dict) else str(item)
            parts.append(f"{loc}: {msg}" if loc else str(msg))
        return "; ".join(parts)
    return str(detail)


def _raise_for(resp: httpx.Response) -> None:
    if resp.is_success:
        return
    try:
        body = resp.json()
        detail = body.get("detail", resp.text)
    except Exception:
        detail = resp.text or f"HTTP {resp.status_code}"
    raise ServiceError(_translate(detail), status=resp.status_code)


class ServiceClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # -- health -----------------------------------------------------------

    def health(self) -> HealthInfo:
        try:
            resp = httpx.get(f"{self.base_url}/health", timeout=5.0)
        except httpx.HTTPError as exc:
            raise ServiceError(f"Python service unreachable at {self.base_url} ({exc.__class__.__name__})") from exc
        _raise_for(resp)
        data = resp.json()
        return HealthInfo(
            status=data.get("status", "unknown"),
            whisper_model=data.get("whisper_model", "N/A"),
            ollama_available=bool(data.get("ollama_available", False)),
            transcriber_state=data.get("transcriber_state", "unknown"),
            transcriber_detail=data.get("transcriber_detail"),
            embedder_state=data.get("embedder_state"),
            embedder_detail=data.get("embedder_detail"),
            live_captions_state=data.get("live_captions_state"),
        )

    # -- templates --------------------------------------------------------

    def list_templates(self) -> list[TemplateInfo]:
        resp = httpx.get(f"{self.base_url}/templates", timeout=10.0)
        _raise_for(resp)
        return [TemplateInfo(name=i.get("name", ""), description=i.get("description", "")) for i in resp.json()]

    # -- transcription ----------------------------------------------------

    def transcribe(
        self,
        *,
        audio_path: str | None = None,
        mic_audio_path: str | None = None,
        me_label: str | None = None,
        vocabulary: str | None = None,
        diarize: bool = True,
        single_file: bool = False,
        whisper_model: str | None = None,
    ) -> dict:
        payload: dict = {
            "diarize": diarize,
            "single_file": single_file,
        }
        if audio_path:
            payload["audio_path"] = audio_path
        if mic_audio_path:
            payload["mic_audio_path"] = mic_audio_path
        if me_label:
            payload["me_label"] = me_label
        if vocabulary:
            payload["vocabulary"] = vocabulary
        if whisper_model:
            payload["whisper_model"] = whisper_model
        resp = httpx.post(f"{self.base_url}/transcribe", json=payload, timeout=3600)
        _raise_for(resp)
        return resp.json()

    # -- summarization ----------------------------------------------------

    def summarize(
        self,
        transcript: str,
        *,
        template_name: str = "general",
        model: str | None = None,
        output_language: str | None = None,
        user_notes: str | None = None,
        meeting_date: str | None = None,
        known_attendees: Sequence[str] | None = None,
        auto_template: bool = False,
    ) -> dict:
        payload: dict = {
            "transcript": transcript,
            "template_name": template_name,
            "auto_template": auto_template,
        }
        if model:
            payload["model"] = model
        if output_language:
            payload["output_language"] = output_language
        if user_notes:
            payload["user_notes"] = user_notes
        if meeting_date:
            payload["meeting_date"] = meeting_date
        if known_attendees:
            payload["known_attendees"] = list(known_attendees)
        resp = httpx.post(f"{self.base_url}/summarize", json=payload, timeout=3600)
        _raise_for(resp)
        return resp.json()

    # -- chat (grounded Q&A, streamed) ------------------------------------

    def chat_stream(
        self, transcript: str, question: str, *, model: str | None = None
    ) -> Iterator[tuple[str, str]]:
        """Yield (kind, value): ('text', token)…, ('done', ''), ('error', msg)."""
        payload: dict = {"transcript": transcript, "question": question}
        if model:
            payload["model"] = model
        with httpx.stream(
            "POST", f"{self.base_url}/chat_stream", json=payload, timeout=None
        ) as resp:
            if resp.status_code != 200:
                _raise_for(resp)
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[len("data: ") :].strip()
                if data == "[DONE]":
                    yield ("done", "")
                    return
                try:
                    frame = json.loads(data)
                except json.JSONDecodeError:
                    continue
                if "t" in frame:
                    yield ("text", frame["t"])
                elif "error" in frame:
                    yield ("error", frame["error"])

    # -- models -----------------------------------------------------------

    def whisper_models(self) -> list[WhisperModelInfo]:
        resp = httpx.get(f"{self.base_url}/whisper_models", timeout=10.0)
        _raise_for(resp)
        return [
            WhisperModelInfo(
                key=i.get("key", ""),
                label=i.get("label", ""),
                size=i.get("size", ""),
                downloaded=bool(i.get("downloaded", False)),
            )
            for i in resp.json()
        ]

    def whisper_download(self, key: str) -> None:
        resp = httpx.post(f"{self.base_url}/whisper_download", json={"model": key}, timeout=86400)
        _raise_for(resp)

    # -- live captions ----------------------------------------------------

    def live_feed(
        self, audio_path: str, session: int, source: str
    ) -> tuple[list[str], list[str], str]:
        payload = {"audio_path": audio_path, "session": session, "source": source}
        resp = httpx.post(f"{self.base_url}/live_feed", json=payload, timeout=30.0)
        _raise_for(resp)
        data = resp.json()
        return (
            data.get("captions", []),
            data.get("caption_boundaries", []),
            data.get("partial", "") or "",
        )

    # -- templates admin --------------------------------------------------

    def get_template(self, name: str) -> str:
        resp = httpx.get(f"{self.base_url}/templates/{name}", timeout=10.0)
        _raise_for(resp)
        return resp.json().get("content", "")


def transcribe_and_summarize(
    client: ServiceClient,
    *,
    audio_path: str | None,
    mic_audio_path: str | None,
    me_label: str | None,
    vocabulary: str | None,
    diarize: bool,
    whisper_model: str | None,
    template_name: str,
    model: str | None,
    output_language: str | None,
    single_file: bool = False,
    recorded_at: str | None = None,
) -> dict:
    """Run the full transcribe -> summarize pipeline, returning a dict ready
    to be stored as a Meeting (with title/summary/transcript/etc.)."""
    t = client.transcribe(
        audio_path=audio_path,
        mic_audio_path=mic_audio_path,
        me_label=me_label,
        vocabulary=vocabulary,
        diarize=diarize,
        whisper_model=whisper_model,
        single_file=single_file,
    )
    transcript = t.get("text", "")
    s = client.summarize(
        transcript,
        template_name=template_name,
        model=model,
        output_language=output_language,
        meeting_date=(recorded_at or "")[:10] or None,
    )
    return {
        "title": s.get("title") or t.get("category_hint") or "Untitled meeting",
        "summary": s.get("summary", ""),
        "transcript": transcript,
        "language": t.get("language", ""),
        "duration_seconds": t.get("duration_seconds", 0.0),
        "template_used": s.get("template_used") or template_name,
        "category": s.get("category") or t.get("category_hint") or "",
        "attendees": s.get("attendees") or [],
    }