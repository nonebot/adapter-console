from typing import cast

from textual.events import Click
from textual.widgets import Static
from textual.message import Message, MessageTarget


class Action(Static, can_focus=True):
    DEFAULT_CSS = """
    $action-active-color: $accent;
    
    Action.left {
        dock: left;
    }
    Action.right {
        dock: right;
    }
    Action:focus, Action:hover {
        color: $action-active-color;
    }
    """

    class Pressed(Message):
        def __init__(self, sender: MessageTarget) -> None:
            super().__init__(sender)

        @property
        def action(self) -> "Action":
            return cast(Action, self.sender)

    def on_click(self, event: Click):
        event.stop()
        self.emit_no_wait(Action.Pressed(self))
