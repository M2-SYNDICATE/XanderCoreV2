from typing import Any
from typing import Callable


class Core:
    def __init__(
        self, flow: list[Callable[..., Any]], exception_handler: Callable[..., Any]
    ):
        self.flow = flow
        self.exc_handler = exception_handler

    def process(self):
        data = ""
        for func in self.flow:
            try:
                data = func(data)
            except Exception as e:
                self.handle_exception(e)

    def handle_exception(self, e):
        self.exc_handler(e)


def cmd_txt_input(e):
    return input("write cmd: ")
