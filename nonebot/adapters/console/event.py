from typing import Literal
from pydantic import BaseModel
from nonebot.typing import overrides

from nonebot.adapters import Event as BaseEvent

from .message import Message


class BaseIcon(BaseModel):
    icon: str


class BaseInfo(BaseModel):
    user_id: str
    nickname: str


class User(BaseInfo, BaseIcon):
    """用户"""
    icon: str = "👤"
    is_me: bool = False
    group_id: int


class Robot(BaseIcon, BaseInfo):
    """机器人"""
    icon: str = "🤖"


class Event(BaseEvent):
    time: int
    self_id: int
    post_type: str

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
    sender: BaseInfo
    message: Message

    @overrides(Event)
    def get_user_id(self) -> str:
        if self.sender:
            return self.sender.user_id
        return ""

    @overrides(Event)
    def get_message(self) -> Message:
        print("get_msg", self.message, sep="")
        return self.message

    @overrides(Event)
    def get_session_id(self) -> str:
        return self.sender.user_id

    @overrides(Event)
    def is_tome(self) -> bool:
        return True

    @overrides(Event)
    def get_event_description(self) -> str:
        return f"{self.sender.nickname} from {self.get_message()}"

    @overrides(Event)
    def get_plaintext(self) -> str:
        return self.get_message().extract_plain_text()
