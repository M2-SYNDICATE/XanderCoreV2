import json
import subprocess as sp


def StandartExecutor(data: str) -> None:
    with open("./data/commands.json") as f:
        config = json.load(f)
    list_of_cmds = config["commands"][data.split(" ")[0]]
    for l in list_of_cmds:
        if l.get(data.split(" ")[1], {}):
            sp.run(f"{l[data.split(' ')[1]]} &>/dev/null &", shell=True)


if __name__ == "__main__":
    StandartExecutor("открыть телеграмм")
