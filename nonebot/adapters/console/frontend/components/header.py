from textual.widgets import Header as TextualHeader


class Header(TextualHeader):
    DEFAULT_CSS = """
    Header > HeaderIcon {
        color: #ea5252;
    }
    """

    def __init__(self):
        super().__init__(show_clock=True)
