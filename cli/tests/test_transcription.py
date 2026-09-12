import base64
import json
import queue
import wave

import httpx
import pytest

from adversaria_cli.audio import Recorder
from adversaria_cli.config import CliError
from adversaria_cli.transcription import RealtimeTranscriber, TranscriptOrder


def test_file_upload_uses_openai_and_never_local_service(env, http_mock, tmp_path):
    config, _, engine = env
    config.save(speech_provider="openai")
    config.save_key("openai", "test-openai")
    file = tmp_path / "test.wav"
    file.write_bytes(b"test-audio-fixture")

    def handler(req):
        assert str(req.url) == "https://api.openai.com/v1/audio/transcriptions"
        assert req.headers["authorization"] == "Bearer test-openai"
        assert b"gpt-transcribe" in req.content
        assert b"test-audio-fixture" in req.content
        return httpx.Response(200, json={"text": "I will write the proposal."})

    http_mock(handler)
    mid, data = engine.transcribe(file)
    assert mid == 1
    assert file.exists()  # Imported originals are never deleted.
    assert data["text"] == "I will write the proposal."


def test_empty_transcription_is_not_saved(env, http_mock, tmp_path):
    config, store, engine = env
    config.save(speech_provider="openai")
    config.save_key("openai", "test-key")
    file = tmp_path / "empty.wav"
    file.touch()
    http_mock(lambda req: httpx.Response(200, json={"text": ""}))
    with pytest.raises(CliError, match="No speech"):
        engine.transcribe(file)
    assert store.rows("SELECT * FROM meetings") == []


def test_transcript_completion_order_and_duplicates():
    emitted = []
    order = TranscriptOrder(emitted.append)
    for item in ("a", "b"):
        order.event({"type": "input_audio_buffer.committed", "item_id": item})
    order.event(
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "b",
            "transcript": "second",
        }
    )
    assert emitted == []
    order.event(
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "a",
            "transcript": "first",
        }
    )
    order.event(
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "a",
            "transcript": "first",
        }
    )
    assert emitted == ["first", "second"]
    assert not order.pending


class Socket:
    def __init__(self):
        self.events = queue.Queue()
        self.sent = []
        self.closed = False

    def send(self, raw):
        frame = json.loads(raw)
        self.sent.append(frame)
        if frame["type"] == "session.update":
            self.events.put(json.dumps({"type": "session.updated"}))
        if frame["type"] == "input_audio_buffer.commit":
            self.events.put(json.dumps({"type": "input_audio_buffer.committed", "item_id": "a"}))
            self.events.put(
                json.dumps(
                    {
                        "type": "conversation.item.input_audio_transcription.completed",
                        "item_id": "a",
                        "transcript": "I will create a diagram.",
                    }
                )
            )

    def recv(self, timeout=None):
        try:
            return self.events.get(timeout=timeout)
        except queue.Empty as exc:
            raise TimeoutError from exc

    def close(self):
        self.closed = True


def test_realtime_protocol_resampling_and_flush(env, monkeypatch):
    config, _, _ = env
    config.save_key("openai", "test-key")
    socket = Socket()

    def connect(url, **kwargs):
        assert url == "wss://api.openai.com/v1/realtime?intent=transcription"
        assert kwargs["additional_headers"]["Authorization"] == "Bearer test-key"
        return socket

    monkeypatch.setattr("adversaria_cli.transcription.connect", connect)
    emitted = []
    realtime = RealtimeTranscriber(config, emitted.append)
    realtime.start()
    realtime.send(bytes(48000 * 2), 48000)
    realtime.finish()
    assert emitted == ["I will create a diagram."]
    session = socket.sent[0]["session"]
    assert session["type"] == "transcription"
    assert session["audio"]["input"]["transcription"]["model"] == "gpt-live-transcribe"
    assert len(base64.b64decode(socket.sent[1]["audio"])) == 48000
    assert socket.closed


def test_realtime_start_rejection_closes_socket(env, monkeypatch):
    config, _, _ = env
    config.save_key("openai", "test-key")
    socket = Socket()
    socket.events.put('{"type":"error","error":{"message":"private-details"}}')
    monkeypatch.setattr("adversaria_cli.transcription.connect", lambda *a, **kw: socket)
    with pytest.raises(CliError, match="rejected") as error:
        RealtimeTranscriber(config, print).start()
    assert "private-details" not in str(error.value)
    assert socket.closed


def test_audio_capture_does_not_need_a_local_model(env, monkeypatch):
    config, _, _ = env
    config.save_key("openrouter", "test-key")
    import sounddevice

    class FakeInput:
        def __init__(self, **kwargs):
            self.callback = kwargs["callback"]

        def start(self):
            self.callback(bytes(48000), 24000, None, None)
            self.callback(bytes(48000), 24000, None, None)

        def stop(self):
            pass

        def close(self):
            pass

    class FakeRealtime:
        def __init__(self, config, emit):
            self.emit = emit

        def start(self):
            pass

        def send(self, data, rate):
            assert rate == 48000

        def finish(self):
            self.emit("I will write the report.")

        def abort(self):
            pass

    monkeypatch.setattr(sounddevice, "query_devices", lambda *a: {"default_samplerate": 48000})
    monkeypatch.setattr(sounddevice, "RawInputStream", FakeInput)
    monkeypatch.setattr("adversaria_cli.audio.create_transcriber", FakeRealtime)
    captions = []
    recorder = Recorder(config, lambda *args: captions.append(args), lambda text: None)
    recorder.start()
    paths = recorder.stop()
    with wave.open(str(paths["Me"])) as wav:
        assert wav.getnframes() == 48000
    assert captions == [("I will write the report.", "Me", "silence")]
    assert recorder.errors == []
    recorder.cleanup()
    assert not paths["Me"].exists()
