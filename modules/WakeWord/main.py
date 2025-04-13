import time
from core import runnable
from wakeword import AudioStream # Импортируем классы из вашей библиотеки

# Создаем экземпляр AudioStream



class WakeWord:
    def __init__(self, model_path, treashold=0.52):
        self.stream = AudioStream(
    buffer_size=1024,      # Размер буфера (можно настроить)
    desired_channels=1,    # Моно (1 канал)
    desired_sample_rate=16000  # Частота дискретизации 16000 Гц
)       
        self.stream.start()
        self.stream.load_model(model_path, normalize_audio=True, band_pass=False)
        self.treashold = treashold


# Запускаем аудиопоток
        print("Запуск WW...")
       
    def process(self):
        while True:
            chunk = self.stream.get_audio_chunk()
            
            if chunk:
                detections = self.stream.detect(chunk)
                
                for detection in detections: 
                    if detection is not None:
                        if detection.score >= self.treashold:
                            print(f"\n\nActive\nscore: {detection.score:.2f}\n\n")
                            return True
            time.sleep(0.01)
