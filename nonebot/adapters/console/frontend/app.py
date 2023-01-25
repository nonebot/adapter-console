from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

from textual.app import App
from textual.binding import Binding

from .router import RouterView
from .views.log_view import LogView
from .views.chatroom import ChatRoom
from .components.footer import Footer
from .components.header import Header

if TYPE_CHECKING:
    from nonebot.adapters.console import Bot, Event, Adapter


class Frontend(App):
    CSS_PATH = Path(__file__).parent / "app.css"

    BINDINGS = [
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+s", "screenshot", "Save a screenshot"),
    ]

    ROUTES = {"chatroom": ChatRoom(), "log": LogView()}

    def __init__(self, adapter: "Adapter"):
        super().__init__()
        self.adapter = adapter
        self.title = "NoneBot"
        self.sub_title = "Welcome to console"

        self.adapter.add_client(self._handle_api)

    def compose(self):
        yield Header()
        yield RouterView(self.ROUTES, "chatroom")
        yield Footer()

    async def _handle_api(self, bot: "Bot", api: str, data: Dict[str, Any]):
        self.log(f"API: {api} {data}")

    async def action_post_event(self, event: "Event"):
        self.adapter.post_event(event)
