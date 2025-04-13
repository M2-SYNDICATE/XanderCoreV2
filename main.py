from core import Core
from core import DialogSession
from modules.STT import STT
from core.Audio import AudioPlayer
from modules.WakeWord import WakeWord
from modules.StandardExecutor import StandartExecutor
from modules.TxtCommandProcessor import TxtCommandProcessor
from core import StandardTextExceptionHandler

from time import time



if __name__ == "__main__":
    processor = TxtCommandProcessor(config_path="./data/config.yaml")
    stt = STT("./data/STT_Model")
    wakeword = WakeWord("./data/WWModel/xander_up.rpw", 0.55)
    player = AudioPlayer("./data/Audio/Normal/")
    executor = StandartExecutor(player=player )

    # Создание pipeline
    core = Core(
        stt.recognize
        | processor.get_lemma
        | processor.fuzzy_search
        | executor.execute,
        exception_handler=StandardTextExceptionHandler,
        verbose_except_output=True
    )

    print("🟢 Система запущена. Говори wake word...")

    while True:
        try:
            if wakeword.process():
                print("🔔 Wake word активирован!")

                player.play_wake()
                session = DialogSession(core=core, timeout=8)
                executor.session = session
                print("SESSION_STARTED")
                session.start()
                print("session closed")

        except KeyboardInterrupt:
            print("👋 Завершение по Ctrl+C")
            break

