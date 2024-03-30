from textual.binding import Binding, BindingType
from textual.widgets import ListView, ListItem, Label


class MemberList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]

    def add_member(self, msg: dict):
        self.append(
            ListItem(
                Label(msg["Nickname"], classes="member-label"),
                id=f"_{str(msg['Id'])}",
                classes="member-item",
            )
        )

    def remove_member(self, msg: dict):
        self.remove_children(f"#_{str(msg['Id'])}")
