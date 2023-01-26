from textual.events import Resize
from textual.widget import Widget
from textual.reactive import Reactive

from ..components.log import LogPanel
from ..components.chatroom import ChatRoom

SHOW_LOG_BREAKPOINT = 120


class HorizontalView(Widget):
    show_log: Reactive[bool] = Reactive(True)

    def __init__(self):
        self.chatroom = ChatRoom()
        self.log_panel = LogPanel()

    def watch_show_log(self, show_log: bool):
        self.log_panel.display = show_log

    def responsive(self, width: int) -> None:
        self.show_log = width > SHOW_LOG_BREAKPOINT

    def on_resize(self, event: Resize):
        self.responsive(event.size.width)

    def compose(self):
        yield self.chatroom
        yield self.log_panel
