from socket import gaierror
from textual.app import ComposeResult, events
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from chatshit.network.client import Client


class LoginScreen(Screen):

    class Result:
        def __init__(self, client: Client, name: str):
            self.client = client
            self.name = name

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        classes: str | None = None,
    ):
        super().__init__(classes=classes)
        self._host = host
        self._port = port

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="input-form"):
            self.info = Static("", id="connecting-error")
            self.name_field = Input(id="name")
            self.ip_field = Input(id="ip")
            self.port_field = Input(id="port")
            self.username_field = Input(id="username")
            self.button = Button("Connect", id="connect")
            yield self.info
            yield self.ip_field
            yield self.port_field
            yield self.username_field
            yield self.name_field
            yield self.button

    def on_mount(self):
        self.ip_field.border_title = "IP"
        self.port_field.border_title = "PORT"
        self.username_field.border_title = "Username"
        self.name_field.border_title = "Name (optional)"
        self.ip_field.focus()
        if self._host and self._port:
            self.ip_field.value = self._host
            self.port_field.value = str(self._port)
            self.username_field.focus()

    def on_key(self, event: events.Key):
        if event.key == "escape":
            event.stop()
            self.dismiss(None)

    def on_button_pressed(self):
        try:
            self._client = Client(
                self.ip_field.value, int(self.port_field.value), self.username_field.value
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
        except OSError as e:
            self.info.update(e.strerror)
        else:
            self.dismiss(self.Result(self._client, self.name_field.value))
