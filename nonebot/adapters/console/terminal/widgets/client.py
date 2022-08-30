from asyncio import sleep
from datetime import datetime
from typing import Union, Optional

from rich.text import Text
from rich.tree import Tree
from rich.panel import Panel
from rich.style import Style
from nonebot.log import logger
from textual.widget import Widget
from rich.markdown import Markdown
from textual.geometry import Spacing
from textual.widgets import ScrollView

from ...message import Message
from ...config import BaseInfo, BotConfig


class ChatScreen(Widget):
    def __init__(self, name: Union[str, None] = None) -> None:
        super().__init__(name)
        self.name = "client"
        self.root = Tree(
            "🌲 [b green]Rich Tree", highlight=False, hide_root=True, expanded=True
        )
        self.node: Optional[Tree] = None
        self.sender: Optional[BaseInfo] = None
        self.padding = Spacing(0, 1, 0, 1)
        self.scroll: ScrollView = ScrollView(self, gutter=1)

    async def send_message(
        self, sender: BaseInfo, message: Union[str, Widget, Markdown]
    ) -> None:
        await sleep(0)
        if self.sender != sender:
            self.sender = sender
            logger.info(str(sender))
            self.node = self.root.add(
                Text(f"[{datetime.now().strftime('%H:%M:%S')}] ", style="#999999")
                + Text(f"{sender.nickname}", style=f"bold {sender.color}"),
                guide_style=Style(color="#1976d2"),
            )
        if self.node:
            self.node.add(message)
            self.refresh(layout=True)
            await self.scroll_end()

    async def scroll_end(self, refresh: bool = True) -> None:
        try:
            self.scroll.target_y = (
                self.scroll.window.virtual_size.height - self.scroll.size.height
            )
            self.scroll.animate("y", self.scroll.target_y, duration=0)
            if refresh:
                self.scroll.window.refresh(layout=True)
        except LookupError as err:
            ...

    def render(self):
        return self.root
