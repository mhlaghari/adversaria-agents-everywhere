"""Local configuration for the terminal client.

Mirrors the desktop app's config keys so a user switching between the two
surfaces keeps a shared mental model. The terminal keeps its OWN copy (it does
not read the desktop's encrypted keychain or its `config.json`), so it can run
fully independently.
"""

from __future__ import annotations

import dataclasses
import json
import os
import sys
from pathlib import Path

DEFAULT_SERVICE_URL = "http://127.0.0.1:9876"

LANGUAGES = [
    ("auto", "Match the meeting's language"),
    ("en", "English"),
    ("ar", "Arabic"),
    ("ur", "Urdu"),
    ("zh", "Chinese"),
    ("hi", "Hindi"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("bn", "Bengali"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
]


def default_data_dir() -> Path:
    """Per-user data dir for terminal history and audio. Overridable with
    ADVERSARIA_TERMINAL_DIR (mirrors the desktop's ADVERSARIA_DATA_DIR)."""
    env = os.environ.get("ADVERSARIA_TERMINAL_DIR")
    if env:
        return Path(env).expanduser()
    base = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME")
    if sys.platform == "win32" and base:
        return Path(base) / "adversaria-terminal"
    if base:
        return Path(base) / "adversaria-terminal"
    return Path.home() / ".local" / "share" / "adversaria-terminal"


@dataclasses.dataclass
class AppConfig:
    python_service_url: str = DEFAULT_SERVICE_URL
    default_prompt_template: str = "general"
    ollama_model: str | None = None
    summary_language: str | None = None
    user_name: str | None = None
    custom_vocabulary: str | None = None
    diarize: bool = True
    data_dir: str | None = None

    def applied_data_dir(self) -> Path:
        if self.data_dir:
            return Path(self.data_dir).expanduser()
        return default_data_dir()


class ConfigError(RuntimeError):
    """Raised when a persisted config file is unreadable."""


def load_config(path: Path | None = None) -> AppConfig:
    """Load config from `data_dir/config.json`, tolerating absence."""
    if path is None:
        path = default_data_dir() / "config.json"
    if not path.exists():
        return AppConfig()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ConfigError(f"Could not read config {path}: {exc}") from exc
    known = {f.name for f in dataclasses.fields(AppConfig)}
    data = {k: v for k, v in raw.items() if k in known}
    config = AppConfig(**data)
    # data_dir can point anywhere; config persists inside it.
    if config.data_dir:
        return config
    return config


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    """Persist config next to the data directory. Returns the config path."""
    if path is None:
        path = default_data_dir() / "config.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(dataclasses.asdict(config), indent=2, ensure_ascii=False)
    path.write_text(raw, encoding="utf-8")
    return path


def service_url_env() -> str | None:
    """Optional ADVERSARIA_SERVICE_URL override, applied on top of config."""
    return os.environ.get("ADVERSARIA_SERVICE_URL")