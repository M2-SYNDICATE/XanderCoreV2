from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Union, List, Any
import functools
from functools import partial
import inspect

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

    def invoke(self, input_data: Any):
        result = input_data
        for step in self.steps:
            step_result = step.invoke(result)
            if inspect.isgenerator(step_result):
                for res in step_result:
                    yield res
                result = res  # Последнее значение из генератора
            else:
                result = step_result
                yield result

class Core:
    """Финальный пайплайн"""
    def __init__(self, pipeline: Runnable, exception_handler: Callable, verbose_except_output: bool = False):
        self.pipeline = pipeline
        self.exception_handler = exception_handler
        self.veo = verbose_except_output
        self.generator = None

    def start(self, input_data: Any):
        """Запускает пайплайн с заданными входными данными, готовит генератор"""
        self.generator = self.pipeline.invoke(input_data)

    def run_next(self):
        """Выполняет следующий шаг в пайплайне"""
        if self.generator is None:
            return None
        try:
            return next(self.generator)
        except StopIteration:
            self.generator = None
            return None
        except Exception as e:
            print("except in run")
            self.exception_handler(e, self.veo)
            self.generator = None
            return None

    def execute(self, input_data: Any) -> Any:
        """Выполняет весь пайплайн целиком"""
        self.start(input_data)
        result = None
        while True:
            try:
                result = next(self.generator)
            except StopIteration:
                break
            except Exception as e:
                print("except in execute")
                self.exception_handler(e, self.veo)
                break
        return result
