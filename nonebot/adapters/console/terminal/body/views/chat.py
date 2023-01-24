from time import time
from typing import List, Optional, Union
from rich.align import Align
from rich.text import Text, TextType
from rich.panel import Panel
from textual.containers import Horizontal
from textual.widget import Widget
from textual.reactive import Reactive
from textual.events import Key
from datetime import datetime
from pydantic import BaseModel
from rich.style import Style
from textual.widgets import (
    Input as BaseInput, 
    Button as BaseButton, 
    Tree as BaseTree,
    TreeNode
)

from ....message import Message, MessageSegment
from ....event import MessageEvent, User, Robot
from ....config import EMOJI


class SenderTreeNode(BaseModel):
    sender: Union[User, Robot]
    """发送者"""
    send_time: str
    """发送时间"""


class HouseBox(Widget):
    DEFAULT_CSS = """
    HouseBox {
        height: 3;
        color: $text;
        dock: top;
    }
    """
    room_name: Reactive[str] = Reactive("House")
    user_name: Reactive[str] = Reactive("Robot")

    def render(self):
        return Panel(
            Align.center( 
                Text(
                    self.room_name,
                    style="blue"
                ) + 
                Text(
                    " / ",
                    style="white"
                ) + 
                Text(
                    self.user_name,
                    style="green"
                )
            )
        )


# --------------------------------- 聊天框 ---------------------------------
class ChatBox(BaseTree):
    def __init__(self) -> None:
        super().__init__("ChatBox")
        self.show_root = False
        self.sender = None
    
    def compose(self):
        yield EmojiBox()
    
    def render_label(
        self, node: TreeNode[SenderTreeNode], 
        base_style: Style, 
        style: Style
    ) -> Text:
        if node.data:
            prefix = (
                Text(node.data.sender.icon) + 
                Text(
                    node.data.send_time,
                    style="green"
                ) + Text(
                    node.data.sender.nickname,
                    style="blue"
                )
            )
        else:
            prefix = node._label.copy()
            prefix.stylize(style)
        return prefix
    
    async def send_message(
        self,
        sender: Union[Robot, User],
        message: TextType
    ):
        """发送消息

        Args:
            sender (Union[Robot, User]): 发送者
            message (TextType): 消息内容
        """
        if message:
            if self.sender != sender:
                self.sender = sender
                self.node = self.root.add(
                    sender.nickname,
                    expand=True,
                    data=SenderTreeNode(
                        sender=sender,
                        send_time=datetime.now().strftime(' [%H:%M:%S] ')
                    )
                )
            self.node.add(
                message
            )
            if not self.node.is_expanded:
                self.node.expand()
        self.scroll_end(animate=False, speed=100)


# --------------------------------- Emoji表情框 ---------------------------------
class EmojiBox(Widget, can_focus=True):
    DEFAULT_CSS = """
    EmojiBox {
        height: 50%;
        max-height: 3;
        border: solid yellow;
        dock: bottom;
        layout: grid;
        grid-size: 10 2;
        grid-rows: 1fr;
        grid-columns: 1fr;
        grid-gutter: 1;
    }
    EmojiBox .emoji {
        width: 100%;
        height: 1;
        min-width: 1;
        border: none;
    }
    """
    
    class EmojiSelect(BaseButton):
        async def on_click(self):
            self.input.value += str(self.label)
        
        async def on_key(self, event: Key):
            if event.key == "enter" and not self.disabled:
                await self.on_click()

        def on_mount(self):
            self.input = self.app.query_one(InputBox).input

    def __init__(self) -> None:
        self.max_show_emoji = 20
        self._index = -1
        self.emoji_max_page = len(EMOJI) // self.max_show_emoji
        super().__init__(*(self.EmojiSelect(classes="emoji") for _ in range(self.max_show_emoji)))

    def on_mount(self):
        self.display = False
        self.switch_emoji()
    
    def switch_emoji(self, is_next: bool = True):
        if is_next and self._index <= self.emoji_max_page:
            self._index += 1
        elif self._index > 0:
            self._index -= 1
        self.refresh_emoji()

    def refresh_emoji(self):
        for but, emo in zip(
            self.children, 
            EMOJI[
                self.max_show_emoji * self._index:self.max_show_emoji * (self._index + 1)
            ]
        ):
            but.label = emo # type: ignore

    def set_display(self, display: Optional[bool] = None):
        """设置emoji框的显示

        Args:
            display (Optional[bool], optional): 显示或不显示并且当display为None表示取非. Defaults to None.
        """
        if display is None:
            self.display = not self.display
        else:
            self.display = display

    def on_key(self, event: Key):
        if event.key in ("left", "up"):
            self.switch_emoji(False)
        elif event.key in ("right", "down"):
            self.switch_emoji(True)


