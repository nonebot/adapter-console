import sys
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from contextlib import redirect_stderr, redirect_stdout

from textual.app import App
from textual.events import Unmount
from textual.binding import Binding
from nonebot.log import logger, default_filter, default_format

import nonebot
from nonebot.adapters.console import MessageEvent

from .storage import Storage
from .router import RouterView
from .log_redirect import FakeIO
from .views.log_view import LogView
from .components.footer import Footer
from .components.header import Header
from .views.horizontal import HorizontalView

if TYPE_CHECKING:
    from nonebot.adapters.console import Bot, Event, Adapter


class Frontend(App):
    BINDINGS = [
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+s", "screenshot", "Save a screenshot"),
    ]

    ROUTES = {"main": lambda: HorizontalView(), "log": lambda: LogView()}

    def __init__(self, adapter: "Adapter"):
        super().__init__()
        self.adapter = adapter
        self.title = "NoneBot"
        self.sub_title = "Welcome to console"

        self.storage = Storage()

        self._logger_id: Optional[int] = None
        self._fake_output = FakeIO(self.storage)
        self._redirect_stdout = redirect_stdout(self._fake_output)  # type: ignore
        self._redirect_stderr = redirect_stderr(self._fake_output)  # type: ignore

        self.adapter.add_client(self._handle_api)

    def compose(self):
        yield Header()
        yield RouterView(self.ROUTES, "main")
        yield Footer()

    def on_mount(self):
        self._redirect_stdout.__enter__()
        self._redirect_stderr.__enter__()
        self._logger_id = logger.add(
            sys.stdout,
            level=0,
            diagnose=False,
            filter=default_filter,
            format=default_format,
        )

    def on_unmount(self, event: Unmount):
        if self._logger_id is not None:
            logger.remove(self._logger_id)
        self._redirect_stderr.__exit__(None, None, None)
        self._redirect_stdout.__exit__(None, None, None)

    async def _handle_api(self, bot: "Bot", api: str, data: Dict[str, Any]):
        if api == "send_msg":
            self.storage.write_chat(
                MessageEvent(
                    time=datetime.now(),
                    self_id=bot.self_id,
                    post_type="message",
                    message=data["message"],
                    user=bot.info,
                )
            )

    async def action_post_event(self, event: "Event"):
        self.adapter.post_event(event)
