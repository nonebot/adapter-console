from textual.widgets import Header as BaseHeader
from textual.widgets._header import HeaderTitle
from textual.reactive import watch
from textual.widget import Widget


class Header(BaseHeader):
    DEFAULT_CSS = """
    Header HeaderIcon {
        color: #cc6633;
    }
    """
    # def on_mount(self):
    #     self.query_one(HeaderTitle).text = "Welcome to Console Treminal"
    ...

