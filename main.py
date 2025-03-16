from core import *
from core import cmd_txt_input  # NOTE: помкнять локацию cmd_txt_input
from core import StandardTextExceptionHandler
from modules.StandardExecutor import StandartExecutor
from modules.TxtCommandProcessor import TxtCommandProcessor


if __name__ == "__main__":
    processor = TxtCommandProcessor(config_path="./data/commands.json")

    core = Core(
        cmd_txt_input | processor.get_lemma | processor.fuzzy_search | StandartExecutor,
        exception_handler=StandardTextExceptionHandler,
    )
    while True:
        core.execute(1)
