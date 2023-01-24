from asyncio import create_task, sleep
import sys
from typing import List, Optional, Union, cast
from rich.console import RenderableType
from rich.measure import measure_renderables
from rich.protocol import is_renderable
from rich.pretty import Pretty
from rich.segment import Segment
from rich.text import Text
from textual.geometry import Size
from rich.highlighter import ReprHighlighter
from textual.widget import Widget
from textual.widgets import TextLog
from textual.scroll_view import ScrollView
from textual.strip import Strip
from logging import StreamHandler, LogRecord
from nonebot import log
# from time import 
from .chat import Input


class LoggerView(TextLog, StreamHandler):
    DEFAULT_CSS = """
    LoggerView {
        width: 0.8fr;
        padding: 1;
    }
    """
    
    def __init__(self) -> None:
        super().__init__(
            highlight=True
        )
        self.console = self.app.console
        self.sys_stdout = sys.stdout
        sys.stdout = self
    
    def on_mount(self):
        super().on_mount()
        self.remove_default_logger()
        self.logger_id = self.set_logger_handler()

    def write(
        self,
        content: Union[RenderableType, object],
        width: Optional[int] = None,
        expand: bool = False,
        shrink: bool = True,
    ) -> None:
        """Write text or a rich renderable.

        Args:
            content (RenderableType): Rich renderable (or text).
            width (int): Width to render or None to use optimal width. Defaults to `None`.
            expand (bool): Enable expand to widget width, or False to use `width`. Defaults to `False`.
            shrink (bool): Enable shrinking of content to fit width. Defaults to `True`.
        """


        renderable: RenderableType
        if not is_renderable(content):
            renderable = Pretty(content)
        else:
            if isinstance(content, str):
                if self.markup:
                    renderable = Text.from_markup(content)
                else:
                    renderable = Text(content)
                if self.highlight:
                    renderable = self.highlighter(renderable)
            else:
                renderable = cast(RenderableType, content)

        render_options = self.console.options

        if isinstance(renderable, Text) and not self.wrap:
            render_options = render_options.update(overflow="ignore", no_wrap=True)

        render_width = measure_renderables(
            self.console, render_options, [renderable]
        ).maximum
        container_width = (
            self.scrollable_content_region.width if width is None else width
        )

        if expand and render_width < container_width:
            render_width = container_width
        if shrink and render_width > container_width:
            render_width = container_width

        segments = self.console.render(
            renderable, render_options.update_width(render_width)
        )
        lines = list(Segment.split_lines(segments))
        if not lines:
            return

        self.max_width = max(
            self.max_width,
            max(sum(segment.cell_length for segment in _line) for _line in lines),
        )
        strips = Strip.from_lines(lines, render_width)
        self.lines.extend(strips)

        if self.max_lines is not None and len(self.lines) > self.max_lines:
            self._start_line += len(self.lines) - self.max_lines
            self.refresh()
            self.lines = self.lines[-self.max_lines :]
        self.virtual_size = Size(self.max_width, len(self.lines))
        self.scroll_end(animate=False, speed=100)

    def restore_logger_handler(self) -> None:
        log.logger.remove(self.logger_id)
        sys.stdout = self.sys_stdout
        log.logger_id = self.set_logger_handler()

    def remove_default_logger(self) -> None:
        log.logger.remove(log.logger_id)
    
    def set_logger_handler(self) -> int:
        return log.logger.add(
            sys.stdout,
            level=0,
            diagnose=False,
            format=log.default_format,
            filter=log.default_filter
        )