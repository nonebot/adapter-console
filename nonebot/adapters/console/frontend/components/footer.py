from textual.widget import Widget
from textual.widgets import Footer as TextualFooter


class Footer(Widget):
    def compose(self):
        yield TextualFooter()
