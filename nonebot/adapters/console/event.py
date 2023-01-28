from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel
from nonebot.typing import overrides
from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message


class User(BaseModel, frozen=True):
    """用户"""

    id: str
    avatar: str = "👤"
    nickname: str = "User"


class Robot(User, frozen=True):
    """机器人"""

    avatar: str = "🤖"
    nickname: str = "Bot"


class Event(BaseEvent):
    time: datetime
    self_id: str
    post_type: str
    user: User

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.post_type

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return str(self.dict())

    @overrides(BaseEvent)
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no user_id!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no session_id!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        """获取事件是否与机器人有关的方法。"""
        return True


class MessageEvent(Event):
    post_type: Literal["message"] = "message"
    message: Message

    @overrides(Event)
    def get_user_id(self) -> str:
        return self.user.nickname

    @overrides(Event)
    def get_message(self) -> Message:
        return self.message

    @overrides(Event)
    def get_session_id(self) -> str:
        return self.user.nickname

    @overrides(Event)
    def is_tome(self) -> bool:
        return True

    @overrides(Event)
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


__all__ = ["User", "Robot", "Event", "MessageEvent"]
