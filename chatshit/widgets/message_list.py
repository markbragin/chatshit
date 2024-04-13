from textual.binding import Binding, BindingType
from textual.widgets import ListView, ListItem, Label
from textual import events
from textual.message import Message

from chatshit.screens.delete_message_screen import DeleteMessageScreen


class MessageList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]
    hl_color = "light_coral"

    class Delete(Message):
        def __init__(self, msg_id: int):
            super().__init__()
            self.msg_id = msg_id

    def add_message(self, msg: dict):
        bottom = self.max_scroll_y == int(self.scroll_y)

        text = msg["Text"]
        tag = f"@{self.screen.client.username}"
        if tag in text.split():
            text = self._highlight_tag(msg["Text"], tag)

        self.append(ListItem(Label(f"{text}"), id=f"_{msg['Id']}"))
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

    def delete_message(self, msg_id: int):
        self.remove_children(f"#_{msg_id}")
        self.action_cursor_down()
        self.action_cursor_up()

    def on_key(self, event: events.Key):
        if event.key == "d" and self.highlighted_child:
            msg_id = int(self.highlighted_child.id[1:])
            self.app.push_screen(DeleteMessageScreen(msg_id), self.del_message)
            event.stop()

    def del_message(self, ans: DeleteMessageScreen.Answer):
        if ans.delete:
            self.delete_message(ans.msg_id)
            if ans.for_all:
                self.post_message(self.Delete(ans.msg_id))
