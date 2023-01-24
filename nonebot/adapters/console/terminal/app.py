from textual.app import App, actions, ActionError
from typing import Callable, List, Optional, Tuple, Coroutine, Union
from asyncio import create_task, wait

from .header import Header
from .body import Body
from .footer import Footer
from ..event import Event, User


class Terminal(App):
    def __init__(self):
        super().__init__()
        self.callable_event_list: List[Callable[[Event], Coroutine]] = []
        self.title = "Console"
        self.sub_title = "Welcome to terminal"
        self.self_info = User(
            user_id="1",
            nickname="user",
            group_id=0,
            is_me=True,
        )
        self.header = Header(True)
        self.body = Body()
        self.footer = Footer()

    async def action(
        self,
        action: Union[str, Tuple[str, tuple[str, ...]]],
        default_namespace: Optional[object] = None,
    ) -> bool:
        """Perform an action (remove print).

        Args:
            action: Action encoded in a string.
            default_namespace: Namespace to use if not provided in the action,
                or None to use app. Defaults to None.

        Returns:
            True if the event has handled.
        """
        if isinstance(action, str):
            target, params = actions.parse(action)
        else:
            target, params = action
        implicit_destination = True
        if "." in target:
            destination, action_name = target.split(".", 1)
            if destination not in self._action_targets:
                raise ActionError(f"Action namespace {destination} is not known")
            action_target = getattr(self, destination)
            implicit_destination = True
        else:
            action_target = default_namespace or self
            action_name = target

        handled = await self._dispatch_action(action_target, action_name, params)
        if not handled and implicit_destination and not isinstance(action_target, App):
            handled = await self.app._dispatch_action(self.app, action_name, params)
        return handled

    def compose(self):
        yield from (
            self.header,
            self.body,
            self.footer
        )

    def on_mount(self):
        ...
    
    async def shutdown(self): 
        await self._shutdown()
    
    def add_handle_event(self, callable: Callable[[Event], Coroutine]):
        self.callable_event_list.append(callable)
    
    def trigger_handle_event(self, event: Event):
        if self.callable_event_list:
            create_task(
                wait([callable(event) for callable in self.callable_event_list])
            )


