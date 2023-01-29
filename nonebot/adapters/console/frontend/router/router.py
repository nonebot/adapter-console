from typing import Dict, Callable, Optional

from textual.widget import Widget
from textual.reactive import Reactive
from textual.message import Message, MessageTarget


class RouteChange(Message, bubble=True):
    def __init__(self, sender: MessageTarget, route: str):
        super().__init__(sender)
        self.route = route


class RouterView(Widget):
    DEFAULT_CSS = """
    RouterView {
        height: 100%;
        width: 100%;
    }
    """

    current_route = Reactive[Optional[str]](None)

    def __init__(self, routes: Dict[str, Callable[[], Widget]], default_route: str):
        super().__init__()
        self.routes = routes
        self.default_route = default_route

        self.current_view: Optional[Widget] = None

    async def on_mount(self):
        self.current_route = self.default_route

    async def watch_current_route(self, current_route: str):
        if self.current_view:
            await self.current_view.remove()

        self.current_view = self.routes[current_route]()
        await self.mount(self.current_view)

    def action_to(self, route: str):
        self.current_route = route

    def on_route_change(self, event: RouteChange):
        event.stop()
        self.action_to(event.route)
