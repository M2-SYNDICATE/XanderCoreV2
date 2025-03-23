import json
import webbrowser
import urllib.parse
import subprocess as sp
from core import runnable
from typing import Any



class StandartExecutor:
    def __init__(self, player: Any | None = None):
        self.player = player

    @runnable
    def execute(self, data: str) -> None:
        if data and not "None" == data:
            if self.player:
                self.player.play_ok('')

            if "search" in data:
                webbrowser.open_new(
                    f"https://www.google.com/search?q={urllib.parse.quote(data.replace('search_internet', ''))}"
                )
            else:
                sp.run(f"{data.replace('None', '')} &> /dev/null &", shell=True)

