"""Wires state, audio and UI widgets together and runs the event loop."""
import sys

import pygame
from pygame._sdl2 import video

from metronome import config
from metronome.audio import AudioEngine
from metronome.key_repeater import KeyRepeater
from metronome.resources import resource_path
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

# Upstream pygame accepts a high-DPI window flag but never applies it, so the
# whole UI comes out blurry on a Retina display. pygame-ce applies it properly.
# Fail loudly rather than silently rendering soft - that silence was the bug.
if not hasattr(pygame, "Window"):
    raise SystemExit(
        "Metronome needs pygame-ce, not upstream pygame.\n"
        "  pip uninstall pygame && pip install -r requirements.txt"
    )


class App:
    def __init__(self):
        pygame.init()

        # allow_high_dpi is what makes the window's backing framebuffer the
        # display's real physical pixel count instead of its point size.
        # Without it macOS hands SDL a 560x420 buffer and then magnifies it
        # onto a 1120x840 Retina area, softening every pixel we drew.
        self.window = pygame.Window(config.WINDOW_TITLE, size=(config.WIDTH, config.HEIGHT),
                                    allow_high_dpi=True)
        self._apply_icon()
        self.renderer = video.Renderer(self.window, vsync=True)
        self.window.show()

        self.clock = pygame.time.Clock()
        self.state = MetronomeState()
        self.audio = AudioEngine()
        self.key_repeater = KeyRepeater()

        self._sync_to_display()
        pygame.time.set_timer(TICK, self.state.interval_ms)

    # --- setup ---
    def _apply_icon(self):
        """Put our own artwork back on the window - and so on the Dock icon.

        pygame gives every window it creates its own icon (the snake), and on
        macOS SDL_SetWindowIcon feeds through to NSApplication's
        setApplicationIconImage:, which replaces the Dock icon that Launch
        Services already set from the bundle's icon.icns. That's why the right
        icon flashes up at launch and is then swapped out. Setting ours here
        wins because it happens after pygame has set its default.
        """
        try:
            icon = pygame.image.load(resource_path(config.ICON_FILE))
        except (pygame.error, OSError):
            return  # purely cosmetic - never stop the app launching over it
        self.window.set_icon(icon)

    def _framebuffer_size(self):
        """The window's true size in physical pixels (not points)."""
        viewport = self.renderer.get_viewport()
        return viewport.width, viewport.height

    def _sync_to_display(self):
        """(Re)build the canvas, fonts and widgets for the current pixel density.

        Everything is drawn at exactly the framebuffer's pixel count, so the
        finished frame is handed to the compositor 1:1 and never resampled -
        text is rasterized straight at its final size, which is as sharp as
        the display can render. self.scale converts the layout's point-based
        coordinates into those pixels (2 on Retina, 1 on a standard display).

        Called again whenever the pixel count changes, e.g. when the window is
        dragged between a Retina and a non-Retina monitor.
        """
        width, height = self._framebuffer_size()
        scale = width / config.WIDTH
        self.scale = int(scale) if float(scale).is_integer() else scale
        self.canvas = pygame.Surface((width, height))
        self.fonts = self._load_fonts()
        self._build_ui()

    def _load_fonts(self):
        def sized(points, bold=False):
            return pygame.font.SysFont(config.FONT_NAME, round(points * self.scale), bold=bold)

        return {
            "bpm": sized(config.FONT_SIZE_BPM, bold=True),
            "small": sized(config.FONT_SIZE_SMALL),
            "hint": sized(config.FONT_SIZE_HINT),
            "legend_title": sized(config.FONT_SIZE_LEGEND_TITLE, bold=True),
            "legend_body": sized(config.FONT_SIZE_LEGEND_BODY),
        }

    def _scaled_rect(self, x, y, w, h):
        s = self.scale
        return pygame.Rect(round(x * s), round(y * s), round(w * s), round(h * s))

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
        if self.canvas.get_size() != self._framebuffer_size():
            self._sync_to_display()

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
        texture.draw()  # canvas is exactly framebuffer-sized -> 1:1, no resampling
        self.renderer.present()
