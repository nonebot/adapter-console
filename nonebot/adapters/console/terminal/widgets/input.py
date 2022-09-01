from typing import Union

from rich import box
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from textual.widget import Widget
from textual.reactive import Reactive


class Input(Widget):
    height: Reactive[int] = Reactive(3)
    value: str = ""
    is_input: Reactive[bool] = Reactive(True)
    cursor_position: int = 0

    def __init__(self, name: Union[str, None] = None, placeholder: str = "") -> None:
        super().__init__(name)
        self.placeholder: str = placeholder

    def _arrow(self) -> Text:
        return Text("> " if self.is_input else "  ", style=Style(color="blue"))

    def text(self) -> Text:
        if self.value:
            return (
                Text(self.value[: self.cursor_position], style=Style(color="white"))
                + Text("|", style=Style(color="blue"))
                + Text(self.value[self.cursor_position :], style=Style(color="white"))
            )
        return Text(self.placeholder, style=Style(color="#999999"))

    def render(self) -> Panel:
        return Panel(
            self._arrow() + self.text(),
            height=self.height,
            border_style="white",
            box=box.SQUARE,
        )

    def cursor_left(self):
        """光标左移"""
        if self.cursor_position > 0:
            self.cursor_position -= 1

    def cursor_right(self):
        """光标右移"""
        if self.cursor_position < len(self.value):
            self.cursor_position += 1

    def insert(self, v: str):
        if self.is_input:
            # 输入状态下
            if v == "escape":
                self.is_input = False
            elif v == "ctrl+h" and v:
                if self.cursor_position > 0:
                    self.value = f"{self.value[:self.cursor_position-1]}{self.value[self.cursor_position:]}"
                    self.cursor_left()
            elif v == "delete" and v:
                if self.cursor_position > 0:
                    self.value = f"{self.value[:self.cursor_position]}{self.value[self.cursor_position+1:]}"
            elif v == "left":
                self.cursor_left()
            elif v == "right":
                self.cursor_right()
            elif v == "home":
                self.cursor_position = 0
            elif v == "end":
                self.cursor_position = len(self.value)
            elif len(v) == 1:
                self.value = f"{self.value[:self.cursor_position]}{v}{self.value[self.cursor_position:]}"
                self.cursor_right()
            self.refresh()
        else:
            # 未输入状态下
            if v == "i":
                self.is_input = True

    def clear(self) -> str:
        """清空输入框同时返回输入框内容"""
        text: str = self.value
        self.value = ""
        self.cursor_position = 0
        self.refresh()
        return text
