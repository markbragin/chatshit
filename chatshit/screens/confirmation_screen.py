from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual import events


class ConfirmationScreen(ModalScreen):

    class Answer:
        def __init__(self, ans: bool, data = None):
            self.ans = ans
            self.data = data

    def __init__(self, question: str, data = None):
        super().__init__()
        self.question = question
        self.data = data

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.question, id="question"),
            Button("Yes", id="yes"),
            Button("No", id="no"),
            id="dialog",
        )

    def on_key(self, event: events.Key):
        if event.key == "escape":
            self.dismiss(self.Answer(False, self.data))
            event.stop()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes":
            self.dismiss(self.Answer(True, self.data))
        else:
            self.dismiss(self.Answer(False, self.data))
