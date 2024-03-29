from threading import Thread
from time import sleep

from socket import gaierror
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .client import Client


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
            self.connect_to_server()
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
            self.dismiss()

    def connect_to_server(self):
        self.app.client = Client(
            self.ip.value, int(self.port.value), self.nickname.value
        )
        self.app.client.connect()
        self.app.set_interval(0.1, callback=self.app.update_messages)
