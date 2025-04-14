from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Union, List, Any, Optional
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

    def get_handlers(self) -> List["Runnable"]:
        return [self]

    @property
    def original(self) -> Any:
        """Возвращает исходный объект (функцию или экземпляр класса)"""
        if isinstance(self.func, partial):
            # Для методов класса возвращаем экземпляр
            return self.func.args[0]
        # Для обычных функций возвращаем саму функцию
        return self.func


class RunnableDescriptor(Runnable):
    """Дескриптор для привязки методов класса к Runnable"""

    def __get__(self, instance: Any, owner: Any) -> Runnable:
        if instance is None:
            return self
        # Сохраняем экземпляр класса в partial
        return Runnable(partial(self.func, instance))


def runnable(func: Callable) -> RunnableDescriptor:
    """Декоратор для создания обработчиков"""
    return RunnableDescriptor(func)


class Parallel(Runnable):
    """Параллельное выполнение"""

    def __init__(self, *steps: Runnable):
        self.steps = steps

    def invoke(self, input_data: Any) -> List[Any]:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(step.invoke, input_data) for step in self.steps]
            return [f.result() for f in futures]

    def get_handlers(self) -> List[Runnable]:
        handlers = []
        for step in self.steps:
            handlers.extend(step.get_handlers())
        return handlers


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
                result = res
            else:
                result = step_result
                yield result

    def get_handlers(self) -> List[Runnable]:
        handlers = []
        for step in self.steps:
            handlers.extend(step.get_handlers())
        return handlers


class Core:
    """Финальный пайплайн"""

    def __init__(
        self,
        pipeline: Runnable,
        exception_handler: Callable,
        verbose_except_output: bool = False,
    ):
        self.pipeline = pipeline
        self.exception_handler = exception_handler
        self.veo = verbose_except_output
        self.generator = None

    def start(self, input_data: Any):
        self.generator = self.pipeline.invoke(input_data)
        if isinstance(self.pipeline, Sequential):
            self.modules_to_terminate = list(self.pipeline.steps)

    def run_next(self):
        if self.generator is None:
            return None
        try:
            return next(self.generator)
        except StopIteration:
            self.generator = None
            return None
        except Exception as e:
            self.exception_handler(e, self.veo)
            self.generator = None
            return None

    def execute(self, input_data: Any) -> Any:
        self.start(input_data)
        result = None
        while True:
            try:
                result = next(self.generator)
            except StopIteration:
                break
            except Exception as e:
                self.exception_handler(e, self.veo)
                break
        return result

    def get_handlers(self) -> List[Runnable]:
        return self.pipeline.get_handlers()

    def get_original_objects(self) -> List[Any]:
        """Возвращает список исходных объектов (функций и экземпляров)"""
        return [handler.original for handler in self.get_handlers()]


# Пример использования
if __name__ == "__main__":
    # Создаем обработчики
    @runnable
    def text_cleaner(text: str) -> str:
        return text.strip()

    class TextProcessor:
        def __init__(self, prefix: str):
            self.prefix = prefix

        @runnable
        def add_prefix(self, text: str) -> str:
            return f"{self.prefix} {text}"

    # Создаем экземпляр класса
    text_processor = TextProcessor(prefix="[Обработано]")

    # Строим пайплайн
    pipeline = text_cleaner | text_processor.add_prefix

    # Инициализируем ядро
    core = Core(
        pipeline=pipeline,
        exception_handler=lambda e, _: print(f"Ошибка: {e}")
    )

    # Получаем исходные объекты
    original_objects = core.get_original_objects()

    # Выводим результат
    print("Исходные объекты в пайплайне:")
    for obj in original_objects:
        if callable(obj):
            print(f"Функция: {obj.__name__}")
        else:
            print(f"Экземпляр класса: {obj.__class__.__name__} {vars(obj)}")
