import random
import sys
import time
from typing import List

import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)
CASINO_RED = (220, 20, 60)
CONFETTI_COLORS = [
    (255, 82, 82),
    (99, 233, 142),
    (255, 219, 77),
    (109, 178, 255),
    (255, 132, 255),
]

# Spin parameters (names per second).
START_SPEED_NAMES_PER_SEC = 20.0
END_SPEED_NAMES_PER_SEC = 0.3 
SPIN_DURATION_SECONDS = 20.0
RUTTLER_PROBABILITY = 0.4
RUTTLER_PAUSE_RANGE = (0.4, 0.8)
TARGET_FPS = 90
END_JERK_THRESHOLD_ROWS = 1.2  # Schwelle (in Namensabständen), ab der der letzte Ruck greift
END_JERK_TIME_SEC = 1       # Dauer, in der der Restweg maximal abgeschlossen wird (schneller Ruck)


def _build_reel(candidates: List[str], min_len: int = 400) -> List[str]:
    reel = list(candidates)
    while len(reel) < min_len:
        reel.extend(candidates)
    random.shuffle(reel)
    return reel


def _create_confetti(width: int, height: int, amount: int = 220):
    pieces = []
    for _ in range(amount):
        size = random.randint(6, 14)
        pieces.append(
            {
                "x": random.uniform(0, width),
                "y": random.uniform(-height, 0),
                "speed": random.uniform(20, 42),
                "color": random.choice(CONFETTI_COLORS),
                "size": size,
                "angle": random.uniform(0, 360),
                "spin": random.uniform(-180, 180),
            }
        )
    return pieces


def _run_confetti(screen, width: int, height: int, winner: str, title_font, winner_font):
    clock = pygame.time.Clock()
    confetti = _create_confetti(width, height)
    duration = 4.0
    start = time.time()

    while time.time() - start < duration:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        screen.fill(DARK_GREEN)

        title_surface = title_font.render("JACKPOT!", True, GOLD)
        title_rect = title_surface.get_rect(center=(width / 2, height * 0.18))
        screen.blit(title_surface, title_rect)

        winner_surface = winner_font.render(winner.upper(), True, WHITE)
        winner_rect = winner_surface.get_rect(center=(width / 2, height / 2))
        screen.blit(winner_surface, winner_rect)

        for piece in confetti:
            piece["y"] += piece["speed"] * dt
            piece["angle"] += piece["spin"] * dt
            if piece["y"] - piece["size"] > height:
                piece["y"] = random.uniform(-height * 0.5, -20)
                piece["x"] = random.uniform(0, width)
                piece["speed"] = random.uniform(200, 420)
                piece["spin"] = random.uniform(-180, 180)

            rect = pygame.Rect(0, 0, piece["size"], piece["size"])
            rect.center = (piece["x"], piece["y"])
            pygame.draw.rect(screen, piece["color"], rect)

        pygame.display.flip()


