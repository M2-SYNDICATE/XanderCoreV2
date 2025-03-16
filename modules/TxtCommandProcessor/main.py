import json
import argparse

import pymorphy3 as pm3

from fuzzywuzzy import fuzz, process


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

    def get_lemma(self, text: str) -> str:
        return " ".join(
            [(self.nlp.parse(word)[0].normal_form) for word in text.split(" ")]
        )

    def fuzzy_search(self, cmd: str, class_label: None | str = None) -> str:
        commands_set = set(self.config["commands"].keys())

        if class_label:
            text = list(set(cmd.split(" ")).difference(commands_set))[0]
            return self.searcher(
                text,
                [
                    str(*list(arg.keys()))
                    for arg in self.config["commands"][class_label]
                ],
                scorer=fuzz.ratio,
            )[0]
        else:
            text = list(commands_set.intersection(set(cmd.split(" "))))[0]
            command = self.searcher(text, commands_set, scorer=fuzz.ratio)[0]
            arg = self.fuzzy_search(cmd, class_label=command)
            return " ".join([command, arg])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t")
    args = parser.parse_args()
    cmd = CommandProcessor("../../data/commands.json")
    print(cmd.fuzzy_search(cmd.get_lemma(args.t)))
