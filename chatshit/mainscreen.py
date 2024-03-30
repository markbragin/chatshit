from textual.app import ComposeResult, events
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Input

from .message_list import MessageList


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        with Container(id="input-form"):
            self.message_list = MessageList(id="message-list")
            self.input = Input(id="message-input")
            yield self.message_list
            yield self.input

    def on_mount(self):
        self.input.focus()

    def on_input_submitted(self, event: events.InputEvent):
        text = self.input.value.strip()
        if text:
            self.app.client.send_msg(self.app.client.pack_text_msg(text))
            self.input.clear()
            if self.message_list.allow_vertical_scroll:
                self.message_list.scroll_end()

