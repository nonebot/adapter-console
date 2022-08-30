from rich import box
from rich.panel import Panel
from rich.style import Style
from textual.widget import Widget


class Right(Widget):
    def render(self):
        return Panel(
            "",
            box=box.SQUARE,
            # style=Style(bgcolor="white",)
        )