class EmojiButton(BaseButton):
    def on_mount(self):
        self.emoji_box = self.app.query_one(EmojiBox)

    async def on_click(self):
        self.emoji_box.set_display()

    async def on_key(self, event: Key):
        if event.key == "enter" and not self.disabled:
            await self.on_click()

# --------------------------------- 输入框 ---------------------------------
class InputBox(Widget):
    DEFAULT_CSS = """
    InputBox {
        dock: bottom;
        height: 3;
        border: solid white;
    }
    InputBox .input {
        width: 1fr;
        height: 100%;
        border: none;
        background: 0%;
        content-align: left middle;
    }
    InputBox .button {
        min-width: 8;
        height: 100%;
        border: none;
        border-left: solid gray;
        background: 0%;
    }
    InputBox #emoji {
        border: none;
        border-right: solid gray;
        min-width: 5;
    }
    """
    def __init__(self) -> None:
        super().__init__()
        self.input = Input(classes="input",placeholder="Send Message")
        self.submit = Button("SEND", classes="button")
        self.emoji = EmojiButton("😀", classes="button", id="emoji")

    def compose(self):
        yield Horizontal(
            self.emoji,
            self.input,
            self.submit,
        )


class Input(BaseInput):
    async def action_submit(self):
        """向聊天框发送消息"""
        if self.value:
            await self.chat_box.send_message(
                self.self_info,
                self.value
            )
            self.app.trigger_handle_event(  # type: ignore
                MessageEvent(
                    time=int(time()),
                    post_type="message",
                    self_id=int(self.self_info.user_id),
                    sender=self.self_info,
                    message=Message(self.value)
                )
            )
            self.value = ""

    def on_mount(self) -> None:
        super().on_mount()
        self.self_info: User = self.app.self_info   # type: ignore
        self.chat_box = self.app.query_one(ChatBox)


class Button(BaseButton):
    def on_mount(self):
        self.input = self.app.query_one(InputBox).input

    async def on_click(self):
        """按钮点击提交"""
        await self.input.action_submit()

    async def on_key(self, event: Key):
        """按下回车提交"""
        if event.key == "enter" and not self.disabled:
            await self.input.action_submit()


# --------------------------------- 聊天视图 ---------------------------------
class ChatView(Widget):
    """聊天界面"""
    DEFAULT_CSS = """
    ChatView {
        width: 1.2fr;
    }
    """
    def compose(self):
        yield from (
            HouseBox(),
            ChatBox(),
            InputBox()
        )
    
    def on_mount(self):
        self.chat_box = self.query_one(ChatBox)
    
    async def send_message(self, robot: Robot, message: Union[str, Message, MessageSegment]):
        """此send_message是由bot发送

        Args:
            robot (Robot): bot消息
            message (Union[str, Message, MessageSegment]): 消息内容
        """
        if isinstance(message, MessageSegment):
            message = Message(message).extract_plain_text()
        elif isinstance(message, Message):
            message = message.extract_plain_text()
        await self.chat_box.send_message(
            sender=robot,
            message=message
        )

