from textual.events import Resize
from textual.widget import Widget
from textual.reactive import Reactive

from ..components.log import LogPanel
from ..components.chatroom import ChatRoom

SHOW_LOG_BREAKPOINT = 120


class HorizontalView(Widget):
    DEFAULT_CSS = """
    HorizontalView {
        layout: horizontal;
        height: 100%;
        width: 100%;
    }

    HorizontalView > * {
        height: 100%;
        width: 100%;
    }

    HorizontalView > .-w-50 {
        width: 50% !important;
    }
    """

    show_log: Reactive[bool] = Reactive(True)

    def __init__(self):
        super().__init__()
        self.chatroom = ChatRoom()
        self.log_panel = LogPanel()

    def compose(self):
        yield self.chatroom
        yield self.log_panel

    def on_resize(self, event: Resize):
        self.responsive(event.size.width)

    async def watch_show_log(self, show_log: bool):
        self.log_panel.display = show_log
        self.chatroom.set_class(show_log, "-w-50")
        self.log_panel.set_class(show_log, "-w-50")

    def responsive(self, width: int) -> None:
        self.show_log = width > SHOW_LOG_BREAKPOINT
