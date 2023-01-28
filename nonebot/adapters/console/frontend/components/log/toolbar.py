from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import Reactive

from ...router import RouteChange
from ..general.action import Action


class Toolbar(Widget):
    DEFAULT_CSS = """
    $toolbar-border-type: round;
    $toolbar-border-color: rgba(170, 170, 170, 0.7);
    $toolbar-border: $toolbar-border-type $toolbar-border-color;

    Toolbar {
        layout: horizontal;
        height: 3;
        width: 100%;
        border: $toolbar-border;
        padding: 0 1;
    }

    Toolbar Static {
        width: 100%;
        content-align: center middle;
    }

    Toolbar Action {
        width: 3;
    }
    """

    def __init__(self):
        super().__init__()
        self.back_button = Action("⬅️", id="back", classes="left")
        self.settings_button = Action("⚙️", id="settings", classes="right")

    def compose(self):
        yield self.back_button
        yield Static("Log", classes="center")
        yield self.settings_button

    async def on_action_pressed(self, event: Action.Pressed):
        event.stop()
        if event.action == self.back_button:
            self.emit_no_wait(RouteChange(self, "main"))
        elif event.action == self.settings_button:
            ...
