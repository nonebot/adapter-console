from textual.widget import Widget
from textual.widgets import Input as TextualInput


class InputBox(Widget):
    DEFAULT_CSS = """
    InputBox {
        height: auto;
        width: 100%;
        dock: bottom;
    }
    
    InputBox > Input {
        padding: 0 1;
        border: solid $background !important;
    }
    InputBox > Input:focus {
        border: solid $accent !important;
    }
    """

    def __init__(self):
        super().__init__()
        self.input = TextualInput(placeholder="Send Message")

    def compose(self):
        yield self.input
