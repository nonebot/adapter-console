from textual.widget import Widget
from textual.widgets import Input as TextualInput


class InputBox(Widget):
    DEFAULT_CSS = """
    $input-background: rgba(0, 0, 0, 0);
    $input-border-type: round;
    $input-border-color: rgba(170, 170, 170, 0.7);
    $input-border-active-color: $accent;
    $input-border: $input-border-type $input-border-color;
    $input-border-active: $input-border-type $input-border-active-color;

    InputBox {
        height: auto;
        width: 100%;
        dock: bottom;
    }

    InputBox > Input {
        padding: 0 1;
        background: $input-background;
        border: $input-border !important;
    }
    InputBox > Input:focus {
        border: $input-border-active !important;
    }
    """

    def __init__(self):
        super().__init__()
        self.input = TextualInput(placeholder="Send Message")

    def compose(self):
        yield self.input
