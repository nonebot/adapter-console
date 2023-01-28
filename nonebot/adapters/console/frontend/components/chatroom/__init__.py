from textual.widget import Widget

from .input import InputBox
from .toolbar import Toolbar
from .history import ChatHistory


class ChatRoom(Widget):
    DEFAULT_CSS = """
    ChatRoom {
        layout: vertical;
    }
    ChatRoom > Toolbar {
        dock: top;
    }
    ChatRoom > InputBox {
        dock: bottom;
    }
    """

    def compose(self):
        yield Toolbar()
        yield ChatHistory()
        yield InputBox()
