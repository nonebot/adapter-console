from typing import Any
from asyncio import create_task

from nonebot.drivers import Driver
from nonebot.typing import overrides

from nonebot.adapters import Adapter as BaseAdapter

from .bot import Bot
from .event import Event, Robot
from .terminal import terminal


class Adapter(BaseAdapter):
    @overrides(BaseAdapter)
    def __init__(self, driver: Driver, **kwargs: Any) -> None:
        super().__init__(driver, **kwargs)
        self.bot = Bot(self, Robot(
            user_id="114514",
            nickname="bot"
        ))

        @terminal.add_handle_event
        async def _handle_event(event: Event) -> None:
            event.self_id = int(self.bot.bot_config.user_id)
            await self.bot.handle_event(event)

        self.setup()

    @staticmethod
    @overrides(BaseAdapter)
    def get_name() -> str:
        return "Console"

    @overrides(BaseAdapter)
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Any:
        if api == "send_message":
            await terminal.body.chat_view.send_message(bot.bot_config, **data)

    def setup(self):
        @self.driver.on_startup
        async def _start() -> None:
            create_task(terminal.run_async())
            # create_task(console_view.run())
            # self.bot_connect(self.bot)

        @self.driver.on_shutdown
        async def _stop() -> None:
            await terminal.shutdown()
            # await console_view.shutdown()
            # self.bot_disconnect(self.bot)
