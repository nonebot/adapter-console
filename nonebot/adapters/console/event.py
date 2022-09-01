from pydantic import BaseModel
from nonebot.typing import overrides

from nonebot.adapters import Event as BaseEvent

from .config import BaseInfo
from .message import Message


class Event(BaseEvent):
    __type__ = "Event"

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return self.__type__

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.__type__

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
        raise NotImplementedError


class MessageEvent(Event):
    __type__: str = "message"
    user_info: BaseInfo
    message: Message

    @overrides(Event)
    def get_user_id(self) -> str:
        if self.user_info:
            return self.user_info.user_id
        return ""

    @overrides(Event)
    def get_message(self) -> Message:
        return self.message

    @overrides(Event)
    def get_session_id(self) -> str:
        return self.user_info.user_id

    @overrides(Event)
    def is_tome(self) -> bool:
        return False

    @overrides(Event)
    def get_event_description(self) -> str:
        return f"{self.user_info.nickname} from {self.get_message()}"

    @overrides(Event)
    def get_plaintext(self) -> str:
        return self.get_message().extract_plain_text()
