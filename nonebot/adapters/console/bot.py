import re
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Union

from nonebot.message import handle_event
from nonechat.model import User, Robot, Channel

from nonebot.adapters import Bot as BaseBot

from .utils import log
from .event import Event, MessageEvent
from .message import Message, MessageSegment

if TYPE_CHECKING:
    from .adapter import Adapter


def _check_at_me(bot: "Bot", event: MessageEvent):

    message = event.get_message()

    # ensure message is not empty
    if not message:
        message.append(MessageSegment.text(""))

    if message[0].type == "text":
        if message[0].data["text"].startswith(f"@{bot.self_id}"):
            event.to_me = True
            message[0].data["text"] = message[0].data["text"][len(f"@{bot.self_id}") :].lstrip("\xa0").lstrip()
        elif message[0].data["text"].startswith(f"@{bot.info.nickname}"):
            event.to_me = True
            message[0].data["text"] = message[0].data["text"][len(f"@{bot.info.nickname}") :].lstrip("\xa0").lstrip()
        if not message[0].data["text"]:
            del message[0]

    if not message:
        message.append(MessageSegment.text(""))


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
        event.to_me = True
        first_msg_seg.data["text"] = first_text[m.end() :]


class Bot(BaseBot):
    adapter: "Adapter"

    if TYPE_CHECKING:

        async def bell(self) -> None: ...

    def __init__(self, adapter: "Adapter", info: Robot):
        super().__init__(adapter, info.id)
        self.info = info

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs: Any,
    ) -> Any:
        full_message = Message()
        full_message += message

        return await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=event.channel,
        )

    async def send_private_message(self, user_id: str, message: Union[str, Message, MessageSegment]):
        channel = await self.create_dm(user_id)
        full_message = Message()
        full_message += message
        return await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=channel,
        )

    async def send_group_message(self, channel_id: str, message: Union[str, Message, MessageSegment]):
        channel = await self.get_channel(channel_id)
        full_message = Message()
        full_message += message
        return await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=channel,
        )

    async def get_user(self, user_id: str) -> User:
        """获取用户信息"""
        return await self.call_api("get_user", user_id=user_id)

    async def get_channel(self, channel_id: str) -> Channel:
        """获取频道信息"""
        return await self.call_api("get_channel", channel_id=channel_id)

    async def list_users(self) -> list[User]:
        """获取所有用户信息"""
        return await self.call_api("list_users")

    async def list_channels(self, list_users: bool = False) -> list[Channel]:
        """获取所有频道信息

        Args:
            list_users (bool): 是否获取私聊用户列表，默认为 False
        """
        return await self.call_api("list_channels", list_users=list_users)

    async def create_dm(self, user_id: str) -> Channel:
        """创建私聊频道

        Args:
            user_id (str): 用户ID
        """
        return await self.call_api("create_dm", user_id=user_id)

    async def handle_event(self, event: Event) -> None:
        """处理收到的事件"""
        if isinstance(event, MessageEvent):
            _check_at_me(self, event)
            _check_nickname(self, event)
            if not self.adapter.console_config.console_strict_tome:
                event.to_me = True
        await handle_event(self, event)
