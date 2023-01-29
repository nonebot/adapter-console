from typing import Type, Union, Literal, Iterable, Optional, TypedDict

from rich.style import Style
from rich.emoji import EmojiVariant
from nonebot.typing import overrides
from rich.text import Text as RichText
from rich.emoji import Emoji as RichEmoji
from rich.markdown import Markdown as RichMarkdown
from rich.measure import Measurement, measure_renderables
from rich.console import Console, RenderResult, JustifyMethod, ConsoleOptions

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import truncate


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @overrides(BaseMessageSegment)
    def __add__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return Message(self) + (
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessageSegment)
    def __radd__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return (
            MessageSegment.text(other) if isinstance(other, str) else Message(other)
        ) + self

    @overrides(BaseMessageSegment)
    def __str__(self) -> str:
        params = ", ".join(
            [f"{k}={truncate(str(v))}" for k, v in self.data.items() if v is not None]
        )
        return f"[{self.type}{':' if params else ''}{params}]"

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == "text"

    @staticmethod
    def text(text: str) -> "Text":
        return Text("text", {"text": text})

    @staticmethod
    def emoji(name: str) -> "Emoji":
        return Emoji("emoji", {"name": name})

    @staticmethod
    def markup(
        markup: str,
        style: Union[str, Style] = "none",
        emoji: bool = True,
        emoji_variant: Optional[EmojiVariant] = None,
    ) -> "Markup":
        return Markup(
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
    ) -> "Markdown":
        return Markdown(
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

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        raise NotImplementedError

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        raise NotImplementedError


class TextData(TypedDict):
    text: str


class Text(MessageSegment):
    type: Literal["text"]
    data: TextData

    @property
    def rich(self) -> RichText:
        return RichText(self.data["text"], end="")

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class EmojiData(TypedDict):
    name: str


class Emoji(MessageSegment):
    type: Literal["emoji"]
    data: EmojiData

    @property
    def rich(self) -> RichEmoji:
        return RichEmoji(self.data["name"])

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class MarkupData(TypedDict):
    markup: str
    style: Union[str, Style]
    emoji: bool
    emoji_variant: Optional[EmojiVariant]


class Markup(MessageSegment):
    type: Literal["markup"]
    data: MarkupData

    @property
    def rich(self) -> RichText:
        return RichText.from_markup(
            self.data["markup"],
            style=self.data["style"],
            emoji=self.data["emoji"],
            emoji_variant=self.data["emoji_variant"],
        )

    def __str__(self) -> str:
        return str(self.rich)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class MarkdownData(TypedDict):
    markup: str
    code_theme: str
    justify: Optional[JustifyMethod]
    style: Union[str, Style]
    hyperlinks: bool
    inline_code_lexer: Optional[str]
    inline_code_theme: Optional[str]


class Markdown(MessageSegment):
    type: Literal["markdown"]
    data: MarkdownData

    @property
    def rich(self) -> RichMarkdown:
        return RichMarkdown(**self.data)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.rich

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, (self.rich,))


class Message(BaseMessage[MessageSegment]):
    """Console 消息"""

    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessage)
    def __radd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessage)
    def __iadd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super().__iadd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        yield MessageSegment.text(msg)

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from self

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return measure_renderables(console, options, self)
