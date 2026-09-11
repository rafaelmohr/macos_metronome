# Metronome App for macOS

A simple, keyboard-driven metronome app for macOS, built natively in Swift
and SwiftUI.

## Controls
Everything is keyboard-driven. Press `H` (or `?`) at any time to open the in-app legend
listing every control.

``Up/Down`` Keys for 5bpm increase/decrease.

``Left/Right`` Keys for 1bpm increase/decrease.

Hold any of the above down to keep changing the value - it speeds up the longer you hold.

``N/M`` keys to change time signature (also hold to keep changing).

``Spacebar`` for Pause.

``0-9`` (or click the BPM number) to start typing an exact BPM, ``Enter`` to confirm,
``Esc`` to cancel. Typing also auto-confirms about a second after you stop.

## Requirements
Full Xcode (not just the Command Line Tools), on macOS 14 or later.

## Code structure
The app lives in `swift/Sources/Metronome` (state, audio, key handling, SwiftUI views),
with `MetronomeApp.swift` as the entry point. It's a Swift Package, so Xcode opens it
directly - no `.xcodeproj` needed.

## Dev
Open the package in Xcode and hit Run:
```
xed swift
```
or run it from the command line:
```
cd swift
swift run
```

## Test
```
cd swift
swift test
```

## Build
```
cd swift
./Scripts/build_app.sh
```
which generates `Metronome.app` in `swift/dist`. You can copy this wherever you like.

The sound files ``high.wav`` and ``low.wav`` (bundled in `swift/Sources/Metronome/Resources`)
can be swapped out.
