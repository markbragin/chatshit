from textual.binding import Binding, BindingType
from textual.widgets import ListView, ListItem, Label


class MessageList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]
    hl_color = "light_coral"

    def add_message(self, msg: str):
        bottom = self.max_scroll_y == int(self.scroll_y)

        tag = f"@{self.app.client.nickname}"
        if tag in msg.split():
            msg = self._highlight_tag(msg, tag)

        self.append(ListItem(Label(f"{msg}")))
        if bottom:
            try:
                self.scroll_end(animate=False)
            except:
                pass

    def _highlight_tag(self, msg: str, tag: str) -> str:
        pos = msg.find(tag)
        return (
            msg[:pos]
            + f"[{self.hl_color}]"
            + msg[pos : pos + len(tag)]
            + f"[/{self.hl_color}]"
            + msg[pos + len(tag) :]
        )
