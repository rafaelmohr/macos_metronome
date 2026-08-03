# Architecture

The app used to be a single 107-line script. It's now a small package so
each concern (state, audio, input, rendering) can change independently.

```
main.py                    entry point: App().run()
metronome/
  config.py                every tunable constant: sizes, limits, timing, theme colors
  resources.py              resource_path() - finds bundled files in dev vs. a frozen .app
  state.py                  MetronomeState - the only place tempo/beats/pause/BPM-entry rules live
  audio.py                  AudioEngine - loads and plays the two click sounds
  key_repeater.py           KeyRepeater - auto-repeat for held-down keys
  sdl_hints.py              ctypes bridge to SDL hints pygame doesn't expose (render scale quality)
  app.py                    App - owns the window/renderer, event loop, and wires everything together
  ui/
    bpm_display.py           the big BPM number; click or type digits to edit it directly
    beat_indicator.py        the row of beat lights
    legend.py                the toggleable help overlay (data-driven list of controls)
```

Control is keyboard-first by design: arrow keys and N/M for tempo and time
signature, spacebar for play/pause, digits to type an exact BPM. The only
mouse interaction is clicking the BPM number to start typing, and clicking
anywhere to dismiss the legend overlay - there are no on-screen +/- or
play/pause buttons.

## Data flow

`App` is the only class that touches pygame events directly. On each event
it calls a method on `MetronomeState` (e.g. `adjust_tempo`, `toggle_pause`,
`append_bpm_digit`) - state validates and clamps, nothing else does. The
draw step then just reads `state` and renders it; widgets don't hold their
own copy of app data.

## Adding a new control

1. Add the rule/clamping to `MetronomeState` in `state.py`.
2. Add the key check in `App._handle_keydown` (route it through
   `key_repeater.press()` if it should auto-repeat while held).
3. Add a row to `ENTRIES` in `ui/legend.py` so it shows up in the help panel.

## Held-key auto-repeat

`KeyRepeater` tracks currently-held keys itself rather than relying on
pygame's global OS key-repeat (which is one fixed rate for every key, no
per-key control). `App._handle_keydown` calls `key_repeater.press(key,
callback)` for repeatable keys (arrows, N/M); `KEYUP` calls
`key_repeater.release(key)`. Each frame, `key_repeater.update(dt_ms)` fires
the callback again once a key has been held past `KEY_REPEAT_INITIAL_DELAY_MS`,
repeating at `KEY_REPEAT_INTERVAL_MS` and speeding up to
`KEY_REPEAT_FAST_INTERVAL_MS` after `KEY_REPEAT_FAST_AFTER_MS` of continuous
holding. All four constants live in `config.py`. Space, Enter/Esc/Backspace
and digit keys are one-shot and never go through the repeater.

## BPM keyboard entry

Typing a digit (with nothing focused) or clicking the BPM number both call
`state.start_bpm_edit()`. While `state.editing_bpm` is true, digit keys
append to `state.bpm_entry_buffer`, Enter calls `confirm_bpm_edit()` (parses,
clamps, applies), Esc calls `cancel_bpm_edit()`. Clicking anywhere else on
the window while editing also confirms, matching common form UX.

## Rendering: supersampling + a real window/renderer

Everything is drawn onto `App.canvas`, a plain `pygame.Surface` sized
`RENDER_SCALE` (currently 4x) larger than the actual window. Every widget's
rect and font is built at that same scale (see `App._scaled_rect` and
`App._load_fonts`), so text and rounded corners are rasterized with real
extra detail rather than just being stretched pixels. Each frame, that
canvas is converted to a `pygame._sdl2.video.Texture` and presented through
a `Renderer`, which stretches it to fill the window - `sdl_hints.py` sets
SDL's render scale quality to `linear` first so that stretch is smooth
rather than blocky.

The window itself is created via `pygame._sdl2.video.Window(...,
allow_highdpi=True)` rather than `pygame.display.set_mode()`, specifically
to ask SDL for a window backed by the display's true physical pixel count
(e.g. 2x on Retina) instead of just its point size - so the OS never has to
silently upscale (and blur) our already-rendered frame after the fact.
Whether that actually engages depends on the SDL/macOS combination it runs
on: on the machine this was built and tested on, `allow_highdpi` measurably
made no difference (verified by querying the window's real pixel size via
`SDL_GetWindowSizeInPixels`, which came back equal to its point size
regardless of the flag, the bundle's `NSHighResolutionCapable` plist entry,
or pygame version) - a currently-unresolved SDL2/pygame limitation, not a
bug in this app. `RENDER_SCALE` is what's actually carrying the visual
quality in that case; if a future SDL/pygame update fixes native HiDPI
backing, `RENDER_SCALE` could likely be lowered without losing sharpness.

Mouse events (`pygame.mouse.get_pos()` / `event.pos`) are reported in
window (point) coordinates, not canvas coordinates, so `App._handle_mouse_down`
scales incoming positions by `self.scale` before hit-testing against widget
rects, which all live in canvas space.
