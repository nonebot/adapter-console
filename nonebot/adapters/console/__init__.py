from .adapter import Adapter
from .terminal import print, console_view


async def shutdown():
    await console_view.shutdown()


async def start():
    await console_view.run()


__all__ = [
    "Adapter",
    "shutdown",
    "start",
    "print",
]
