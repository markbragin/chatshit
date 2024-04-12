from textual.binding import Binding, BindingType
from textual.widgets import ListView, ListItem, Label
from textual import events


class MemberList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]

    def add_member(self, msg: dict):
        if msg["Username"] == self.screen.client.username:
            label = Label(msg["Username"] + " (you)")
        else:
            label = Label(msg["Username"])

        uid = msg["Username"].encode().hex()
        self.append(ListItem(label, id=f"_{uid}"))

    def remove_member(self, msg: dict):
        self.remove_children(f"#_{str(msg['Username'])}")

    def on_key(self, event: events.Key):
        if event.key == "enter":
            val = self.screen.input.value
            username = bytes.fromhex(self.highlighted_child.id[1:]).decode()
            self.screen.input.value = f"{val}@{username}"
            self.screen.input.focus()
            event.stop()
