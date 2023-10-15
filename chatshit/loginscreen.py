from socket import gaierror
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Input, Static


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        with Container(id="input-form"):
            self.info = Static("", id="connecting-error")
            self.ip = Input(id="ip")
            self.port = Input(id="port")
            self.nickname = Input(id="nickname")
            self.button = Button("Connect", id="connect")
            yield self.info
            yield self.ip
            yield self.port
            yield self.nickname
            yield self.button

    def on_mount(self) -> None:
        self.ip.border_title = "IP"
        self.port.border_title = "PORT"
        self.nickname.border_title = "Nickname"

    def on_button_pressed(self) -> None:
        try:
            self.app.client.set_address(self.ip.value, int(self.port.value))
            self.app.client.set_nickname(self.nickname.value)
            self.app.client.connect()
        except ValueError:
            self.info.update("Port is a number")
        except gaierror:
            self.info.update("Wrong address")
        except ConnectionRefusedError:
            self.info.update("No server on this port")
        else:
            self.dismiss()
