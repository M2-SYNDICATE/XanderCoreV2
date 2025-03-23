from .core import Core
import threading
class DialogSession:
    def __init__(self, core: Core, timeout: float = 5.0):
        self.core = core
        self.timeout = timeout
        self.timer = None
        self.active = False
        self._lock = threading.Lock()

    def start(self):
        print("🎤 Диалог начат. Говори команду.")
        self.active = True
        self._reset_timer()
        self._run_loop()

    def _run_loop(self):
        while self.active:
            try:
                self.core.execute(1)  # запускает распознавание и выполнение

                # ❗️ Проверяем, не был ли диалог остановлен пока выполнялась команда
                if not self.active:
                    break

                self._reset_timer()
            except Exception as e:
                print(f"⚠️ Ошибка в pipeline: {e}")
                self.stop()
                break

    def _reset_timer(self):
        with self._lock:
            if self.timer:
                self.timer.cancel()

            self.timer = threading.Timer(self.timeout, self.stop)
            self.timer.start()

    def stop(self):
        with self._lock:
            if not self.active:
                return
            self.active = False
            if self.timer:
                self.timer.cancel()
            print("⏹️ Диалог завершён. Возврат в режим ожидания wake word.")

