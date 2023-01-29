from datetime import timedelta
from typing import TYPE_CHECKING, Iterable, Optional, cast

from textual.widget import Widget

from .message import Timer, Message

if TYPE_CHECKING:
    from nonebot.adapters.console import MessageEvent

    from ...app import Frontend
    from ...storage import Storage


class ChatHistory(Widget):
    DEFAULT_CSS = """
    ChatHistory {
        layout: vertical;
        height: 100%;
        overflow: hidden scroll;
        scrollbar-size-vertical: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.last_msg: Optional["MessageEvent"] = None

    @property
    def storage(self) -> "Storage":
        return cast("Frontend", self.app).storage

    def on_mount(self):
        self.on_new_message(self.storage.chat_history)
        self.storage.add_chat_watcher(self.on_new_message)

    def on_unmount(self):
        self.storage.remove_chat_watcher(self.on_new_message)

    def action_new_message(self, message: "MessageEvent"):
        if not self.last_msg or message.time - self.last_msg.time > timedelta(
            minutes=1
        ):
            self.mount(Timer(message.time))
        self.mount(Message(message))
        self.last_msg = message

    def on_new_message(self, messages: Iterable["MessageEvent"]):
        for message in messages:
            self.action_new_message(message)

    def action_clear_history(self):
        for msg in self.walk_children():
            cast(Widget, msg).remove()
        self.storage.chat_history.clear()
