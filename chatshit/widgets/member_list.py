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

    def add_member(self, username: str):
        if username == self.screen.client.username:
            label = Label(username + " (you)")
        else:
            label = Label(username)

        uid = username.encode().hex()
        self.append(ListItem(label, id=f"_{uid}"))

    def remove_member(self, username: str):
        uid = username.encode().hex()
        self.remove_children(f"#_{uid}")

    def on_key(self, event: events.Key):
        if event.key == "enter":
            val = self.screen.input.value
            uid = self.highlighted_child.id[1:]
            username = bytes.fromhex(uid).decode()
            self.screen.input.value = f"{val}@{username}"
            self.screen.input.focus()
            event.stop()
