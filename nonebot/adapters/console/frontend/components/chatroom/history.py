from typing import TYPE_CHECKING, cast

from textual.widget import Widget

if TYPE_CHECKING:
    from ...app import Frontend
    from ...storage import Storage


class ChatHistory(Widget):
    DEFAULT_CSS = """
    ChatHistory {
        height: 100%;
        overflow-y: scroll;
        scrollbar-size-vertical: 1;
    }
    """

    @property
    def storage(self) -> "Storage":
        return cast("Frontend", self.app).storage

    def action_new_message(self):
        ...

    def action_clear_history(self):
        for msg in self.walk_children():
            cast(Widget, msg).remove()
