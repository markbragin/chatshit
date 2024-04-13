from socket import gaierror
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Input, Static


class CreateServerScreen(Screen):

    def compose(self) -> ComposeResult:
        with Container(id="input-form"):
            self.info = Static("", id="connecting-error")
            self.ip = Input(id="ip")
            self.port = Input(id="port")
            self.button = Button("Create")
            yield self.info
            yield self.ip
            yield self.port
            yield self.button

    def on_mount(self):
        self.ip.placeholder = "0.0.0.0"
        self.ip.border_title = "IP"
        self.port.border_title = "PORT"

    def on_button_pressed(self):
        try:
            host = self.ip.value if self.ip.value else self.ip.placeholder
            port = int(self.port.value)
            self.app.create_server(host, port)
        except PermissionError:
            self.info.update("PermissionError. Try another port")
        except ValueError:
            self.info.update("Port is a number")
        except gaierror:
            self.info.update("Wrong address")
        except OverflowError:
            self.info.update("Port must be 0-65535.")
        except OSError as e:
            self.info.update(e.strerror)
        else:
            self.dismiss()

