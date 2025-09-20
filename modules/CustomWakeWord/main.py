import numpy as np
import tensorflow as tf
import librosa
import pyaudio
import sys
from typing import Literal

class CustomWakeWord:

    def __init__(self, model_path, threshold=0.6, metric: Literal["distance","logical"] = "logical"):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.p = pyaudio.PyAudio()
        self.threshold = threshold
        self.metric = metric
        self.stream = self.p.open(rate=48000, channels=1, format=pyaudio.paFloat32, input=True)


    # Функция предобработки аудио
    def preprocess_audio(self, waveform, sr=8000, n_mfcc=40, max_time_steps=11, target_dB=-20):
        # Передискретизация, если необходимо
        if sr != 8000:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=8000)
            sr = 8000

        # Нормализация громкости
        rms = np.sqrt(np.mean(waveform**2))
        if rms > 0:
            scalar = (10 ** (target_dB / 20)) / rms
            waveform = waveform * scalar

        # Вычисление MFCC с параметрами, соответствующими обучению
        mfcc = librosa.feature.mfcc(y=waveform, sr=sr, n_mfcc=n_mfcc)
        mfcc = mfcc.T  # [time_steps, n_mfcc]

        # Дополнение или обрезка до max_time_steps
        if mfcc.shape[0] < max_time_steps:
            pad_width = max_time_steps - mfcc.shape[0]
            mfcc = np.pad(mfcc, ((0, pad_width), (0, 0)), mode='constant')
        else:
            mfcc = mfcc[:max_time_steps, :]

        # Транспонирование и добавление размерности канала
        mfcc = mfcc.T  # [n_mfcc, max_time_steps]
        mfcc = mfcc[..., np.newaxis]  # [n_mfcc, max_time_steps, 1]

        return mfcc.astype(np.float32)

    # Загрузка модели TFLite


    # Обработка входного файла

    # Обратный вызов для микрофона
    def process(self):
        waveform = np.frombuffer(self.stream.read(48000, exception_on_overflow=False), dtype=np.float32)
        #waveform = indata[:, 0]  # Моно
        mfcc = self.preprocess_audio(waveform, sr=48000)
        self.interpreter.set_tensor(self.input_details[0]['index'], np.array([mfcc]))
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        print(output)
        match self.metric:
            case "distance":
                output = (abs(output) < 1-self.threshold)
            case "logical":
                output = (output >= self.threshold).astype(int)
            case _:
                raise ValueError("invalid metric for model activation")

        if output >= self.threshold:
            print("Обнаружено ключевое слово!" + str(output), sep="\t")
            #stream.close()
            return True
        #stream.close()
        return False
        #input("press enter for continue...")
