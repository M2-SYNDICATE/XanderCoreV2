import json
import webbrowser
import urllib.parse
import subprocess as sp
from core import runnable
from typing import Any



class StandartExecutor:
    def __init__(self, player: Any | None = None, session: Any | None = None):
        self.player = player
        self.session = session

    @runnable
    def execute(self, data: str) -> None:
        if data and not "None" == data:
            if self.player and "$" not in data:
                self.player.play_ok()

            if "search" in data:
                webbrowser.open_new(
                    f"https://www.google.com/search?q={urllib.parse.quote(data.replace('search_internet', ''))}"
                )
            elif "$" in data:
                if "stop" in data:
                    if self.session:
                        if self.player:
                            self.player.play_ok("adjutant_ru_11.wav")
                        self.session.manual_stop()
                    else:
                        print("Остановка не возможна отключены системные прерывания")
                else:
                    if self.player:
                        self.player.play_ok()
                    try:
                        sp.run(f"./Scripts/{data.split()[0].replace('$', '')} {' '.join(data.split()[1:])} &> /dev/null &",shell=True)
                    except Exception as e:
                        print(e)
            else:
                sp.run(f"{data.replace('None', '')} &> /dev/null &", shell=True)

