"""Wires state, audio and UI widgets together and runs the event loop."""
import sys

import pygame
from pygame._sdl2 import video

from metronome import config, sdl_hints
from metronome.audio import AudioEngine
from metronome.key_repeater import KeyRepeater
from metronome.state import MetronomeState
from metronome.ui.beat_indicator import BeatIndicator
from metronome.ui.bpm_display import BpmDisplay
from metronome.ui.legend import Legend

TICK = pygame.USEREVENT + 1

# keyboard-only controls: key -> delta, driven through KeyRepeater so
# holding the key keeps changing the value (see key_repeater.py)
TEMPO_KEYS = {
    pygame.K_RIGHT: config.TEMPO_STEP_SMALL,
    pygame.K_LEFT: -config.TEMPO_STEP_SMALL,
    pygame.K_UP: config.TEMPO_STEP_LARGE,
    pygame.K_DOWN: -config.TEMPO_STEP_LARGE,
}
BEATS_KEYS = {
    pygame.K_m: 1,
    pygame.K_n: -1,
}
LEGEND_KEYS = (pygame.K_h, pygame.K_SLASH)


class App:
    def __init__(self):
        pygame.init()
        sdl_hints.set_render_scale_quality_linear()

        # A real (allow_highdpi) window + renderer, not display.set_mode():
        # on a Retina display this gets a window whose backing framebuffer
        # is the true physical pixel count, not just the point size - so
        # our content is never silently upscaled/blurred by the OS after
        # we've already rendered it. Content is still drawn onto a plain
        # Surface (self.canvas) exactly as before; each frame that Surface
        # is converted to a Texture and presented through the renderer,
        # which stretches it to fill the window using linear filtering.
        self.window = video.Window(config.WINDOW_TITLE, size=(config.WIDTH, config.HEIGHT),
                                    allow_highdpi=True)
        self.renderer = video.Renderer(self.window, vsync=True)
        self.window.show()

        self.scale = config.RENDER_SCALE
        # Drawing happens on this higher-resolution canvas, then each frame
        # gets smoothly downsampled at presentation time (see _draw). That
        # gives real supersampled anti-aliasing on top of the native window.
        self.canvas = pygame.Surface((config.WIDTH * self.scale, config.HEIGHT * self.scale))
        self.clock = pygame.time.Clock()

        self.fonts = self._load_fonts()
        self.state = MetronomeState()
        self.audio = AudioEngine()
        self.key_repeater = KeyRepeater()

        self._build_ui()
        pygame.time.set_timer(TICK, self.state.interval_ms)

    # --- setup ---
    def _load_fonts(self):
        s = self.scale
        return {
            "bpm": pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_BPM * s, bold=True),
            "small": pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_SMALL * s),
            "hint": pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_HINT * s),
            "legend_title": pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_LEGEND_TITLE * s, bold=True),
            "legend_body": pygame.font.SysFont(config.FONT_NAME, config.FONT_SIZE_LEGEND_BODY * s),
        }

    def _scaled_rect(self, x, y, w, h):
        s = self.scale
        return pygame.Rect(x * s, y * s, w * s, h * s)

    def _build_ui(self):
        f = self.fonts
        bpm_rect = self._scaled_rect(config.WIDTH // 2 - 170, 50, 340, 170)
        self.bpm_display = BpmDisplay(bpm_rect, f["bpm"], scale=self.scale)
        beat_rect = self._scaled_rect(40, 250, config.WIDTH - 80, 56)
        self.beat_indicator = BeatIndicator(beat_rect, f["small"], scale=self.scale)
        self.legend = Legend(self.canvas.get_rect(), f["legend_title"], f["legend_body"], scale=self.scale)

    # --- callbacks ---
    def _nudge_tempo(self, delta):
        self.state.adjust_tempo(delta)
        self._reset_timer()

    def _reset_timer(self):
        pygame.time.set_timer(TICK, self.state.interval_ms)

    # --- main loop ---
    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(config.FPS)
            running = self._handle_events()
            self._update(dt_ms)
            self._draw()
        pygame.quit()
        sys.exit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.WINDOWCLOSE):
                return False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self.key_repeater.release(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_down(event.pos)
            elif event.type == TICK and not self.state.paused:
                is_downbeat = self.state.advance_beat()
                self.audio.play_beat(is_downbeat)
        return True

    def _handle_mouse_down(self, pos):
        # mouse events are reported in window (point) coordinates; our
        # widgets' rects live in canvas space, so scale up to match.
        pos = (pos[0] * self.scale, pos[1] * self.scale)

        if self.legend.visible:
            self.legend.visible = False
            return

        if self.bpm_display.contains(pos):
            if self.state.editing_bpm:
                self.state.confirm_bpm_edit()
                self._reset_timer()
            else:
                self.state.start_bpm_edit()
            return

        if self.state.editing_bpm:
            self.state.confirm_bpm_edit()
            self._reset_timer()

    def _handle_keydown(self, event):
        if self.state.editing_bpm:
            self._handle_bpm_entry_key(event)
            return

        if event.key == pygame.K_SPACE:
            self.state.toggle_pause()
        elif event.key in TEMPO_KEYS:
            delta = TEMPO_KEYS[event.key]
            self.key_repeater.press(event.key, lambda d=delta: self._nudge_tempo(d))
        elif event.key in BEATS_KEYS:
            delta = BEATS_KEYS[event.key]
            self.key_repeater.press(event.key, lambda d=delta: self.state.adjust_beats_per_bar(d))
        elif event.key in LEGEND_KEYS:
            self.legend.toggle()
        elif pygame.K_0 <= event.key <= pygame.K_9:
            self.state.start_bpm_edit()
            self.state.append_bpm_digit(chr(event.key))

    def _handle_bpm_entry_key(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.state.confirm_bpm_edit()
        elif event.key == pygame.K_ESCAPE:
            self.state.cancel_bpm_edit()
        elif event.key == pygame.K_BACKSPACE:
            self.state.backspace_bpm_edit()
        elif pygame.K_0 <= event.key <= pygame.K_9:
            self.state.append_bpm_digit(chr(event.key))
        else:
            return
        self._reset_timer()

    def _update(self, dt_ms):
        self.key_repeater.update(dt_ms)
        self.bpm_display.update(dt_ms)

    def _draw(self):
        s = self.scale
        canvas = self.canvas
        canvas.fill(config.Color.BACKGROUND)

        self.bpm_display.draw(canvas, self.state)
        self.beat_indicator.draw(canvas, self.state)

        canvas_center_x = canvas.get_width() // 2
        if self.state.paused:
            paused_surf = self.fonts["small"].render("PAUSED", True, config.Color.PAUSE)
            canvas.blit(paused_surf, paused_surf.get_rect(midtop=(canvas_center_x, 322 * s)))

        hint_surf = self.fonts["hint"].render("Press H for controls", True, config.Color.TEXT_MUTED)
        canvas.blit(hint_surf, hint_surf.get_rect(midbottom=(canvas_center_x, canvas.get_height() - 14 * s)))

        self.legend.draw(canvas)

        texture = video.Texture.from_surface(self.renderer, canvas)
        self.renderer.clear()
        texture.draw()  # dstrect=None -> stretched to fill the whole window
        self.renderer.present()
