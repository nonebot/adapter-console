import asyncio
from typing import Any, Dict, List, Callable, Optional, Awaitable

from nonebot.drivers import Driver
from nonebot.typing import overrides

from nonebot.adapters import Adapter as BaseAdapter

from . import BOT_ID
from .bot import Bot
from .event import Event
from .config import Config
from .frontend import Frontend


class Adapter(BaseAdapter):
    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.console_config = Config.parse_obj(self.config)
        self.bot = Bot(self, BOT_ID)

        self._task: Optional[asyncio.Task] = None
        self.frontend = Frontend(self)
        self.clients: List[Callable[[Bot, str, Dict[str, Any]], Awaitable[Any]]] = []

        self.setup()

    @staticmethod
    @overrides(BaseAdapter)
    def get_name() -> str:
        return "Console"

    def setup(self):
        if not self.console_config.console_silent_mode:
            self.driver.on_startup(self._start)
            self.driver.on_shutdown(self._shutdown)

    async def _start(self) -> None:
        self._task = asyncio.create_task(self.frontend.run_async())
        self.bot_connect(self.bot)

    async def _shutdown(self) -> None:
        self.bot_disconnect(self.bot)
        if self._task:
            self.frontend.exit()
            await self._task

    def add_client(self, client: Callable[[Bot, str, Dict[str, Any]], Awaitable[Any]]):
        self.clients.append(client)

    def post_event(self, event: Event) -> None:
        asyncio.create_task(self.bot.handle_event(event))

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        await asyncio.gather(*(client(bot, api, data) for client in self.clients))
