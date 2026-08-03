"""Auto-repeat for held-down keys (e.g. arrow keys, N/M).

pygame only sends one KEYDOWN per physical key press unless you opt in to
OS-level key repeat - and that repeat is a single global rate for every key,
which doesn't give us acceleration. Instead we track held keys ourselves:
a key fires once immediately, waits KEY_REPEAT_INITIAL_DELAY_MS, then
repeats at KEY_REPEAT_INTERVAL_MS, speeding up to KEY_REPEAT_FAST_INTERVAL_MS
after KEY_REPEAT_FAST_AFTER_MS of continuous holding.
"""
from metronome import config


class KeyRepeater:
    def __init__(self):
        self._held = {}  # key -> {"callback", "held_ms", "since_repeat_ms"}

    def press(self, key, callback):
        self._held[key] = {"callback": callback, "held_ms": 0.0, "since_repeat_ms": 0.0}
        callback()

    def release(self, key):
        self._held.pop(key, None)

    def update(self, dt_ms):
        for state in self._held.values():
            state["held_ms"] += dt_ms
            state["since_repeat_ms"] += dt_ms

            if state["held_ms"] < config.KEY_REPEAT_INITIAL_DELAY_MS:
                continue

            held_after_delay = state["held_ms"] - config.KEY_REPEAT_INITIAL_DELAY_MS
            interval = (
                config.KEY_REPEAT_FAST_INTERVAL_MS
                if held_after_delay >= config.KEY_REPEAT_FAST_AFTER_MS
                else config.KEY_REPEAT_INTERVAL_MS
            )
            if state["since_repeat_ms"] >= interval:
                state["since_repeat_ms"] = 0.0
                state["callback"]()
