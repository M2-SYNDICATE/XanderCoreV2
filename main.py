from core import *
from core import cmd_txt_input  # NOTE: помкнять локацию cmd_txt_input
from core import StandardTextExceptionHandler
from modules.STT import STT
from modules.WakeWord import WakeWord
from modules.StandardExecutor import StandartExecutor
from modules.TxtCommandProcessor import TxtCommandProcessor


if __name__ == "__main__":
    processor = TxtCommandProcessor(config_path="./data/commands.json")
    stt = STT("./data/STT_Model")
    wakeword = WakeWord("./data/WWModel/xander.rpw")

    core = Core(
         stt.recognize
        | processor.get_lemma 
        | processor.fuzzy_search 
        | StandartExecutor,
        exception_handler=StandardTextExceptionHandler,
        verbose_except_output=True
    )
    while True:
        try:
            if wakeword.process(''):
                core.execute(1)
        except KeyboardInterrupt:
            exit(0)
