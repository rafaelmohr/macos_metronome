"""Locating bundled resources in both dev and frozen (py2app) builds."""
import os
import sys


def resource_path(filename: str) -> str:
    """Return the absolute path to a bundled resource file.

    In a py2app-frozen .app, data files live in Contents/Resources next to
    the executable rather than next to the source tree, so the lookup base
    differs between dev and frozen runs.
    """
    if getattr(sys, "frozen", False):
        base_path = os.path.join(os.path.dirname(sys.executable), "..", "Resources")
        base_path = os.path.abspath(base_path)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)
