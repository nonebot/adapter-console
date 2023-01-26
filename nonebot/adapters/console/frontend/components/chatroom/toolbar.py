from textual.widget import Widget
from textual.widgets import Static
from textual.reactive import Reactive, watch


class Toolbar(Widget):
    DEFAULT_CSS = """
    Toolbar {
        layout: horizontal;
        height: 3;
        width: 100%;
        dock: top;
        border: solid $accent;
    }

    Toolbar Static.left {
        width: 3;
        dock: left;
    }

    Toolbar Static.center {
        width: 100%;
        content-align: center middle;
    }

    Toolbar Static.right {
        width: 3;
        dock: right;
    }

    Toolbar Static.mr-3 {
        margin-right: 3;
    }
    """

    title: Reactive[str] = Reactive("Bot")

    def __init__(self):
        super().__init__()
        self.exit_button = Static("❌", id="exit", classes="left")
        self.settings_button = Static("⚙️", id="settings", classes="right")
        self.log_button = Static("📝", id="log", classes="right")

    def compose(self):
        yield self.exit_button
        yield Static(self.title, classes="center")
        yield self.settings_button
        yield self.log_button

    def on_mount(self):
        watch(self.app.query_one("HorizontalView"), "show_log", self.watch_show_log)

    def watch_show_log(self, show_log):
        self.settings_button.set_class(not show_log, "mr-3")
        self.log_button.display = not show_log
