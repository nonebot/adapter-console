from copy import deepcopy
from datetime import datetime
from typing import Any, Literal
from typing_extensions import override

from pydantic import Field
from nonechat.model import DIRECT, User, Channel
from nonebot.utils import DataclassEncoder, escape_tag
from nonebot.compat import PYDANTIC_V2, ConfigDict, model_dump, model_validator, type_validate_python

from nonebot.adapters import Event as BaseEvent

from .message import Message


class Event(BaseEvent):
    time: datetime
    self_id: str
    post_type: str
    user: User
    channel: Channel

    if PYDANTIC_V2:  # pragma: pydantic-v2
        model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)
    else:  # pragma: pydantic-v1

        class Config(ConfigDict):
            extra = "ignore"  # type: ignore
            arbitrary_types_allowed = True  # type: ignore
            json_encoders = {Message: DataclassEncoder}  # noqa: RUF012

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

    original_message: Message = Field(init=False, default_factory=Message)

    @model_validator(mode="after")
    @classmethod
    def _check_message(cls, data) -> Any:
        if isinstance(data, dict):
            data["original_message"] = deepcopy(data["message"])
        else:
            data.original_message = deepcopy(data.message)
        return data

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
        if self.channel.id == DIRECT.id or self.channel.id.startswith("private:"):
            return f"Message from {self.user.nickname}({self.user.id}): {''.join(msg_string)!r}"
        return f"Message from {self.user.nickname}({self.user.id}) @ {self.channel.name}: {''.join(msg_string)!r}"

    def convert(self):
        if self.channel.id == DIRECT.id or self.channel.id.startswith("private:"):
            return type_validate_python(PrivateMessageEvent, model_dump(self))
        return type_validate_python(PublicMessageEvent, model_dump(self))


class PrivateMessageEvent(MessageEvent):
    @override
    def is_tome(self) -> bool:
        return True


class PublicMessageEvent(MessageEvent):
    pass


__all__ = ["Event", "MessageEvent", "PrivateMessageEvent", "PublicMessageEvent"]
