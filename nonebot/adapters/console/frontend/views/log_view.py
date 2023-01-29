from textual.widget import Widget

from ..components.log import LogPanel
from ..components.log.toolbar import Toolbar


class LogView(Widget):
    DEFAULT_CSS = """
    LogView > Toolbar {
        dock: top;
    }
    """

    def compose(self):
        yield Toolbar()
        yield LogPanel()
