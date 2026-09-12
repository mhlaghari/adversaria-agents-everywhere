"""Unit tests for pure helpers (WAV IO, action-item parsing, formatting)."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from adversaria_terminal import util


def test_np_float32_to_pcm16_clamps_and_scales():
    samples = np.array([0.0, 1.0, -1.0, 0.5, -0.5], dtype=np.float32)
    pcm = util.np_float32_to_pcm16(samples)
    assert len(pcm) == 5 * 2
    values = np.frombuffer(pcm, dtype="<i2")
    assert values[0] == 0
    assert values[1] == 32767
    assert values[2] == -32767
    assert abs(abs(values[3]) - 16384) <= 2


def test_write_wav_pcm16_is_readable_and_mono(tmp_path: Path):
    samples = np.zeros(16000, dtype=np.float32)
    samples[::97] = 0.5
    out = tmp_path / "tone.wav"
    util.write_wav_pcm16(out, samples, 16000)
    with wave.open(str(out), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getframerate() == 16000
        assert w.getsampwidth() == 2
        assert w.getnframes() == 16000


def test_write_wav_pcm16_stereo_preserves_channels(tmp_path: Path):
    stereo = np.zeros((1600, 2), dtype=np.float32)
    stereo[:, 0] = 0.4
    stereo[:, 1] = 1.0
    out = tmp_path / "stereo.wav"
    util.write_wav_pcm16(out, stereo, 16000)
    with wave.open(str(out), "rb") as w:
        assert w.getnchannels() == 2
        assert w.getnframes() == 1600


def test_write_wav_pcm16_mono_after_downmix(tmp_path: Path):
    stereo = np.zeros((1600, 2), dtype=np.float32)
    stereo[:, 0] = 0.4
    mono = util.merge_channels_to_mono(stereo)
    assert mono.shape == (1600,)
    out = tmp_path / "mono.wav"
    util.write_wav_pcm16(out, mono, 16000)
    with wave.open(str(out), "rb") as w:
        assert w.getnchannels() == 1


def test_merge_channels_to_mono_preserves_1d():
    a = np.array([0.1, -0.2, 0.3], dtype=np.float32)
    b = util.merge_channels_to_mono(a)
    assert b.shape == a.shape
    np.testing.assert_array_equal(b, a)


# ---------------------------------------------------------------------------
# Action-item extraction (mirrors desktop `extract_action_items`)
# ---------------------------------------------------------------------------


def test_parse_action_items_picks_bullets_under_heading():
    summary = """# Title
Some paragraph.

## Action Items
- Ship the release notes
- Fix the login bug

## Next Steps
* Migrate the database
"""
    items = util.parse_action_items(summary)
    assert items == ["Ship the release notes", "Fix the login bug", "Migrate the database"]


def test_parse_action_items_stops_at_next_heading():
    summary = """## Action Items
- Only this one
## Summary
- Not an action item
"""
    assert util.parse_action_items(summary) == ["Only this one"]


def test_parse_action_items_empty():
    assert util.parse_action_items("") == []
    assert util.parse_action_items("No headings here\n- dangling bullet") == []


def test_parse_action_items_case_insensitive():
    assert util.parse_action_items("## NEXT STEPS:\n- Do the thing") == ["Do the thing"]


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def test_humanize_duration():
    assert util.humanize_duration(45) == "45s"
    assert util.humanize_duration(65) == "1m 05s"
    assert util.humanize_duration(3661) == "1h 01m 01s"


def test_safe_filename_strips_windows_unsafe_chars():
    assert util.safe_filename('A/B:C*D?"<>|') == "A_B_C_D_____"
    assert util.safe_filename("   ") == "meeting"


def test_fmt_bytes():
    assert util.fmt_bytes(500) == "500 B"
    assert util.fmt_bytes(2048) == "2.0 KB"