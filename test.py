import inspect
from pathlib import Path

from rich.text import Text
from rich.markdown import Markdown
from rich.console import Group, Console

import nonebot.adapters

nonebot.adapters.__path__.append(  # type: ignore
    str((Path(__file__).parent / "nonebot" / "adapters").resolve())
)

from nonebot.log import logger

import nonebot
from nonebot import on_command
from nonebot.adapters.console import Adapter, MessageSegment

# logger.add("test.log", level=0, colorize=False, mode="w")

nonebot.init(driver="~none")

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins("echo")
# nonebot.load_plugin("nonebot_plugin_wordcloud")


content = (
    MessageSegment.markdown(
        inspect.cleandoc(
            """
            # title

            ## subtitle
            
            some text **bold** *italic* ~~strikethrough~~
            
            - list
            - list
            """
        )
    )
    + MessageSegment.emoji("tada")
    + MessageSegment.text("test text")
)

test = on_command("test")


@test.handle()
async def _():
    await test.send(content)


if __name__ == "__main__":
    nonebot.run()
