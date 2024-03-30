from textual.app import ComposeResult, events
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input

from .message_list import MessageList
from .member_list import MemberList


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        self.message_list = MessageList(id="message-list")
        self.input = Input(id="message-input")
        self.member_list = MemberList(id="member-list")
        self.member_list.border_title = "Members"
        with Horizontal(id="horizontal-layout"):
            yield self.member_list
            with Vertical(id="vertical-layout"):
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

