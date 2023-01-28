import re
from typing import TYPE_CHECKING, Any, Union

from nonebot.typing import overrides
from nonebot.message import handle_event

from nonebot.adapters import Adapter
from nonebot.adapters import Bot as BaseBot

from .utils import log
from .message import Message, MessageSegment
from .event import Event, Robot, MessageEvent


def _check_nickname(bot: "Bot", event: MessageEvent) -> None:
    first_msg_seg = event.message[0]
    if first_msg_seg.type != "text":
        return

    nicknames = {re.escape(n) for n in bot.config.nickname}
    if not nicknames:
        return

    # check if the user is calling me with my nickname
    nickname_regex = "|".join(nicknames)
    first_text = first_msg_seg.data["text"]
    if m := re.search(rf"^({nickname_regex})([\s,，]*|$)", first_text, re.IGNORECASE):
        log("DEBUG", f"User is calling me {m[1]}")
        first_msg_seg.data["text"] = first_text[m.end() :]


class Bot(BaseBot):
    if TYPE_CHECKING:

        async def send_msg(self, user_id: str, message: Message, **kwargs: Any) -> Any:
            ...

    @overrides(BaseBot)
    def __init__(self, adapter: "Adapter", self_id: str):
        super().__init__(adapter, self_id)
        self.info = Robot(id=self_id)

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
        full_message = Message()
        full_message += message

        return await self.send_msg(
            user_id=event.user.nickname, message=full_message, **kwargs
        )

    async def handle_event(self, event: Event) -> None:
        """处理收到的事件"""
        if isinstance(event, MessageEvent):
            _check_nickname(self, event)
        await handle_event(self, event)
