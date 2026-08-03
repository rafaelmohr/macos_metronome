"""Central place for constants: sizing, limits, timing, theme colors.

Keeping every tunable value here means the rest of the codebase never
hardcodes a number that a designer/future-me would want to tweak.
"""

# --- window ---
WIDTH, HEIGHT = 560, 420          # actual on-screen window size, in points
FPS = 60
WINDOW_TITLE = "Metronome"

# Everything is drawn onto an internal canvas RENDER_SCALE times larger than
# the window, then downsampled with high-quality filtering into the window
# each frame. This gives genuine supersampled anti-aliasing (crisp text,
# smooth rounded corners) on any display, independent of whatever HiDPI
# support the OS/SDL/windowing setup does or doesn't provide.
RENDER_SCALE = 4

# --- musical limits ---
START_TEMPO = 120
MIN_TEMPO = 20
MAX_TEMPO = 300

START_BEATS_PER_BAR = 4
MIN_BEATS_PER_BAR = 1
MAX_BEATS_PER_BAR = 32

TEMPO_STEP_SMALL = 1
TEMPO_STEP_LARGE = 5

# --- held-key auto-repeat behaviour (arrow keys / N / M) ---
KEY_REPEAT_INITIAL_DELAY_MS = 400   # hold-still time before repeating starts
KEY_REPEAT_INTERVAL_MS = 110        # repeat rate right after the delay
KEY_REPEAT_FAST_AFTER_MS = 1500     # how long to hold before speeding up
KEY_REPEAT_FAST_INTERVAL_MS = 40    # repeat rate once "fast" kicks in

# --- BPM keyboard text-entry ---
BPM_ENTRY_MAX_DIGITS = 3

# --- theme: dark, modern, flat ---
class Color:
    BACKGROUND = (16, 17, 21)
    PANEL = (26, 27, 34)
    PANEL_BORDER = (42, 44, 54)
    TEXT_PRIMARY = (237, 237, 242)
    TEXT_SECONDARY = (144, 146, 163)
    TEXT_MUTED = (96, 98, 114)

    ACCENT = (92, 170, 255)

    DOWNBEAT = (255, 122, 89)

    BEAT_ACTIVE = ACCENT
    BEAT_DOWNBEAT_ACTIVE = DOWNBEAT
    BEAT_INACTIVE = (46, 48, 58)

    PAUSE = (255, 196, 80)
    EDIT_BORDER = ACCENT
    OVERLAY_SCRIM = (0, 0, 0, 170)

# --- fonts (sizes only; actual Font objects are created after pygame.init) ---
FONT_NAME = "Arial"
FONT_SIZE_BPM = 116
FONT_SIZE_SMALL = 16
FONT_SIZE_HINT = 13
FONT_SIZE_LEGEND_TITLE = 22
FONT_SIZE_LEGEND_BODY = 16
