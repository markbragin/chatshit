from textual.binding import Binding, BindingType
from textual.message import Message
from textual.widgets import ListView, ListItem, Label
from textual import events

from chatshit.screens.confirmation_screen import ConfirmationScreen


class ChatList(ListView):

    BINDINGS: list[BindingType] = [
        Binding("j", "cursor_down", "Cursor_down", show=False),
        Binding("k", "cursor_up", "Cursor_up", show=False),
        Binding("[", "scroll_home", "Scroll home", show=False),
        Binding("]", "scroll_end", "Scroll end", show=False),
    ]

    class OpenChat(Message):
        def __init__(self, chat_id: int):
            super().__init__()
            self.chat_id = chat_id

    class LeaveChat(Message):
        def __init__(self, chat_id: int):
            super().__init__()
            self.chat_id = chat_id

    def add_chat(self, chat_id: int, host: str, port: int, name: str = ""):
        if not name:
            name = f"{host}:{port}"
        label = Label(name)
        self.append(ListItem(label, id=f"_{chat_id}"))

    def remove_chat(self, chat_id: int):
        self.remove_children(f"#_{chat_id}")
        self.action_cursor_down()
        self.action_cursor_up()

    def on_key(self, event: events.Key):
        if event.key == "enter":
            chat_id = int(self.highlighted_child.id[1:])
            self.post_message(self.OpenChat(chat_id))
            event.stop()
        elif event.key == "d":
            chat_id = int(self.highlighted_child.id[1:])
            q = "Do you want to delete this chat?"
            self.app.push_screen(
                ConfirmationScreen(q, chat_id), self.leave_chat
            )
            event.stop()

    def leave_chat(self, ans: ConfirmationScreen.Answer):
        if ans.ans == True:
            self.post_message(self.LeaveChat(ans.data))
