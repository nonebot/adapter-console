from textual.widget import Widget

from .toolbar import Toolbar


class ChatRoom(Widget):
    def compose(self):
        yield Toolbar()
