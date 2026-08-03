# Metronome App for macOS

A simple, keyboard-driven metronome app for macOS, built with pygame-ce.

Note: it needs **pygame-ce**, not upstream `pygame`. Upstream accepts the
high-DPI window flag but never applies it, so the UI renders blurry on Retina
displays; see `docs/ARCHITECTURE.md` for details.

## Controls
Everything is keyboard-driven. Press `H` (or `?`) at any time to open the in-app legend
listing every control.

``Up/Down`` Keys for 5bpm increase/decrease.

``Left/Right`` Keys for 1bpm increase/decrease.

Hold any of the above down to keep changing the value - it speeds up the longer you hold.

``N/M`` keys to change time signature (also hold to keep changing).

``Spacebar`` for Pause.

``0-9`` (or click the BPM number) to start typing an exact BPM, ``Enter`` to confirm, ``Esc`` to cancel.

## Code structure
The app lives in the `metronome/` package (state, audio, UI widgets, main app loop),
with `main.py` as a thin entry point. See `docs/ARCHITECTURE.md` for a tour of how it
fits together.

## Install
First create & activate venv, then install dependencies.
```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel

pip install -r requirements.txt
```

## Dev
Run
```
python main.py
```
for development testing.

## Build
Run 
```
rm -rf build dist
python setup.py py2app
```
which should generate ``Metronome.app`` in ``/dist``. You can copy this wherever you like.

The sound files ``high.wav`` and ``low.wav`` can be swapped out.