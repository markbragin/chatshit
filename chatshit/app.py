from textual.app import App

from chatshit.screens.chatroom_screen import ChatRoomScreen
from chatshit.network.client import Client


class ChatApp(App):

    CSS_PATH = "styles.css"

    def __init__(self):
        super().__init__()
        self._clients: list[Client] = []

    def on_mount(self):
        self.push_screen(ChatRoomScreen())

    def add_client(self, client: Client):
        self._clients.append(client)
    
    def on_chat_room_screen_add_client(self, message: ChatRoomScreen.AddClient):
        self.add_client(message.client)

    def close_all_clients(self):
        for client in self._clients:
            client.close()


if __name__ == "__main__":
    app = ChatApp()
    try:
        app.run()
    except KeyboardInterrupt:
        app.close_all_clients()
