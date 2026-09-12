"""Settings — edit the terminal's local config and save it."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Input, Static

from .base import BaseScreen


class SettingsScreen(BaseScreen):
    """Edit config.json for the terminal (its own copy, not the desktop's)."""

    CSS = """
    SettingsScreen {
        align: center top;
    }
    #settings-header {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #settings-title {
        text-style: bold;
        color: $accent;
    }
    #settings-form {
        width: 90%;
        height: auto;
        grid-size: 2;
        grid-gutter: 1 2;
        margin: 1 2;
    }
    #settings-form Label {
        padding-top: 1;
    }
    #settings-note {
        width: 90%;
        margin: 0 2;
    }
    #settings-actions {
        width: 100%;
        height: auto;
        padding: 1 2;
    }
    #settings-actions Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Settings", id="settings-title"),
            Static("", id="settings-dir"),
            id="settings-header",
        )
        with Grid(id="settings-form"):
            yield Static("Python service URL", classes="field-label")
            yield Input(id="set-url", placeholder="http://127.0.0.1:9876")
            yield Static("Default template", classes="field-label")
            yield Input(id="set-template", placeholder="general")
            yield Static("Ollama model (blank = default)", classes="field-label")
            yield Input(id="set-model", placeholder="e.g. llama3.1:8b")
            yield Static("Summary language (blank = auto)", classes="field-label")
            yield Input(id="set-lang", placeholder="e.g. en, ar")
            yield Static("Your name (speaker label)", classes="field-label")
            yield Input(id="set-name", placeholder="Me")
            yield Static("Custom vocabulary (comma-separated)", classes="field-label")
            yield Input(id="set-vocab", placeholder="Name1, product, jargon")
            yield Static("Speaker diarization", classes="field-label")
            yield Checkbox("Assign speech to speakers (Them / Me)", id="set-diarize")
        yield Static(
            "[dim]The terminal keeps its own config and history, fully separate from "
            "the desktop app. Changes apply to new transcriptions immediately.[/dim]",
            id="settings-note",
        )
        yield Horizontal(
            Button("Save", id="btn-save", variant="primary"),
            Button("Back", id="btn-back", variant="default"),
            id="settings-actions",
        )

    def on_mount(self) -> None:
        cfg = self.app.rt.config
        self.query_one("#settings-dir", Static).update(
            f"[dim]Config & history: {self.app.rt.data_dir}[/dim]"
        )
        self.query_one("#set-url", Input).value = cfg.python_service_url
        self.query_one("#set-template", Input).value = cfg.default_prompt_template
        if cfg.ollama_model:
            self.query_one("#set-model", Input).value = cfg.ollama_model
        if cfg.summary_language:
            self.query_one("#set-lang", Input).value = cfg.summary_language
        if cfg.user_name:
            self.query_one("#set-name", Input).value = cfg.user_name
        if cfg.custom_vocabulary:
            self.query_one("#set-vocab", Input).value = cfg.custom_vocabulary
        self.query_one("#set-diarize", Checkbox).value = cfg.diarize

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            self._save()
        elif event.button.id == "btn-back":
            self.action_back()

    def _save(self) -> None:
        cfg = self.app.rt.config
        cfg.python_service_url = self.query_one("#set-url", Input).value.strip() or cfg.python_service_url
        cfg.default_prompt_template = (
            self.query_one("#set-template", Input).value.strip() or cfg.default_prompt_template
        )
        cfg.ollama_model = self.query_one("#set-model", Input).value.strip() or None
        cfg.summary_language = self.query_one("#set-lang", Input).value.strip() or None
        cfg.user_name = self.query_one("#set-name", Input).value.strip() or None
        cfg.custom_vocabulary = self.query_one("#set-vocab", Input).value.strip() or None
        cfg.diarize = self.query_one("#set-diarize", Checkbox).value
        try:
            from ..config import save_config

            save_config(cfg)
        except Exception as exc:
            self.notify(str(exc), severity="error")
            return
        self.notify("Settings saved.")
        self.app.pop_screen()