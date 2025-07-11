from copy import deepcopy
from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Optional, cast

from loguru import _colorama
from nonechat import Backend
from loguru._logger import Logger
from nonechat.app import Frontend
from loguru._handler import Handler
from nonebot.log import logger, logger_id
from loguru._simple_sinks import StreamSink
from nonechat.model import Event as ConsoleEvent
from nonechat.message import Text, Emoji, Markup, Markdown
from nonechat.model import MessageEvent as ConsoleMessageEvent

from .event import Event, MessageEvent
from .message import Message, MessageSegment

if TYPE_CHECKING:
    from .adapter import Adapter


class AdapterConsoleBackend(Backend):
    _adapter: "Adapter"

    def __init__(self, frontend: "Frontend"):
        super().__init__(frontend)
        self.frontend.storage.current_user = replace(self.frontend.storage.current_user, id="User")
        self._origin_sink: Optional[StreamSink] = None

    def set_adapter(self, adapter: "Adapter"):
        self._adapter = adapter

    def on_console_load(self):
        current_handler: Handler = cast(Logger, logger)._core.handlers[logger_id]
        if current_handler._colorize and _colorama.should_wrap(self.frontend._fake_output):
            stream = _colorama.wrap(self.frontend._fake_output)
        else:
            stream = self.frontend._fake_output
        self._origin_sink = current_handler._sink
        current_handler._sink = StreamSink(stream)

    def on_console_mount(self):
        logger.success("Console mounted.")

    def on_console_unmount(self):
        if self._origin_sink is not None:
            current_handler: Handler = cast(Logger, logger)._core.handlers[logger_id]
            current_handler._sink = self._origin_sink
            self._origin_sink = None
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
                    if TYPE_CHECKING:
                        assert isinstance(elem, (Markdown, Markup))
                    message += MessageSegment(type=elem.__class__.__name__.lower(), data=asdict(elem))  # noqa
            self._adapter.post_event(
                MessageEvent(
                    time=event.time,
                    self_id=event.self_id,
                    user=event.user,
                    post_type="message",
                    message=message,
                    channel=event.channel,
                    original_message=deepcopy(message),
                )
            )
        else:
            self._adapter.post_event(
                Event(
                    time=event.time,
                    self_id=event.self_id,
                    user=event.user,
                    post_type=event.type,
                    channel=event.channel,
                )
            )
