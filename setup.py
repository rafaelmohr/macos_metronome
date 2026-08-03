import os

from setuptools import setup

import py2app.recipes.pygame as _pygame_recipe


def _pygame_resources(cmd, mf):
    """Replacement for py2app's bundled pygame recipe.

    That recipe (still the case in py2app 0.28.10) hardcodes a resource list
    containing pygame_icon.icns. pygame-ce ships pygame_icon.bmp instead, so
    the stock recipe aborts the build copying a file that isn't there. Copy
    whichever of the known resources the installed flavour actually has.
    """
    module = mf.findNode("pygame")
    if module is None or module.filename is None:
        return None
    package_dir = os.path.dirname(module.filename)
    candidates = ["freesansbold.ttf", "pygame_icon.icns",
                  "pygame_icon.bmp", "pygame_icon_mac.bmp"]
    present = [os.path.join(package_dir, name) for name in candidates
               if os.path.exists(os.path.join(package_dir, name))]
    return {"loader_files": [("pygame", present)]}


_pygame_recipe.check = _pygame_resources

APP = ['main.py']
DATA_FILES = ['high.wav', 'low.wav', 'icon.png']
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

