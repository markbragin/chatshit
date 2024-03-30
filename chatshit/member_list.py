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
        self.append(ListItem(Label(msg["Nickname"]), id=f"_{str(msg['Id'])}"))

    def remove_member(self, msg: dict):
        self.remove_children(f"#_{str(msg['Id'])}")

    def on_key(self, event: events.Key):
        main_screen = self.app.get_screen("main_screen")
        if event.key == "enter":
            val = main_screen.input.value
            nickname = str(self.highlighted_child.children[0].renderable)
            main_screen.input.value = f"{val}@{nickname}"
            main_screen.input.focus()
            event.stop()
