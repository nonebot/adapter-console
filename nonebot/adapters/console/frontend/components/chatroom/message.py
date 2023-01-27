from datetime import datetime
from typing import TYPE_CHECKING

from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from nonebot.adapters.console import MessageEvent


class Timer(Widget):
    DEFAULT_CSS = """
    Timer {
        height: 1;
        width: 100%;
        content-align: center;
    }
    """

    def __init__(self, time: datetime):
        super().__init__()
        self.time = time

    def compose(self):
        yield Static(self.time.strftime("%H:%M:%S"))


class Message(Widget):
    def __init__(self, message: "MessageEvent"):
        self.message = message
