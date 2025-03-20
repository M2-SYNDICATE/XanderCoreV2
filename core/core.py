from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Union, List, Any
import functools
from functools import partial


class Runnable:
    """Базовый класс для элементов пайплайна"""

    def __init__(self, func: Callable):
        self.func = func

    def __or__(self, other: Union["Runnable", "Parallel"]) -> "Sequential":
        return Sequential(self, other)

    def __ror__(self, other: Callable) -> "Sequential":
        return Sequential(Runnable(other), self)

    def invoke(self, input_data: Any) -> Any:
        return self.func(input_data)

    def handle_exception(self, exc: Exception, input_data: Any) -> Any:
        raise exc


class RunnableDescriptor(Runnable):
    """Дескриптор для привязки методов класса к Runnable"""

    def __get__(self, instance: Any, owner: Any) -> Runnable:
        if instance is None:
            return self
        return Runnable(partial(self.func, instance))


def runnable(func: Callable) -> RunnableDescriptor:
    """Декоратор, оборачивающий функцию в Runnable с поддержкой методов класса"""
    return RunnableDescriptor(func)


class Parallel(Runnable):
    """Параллельное выполнение"""

    def __init__(self, *steps: Runnable):
        self.steps = steps

    def invoke(self, input_data: Any) -> List[Any]:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(step.invoke, input_data) for step in self.steps]
            return [f.result() for f in futures]


class Sequential(Runnable):
    """Последовательное выполнение"""

    def __init__(self, *steps: Runnable):
        self.steps = steps

    def invoke(self, input_data: Any) -> Any:
        result = input_data
        for step in self.steps:
            result = step.invoke(result)
        return result


class Core:
    """Финальный пайплайн"""

    def __init__(self, pipeline: Runnable, exception_handler: Callable, verbose_except_output: bool=False):
        self.pipeline = pipeline
        self.exception_handler = exception_handler
        self.veo = verbose_except_output

    def execute(self, input_data: Any) -> Any:
        def process(step: Runnable, data: Any) -> Any:
            if isinstance(step, Parallel):
                with ThreadPoolExecutor() as executor:
                    futures = [executor.submit(process, s, data) for s in step.steps]
                    return [f.result() for f in futures]
            elif isinstance(step, Sequential):
                result = data
                for s in step.steps:
                    result = process(s, result)
                return result
            else:
                try:
                    return step.invoke(data)
                except Exception as e:
                    self.exception_handler(e, self.veo)

        return process(self.pipeline, input_data)


@runnable
def cmd_txt_input(data):
    return input("write cmd: ")
