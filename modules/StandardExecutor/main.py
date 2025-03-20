import json
import subprocess as sp
from core import runnable


@runnable
def StandartExecutor(data: str) -> None:
    with open("./data/commands.json") as f:
        config = json.load(f)
    print(data)
    list_of_cmds = config["commands"][data.split(" ")[0]]
    for l in list_of_cmds:
        if (arg := l.get(data.split(" ")[1], {})) :
            if "&" in arg:
                print("AZAZAZA")
                sp.run(f"./Scripts/{l[data.split(' ')[1]].replace('&', '')} &", shell=True)
            else:
                print("no azaaz")
                sp.run(f"{l[data.split(' ')[1]]} &> /dev/null &", shell=True)

