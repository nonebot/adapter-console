from typing import Optional

from nonebot.exception import AdapterException
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable


class ConsoleAdapterException(AdapterException):
    def __init__(self):
        super().__init__("Console")


class ApiNotAvailable(BaseApiNotAvailable, ConsoleAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""
