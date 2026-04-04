import asyncio
import sys
from collections.abc import Awaitable, Callable
from typing import Any
from typing_extensions import override

from nonebot.drivers import Driver
from nonechat import ConsoleSetting, Frontend
from textual.color import Color

from nonebot import get_plugin_config
from nonebot.adapters import Adapter as BaseAdapter

from .backend import AdapterConsoleBackend
from .bot import Bot
from .config import Config
from .event import Event
from .exception import ApiNotAvailable
from .utils import log


class Adapter(BaseAdapter):
    _frontend: Frontend[AdapterConsoleBackend]

    @override
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.console_config = get_plugin_config(Config)
        self._task: asyncio.Task | None = None

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
        match api:
            case "send_msg":
                return await self._frontend.send_message(**data, bot=bot.info)
            case "bell":
                return await self._frontend.toggle_bell()
            case "current_user":
                return self._frontend.backend.current_user
            case "current_channel":
                return self._frontend.backend.current_channel
            case "get_user":
                return await self._frontend.backend.get_user(data["user_id"])
            case "get_channel":
                return await self._frontend.backend.get_channel(data["channel_id"])
            case "list_users":
                return await self._frontend.backend.list_users()
            case "list_channels":
                return await self._frontend.backend.list_channels(data.get("list_users", False))
            case "create_dm":
                user = await self._frontend.backend.get_user(data["user_id"])
                return await self._frontend.backend.create_dm(user)
            case "get_msg":
                channel = await self._frontend.backend.get_channel(data["channel_id"])
                return await self._frontend.backend.get_chat(data["message_id"], channel)
            case "recall_msg":
                channel = await self._frontend.backend.get_channel(data["channel_id"])
                return await self._frontend.recall_message(data["message_id"], channel)
            case "edit_msg":
                channel = await self._frontend.backend.get_channel(data["channel_id"])
                return await self._frontend.edit_message(data["message_id"], data["content"], channel)
            case _:
                raise ApiNotAvailable(f"API {api} is not available in Console adapter")
