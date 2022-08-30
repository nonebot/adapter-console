import os
from collections import defaultdict
from asyncio import wait, create_task, ensure_future
from typing import Dict, List, Union, Callable, Optional

from textual import events
from textual.app import App
from nonebot.log import logger
from rich.markdown import Markdown
from textual.widgets import ScrollView

from ..config import UserInfo
from .widgets.input import Input
from .widgets.right import Right
from .widgets.logger import Logger
from .widgets.header import HeadBar
from .widgets.client import ChatScreen
from ..event import Event, MessageEvent
from ..message import Message, MessageSegment


class ConsoleView(App):
    def __init__(self, user_info: Optional[UserInfo] = None) -> None:
        super().__init__()
        self.on: List[Callable] = []
        self.scroll_types: List[str] = []
        self.scroll_index: int = 0
        self.user_info: UserInfo = user_info or UserInfo(nickname="user", user_id="1")

    def trigger(self) -> None:
        ensure_future(wait(create_task(on()) for on in self.on))

    async def on_load(self) -> None:
        await self.bind("enter", "send_msg")
        await self.bind("up", "scroll_up")
        await self.bind("down", "scroll_down")

    async def action_swicth_scroll(self) -> None:
        """滚轮切换"""
        if self.scroll_index < len(self.scroll_types) - 1:
            self.scroll_index += 1
        else:
            self.scroll_index = 0

    async def _on(self, event: Event):
        if self.on:
            await wait([create_task(on(event)) for on in self.on])

    async def action_scroll_up(self) -> None:
        await self.scroll[self.scroll_types[self.scroll_index]].key_up()

    async def action_scroll_down(self) -> None:
        await self.scroll[self.scroll_types[self.scroll_index]].key_down()

    async def action_send_msg(self) -> None:
        if value := self.input.clear():
            event: MessageEvent = MessageEvent(
                user_info=self.user_info, message=Message(value)
            )
            await self.send_message(event, event.message)
            await self._on(event)

    async def send_message(
        self, event: MessageEvent, message: Union[str, Message, MessageSegment]
    ) -> None:
        """发送消息

        Args:
            event (MessageEvent): 消息事件
            message (Union[str, Message, MessageSegment]): 回复内容
        """
        try:
            if isinstance(message, MessageSegment):
                message = Message(message)
            elif isinstance(message, str):
                await self.client.send_message(event.user_info, message)

            if isinstance(message, Message) and message:
                widget = None
                text = None
                if md := message.get("markdown"):
                    widget = Markdown(**md[0].data["markdown"])
                else:
                    text = message.extract_plain_text()
                assert widget or text
                await self.client.send_message(event.user_info, widget or text or "")
        finally:
            logger.info("%s: %s" % (event.user_info.nickname, message))

    async def on_mount(self) -> None:
        self.width, self.height = os.get_terminal_size()
        self.head_bar: HeadBar = HeadBar()
        self.input: Input = Input()
        self.logger: Logger = Logger()
        self.client: ChatScreen = ChatScreen()
        self.scroll: Dict[str, ScrollView] = defaultdict(ScrollView)
        self.scroll_types = [self.client.name, self.logger.name]
        self.scroll[self.client.name] = self.client.scroll
        self.scroll[self.logger.name] = self.logger.scroll

        await self.view.dock(self.head_bar)
        await self.view.dock(
            self.scroll[self.logger.name],
            edge="right",
            name=self.logger.name,
            size=int(self.width * 0.39),
        )
        await self.view.dock(Right(), edge="right", size=2)
        await self.view.dock(
            self.scroll[self.client.name],
            name=self.client.name,
            size=self.height - self.input.height - 1,
        )
        await self.view.dock(self.input)

    async def on_key(self, event: events.Key) -> None:
        self.input.insert(event.key)
        if event.key == "escape":
            self.input.is_input = False
            self.head_bar.status = "No input"
        elif event.key == "i":
            self.input.is_input = True
            self.head_bar.status = "Input"
        elif event.key == "ctrl+i":
            await self.action_swicth_scroll()
            self.head_bar.status = f"{self.scroll_types[self.scroll_index]} scroll"

    async def run(self) -> None:
        await self.process_messages()
