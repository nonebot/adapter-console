from textual.widgets import Footer as BaseFooter


class Footer(BaseFooter):
    def __init__(self) -> None:
        super().__init__()
        self.styles.background = "#cc6633"
