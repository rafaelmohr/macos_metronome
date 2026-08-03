"""The row of beat lights showing where we are in the bar."""
import pygame

from metronome import config

MIN_LABEL_CELL_WIDTH = 18


class BeatIndicator:
    def __init__(self, rect, number_font, scale=1):
        self.rect = pygame.Rect(rect)
        self.number_font = number_font
        self.scale = scale

    def draw(self, surface, state):
        n = state.beats_per_bar
        gap = 6 * self.scale
        cell_width = (self.rect.width - gap * (n - 1)) / n

        for i in range(n):
            x = self.rect.x + i * (cell_width + gap)
            cell_rect = pygame.Rect(round(x), self.rect.y, round(cell_width), self.rect.height)
            is_downbeat = i == 0
            active = (i == state.beat) and not state.paused

            if active:
                color = (config.Color.BEAT_DOWNBEAT_ACTIVE if is_downbeat
                         else config.Color.BEAT_ACTIVE)
            else:
                color = config.Color.BEAT_INACTIVE

            radius = min(10 * self.scale, cell_rect.height // 2)
            pygame.draw.rect(surface, color, cell_rect, border_radius=radius)

            if cell_width >= MIN_LABEL_CELL_WIDTH * self.scale:
                num_color = config.Color.BACKGROUND if active else config.Color.TEXT_MUTED
                num_surf = self.number_font.render(str(i + 1), True, num_color)
                surface.blit(num_surf, num_surf.get_rect(center=cell_rect.center))
