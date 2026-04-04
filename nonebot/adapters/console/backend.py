from typing import TYPE_CHECKING, cast

from loguru import _colorama
from loguru._handler import Handler
from loguru._logger import Logger
from loguru._simple_sinks import StreamSink
from nonebot.log import logger, logger_id
from nonechat import Backend
from nonechat.app import Frontend
from nonechat.backend import BotAdd
from nonechat.model import Event as ConsoleEvent
from nonechat.model import MessageEvent as ConsoleMessageEvent
from nonechat.model import Robot

from .bot import Bot
from .event import Event, MessageEvent
from .message import Message

if TYPE_CHECKING:
    from .adapter import Adapter


class AdapterConsoleBackend(Backend):
    _adapter: "Adapter"

    def __init__(self, frontend: "Frontend"):
        super().__init__(frontend)
        self.current_user.id = "user"
        self._origin_sink: StreamSink | None = None

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

    async def add_bot(self, bot: Robot):
        if self.storage.add_bot(bot):
            for watcher in self.bot_watchers:
                watcher.post_message(BotAdd(bot))
            self._adapter.bot_connect(Bot(self._adapter, bot))

    async def on_console_mount(self):
        logger.success("Console mounted.")

    async def on_console_unmount(self):
        if self._origin_sink is not None:
            current_handler: Handler = cast(Logger, logger)._core.handlers[logger_id]
            current_handler._sink = self._origin_sink
            self._origin_sink = None
        logger.success("Console unmounted.")
        logger.warning("Press Ctrl-C for Application exit")

    async def post_event(self, event: ConsoleEvent):
        if isinstance(event, ConsoleMessageEvent):
            self._adapter.post_event(
                MessageEvent(
                    time=event.time,
                    self_id=event.self_id,
                    user=event.user,
                    post_type="message",
                    message_id=event.message_id,
                    message=Message.from_console_message(event.message),
                    channel=event.channel,
                ).convert()
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
