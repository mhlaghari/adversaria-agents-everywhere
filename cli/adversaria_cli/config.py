"""Small, private CLI configuration. Credentials never enter SQLite or prompts."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


class CliError(Exception):
    """An actionable error suitable for the terminal."""


def private_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def atomic_text(path: Path, text: str) -> None:
    private_dir(path.parent)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".adversaria-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(text)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class Config:
    def __init__(self, directory: str | Path | None = None):
        self.directory = (
            Path(
                directory
                or os.getenv("ADVERSARIA_CLI_HOME")
                or Path.home() / ".local/share/adversaria-cli"
            )
            .expanduser()
            .resolve()
        )
        private_dir(self.directory)
        self.path = self.directory / "config.json"
        self.values = {
            "provider": "openrouter",
            "model": "auto",
            "speech_provider": "openrouter",
            "openrouter_speech_model": "openai/gpt-transcribe",
            "transcription_model": "gpt-transcribe",
            "live_model": "gpt-live-transcribe",
            "workspace": "Live meetings",
            "auto_web": True,
        }
        if self.path.exists():
            try:
                self.values.update(json.loads(self.path.read_text()))
            except (ValueError, TypeError) as exc:
                raise CliError(f"Invalid config at {self.path}: {exc}") from exc

    def save(self, **values):
        self.values.update(values)
        atomic_text(self.path, json.dumps(self.values, indent=2) + "\n")

    def key(self, provider: str) -> str:
        env = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "exa": "EXA_API_KEY",
        }[provider]
        value = os.getenv(env, "").strip()
        path = self.directory / f"{provider}.key"
        if not value and path.exists():
            value = path.read_text().strip()
        return value

    def save_key(self, provider: str, value: str):
        if provider not in {"openrouter", "openai", "exa"} or not value.strip():
            raise CliError("A nonempty OpenAI, OpenRouter or Exa key is required.")
        atomic_text(self.directory / f"{provider}.key", value.strip() + "\n")

    def selection(self, provider=None, model=None) -> tuple[str, str]:
        selected = provider or self.values["provider"]
        # Switching provider must never reuse another provider's model ID.
        chosen = model or (self.values["model"] if selected == self.values["provider"] else "auto")
        return selected, chosen
