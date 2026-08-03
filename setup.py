from setuptools import setup

APP = ['main.py']
DATA_FILES = ['high.wav', 'low.wav']
OPTIONS = {
    'argv_emulation': False,
    'packages': ['pygame', 'metronome'],
    'iconfile': 'icon.icns',
    'includes': ['jaraco.text'],
    'excludes': ['wheel'],   # <<< prevent wheel metadata duplication
    'plist': {
        'CFBundleName': 'Metronome',
        'CFBundleIdentifier': 'com.example.simplemetronome',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

