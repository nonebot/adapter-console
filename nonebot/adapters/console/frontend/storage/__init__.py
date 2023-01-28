from dataclasses import field, dataclass
from typing import TYPE_CHECKING, Any, List, Tuple, Callable

from rich.console import RenderableType

from nonebot.adapters.console import User, MessageEvent

MAX_LOG_RECORDS = 500
MAX_MSG_RECORDS = 500


@dataclass
class Storage:
    current_user: User = field(default_factory=lambda: User(id="console_user"))

    log_history: List[RenderableType] = field(default_factory=list)
    log_watchers: List[Callable[[Tuple[RenderableType, ...]], Any]] = field(
        default_factory=list
    )

    chat_history: List[MessageEvent] = field(default_factory=list)
    chat_watchers: List[Callable[[Tuple[MessageEvent, ...]], Any]] = field(
        default_factory=list
    )

    def set_user(self, user: User):
        self.current_user = user

    def write_log(self, *logs: RenderableType) -> None:
        self.log_history.extend(logs)
        if len(self.log_history) > MAX_LOG_RECORDS:
            self.log_history = self.log_history[-MAX_LOG_RECORDS:]
        self.emit_log_watcher(*logs)

    def add_log_watcher(
        self, watcher: Callable[[Tuple[RenderableType, ...]], Any]
    ) -> None:
        self.log_watchers.append(watcher)

    def remove_log_watcher(
        self, watcher: Callable[[Tuple[RenderableType, ...]], Any]
    ) -> None:
        self.log_watchers.remove(watcher)

    def emit_log_watcher(self, *logs: RenderableType) -> None:
        for watcher in self.log_watchers:
            watcher(logs)

    def write_chat(self, *messages: "MessageEvent") -> None:
        self.chat_history.extend(messages)
        if len(self.chat_history) > MAX_MSG_RECORDS:
            self.chat_history = self.chat_history[-MAX_MSG_RECORDS:]
        self.emit_chat_watcher(*messages)

    def add_chat_watcher(
        self, watcher: Callable[[Tuple["MessageEvent", ...]], Any]
    ) -> None:
        self.chat_watchers.append(watcher)

    def remove_chat_watcher(
        self, watcher: Callable[[Tuple["MessageEvent", ...]], Any]
    ) -> None:
        self.chat_watchers.remove(watcher)

    def emit_chat_watcher(self, *messages: "MessageEvent") -> None:
        for watcher in self.chat_watchers:
            watcher(messages)
