from typing import List
from contextlib import redirect_stderr, redirect_stdout

from rich.text import Text
from textual.widget import Widget
from textual.events import Unmount
from textual.widgets import TextLog


class _FakeIO:
    def __init__(self, text_log: TextLog) -> None:
        self.text_log = text_log
        self._buffer: List[str] = []

    def write(self, string: str) -> None:
        self._buffer.append(string)

        # By default, `print` adds a "\n" suffix which results in a buffer
        # flush. You can choose a different suffix with the `end` parameter.
        # If you modify the `end` parameter to something other than "\n",
        # then `print` will no longer flush automatically. However, if a
        # string you are printing contains a "\n", that will trigger
        # a flush after that string has been buffered, regardless of the value
        # of `end`.
        if "\n" in string:
            self.flush()

    def flush(self) -> None:
        self._write_to_textlog()
        self._buffer.clear()

    def _write_to_textlog(self) -> None:
        self.text_log.write(Text("".join(self._buffer), end=""))


class LogPanel(Widget):
    DEFAULT_CSS = """
    LogPanel > TextLog {
        border-left: solid rgba(204, 204, 204, 0.7);
    }
    """

    def __init__(self) -> None:
        super().__init__()

        self.output = TextLog()
        self._fake_output = _FakeIO(self.output)

        self._redirect_stdout = redirect_stdout(self._fake_output)  # type: ignore
        self._redirect_stderr = redirect_stderr(self._fake_output)  # type: ignore

    def compose(self):
        yield self.output

    def on_mount(self):
        self._redirect_stdout.__enter__()
        self._redirect_stderr.__enter__()

    def on_unmount(self, event: Unmount):
        self._redirect_stderr.__exit__(None, None, None)
        self._redirect_stdout.__exit__(None, None, None)
