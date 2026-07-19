"""
MediaController: Controls media playback via virtual keys.
"""
from pynput.keyboard import Key, Controller
import logging

logger = logging.getLogger("MediaController")

class MediaController:
    def __init__(self):
        self.keyboard = Controller()

    def play_pause(self):
        logger.info("Media: Play/Pause")
        self.keyboard.press(Key.media_play_pause)
        self.keyboard.release(Key.media_play_pause)

    def next_track(self):
        logger.info("Media: Next")
        self.keyboard.press(Key.media_next)
        self.keyboard.release(Key.media_next)

    def prev_track(self):
        logger.info("Media: Previous")
        self.keyboard.press(Key.media_previous)
        self.keyboard.release(Key.media_previous)

    def volume_up(self):
        self.keyboard.press(Key.media_volume_up)
        self.keyboard.release(Key.media_volume_up)

    def volume_down(self):
        self.keyboard.press(Key.media_volume_down)
        self.keyboard.release(Key.media_volume_down)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    media = MediaController()
    media.play_pause()
