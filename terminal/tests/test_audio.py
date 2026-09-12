"""Unit tests for the LiveBuffer delta-snapshot machinery and WAV writer."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from adversaria_terminal.audio import LiveBuffer, check_loopback_duration, write_pcm16_wav
from adversaria_terminal.util import np_float32_to_pcm16


def _pcm_bytes(n_samples: int, rate: int = 16000) -> bytes:
    return np_float32_to_pcm16(np.zeros(n_samples, dtype=np.float32))


def test_write_pcm16_wav_header(tmp_path: Path):
    out = tmp_path / "x.wav"
    write_pcm16_wav(out, b"\x00\x00" * 160, 16000, 1)
    raw = out.read_bytes()
    assert raw[:4] == b"RIFF"
    assert raw[8:12] == b"WAVE"
    assert raw[20:22] == (1).to_bytes(2, "little")  # PCM
    assert int.from_bytes(raw[24:28], "little") == 16000
    assert raw[36:40] == b"data"
    assert len(raw) == 44 + 320


def test_check_loopback_duration(tmp_path: Path):
    out = tmp_path / "d.wav"
    write_pcm16_wav(out, b"\x00\x00" * 16000, 16000, 1)
    assert check_loopback_duration(out) == 1.0


def test_livebuffer_append_retains_and_evicts():
    buf = LiveBuffer(sample_rate=16000, channels=1)
    one_second = b"\x00\x00" * 16000
    for _ in range(20):
        buf.append(one_second)
    # retention is 15s: oldest bytes were evicted
    assert buf._end == 20 * 32000
    assert buf._start > 0
    assert len(buf._bytes) <= buf._max_bytes


def test_livebuffer_snapshot_since_empty(tmp_path: Path):
    buf = LiveBuffer(sample_rate=16000, channels=1)
    wrote, next_offset = buf.snapshot_since(tmp_path / "s.wav", 0)
    assert wrote is False
    assert next_offset == 0


def test_livebuffer_snapshot_since_deltas(tmp_path: Path):
    buf = LiveBuffer(sample_rate=16000, channels=1)
    chunk = _pcm_bytes(16000 * 2)  # exactly 2 entire seconds
    buf.append(chunk)

    wrote, off1 = buf.snapshot_since(tmp_path / "first.wav", 0)
    assert wrote is True
    assert off1 == len(chunk)
    assert check_loopback_duration(tmp_path / "first.wav") == 2.0

    buf.append(_pcm_bytes(16000))  # +1 more second
    wrote, off2 = buf.snapshot_since(tmp_path / "second.wav", off1)
    assert wrote is True
    assert off2 > off1
    assert check_loopback_duration(tmp_path / "second.wav") == 1.0

    # nothing new -> no write, offset stays
    wrote, off3 = buf.snapshot_since(tmp_path / "none.wav", off2)
    assert wrote is False
    assert off3 == off2


def test_livebuffer_snapshot_below_min_silence(tmp_path: Path):
    buf = LiveBuffer(sample_rate=16000, channels=1)
    buf.append(_pcm_bytes(1600))  # 0.1s < MIN_SNAPSHOT_SECONDS (0.25s)
    wrote, _ = buf.snapshot_since(tmp_path / "tiny.wav", 0)
    assert wrote is False