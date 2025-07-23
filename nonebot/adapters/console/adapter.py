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
from .utils import log
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
            ),
        )
        self._frontend.backend.set_adapter(self)
        self._frontend.backend.current_bot.id = self.console_config.console_bot_id
        self._frontend.backend.current_bot.nickname = self.console_config.console_bot_name
        self._task = asyncio.create_task(self._frontend.run_async())

    async def _shutdown(self) -> None:
        if self._frontend:
            self._frontend.exit()
        if self._task:
            await self._task
        for bot in self.bots.copy().values():
            self.bot_disconnect(bot)

    def post_event(self, event: Event) -> None:
        if event.self_id not in self.bots:
            log("WARNING", f"Received event from unknown bot {event.self_id}.")
        bot: Bot = self.bots[event.self_id]  # type: ignore
        asyncio.create_task(bot.handle_event(event))

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any):
        if api == "send_msg":
            await self._frontend.send_message(**data, bot=bot.info)
        elif api == "bell":
            await self._frontend.toggle_bell()
        elif api == "get_user":
            return await self._frontend.backend.get_user(data["user_id"])
        elif api == "get_channel":
            return await self._frontend.backend.get_channel(data["channel_id"])
        elif api == "get_users":
            return await self._frontend.backend.list_users()
        elif api == "get_channels":
            return await self._frontend.backend.list_channels(data.get("list_users", False))
        elif api == "create_dm":
            user = await self._frontend.backend.get_user(data["user_id"])
            return await self._frontend.backend.create_dm(user)
        else:
            raise ApiNotAvailable(f"API {api} is not available in Console adapter")
