import sys
import asyncio
from typing_extensions import override
from typing import Any, Dict, List, Callable, Optional, Awaitable

from textual.color import Color
from nonebot.drivers import Driver
from nonechat import Frontend, ConsoleSetting

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter

from . import BOT_ID
from .bot import Bot
from .event import Event
from .config import Config
from .backend import AdapterConsoleBackend


class Adapter(BaseAdapter):
    @override
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.console_config = get_plugin_config(Config)
        self.bot = Bot(self, BOT_ID)

        self._task: Optional[asyncio.Task] = None
        self._frontend: Optional[Frontend[AdapterConsoleBackend]] = None
        self._stdout = sys.stdout
        self.clients: List[Callable[[Bot, str, Dict[str, Any]], Awaitable[Any]]] = []

        self.setup()

    @staticmethod
    @override
    def get_name() -> str:
        return "Console"

    def setup(self):
        if not self.console_config.console_headless_mode:
            self.driver.on_startup(self._start)
            self.driver.on_shutdown(self._shutdown)

    async def _start(self) -> None:
        self._frontend = Frontend(
            AdapterConsoleBackend,
            ConsoleSetting(
                title="Nonebot",
                sub_title="welcome to Console",
                toolbar_exit="❌",
                toolbar_back="⬅",
                icon_color=Color.parse("#EA5252"),
            ),
        )
        self._frontend.backend.set_adapter(self)
        self._task = asyncio.create_task(self._frontend.run_async())

    async def _shutdown(self) -> None:
        if self._frontend:
            self._frontend.exit()
        if self._task:
            await self._task

    def post_event(self, event: Event) -> None:
        asyncio.create_task(self.bot.handle_event(event))

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> None:
        await self._frontend.call(api, data)
