from typing import TYPE_CHECKING, cast

from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import Reactive

from ...router import RouteChange
from ..general.action import Action

if TYPE_CHECKING:
    from ...views.horizontal import HorizontalView


class Toolbar(Widget):
    DEFAULT_CSS = """
    Toolbar {
        layout: horizontal;
        height: 3;
        width: 100%;
        dock: top;
        border: round $foreground;
    }

    Toolbar Static {
        width: 100%;
        content-align: center middle;
    }

    Toolbar Action {
        width: 3;
    }
    Toolbar Action.mr {
        margin-right: 4;
    }
    """

    title: Reactive[str] = Reactive("Bot")

    def __init__(self):
        super().__init__()
        self.exit_button = Action("❌", id="exit", classes="left")
        self.settings_button = Action("⚙️", id="settings", classes="right mr")
        self.log_button = Action("📝", id="log", classes="right")

    def compose(self):
        yield self.exit_button
        yield Static(self.title, classes="center")
        yield self.settings_button
        yield self.log_button

    async def on_action_pressed(self, event: Action.Pressed):
        event.stop()
        if event.action == self.exit_button:
            self.app.exit()
        elif event.action == self.settings_button:
            ...
        elif event.action == self.log_button:
            view = cast("HorizontalView", self.app.query_one("HorizontalView"))
            if view.can_show_log:
                view.action_toggle_log_panel()
            else:
                self.emit_no_wait(RouteChange(self, "log"))
