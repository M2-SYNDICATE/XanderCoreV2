import traceback
from rich import print as printr


def StandardTextExceptionHandler(e):
    tb_list = traceback.extract_tb(e.__traceback__)
    last_frame = tb_list[-1]
    line_number = last_frame.lineno
    path = last_frame.filename

    message = f":warning: [red bold][ ERR ][/] В модуле [red bold link=vscode://file//{path}:{line_number} ]{last_frame.name}[/](<- кликабельно) возникла ошибка, смотри на [red bold]{line_number}[/] строке!"

    printr(message)
    printr("\n", *traceback.format_tb(e.__traceback__), f"{e}\n")
