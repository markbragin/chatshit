from textual.app import ComposeResult, events
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input
from textual.message import Message

import chatshit.network.proto as proto
from chatshit.screens.login_screen import LoginScreen
from chatshit.widgets.message_list import MessageList
from chatshit.widgets.member_list import MemberList
from chatshit.network.client import Client


class ChatRoomScreen(Screen):

    class AddClient(Message):
        def __init__(self, client: Client):
            super().__init__()
            self.client = client

    def __init__(self):
        super().__init__()
        self._client = None

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
        if self._client == None:
            self.app.push_screen(LoginScreen(), self.setup_client)

    def setup_client(self, client: Client):
        self.client = client
        self.post_message(self.AddClient(client))
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
                self.member_list.add_member(msg)
            elif msg["Type"] == "left_chat":
                self.member_list.remove_member(msg)
            elif msg["Type"] == "unique_username":
                self.client.username = msg["Username"]
            elif msg["Type"] == "delete_message":
                self.message_list.delete_message(msg['Id'])

