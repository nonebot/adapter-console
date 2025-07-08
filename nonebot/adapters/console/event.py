from typing import Literal
from datetime import datetime
from typing_extensions import override

from nonechat.storage import DIRECT
from nonebot.utils import escape_tag
from nonechat.model import User, Channel
from nonebot.compat import model_dump, type_validate_python

from nonebot.adapters import Event as BaseEvent

from .message import Message


class Event(BaseEvent):
    time: datetime
    self_id: str
    post_type: str
    user: User
    channel: Channel

    @override
    def get_type(self) -> str:
        return self.post_type

    @override
    def get_event_name(self) -> str:
        return self.post_type

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(model_dump(self)))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        return self.user.id

    @override
    def get_session_id(self) -> str:
        if self.channel == DIRECT:
            return self.user.id
        return f"{self.channel.id}_{self.user.id}"

    @override
    def is_tome(self) -> bool:
        """获取事件是否与机器人有关的方法。"""
        return True


class MessageEvent(Event):
    post_type: Literal["message"] = "message"
    message: Message
    to_me: bool = False

    original_message: Message

    @override
    def get_message(self) -> Message:
        return self.message

    @override
    def is_tome(self) -> bool:
        return self.to_me

    @override
    def get_event_description(self) -> str:
        texts: list[str] = []
        msg_string: list[str] = []
        for seg in self.message:
            if seg.is_text():
                texts.append(str(seg))
            else:
                msg_string.extend((escape_tag("".join(texts)), f"<le>{escape_tag(str(seg))}</le>"))
                texts.clear()
        msg_string.append(escape_tag("".join(texts)))
        if self.channel == DIRECT:
            return f"Message from {self.user.nickname} {''.join(msg_string)!r}"
        return f"Message from {self.user.nickname}@{self.channel.name} {''.join(msg_string)!r}"

    def convert(self):
        if self.channel == DIRECT:
            return type_validate_python(PrivateMessageEvent, model_dump(self))
        return type_validate_python(PublicMessageEvent, model_dump(self))


class PrivateMessageEvent(MessageEvent):
    @override
    def is_tome(self) -> bool:
        return True


class PublicMessageEvent(MessageEvent):
    pass


__all__ = ["Event", "MessageEvent", "PrivateMessageEvent", "PublicMessageEvent"]
