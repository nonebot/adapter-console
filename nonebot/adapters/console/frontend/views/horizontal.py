from textual.widget import Widget


class HorizontalView(Widget):
    def __init__(self, chatroom, log_view):
        self.chatroom = chatroom
        self.log_view = log_view

    def compose(self):
        yield self.chatroom
        yield self.log_view
