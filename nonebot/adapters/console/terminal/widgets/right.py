from rich.panel import Panel
from textual.widget import Widget

from rich import box
from rich.style import Style

class Right(Widget):
    def render(self):
        return Panel(
            "", 
            box=box.SQUARE,
            # style=Style(bgcolor="white",)
            )

