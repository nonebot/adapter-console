import sys
import contextlib
from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Optional

from nonechat import Backend
from nonechat.info import Robot
from nonechat.app import Frontend
from nonechat.message import Text, Emoji
from nonechat.info import Event as ConsoleEvent
from nonechat.info import MessageEvent as ConsoleMessageEvent
from nonebot.log import logger, logger_id, default_filter, default_format

from .event import Event, MessageEvent
from .message import Message, MessageSegment

if TYPE_CHECKING:
    from .adapter import Adapter


class AdapterConsoleBackend(Backend):
    def __init__(self, frontend: "Frontend"):
        super().__init__(frontend)
        self.frontend.storage.current_user = replace(
            self.frontend.storage.current_user, id="User"
        )
        self._stdout = sys.stdout
        self._logger_id: Optional[int] = None
        self._should_restore_logger: bool = False
        self._adapter: Optional["Adapter"] = None  # noqa: UP037

    def set_adapter(self, adapter: "Adapter"):
        self._adapter = adapter
        self.bot = Robot(id=self._adapter.bot.self_id)

    def on_console_load(self):
        with contextlib.suppress(ValueError):
            logger.remove(logger_id)
            self._should_restore_logger = True
        self._logger_id = logger.add(
            self.frontend._fake_output,
            level=0,
            diagnose=False,
            filter=default_filter,
            format=default_format,
        )

    def on_console_mount(self):
        self._adapter.bot_connect(self._adapter.bot)
        logger.success("Console mounted.")

    def on_console_unmount(self):
        if self._logger_id is not None:
            logger.remove(self._logger_id)
            self._logger_id = None
        if self._should_restore_logger:
            logger.add(
                self._stdout,
                level=0,
                diagnose=False,
                filter=default_filter,
                format=default_format,
            )
            self._should_restore_logger = False
        self._adapter.bot_disconnect(self._adapter.bot)
        logger.success("Console unmounted.")
        logger.warning("Press Ctrl-C for Application exit")

    async def post_event(self, event: ConsoleEvent):
        if isinstance(event, ConsoleMessageEvent):
            message = Message()
            for elem in event.message:
                if isinstance(elem, Text):
                    message += MessageSegment.text(elem.text)
                elif isinstance(elem, Emoji):
                    message += MessageSegment.emoji(elem.name)
                else:
                    message += MessageSegment(
                        type=elem.__class__.__name__.lower(), data=asdict(elem)  # noqa
                    )
            self._adapter.post_event(
                MessageEvent(
                    time=event.time,
                    self_id=event.self_id,
                    user=event.user,
                    post_type="message",
                    message=message,
                )
            )
        else:
            self._adapter.post_event(
                Event(
                    time=event.time,
                    self_id=event.self_id,
                    user=event.user,
                    post_type=event.type,
                )
            )
