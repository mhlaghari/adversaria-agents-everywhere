"""Small pure helpers: WAV IO, action-item parsing, formatting."""

from __future__ import annotations

import re
import wave
from pathlib import Path

import numpy as np

# --------------------------------------------------------------------------
# WAV writing (PCM16, the most compatible format for Whisper/PyAV)
# --------------------------------------------------------------------------

WAV_SAMPLE_RATE = 48000


def np_float32_to_pcm16(samples: np.ndarray) -> bytes:
    """Interleaved float32 (-1..1) -> int16 little-endian bytes."""
    clipped = np.clip(samples, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype("<i2", copy=False)
    return pcm.tobytes()


def write_wav_pcm16(path: Path, samples: np.ndarray, sample_rate: int) -> None:
    """Write a float32 array (shape N x channels or N,) as a PCM16 WAV file."""
    if samples.ndim == 1:
        samples = samples.reshape(-1, 1)
    n_channels = samples.shape[1]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(n_channels)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(np_float32_to_pcm16(samples))


def merge_channels_to_mono(samples: np.ndarray) -> np.ndarray:
    """Downmix multi-channel float32 to a single channel (mean of channels)."""
    if samples.ndim == 1:
        return samples
    return samples.mean(axis=1, dtype=np.float32)


# --------------------------------------------------------------------------
# Action-item extraction (mirrors the desktop's `extract_action_items`)
# --------------------------------------------------------------------------

_ACTION_HEADING = re.compile(
    r"^\s*#{1,5}\s*(action items?|next steps?|actions|to[- ]?dos?|to-do items?"
    r"|deliverables?|tasks?|follow-ups?|key actions?)\s*:?\s*$",
    re.IGNORECASE,
)
_HEADING_ANY = re.compile(r"^\s*#{1,5}\s+", re.IGNORECASE)
_BULLET = re.compile(r"^\s*[-*]\s+(.+?)\s*$")


def parse_action_items(summary: str) -> list[str]:
    """Return bullet texts under action-item headings, in order."""
    lines = summary.splitlines()
    items: list[str] = []
    in_section = False
    for line in lines:
        if _ACTION_HEADING.match(line):
            in_section = True
            continue
        if in_section and _HEADING_ANY.match(line):
            in_section = False
            continue
        if in_section:
            m = _BULLET.match(line)
            if m:
                text = m.group(1).strip()
                if text:
                    items.append(text)
    return items


def humanize_duration(seconds: float) -> str:
    seconds = round(seconds)
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)
    if hh:
        return f"{hh}h {mm:02d}m {ss:02d}s"
    if mm:
        return f"{mm}m {ss:02d}s"
    return f"{ss}s"


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------
# Text formatting helpers for the terminal
# --------------------------------------------------------------------------


def fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} GB"


def fmt_iso_timestamp(iso: str) -> str:
    if not iso:
        return ""
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    return dt.strftime("%Y-%m-%d %H:%M")


def safe_filename(title: str) -> str:
    keep = re.sub(r'[<>:"/\\|?*]', "_", title).strip()
    return keep or "meeting"