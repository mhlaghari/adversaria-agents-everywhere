"""Audio capture for the terminal client, using `soundcard`.

`soundcard` is a tiny ctypes-only library (no compilation), which keeps the
terminal client dependency-free of native builds while still doing real
WASAPI/loopback capture on Windows and CoreAudio on macOS.

Mirrors the desktop's dual-capture shape:
  - "them" = system audio (default speaker loopback)
  - "me"   = microphone (default capture device)

Capture is always best-effort — a missing or failing source falls back to the
others and never aborts a recording, exactly like `audio/mod.rs`.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path

from .util import WAV_SAMPLE_RATE, merge_channels_to_mono, np_float32_to_pcm16

try:
    import soundcard as _sc  # type: ignore
except Exception:  # pragma: no cover - platform without soundcard wheels
    _sc = None

LIVE_RETENTION_SECONDS = 15.0
MIN_SNAPSHOT_SECONDS = 0.25

_PCM16_HEADER = 44


@dataclass
class Source:
    kind: str  # "them" | "me"
    device_name: str


def _relaxed_title(name: str) -> str:
    return name.replace("（", "(").replace("）", ")").replace("「Loopback」", "").strip()


def available_sources() -> tuple[list[Source], str | None]:
    """Return (sources, reason). `reason` is set when capture is unusable."""
    if _sc is None:
        return [], "soundcard is not installed"
    try:
        mics = _sc.all_microphones(include_loopback=True)
    except Exception as exc:
        return [], f"soundcard enumeration failed: {exc}"
    sources: list[Source] = []
    # `soundcard`'s loopback-capable devices carry `isloopback=True`; their
    # `.name` is just the speaker's plain name ("Speaker (Realtek(R) Audio)"),
    # with NO "loopback" substring — only `repr()` prefixes "Loopback". The old
    # name-sniff therefore always missed them, so "them" fell back to a
    # `_Speaker` (playback-only, no `.recorder()` — instant capture-thread
    # crash) and "me" grabbed the loopback mic instead of the real microphone
    # (verified live on this machine: `all_microphones` returned exactly one
    # `<Loopback Speaker ...>` and one real `<Microphone Microphone Array...>`,
    # and the name-sniff routed both "them" and "me" to the loopback entry).
    loopbacks = [m for m in mics if getattr(m, "isloopback", False)]
    plain_mics = [m for m in mics if not getattr(m, "isloopback", False)]
    if loopbacks:
        sources.append(Source("them", _relaxed_title(loopbacks[0].name)))
    if plain_mics:
        sources.append(Source("me", _relaxed_title(plain_mics[0].name)))
    return sources, None


class LiveBuffer:
    """Append-only rolling byte buffer supporting delta snapshot WAVs.

    Mirrors `audio/mod.rs::snapshot_since`: a snapshot writes the bytes NEW
    since the last offset as a WAV and returns the new offset.
    """

    def __init__(self, sample_rate: int = WAV_SAMPLE_RATE, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._bytes = bytearray()
        self._start = 0
        self._end = 0
        self._max_bytes = int(sample_rate * channels * 2 * LIVE_RETENTION_SECONDS)
        self._lock = threading.RLock()

    def append(self, data: bytes) -> None:
        with self._lock:
            self._bytes.extend(data)
            self._end += len(data)
            excess = len(self._bytes) - self._max_bytes
            if excess > 0 and self._bytes:
                del self._bytes[:excess]
                self._start += excess

    def snapshot_since(self, path: Path, from_byte: int) -> tuple[bool, int]:
        """Write a delta WAV of audio after `from_byte`. Returns (wrote, next)."""
        with self._lock:
            requested = max(from_byte, self._start)
            start = requested - self._start
            if not self._bytes or len(self._bytes) - start < int(
                MIN_SNAPSHOT_SECONDS * self.sample_rate * self.channels * 2
            ):
                return False, self._end
            data = bytes(self._bytes[start:])
            next_offset = self._end
        write_pcm16_wav(path, data, self.sample_rate, self.channels)
        return True, next_offset


def write_pcm16_wav(path: Path, pcm16: bytes, sample_rate: int, channels: int) -> None:
    """Write a canonical 44-byte PCM16 WAV header + data."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    byte_rate = sample_rate * channels * 2
    block_align = channels * 2
    data_size = len(pcm16)
    header = (
        b"RIFF"
        + (36 + data_size).to_bytes(4, "little")
        + b"WAVE"
        + b"fmt "
        + (16).to_bytes(4, "little")
        + (1).to_bytes(2, "little")  # PCM
        + channels.to_bytes(2, "little")
        + sample_rate.to_bytes(4, "little")
        + byte_rate.to_bytes(4, "little")
        + block_align.to_bytes(2, "little")
        + (16).to_bytes(2, "little")
        + b"data"
        + data_size.to_bytes(4, "little")
    )
    path.write_bytes(header + pcm16)


