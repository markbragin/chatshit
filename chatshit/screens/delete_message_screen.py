from dataclasses import dataclass

from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual import events


class DeleteMessageScreen(ModalScreen):

    class Answer:
        def __init__(self, msg_id: int, delete: bool, for_all: bool):
            self.msg_id = msg_id
            self.delete = delete
            self.for_all = for_all


    def __init__(self, msg_id: int):
        super().__init__()
        self._msg_id = msg_id

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to delete message?", id="question"),
            Button("Delete", id="button-delete"),
            Button("Delete for all", id="button-delete-for-all"),
            Button("Cancel", id="button-cancel"),
            id="dialog",
        )

    def on_key(self, event: events.Key):
        if event.key == "escape":
            self.dismiss(self.Answer(0, False, False))
            event.stop()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "button-delete":
            self.dismiss(self.Answer(self._msg_id, True, False))
        elif event.button.id == "button-delete-for-all":
            self.dismiss(self.Answer(self._msg_id, True, True))
        else:
            self.dismiss(self.Answer(0, False, False))
