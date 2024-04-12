from socket import gaierror
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from chatshit.network.client import Client


class LoginScreen(Screen):

    def compose(self) -> ComposeResult:
        with Container(id="input-form"):
            self.info = Static("", id="connecting-error")
            self.ip = Input(id="ip")
            self.port = Input(id="port")
            self.username = Input(id="username")
            self.button = Button("Connect", id="connect")
            yield self.info
            yield self.ip
            yield self.port
            yield self.username
            yield self.button

    def on_mount(self) -> None:
        self.ip.border_title = "IP"
        self.port.border_title = "PORT"
        self.username.border_title = "Username"

    def on_button_pressed(self) -> None:
        try:
            self._client = Client(
                self.ip.value, int(self.port.value), self.username.value
            )
            self._client.connect()
        except ValueError:
            self.info.update("Port is a number")
        except gaierror:
            self.info.update("Wrong address")
        except ConnectionRefusedError:
            self.info.update("No server on this port")
        except OverflowError:
            self.info.update("Port must be 0-65535.")
        except TimeoutError:
            self.info.update("Timeout")
        else:
            self.dismiss(self._client)

