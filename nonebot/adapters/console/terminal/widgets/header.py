from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from textual.widgets import Header
from textual.reactive import Reactive
from rich.console import RenderableType


class HeadBar(Header):
    """
    Custom Header for Gupshup showing status for the server and a Welcome message
    """

    status: Reactive[str] = Reactive("Console")

    def __init__(self):
        super().__init__(tall=False, style=Style(color="#b48ead", bgcolor="#3b4252"))

    def render(self) -> RenderableType:
        header_table: Table = Table.grid(padding=(1, 1), expand=True)
        header_table.style = self.style
        header_table.add_column(justify="left", ratio=0, width=20)
        header_table.add_column("title", justify="center", ratio=1)
        header_table.add_column("clock", justify="center", width=10)
        header_table.add_row(
            "  " + self.status,
            Text(
                "Welcome to Console Bot Test", style=Style(bold=True, color="#ea5252")
            ),
            self.get_clock() if self.clock else "",
        )
        header: RenderableType
        header = Panel(header_table, style=self.style) if self.tall else header_table
        return header
