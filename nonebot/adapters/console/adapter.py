import sys
import asyncio
from collections.abc import Awaitable
from typing_extensions import override
from typing import Any, Callable, Optional

from textual.color import Color
from nonebot.drivers import Driver
from nonechat import Frontend, ConsoleSetting

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .event import Event
from .config import Config
from .exception import ApiNotAvailable
from .backend import AdapterConsoleBackend


class Adapter(BaseAdapter):
    _frontend: Frontend[AdapterConsoleBackend]

    @override
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.console_config = get_plugin_config(Config)
        self._task: Optional[asyncio.Task] = None

        self._stdout = sys.stdout
        self.clients: list[Callable[[Bot, str, dict[str, Any]], Awaitable[Any]]] = []

        self.setup()

    @classmethod
    @override
    def get_name(cls) -> str:
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
                icon_color=Color.parse("#EA5252"),
                bot_name=self.console_config.console_bot_name,
            ),
        )
        self._frontend.backend.set_adapter(self)
        bot = Bot(self, self._frontend.backend.bot)
        self.bot_connect(bot)
        self._task = asyncio.create_task(self._frontend.run_async())

    async def _shutdown(self) -> None:
        if self._frontend:
            self._frontend.exit()
        if self._task:
            await self._task
        for bot in self.bots.copy().values():
            self.bot_disconnect(bot)

    def post_event(self, event: Event) -> None:
        bot: Bot = self.bots[event.self_id]  # type: ignore
        asyncio.create_task(bot.handle_event(event))

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any):
        if api == "send_msg":
            self._frontend.send_message(**data)
        elif api == "bell":
            await self._frontend.toggle_bell()
        elif api == "get_user":
            return next(user for user in self._frontend.storage.users if user.id == data["user_id"])
        elif api == "get_channel":
            return next(
                channel for channel in self._frontend.storage.channels if channel.id == data["channel_id"]
            )
        elif api == "get_users":
            return self._frontend.storage.users
        elif api == "get_channels":
            return self._frontend.storage.channels
        else:
            raise ApiNotAvailable(f"API {api} is not available in Console adapter")
