from dataclasses import field, dataclass
from typing import Any, List, Tuple, Callable

from rich.console import RenderableType

MAX_LOG_RECORDS = 500


@dataclass
class Storage:
    log_history: List[RenderableType] = field(default_factory=list)
    log_watchers: List[Callable[[Tuple[RenderableType, ...]], Any]] = field(
        default_factory=list
    )

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
