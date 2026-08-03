"""Thin ctypes bridge to an SDL2 hint pygame doesn't expose: render
scale-quality, which controls whether stretching a texture to fill the
window uses smooth (bilinear) or blocky (nearest-neighbor) filtering.

Uses ctypes.CDLL(None) to reach into the SDL2 symbols pygame has already
loaded into the process, rather than hardcoding pygame's internal package
layout - this keeps it working across pygame install methods. Best-effort:
any failure here just means we fall back to SDL's default (nearest), never
a crash.
"""
import ctypes

try:
    _sdl = ctypes.CDLL(None)
    _sdl.SDL_SetHint.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _sdl.SDL_SetHint.restype = ctypes.c_int
except (OSError, AttributeError):
    _sdl = None


def set_render_scale_quality_linear():
    """Make texture scaling smooth (bilinear) instead of blocky (nearest)."""
    if _sdl is None:
        return
    try:
        _sdl.SDL_SetHint(b"SDL_RENDER_SCALE_QUALITY", b"linear")
    except Exception:
        pass
