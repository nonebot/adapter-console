from typing import Any, Union

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Adapter
from nonebot.adapters import Bot as BaseBot

from .config import BaseInfo
from .terminal import console_view
from .event import Event, MessageEvent
from .message import Message, MessageSegment


class Bot(BaseBot):
    @overrides(BaseBot)
    def __init__(self, adapter: "Adapter", bot_config: BaseInfo):
        super().__init__(adapter, "0")
        self.bot_config: BaseInfo = bot_config

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
            event.user_info = self.bot_config
            await console_view.send_message(event, message)

    async def handle_event(self, event: Event) -> None:
        """处理收到的事件。"""
        await handle_event(self, event)
