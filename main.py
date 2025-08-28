import os
import sys
import pygame

def resource_path(filename):
    """Return path to resource in development or in .app bundle"""
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
        base_path = os.path.abspath(base_path)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, filename)

# --- settings ---
WIDTH, HEIGHT = 400, 300
FPS = 60
START_TEMPO = 120  # BPM
BEATS_PER_BAR = 4

# --- init ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Metronome")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 72, bold=True)
small_font = pygame.font.SysFont("Arial", 24)

tempo = START_TEMPO
beat = 0
paused = False  # <-- new pause state

# load sounds
high_sound = pygame.mixer.Sound(resource_path("high.wav"))
low_sound = pygame.mixer.Sound(resource_path("low.wav"))

# custom event for metronome tick
TICK = pygame.USEREVENT + 1
interval_ms = int(60000 / tempo)
pygame.time.set_timer(TICK, interval_ms)

# --- loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  # toggle pause

            elif event.key == pygame.K_RIGHT:
                tempo += 1
            elif event.key == pygame.K_LEFT:
                tempo -= 1
            elif event.key == pygame.K_UP:
                tempo += 5
            elif event.key == pygame.K_DOWN:
                tempo -= 5
            elif event.key == pygame.K_m:
                BEATS_PER_BAR = max(1, min(8, BEATS_PER_BAR + 1))
            elif event.key == pygame.K_n:
                BEATS_PER_BAR = max(1, min(8, BEATS_PER_BAR - 1))



            tempo = max(20, min(300, tempo))  # clamp

            # update timer interval when tempo changes
            interval_ms = int(60000 / tempo)
            pygame.time.set_timer(TICK, interval_ms)

        elif event.type == TICK and not paused:  # only tick if not paused
            beat = (beat + 1) % BEATS_PER_BAR
            if beat == 0:
                high_sound.play()
            else:
                low_sound.play()

    screen.fill((30, 30, 30))

    # draw BPM
    text_surface = font.render(f"{tempo} BPM", True, (220, 220, 220))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(text_surface, text_rect)

    # draw beat bars
    bar_width = WIDTH // BEATS_PER_BAR
    for i in range(BEATS_PER_BAR):
        rect = pygame.Rect(i * bar_width, HEIGHT - 80, bar_width - 10, 50)
        color = (100, 100, 100)
        if i == beat and not paused:
            color = (200, 80, 80) if i == 0 else (80, 200, 80)
        pygame.draw.rect(screen, color, rect, border_radius=15)

    # draw pause text
    if paused:
        pause_surface = small_font.render("PAUSED", True, (200, 200, 50))
        pause_rect = pause_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(pause_surface, pause_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

