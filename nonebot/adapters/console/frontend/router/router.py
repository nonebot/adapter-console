from typing import Dict, Callable, Optional

from textual.widget import Widget
from textual.reactive import Reactive
from textual.message import Message, MessageTarget


class RouteChange(Message):
    def __init__(self, sender: MessageTarget, route: str):
        super().__init__(sender)
        self.route = route


class RouterView(Widget):
    current_route = Reactive[Optional[str]](None)

    def __init__(self, routes: Dict[str, Callable[[], Widget]], default_route: str):
        super().__init__()
        self.routes = routes
        self.default_route = default_route

        self.current_view: Optional[Widget] = None

    async def watch_current_route(self, current_route: str):
        if self.current_view:
            await self.current_view.remove()

        self.current_view = self.routes[current_route]()
        self.mount(self.current_view)

    def action_to(self, route: str):
        self.current_route = route

    def on_route_change(self, event: RouteChange):
        self.action_to(event.route)
