from textual.screen import Screen
from chatshit.network.client import Client


class ClientScreen(Screen):
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        client: Client | None = None,
        classes: str | None = None,
        name: str | None = None
    ):
        super().__init__(classes=classes, name=name)
        self._host = host
        self._port = port
        self.client = client
        self.chat_name = None
