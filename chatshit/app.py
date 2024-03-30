from threading import Thread

from textual.app import App

from .loginscreen import LoginScreen
from .mainscreen import MainScreen
from .client import Client


class ChatRoom(App):

    CSS_PATH = "styles.css"

    SCREENS = {
        "login_screen": LoginScreen(),
        "main_screen": MainScreen()
    }

    client: Client

    def on_mount(self):
        self.push_screen("main_screen")
        self.push_screen("login_screen")

    def process_messages(self):
        screen = self.get_screen("main_screen")
        while not self.client.message_queue.empty():
            msg = self.client.message_queue.get()
            if msg["Type"] == "text":
                screen.message_list.add_message(msg["Text"]) #type: ignore
            elif msg["Type"] == "new_member":
                screen.member_list.add_member(msg) #type: ignore
            elif msg["Type"] == "left_chat":
                screen.member_list.remove_member(msg) #type: ignore


if __name__ == "__main__":
    app = ChatRoom()
    try:
        app.run()
    except KeyboardInterrupt:
        app.client.close()
