"""OpenAI file and realtime transcription; no local ML runtime required."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from websockets.exceptions import WebSocketException
from websockets.sync.client import connect

from .config import CliError
from .transport import request


def openai_key(config):
    key = config.key("openai")
    if not key:
        raise CliError(
            "Transcription needs an OpenAI key: adversaria auth openai (or OPENAI_API_KEY)."
        )
    return key


def speech_key(config):
    provider = config.values["speech_provider"]
    key = config.key(provider)
    if not key:
        raise CliError(f"Transcription needs a {provider} key: adversaria auth {provider}.")
    return key


def create_transcriber(config, emit):
    if config.values["speech_provider"] == "openrouter":
        from .speech_turns import RouterTranscriber

        return RouterTranscriber(config, emit)
    return RealtimeTranscriber(config, emit)


def transcribe_file(config, path):
    provider = config.values["speech_provider"]
    key = speech_key(config)
    path = Path(path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise CliError("Audio path must be a file.")

    def upload(file):
        with file.open("rb") as audio:
            return request(
                "POST",
                (
                    "https://openrouter.ai/api/v1"
                    if provider == "openrouter"
                    else "https://api.openai.com/v1"
                )
                + "/audio/transcriptions",
                timeout=300,
                headers={"Authorization": "Bearer " + key},
                data={
                    "model": config.values["openrouter_speech_model"]
                    if provider == "openrouter"
                    else config.values["transcription_model"]
                },
                files={"file": (file.name, audio)},
            )

    if path.stat().st_size < 24_000_000:
        return upload(path)
    if not shutil.which("ffmpeg"):
        raise CliError(
            "Files over 24 MB need ffmpeg to split audio into upload-sized parts. Install ffmpeg, then retry."
        )
    # Temporary derived audio only. The caller's original recording is never deleted.
    with tempfile.TemporaryDirectory(prefix="adversaria-upload-") as directory:
        output = Path(directory) / "part-%04d.mp3"
        result = subprocess.run(
            [
                "ffmpeg",
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(path),
                "-map",
                "0:a:0",
                "-ac",
                "1",
                "-ar",
                "24000",
                "-b:a",
                "48k",
                "-f",
                "segment",
                "-segment_time",
                "600",
                str(output),
            ],
            capture_output=True,
            timeout=600,
            check=False,
        )
        if result.returncode:
            raise CliError("ffmpeg could not split this audio file. Check its format.")
        chunks = sorted(Path(directory).glob("part-*.mp3"))
        if not chunks:
            raise CliError("No audio found in this file.")
        parts = [upload(chunk).get("text", "") for chunk in chunks]
        return {"text": "\n".join(parts), "chunks": len(parts)}


class TranscriptOrder:
    """Completion events can arrive out of order; emit in commit order."""

    def __init__(self, emit):
        self.emit = emit
        self.order, self.finals = [], {}
        self.cursor = 0

    def event(self, event):
        kind, item = event.get("type"), event.get("item_id")
        if kind == "input_audio_buffer.committed" and item not in self.order:
            self.order.append(item)
        elif kind == "conversation.item.input_audio_transcription.completed":
            if item in self.order[: self.cursor]:
                return
            self.finals[item] = event.get("transcript", "")
        while self.cursor < len(self.order) and self.order[self.cursor] in self.finals:
            text = self.finals.pop(self.order[self.cursor])
            self.cursor += 1
            if text.strip():
                self.emit(text)

    @property
    def pending(self):
        return self.cursor < len(self.order)


class RealtimeTranscriber:
    def __init__(self, config, emit):
        self.config, self.emit = config, emit
        self.socket = None
        self.thread = None
        self.closed = threading.Event()
        self.flush_ack = threading.Event()
        self.failure = None
        self.order = TranscriptOrder(emit)
        self.rate_state = None

    def start(self):
        key = openai_key(self.config)
        try:
            self.socket = connect(
                "wss://api.openai.com/v1/realtime?intent=transcription",
                additional_headers={"Authorization": "Bearer " + key},
                proxy=None,
                open_timeout=10,
                close_timeout=3,
            )
            self.socket.send(
                json.dumps(
                    {
                        "type": "session.update",
                        "session": {
                            "type": "transcription",
                            "audio": {
                                "input": {
                                    "format": {"type": "audio/pcm", "rate": 24000},
                                    "transcription": {"model": self.config.values["live_model"]},
                                    "turn_detection": {
                                        "type": "server_vad",
                                        "threshold": 0.5,
                                        "prefix_padding_ms": 300,
                                        "silence_duration_ms": 700,
                                    },
                                }
                            },
                        },
                    }
                )
            )
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                event = json.loads(self.socket.recv(timeout=max(0.1, deadline - time.monotonic())))
                if event.get("type") == "session.updated":
                    break
                if event.get("type") == "error":
                    raise CliError(
                        "OpenAI rejected the transcription session. Check key access and speech model settings."
                    )
            else:
                raise CliError("OpenAI did not acknowledge the transcription session.")
            self.thread = threading.Thread(target=self._receive, daemon=True)
            self.thread.start()
        except (OSError, TimeoutError, WebSocketException, ValueError, CliError) as exc:
            if self.socket:
                self.socket.close()
            if isinstance(exc, CliError):
                raise
            raise CliError(
                f"Cannot start OpenAI realtime transcription ({type(exc).__name__}). Check auth openai."
            ) from exc

    def _receive(self):
        try:
            while not self.closed.is_set():
                try:
                    event = json.loads(self.socket.recv(timeout=0.5))
                except TimeoutError:
                    continue
                if event.get("type") == "error":
                    if event.get("error", {}).get("code") == "input_audio_buffer_commit_empty":
                        continue
                    raise CliError(
                        "OpenAI realtime transcription returned an error; audio is preserved for retry."
                    )
                if event.get("type") == "conversation.item.input_audio_transcription.failed":
                    raise CliError(
                        "An audio turn failed transcription; audio is preserved for retry."
                    )
                self.order.event(event)
                if event.get("type") == "session.updated":
                    self.flush_ack.set()
        except (WebSocketException, ValueError, OSError, CliError) as exc:
            if not self.closed.is_set():
                self.failure = (
                    str(exc) if isinstance(exc, CliError) else "Realtime connection interrupted."
                )

    def send(self, pcm, rate):
        if self.failure:
            raise CliError(self.failure)
        import audioop

        converted, self.rate_state = audioop.ratecv(pcm, 2, 1, rate, 24000, self.rate_state)
        try:
            self.socket.send(
                json.dumps(
                    {
                        "type": "input_audio_buffer.append",
                        "audio": base64.b64encode(converted).decode("ascii"),
                    }
                )
            )
        except (WebSocketException, OSError) as exc:
            raise CliError(
                "Realtime audio connection interrupted. Audio is preserved for retry."
            ) from exc

    def finish(self):
        try:
            if self.failure:
                raise CliError(self.failure)
            self.flush_ack.clear()
            self.socket.send(json.dumps({"type": "input_audio_buffer.commit"}))
            # Protocol barrier: its acknowledgement follows the final commit,
            # unlike a late VAD commit already in flight when finish() starts.
            self.socket.send(
                json.dumps({"type": "session.update", "session": {"type": "transcription"}})
            )
            deadline = time.monotonic() + 25
            while time.monotonic() < deadline:
                if self.failure:
                    raise CliError(self.failure)
                if self.flush_ack.is_set() and not self.order.pending:
                    return
                time.sleep(0.05)
            raise CliError("Final transcript timed out. Audio is preserved for retry.")
        finally:
            self.abort()

    def abort(self):
        self.closed.set()
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join(timeout=4)
