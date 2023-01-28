from enum import Enum
from datetime import datetime

from rich.panel import Panel
from textual.widget import Widget
from textual.widgets import Static
from rich.console import RenderableType

from nonebot.adapters.console import User, MessageEvent


class Timer(Widget):
    DEFAULT_CSS = """
    Timer {
        layout: horizontal;
        height: 1;
        width: 100%;
        align: center middle;
    }
    Timer > Static {
        width: auto;
    }
    """

    def __init__(self, time: datetime):
        super().__init__()
        self.time = time

    def compose(self):
        yield Static(self.time.strftime("%H:%M"))


class Side(str, Enum):
    LEFT = "left"
    RIGHT = "right"


class Message(Widget):
    DEFAULT_CSS = """
    Message {
        layout: horizontal;
        height: auto;
        width: 100%;
        align-vertical: top;
    }
    Message.left {
        align-horizontal: left;
    }
    Message.right {
        align-horizontal: right;
    }
    """

    def __init__(self, event: "MessageEvent"):
        self.event = event
        self.side: Side = Side.LEFT if event.user.id == event.self_id else Side.RIGHT
        super().__init__(classes="left" if self.side == Side.LEFT else "right")

    def compose(self):
        if self.side == Side.LEFT:
            yield Avatar(self.event.user)
            yield Bubble(self.event.message, self.side)
        else:
            yield Bubble(self.event.message, self.side)
            yield Avatar(self.event.user)


class Avatar(Widget):
    DEFAULT_CSS = """
    Avatar {
        layout: horizontal;
        height: auto;
        width: auto;
        min-height: 1;
        min-width: 3;
    }
    """

    def __init__(self, user: User):
        super().__init__()
        self.user = user

    def render(self):
        return self.user.avatar


class Bubble(Widget):
    DEFAULT_CSS = """
    $bubble-max-width: 65%;
    $bubble-border-type: round;
    $bubble-border-color: rgba(170, 170, 170, 0.7);
    $bubble-border: $bubble-border-type $bubble-border-color;
    
    Bubble {
        height: auto;
        width: auto;
        min-height: 1;
        max-width: $bubble-max-width;
        padding: 0 1;
        border: $bubble-border;
    }
    """

    def __init__(self, renderable: RenderableType, side: Side):
        super().__init__()
        self.renderable = renderable
        self.side = side

    def render(self):
        return self.renderable
