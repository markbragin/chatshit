from textual.binding import Binding, BindingType
from textual.message import Message
from textual.widgets import ListView, ListItem, Label
from textual import events


class ServerList(ListView):

    class ConnectTo(Message):
        def __init__(self, server_id: int):
            super().__init__()
            self.server_id = server_id


    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]

    def add_server(self, server_id: int, host: str, port: int):
        name = f"{host}:{port}"
        label = Label(name)
        self.append(ListItem(label, id=f"_{server_id}"))

    def remove_server(self, server_id: int):
        self.remove_children(f"#_{server_id}")

    def on_key(self, event: events.Key):
        if event.key == "enter":
            server_id = int(self.highlighted_child.id[1:])
            self.post_message(self.ConnectTo(server_id))
            event.stop()