def run_animation(candidates: List[str], task_name: str, weights: dict | None = None):
    """Casino-Slot-Animation mit verlangsamter Endphase und Jubel."""
    if not candidates:
        print(f"Für '{task_name}' hat niemand eine Lösung eingereicht.")
        return None

    pygame.init()

    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Casino Auswahl")
    width, height = screen.get_size()

    try:
        title_font = pygame.font.Font(None, 110)
        name_font = pygame.font.Font(None, 160)
        winner_font = pygame.font.Font(None, 220)
        overlay_font = pygame.font.Font(None, 160)
        summary_font = pygame.font.Font(None, 120)
    except pygame.error:
        title_font = pygame.font.SysFont("sans", 110, bold=True)
        name_font = pygame.font.SysFont("sans", 160, bold=True)
        winner_font = pygame.font.SysFont("sans", 220, bold=True)
        overlay_font = pygame.font.SysFont("sans", 160, bold=True)
        summary_font = pygame.font.SysFont("sans", 120, bold=True)

    spacing = int(name_font.get_height() * 1.4)

    def draw_frame_lines():
        pygame.draw.line(screen, GOLD, (0, height / 2 - spacing / 2), (width, height / 2 - spacing / 2), 8)
        pygame.draw.line(screen, GOLD, (0, height / 2 + spacing / 2), (width, height / 2 + spacing / 2), 8)

    def spin_once():
        nonlocal screen
        start_speed_names = max(START_SPEED_NAMES_PER_SEC, 0.01)
        end_speed_names = max(END_SPEED_NAMES_PER_SEC, 0.0)
        mid_speed_names = max(end_speed_names, min(start_speed_names, 3.0 * end_speed_names))
        motion_duration = max(SPIN_DURATION_SECONDS, 0.5)

        phase1_time = motion_duration * 0.5
        phase2_time = motion_duration - phase1_time

        start_speed_px = start_speed_names * spacing
        mid_speed_px = mid_speed_names * spacing
        end_speed_px = end_speed_names * spacing

        distance_phase1 = ((start_speed_px + mid_speed_px) * 0.5) * phase1_time
        distance_phase2 = ((mid_speed_px + end_speed_px) * 0.5) * phase2_time
        estimated_distance = distance_phase1 + distance_phase2
        winner_index = max(int(round(estimated_distance / spacing)), 5)
        target_offset = winner_index * spacing

        min_reel_length = max(400, winner_index + 200)
        reel = _build_reel(candidates, min_len=min_reel_length)
        # Wähle Gewinner - falls Gewichte übergeben wurden, nutze sie
        if weights:
            # Stelle sicher, dass die Reihenfolge mit 'candidates' übereinstimmt
            try:
                weight_list = [max(0.0, float(weights.get(c, 0.0))) for c in candidates]
            except Exception:
                weight_list = None
            if weight_list and any(w > 0 for w in weight_list):
                winner = random.choices(candidates, weights=weight_list, k=1)[0]
            else:
                winner = random.choice(candidates)
        else:
            winner = random.choice(candidates)

        decoy = None
        if len(set(candidates)) > 1 and random.random() < RUTTLER_PROBABILITY:
            decoys = [c for c in candidates if c != winner]
            if decoys:
                decoy = random.choice(decoys)
        use_decoy = decoy is not None

        if winner in reel:
            reel.remove(winner)
        if decoy and decoy in reel:
            reel.remove(decoy)

        if use_decoy and winner_index > 0:
            insert_index = winner_index - 1
            reel.insert(insert_index, decoy)
            reel.insert(insert_index + 1, winner)
            decoy_offset = insert_index * spacing
            winner_offset = (insert_index + 1) * spacing
        else:
            insert_index = winner_index
            reel.insert(insert_index, winner)
            decoy_offset = None
            winner_offset = insert_index * spacing
            use_decoy = False

        target_offset = winner_offset

        clock = pygame.time.Clock()
        scroll_offset = 0.0
        motion_elapsed = 0.0
        pause_until = None
        rattle_triggered = False

        finished = False
        while not finished:
            dt = clock.tick(TARGET_FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit(0)

            moving = True
            if pause_until is not None:
                if time.time() >= pause_until:
                    pause_until = None
                else:
                    moving = False

            if moving and scroll_offset < target_offset:
                if motion_elapsed < phase1_time:
                    phase_progress = min(motion_elapsed / phase1_time, 1.0)
                    current_speed_names = start_speed_names + (mid_speed_names - start_speed_names) * phase_progress
                else:
                    phase_progress = min((motion_elapsed - phase1_time) / max(phase2_time, 1e-6), 1.0)
                    current_speed_names = mid_speed_names + (end_speed_names - mid_speed_names) * phase_progress
                current_speed_names = max(current_speed_names, 0.0)
                current_speed_px = current_speed_names * spacing
                max_travel = max(target_offset - scroll_offset, 0.0)

                # Letzter schneller Ruck: wenn wir nah am Ziel sind, erhöhen wir die Geschwindigkeit
                # so, dass der Rest in END_JERK_TIME_SEC abgeschlossen wird (aber ohne zu überspringen).
                if max_travel > 0 and max_travel <= spacing * END_JERK_THRESHOLD_ROWS:
                    desired_speed = max_travel / max(END_JERK_TIME_SEC, 1e-6)
                    current_speed_px = max(current_speed_px, desired_speed)

                if current_speed_px <= 0.0:
                    effective_dt = 0.0
                    distance = 0.0
                else:
                    distance = current_speed_px * dt
                    if distance > max_travel:
                        effective_dt = max_travel / current_speed_px
                        distance = max_travel
                    else:
                        effective_dt = dt

                scroll_offset += distance
                motion_elapsed = min(motion_elapsed + effective_dt, motion_duration)

                if use_decoy and not rattle_triggered and decoy_offset is not None and scroll_offset >= decoy_offset:
                    pause_until = time.time() + random.uniform(*RUTTLER_PAUSE_RANGE)
                    rattle_triggered = True

                if scroll_offset >= target_offset:
                    scroll_offset = target_offset

            screen.fill(DARK_GREEN)
            title_surface = title_font.render(f"Auswahl für: {task_name}", True, WHITE)
            screen.blit(title_surface, title_surface.get_rect(center=(width / 2, height * 0.12)))
            draw_frame_lines()

            center_y = height / 2
            visible_band = spacing * 1.2
            for i, name in enumerate(reel):
                pos_y = (i * spacing) - scroll_offset + center_y
                dist = abs(pos_y - center_y)
                if dist <= visible_band:
                    emphasis = max(0.0, 1.0 - dist / visible_band)
                    alpha = max(80, int(255 * emphasis))
                    scale_factor = 1.0 + 0.15 * emphasis

                    base_surface = name_font.render(name, True, WHITE)
                    if scale_factor != 1.0:
                        new_size = (int(base_surface.get_width() * scale_factor), int(base_surface.get_height() * scale_factor))
                        base_surface = pygame.transform.smoothscale(base_surface, new_size)

                    base_surface.set_alpha(alpha)
                    rect = base_surface.get_rect(center=(width / 2, pos_y))
                    screen.blit(base_surface, rect)

            pygame.display.flip()

            finished = scroll_offset >= target_offset and pause_until is None
            if motion_elapsed >= motion_duration and pause_until is None:
                scroll_offset = target_offset
                finished = True

        return winner

    final_winner = spin_once()

    freespin_triggered = random.random() < 0.1
    if freespin_triggered:
        pause_clock = pygame.time.Clock()
        pause_end = time.time() + 2.0
        while time.time() < pause_end:
            pause_clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return final_winner

        overlay_text = "FREISPIELE AKTIVIERT!"
        blink_start = time.time()
        blink_duration = 1.8
        overlay_clock = pygame.time.Clock()
        while time.time() - blink_start < blink_duration:
            overlay_clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return final_winner
            screen.fill(DARK_GREEN)
            msg = overlay_font.render(overlay_text, True, GOLD)
            pygame.draw.rect(screen, GOLD, (0, height / 2 - 150, width, 300), 12)
            screen.blit(msg, msg.get_rect(center=(width / 2, height / 2)))
            pygame.display.flip()

        final_winner = spin_once()

    _run_confetti(screen, width, height, final_winner, title_font, winner_font)

    summary_clock = pygame.time.Clock()
    waiting = True
    while waiting:
        summary_clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                waiting = False

        screen.fill(DARK_GREEN)
        pygame.draw.rect(screen, GOLD, (0, height / 2 - 220, width, 440), 14)

        title_surface = summary_font.render("Votierer:in:", True, WHITE)
        screen.blit(title_surface, title_surface.get_rect(center=(width / 2, height / 2 - 110)))

        winner_surface = winner_font.render(final_winner.upper(), True, CASINO_RED)
        screen.blit(winner_surface, winner_surface.get_rect(center=(width / 2, height / 2 + 40)))

        hint_surface = summary_font.render("Beliebige Taste zum Beenden drücken", True, WHITE)
        screen.blit(hint_surface, hint_surface.get_rect(center=(width / 2, height * 0.88)))

        pygame.display.flip()

    pygame.quit()
    return final_winner
