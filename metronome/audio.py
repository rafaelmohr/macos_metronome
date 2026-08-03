"""Click-sound loading and playback."""
import pygame

from metronome.resources import resource_path


class AudioEngine:
    def __init__(self, high_file: str = "high.wav", low_file: str = "low.wav"):
        pygame.mixer.init()
        self.high_sound = pygame.mixer.Sound(resource_path(high_file))
        self.low_sound = pygame.mixer.Sound(resource_path(low_file))

    def play_beat(self, is_downbeat: bool):
        (self.high_sound if is_downbeat else self.low_sound).play()
