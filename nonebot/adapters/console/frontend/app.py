import contextlib
from datetime import datetime
from typing import Any, Dict, TextIO, Optional, cast

from textual.app import App
from textual.widgets import Input
from textual.binding import Binding
from nonebot.log import logger, logger_id, default_filter, default_format

from nonebot.adapters.console import Bot, Event, Adapter, Message, MessageEvent

from .storage import Storage
from .router import RouterView
from .log_redirect import FakeIO
from .views.log_view import LogView
from .components.footer import Footer
from .components.header import Header
from .views.horizontal import HorizontalView


class Frontend(App):
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True),
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+s", "screenshot", "Save a screenshot"),
        Binding("ctrl+underscore", "focus_input", "Focus input", key_display="ctrl+/"),
    ]

    ROUTES = {"main": lambda: HorizontalView(), "log": lambda: LogView()}

    def __init__(self, adapter: Adapter):
        super().__init__()
        self.adapter = adapter
        self.title = "NoneBot"
        self.sub_title = "Welcome to console"

        self.storage = Storage()

        self._logger_id: Optional[int] = None
        self._should_restore_logger: bool = False
        self._fake_output = cast(TextIO, FakeIO(self.storage))
        self._redirect_stdout: Optional[contextlib.redirect_stdout[TextIO]] = None
        self._redirect_stderr: Optional[contextlib.redirect_stderr[TextIO]] = None

        self.adapter.add_client(self._handle_api)

    def compose(self):
        yield Header()
        yield RouterView(self.ROUTES, "main")
        yield Footer()

    def on_load(self):
        with contextlib.suppress(ValueError):
            logger.remove(logger_id)
            self._should_restore_logger = True
        self._logger_id = logger.add(
            self._fake_output,
            level=0,
            diagnose=False,
            filter=default_filter,
            format=default_format,
        )

    def on_mount(self):
        with contextlib.suppress(Exception):
            stdout = contextlib.redirect_stdout(self._fake_output)
            stdout.__enter__()
            self._redirect_stdout = stdout

        with contextlib.suppress(Exception):
            stderr = contextlib.redirect_stderr(self._fake_output)
            stderr.__enter__()
            self._redirect_stderr = stderr

    def on_unmount(self):
        if self._redirect_stderr is not None:
            self._redirect_stderr.__exit__(None, None, None)
            self._redirect_stderr = None
        if self._redirect_stdout is not None:
            self._redirect_stdout.__exit__(None, None, None)
            self._redirect_stdout = None

        if self._logger_id is not None:
            logger.remove(self._logger_id)
            self._logger_id = None
        if self._should_restore_logger:
            logger.add(
                self.adapter._stdout,
                level=0,
                diagnose=False,
                filter=default_filter,
                format=default_format,
            )
            self._should_restore_logger = False

    async def _handle_api(self, bot: Bot, api: str, data: Dict[str, Any]):
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

    def action_focus_input(self):
        with contextlib.suppress(Exception):
            self.query_one(Input).focus()

    def action_post_message(self, message: str):
        self.action_post_event(
            MessageEvent(
                time=datetime.now(),
                self_id=self.adapter.bot.self_id,
                post_type="message",
                message=Message(message),
                user=self.storage.current_user,
            )
        )

    def action_post_event(self, event: Event):
        if isinstance(event, MessageEvent):
            self.storage.write_chat(event)
        self.adapter.post_event(event)
