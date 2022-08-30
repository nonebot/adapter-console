import os
from typing import Any

from nonebot.drivers import Driver
from nonebot.typing import overrides

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .event import Event
from .config import BotConfig
from .terminal import console_view


class Adapter(BaseAdapter):
    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.bot = Bot(self, BotConfig(user_id="0"))

        @console_view.on.append
        async def _handle_event(event: Event) -> None:
            await self.bot.handle_event(event)

        self.setup()

    @staticmethod
    @overrides(BaseAdapter)
    def get_name() -> str:
        return "Console"

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        if api == "send_message":
            await console_view.client.send_message(bot.bot_config, **data)

    def setup(self):
        @self.driver.on_startup
        async def _start() -> None:
            self.bot_connect(self.bot)
            await console_view.run()
            # os.system("exit")
            # os.system("exit")

        @self.driver.on_shutdown
        async def _stop() -> None:
            await console_view.shutdown()
            self.bot_disconnect(self.bot)
