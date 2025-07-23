from dataclasses import asdict
from collections.abc import Iterable
from typing_extensions import Self, override
from typing import TYPE_CHECKING, Union, Optional

from rich.style import Style
from rich.emoji import EmojiVariant
from rich.console import JustifyMethod
from nonechat import Text, Emoji, Markup, Markdown, ConsoleMessage

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import truncate


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> type["Message"]:
        return Message

    @override
    def __add__(self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]) -> "Message":
        return Message(self) + (MessageSegment.text(other) if isinstance(other, str) else other)

    @override
    def __radd__(self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]) -> "Message":
        return (MessageSegment.text(other) if isinstance(other, str) else Message(other)) + self

    @override
    def __str__(self) -> str:
        if self.type == "text":
            return self.data["text"]
        params = ", ".join([f"{k}={truncate(str(v))}" for k, v in self.data.items() if v is not None])
        return f"[{self.type}{':' if params else ''}{params}]"

    @override
    def is_text(self) -> bool:
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "MessageSegment":
        return MessageSegment("text", {"text": text})

    @staticmethod
    def emoji(name: str) -> "MessageSegment":
        return MessageSegment("emoji", {"name": name})

    @staticmethod
    def markup(
        markup: str,
        style: Union[str, Style] = "none",
        emoji: bool = True,
        emoji_variant: Optional[EmojiVariant] = None,
    ) -> "MessageSegment":
        return MessageSegment(
            "markup",
            {
                "markup": markup,
                "style": style,
                "emoji": emoji,
                "emoji_variant": emoji_variant,
            },
        )

    @staticmethod
    def markdown(
        markup: str,
        code_theme: str = "monokai",
        justify: Optional[JustifyMethod] = None,
        style: Union[str, Style] = "none",
        hyperlinks: bool = True,
        inline_code_lexer: Optional[str] = None,
        inline_code_theme: Optional[str] = None,
    ) -> "MessageSegment":
        return MessageSegment(
            "markdown",
            {
                "markup": markup,
                "code_theme": code_theme,
                "justify": justify,
                "style": style,
                "hyperlinks": hyperlinks,
                "inline_code_lexer": inline_code_lexer,
                "inline_code_theme": inline_code_theme,
            },
        )


class Message(BaseMessage[MessageSegment]):
    """Console 消息"""

    @classmethod
    @override
    def get_segment_class(cls) -> type[MessageSegment]:
        return MessageSegment

    @override
    def __add__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> Self:
        return super().__add__(MessageSegment.text(other) if isinstance(other, str) else other)

    @override
    def __radd__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> Self:
        return super().__radd__(MessageSegment.text(other) if isinstance(other, str) else other)

    @override
    def __iadd__(self, other: Union[str, MessageSegment, Iterable[MessageSegment]]) -> Self:
        return super().__iadd__(MessageSegment.text(other) if isinstance(other, str) else other)

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    def to_console_message(self) -> ConsoleMessage:
        """将 Message 转换为 ConsoleMessage"""
        elements = []
        for seg in self:
            if seg.type == "text":
                elements.append(Text(seg.data["text"]))
            elif seg.type == "emoji":
                elements.append(Emoji(seg.data["name"]))
            elif seg.type == "markdown":
                elements.append(Markdown(**seg.data))
            elif seg.type == "markup":
                elements.append(Markup(**seg.data))
        return ConsoleMessage(elements)

    @classmethod
    def from_console_message(cls, message: ConsoleMessage) -> "Message":
        """从 ConsoleMessage 创建 Message"""
        msg = cls()
        for elem in message:
            if isinstance(elem, Text):
                msg += MessageSegment.text(elem.text)
            elif isinstance(elem, Emoji):
                msg += MessageSegment.emoji(elem.name)
            else:
                if TYPE_CHECKING:
                    assert isinstance(elem, (Markdown, Markup))
                msg += MessageSegment(type=elem.__class__.__name__.lower(), data=asdict(elem))  # noqa
        return msg
