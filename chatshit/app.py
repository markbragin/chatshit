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
        self.client = Client()
        self.push_screen("main_screen")
        self.push_screen("login_screen")
        self.set_interval(0.1, callback=self.update_messages)

    def update_messages(self):
        screen = self.get_screen("main_screen")
        if not self.client.connection_closed:
            while not self.client.message_queue.empty():
                msg: str = self.client.message_queue.get()
                screen.message_list.add_message(msg) #type: ignore
                try:
                    screen.message_list.action_scroll_end() #type: ignore
                except:
                    pass


if __name__ == "__main__":
    app = ChatRoom()
    try:
        app.run()
    except KeyboardInterrupt:
        app.client.close()
