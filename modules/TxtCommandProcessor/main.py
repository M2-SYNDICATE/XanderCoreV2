import yaml
import argparse

import pymorphy3 as pm3

from fuzzywuzzy import fuzz, process
from core import runnable
from time import time
from functools import lru_cache


class CommandProcessor:
    def __init__(self, config_path: None | str = None, threshold = 60):
        self.nlp = pm3.MorphAnalyzer()
        if not config_path:
            config_path = "config.json"
        self.get_config(config_path)
        self.last_command = None
        self.SIMILARITY_THRESHOLD = threshold
        self.fixed_parts = [(cmd, self.extract_fixed_part(cmd['template'])) for cmd in self.config['commands']]


        # print(self.HOME)
        # print(self.config)

    def get_config(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file) 
    
    @runnable
    def get_lemma(self, text: str) -> str:
        return " ".join(
            [(self.nlp.parse(word)[0].normal_form) for word in text.split(" ")]
        )

    def extract_fixed_part(self, template):
        """Извлекает фиксированную часть шаблона до первого плейсхолдера."""
        return template.split('{')[0].strip()
    @runnable
    def fuzzy_search(self, user_command):
        """Находит наилучшую команду по нечёткому соответствию."""
        # Создаём список фиксированных частей шаблонов и соответствующих команд
                # Ищем лучшее соответствие для команды пользователя
        best_match, score = process.extractOne(user_command, [fp[1] for fp in self.fixed_parts], scorer=fuzz.partial_ratio)
        if score >= self.SIMILARITY_THRESHOLD:
            print(score)
            # Возвращаем команду, соответствующую найденной фиксированной части
            command = [cmd for cmd, fp in self.fixed_parts if fp == best_match][0]
            arg = self.extract_arguments(user_command, command['template'], command.get('arguments', {}))
            #print("arg:", arg)
            output = f"{command['action']} {arg}"
            if command['action'] == "retry":
                return self.last_command
            else:
                self.last_command = output
                print(f"command: {output}")
                return output
        return None

    def extract_arguments(self, user_command, template, arguments):
        """Извлекает аргументы из команды пользователя."""
        fixed_part = self.extract_fixed_part(template)
        if '{' in template:
            # Извлекаем часть после фиксированной
            arg_part = user_command[len(fixed_part):].strip()
            # Получаем имена аргументов из шаблона
            arg_names = [arg.strip('{}') for arg in template.split('{')[1:]]
            if arguments:
                # Для аргументов с ограниченным списком
                for arg_name in arg_names:
                    if arg_name in arguments:
                        choices = arguments[arg_name]
                        best_arg, score = process.extractOne(arg_part, choices, scorer=fuzz.ratio)
                        if score >= self.SIMILARITY_THRESHOLD/2:
                            #print(f"{best_arg = }\n{score = }")
                            return best_arg.split("->")[1]
            else:
                # Для аргументов из текста
                return arg_part
        return ""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t")
    args = parser.parse_args()
    cmd = CommandProcessor("../../data/config.yaml")
    start = time()
    print(cmd.fuzzy_search(cmd.get_lemma(args.t)))
    print(time() - start)
