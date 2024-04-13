from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input
from textual.message import Message

import chatshit.network.proto as proto
from chatshit.screens.login_screen import LoginScreen
from chatshit.widgets.message_list import MessageList
from chatshit.widgets.member_list import MemberList
from chatshit.screens.client_screen import ClientScreen


class ChatRoomScreen(ClientScreen):

    class AddClient(Message):
        def __init__(self, screen: ClientScreen):
            super().__init__()
            self.screen = screen

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
        if self.client is None:
            self.app.push_screen(
                LoginScreen(
                    host=self._host,
                    port=self._port,
                    classes="input-screen",
                ),
                self.setup_client,
            )

    def setup_client(self, creds: LoginScreen.Result | None):
        if creds is None:
            self.dismiss()
        else:
            self.client = creds.client
            self.chat_name = creds.name
            self.post_message(self.AddClient(self))
            self.set_interval(0.1, callback=self.process_messages)

    def on_input_submitted(self):
        text = self.input.value.strip()
        if text:
            self.client.send_msg(proto.pack_text_msg(text))
            self.input.clear()
            self.message_list.scroll_end()

    def on_message_list_delete(self, message: MessageList.Delete):
        self.client.send_msg(proto.pack_delete_message(message.msg_id))

    def process_messages(self):
        while not self.client.message_queue.empty():
            msg = self.client.message_queue.get()
            if msg["Type"] == "text":
                self.message_list.add_message(msg)
            elif msg["Type"] == "join_chat":
                self.member_list.add_member(msg["Username"])
            elif msg["Type"] == "left_chat":
                self.member_list.remove_member(msg["Username"])
            elif msg["Type"] == "unique_username":
                self.client.username = msg["Username"]
            elif msg["Type"] == "delete_message":
                self.message_list.delete_message(msg["Id"])
