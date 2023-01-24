from textual.widget import Widget
from textual.containers import Horizontal
from sys import stdout
from .views import ChatView, LoggerView


class Body(Widget):
    DEFAULT_CSS = """
    Body {
        layout: horizontal;
    }
    """
    def __init__(self) -> None:
        super().__init__()
        self.chat_view = ChatView()

    def compose(self):
        yield from (
            self.chat_view,
            LoggerView(),
        )
        
    
    # def on_mount(self):
        