class _WavStream:
    """Append-only PCM16 WAV that patches its header on close.

    `__init__` used to reserve the header as 44 zero bytes and `close()`
    patched only the two size fields (offsets 4 and 40) — every other header
    byte (the "RIFF"/"WAVE"/"fmt " magic, format tag, channel count, sample
    rate) was left as zeros, so the file never started with a valid RIFF id
    and nothing downstream (ffmpeg, the transcribe endpoint) could open it.
    Now the full valid header is written up front with size 0, and `close()`
    rewrites that same header in place with the real size — mirrors
    `write_pcm16_wav`'s layout exactly.
    """

    def __init__(self, path: Path, sample_rate: int, channels: int):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.file = self.path.open("wb")
        self.sample_rate = sample_rate
        self.channels = channels
        self.data_size = 0
        self._write_header(0)

    def _write_header(self, data_size: int) -> None:
        byte_rate = self.sample_rate * self.channels * 2
        block_align = self.channels * 2
        header = (
            b"RIFF"
            + (36 + data_size).to_bytes(4, "little")
            + b"WAVE"
            + b"fmt "
            + (16).to_bytes(4, "little")
            + (1).to_bytes(2, "little")  # PCM
            + self.channels.to_bytes(2, "little")
            + self.sample_rate.to_bytes(4, "little")
            + byte_rate.to_bytes(4, "little")
            + block_align.to_bytes(2, "little")
            + (16).to_bytes(2, "little")
            + b"data"
            + data_size.to_bytes(4, "little")
        )
        self.file.write(header)

    def write(self, pcm16: bytes) -> None:
        self.file.write(pcm16)
        self.data_size += len(pcm16)

    def close(self) -> None:
        self.file.seek(0)
        self._write_header(self.data_size)
        self.file.close()


def _device_for(kind: str):
    mics = _sc.all_microphones(include_loopback=True)
    if kind == "me":
        for m in mics:
            if not getattr(m, "isloopback", False):
                return m
        return None
    for m in mics:
        if getattr(m, "isloopback", False):
            return m
    # No loopback-capable mic entry at all: a plain `_Speaker` has no
    # `.recorder()`, so there is genuinely nothing to capture "them" with —
    # return None and let the caller report "no audio device found" instead
    # of handing back an object that crashes the capture thread.
    return None


class RecordingSession:
    """Dual capture of system ("them") + mic ("me") into PCM16 WAV files."""

    def __init__(self, audio_dir: Path, *, them: bool = True, me: bool = True):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.them = them
        self.me = me
        self.sources: dict[str, str] = {}
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._errors: list[str] = []
        self._lock = threading.Lock()
        self.system_buffer = LiveBuffer()
        self.mic_buffer = LiveBuffer()
        self.system_path: Path | None = None
        self.mic_path: Path | None = None

    def start(self) -> list[str]:
        """Open streams and spawn capture threads. Returns warning messages."""
        warnings: list[str] = []
        if _sc is None:
            return ["soundcard is not installed"]
        self.system_path = self.audio_dir / "recording_system.wav"
        self.mic_path = self.audio_dir / "recording_mic.wav"

        wants = [("them", self.them, self.system_path, self.system_buffer),
                 ("me", self.me, self.mic_path, self.mic_buffer)]
        for kind, enabled, wav_path, buffer in wants:
            if not enabled:
                continue
            device = _device_for(kind)
            if device is None:
                warnings.append(f"{kind}: no audio device found")
                continue
            t = threading.Thread(
                target=self._capture_loop,
                args=(kind, device, wav_path, buffer),
                name=f"capture-{kind}",
                daemon=True,
            )
            self._threads.append(t)
            t.start()
        return warnings

    def _capture_loop(self, kind: str, device, wav_path: Path, buffer: LiveBuffer) -> None:
        channels = 1
        try:
            with device.recorder(
                samplerate=WAV_SAMPLE_RATE, channels=channels, blocksize=4096
            ) as recorder:
                writer = _WavStream(wav_path, WAV_SAMPLE_RATE, channels)
                try:
                    while not self._stop.is_set():
                        frames = recorder.record(numframes=4096)
                        if frames is None or len(frames) == 0:
                            continue
                        mono = merge_channels_to_mono(frames)
                        pcm = np_float32_to_pcm16(mono)
                        writer.write(pcm)
                        buffer.append(pcm)
                finally:
                    writer.close()
        except Exception as exc:  # pragma: no cover - device/hardware dependent
            with self._lock:
                self._errors.append(f"{kind}: {exc}")

    def stop(self) -> None:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=5.0)

    @property
    def warnings(self) -> list[str]:
        with self._lock:
            return list(self._errors)

    def close(self) -> None:
        self.stop()


def check_loopback_duration(delta_wav: Path) -> float:
    """Sanity helper: seconds of PCM16 audio in a WAV (used in tests)."""
    data = delta_wav.read_bytes()
    if len(data) < _PCM16_HEADER:
        return 0.0
    rate = int.from_bytes(data[24:28], "little")
    channels = int.from_bytes(data[22:24], "little")
    size = int.from_bytes(data[40:44], "little")
    if rate == 0 or channels == 0:
        return 0.0
    return size / (rate * channels * 2)