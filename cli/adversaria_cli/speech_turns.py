"""Speech turns for OpenRouter STT: silence segmentation, no local ML model."""

import base64
import io
import wave
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError

from .config import CliError
from .transport import request


class AudioTurns:
    """PCM16 energy gate, 300ms pre-roll, 400ms silence, 4s forced fragments."""

    def __init__(self, rate):
        self.rate = rate
        self.frame_bytes = round(rate * 0.02) * 2
        self.tail = b""
        self.pre = deque(maxlen=15)
        self.frames = []
        self.active = False
        self.voiced = self.silent = 0
        self.continued = False
        self.noise = 80.0

    def feed(self, data):
        import audioop

        self.tail += data
        while len(self.tail) >= self.frame_bytes:
            frame, self.tail = self.tail[: self.frame_bytes], self.tail[self.frame_bytes :]
            energy = audioop.rms(frame, 2)
            speech = energy > max(240, self.noise * 3)
            if not self.active:
                if not speech:
                    self.noise = min(300, 0.97 * self.noise + 0.03 * energy)
                    self.pre.append(frame)
                    continue
                self.active = True
                self.frames = list(self.pre)
                self.pre.clear()
            self.frames.append(frame)
            self.voiced += int(speech)
            self.silent = 0 if speech else self.silent + 1
            if self.silent >= 20:
                if self.voiced >= 6:
                    yield b"".join(self.frames), "silence"
                elif self.continued:
                    yield b"", "silence"
                self.frames = []
                self.active = False
                self.voiced = self.silent = 0
                self.continued = False
            elif len(self.frames) >= 200:
                yield b"".join(self.frames), "forced"
                self.frames = []
                self.voiced = self.silent = 0
                self.continued = True


class RouterTranscriber:
    """Segment capture without waiting on HTTP; emit concurrent requests in audio order."""

    def __init__(self, config, emit):
        self.config, self.emit = config, emit
        self.turns = None
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="router-asr")
        self.pending = deque()
        self.closed = False

    def start(self):
        if not self.config.key("openrouter"):
            raise CliError("Run auth openrouter to enable speech transcription.")

    def _transcribe(self, pcm, rate):
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm)
        result = request(
            "POST",
            "https://openrouter.ai/api/v1/audio/transcriptions",
            headers={"Authorization": "Bearer " + self.config.key("openrouter")},
            json={
                "model": self.config.values["openrouter_speech_model"],
                "input_audio": {
                    "data": base64.b64encode(buffer.getvalue()).decode("ascii"),
                    "format": "wav",
                },
            },
            timeout=20,
        )
        return result.get("text", "").strip()

    def _drain(self, wait=False):
        while self.pending and (wait or self.pending[0][0].done()):
            future, boundary = self.pending[0]
            try:
                text = future.result(timeout=25 if wait else 0)
            except TimeoutError as exc:
                raise CliError("Speech provider timed out; full audio is preserved.") from exc
            self.pending.popleft()
            self.emit(text, boundary)

    def send(self, data, rate):
        if self.closed:
            raise CliError("Speech session is closed.")
        self._drain()
        if self.turns is None:
            self.turns = AudioTurns(rate)
        for pcm, boundary in self.turns.feed(data):
            self._drain()
            if len(self.pending) >= 6:
                raise CliError(
                    "Speech provider is falling behind. Stop and retry; full audio is preserved."
                )
            if pcm:
                future = self.pool.submit(self._transcribe, pcm, rate)
            else:
                future = Future()
                future.set_result("")
            self.pending.append((future, boundary))
        self._drain()

    def finish(self):
        try:
            if self.turns:
                self.send(bytes(self.turns.rate * 2), self.turns.rate)
            self._drain(wait=True)
        finally:
            self.abort()

    def abort(self):
        self.closed = True
        self.pool.shutdown(wait=False, cancel_futures=True)
