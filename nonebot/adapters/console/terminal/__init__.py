from .app import ConsoleView

console_view: ConsoleView = ConsoleView()


def print(*args, seq: str = " ") -> None:
    console_view.logger.append(seq.join(str(v) for v in args))


__all__ = [
    "ConsoleView",
    "console_view",
    "print",
    ]
