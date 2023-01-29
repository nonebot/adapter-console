from textual.widget import Widget
from textual.widgets import Header as TextualHeader


class Header(Widget):
    DEFAULT_CSS = """
    Header > HeaderIcon {
        color: #ea5252;
    }
    """

    def compose(self):
        yield TextualHeader(True)
