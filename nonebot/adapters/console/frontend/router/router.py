from typing import Dict

from textual.widget import Widget
from textual.message import Message, MessageTarget


class RouteChange(Message):
    def __init__(self, sender: MessageTarget, route: str):
        super().__init__(sender)
        self.route = route


class RouterView(Widget):
    def __init__(self, routes: Dict[str, Widget], default_route: str):
        super().__init__()
        self.routes = routes

        self.current_route = default_route

    def compose(self):
        yield from self.routes.values()

    def update(self):
        for r, w in self.routes.items():
            w.display = r == self.current_route

    def on_mount(self):
        self.update()

    def action_to(self, route: str):
        self.current_route = route
        self.update()

    def on_route_change(self, event: RouteChange):
        self.action_to(event.route)
