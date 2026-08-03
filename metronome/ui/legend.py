"""A toggleable overlay listing every mouse and keyboard control.

Kept data-driven (a plain list of (control, description) pairs) so adding
a new shortcut later just means adding a row here.
"""
import pygame

from metronome import config

ENTRIES = [
    ("Click BPM number, or 0-9", "Start typing an exact BPM"),
    ("Enter", "Confirm typed BPM"),
    ("Esc", "Cancel typed BPM"),
    ("Space", "Start or stop the click"),
    ("Left / Right", "BPM -1 / +1"),
    ("Up / Down", "BPM -5 / +5"),
    ("N / M", "Beats per bar -1 / +1"),
    ("H or ?", "Toggle this help panel"),
]
NOTE = "Arrow keys and N / M can be held down to keep changing"


class Legend:
    def __init__(self, screen_rect, title_font, body_font, scale=1):
        self.screen_rect = screen_rect
        self.title_font = title_font
        self.body_font = body_font
        self.scale = scale
        self.visible = False

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surface):
        if not self.visible:
            return
        s = self.scale

        scrim = pygame.Surface(self.screen_rect.size, pygame.SRCALPHA)
        scrim.fill(config.Color.OVERLAY_SCRIM)
        surface.blit(scrim, (0, 0))

        control_surfs = [self.body_font.render(c, True, config.Color.ACCENT) for c, _ in ENTRIES]
        desc_surfs = [self.body_font.render(d, True, config.Color.TEXT_SECONDARY) for _, d in ENTRIES]
        note_surf = self.body_font.render(NOTE, True, config.Color.TEXT_SECONDARY)

        column_gap = 28 * s
        side_padding = 24 * s
        control_col_width = max(surf.get_width() for surf in control_surfs)
        desc_col_width = max(surf.get_width() for surf in desc_surfs)
        content_width = side_padding * 2 + control_col_width + column_gap + desc_col_width
        content_width = max(content_width, note_surf.get_width() + side_padding * 2)

        margin = 32 * s  # minimum breathing room against the window edges
        panel_width = min(content_width, self.screen_rect.width - margin)

        header_height = 56 * s
        note_height = 32 * s
        footer_height = 36 * s
        default_row_height = 28 * s
        available_for_rows = self.screen_rect.height - margin - header_height - note_height - footer_height
        row_height = min(default_row_height, available_for_rows // len(ENTRIES))

        panel_height = header_height + row_height * len(ENTRIES) + note_height + footer_height
        panel = pygame.Rect(0, 0, panel_width, panel_height)
        panel.center = self.screen_rect.center

        pygame.draw.rect(surface, config.Color.PANEL, panel, border_radius=16 * s)
        pygame.draw.rect(surface, config.Color.PANEL_BORDER, panel, width=1 * s, border_radius=16 * s)

        title_surf = self.title_font.render("Controls", True, config.Color.TEXT_PRIMARY)
        surface.blit(title_surf, (panel.x + side_padding, panel.y + 18 * s))

        y = panel.y + header_height
        control_x = panel.x + side_padding
        desc_x = control_x + control_col_width + column_gap
        for control_surf, desc_surf in zip(control_surfs, desc_surfs):
            surface.blit(control_surf, (control_x, y))
            surface.blit(desc_surf, (desc_x, y))
            y += row_height

        surface.blit(note_surf, note_surf.get_rect(midtop=(panel.centerx, y + 4 * s)))

        hint_surf = self.body_font.render("click anywhere or press H to close", True, config.Color.TEXT_MUTED)
        surface.blit(hint_surf, hint_surf.get_rect(midbottom=(panel.centerx, panel.bottom - 12 * s)))
