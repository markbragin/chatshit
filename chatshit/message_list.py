from textual.binding import Binding, BindingType
from textual.widgets import ListView, ListItem, Label


class MessageList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]

    def add_message(self, msg: str):
        bottom = self.max_scroll_y == int(self.scroll_y)
        label_classes = "message-label"
        if f"@{self.app.client.nickname}" in msg:  # type: ignore
            label_classes += " tagged"
        self.append(
            ListItem(
                Label(msg, classes=label_classes),
                classes="message-item",
            )
        )
        if bottom:
            try:
                self.scroll_end(animate=False)
            except:
                pass
