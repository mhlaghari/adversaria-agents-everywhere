"""Base screen: shared bindings, navigation helpers, small shared modals."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Static


class ConfirmModal(ModalScreen[bool]):
    """Yes/no modal; the answer is dismissed back to `push_screen(..., callback)`."""

    CSS = """
    ConfirmModal {
        align: center middle;
    }
    #confirm-card {
        width: 44;
        height: auto;
        border: round $error;
        background: $surface;
        padding: 1 2;
    }
    #confirm-text {
        margin-bottom: 1;
    }
    """

    def __init__(self, message: str, confirm_label: str = "Delete", cancel_label: str = "Cancel"):
        super().__init__()
        self.message = message
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label

    def compose(self) -> ComposeResult:
        yield Static(self.message, id="confirm-text")
        yield Horizontal(
            Button(self.confirm_label, id="confirm-yes", variant="error"),
            Button(self.cancel_label, id="confirm-no", variant="default"),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm-yes")


class BaseScreen(Screen):
    """Shared key binds for all pushed screens."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("ctrl+r", "record", "Record"),
        Binding("ctrl+m", "meetings", "Meetings"),
        Binding("ctrl+i", "import", "Import"),
        Binding("ctrl+t", "todos", "To-dos"),
        Binding("ctrl+e", "templates", "Templates"),
        Binding("ctrl+l", "models", "Models"),
        Binding("ctrl+s", "settings", "Settings"),
    ]

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_record(self) -> None:
        from .record import RecordScreen

        self.app.push_screen(RecordScreen())

    def action_meetings(self) -> None:
        from .meetings import MeetingsScreen

        self.app.push_screen(MeetingsScreen())

    def action_import(self) -> None:
        from .import_screen import ImportScreen

        self.app.push_screen(ImportScreen())

    def action_todos(self) -> None:
        from .todos import TodosScreen

        self.app.push_screen(TodosScreen())

    def action_templates(self) -> None:
        from .templates import TemplatesScreen

        self.app.push_screen(TemplatesScreen())

    def action_models(self) -> None:
        from .models import ModelsScreen

        self.app.push_screen(ModelsScreen())

    def action_settings(self) -> None:
        from .settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def open_meeting(self, meeting_id: int) -> None:
        self.app.open_meeting(meeting_id)


class DashboardScreenBase(BaseScreen):
    """Screen that never pops below the dashboard (escape quits)."""

    def action_back(self) -> None:
        self.app.exit()