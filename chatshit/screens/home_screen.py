from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button

from chatshit.screens.chatroom_screen import ChatRoomScreen
from chatshit.widgets.chat_list import ChatList
from chatshit.widgets.server_list import ServerList
from chatshit.screens.create_server_screen import CreateServerScreen


class HomeScreen(Screen):

    def compose(self) -> ComposeResult:
        self.chat_list = ChatList(id="chat-list")
        self.chat_list.border_title = "Chats"
        self.server_list = ServerList(id="server-list")
        self.server_list.border_title = "Servers"

        with Horizontal(id="horizontal-layout"):
            with Vertical(id="vertical-layout"):
                yield self.chat_list
                yield self.server_list
            with Container(id="home-screen-buttons"):
                self.create_chatroom_button = Button("Create chatroom")
                self.connect_to_chatroom_button = Button("Connect to chatroom")
                yield self.create_chatroom_button
                yield self.connect_to_chatroom_button

    def on_mount(self):
        self.focus()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button == self.create_chatroom_button:
            self.app.push_screen(CreateServerScreen(classes="input-screen"))
        elif event.button == self.connect_to_chatroom_button:
            self.app.push_screen(ChatRoomScreen())

    def on_server_list_connect_to(self, message: ServerList.ConnectTo):
        host, port = self.app.get_server_address(message.server_id)
        if host == "0.0.0.0":
            host = "127.0.0.1"
        self.app.push_screen(ChatRoomScreen(host=host, port=port))
