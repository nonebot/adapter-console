from textual.widget import Widget
from textual.widgets import Header as TextualHeader


class Header(Widget):
    def compose(self):
        yield TextualHeader(True)
