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

    def update_messages(self):
        screen = self.get_screen("main_screen")
        while not self.client.message_queue.empty():
            msg = self.client.message_queue.get()
            screen.message_list.add_message(msg) #type: ignore
        self.set_interval



if __name__ == "__main__":
    app = ChatRoom()
    try:
        app.run()
    except KeyboardInterrupt:
        app.client.close()
