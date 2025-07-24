import re
from typing_extensions import override
from typing import TYPE_CHECKING, Any, Union

from nonebot.message import handle_event
from nonechat.model import User, Robot, Channel

from nonebot.adapters import Bot as BaseBot

from .utils import log
from .message import Message, MessageSegment
from .event import Event, MessageEvent, MessageResponse

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

        msg_id = await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=event.channel,
        )
        return MessageResponse(message_id=msg_id, channel_id=event.channel.id)

    async def send_private_message(self, user_id: str, message: Union[str, Message, MessageSegment]):
        channel = await self.create_dm(user_id)
        full_message = Message()
        full_message += message
        msg_id = await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=channel,
        )
        return MessageResponse(message_id=msg_id, channel_id=channel.id)

    async def send_message(self, channel_id: str, message: Union[str, Message, MessageSegment]):
        channel = await self.get_channel(channel_id)
        full_message = Message()
        full_message += message
        msg_id = await self.call_api(
            "send_msg",
            content=full_message.to_console_message(),
            channel=channel,
        )
        return MessageResponse(message_id=msg_id, channel_id=channel.id)

    async def get_message(self, message_id: str, channel_id: str) -> MessageEvent:
        """获取消息内容

        Args:
            message_id (str): 消息ID
            channel_id (str): 频道ID
        """
        event = await self.call_api("get_msg", message_id=message_id, channel_id=channel_id)
        return MessageEvent(
            time=event.time,
            self_id=event.self_id,
            user=event.user,
            post_type="message",
            message_id=event.message_id,
            message=Message.from_console_message(event.message),
            channel=event.channel,
        ).convert()

    async def recall_message(self, message_id: str, channel_id: str) -> None:
        """撤回消息

        Args:
            message_id (str): 消息ID
            channel_id (str): 频道ID
        """
        await self.call_api("recall_msg", message_id=message_id, channel_id=channel_id)

    async def edit_message(
        self, message_id: str, channel_id: str, content: Union[str, Message, MessageSegment]
    ) -> None:
        """编辑消息

        Args:
            message_id (str): 消息ID
            channel_id (str): 频道ID
            content (Union[str, Message, MessageSegment]): 消息内容
        """
        full_message = Message()
        full_message += content
        await self.call_api(
            "edit_msg", message_id=message_id, content=full_message.to_console_message(), channel_id=channel_id
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
