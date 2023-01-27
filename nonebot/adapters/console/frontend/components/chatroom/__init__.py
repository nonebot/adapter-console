from textual.widget import Widget

from .input import InputBox
from .toolbar import Toolbar
from .history import ChatHistory


class ChatRoom(Widget):
    def compose(self):
        yield Toolbar()
        yield ChatHistory()
        yield InputBox()
