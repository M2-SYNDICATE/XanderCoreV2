import json
import argparse

import pymorphy3 as pm3

from fuzzywuzzy import fuzz, process
from core import runnable


class CommandProcessor:
    def __init__(self, config_path: None | str = None):
        self.nlp = pm3.MorphAnalyzer()
        self.searcher = process.extractOne
        if not config_path:
            config_path = "config.json"
        self.get_config(config_path)

        # print(self.HOME)
        # print(self.config)

    def get_config(self, path):
        with open(path, "r") as config_file:
            self.config = json.load(config_file)

    @runnable
    def get_lemma(self, text: str) -> str:
        return " ".join(
            [(self.nlp.parse(word)[0].normal_form) for word in text.split(" ")]
        )

    def fuzzy_search_arg(self, cmd, class_label):
        text = list(set(cmd.split(" ")).difference(self.commands_set))[0]
        return self.searcher(
            text,
            [str(*list(arg.keys())) for arg in self.config["commands"][class_label]],
            scorer=fuzz.ratio,
        )[0]

    @runnable
    def fuzzy_search(self, cmd: str) -> str:
        commands_set = set(self.config["commands"].keys())
        self.commands_set = commands_set
        text = list(commands_set.intersection(set(cmd.split(" "))))[0]
        command = self.searcher(text, commands_set, scorer=fuzz.ratio)[0]
        arg = self.fuzzy_search_arg(cmd, class_label=command)
        return " ".join([command, arg])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t")
    args = parser.parse_args()
    cmd = CommandProcessor("../../data/commands.json")
    print(cmd.fuzzy_search(cmd.get_lemma(args.t)))
