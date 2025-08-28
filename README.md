# Metronome App for macOS

Needed a simple metronome app for mac and wanted to test ChatGPT 5's vibe coding capabilities a bit. 

Worked quite good, apart from some debugging which ChatGPT couldn't manage. All code as well as the icon is from ChatGPT. Therefore may include some deprecated things or other bad practices.

## Controls
``Up/Down`` Keys for 5bpm increase/decrease.

``Left/Right`` Keys for 1bpm increase/decrease.

``N/M`` keys to change time signature.

``Spacebar`` for Pause.


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