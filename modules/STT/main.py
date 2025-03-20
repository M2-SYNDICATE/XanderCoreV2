
import time
import wakeword # ваш Rust-модуль
import struct
import json
from vosk import Model, KaldiRecognizer

from core import runnable

class STT:
    def __init__(self, model_path, buffer_size=1024, desired_channels=1, desired_sample_rate=16000):

        # Параметры аудио
        self.MODEL_PATH = model_path
        self.BUFFER_SIZE = buffer_size
        self.DESIRED_CHANNELS = desired_channels      # моно
        self.DESIRED_SAMPLE_RATE = desired_sample_rate 


        # Создаём и запускаем аудиопоток
        self.audio = wakeword.AudioStream(self.BUFFER_SIZE, self.DESIRED_CHANNELS, self.DESIRED_SAMPLE_RATE)

        # Инициализируем модель Vosk
        self.model = Model(self.MODEL_PATH)  # убедитесь, что папка "model" содержит нужную модель
        self.recognizer = KaldiRecognizer(self.model, self.DESIRED_SAMPLE_RATE)
    @runnable
    def recognize(self, e): 
        self.audio.start()
        while True:
            chunk = self.audio.get_audio_chunk()
            if chunk:
                # Преобразуем float-сэмплы в int16 и упаковываем в байты
                data_bytes = b"".join(
                    struct.pack("<h", int(max(-1.0, min(1.0, sample)) * 32767))
                    for sample in chunk
                )
                # Передаём данные в распознаватель
                if self.recognizer.AcceptWaveform(data_bytes):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print("\nРезультат:", text)
                        return text
            time.sleep(0.01)  # небольшая задержка для снижения нагрузки

if __name__ == "__main__":
    stt = STT("../../data/STT_Model", buffer_size=480)
    print(stt.recognize(''))
