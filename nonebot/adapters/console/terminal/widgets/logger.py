from typing import List, Union
from logging import StreamHandler

from rich.tree import Tree
from textual.widget import Widget
from textual.widgets import ScrollView
from nonebot.log import logger, default_filter, default_format


class ConsoleHandler(StreamHandler):
    def __init__(self, messages: "Logger") -> None:
        super().__init__(None)
        self.messages: "Logger" = messages
        self.temp_logger: List[str] = []

    def emit(self, record) -> None:
        try:
            self.temp_logger.append(self.format(record))
            for msg in self.temp_logger.copy():
                self.messages.append(msg)
            self.temp_logger.clear()
        except LookupError:
            ...


class Logger(Widget):
    def __init__(self, name: Union[str, None] = None) -> None:
        name = name or "logger"
        super().__init__(name)
        self.root: Tree = Tree("", highlight=True, hide_root=True, expanded=True)
        self.handler: ConsoleHandler = ConsoleHandler(self)
        self.scroll: ScrollView = ScrollView(self, gutter=1)
        logger.remove()
        logger.add(
            self.handler,
            filter=default_filter,
            format=default_format,
        )

    def scroll_end(self, refresh: bool = True) -> None:
        self.scroll.target_y = (
            self.scroll.window.virtual_size.height - self.scroll.size.height
        )
        self.scroll.animate("y", self.scroll.target_y, duration=0)
        if refresh:
            self.scroll.window.refresh(layout=True)

    def append(self, msg: str) -> None:
        self.root.add(msg)
        self.refresh(layout=True)
        self.scroll_end()

    def render(self) -> Tree:
        return self.root
