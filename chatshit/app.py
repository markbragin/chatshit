from textual.app import App

from .loginscreen import LoginScreen
from .mainscreen import MainScreen
from .client import Client


class ChatRoom(App):

    CSS_PATH = "styles.css"

    SCREENS = {
        "login_screen": LoginScreen(),
        "main_screen": MainScreen(),
    }

    client: Client

    def on_mount(self):
        self.push_screen("main_screen")
        self.push_screen("login_screen")

    def process_messages(self):
        screen: MainScreen = self.get_screen("main_screen")  # type: ignore
        while not self.client.message_queue.empty():
            msg = self.client.message_queue.get()
            if msg["Type"] == "text":
                screen.message_list.add_message(msg["Text"])
            elif msg["Type"] == "new_member":
                screen.member_list.add_member(msg)
            elif msg["Type"] == "left_chat":
                screen.member_list.remove_member(msg)


if __name__ == "__main__":
    app = ChatRoom()
    try:
        app.run()
    except KeyboardInterrupt:
        app.client.close()
