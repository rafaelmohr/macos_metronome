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

## Rendering: draw once, at the display's real pixel count

The window is created as `pygame.Window(..., allow_high_dpi=True)`. That flag
is the whole ballgame on a Retina display: with it, SDL gives the window a
framebuffer measured in real physical pixels (1120x840 for our 560x420-point
window at 2x); without it, SDL gets a 560x420 buffer and macOS magnifies it
to fill the same screen area, softening every pixel we drew.

`App._sync_to_display()` reads that framebuffer's true size from
`renderer.get_viewport()` and sizes `App.canvas` - a plain `pygame.Surface` -
to match it exactly. `App.scale` is the ratio between the two (2 on Retina,
1 on a standard display), and every widget rect and font is built at that
scale (`App._scaled_rect`, `App._load_fonts`). Each frame the canvas becomes
a `pygame._sdl2.video.Texture` and is presented through the `Renderer`;
because the canvas is already exactly framebuffer-sized, that present is 1:1
and nothing is ever resampled. Glyphs are rasterized straight at their final
pixel size, which is as sharp as the display can render.

`_draw` compares the canvas size against the framebuffer each frame and calls
`_sync_to_display()` again if they diverge, so dragging the window between a
Retina and a non-Retina monitor rebuilds the canvas and fonts at the new
density instead of scaling the old ones.

This is also why the project depends on **pygame-ce rather than upstream
pygame**. Upstream's `pygame._sdl2.video.Window` accepts an `allow_highdpi`
keyword - it validates the name, so a typo raises `TypeError` - but never
actually passes `SDL_WINDOW_ALLOW_HIGHDPI` to SDL. The window silently comes
back at point resolution, which is what made the whole UI blurry. The same
SDL build honours the flag correctly when it's passed by hand via ctypes, and
pygame-ce's `allow_high_dpi` (note the underscores) passes it properly. If
you ever swap the dependency back, `app.py` raises on import rather than
quietly rendering soft again.

Because there is no supersampling any more, there is deliberately no
render-scale constant in `config.py`. Drawing at a fixed multiple of the
window size would mean resampling the finished frame to fit the framebuffer,
which is exactly what softens a UI.

Mouse events (`pygame.mouse.get_pos()` / `event.pos`) are reported in
window (point) coordinates, not canvas coordinates, so `App._handle_mouse_down`
scales incoming positions by `self.scale` before hit-testing against widget
rects, which all live in canvas space.

## The Dock icon

`App._apply_icon()` loads `icon.png` and sets it on the window right after
creating it. This is not redundant with the bundle's `icon.icns`: pygame
gives every window it creates its own icon, and on macOS `SDL_SetWindowIcon`
feeds through to NSApplication's `setApplicationIconImage:`, which replaces
the Dock icon Launch Services set from the bundle. Without this the correct
icon flashes up at launch and is then swapped for the pygame snake. Ours wins
because it is set after pygame's default. `icon.png` therefore has to ship in
`DATA_FILES` alongside the click sounds, not just as the `iconfile`.

## Packaging note

`setup.py` replaces py2app's bundled pygame recipe. That recipe (still true
in py2app 0.28.10) hardcodes `pygame_icon.icns`, a file upstream pygame ships
and pygame-ce doesn't, so the stock recipe aborts the build. The replacement
copies whichever of the known pygame resource files actually exist.
