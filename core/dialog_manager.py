import threading


class DialogSession:
    def __init__(self, core, timeout):
        self.core = core  # Основной объект для обработки команд
        self.timeout = timeout  # Время ожидания бездействия
        self.timer = None
        self.active = False
        self._lock = threading.Lock()

    def start(self):
        """Запускает диалоговую сессию."""
        print("🎤 Диалог начат. Говори команду.")
        self.active = True
        self._reset_timer()
        self._run_loop()

    def _run_loop(self):
        """Цикл обработки команд."""
        while self.active:
            try:
                if self.active:
                    # Выполнение команды через основной пайплайн
                    self.core.start("")
                    while self.core.generator is not None:
                        result = self.core.run_next()
                        #print(f"{result = }")
                        if result is None:
                            break  # Команда выполнена

                    # После выполнения команды сбрасываем таймер
                    self._reset_timer()
                else:
                    self.stop()
            except Exception as e:
                self.core.exception_handler(e, self.core.veo)
                self.stop()
                break

    def _reset_timer(self):
        """Сбрасывает таймер бездействия."""
        with self._lock:
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.timeout, self.stop)
            self.timer.start()

    def stop(self):
        """Останавливает сессию."""
        with self._lock:
            if not self.active:
                return
            self.active = False
            if self.timer:
                self.timer.cancel()
            steps = self.core.get_original_objects()
            for obj in steps:
                if not callable(obj):
                    try:
                        obj.terminate()
                        #print(f"terminated: {obj}")
                    except:
                        #print(obj)
                        pass#TODO: Переделать эту часть на hasattr
            self.core.generator = None
            print("⏹️ Диалог завершён. Ожидание wake word.")

    def manual_stop(self):
        """Ручная остановка сессии."""
        print("🛑 Сессия остановлена вручную.")
        self.stop()
