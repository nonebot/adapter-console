from .adapter import Adapter
from .terminal import print
from .terminal import console_view


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