from textual.widget import Widget

from ..components.log import LogPanel


class LogView(Widget):
    def compose(self):
        yield LogPanel()
