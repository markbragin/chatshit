from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual import events


class DeleteMessageScreen(ModalScreen):
    
    def __init__(
        self,
        msg_id: int,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
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
            self.app.pop_screen()
            event.stop()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "button-delete":
            message_list = self.app.get_screen("main_screen").message_list
            message_list.delete_message(self._msg_id)
        elif event.button.id == "button-delete-for-all":
            self.app.client.send_msg(
                self.app.client.pack_delete_message(self._msg_id)
            )
        self.app.pop_screen()
