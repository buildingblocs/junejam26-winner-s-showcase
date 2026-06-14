import asyncio
import array
import json
import math
from pathlib import Path
import queue
import random
import sys
import threading
import time

import pygame
import websockets

from challenges import CHEATSHEET_TOPICS
from config import (
    INTERACTION_RANGE,
    NORMAL_TERMINALS,
    PLAYER_RADIUS,
    PLAYER_SPEED,
    ROLE_COLORS,
    SERVER_PORT,
    TERMINAL_HEIGHT,
    TERMINAL_WIDTH,
    TERMINALS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from protocol import (
    RESULT_ATTACKERS_WIN,
    RESULT_DEFENDERS_WIN,
    ROLE_ATTACKER,
    ROLE_DEFENDER,
    display_social_role,
)


BG = (12, 17, 27)
PANEL = (23, 31, 46)
TEXT = (232, 237, 245)
MUTED = (150, 163, 184)
GREEN = (65, 220, 130)
RED = (245, 90, 90)
YELLOW = (245, 205, 80)
ORANGE = (255, 165, 80)
CURRENT_PLAYER_LABEL = (95, 230, 255)
CARET_BLINK_SECONDS = 0.45
SPRITE_HEIGHT = 72
TERMINAL_SPRITE_HEIGHT = 136
ROLE_REVEAL_FADE_SECONDS = 0.3
ROLE_REVEAL_CARD_HOLD_SECONDS = 2.3
ROLE_REVEAL_EXIT_FADE_SECONDS = 0.3
ROLE_REVEAL_SECONDS = (
    ROLE_REVEAL_FADE_SECONDS
    + ROLE_REVEAL_CARD_HOLD_SECONDS
    + ROLE_REVEAL_EXIT_FADE_SECONDS
)
ROLE_REVEAL_BLACK_SECONDS = 0.25
ROLE_REVEAL_GLITCH_SECONDS = 2.65
ROLE_REVEAL_BLACK_HOLD_SECONDS = 0.25
ROLE_REVEAL_SPOTLIGHT_SECONDS = 0.0
GAME_OVER_ANIMATION_SECONDS = 6.0
GAME_OVER_TRANSITION_SECONDS = 0.75
WRONG_ANSWER_EFFECT_SECONDS = 0.55
WRONG_ANSWER_SHAKE_PIXELS = 10
FLOATING_FEEDBACK_SECONDS = 1.35
SYSTEM_REACTION_SECONDS = 0.9
OBJECTIVE_BANNER_SECONDS = 3.25
IDLE_ANIMATION_FPS = 7
RUN_ANIMATION_FPS = 12
FIX_ANIMATION_FPS = 10
POSITION_SMOOTHING = 18
SPRITE_ROOT = Path(__file__).resolve().parent / "assets" / "sprites" / "engineer"
TERMINAL_SPRITE_ROOT = Path(__file__).resolve().parent / "assets" / "sprites" / "terminal"
TERMINAL_SPRITE_FILES = {
    "terminal_python": "data_centre_sprite.png",
    "terminal_crypto": "network_core_sprite.png",
    "terminal_network": "power_grid_sprite.png",
}
LAB_AMBIENT_PROPS = (
    {"kind": "monitor", "x": 92, "y": 430, "color": (70, 150, 255), "phase": 0.0},
    {"kind": "scanner", "x": 330, "y": 575, "color": (245, 205, 80), "phase": 1.4},
    {"kind": "monitor", "x": 680, "y": 585, "color": (70, 220, 150), "phase": 3.1},
    {"kind": "scanner", "x": 905, "y": 430, "color": (255, 165, 80), "phase": 4.0},
)
TITLE_FONT_CANDIDATES = ("bahnschrift", "segoeuisemibold", "segoeui", "arial")
UI_FONT_CANDIDATES = ("bahnschrift", "segoeui", "arial", "calibri")
GUIDE_BUTTON_RECT = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 54, 130, 36)
CHEATSHEET_BUTTON_RECT = GUIDE_BUTTON_RECT.move(0, -44)
CHEATSHEET_BOX_RECT = pygame.Rect(70, 54, 860, 580)
CHEATSHEET_VIEWPORT_RECT = pygame.Rect(104, 148, 770, 452)
CHEATSHEET_SECTION_HEADER_HEIGHT = 70
CHEATSHEET_SECTION_GAP = 18
CHEATSHEET_TOPIC_HEIGHT = 58
CHEATSHEET_SCROLL_STEP = 48
GUIDE_TABS = (
    ("overview", "Overview"),
    ("roles", "Roles"),
    ("defender", "Defender"),
    ("attacker", "Attacker"),
    ("controls", "Controls"),
)
REPORT_BUTTON_RECT = pygame.Rect(WINDOW_WIDTH // 2 - 150, 378, 300, 46)
RESULT_PANEL_RECT = pygame.Rect(135, 96, WINDOW_WIDTH - 270, 390)
REPORT_BOX_RECT = pygame.Rect(55, 55, WINDOW_WIDTH - 110, WINDOW_HEIGHT - 115)
REPORT_CLOSE_RECT = pygame.Rect(WINDOW_WIDTH - 178, 78, 96, 34)
REPORT_PREV_RECT = pygame.Rect(WINDOW_WIDTH // 2 - 185, WINDOW_HEIGHT - 78, 145, 38)
REPORT_NEXT_RECT = pygame.Rect(WINDOW_WIDTH // 2 + 40, WINDOW_HEIGHT - 78, 145, 38)
ATTACKER_ABILITY_ROWS = (
    ("BLACKOUT", 1, "Freeze and darken nearest defender screen"),
    ("FALSE_ALERT", 2, "Force a healthy system critical"),
    ("MALWARE_INJECTION", 3, "Choose a system: -15+bonus health"),
)


class NetworkClient:
    def __init__(self, uri):
        self.uri = uri
        self.incoming = queue.Queue()
        self.outgoing = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self.thread.start()

    def send(self, message):
        self.outgoing.put(message)

    def close(self):
        self.stop_event.set()

    def _run(self):
        asyncio.run(self._network_loop())

    async def _network_loop(self):
        try:
            async with websockets.connect(self.uri) as websocket:
                self.incoming.put({"type": "connection", "connected": True})

                async def receive():
                    async for raw_message in websocket:
                        self.incoming.put(json.loads(raw_message))

                async def transmit():
                    while not self.stop_event.is_set():
                        try:
                            message = self.outgoing.get_nowait()
                        except queue.Empty:
                            await asyncio.sleep(0.01)
                            continue
                        await websocket.send(json.dumps(message))

                receiver = asyncio.create_task(receive())
                sender = asyncio.create_task(transmit())
                done, pending = await asyncio.wait(
                    [receiver, sender], return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()
                for task in done:
                    task.result()
        except Exception as exc:
            self.incoming.put(
                {"type": "connection", "connected": False, "message": str(exc)}
            )


def server_uri(argument):
    if argument.startswith(("ws://", "wss://")):
        return argument
    return f"ws://{argument}:{SERVER_PORT}"


def build_tone_sequence(tones, sample_rate=22050):
    if not pygame.mixer.get_init():
        return None
    samples = array.array("h")
    for frequency, duration, volume in tones:
        frame_count = max(1, int(sample_rate * duration))
        fade_frames = max(1, int(sample_rate * min(0.012, duration / 3)))
        for frame in range(frame_count):
            envelope = 1.0
            if frame < fade_frames:
                envelope = frame / fade_frames
            elif frame > frame_count - fade_frames:
                envelope = max(0.0, (frame_count - frame) / fade_frames)
            value = math.sin(2 * math.pi * frequency * frame / sample_rate)
            samples.append(int(32767 * volume * envelope * value))
    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


def build_game_sounds():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error:
        return {}
    return {
        "correct": build_tone_sequence(((660, 0.07, 0.18), (880, 0.09, 0.16))),
        "wrong": build_tone_sequence(((180, 0.12, 0.2), (120, 0.14, 0.16))),
        "ability": build_tone_sequence(((330, 0.05, 0.16), (220, 0.06, 0.18), (440, 0.08, 0.14))),
        "banner": build_tone_sequence(((440, 0.06, 0.12), (660, 0.08, 0.12))),
        "victory": build_tone_sequence(((523, 0.08, 0.14), (659, 0.08, 0.14), (784, 0.13, 0.14))),
        "defeat": build_tone_sequence(((220, 0.12, 0.16), (165, 0.16, 0.16))),
    }


def play_sound(sounds, name):
    sound = sounds.get(name)
    if sound:
        try:
            sound.play()
        except pygame.error:
            pass


def specialty_terminal_label(specialty):
    labels = {
        "Python Engineer": "Data Center",
        "Cryptographer": "Network Core",
        "Network Analyst": "Power Grid",
    }
    return labels.get(specialty, "Choose Specialty")


def taken_specialties(state, current_player_id=None):
    taken = set()
    for other_id, player in state.get("players", {}).items():
        if other_id == current_player_id:
            continue
        specialty = player.get("specialty")
        if player.get("joined") and specialty:
            taken.add(specialty)
    return taken


def draw_text(surface, font, text, color, x, y, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)


def alpha_text(surface, font, text, color, x, y, alpha, center=True):
    rendered = font.render(text, True, color)
    rendered.set_alpha(max(0, min(255, int(alpha))))
    rect = rendered.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    shadow = font.render(text, True, (2, 5, 10))
    shadow.set_alpha(max(0, min(180, int(alpha))))
    surface.blit(shadow, rect.move(2, 2))
    surface.blit(rendered, rect)


def impact_color(name):
    return {
        "green": GREEN,
        "red": RED,
        "orange": ORANGE,
        "yellow": YELLOW,
    }.get(name, YELLOW)


def add_floating_feedback(items, impact, state, player_id, now):
    if not impact:
        return
    terminal_id = impact.get("terminal_id")
    terminal = TERMINALS.get(terminal_id) if terminal_id else None
    if terminal:
        x = terminal["x"]
        y = terminal["y"] + 20
    else:
        player = state.get("players", {}).get(player_id, {})
        x = int(player.get("x", WINDOW_WIDTH // 2))
        y = int(player.get("y", WINDOW_HEIGHT // 2)) - 54
    text = str(impact.get("text") or "").strip()
    if not text:
        return
    items.append(
        {
            "text": text,
            "x": x,
            "y": y,
            "color": impact_color(impact.get("color")),
            "started_at": now,
        }
    )


def add_system_reaction(reactions, impact, now):
    if not impact or not impact.get("terminal_id"):
        return
    reactions.append(
        {
            "terminal_id": impact["terminal_id"],
            "color": impact_color(impact.get("color")),
            "kind": impact.get("kind", "impact"),
            "started_at": now,
        }
    )


def draw_floating_feedback(surface, font, items, now):
    alive = []
    for item in items:
        elapsed = now - item["started_at"]
        if elapsed >= FLOATING_FEEDBACK_SECONDS:
            continue
        progress = elapsed / FLOATING_FEEDBACK_SECONDS
        lift = 46 * progress
        alpha = 255 * (1.0 - progress)
        scale_y = item["y"] - lift
        alpha_text(surface, font, item["text"], item["color"], item["x"], scale_y, alpha)
        alive.append(item)
    items[:] = alive


def draw_system_reactions(surface, reactions, now):
    alive = []
    for reaction in reactions:
        elapsed = now - reaction["started_at"]
        if elapsed >= SYSTEM_REACTION_SECONDS:
            continue
        terminal = TERMINALS.get(reaction["terminal_id"])
        if not terminal:
            continue
        progress = elapsed / SYSTEM_REACTION_SECONDS
        radius_x = int(64 + 58 * progress)
        radius_y = int(34 + 28 * progress)
        alpha = int(180 * (1.0 - progress))
        pulse_rect = pygame.Rect(0, 0, radius_x * 2, radius_y * 2)
        pulse_rect.center = (terminal["x"], terminal["y"] + 52)
        pulse = pygame.Surface(pulse_rect.size, pygame.SRCALPHA)
        color = reaction["color"]
        pygame.draw.ellipse(pulse, (*color, max(0, alpha // 4)), pulse.get_rect())
        pygame.draw.ellipse(pulse, (*color, max(0, alpha)), pulse.get_rect(), 4)
        if reaction.get("kind") in ("malware", "false_alert", "wrong"):
            inner = pulse.get_rect().inflate(-26, -18)
            if inner.width > 0 and inner.height > 0:
                pygame.draw.ellipse(pulse, (*RED, max(0, alpha // 2)), inner, 2)
        surface.blit(pulse, pulse_rect)
        alive.append(reaction)
    reactions[:] = alive


def compact_number(value):
    try:
        return f"{float(value):g}"
    except (TypeError, ValueError):
        return str(value)


def format_insight_topic(row):
    topic = row.get("topic", "Topic")
    correct = row.get("correct", 0)
    attempts = row.get("attempts", 0)
    accuracy = row.get("accuracy", 0)
    return f"{topic} {correct}/{attempts} ({accuracy}%)"


def format_insight_list(rows, fallback):
    if not rows:
        return fallback
    return ", ".join(format_insight_topic(row) for row in rows[:2])


def report_page_count(state):
    insights = state.get("learning_insights", {})
    own_insight = insights.get("self") or {}
    mistakes = own_insight.get("mistakes", [])
    return 1 + max(1, len(mistakes))


def draw_wrapped_block(surface, font, text, color, x, y, max_width, line_height=22):
    for line in wrapped_lines(font, str(text or ""), max_width):
        draw_text(surface, font, line, color, x, y)
        y += line_height
    return y


def draw_full_report(surface, title_font, font, small_font, state, page):
    insights = state.get("learning_insights", {})
    own_insight = insights.get("self") or {}
    player_insights = insights.get("players", [])
    mistakes = own_insight.get("mistakes", [])
    total_pages = report_page_count(state)
    page = max(0, min(page, total_pages - 1))

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((2, 5, 12, 238))
    surface.blit(overlay, (0, 0))
    pygame.draw.rect(surface, PANEL, REPORT_BOX_RECT, border_radius=8)
    pygame.draw.rect(surface, (80, 120, 175), REPORT_BOX_RECT, 3, 8)
    draw_text(surface, title_font, "Round Report", TEXT, WINDOW_WIDTH // 2, 95, center=True)
    draw_text(surface, small_font, f"Page {page + 1} / {total_pages}", MUTED, WINDOW_WIDTH // 2, 132, center=True)

    pygame.draw.rect(surface, (13, 20, 32), REPORT_CLOSE_RECT, border_radius=5)
    pygame.draw.rect(surface, (80, 120, 175), REPORT_CLOSE_RECT, 1, 5)
    draw_text(surface, small_font, "Close", TEXT, REPORT_CLOSE_RECT.centerx, REPORT_CLOSE_RECT.centery, center=True)

    content_x = REPORT_BOX_RECT.x + 48
    content_y = 160
    content_w = REPORT_BOX_RECT.width - 96

    if page == 0:
        attempts = own_insight.get("attempts", 0)
        correct = own_insight.get("correct", 0)
        accuracy = own_insight.get("accuracy", 0)
        draw_text(surface, font, "Summary Statistics", YELLOW, content_x, content_y)
        content_y += 42
        if attempts:
            draw_text(surface, font, f"You: {correct}/{attempts} correct ({accuracy}%)", TEXT, content_x, content_y)
            content_y += 34
            content_y = draw_wrapped_block(
                surface,
                small_font,
                "Strong: " + format_insight_list(own_insight.get("strengths", []), "not enough correct answers yet"),
                GREEN,
                content_x,
                content_y,
                content_w,
            )
            content_y = draw_wrapped_block(
                surface,
                small_font,
                "Review: " + format_insight_list(own_insight.get("weaknesses", []), "no weak topic found"),
                ORANGE,
                content_x,
                content_y + 8,
                content_w,
            )
        else:
            draw_text(surface, font, "No challenge attempts recorded this round.", MUTED, content_x, content_y)
            content_y += 34

        content_y += 28
        draw_text(surface, font, "Team Snapshot", YELLOW, content_x, content_y)
        content_y += 36
        for insight in player_insights[:8]:
            name = insight.get("name", "Player")[:18]
            attempts = insight.get("attempts", 0)
            accuracy = insight.get("accuracy", 0)
            line = f"{name}: {accuracy}% over {attempts} questions" if attempts else f"{name}: no attempts"
            draw_text(surface, small_font, line, TEXT if attempts else MUTED, content_x + 18, content_y)
            content_y += 25
    else:
        draw_text(surface, font, "Missed Question Review", YELLOW, content_x, content_y)
        content_y += 42
        if not mistakes:
            draw_text(surface, font, "No wrong answers to review.", GREEN, content_x, content_y)
        else:
            mistake = mistakes[page - 1]
            draw_text(
                surface,
                font,
                f"{page}. {mistake.get('topic', 'Topic')} | {mistake.get('system', 'Lab')}",
                YELLOW,
                content_x,
                content_y,
            )
            content_y += 42
            draw_text(surface, small_font, "Question", MUTED, content_x, content_y)
            content_y = draw_wrapped_block(
                surface,
                font,
                mistake.get("question", ""),
                TEXT,
                content_x,
                content_y + 25,
                content_w,
                line_height=28,
            )
            content_y += 26
            draw_text(surface, small_font, "Your answer", MUTED, content_x, content_y)
            content_y = draw_wrapped_block(
                surface,
                font,
                mistake.get("your_answer", "(blank)"),
                ORANGE,
                content_x,
                content_y + 25,
                content_w,
                line_height=28,
            )
            content_y += 26
            draw_text(surface, small_font, "Correct answer", MUTED, content_x, content_y)
            draw_wrapped_block(
                surface,
                font,
                mistake.get("correct_answer", ""),
                GREEN,
                content_x,
                content_y + 25,
                content_w,
                line_height=28,
            )

    prev_enabled = page > 0
    next_enabled = page < total_pages - 1
    prev_color = TEXT if prev_enabled else MUTED
    next_color = TEXT if next_enabled else MUTED
    pygame.draw.rect(surface, (13, 20, 32), REPORT_PREV_RECT, border_radius=5)
    pygame.draw.rect(surface, (80, 120, 175) if prev_enabled else (42, 56, 78), REPORT_PREV_RECT, 2, 5)
    draw_text(surface, small_font, "Previous", prev_color, REPORT_PREV_RECT.centerx, REPORT_PREV_RECT.centery, center=True)
    pygame.draw.rect(surface, (13, 20, 32), REPORT_NEXT_RECT, border_radius=5)
    pygame.draw.rect(surface, YELLOW if next_enabled else (42, 56, 78), REPORT_NEXT_RECT, 2, 5)
    draw_text(surface, small_font, "Next", next_color, REPORT_NEXT_RECT.centerx, REPORT_NEXT_RECT.centery, center=True)
    draw_text(surface, small_font, "Left/Right or A/D also change pages", MUTED, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 28, center=True)


def make_font(candidates, size, bold=False):
    available_fonts = set(pygame.font.get_fonts())
    for name in candidates:
        normalized = name.lower().replace(" ", "")
        if normalized in available_fonts:
            return pygame.font.SysFont(normalized, size, bold=bold)
    return pygame.font.SysFont("arial", size, bold=bold)


def draw_typing_indicator(surface, font, text, x, y, color, now):
    if int(now / CARET_BLINK_SECONDS) % 2:
        return
    text_width = font.size(text)[0]
    caret_rect = pygame.Rect(
        x + text_width + 3,
        y + 2,
        2,
        font.get_height() - 4,
    )
    pygame.draw.rect(surface, color, caret_rect)


def load_animation_frames(folder_name, prefix):
    frames = []
    folder = SPRITE_ROOT / folder_name
    for path in sorted(folder.glob(f"{prefix}*.png")):
        image = pygame.image.load(str(path)).convert_alpha()
        width, height = image.get_size()
        if width < 10 or height < 10:
            continue
        scale = SPRITE_HEIGHT / height
        size = (int(width * scale), SPRITE_HEIGHT)
        frames.append(pygame.transform.smoothscale(image, size))
    return frames


def load_player_sprites():
    sprites = {
        "idle": load_animation_frames("idle", "idle"),
        "run": load_animation_frames("run", "run"),
        "fix": load_animation_frames("fix", "fix"),
    }
    if not sprites["idle"] or not sprites["run"] or not sprites["fix"]:
        print("Sprite frames missing; falling back to circle players.")
    return sprites


def load_terminal_sprites():
    sprites = {}
    for terminal_id, filename in TERMINAL_SPRITE_FILES.items():
        path = TERMINAL_SPRITE_ROOT / filename
        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            continue
        width, height = image.get_size()
        scale = TERMINAL_SPRITE_HEIGHT / height
        size = (max(1, int(width * scale)), TERMINAL_SPRITE_HEIGHT)
        sprites[terminal_id] = pygame.transform.smoothscale(image, size)
    return sprites


def update_player_visuals(visuals, players, dt, now):
    for missing_id in set(visuals) - set(players):
        del visuals[missing_id]

    smoothing = 1 - pow(2.718281828, -POSITION_SMOOTHING * dt)
    for player_id, player in players.items():
        target_x = float(player["x"])
        target_y = float(player["y"])
        visual = visuals.setdefault(
            player_id,
            {
                "x": target_x,
                "y": target_y,
                "target_x": target_x,
                "target_y": target_y,
                "facing": 1,
                "moving_until": 0,
                "fixing": False,
                "fixing_started_at": 0,
            },
        )
        target_dx = target_x - visual["target_x"]
        target_dy = target_y - visual["target_y"]
        if abs(target_dx) > 0.2 or abs(target_dy) > 0.2:
            visual["moving_until"] = now + 0.18
            if abs(target_dx) > 0.1:
                visual["facing"] = 1 if target_dx > 0 else -1

        visual["target_x"] = target_x
        visual["target_y"] = target_y
        server_fixing = player.get("activity") == "fixing"
        if server_fixing != visual.get("fixing", False):
            visual["fixing"] = server_fixing
            if server_fixing:
                visual["fixing_started_at"] = now
        visual["x"] += (target_x - visual["x"]) * smoothing
        visual["y"] += (target_y - visual["y"]) * smoothing


def set_player_fixing(visuals, player_id, is_fixing, now):
    visual = visuals.get(player_id)
    if not visual:
        return
    visual["fixing"] = is_fixing
    if is_fixing:
        visual["fixing_started_at"] = now


def draw_player(surface, sprites, small_font, player, visual, is_current, now):
    color = tuple(player.get("color", (220, 220, 220)))
    position = (int(visual["x"]), int(visual["y"]))
    moving = (
        now < visual["moving_until"]
        or abs(visual["target_x"] - visual["x"]) > 1.0
        or abs(visual["target_y"] - visual["y"]) > 1.0
    )
    fixing = visual.get("fixing", False)
    animation = "fix" if fixing else ("run" if moving else "idle")
    frames = sprites.get(animation) or sprites.get("idle") or []

    if frames:
        if fixing:
            elapsed = now - visual.get("fixing_started_at", now)
            frame = frames[int(elapsed * FIX_ANIMATION_FPS) % len(frames)]
        elif moving:
            frame = frames[int(now * RUN_ANIMATION_FPS) % len(frames)]
        else:
            frame = frames[0]
        if visual["facing"] < 0:
            frame = pygame.transform.flip(frame, True, False)
        rect = frame.get_rect(midbottom=(position[0], position[1] + PLAYER_RADIUS))
        shadow_rect = pygame.Rect(0, 0, 44, 12)
        shadow_rect.center = (position[0], position[1] + PLAYER_RADIUS - 3)
        pygame.draw.ellipse(surface, (4, 8, 14), shadow_rect)
        surface.blit(frame, rect)
    else:
        pygame.draw.circle(surface, color, position, PLAYER_RADIUS)
        if is_current:
            pygame.draw.circle(surface, TEXT, position, PLAYER_RADIUS + 5, 3)

    label = player["name"]
    label_color = CURRENT_PLAYER_LABEL if is_current else TEXT
    shadow = small_font.render(label, True, (3, 7, 12))
    shadow_rect = shadow.get_rect(center=(position[0] + 1, position[1] - 53))
    surface.blit(shadow, shadow_rect)
    draw_text(
        surface,
        small_font,
        label,
        label_color,
        position[0],
        position[1] - 54,
        center=True,
    )


def draw_terminal_text(surface, font, lines, status_color, x, y):
    for index, line in enumerate(lines):
        color = TEXT if index == 0 else status_color
        rendered = font.render(line, True, color)
        shadow = font.render(line, True, (3, 7, 12))
        rect = rendered.get_rect(center=(x, y + index * 18))
        surface.blit(shadow, rect.move(1, 1))
        surface.blit(rendered, rect)


def draw_hud_metric(surface, font, small_font, label, value, color, x):
    draw_text(surface, small_font, label, MUTED, x, 14)
    draw_text(surface, font, value, color, x, 39)


def draw_system_pad(surface, terminal, color, is_close):
    pad_rect = pygame.Rect(0, 0, 190, 62)
    pad_rect.center = (terminal["x"], terminal["y"] + 82)
    pad = pygame.Surface(pad_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(pad, (*color, 14), pad.get_rect())
    pygame.draw.ellipse(pad, (*color, 64 if is_close else 28), pad.get_rect(), 2)
    pygame.draw.line(
        pad,
        (*color, 34),
        (38, pad_rect.height // 2),
        (pad_rect.width - 38, pad_rect.height // 2),
        1,
    )
    surface.blit(pad, pad_rect)


def draw_ambient_lab_props(surface, small_font, now):
    for prop in LAB_AMBIENT_PROPS:
        bob = math.sin(now * 0.75 + prop["phase"]) * 5
        x = int(prop["x"])
        y = int(prop["y"] + bob)
        color = prop["color"]
        kind = prop["kind"]

        glow_rect = pygame.Rect(0, 0, 86, 54)
        glow_rect.center = (x, y)
        glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*color, 20), glow.get_rect())
        surface.blit(glow, glow_rect)

        if kind == "monitor":
            base = pygame.Rect(0, 0, 52, 30)
            base.center = (x, y)
            pygame.draw.rect(surface, (10, 16, 26), base, border_radius=4)
            pygame.draw.rect(surface, (*color, 120), base, 2, border_radius=4)
            line_y = base.y + 10
            pygame.draw.line(surface, color, (base.x + 9, line_y), (base.x + 22, line_y), 1)
            pygame.draw.line(surface, color, (base.x + 27, line_y + 7), (base.right - 8, line_y + 7), 1)
            pygame.draw.line(surface, (4, 8, 14), (x - 18, base.bottom + 7), (x + 18, base.bottom + 7), 3)
        elif kind == "scanner":
            pygame.draw.circle(surface, (10, 16, 26), (x, y), 18)
            pygame.draw.circle(surface, (*color, 130), (x, y), 18, 2)
            sweep_angle = now * 0.55 + prop["phase"]
            end = (x + int(math.cos(sweep_angle) * 24), y + int(math.sin(sweep_angle) * 24))
            pygame.draw.line(surface, color, (x, y), end, 2)
            pygame.draw.circle(surface, color, (x, y), 4)


def draw_action_strip(surface, small_font, me):
    strip = pygame.Rect(24, WINDOW_HEIGHT - 58, 560, 34)
    pygame.draw.rect(surface, (13, 20, 32), strip, border_radius=5)
    pygame.draw.rect(surface, (42, 56, 78), strip, 1, 5)
    is_attacker = me.get("social_role") == ROLE_ATTACKER
    goal = "Goal: destroy the most before time ends" if is_attacker else "Goal: recover the most before time ends"
    action = "E challenge  |  X abilities" if is_attacker else "E challenge near a highlighted system"
    draw_text(surface, small_font, goal, TEXT, strip.x + 14, strip.y + 8)
    draw_text(surface, small_font, action, ORANGE if is_attacker else YELLOW, strip.x + 285, strip.y + 8)


def start_objective_banner(role, now):
    is_attacker = role == ROLE_ATTACKER
    return {
        "started_at": now,
        "role": role,
        "title": "ATTACKER OBJECTIVE" if is_attacker else "DEFENDER OBJECTIVE",
        "line": (
            "Earn Attack Points with E. Spend them with X to disrupt the lab."
            if is_attacker
            else "Recover lab systems. Press E near highlighted systems."
        ),
        "accent": ORANGE if is_attacker else GREEN,
    }


def draw_objective_banner(surface, font, small_font, banner, now):
    elapsed = now - banner["started_at"]
    if elapsed >= OBJECTIVE_BANNER_SECONDS:
        return False
    fade_in = min(1.0, elapsed / 0.25)
    fade_out = min(1.0, (OBJECTIVE_BANNER_SECONDS - elapsed) / 0.35)
    alpha = int(235 * min(fade_in, fade_out))
    slide = int((1.0 - min(1.0, elapsed / 0.35)) * -18)
    rect = pygame.Rect(0, 0, 620, 82)
    rect.center = (WINDOW_WIDTH // 2, 132 + slide)
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (13, 20, 32, alpha), panel.get_rect(), border_radius=8)
    pygame.draw.rect(panel, (*banner["accent"], alpha), panel.get_rect(), 2, 8)
    surface.blit(panel, rect)
    alpha_text(surface, small_font, "MISSION START", MUTED, rect.centerx, rect.y + 18, alpha)
    alpha_text(surface, font, banner["title"], banner["accent"], rect.centerx, rect.y + 42, alpha)
    alpha_text(surface, small_font, banner["line"], TEXT, rect.centerx, rect.y + 66, alpha)
    return True


class GlitchIntro:
    def __init__(
        self,
        size,
        duration=ROLE_REVEAL_GLITCH_SECONDS,
        intensity=0.82,
        slice_count=28,
        jitter_strength=9,
        noise_amount=0.32,
        rgb_split=True,
        label="SIGNAL LOADING",
    ):
        self.size = size
        self.duration = duration
        self.intensity = intensity
        self.slice_count = slice_count
        self.jitter_strength = jitter_strength
        self.noise_amount = noise_amount
        self.rgb_split = rgb_split
        self.label = label
        self.started_at = None
        self._rng = random.Random()
        self._last_plan_at = -1.0
        self._slices = []
        self._blocks = []

    def start(self, now):
        self.started_at = now
        self._rng.seed(int(now * 1000))
        self._last_plan_at = -1.0
        self._slices = []
        self._blocks = []

    def is_finished(self, now):
        return self.started_at is not None and now - self.started_at >= self.duration

    def _progress(self, now):
        if self.started_at is None:
            return 0.0
        return max(0.0, min(1.0, (now - self.started_at) / self.duration))

    def _refresh_plan(self, progress, now):
        if now - self._last_plan_at < 0.045:
            return
        self._last_plan_at = now
        width, height = self.size
        remaining = max(0.12, 1.0 - progress)
        strength = self.intensity * (0.35 + remaining * 0.9)
        count = max(8, int(self.slice_count * (0.55 + remaining)))
        self._slices = []
        y = 0
        while y < height and len(self._slices) < count:
            slice_h = self._rng.randint(4, max(9, int(34 * strength)))
            if self._rng.random() < 0.35:
                slice_h = self._rng.randint(2, 6)
            max_shift = max(3, int(width * 0.065 * strength))
            shift = self._rng.randint(-max_shift, max_shift)
            visible = progress > 0.78 or self._rng.random() < 0.28 + progress * 0.8
            self._slices.append((y, min(slice_h, height - y), shift, visible))
            y += slice_h + self._rng.randint(0, max(2, int(12 * strength)))

        block_count = int(7 + 20 * self.noise_amount * strength)
        self._blocks = []
        for _ in range(block_count):
            block_w = self._rng.randint(10, max(18, int(85 * strength)))
            block_h = self._rng.randint(4, max(8, int(28 * strength)))
            x = self._rng.randint(0, max(0, width - block_w))
            y = self._rng.randint(0, max(0, height - block_h))
            shift = self._rng.randint(-max_shift, max_shift)
            color = self._rng.choice(
                (
                    (0, 255, 235, self._rng.randint(55, 145)),
                    (255, 35, 190, self._rng.randint(55, 145)),
                    (245, 205, 80, self._rng.randint(40, 110)),
                    (255, 255, 255, self._rng.randint(25, 80)),
                )
            )
            self._blocks.append((x, y, block_w, block_h, shift, color))

    def draw(self, target, source, now, font=None):
        progress = self._progress(now)
        self._refresh_plan(progress, now)
        width, height = self.size
        remaining = max(0.0, 1.0 - progress)
        burst = 0.25 + remaining * self.intensity
        shake = int(self.jitter_strength * burst)
        base_dx = self._rng.randint(-shake, shake) if shake else 0
        base_dy = self._rng.randint(-max(1, shake // 2), max(1, shake // 2)) if shake else 0

        target.fill((0, 0, 0))
        hidden_alpha = int(205 * max(0.0, 1.0 - progress * 1.45))
        if progress > 0.74:
            target.blit(source, (base_dx, base_dy))

        for y, slice_h, shift, visible in self._slices:
            if not visible:
                continue
            target.blit(source, (base_dx + shift, base_dy + y), pygame.Rect(0, y, width, slice_h))
            if self.rgb_split and self._rng.random() < 0.7:
                rgb_shift = max(2, abs(shift) // 2 + self._rng.randint(1, 7))
                target.blit(source, (base_dx + shift - rgb_shift, base_dy + y), pygame.Rect(0, y, width, slice_h), special_flags=pygame.BLEND_ADD)
                cyan = pygame.Surface((width, slice_h), pygame.SRCALPHA)
                cyan.fill((0, 220, 255, int(32 + 65 * burst)))
                target.blit(cyan, (base_dx + shift + rgb_shift, base_dy + y), special_flags=pygame.BLEND_RGBA_ADD)

        for x, y, block_w, block_h, shift, color in self._blocks:
            rect = pygame.Rect(x, y, block_w, block_h)
            if self._rng.random() < 0.55:
                target.blit(source, (x + shift, y), rect)
            block = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
            block.fill(color)
            target.blit(block, (x, y))

        static = pygame.Surface((width, height), pygame.SRCALPHA)
        line_alpha = int(18 + 55 * self.noise_amount * burst)
        for y in range(self._rng.randint(0, 3), height, 4):
            color = (255, 255, 255, line_alpha if y % 8 else line_alpha // 2)
            pygame.draw.line(static, color, (0, y), (width, y), 1)
        specks = int(95 * self.noise_amount * (0.35 + burst))
        for _ in range(specks):
            x = self._rng.randrange(width)
            y = self._rng.randrange(height)
            alpha = self._rng.randint(30, 105)
            pygame.draw.rect(static, (255, 255, 255, alpha), (x, y, self._rng.randint(1, 3), 1))
        target.blit(static, (0, 0))

        if hidden_alpha > 0:
            veil = pygame.Surface((width, height), pygame.SRCALPHA)
            veil.fill((0, 0, 0, hidden_alpha))
            target.blit(veil, (0, 0))

        if font and self.label:
            label = self.label
            if self._rng.random() < 0.22:
                label = "SIGNAL L0ADING"
            rendered = font.render(label, True, (180, 245, 235))
            rect = rendered.get_rect(center=(width // 2 + base_dx, height // 2 + 150 + base_dy))
            target.blit(rendered, rect)
            if self.rgb_split:
                red = font.render(label, True, (255, 55, 95))
                cyan = font.render(label, True, (40, 230, 255))
                target.blit(red, rect.move(-4, 0))
                target.blit(cyan, rect.move(4, 0), special_flags=pygame.BLEND_ADD)


def role_reveal_total_seconds(reveal):
    intro = reveal.get("glitch_intro") if reveal else None
    intro_seconds = intro.duration if intro else 0.0
    fallback_black_seconds = 0.0 if intro else ROLE_REVEAL_BLACK_SECONDS
    return (
        intro_seconds
        + ROLE_REVEAL_BLACK_HOLD_SECONDS
        + ROLE_REVEAL_SPOTLIGHT_SECONDS
        + fallback_black_seconds
        + ROLE_REVEAL_SECONDS
    )


def draw_role_reveal_intro_source(font, now):
    source = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    source.fill((2, 5, 12))

    for x in range(80, WINDOW_WIDTH, 140):
        pulse = int(22 + 14 * (0.5 + 0.5 * math.sin(now * 2.2 + x * 0.02)))
        pygame.draw.line(source, (18, 36, 56), (x, 95), (x, WINDOW_HEIGHT - 95), 1)
        pygame.draw.circle(source, (40, 150, 210), (x, 210), 3)
        pygame.draw.circle(source, (40, 150, 210), (x, 210), pulse, 1)
    for y in range(130, WINDOW_HEIGHT, 96):
        pygame.draw.line(source, (15, 31, 49), (70, y), (WINDOW_WIDTH - 70, y), 1)

    core = pygame.Rect(0, 0, 360, 112)
    core.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 18)
    pygame.draw.rect(source, (7, 13, 24), core, border_radius=10)
    pygame.draw.rect(source, (42, 56, 78), core, 1, 10)
    pygame.draw.line(source, (95, 230, 255), (core.x + 38, core.y + 2), (core.right - 38, core.y + 2), 2)
    draw_text(source, font, "ASSIGNING ROLES", TEXT, core.centerx, core.y + 36, center=True)
    draw_text(source, font, "PREPARING MISSION", MUTED, core.centerx, core.y + 70, center=True)
    return source


def draw_spotlight_reveal(surface, source, progress, now):
    progress = max(0.0, min(1.0, progress))
    eased = 1.0 - (1.0 - progress) ** 3
    max_radius = int(math.hypot(WINDOW_WIDTH, WINDOW_HEIGHT))
    radius = int(28 + (max_radius - 28) * eased)
    center = (
        WINDOW_WIDTH // 2 + int(math.sin(now * 18.0) * 8 * (1.0 - progress)),
        WINDOW_HEIGHT // 2 + int(math.cos(now * 15.0) * 6 * (1.0 - progress)),
    )

    surface.blit(source, (0, 0))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 255))
    pygame.draw.circle(overlay, (0, 0, 0, 0), center, radius)
    surface.blit(overlay, (0, 0))

    ring_alpha = int(170 * (1.0 - progress))
    if ring_alpha > 0:
        ring = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(ring, (95, 230, 255, ring_alpha), center, radius, 3)
        pygame.draw.circle(
            ring,
            (255, 35, 190, ring_alpha // 2),
            (center[0] - 4, center[1]),
            radius + 4,
            1,
        )
        surface.blit(ring, (0, 0))


def draw_role_reveal(surface, title_font, font, small_font, reveal, now):
    intro = reveal.get("glitch_intro")
    if intro and not intro.is_finished(now):
        intro.draw(surface, draw_role_reveal_intro_source(font, now), now, small_font)
        return

    intro_seconds = intro.duration if intro else 0.0
    transition_elapsed = max(0.0, now - reveal["started_at"] - intro_seconds)
    if transition_elapsed < ROLE_REVEAL_BLACK_HOLD_SECONDS:
        surface.fill((0, 0, 0))
        return

    spotlight_elapsed = transition_elapsed - ROLE_REVEAL_BLACK_HOLD_SECONDS
    if ROLE_REVEAL_SPOTLIGHT_SECONDS > 0 and spotlight_elapsed < ROLE_REVEAL_SPOTLIGHT_SECONDS:
        draw_spotlight_reveal(
            surface,
            surface.copy(),
            spotlight_elapsed / ROLE_REVEAL_SPOTLIGHT_SECONDS,
            now,
        )
        return

    elapsed = max(0.0, spotlight_elapsed - ROLE_REVEAL_SPOTLIGHT_SECONDS)
    if not intro:
        if elapsed < ROLE_REVEAL_BLACK_SECONDS:
            surface.fill((0, 0, 0))
            return
        elapsed -= ROLE_REVEAL_BLACK_SECONDS

    role = reveal["role"]
    specialty = reveal.get("specialty") or "Specialist"
    is_attacker = role == ROLE_ATTACKER
    role_label = "ATTACKER" if is_attacker else "DEFENDER"
    accent = ORANGE if is_attacker else GREEN
    mission = (
        "Disrupt systems and cause the most damage before time expires."
        if is_attacker
        else "Repair systems and recover the most infrastructure before time expires."
    )
    tip = "Press X for abilities after earning points." if is_attacker else "Press E near highlighted systems to repair."
    fade_in = max(0.0, min(1.0, elapsed / ROLE_REVEAL_FADE_SECONDS))
    exit_start = ROLE_REVEAL_FADE_SECONDS + ROLE_REVEAL_CARD_HOLD_SECONDS
    if elapsed > exit_start:
        fade_out = 1.0 - max(
            0.0,
            min(1.0, (elapsed - exit_start) / ROLE_REVEAL_EXIT_FADE_SECONDS),
        )
    else:
        fade_out = 1.0
    fade_in_eased = 1.0 - (1.0 - fade_in) ** 3
    fade_out_eased = fade_out * fade_out
    card_progress = fade_in_eased * fade_out_eased
    black_alpha = int(238 * fade_out_eased)

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((2, 5, 12, black_alpha))
    surface.blit(overlay, (0, 0))
    if card_progress <= 0:
        return

    card_alpha = int(255 * card_progress)
    card = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    card_shift = int((1.0 - fade_in_eased) * 18 - (1.0 - fade_out_eased) * 10)
    box = pygame.Rect(150, 135 + card_shift, 700, 380)
    glow = pygame.Surface((box.width + 36, box.height + 36), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*accent, int(42 * card_progress)), glow.get_rect(), border_radius=14)
    card.blit(glow, (box.x - 18, box.y - 18))
    pygame.draw.rect(card, (16, 24, 38, int(245 * card_progress)), box, border_radius=8)
    pygame.draw.rect(card, (*accent, card_alpha), box, 3, 8)
    pygame.draw.line(
        card,
        (42, 56, 78, card_alpha),
        (box.x + 45, box.y + 96),
        (box.right - 45, box.y + 96),
        1,
    )

    muted_color = (*MUTED, card_alpha)
    text_color = (*TEXT, card_alpha)
    accent_color = (*accent, card_alpha)
    yellow_color = (*YELLOW, card_alpha)
    draw_text(card, small_font, "ROLE ASSIGNED", muted_color, WINDOW_WIDTH // 2, box.y + 42, center=True)
    draw_text(card, title_font, role_label, accent_color, WINDOW_WIDTH // 2, box.y + 105, center=True)
    draw_text(card, font, specialty, text_color, WINDOW_WIDTH // 2, box.y + 165, center=True)
    draw_text(card, small_font, specialty_terminal_label(specialty), muted_color, WINDOW_WIDTH // 2, box.y + 196, center=True)

    draw_text(card, font, "Mission", yellow_color, box.x + 80, box.y + 250)
    for index, line in enumerate(wrapped_lines(small_font, mission, 520)):
        draw_text(card, small_font, line, text_color, box.x + 100, box.y + 286 + index * 22)
    draw_text(card, small_font, tip, accent_color, box.x + 100, box.y + 344)
    draw_text(card, small_font, "Enter / Space / Esc to skip", muted_color, WINDOW_WIDTH // 2, box.bottom - 30, center=True)
    surface.blit(card, (0, 0))


def draw_wrong_answer_flash(surface, effect, now):
    elapsed = now - effect["started_at"]
    if elapsed >= WRONG_ANSWER_EFFECT_SECONDS:
        return
    progress = max(0.0, min(1.0, elapsed / WRONG_ANSWER_EFFECT_SECONDS))
    alpha = int(150 * (1.0 - progress))
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 24, 48, alpha))
    surface.blit(overlay, (0, 0))


def shake_offset(effect, now):
    if not effect:
        return (0, 0)
    elapsed = now - effect["started_at"]
    if elapsed >= WRONG_ANSWER_EFFECT_SECONDS:
        return (0, 0)
    strength = int(WRONG_ANSWER_SHAKE_PIXELS * (1.0 - elapsed / WRONG_ANSWER_EFFECT_SECONDS))
    if strength <= 0:
        return (0, 0)
    return (random.randint(-strength, strength), random.randint(-strength, strength))


def draw_interact_highlight(surface, rect, font):
    highlight_rect = rect.inflate(18, 18)
    pygame.draw.rect(surface, YELLOW, highlight_rect, 3, 8)
    badge_rect = pygame.Rect(0, 0, 26, 22)
    badge_rect.center = (highlight_rect.right - 8, highlight_rect.top + 14)
    pygame.draw.rect(surface, PANEL, badge_rect, border_radius=4)
    pygame.draw.rect(surface, YELLOW, badge_rect, 2, 4)
    draw_text(surface, font, "E", YELLOW, badge_rect.centerx, badge_rect.centery, center=True)


def draw_terminal_sprite(
    surface,
    sprite,
    font,
    terminal,
    status_text,
    status_color,
    is_close,
    health=None,
):
    sprite_rect = sprite.get_rect(midbottom=(terminal["x"], terminal["y"] + 70))
    glow_rect = sprite_rect.inflate(44, 34)
    glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*status_color, 38), glow.get_rect())
    surface.blit(glow, glow_rect)

    shadow_rect = pygame.Rect(0, 0, sprite_rect.width + 54, 22)
    shadow_rect.center = (sprite_rect.centerx, sprite_rect.bottom - 5)
    pygame.draw.ellipse(surface, (2, 6, 12), shadow_rect)
    surface.blit(sprite, sprite_rect)

    draw_terminal_text(
        surface,
        font,
        (terminal["label"], status_text),
        status_color,
        sprite_rect.centerx,
        sprite_rect.top - 38,
    )
    if health is not None:
        bar_rect = pygame.Rect(0, 0, sprite_rect.width + 28, 8)
        bar_rect.center = (sprite_rect.centerx, sprite_rect.bottom + 10)
        fill_rect = bar_rect.copy()
        fill_rect.width = int(bar_rect.width * max(0, min(100, health)) / 100)
        pygame.draw.rect(surface, (8, 12, 20), bar_rect, border_radius=3)
        pygame.draw.rect(surface, status_color, fill_rect, border_radius=3)
    if is_close:
        draw_interact_highlight(surface, sprite_rect, font)


def draw_terminal_card(surface, font, terminal, status_text, status_color, is_close):
    rect = pygame.Rect(0, 0, TERMINAL_WIDTH, TERMINAL_HEIGHT)
    rect.center = (terminal["x"], terminal["y"])
    shadow = pygame.Rect(rect.x + 5, rect.y + 6, rect.width, rect.height)
    pygame.draw.rect(surface, (3, 7, 14), shadow, border_radius=7)
    pygame.draw.rect(surface, (28, 39, 56), rect, border_radius=5)
    pygame.draw.rect(surface, status_color, rect, 3, 5)
    if is_close:
        draw_interact_highlight(surface, rect, font)
    draw_terminal_text(
        surface,
        font,
        (terminal["label"], status_text),
        status_color,
        rect.centerx,
        rect.y + 16,
    )


def wrapped_lines(font, text, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def task_completed(task):
    return bool(task.get("completed")) if isinstance(task, dict) else bool(task)


def system_health_color(task, fallback):
    if not isinstance(task, dict) or "health" not in task:
        return fallback
    health = int(task.get("health", 0))
    if health >= 100:
        return GREEN
    if health <= 25:
        return RED
    if health <= 50:
        return ORANGE
    return YELLOW


def nearest_terminal(player, state):
    if not player:
        return None
    best_id = None
    best_distance = float("inf")
    for terminal_id, terminal in TERMINALS.items():
        dx = player["x"] - terminal["x"]
        dy = player["y"] - terminal["y"]
        distance = (dx * dx + dy * dy) ** 0.5
        if distance < best_distance:
            best_id = terminal_id
            best_distance = distance
    return best_id if best_distance <= INTERACTION_RANGE else None


def malware_target_options(state):
    return [
        terminal_id
        for terminal_id in NORMAL_TERMINALS
        if isinstance(state.get("tasks", {}).get(terminal_id), dict)
        and state["tasks"][terminal_id].get("health", 0) > 0
    ]


def guide_system_domain(terminal_id):
    domains = {
        "terminal_python": "Python Basics",
        "terminal_crypto": "Pwn / binary exploitation",
        "terminal_network": "Reverse Engineering",
    }
    return domains.get(terminal_id, "Cyber Defense")


def guide_tab_rects():
    tab_width = 132
    tab_height = 34
    gap = 10
    total_width = len(GUIDE_TABS) * tab_width + (len(GUIDE_TABS) - 1) * gap
    x = (WINDOW_WIDTH - total_width) // 2
    y = 142
    return {
        tab_id: pygame.Rect(x + index * (tab_width + gap), y, tab_width, tab_height)
        for index, (tab_id, _label) in enumerate(GUIDE_TABS)
    }


def guide_tab_at(position):
    for tab_id, rect in guide_tab_rects().items():
        if rect.collidepoint(position):
            return tab_id
    return None


def cheatsheet_content_height() -> int:
    section_height = sum(
        CHEATSHEET_SECTION_HEADER_HEIGHT
        + len(section["topics"]) * CHEATSHEET_TOPIC_HEIGHT
        + CHEATSHEET_SECTION_GAP
        for section in CHEATSHEET_TOPICS.values()
    )
    return section_height - CHEATSHEET_SECTION_GAP


def clamp_cheatsheet_scroll(scroll: int) -> int:
    max_scroll = max(0, cheatsheet_content_height() - CHEATSHEET_VIEWPORT_RECT.height)
    return max(0, min(scroll, max_scroll))


def draw_cheatsheet_section_header(
    surface: pygame.Surface,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    terminal_id: str,
    y: int,
) -> None:
    terminal = TERMINALS[terminal_id]
    section = CHEATSHEET_TOPICS[terminal_id]
    draw_text(surface, font, terminal["label"], terminal["color"], 6, y + 4)
    draw_text(surface, small_font, section["title"], TEXT, 6, y + 30)
    draw_wrapped_block(
        surface,
        small_font,
        section["summary"],
        MUTED,
        224,
        y + 6,
        surface.get_width() - 236,
        18,
    )


def draw_cheatsheet_topic_row(
    surface: pygame.Surface,
    small_font: pygame.font.Font,
    terminal_id: str,
    topic: str,
    description: str,
    y: int,
) -> None:
    row = pygame.Rect(
        4,
        y,
        surface.get_width() - 8,
        CHEATSHEET_TOPIC_HEIGHT - 6,
    )
    pygame.draw.rect(surface, (12, 19, 31), row, border_radius=6)
    pygame.draw.rect(surface, (48, 65, 91), row, 1, 6)
    color = TERMINALS[terminal_id]["color"]
    draw_text(surface, small_font, topic, color, row.x + 14, row.y + 10)
    draw_wrapped_block(
        surface,
        small_font,
        description,
        TEXT,
        row.x + 212,
        row.y + 9,
        row.width - 226,
        18,
    )


def draw_cheatsheet_content(
    surface: pygame.Surface,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    y = 0
    for terminal_id in NORMAL_TERMINALS:
        section = CHEATSHEET_TOPICS[terminal_id]
        draw_cheatsheet_section_header(surface, font, small_font, terminal_id, y)
        y += CHEATSHEET_SECTION_HEADER_HEIGHT
        for topic, description in section["topics"]:
            draw_cheatsheet_topic_row(
                surface,
                small_font,
                terminal_id,
                topic,
                description,
                y,
            )
            y += CHEATSHEET_TOPIC_HEIGHT
        y += CHEATSHEET_SECTION_GAP


def draw_cheatsheet_scrollbar(surface: pygame.Surface, scroll: int) -> None:
    content_height = cheatsheet_content_height()
    track = pygame.Rect(
        CHEATSHEET_VIEWPORT_RECT.right + 8,
        CHEATSHEET_VIEWPORT_RECT.y,
        6,
        CHEATSHEET_VIEWPORT_RECT.height,
    )
    pygame.draw.rect(surface, (8, 14, 24), track, border_radius=3)
    thumb_height = max(36, int(track.height * track.height / content_height))
    max_scroll = content_height - CHEATSHEET_VIEWPORT_RECT.height
    thumb_y = track.y + int((track.height - thumb_height) * scroll / max_scroll)
    thumb = pygame.Rect(track.x, thumb_y, track.width, thumb_height)
    pygame.draw.rect(surface, (80, 120, 175), thumb, border_radius=3)


def draw_cheatsheet_frame(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 215))
    surface.blit(overlay, (0, 0))
    pygame.draw.rect(surface, (17, 25, 39), CHEATSHEET_BOX_RECT, border_radius=10)
    pygame.draw.rect(surface, (80, 120, 175), CHEATSHEET_BOX_RECT, 2, 10)
    draw_text(
        surface,
        title_font,
        "Cybersecurity Cheatsheet",
        TEXT,
        CHEATSHEET_BOX_RECT.centerx,
        84,
        center=True,
    )
    draw_text(
        surface,
        small_font,
        "Mouse wheel or Arrow / Page keys to scroll",
        MUTED,
        CHEATSHEET_BOX_RECT.centerx,
        119,
        center=True,
    )
    draw_text(
        surface,
        small_font,
        "Esc to close",
        MUTED,
        CHEATSHEET_BOX_RECT.right - 82,
        78,
        center=True,
    )
    pygame.draw.rect(surface, (8, 14, 24), CHEATSHEET_VIEWPORT_RECT, border_radius=6)


def create_cheatsheet_content(
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> pygame.Surface:
    content_size = (
        CHEATSHEET_VIEWPORT_RECT.width - 18,
        cheatsheet_content_height(),
    )
    content = pygame.Surface(content_size, pygame.SRCALPHA)
    draw_cheatsheet_content(content, font, small_font)
    return content


def draw_cheatsheet(
    surface: pygame.Surface,
    title_font: pygame.font.Font,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    scroll: int,
) -> None:
    draw_cheatsheet_frame(surface, title_font, small_font)
    content = create_cheatsheet_content(font, small_font)
    clamped_scroll = clamp_cheatsheet_scroll(scroll)
    source = pygame.Rect(
        0,
        clamped_scroll,
        content.get_width(),
        CHEATSHEET_VIEWPORT_RECT.height,
    )
    surface.blit(content, CHEATSHEET_VIEWPORT_RECT.topleft, source)
    pygame.draw.rect(surface, (42, 56, 78), CHEATSHEET_VIEWPORT_RECT, 1, 6)
    draw_cheatsheet_scrollbar(surface, clamped_scroll)


def handle_cheatsheet_key(key: int, scroll: int) -> tuple[int, bool]:
    if key == pygame.K_ESCAPE:
        return scroll, False
    if key in (pygame.K_UP, pygame.K_w):
        scroll -= CHEATSHEET_SCROLL_STEP
    elif key in (pygame.K_DOWN, pygame.K_s):
        scroll += CHEATSHEET_SCROLL_STEP
    elif key in (pygame.K_PAGEUP, pygame.K_LEFT, pygame.K_a):
        scroll -= CHEATSHEET_VIEWPORT_RECT.height
    elif key in (
        pygame.K_PAGEDOWN,
        pygame.K_RIGHT,
        pygame.K_d,
        pygame.K_SPACE,
    ):
        scroll += CHEATSHEET_VIEWPORT_RECT.height
    elif key == pygame.K_HOME:
        scroll = 0
    elif key == pygame.K_END:
        scroll = cheatsheet_content_height()
    return clamp_cheatsheet_scroll(scroll), True


def draw_guide_panel(surface, rect, accent=None):
    pygame.draw.rect(surface, (12, 19, 31), rect, border_radius=8)
    pygame.draw.rect(surface, (48, 65, 91), rect, 1, 8)
    if accent:
        pygame.draw.line(
            surface,
            accent,
            (rect.x + 18, rect.y + 1),
            (rect.right - 18, rect.y + 1),
            2,
        )


def draw_guide_keycap(surface, small_font, rect, label):
    pygame.draw.rect(surface, (7, 13, 22), rect, border_radius=5)
    pygame.draw.rect(surface, (80, 120, 175), rect, 1, 5)
    draw_text(surface, small_font, label, TEXT, rect.centerx, rect.centery, center=True)


def draw_guide_system_row(surface, font, small_font, rect, terminal_id, state):
    terminal = TERMINALS[terminal_id]
    task = state.get("tasks", {}).get(terminal_id, {})
    health = task.get("health", 0) if isinstance(task, dict) else 0
    status = task.get("status", "UNKNOWN") if isinstance(task, dict) else "UNKNOWN"
    status_color = system_health_color(task, terminal["color"])
    draw_guide_panel(surface, rect)
    pygame.draw.circle(surface, terminal["color"], (rect.x + 28, rect.centery), 8)
    draw_text(surface, font, terminal["label"], TEXT, rect.x + 52, rect.y + 16)
    draw_text(surface, small_font, guide_system_domain(terminal_id), MUTED, rect.x + 52, rect.y + 43)
    status_x = rect.right - 88
    draw_text(surface, font, f"{health}%", status_color, status_x, rect.y + 18, center=True)
    draw_text(surface, small_font, status, status_color, status_x, rect.y + 44, center=True)
    bar = pygame.Rect(rect.x + 52, rect.bottom - 15, rect.width - 190, 6)
    fill = bar.copy()
    fill.width = int(bar.width * max(0, min(100, int(health))) / 100)
    pygame.draw.rect(surface, (5, 10, 18), bar, border_radius=3)
    pygame.draw.rect(surface, status_color, fill, border_radius=3)


def draw_guide_tabs(surface, font, small_font, active_tab):
    for tab_id, label in GUIDE_TABS:
        rect = guide_tab_rects()[tab_id]
        is_active = tab_id == active_tab
        fill = (23, 36, 56) if is_active else (9, 15, 25)
        border = YELLOW if is_active else (48, 65, 91)
        text_color = TEXT if is_active else MUTED
        pygame.draw.rect(surface, fill, rect, border_radius=6)
        pygame.draw.rect(surface, border, rect, 1, 6)
        draw_text(surface, font if is_active else small_font, label, text_color, rect.centerx, rect.centery, center=True)


def draw_guide_overview(surface, font, small_font, state, content_rect):
    draw_text(
        surface,
        font,
        "Repair or crash the lab before time runs out.",
        TEXT,
        content_rect.centerx,
        content_rect.y + 16,
        center=True,
    )

    row_y = content_rect.y + 66
    for index, terminal_id in enumerate(NORMAL_TERMINALS):
        rect = pygame.Rect(content_rect.x + 44, row_y + index * 94, content_rect.width - 88, 82)
        draw_guide_system_row(surface, font, small_font, rect, terminal_id, state)

    footer = pygame.Rect(content_rect.x + 100, content_rect.bottom - 58, content_rect.width - 200, 44)
    pygame.draw.rect(surface, (8, 14, 24), footer, border_radius=7)
    pygame.draw.rect(surface, (48, 65, 91), footer, 1, 7)
    draw_text(surface, small_font, "100% restores a system. 0% crashes it.", YELLOW, footer.centerx, footer.centery, center=True)


def draw_guide_roles(surface, font, small_font, content_rect):
    panel_gap = 28
    panel_width = (content_rect.width - panel_gap) // 2
    defender = pygame.Rect(content_rect.x, content_rect.y + 18, panel_width, 245)
    attacker = pygame.Rect(defender.right + panel_gap, defender.y, panel_width, defender.height)
    draw_guide_panel(surface, defender, GREEN)
    draw_guide_panel(surface, attacker, ORANGE)

    draw_text(surface, font, "Defender", GREEN, defender.x + 26, defender.y + 28)
    defender_lines = [
        "Solve repair questions.",
        "Raise system health.",
        "Restore systems to win.",
        "Specialty match: +5 repair.",
    ]
    for index, line in enumerate(defender_lines):
        draw_text(surface, small_font, line, TEXT, defender.x + 42, defender.y + 78 + index * 32)

    draw_text(surface, font, "Attacker", ORANGE, attacker.x + 26, attacker.y + 28)
    attacker_lines = [
        "Solve attack questions.",
        "Earn Attack Points.",
        "Spend AP on abilities.",
        "Specialty match: bonus malware.",
    ]
    for index, line in enumerate(attacker_lines):
        draw_text(surface, small_font, line, TEXT, attacker.x + 42, attacker.y + 78 + index * 32)

    note = pygame.Rect(content_rect.x + 90, content_rect.bottom - 88, content_rect.width - 180, 52)
    pygame.draw.rect(surface, (8, 14, 24), note, border_radius=7)
    pygame.draw.rect(surface, (48, 65, 91), note, 1, 7)
    draw_text(surface, small_font, "Roles are assigned after difficulty voting.", MUTED, note.centerx, note.centery, center=True)


def draw_guide_defender(surface, font, small_font, content_rect):
    banner = pygame.Rect(content_rect.x + 80, content_rect.y + 16, content_rect.width - 160, 52)
    pygame.draw.rect(surface, (8, 14, 24), banner, border_radius=7)
    pygame.draw.rect(surface, GREEN, banner, 1, 7)
    draw_text(surface, font, "Restore systems by solving repair questions.", GREEN, banner.centerx, banner.centery, center=True)

    rows = [
        ("REPAIR", "Press E near a highlighted system."),
        ("ANSWER", "Use 1-4, or type and press Enter."),
        ("BONUS", "Matching specialty gives +5 repair."),
    ]
    start_y = content_rect.y + 96
    for index, (label, description) in enumerate(rows):
        rect = pygame.Rect(content_rect.x + 90, start_y + index * 78, content_rect.width - 180, 62)
        draw_guide_panel(surface, rect)
        draw_text(surface, font, label, GREEN, rect.x + 28, rect.y + 20)
        draw_text(surface, small_font, description, TEXT, rect.x + 190, rect.y + 26)

    footer = pygame.Rect(content_rect.x + 130, content_rect.bottom - 42, content_rect.width - 260, 44)
    pygame.draw.rect(surface, (8, 14, 24), footer, border_radius=7)
    pygame.draw.rect(surface, (48, 65, 91), footer, 1, 7)
    draw_text(surface, small_font, "Win by restoring every system to 100%.", MUTED, footer.centerx, footer.centery, center=True)


def draw_guide_controls(surface, font, small_font, content_rect):
    groups = [
        ("Movement", [("WASD", "Move"), ("Arrows", "Move")]),
        ("Lobby", [("Space", "Ready"), ("1-3", "Choose / vote")]),
        ("Challenge", [("E", "Interact"), ("1-4", "Answer"), ("Enter", "Submit")]),
        ("Menus", [("X", "Attacker abilities"), ("Esc", "Close")]),
    ]
    card_w = (content_rect.width - 28) // 2
    card_h = 158
    for index, (title, rows) in enumerate(groups):
        col = index % 2
        row = index // 2
        rect = pygame.Rect(
            content_rect.x + col * (card_w + 28),
            content_rect.y + 18 + row * (card_h + 22),
            card_w,
            card_h,
        )
        draw_guide_panel(surface, rect, YELLOW if title in ("Challenge", "Menus") else (70, 150, 255))
        draw_text(surface, font, title, YELLOW, rect.x + 24, rect.y + 20)
        for row_index, (key, action) in enumerate(rows):
            y = rect.y + 58 + row_index * 32
            key_rect = pygame.Rect(rect.x + 24, y - 6, 78, 26)
            draw_guide_keycap(surface, small_font, key_rect, key)
            draw_text(surface, small_font, action, TEXT, key_rect.right + 18, y)


def draw_guide_attacker(surface, font, small_font, content_rect):
    banner = pygame.Rect(content_rect.x + 80, content_rect.y + 16, content_rect.width - 160, 52)
    pygame.draw.rect(surface, (8, 14, 24), banner, border_radius=7)
    pygame.draw.rect(surface, ORANGE, banner, 1, 7)
    draw_text(surface, font, "Earn AP by solving attack questions.", ORANGE, banner.centerx, banner.centery, center=True)

    rows = [
        ("BLACKOUT", "1 AP", "Freezes and blinds one defender for 10s."),
        ("FALSE_ALERT", "2 AP", "Healthy system -> critical."),
        ("MALWARE_INJECTION", "3 AP", "Damage a chosen system."),
    ]
    start_y = content_rect.y + 96
    for index, (ability, cost, description) in enumerate(rows):
        rect = pygame.Rect(content_rect.x + 90, start_y + index * 78, content_rect.width - 180, 62)
        draw_guide_panel(surface, rect)
        draw_text(surface, font, ability, ORANGE, rect.x + 26, rect.y + 20)
        draw_text(surface, small_font, cost, YELLOW, rect.x + 292, rect.y + 26)
        draw_text(surface, small_font, description, TEXT, rect.x + 350, rect.y + 26)

    footer = pygame.Rect(content_rect.x + 120, content_rect.bottom - 42, content_rect.width - 240, 44)
    pygame.draw.rect(surface, (8, 14, 24), footer, border_radius=7)
    pygame.draw.rect(surface, (48, 65, 91), footer, 1, 7)
    draw_text(surface, small_font, "Matching specialty banks extra malware damage.", MUTED, footer.centerx, footer.centery, center=True)


def draw_lab_guide(surface, title_font, font, small_font, state, active_tab):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 205))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(70, 54, 860, 580)
    pygame.draw.rect(surface, (17, 25, 39), box, border_radius=10)
    pygame.draw.rect(surface, (80, 120, 175), box, 2, 10)
    pygame.draw.line(surface, (42, 56, 78), (box.x + 30, box.y + 78), (box.right - 30, box.y + 78), 1)

    draw_text(surface, title_font, "Lab Guide", TEXT, box.centerx, box.y + 30, center=True)
    draw_text(
        surface,
        small_font,
        "Player command manual",
        MUTED,
        box.centerx,
        box.y + 58,
        center=True,
    )
    draw_text(surface, small_font, "Esc to close", MUTED, box.right - 82, box.y + 24, center=True)

    lab_health = max(0, min(100, int(state.get("global_progress", 0) * 100)))
    health_color = GREEN if lab_health >= 75 else YELLOW if lab_health >= 30 else RED
    status_rect = pygame.Rect(box.x + 32, box.y + 22, 104, 30)
    pygame.draw.rect(surface, (8, 14, 24), status_rect, border_radius=5)
    pygame.draw.rect(surface, health_color, status_rect, 1, 5)
    draw_text(surface, small_font, f"LAB {lab_health}%", health_color, status_rect.centerx, status_rect.centery, center=True)

    draw_guide_tabs(surface, font, small_font, active_tab)
    content_rect = pygame.Rect(box.x + 52, box.y + 130, box.width - 104, box.height - 170)

    if active_tab == "roles":
        draw_guide_roles(surface, font, small_font, content_rect)
    elif active_tab == "defender":
        draw_guide_defender(surface, font, small_font, content_rect)
    elif active_tab == "controls":
        draw_guide_controls(surface, font, small_font, content_rect)
    elif active_tab == "attacker":
        draw_guide_attacker(surface, font, small_font, content_rect)
    else:
        draw_guide_overview(surface, font, small_font, state, content_rect)
def local_player_won(result, player):
    social_role = player.get("social_role", "")
    if result == RESULT_DEFENDERS_WIN:
        return social_role != ROLE_ATTACKER
    if result == RESULT_ATTACKERS_WIN:
        return social_role == ROLE_ATTACKER
    return False


def game_over_title(result, ended_by_timer):
    if result == RESULT_DEFENDERS_WIN:
        return "DEFENDERS HELD THE LAB" if ended_by_timer else "DEFENDERS RESTORED THE LAB"
    if ended_by_timer:
        return "ATTACKERS OVERRAN THE LAB"
    return "ATTACKERS CRASHED THE LAB"


class EndScreenAnimation:
    def __init__(
        self,
        size,
        mode,
        duration=GAME_OVER_ANIMATION_SECONDS,
        intensity=1.0,
        particle_count=150,
        speed=1.0,
    ):
        self.size = size
        self.mode = mode
        self.duration = duration
        self.intensity = intensity
        self.particle_count = particle_count
        self.speed = speed
        self.started_at = None
        self._rng = random.Random()
        self._confetti = []
        self._last_glitch_at = -1.0
        self._glitch_slices = []
        self._glitch_blocks = []

    def start(self, now):
        self.started_at = now
        self._rng.seed(int(now * 1000))
        self._last_glitch_at = -1.0
        self._glitch_slices = []
        self._glitch_blocks = []
        self._confetti = []
        if self.mode == "victory":
            self._spawn_confetti()

    def transition_progress(self, now):
        if self.started_at is None:
            return 0.0
        elapsed = max(0.0, now - self.started_at)
        return max(0.0, min(1.0, elapsed / GAME_OVER_TRANSITION_SECONDS))

    def _spawn_confetti(self):
        width, height = self.size
        palette = (
            (95, 230, 255),
            (65, 220, 130),
            (245, 205, 80),
            (255, 105, 185),
            (255, 165, 80),
            (170, 130, 255),
            (255, 255, 255),
        )
        for index in range(self.particle_count):
            side = -1 if index % 2 == 0 else 1
            x = -30 if side < 0 else width + 30
            y = self._rng.uniform(65, height * 0.62)
            speed_x = self._rng.uniform(210, 520) * -side * self.speed
            speed_y = self._rng.uniform(-260, 95) * self.speed
            size = self._rng.randint(4, 11)
            shape = self._rng.choice(("rect", "line", "circle"))
            self._confetti.append(
                {
                    "x": x + self._rng.uniform(-80, 35) * side,
                    "y": y,
                    "vx": speed_x,
                    "vy": speed_y,
                    "size": size,
                    "angle": self._rng.uniform(0, math.tau),
                    "spin": self._rng.uniform(-7.0, 7.0),
                    "color": self._rng.choice(palette),
                    "shape": shape,
                    "delay": self._rng.uniform(0.0, 0.45),
                }
            )

    def _draw_confetti(self, surface, elapsed):
        width, height = self.size
        fade = max(0.0, min(1.0, (self.duration - elapsed) / 1.4))
        for piece in self._confetti:
            active_time = (elapsed - piece["delay"]) * self.speed
            if active_time < 0:
                continue
            gravity = 220 * self.intensity
            drift = math.sin(active_time * 4.2 + piece["angle"]) * 28
            x = piece["x"] + piece["vx"] * active_time + drift
            y = piece["y"] + piece["vy"] * active_time + 0.5 * gravity * active_time * active_time
            if y > height + 40 or x < -90 or x > width + 90:
                continue
            alpha = int(230 * fade)
            color = (*piece["color"], alpha)
            size = piece["size"]
            angle = piece["angle"] + piece["spin"] * active_time
            if piece["shape"] == "circle":
                pygame.draw.circle(surface, color, (int(x), int(y)), max(2, size // 2))
            elif piece["shape"] == "line":
                dx = math.cos(angle) * size * 1.5
                dy = math.sin(angle) * size * 1.5
                pygame.draw.line(surface, color, (x - dx, y - dy), (x + dx, y + dy), 2)
            else:
                rect = pygame.Rect(0, 0, size * 2, size)
                rect.center = (int(x), int(y))
                pygame.draw.rect(surface, color, rect, border_radius=2)

    def _refresh_loss_glitch(self, now, elapsed):
        if now - self._last_glitch_at < 0.055:
            return
        self._last_glitch_at = now
        width, height = self.size
        pulse = 0.65 + 0.35 * math.sin(elapsed * 11.0)
        strength = self.intensity * pulse
        slice_count = max(10, int(18 * strength))
        self._glitch_slices = []
        for _ in range(slice_count):
            y = self._rng.randint(0, height - 2)
            h = self._rng.randint(2, max(5, int(22 * strength)))
            shift = self._rng.randint(-int(48 * strength), int(48 * strength))
            alpha = self._rng.randint(35, 120)
            self._glitch_slices.append((y, h, shift, alpha))

        block_count = max(4, int(14 * strength))
        self._glitch_blocks = []
        for _ in range(block_count):
            block_w = self._rng.randint(24, 150)
            block_h = self._rng.randint(4, 34)
            x = self._rng.randint(0, max(0, width - block_w))
            y = self._rng.randint(70, max(70, height - block_h))
            color = self._rng.choice(
                (
                    (120, 0, 18, self._rng.randint(70, 160)),
                    (190, 20, 35, self._rng.randint(55, 135)),
                    (55, 0, 8, self._rng.randint(100, 190)),
                    (255, 40, 55, self._rng.randint(35, 95)),
                )
            )
            self._glitch_blocks.append((x, y, block_w, block_h, color))

    def _draw_loss_glitch(self, surface, elapsed, now):
        width, height = self.size
        self._refresh_loss_glitch(now, elapsed)
        layer = pygame.Surface((width, height), pygame.SRCALPHA)
        layer.fill((20, 0, 5, int(35 + 40 * self.intensity)))
        for y, h, shift, alpha in self._glitch_slices:
            color = (210, 20, 42, alpha)
            pygame.draw.rect(layer, color, pygame.Rect(max(0, shift), y, width, h))
            if self._rng.random() < 0.45:
                pygame.draw.rect(layer, (40, 0, 8, alpha + 40), pygame.Rect(0, y + h, width, 2))
        for x, y, block_w, block_h, color in self._glitch_blocks:
            pygame.draw.rect(layer, color, pygame.Rect(x, y, block_w, block_h))
        for y in range(self._rng.randint(0, 5), height, 6):
            pygame.draw.line(layer, (120, 0, 18, 42), (0, y), (width, y), 1)
        if self._rng.random() < 0.35:
            tear_y = self._rng.randint(95, height - 80)
            pygame.draw.rect(layer, (255, 20, 35, 120), pygame.Rect(0, tear_y, width, 3))
        surface.blit(layer, (self._rng.randint(-4, 4), self._rng.randint(-2, 2)))

    def draw(self, surface, now):
        if self.started_at is None:
            self.start(now)
        elapsed = max(0.0, now - self.started_at)
        if self.mode == "victory":
            layer = pygame.Surface(self.size, pygame.SRCALPHA)
            self._draw_confetti(layer, min(elapsed, self.duration))
            surface.blit(layer, (0, 0))
        else:
            self._draw_loss_glitch(surface, min(elapsed, self.duration), now)


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    uri = server_uri(host)
    network = NetworkClient(uri)
    network.start()

    try:
        pygame.mixer.pre_init(22050, -16, 1, 512)
    except pygame.error:
        pass
    pygame.init()
    pygame.key.set_repeat(250, 45)
    display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("BREACH Multiplayer MVP")
    screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    sounds = build_game_sounds()
    sprites = load_player_sprites()
    terminal_sprites = load_terminal_sprites()
    clock = pygame.time.Clock()
    title_font = make_font(TITLE_FONT_CANDIDATES, 36, bold=True)
    font = make_font(UI_FONT_CANDIDATES, 20)
    small_font = make_font(UI_FONT_CANDIDATES, 15)
    screen_name = "name"
    name = "Player"
    connected = False
    player_id = None
    selected_role = ""
    state = {
        "players": {},
        "tasks": {terminal_id: False for terminal_id in TERMINALS},
        "timer": 200,
        "status": "lobby",
        "minimum_players": 2,
        "difficulties": ("easy", "medium", "hard"),
        "difficulty_votes": {"easy": 0, "medium": 0, "hard": 0},
        "selected_difficulty": None,
        "vote_result_seconds": 3,
        "vote_result_tied": False,
        "vote_result_tied_options": [],
        "phase": "lobby",
        "result": None,
        "game_over_reason": "",
        "global_progress": 0,
        "score": {
            "baseline_health": 50,
            "average_health": 50,
            "net_health": 0,
            "defender_score": 0,
            "attacker_score": 0,
        },
        "learning_insights": {"self": None, "players": []},
        "effects": {"blackout_remaining": 0, "false_alert": None},
    }
    popup = None
    result_popup = None
    pending_task = None
    answer = ""
    guide_open = False
    guide_tab = "overview"
    cheatsheet_open = False
    cheatsheet_scroll = 0
    ability_menu_open = False
    ability_target_mode = ""
    role_reveal = None
    role_reveal_seen = False
    objective_banner = None
    wrong_answer_effect = None
    floating_feedback = []
    system_reactions = []
    report_open = False
    report_page = 0
    end_screen_animation = None
    end_screen_animation_key = None
    blackout_snapshot = None
    blackout_was_active = False
    notice = f"Connecting to {uri}..."
    notice_color = MUTED
    notice_until = 0
    last_move_sent = 0.0
    player_visuals = {}
    last_frame_time = time.monotonic()
    running = True

    while running:
        now = time.monotonic()
        dt = min(0.05, now - last_frame_time)
        last_frame_time = now
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif role_reveal and now - role_reveal["started_at"] < role_reveal_total_seconds(role_reveal):
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                    pygame.K_ESCAPE,
                ):
                    role_reveal["started_at"] = now - role_reveal_total_seconds(role_reveal)
            elif event.type == pygame.MOUSEWHEEL and cheatsheet_open:
                cheatsheet_scroll = clamp_cheatsheet_scroll(
                    cheatsheet_scroll - event.y * CHEATSHEET_SCROLL_STEP
                )
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if guide_open:
                    if GUIDE_BUTTON_RECT.collidepoint(event.pos):
                        guide_open = False
                        continue
                    if CHEATSHEET_BUTTON_RECT.collidepoint(event.pos):
                        guide_open = False
                        cheatsheet_open = True
                        cheatsheet_scroll = 0
                        continue
                    clicked_tab = guide_tab_at(event.pos)
                    if clicked_tab:
                        guide_tab = clicked_tab
                    continue
                if cheatsheet_open:
                    if CHEATSHEET_BUTTON_RECT.collidepoint(event.pos):
                        cheatsheet_open = False
                    elif GUIDE_BUTTON_RECT.collidepoint(event.pos):
                        cheatsheet_open = False
                        guide_open = True
                        guide_tab = "overview"
                    continue
                if state.get("status") in ("win", "loss") and report_open:
                    total_pages = report_page_count(state)
                    if REPORT_CLOSE_RECT.collidepoint(event.pos):
                        report_open = False
                    elif REPORT_PREV_RECT.collidepoint(event.pos):
                        report_page = max(0, report_page - 1)
                    elif REPORT_NEXT_RECT.collidepoint(event.pos):
                        report_page = min(total_pages - 1, report_page + 1)
                    continue
                if state.get("status") in ("win", "loss") and REPORT_BUTTON_RECT.collidepoint(event.pos):
                    report_open = True
                    report_page = 0
                    continue
                if pending_task:
                    continue
                if CHEATSHEET_BUTTON_RECT.collidepoint(event.pos):
                    cheatsheet_open = not cheatsheet_open
                    cheatsheet_scroll = 0
                    guide_open = False
                elif GUIDE_BUTTON_RECT.collidepoint(event.pos):
                    guide_open = not guide_open
                    guide_tab = "overview"
                    cheatsheet_open = False
            elif event.type == pygame.KEYDOWN:
                if cheatsheet_open:
                    cheatsheet_scroll, cheatsheet_open = handle_cheatsheet_key(
                        event.key,
                        cheatsheet_scroll,
                    )
                    continue
                if state["status"] in ("win", "loss") and report_open:
                    total_pages = report_page_count(state)
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        report_open = False
                    elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_PAGEUP):
                        report_page = max(0, report_page - 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_PAGEDOWN, pygame.K_SPACE):
                        report_page = min(total_pages - 1, report_page + 1)
                    elif event.key == pygame.K_HOME:
                        report_page = 0
                    elif event.key == pygame.K_END:
                        report_page = total_pages - 1
                    elif event.key == pygame.K_r:
                        network.send({"type": "reset_game"})
                        selected_role = ""
                        report_open = False
                        report_page = 0
                        end_screen_animation = None
                        end_screen_animation_key = None
                        set_player_fixing(player_visuals, player_id, False, now)
                        popup = None
                        result_popup = None
                        pending_task = None
                elif event.key == pygame.K_ESCAPE:
                    if ability_menu_open:
                        ability_menu_open = False
                        ability_target_mode = ""
                    elif guide_open:
                        guide_open = False
                    elif result_popup:
                        result_popup = None
                    elif pending_task:
                        notice = "Challenge is still generating..."
                        notice_color = YELLOW
                        notice_until = now + 2
                    elif popup:
                        network.send({"type": "cancel_interaction"})
                        set_player_fixing(player_visuals, player_id, False, now)
                        popup = None
                        answer = ""
                    else:
                        running = False
                elif state["status"] in ("win", "loss") and event.key == pygame.K_r:
                    network.send({"type": "reset_game"})
                    selected_role = ""
                    report_open = False
                    report_page = 0
                    end_screen_animation = None
                    end_screen_animation_key = None
                    set_player_fixing(player_visuals, player_id, False, now)
                    popup = None
                    result_popup = None
                    pending_task = None
                elif result_popup:
                    if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                        result_popup = None
                elif pending_task:
                    pass
                elif popup:
                    if event.key == pygame.K_RETURN:
                        network.send(
                            {
                                "type": "submit_answer",
                                "terminal_id": popup["terminal_id"],
                                "answer": answer,
                            }
                        )
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                        index = event.key - pygame.K_1
                        options = popup.get("options", [])
                        if index < len(options):
                            answer = chr(ord("a") + index)
                            network.send(
                                {
                                    "type": "submit_answer",
                                    "terminal_id": popup["terminal_id"],
                                    "answer": answer,
                                }
                            )
                    elif event.key == pygame.K_BACKSPACE:
                        answer = answer[:-1]
                    elif event.unicode.isprintable() and len(answer) < 60:
                        answer += event.unicode
                elif screen_name == "name":
                    if event.key == pygame.K_RETURN and connected:
                        network.send({"type": "join", "name": name})
                        screen_name = "role"
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode.isprintable() and len(name) < 20:
                        if name == "Player":
                            name = ""
                        name += event.unicode
                elif screen_name == "role" and event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                ):
                    roles = {
                        pygame.K_1: "Python Engineer",
                        pygame.K_2: "Cryptographer",
                        pygame.K_3: "Network Analyst",
                    }
                    requested_role = roles[event.key]
                    if requested_role in taken_specialties(state, player_id):
                        notice = f"{requested_role} is already taken."
                        notice_color = RED
                        notice_until = now + 2
                    else:
                        selected_role = requested_role
                        network.send({"type": "select_role", "role": selected_role})
                        screen_name = "lobby"
                elif screen_name == "lobby" and event.key == pygame.K_SPACE:
                    player = state["players"].get(player_id, {})
                    network.send(
                        {"type": "ready", "ready": not player.get("ready", False)}
                    )
                elif screen_name == "vote" and event.key in (
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                ):
                    difficulties = {
                        pygame.K_1: "easy",
                        pygame.K_2: "medium",
                        pygame.K_3: "hard",
                    }
                    network.send(
                        {
                            "type": "difficulty_vote",
                            "difficulty": difficulties[event.key],
                        }
                    )
                elif screen_name == "game" and ability_menu_open:
                    if event.key == pygame.K_x:
                        ability_menu_open = False
                        ability_target_mode = ""
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if ability_target_mode == "malware":
                            options = malware_target_options(state)
                            if index < len(options):
                                network.send(
                                    {
                                        "type": "use_ability",
                                        "ability": "MALWARE_INJECTION",
                                        "terminal_id": options[index],
                                    }
                                )
                                ability_menu_open = False
                                ability_target_mode = ""
                        elif index == 0:
                            network.send({"type": "use_ability", "ability": "BLACKOUT"})
                            ability_menu_open = False
                        elif index == 1:
                            network.send({"type": "use_ability", "ability": "FALSE_ALERT"})
                            ability_menu_open = False
                        elif index == 2:
                            ability_target_mode = "malware"
                    elif ability_target_mode == "malware" and event.key == pygame.K_BACKSPACE:
                        ability_target_mode = ""
                elif screen_name == "game" and event.key == pygame.K_e:
                    player = state["players"].get(player_id)
                    terminal_id = nearest_terminal(player, state)
                    if terminal_id:
                        network.send({"type": "interact", "terminal_id": terminal_id})
                        set_player_fixing(player_visuals, player_id, True, now)
                        me = state["players"].get(player_id, {})
                        terminal_label = TERMINALS.get(terminal_id, {}).get("label", "System")
                        if me.get("social_role") == ROLE_ATTACKER:
                            action_label = "Generating attack challenge"
                        else:
                            action_label = "Generating repair challenge"
                        pending_task = {
                            "terminal_id": terminal_id,
                            "label": terminal_label,
                            "action": action_label,
                            "started_at": now,
                        }
                    else:
                        notice = "Move within 80 pixels of a terminal."
                        notice_color = YELLOW
                        notice_until = now + 2
                elif screen_name == "game" and event.key == pygame.K_z:
                    if state.get("phase") == "playing":
                        network.send({"type": "demo_end_match"})
                        notice = "Demo speedrun: ending match..."
                        notice_color = YELLOW
                        notice_until = now + 2
                elif screen_name == "game" and event.key == pygame.K_x:
                    me = state["players"].get(player_id, {})
                    if me.get("social_role") == ROLE_ATTACKER and me.get("life_state") == "alive":
                        ability_menu_open = not ability_menu_open
                        ability_target_mode = ""

        while True:
            try:
                message = network.incoming.get_nowait()
            except queue.Empty:
                break

            message_type = message.get("type")
            if message_type == "connection":
                connected = message["connected"]
                if not connected:
                    pending_task = None
                    wrong_answer_effect = None
                    set_player_fixing(player_visuals, player_id, False, now)
                notice = (
                    f"Connected to {uri}"
                    if connected
                    else f"Disconnected: {message.get('message', 'server unavailable')}"
                )
                notice_color = GREEN if connected else RED
                notice_until = now + 4
            elif message_type == "welcome":
                player_id = message["player_id"]
            elif message_type == "state_update":
                state = message["state"]
                phase = state.get("phase", state["status"])
                me = state["players"].get(player_id, {})
                server_specialty = me.get("specialty", "")
                if server_specialty != selected_role:
                    selected_role = server_specialty
                if phase != "playing" and pending_task:
                    pending_task = None
                    set_player_fixing(player_visuals, player_id, False, now)
                if phase == "playing":
                    screen_name = "game"
                    assigned_role = me.get("social_role", "")
                    if (
                        not role_reveal_seen
                        and assigned_role in (ROLE_DEFENDER, ROLE_ATTACKER)
                    ):
                        glitch_intro = GlitchIntro((WINDOW_WIDTH, WINDOW_HEIGHT))
                        glitch_intro.start(now)
                        role_reveal = {
                            "started_at": now,
                            "role": assigned_role,
                            "specialty": me.get("specialty", ""),
                            "glitch_intro": glitch_intro,
                        }
                        role_reveal_seen = True
                        guide_open = False
                        cheatsheet_open = False
                        ability_menu_open = False
                        ability_target_mode = ""
                        pending_task = None
                        set_player_fixing(player_visuals, player_id, False, now)
                elif phase == "vote_results":
                    screen_name = "vote_results"
                elif phase == "voting":
                    screen_name = "vote"
                elif phase == "lobby" and screen_name in (
                    "game",
                    "vote",
                    "vote_results",
                    "lobby",
                ):
                    screen_name = "role" if me.get("joined") and not server_specialty else "lobby"
                if phase != "playing":
                    role_reveal = None
                    role_reveal_seen = False
                    wrong_answer_effect = None
                    objective_banner = None
                if phase not in ("game_over", "win", "loss"):
                    end_screen_animation = None
                    end_screen_animation_key = None
            elif message_type == "task_opened":
                pending_task = None
                popup = message
                answer = ""
                set_player_fixing(player_visuals, player_id, True, now)
            elif message_type == "task_result":
                notice = message["message"]
                notice_color = GREEN if message["correct"] else RED
                notice_until = now + 3
                add_floating_feedback(floating_feedback, message.get("impact"), state, player_id, now)
                add_system_reaction(system_reactions, message.get("impact"), now)
                if message.get("correct"):
                    play_sound(sounds, "correct")
                else:
                    play_sound(sounds, "wrong")
                    wrong_answer_effect = {"started_at": now}
                set_player_fixing(player_visuals, player_id, False, now)
                result_popup = message
                popup = None
                pending_task = None
                answer = ""
            elif message_type == "hint":
                notice = message["message"]
                notice_color = GREEN
                notice_until = now + 5
            elif message_type == "ability_result":
                notice = message["message"]
                notice_color = ORANGE
                notice_until = now + 4
                add_floating_feedback(floating_feedback, message.get("impact"), state, player_id, now)
                add_system_reaction(system_reactions, message.get("impact"), now)
                play_sound(sounds, "ability")
            elif message_type == "error":
                notice = message["message"]
                notice_color = RED
                notice_until = now + 3
                pending_task = None
                set_player_fixing(player_visuals, player_id, False, now)
            elif message_type == "game_over":
                was_game_over = state.get("status") in ("win", "loss")
                previous_result = state.get("result")
                state["result"] = message["result"]
                state["phase"] = "game_over"
                state["status"] = "win" if message["result"] == RESULT_DEFENDERS_WIN else "loss"
                if not was_game_over or previous_result != message["result"]:
                    report_open = False
                    report_page = 0
                    end_screen_animation = None
                    end_screen_animation_key = None
                    me = state.get("players", {}).get(player_id, {})
                    play_sound(
                        sounds,
                        "victory" if local_player_won(message["result"], me) else "defeat",
                    )
                set_player_fixing(player_visuals, player_id, False, now)
                popup = None
                result_popup = None
                pending_task = None
                role_reveal = None
                wrong_answer_effect = None
                objective_banner = None

        reveal_active = bool(
            role_reveal and now - role_reveal["started_at"] < role_reveal_total_seconds(role_reveal)
        )
        if (
            screen_name == "game"
            and not popup
            and not pending_task
            and not reveal_active
            and state.get("phase") == "playing"
        ):
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (
                keys[pygame.K_a] or keys[pygame.K_LEFT]
            )
            dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (
                keys[pygame.K_w] or keys[pygame.K_UP]
            )
            if (dx or dy) and now - last_move_sent >= 1 / 30:
                if dx and dy:
                    dx *= 0.707
                    dy *= 0.707
                network.send(
                    {
                        "type": "move",
                        "dx": dx * PLAYER_SPEED,
                        "dy": dy * PLAYER_SPEED,
                    }
                )
                last_move_sent = now
        update_player_visuals(player_visuals, state["players"], dt, now)

        screen.fill(BG)
        if screen_name == "name":
            draw_text(
                screen, title_font, "BREACH", TEXT, WINDOW_WIDTH // 2, 180, center=True
            )
            draw_text(
                screen,
                font,
                "Cyber Defense Lab",
                MUTED,
                WINDOW_WIDTH // 2,
                225,
                center=True,
            )
            draw_text(screen, font, "Player name:", TEXT, 300, 310)
            pygame.draw.rect(screen, PANEL, (300, 345, 400, 48), border_radius=5)
            pygame.draw.rect(screen, (75, 100, 140), (300, 345, 400, 48), 2, 5)
            draw_text(screen, font, name or "", TEXT, 315, 357)
            draw_typing_indicator(screen, font, name or "", 315, 357, TEXT, now)
            prompt = "Press Enter to continue" if connected else "Waiting for server..."
            draw_text(
                screen, font, prompt, MUTED, WINDOW_WIDTH // 2, 440, center=True
            )

        elif screen_name == "role":
            draw_text(
                screen,
                title_font,
                "Choose Your Specialty",
                TEXT,
                WINDOW_WIDTH // 2,
                150,
                center=True,
            )
            roles = list(ROLE_COLORS.items())
            taken = taken_specialties(state, player_id)
            for index, (role, color) in enumerate(roles, start=1):
                y = 245 + (index - 1) * 90
                is_taken = role in taken
                border_color = MUTED if is_taken else color
                text_color = MUTED if is_taken else TEXT
                pygame.draw.rect(screen, PANEL, (260, y, 480, 62), border_radius=6)
                pygame.draw.rect(screen, border_color, (260, y, 480, 62), 2, 6)
                draw_text(screen, font, f"{index}  {role}", text_color, 290, y + 18)
                if is_taken:
                    draw_text(screen, small_font, "TAKEN", RED, 660, y + 21)
                else:
                    draw_text(screen, small_font, specialty_terminal_label(role), border_color, 560, y + 21)

        elif screen_name == "lobby":
            draw_text(
                screen,
                title_font,
                "Mission Lobby",
                TEXT,
                WINDOW_WIDTH // 2,
                105,
                center=True,
            )
            draw_text(
                screen,
                font,
                "All connected players must be ready",
                MUTED,
                WINDOW_WIDTH // 2,
                150,
                center=True,
            )
            players = list(state["players"].values())
            for index, player in enumerate(players):
                y = 205 + index * 62
                color = tuple(player.get("color", MUTED))
                pygame.draw.rect(screen, PANEL, (220, y, 560, 48), border_radius=5)
                pygame.draw.rect(screen, color, (220, y, 560, 48), 2, 5)
                draw_text(screen, font, player["name"], TEXT, 240, y + 12)
                draw_text(
                    screen,
                    small_font,
                    player.get("role") or "Choosing role",
                    MUTED,
                    440,
                    y + 15,
                )
                ready_text = "READY" if player.get("ready") else "NOT READY"
                ready_color = GREEN if player.get("ready") else YELLOW
                draw_text(screen, small_font, ready_text, ready_color, 660, y + 15)

            own_player = state["players"].get(player_id, {})
            enough_players = len(players) >= state.get("minimum_players", 2)
            if not enough_players:
                prompt = (
                    f"Waiting for players ({len(players)}/"
                    f"{state.get('minimum_players', 2)})"
                )
                prompt_color = YELLOW
            elif own_player.get("ready"):
                prompt = "You are ready. Press SPACE to cancel."
                prompt_color = GREEN
            else:
                prompt = "Press SPACE when ready"
                prompt_color = TEXT
            draw_text(
                screen,
                font,
                prompt,
                prompt_color,
                WINDOW_WIDTH // 2,
                585,
                center=True,
            )
            draw_text(
                screen,
                small_font,
                f"Your specialty: {selected_role}",
                MUTED,
                WINDOW_WIDTH // 2,
                625,
                center=True,
            )

        elif screen_name == "vote":
            draw_text(
                screen,
                title_font,
                "Vote Difficulty",
                TEXT,
                WINDOW_WIDTH // 2,
                115,
                center=True,
            )
            draw_text(
                screen,
                font,
                "Everyone is ready. Choose the question difficulty.",
                MUTED,
                WINDOW_WIDTH // 2,
                160,
                center=True,
            )
            vote_options = [
                ("easy", "EASY", "Simple fundamentals"),
                ("medium", "MEDIUM", "Slightly trickier prompts"),
                ("hard", "HARD", "More demanding incident clues"),
            ]
            own_vote = state["players"].get(player_id, {}).get("difficulty_vote", "")
            for index, (difficulty, label, description) in enumerate(vote_options, start=1):
                y = 240 + (index - 1) * 85
                vote_count = state.get("difficulty_votes", {}).get(difficulty, 0)
                selected = own_vote == difficulty
                color = GREEN if selected else (80, 120, 175)
                pygame.draw.rect(screen, PANEL, (230, y, 540, 62), border_radius=6)
                pygame.draw.rect(screen, color, (230, y, 540, 62), 3, 6)
                draw_text(screen, font, f"{index}  {label}", TEXT, 260, y + 12)
                draw_text(screen, small_font, description, MUTED, 260, y + 38)
                draw_text(
                    screen,
                    font,
                    f"{vote_count}",
                    color,
                    720,
                    y + 20,
                    center=True,
                )
            voted = sum(1 for player in state["players"].values() if player.get("difficulty_vote"))
            total = len(state["players"])
            prompt = (
                f"Your vote: {own_vote.upper()}"
                if own_vote
                else "Press 1, 2, or 3 to vote"
            )
            draw_text(
                screen,
                font,
                prompt,
                GREEN if own_vote else TEXT,
                WINDOW_WIDTH // 2,
                555,
                center=True,
            )
            draw_text(
                screen,
                small_font,
                f"Votes received: {voted}/{total}",
                MUTED,
                WINDOW_WIDTH // 2,
                590,
                center=True,
            )
            draw_text(
                screen,
                small_font,
                "If tied, the server randomly chooses from the tied options.",
                MUTED,
                WINDOW_WIDTH // 2,
                625,
                center=True,
            )

        elif screen_name == "vote_results":
            draw_text(
                screen,
                title_font,
                "Vote Results",
                TEXT,
                WINDOW_WIDTH // 2,
                120,
                center=True,
            )
            vote_options = [
                ("easy", "EASY"),
                ("medium", "MEDIUM"),
                ("hard", "HARD"),
            ]
            for index, (difficulty, label) in enumerate(vote_options):
                y = 220 + index * 72
                votes = state.get("difficulty_votes", {}).get(difficulty, 0)
                selected = state.get("selected_difficulty") == difficulty
                color = GREEN if selected else (80, 120, 175)
                pygame.draw.rect(screen, PANEL, (280, y, 440, 50), border_radius=5)
                pygame.draw.rect(screen, color, (280, y, 440, 50), 3, 5)
                draw_text(screen, font, label, TEXT, 310, y + 13)
                draw_text(screen, font, f"{votes} vote(s)", color, 590, y + 13)

            selected = (state.get("selected_difficulty") or "").upper()
            if state.get("vote_result_tied"):
                tied = ", ".join(
                    difficulty.upper()
                    for difficulty in state.get("vote_result_tied_options", [])
                )
                result_line = f"Tie between {tied}. Random pick: {selected}"
            else:
                result_line = f"Selected difficulty: {selected}"
            draw_text(
                screen,
                font,
                result_line,
                GREEN,
                WINDOW_WIDTH // 2,
                500,
                center=True,
            )
            draw_text(
                screen,
                small_font,
                "Game starting...",
                MUTED,
                WINDOW_WIDTH // 2,
                545,
                center=True,
            )

        else:
            pygame.draw.rect(screen, PANEL, (0, 0, WINDOW_WIDTH, 82))
            pygame.draw.line(screen, (42, 56, 78), (0, 82), (WINDOW_WIDTH, 82), 1)
            me = state["players"].get(player_id, {})
            specialty = me.get("specialty") or selected_role
            role_text = display_social_role(me.get("social_role", ""))
            draw_text(screen, small_font, "ROLE", MUTED, 24, 14)
            draw_text(screen, font, f"{role_text}", TEXT, 24, 39)
            draw_text(
                screen,
                small_font,
                f"{specialty_terminal_label(specialty)} | {specialty}",
                MUTED,
                24,
                62,
            )
            pygame.draw.line(screen, (42, 56, 78), (315, 16), (315, 66), 1)
            lab_health = max(0, min(100, int(state.get("global_progress", 0) * 100)))
            health_color = GREEN if lab_health >= 75 else YELLOW if lab_health >= 30 else RED
            difficulty = state.get("selected_difficulty") or "?"
            hud_items = (
                ("LAB HEALTH", f"{lab_health}%", health_color, 350),
                ("TIME", f"{state['timer']:03d}", TEXT, 500),
                ("DIFFICULTY", difficulty.upper(), TEXT, 625),
            )
            for label, value, color, x in hud_items:
                draw_hud_metric(screen, font, small_font, label, value, color, x)
            pygame.draw.line(screen, (42, 56, 78), (765, 16), (765, 66), 1)
            if me.get("social_role") == ROLE_ATTACKER and me.get("life_state") == "alive":
                attack_points = me.get("attack_points", 0)
                attack_bonus = me.get("attack_bonus", 0)
                draw_hud_metric(screen, font, small_font, "ATTACK POINTS", str(attack_points), ORANGE, 795)
                tools_note = "X abilities"
                if attack_bonus > 0:
                    tools_note += f" | Bonus +{attack_bonus} dmg"
                draw_text(screen, small_font, tools_note, ORANGE, 795, 62)
            else:
                draw_hud_metric(screen, font, small_font, "DEFENDER GOAL", "recover", GREEN, 795)
                draw_text(screen, small_font, "most by time", MUTED, 795, 62)

            for x in range(0, WINDOW_WIDTH, 50):
                pygame.draw.line(screen, (20, 28, 42), (x, 82), (x, WINDOW_HEIGHT))
            for y in range(82, WINDOW_HEIGHT, 50):
                pygame.draw.line(screen, (20, 28, 42), (0, y), (WINDOW_WIDTH, y))

            draw_ambient_lab_props(screen, small_font, now)
            draw_system_reactions(screen, system_reactions, now)

            player = state["players"].get(player_id)
            close_terminal = nearest_terminal(player, state)
            for terminal_id, terminal in TERMINALS.items():
                task = state["tasks"].get(terminal_id, {})
                complete = task_completed(task)
                cooling = isinstance(task, dict) and task.get("cooldown_remaining", 0) > 0
                compromised = isinstance(task, dict) and task.get("compromised")
                color = system_health_color(task, terminal["color"])
                if compromised and not complete:
                    color = RED
                if isinstance(task, dict) and "health" in task and cooling:
                    action_label = "Attack" if me.get("social_role") == ROLE_ATTACKER else "Repair"
                    terminal_status = (
                        f"{action_label} lock {task.get('cooldown_remaining')}s | "
                        f"{task.get('health', 0)}%"
                    )
                elif isinstance(task, dict) and "health" in task:
                    terminal_status = f"{task.get('status', 'STABLE')} {task.get('health', 0)}%"
                elif compromised:
                    terminal_status = f"DISRUPTED {task.get('difficulty', '').upper()}"
                else:
                    terminal_status = f"{task.get('difficulty', difficulty).upper()} repair"

                health = task.get("health") if isinstance(task, dict) else None
                draw_system_pad(screen, terminal, color, terminal_id == close_terminal)
                sprite = terminal_sprites.get(terminal_id)
                if sprite:
                    draw_terminal_sprite(
                        screen,
                        sprite,
                        small_font,
                        terminal,
                        terminal_status,
                        color,
                        terminal_id == close_terminal,
                        health,
                    )
                else:
                    draw_terminal_card(
                        screen,
                        small_font,
                        terminal,
                        terminal_status,
                        color,
                        terminal_id == close_terminal,
                    )

            for other_id, player in state["players"].items():
                visual = player_visuals.get(other_id)
                if visual:
                    draw_player(
                        screen,
                        sprites,
                        small_font,
                        player,
                        visual,
                        other_id == player_id,
                        now,
                    )

            draw_action_strip(screen, small_font, me)
            draw_floating_feedback(screen, font, floating_feedback, now)

            if ability_menu_open:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                screen.blit(overlay, (0, 0))
                box = pygame.Rect(190, 125, 620, 430)
                pygame.draw.rect(screen, PANEL, box, border_radius=8)
                pygame.draw.rect(screen, ORANGE, box, 3, 8)
                me = state["players"].get(player_id, {})
                points = me.get("attack_points", 0)
                attack_bonus = me.get("attack_bonus", 0)
                cooldowns = me.get("ability_cooldowns_remaining", {})
                if ability_target_mode == "malware":
                    draw_text(screen, title_font, "Malware Target", TEXT, WINDOW_WIDTH // 2, 165, center=True)
                    draw_text(
                        screen,
                        small_font,
                        f"Attack Points: {points}   Cost: 3   Banked bonus: +{attack_bonus}",
                        ORANGE,
                        WINDOW_WIDTH // 2,
                        210,
                        center=True,
                    )
                    options = malware_target_options(state)
                    if options:
                        for index, terminal_id in enumerate(options, start=1):
                            task = state["tasks"].get(terminal_id, {})
                            terminal = TERMINALS[terminal_id]
                            y = 250 + (index - 1) * 62
                            health = task.get("health", 0)
                            draw_text(screen, font, f"{index}. {terminal['label']}", TEXT, 245, y)
                            draw_text(
                                screen,
                                small_font,
                                f"{health}% health   {task.get('status', 'STABLE')}",
                                ORANGE,
                                275,
                                y + 28,
                            )
                    else:
                        draw_text(
                            screen,
                            font,
                            "No online systems remain.",
                            MUTED,
                            WINDOW_WIDTH // 2,
                            320,
                            center=True,
                        )
                    draw_text(screen, small_font, "1-3: select   Backspace: abilities   X/Esc: close", MUTED, WINDOW_WIDTH // 2, 510, center=True)
                else:
                    draw_text(screen, title_font, "Attacker Abilities", TEXT, WINDOW_WIDTH // 2, 165, center=True)
                    draw_text(screen, font, f"Attack Points: {points}   Bonus +{attack_bonus}", ORANGE, WINDOW_WIDTH // 2, 210, center=True)
                    for index, (ability, cost, description) in enumerate(ATTACKER_ABILITY_ROWS, start=1):
                        y = 250 + (index - 1) * 72
                        cooldown = cooldowns.get(ability, 0)
                        if cooldown:
                            status = f"CD {cooldown}s"
                            status_color = MUTED
                        elif points < cost:
                            status = f"Need {cost}"
                            status_color = RED
                        else:
                            status = "READY"
                            status_color = GREEN
                        draw_text(screen, font, f"{index}. {ability}", TEXT, 245, y)
                        draw_text(screen, small_font, description, MUTED, 275, y + 28)
                        draw_text(screen, small_font, f"Cost {cost}   {status}", status_color, 620, y + 18)
                    draw_text(screen, small_font, "1-2: launch   3: choose target   X/Esc: close", MUTED, WINDOW_WIDTH // 2, 510, center=True)

            if popup:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 170))
                screen.blit(overlay, (0, 0))
                box = pygame.Rect(160, 150, 680, 400)
                pygame.draw.rect(screen, PANEL, box, border_radius=8)
                pygame.draw.rect(screen, (80, 120, 175), box, 3, 8)
                draw_text(screen, title_font, popup["title"], TEXT, 195, 180)
                y = 240
                for line in wrapped_lines(font, popup["question"], 610):
                    draw_text(screen, font, line, TEXT, 195, y)
                    y += 28
                options = popup.get("options", [])
                for index, option in enumerate(options, start=1):
                    option_y = y + 8 + (index - 1) * 25
                    draw_text(
                        screen,
                        small_font,
                        f"{index}. {option}",
                        TEXT,
                        215,
                        option_y,
                    )
                if options:
                    y += 30 + len(options) * 25
                if popup.get("role_bonus"):
                    bonus = popup.get("specialty_bonus", {})
                    draw_text(
                        screen,
                        small_font,
                        "SPECIALTY BONUS",
                        GREEN,
                        195,
                        y + 15,
                    )
                    if bonus.get("applies"):
                        draw_text(
                            screen,
                            small_font,
                            f"{bonus.get('track', '').title()}: {bonus.get('label', '')}",
                            GREEN,
                            335,
                            y + 15,
                        )
                    draw_text(
                        screen,
                        small_font,
                        f"Hint: {popup['hint']}",
                        MUTED,
                        195,
                        y + 42,
                    )
                else:
                    draw_text(
                        screen,
                        small_font,
                        "No role hint available.",
                        MUTED,
                        195,
                        y + 15,
                    )
                input_label = "Answer" if options else "One-word answer"
                pygame.draw.rect(screen, BG, (195, 440, 610, 48), border_radius=4)
                pygame.draw.rect(screen, (80, 120, 175), (195, 440, 610, 48), 2, 4)
                draw_text(screen, small_font, f"{input_label}:", MUTED, 205, 421)
                draw_text(screen, font, answer, TEXT, 210, 452)
                draw_typing_indicator(screen, font, answer, 210, 452, TEXT, now)
                help_text = "1-4: choose MCQ   Enter: submit   Esc: close" if options else "Type the term   Enter: submit   Esc: close"
                draw_text(
                    screen,
                    small_font,
                    help_text,
                    MUTED,
                    195,
                    505,
                )

            if pending_task and not popup and not result_popup:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 165))
                screen.blit(overlay, (0, 0))
                box = pygame.Rect(250, 215, 500, 230)
                pygame.draw.rect(screen, PANEL, box, border_radius=8)
                pygame.draw.rect(screen, YELLOW, box, 3, 8)
                elapsed = max(0.0, now - pending_task.get("started_at", now))
                dots = "." * (int(elapsed * 2) % 4)
                spinner_center = (WINDOW_WIDTH // 2, 322)
                spinner_radius = 30
                pygame.draw.circle(screen, (49, 62, 82), spinner_center, spinner_radius, 5)
                start_angle = (elapsed * 4.0) % 6.283
                end_angle = start_angle + 1.8
                spinner_rect = pygame.Rect(0, 0, spinner_radius * 2, spinner_radius * 2)
                spinner_rect.center = spinner_center
                pygame.draw.arc(screen, YELLOW, spinner_rect, start_angle, end_angle, 5)
                draw_text(
                    screen,
                    title_font,
                    "Preparing Challenge",
                    TEXT,
                    WINDOW_WIDTH // 2,
                    250,
                    center=True,
                )
                draw_text(
                    screen,
                    font,
                    f"{pending_task.get('action', 'Generating challenge')}{dots}",
                    TEXT,
                    WINDOW_WIDTH // 2,
                    282,
                    center=True,
                )
                draw_text(
                    screen,
                    font,
                    pending_task.get("label", "System"),
                    YELLOW,
                    WINDOW_WIDTH // 2,
                    370,
                    center=True,
                )
                helper_text = (
                    "AI is tailoring this question to your recent answers."
                    if elapsed < 4
                    else "Still generating. The server will fall back if AI is slow."
                )
                draw_text(
                    screen,
                    small_font,
                    helper_text,
                    MUTED,
                    WINDOW_WIDTH // 2,
                    400,
                    center=True,
                )
                draw_text(
                    screen,
                    small_font,
                    f"Waiting {int(elapsed)}s",
                    MUTED,
                    WINDOW_WIDTH // 2,
                    424,
                    center=True,
                )

            if result_popup:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                box = pygame.Rect(150, 125, 700, 455)
                result_color = GREEN if result_popup.get("correct") else RED
                pygame.draw.rect(screen, PANEL, box, border_radius=8)
                pygame.draw.rect(screen, result_color, box, 3, 8)
                draw_text(
                    screen,
                    title_font,
                    "Challenge Complete" if result_popup.get("correct") else "Challenge Review",
                    TEXT,
                    WINDOW_WIDTH // 2,
                    165,
                    center=True,
                )
                draw_text(screen, font, result_popup.get("message", ""), result_color, 185, 215)
                y = 260
                details = [
                    ("Correct answer", result_popup.get("correct_answer", "")),
                    ("Lesson", result_popup.get("lesson", "")),
                    ("Explanation", result_popup.get("explanation", "")),
                    ("Real-world relevance", result_popup.get("relevance", "")),
                ]
                for label, text in details:
                    label_color = GREEN if label == "Lesson" else YELLOW
                    draw_text(screen, small_font, f"{label}:", label_color, 185, y)
                    y += 22
                    for line in wrapped_lines(small_font, str(text or "Not available."), 630):
                        draw_text(screen, small_font, line, TEXT, 205, y)
                        y += 20
                    y += 12
                draw_text(
                    screen,
                    small_font,
                    "Enter/Esc: close",
                    MUTED,
                    WINDOW_WIDTH // 2,
                    545,
                    center=True,
                )

            if state["status"] in ("win", "loss"):
                result = state.get("result") or (RESULT_DEFENDERS_WIN if state["status"] == "win" else RESULT_ATTACKERS_WIN)
                me = state["players"].get(player_id, {})
                player_won = local_player_won(result, me)
                animation_mode = "victory" if player_won else "defeat"
                animation_key = (result, animation_mode)
                if end_screen_animation is None or end_screen_animation_key != animation_key:
                    end_screen_animation = EndScreenAnimation(
                        (WINDOW_WIDTH, WINDOW_HEIGHT),
                        animation_mode,
                        intensity=1.0 if animation_mode == "victory" else 1.12,
                        particle_count=170 if animation_mode == "victory" else 90,
                        speed=1.0,
                    )
                    end_screen_animation.start(now)
                    end_screen_animation_key = animation_key

                transition = end_screen_animation.transition_progress(now)
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((4, 7, 12, int(220 * transition)))
                screen.blit(overlay, (0, 0))
                end_screen_animation.draw(screen, now)
                score = state.get("score", {})
                average_health = score.get("average_health", 0)
                baseline_health = score.get("baseline_health", 50)
                defender_score = score.get("defender_score", 0)
                attacker_score = score.get("attacker_score", 0)
                average_text = compact_number(average_health)
                baseline_text = compact_number(baseline_health)
                defender_text = compact_number(defender_score)
                attacker_text = compact_number(attacker_score)
                ended_by_timer = state.get("game_over_reason") == "timer"
                title = game_over_title(result, ended_by_timer)
                defenders_won = result == RESULT_DEFENDERS_WIN
                if ended_by_timer and defenders_won:
                    detail = f"Final lab health {average_text}% vs starting {baseline_text}%"
                    score_line = f"Net recovered: +{defender_text}%"
                elif ended_by_timer:
                    detail = f"Final lab health {average_text}% vs starting {baseline_text}%"
                    score_line = f"Net destroyed: +{attacker_text}%"
                else:
                    detail = "Systems restored to 100%" if defenders_won else "Systems reduced to 0%"
                    score_line = f"Final lab health: {average_text}%"
                title_color = GREEN if defenders_won else ORANGE
                if not player_won:
                    title_color = RED
                panel = RESULT_PANEL_RECT
                shadow = panel.move(0, 8)
                pygame.draw.rect(screen, (2, 5, 11), shadow, border_radius=12)
                pygame.draw.rect(screen, (13, 20, 32), panel, border_radius=12)
                pygame.draw.rect(screen, (48, 65, 91), panel, 1, 12)
                pygame.draw.line(
                    screen,
                    title_color,
                    (panel.x + 46, panel.y + 2),
                    (panel.right - 46, panel.y + 2),
                    3,
                )
                draw_text(
                    screen,
                    small_font,
                    "MISSION RESULT",
                    MUTED,
                    panel.centerx,
                    panel.y + 38,
                    center=True,
                )
                draw_text(
                    screen,
                    title_font,
                    title,
                    title_color,
                    panel.centerx,
                    panel.y + 88,
                    center=True,
                )
                draw_text(
                    screen,
                    font,
                    detail,
                    TEXT,
                    panel.centerx,
                    panel.y + 142,
                    center=True,
                )
                badge = pygame.Rect(0, 0, 250, 34)
                badge.center = (panel.centerx, panel.y + 184)
                pygame.draw.rect(screen, (8, 14, 24), badge, border_radius=17)
                pygame.draw.rect(screen, title_color, badge, 1, 17)
                draw_text(
                    screen,
                    small_font,
                    score_line,
                    YELLOW,
                    badge.centerx,
                    badge.centery,
                    center=True,
                )
                pygame.draw.line(
                    screen,
                    (42, 56, 78),
                    (panel.x + 70, panel.y + 226),
                    (panel.right - 70, panel.y + 226),
                    1,
                )
                draw_text(
                    screen,
                    small_font,
                    "Review your stats, missed questions, and team performance.",
                    TEXT,
                    panel.centerx,
                    panel.y + 256,
                    center=True,
                )
                pygame.draw.rect(screen, (13, 20, 32), REPORT_BUTTON_RECT, border_radius=6)
                pygame.draw.rect(screen, YELLOW, REPORT_BUTTON_RECT, 2, 6)
                draw_text(
                    screen,
                    small_font,
                    "View Full Report",
                    YELLOW,
                    REPORT_BUTTON_RECT.centerx,
                    REPORT_BUTTON_RECT.centery,
                    center=True,
                )
                draw_text(
                    screen,
                    small_font,
                    "Press R to reset the shared lab",
                    MUTED,
                    panel.centerx,
                    panel.y + 356,
                    center=True,
                )

        pygame.draw.rect(screen, PANEL, GUIDE_BUTTON_RECT, border_radius=5)
        pygame.draw.rect(screen, (80, 120, 175), GUIDE_BUTTON_RECT, 2, 5)
        draw_text(
            screen,
            small_font,
            "Guide",
            TEXT,
            GUIDE_BUTTON_RECT.centerx,
            GUIDE_BUTTON_RECT.centery,
            center=True,
        )

        pygame.draw.rect(screen, PANEL, CHEATSHEET_BUTTON_RECT, border_radius=5)
        pygame.draw.rect(screen, (80, 120, 175), CHEATSHEET_BUTTON_RECT, 2, 5)
        draw_text(
            screen,
            small_font,
            "Cheatsheet",
            TEXT,
            CHEATSHEET_BUTTON_RECT.centerx,
            CHEATSHEET_BUTTON_RECT.centery,
            center=True,
        )

        if cheatsheet_open:
            draw_cheatsheet(screen, title_font, font, small_font, cheatsheet_scroll)
        elif guide_open:
            draw_lab_guide(screen, title_font, font, small_font, state, guide_tab)

        if report_open and state.get("status") in ("win", "loss"):
            report_page = max(0, min(report_page, report_page_count(state) - 1))
            draw_full_report(screen, title_font, font, small_font, state, report_page)

        if notice and (notice_until == 0 or now < notice_until):
            rendered_width = small_font.size(notice)[0]
            if screen_name != "game":
                draw_text(
                    screen,
                    small_font,
                    notice,
                    notice_color,
                    WINDOW_WIDTH // 2,
                    620,
                    center=True,
                )
            else:
                pygame.draw.rect(
                    screen,
                    PANEL,
                    (WINDOW_WIDTH - rendered_width - 35, 10, rendered_width + 25, 30),
                )
                draw_text(
                    screen,
                    small_font,
                    notice,
                    notice_color,
                    WINDOW_WIDTH - rendered_width - 23,
                    17,
                )

        if role_reveal:
            if now - role_reveal["started_at"] < role_reveal_total_seconds(role_reveal):
                draw_role_reveal(screen, title_font, font, small_font, role_reveal, now)
            else:
                objective_banner = start_objective_banner(role_reveal["role"], now)
                play_sound(sounds, "banner")
                role_reveal = None

        if objective_banner:
            if not draw_objective_banner(screen, font, small_font, objective_banner, now):
                objective_banner = None

        blackout_remaining = state.get("effects", {}).get("blackout_remaining", 0)
        blackout_active = blackout_remaining > 0
        if blackout_active:
            if not blackout_was_active or blackout_snapshot is None:
                blackout_snapshot = screen.copy()
            else:
                screen.blit(blackout_snapshot, (0, 0))
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 210))
            screen.blit(overlay, (0, 0))
            draw_text(
                screen,
                title_font,
                "BLACKOUT",
                RED,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 - 20,
                center=True,
            )
            draw_text(
                screen,
                font,
                f"Signal lost: {blackout_remaining}s",
                TEXT,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2 + 30,
                center=True,
            )
        else:
            blackout_snapshot = None
        blackout_was_active = blackout_active

        if wrong_answer_effect:
            if now - wrong_answer_effect["started_at"] < WRONG_ANSWER_EFFECT_SECONDS:
                draw_wrong_answer_flash(screen, wrong_answer_effect, now)
            else:
                wrong_answer_effect = None

        display.fill((2, 5, 12))
        offset_x, offset_y = shake_offset(wrong_answer_effect, now)
        display.blit(screen, (offset_x, offset_y))
        pygame.display.flip()
        clock.tick(60)

    network.close()
    pygame.quit()


if __name__ == "__main__":
    main()
    
