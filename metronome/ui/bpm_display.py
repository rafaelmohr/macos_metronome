"""The big BPM number. Doubles as a click target that enters keyboard
text-entry mode (typed digits build a buffer, Enter confirms, Esc cancels).
"""
import pygame

from metronome import config

CURSOR_BLINK_MS = 500


class BpmDisplay:
    def __init__(self, rect, font, scale=1):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.scale = scale
        self._cursor_visible = True
        self._cursor_timer_ms = 0.0

    def contains(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def update(self, dt_ms):
        self._cursor_timer_ms += dt_ms
        if self._cursor_timer_ms >= CURSOR_BLINK_MS:
            self._cursor_timer_ms = 0.0
            self._cursor_visible = not self._cursor_visible

    def draw(self, surface, state):
        editing = state.editing_bpm

        if editing:
            cursor = "|" if self._cursor_visible else " "
            display_text = state.bpm_entry_buffer + cursor
            color = config.Color.ACCENT
        else:
            display_text = str(state.tempo)
            color = config.Color.TEXT_PRIMARY

        text_surf = self.font.render(display_text, True, color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

        if editing:
            pygame.draw.rect(surface, config.Color.EDIT_BORDER, self.rect,
                              width=2 * self.scale, border_radius=18 * self.scale)
