from typing import Any, Union

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Adapter
from nonebot.adapters import Bot as BaseBot

from asyncio import create_task

from .terminal import terminal
from .event import Event, MessageEvent, Robot
from .message import Message, MessageSegment


class Bot(BaseBot):
    @overrides(BaseBot)
    def __init__(self, adapter: "Adapter", bot_config: Robot):
        super().__init__(adapter, str(bot_config.user_id))
        self.bot_config: Robot = bot_config

    @property
    def type(self) -> str:
        return "Console"

    @overrides(BaseBot)
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> Any:
        if isinstance(event, MessageEvent):
            await terminal.body.chat_view.send_message(
                robot=self.bot_config,
                message=message
            )

    async def handle_event(self, event: Event) -> None:
        """处理收到的事件"""
        create_task(handle_event(self, event))
