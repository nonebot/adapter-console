from datetime import datetime
from typing import List, Literal
from typing_extensions import override

from nonechat.info import User
from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message


class Event(BaseEvent):
    time: datetime
    self_id: str
    post_type: str
    user: User

    @override
    def get_type(self) -> str:
        return self.post_type

    @override
    def get_event_name(self) -> str:
        return self.post_type

    @override
    def get_event_description(self) -> str:
        return str(self.dict())

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no user_id!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no session_id!")

    @override
    def is_tome(self) -> bool:
        """获取事件是否与机器人有关的方法。"""
        return True


class MessageEvent(Event):
    post_type: Literal["message"] = "message"
    message: Message

    @override
    def get_user_id(self) -> str:
        return self.user.nickname

    @override
    def get_message(self) -> Message:
        return self.message

    @override
    def get_session_id(self) -> str:
        return self.user.nickname

    @override
    def is_tome(self) -> bool:
        return True

    @override
    def get_event_description(self) -> str:
        texts: List[str] = []
        msg_string: List[str] = []
        for seg in self.message:
            if seg.is_text():
                texts.append(str(seg))
            else:
                msg_string.extend(
                    (escape_tag("".join(texts)), f"<le>{escape_tag(str(seg))}</le>")
                )
                texts.clear()
        msg_string.append(escape_tag("".join(texts)))
        return f"Message from {self.user.nickname} {''.join(msg_string)!r}"


__all__ = ["Event", "MessageEvent"]
