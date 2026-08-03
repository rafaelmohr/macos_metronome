"""Mutable application state and the rules for changing it.

Nothing in here touches pygame drawing or events directly - this module is
the single source of truth for "what is the metronome currently doing",
so UI code can stay dumb (render whatever the state says) and input code
can stay dumb (translate raw events into calls on this class).
"""
from metronome import config


class MetronomeState:
    def __init__(self):
        self.tempo = config.START_TEMPO
        self.beats_per_bar = config.START_BEATS_PER_BAR
        self.beat = 0
        self.paused = False

        # BPM keyboard text-entry mode
        self.editing_bpm = False
        self.bpm_entry_buffer = ""

    # --- tempo ---
    @property
    def interval_ms(self) -> int:
        return int(60000 / self.tempo)

    def adjust_tempo(self, delta: int):
        self.set_tempo(self.tempo + delta)

    def set_tempo(self, value: int):
        self.tempo = max(config.MIN_TEMPO, min(config.MAX_TEMPO, int(value)))

    # --- time signature ---
    def adjust_beats_per_bar(self, delta: int):
        self.beats_per_bar = max(
            config.MIN_BEATS_PER_BAR,
            min(config.MAX_BEATS_PER_BAR, self.beats_per_bar + delta),
        )
        self.beat = 0

    # --- transport ---
    def toggle_pause(self):
        self.paused = not self.paused

    def advance_beat(self) -> bool:
        """Move to the next beat, returning True if it's the downbeat."""
        self.beat = (self.beat + 1) % self.beats_per_bar
        return self.beat == 0

    # --- BPM keyboard text-entry ---
    def start_bpm_edit(self):
        self.editing_bpm = True
        self.bpm_entry_buffer = ""

    def append_bpm_digit(self, digit: str):
        if len(self.bpm_entry_buffer) < config.BPM_ENTRY_MAX_DIGITS:
            self.bpm_entry_buffer += digit

    def backspace_bpm_edit(self):
        self.bpm_entry_buffer = self.bpm_entry_buffer[:-1]

    def confirm_bpm_edit(self):
        if self.bpm_entry_buffer:
            self.set_tempo(int(self.bpm_entry_buffer))
        self.editing_bpm = False
        self.bpm_entry_buffer = ""

    def cancel_bpm_edit(self):
        self.editing_bpm = False
        self.bpm_entry_buffer = ""
