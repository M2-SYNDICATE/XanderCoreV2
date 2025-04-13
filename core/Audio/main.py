
import os
import pyglet
from random import choice

class AudioPlayer:
    def __init__(self, path_to_audio_dir):
        self.ok_path = path_to_audio_dir + "ok"
        self.err_path = path_to_audio_dir + "err"
        self.wake_path = path_to_audio_dir + "wake" 

    def play_ok(self, e=None):
        if e:
            source = pyglet.media.load(f"{self.ok_path}/{e}", streaming=False)
        else:
            source = pyglet.media.load(f"{self.ok_path}/{choice(os.listdir(self.ok_path))}", streaming=False)
        player = pyglet.media.Player()
        player.queue(source)
        player.play()

        # Обработчик события окончания воспроизведения
        def on_eos():
            pyglet.app.exit()  # Выход из цикла событий

        player.push_handlers(on_eos=on_eos)

        pyglet.app.run()
        return e
        
    def play_err(self):

        source = pyglet.media.load(f"{self.err_path}/{choice(os.listdir(self.err_path))}", streaming=False)
        player = pyglet.media.Player()
        player.queue(source)
        player.play()

        # Обработчик события окончания воспроизведения
        def on_eos():
            pyglet.app.exit()  # Выход из цикла событий

        player.push_handlers(on_eos=on_eos)

        pyglet.app.run()
    def play_wake(self):

        source = pyglet.media.load(f"{self.wake_path}/{choice(os.listdir(self.wake_path))}", streaming=False)
        player = pyglet.media.Player()
        player.queue(source)
        player.play()

        # Обработчик события окончания воспроизведения
        def on_eos():
            pyglet.app.exit()  # Выход из цикла событий

        player.push_handlers(on_eos=on_eos)

        pyglet.app.run()
    

