import math
import random
import sys
import array
import pygame

from dataclasses import dataclass, field

# --- ENGINE CONFIGURATIONS ---
WIDTH, HEIGHT = 1200, 700
PLAYER_X = 180
GROUND_Y = HEIGHT - 120
MAX_SPEED = 22.0        
ACCELERATION = 0.0012   
JUMP_SPEED = -18
GRAVITY = 1.0

# --- THEMES & STYLING COLORS ---
PALETTE = {
    "wall": (230, 218, 198), "locker": (165, 185, 195), "locker_d": (130, 150, 160), "glare": (245, 245, 250),
    "pillar": (195, 180, 160), "tile_a": (150, 140, 130), "tile_b": (135, 125, 115), "baseboard": (90, 60, 35),
    "det_wall": (14, 10, 22), "cyber_bg": (28, 18, 45), "grid_far": (0, 90, 110), "det_glow": (0, 255, 220),
    "det_line": (255, 0, 90), "nodes": (0, 180, 255), "det_base": (35, 15, 45),
    "sky": (8, 6, 18), "roof_f": (55, 58, 66), "roof_d": (38, 40, 46), "sil_far": (18, 15, 32),
    "sil_near": (32, 24, 48), "win_on": (255, 215, 80), "win_off": (60, 50, 75),
    "cyan": (0, 255, 240), "pink": (255, 0, 100), "orange": (255, 120, 0), "page": (255, 255, 240),
    "page_b": (120, 110, 90), "text": (20, 20, 20), "coffee_b": (110, 65, 35), "coffee_c": (235, 235, 240),
    "btn": (70, 140, 90), "btn_h": (90, 170, 110), "warn": (160, 60, 60), "warn_h": (190, 80, 80),
    "shop": (50, 100, 140), "shop_h": (70, 130, 180), "skin": (255, 220, 180), "shoe": (15, 15, 15),
    "suit": (80, 85, 90), "t_hair": (210, 200, 190)
}

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
FONT = pygame.font.SysFont(None, 24)
LARGE_FONT = pygame.font.SysFont(None, 32, bold=True)
HUGE_FONT = pygame.font.SysFont(None, 64, bold=True)  
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Subway Runner - Complete Unified Build")
CLOCK = pygame.time.Clock()

# --- SYNTHETIC AUDIO PROCEDURAL LOGIC ---
def generate_synth_track(notes, duration_ms=250, wave_type="square"):
    sample_rate = 22050
    buffer = array.array('h')
    for note in notes:
        samples = int(sample_rate * (duration_ms / 1000.0))
        if note == 0:
            buffer.extend([0, 0] * samples)
        else:
            period = sample_rate / note
            for i in range(samples):
                if wave_type == "square":
                    val = 1800 if (i % period) < (period / 2) else -1800
                elif wave_type == "triangle":
                    val = int(1800 * (4 * abs((i % period) / period - 0.5) - 1))
                else:
                    val = int(1800 * math.sin(2 * math.pi * note * (i / sample_rate)))
                buffer.extend([val, val])
    return pygame.mixer.Sound(buffer)

def generate_pacman_death_sound():
    sample_rate = 22050
    buffer = array.array('h')
    for freq in [440, 392, 349, 329, 293, 261, 220, 196, 174, 146, 130, 110]:
        samples = int(sample_rate * (70 / 1000.0))
        period = sample_rate / freq
        for i in range(samples):
            val = 2500 if (i % period) < (period / 2) else -2500
            buffer.extend([val, val])
    return pygame.mixer.Sound(buffer)

MUSIC_LOBBY = generate_synth_track([293, 329, 392, 440, 523, 440, 392, 329, 293, 0, 392, 0, 440, 523, 587, 0], 240, "triangle")
MUSIC_ZONE1 = generate_synth_track([146, 0, 146, 165, 174, 0, 174, 165, 146, 0, 146, 196, 130, 130, 138, 0], 220, "square")
MUSIC_ZONE2 = generate_synth_track([110, 220, 110, 220, 130, 260, 130, 260, 98, 196, 98, 196, 116, 233, 146, 0], 170, "square")
MUSIC_ZONE3 = generate_synth_track([220, 293, 349, 440, 392, 311, 233, 311, 220, 293, 349, 440, 587, 523, 493, 392], 150, "triangle")
SFX_CATCH_DEATH = generate_pacman_death_sound()

CURRENT_PLAYING_CHANNEL, CURRENT_MUSIC_ID = None, None

def play_soundtrack(track_obj, track_id):
    global CURRENT_PLAYING_CHANNEL, CURRENT_MUSIC_ID
    if CURRENT_MUSIC_ID == track_id: return
    if CURRENT_PLAYING_CHANNEL: CURRENT_PLAYING_CHANNEL.stop()
    CURRENT_MUSIC_ID = track_id
    CURRENT_PLAYING_CHANNEL = pygame.mixer.find_channel()
    if CURRENT_PLAYING_CHANNEL: CURRENT_PLAYING_CHANNEL.play(track_obj, loops=-1)

def draw_teacher_sprite(x, y):
    pygame.draw.rect(SCREEN, PALETTE["suit"], (int(x), int(y + 25), 65, 75), border_radius=22)
    pygame.draw.polygon(SCREEN, PALETTE["glare"], [(int(x + 22), int(y + 25)), (int(x + 43), int(y + 25)), (int(x + 32), int(y + 50))])
    pygame.draw.rect(SCREEN, PALETTE["skin"], (int(x + 12), int(y - 12), 40, 38), border_radius=12)
    pygame.draw.rect(SCREEN, PALETTE["t_hair"], (int(x + 12), int(y - 12), 40, 14), border_radius=8)
    pygame.draw.circle(SCREEN, (25, 25, 25), (int(x + 40), int(y + 6)), 5) 
    pygame.draw.rect(SCREEN, PALETTE["suit"], (int(x + 8), int(y + 98), 49, 32), border_radius=6)
    for ox in [6, 37]: pygame.draw.rect(SCREEN, PALETTE["shoe"], (int(x + ox), int(y + 126), 22, 12), border_radius=4)

@dataclass
class ParticleSystem:
    particles: list = field(default_factory=list)

    def update_and_draw(self, dt, speed, current_level, player_has_boost=False):
        if player_has_boost:
            for _ in range(2):
                self.particles.append({"x": PLAYER_X + 10, "y": random.randint(GROUND_Y - 120, GROUND_Y), "vx": -random.randint(150, 350), "vy": random.randint(-60, 60), "color": (255, random.randint(140, 220), 0), "size": random.randint(4, 7), "life": 0.6})
        if current_level == 2 and random.random() < 0.2:
            self.particles.append({"x": random.randint(0, WIDTH), "y": GROUND_Y, "vx": random.randint(-40, 40), "vy": -random.randint(50, 120), "color": PALETTE["det_glow"], "size": random.randint(2, 4), "life": 1.8})
        elif current_level == 3 and random.random() < 0.4:
            self.particles.append({"x": WIDTH, "y": random.randint(30, GROUND_Y - 20), "vx": -(speed * 85) - random.randint(150, 300), "vy": random.randint(-4, 4), "color": (140, 170, 235), "size": random.randint(4, 8), "life": 1.2})
        for p in list(self.particles):
            p["x"] += p["vx"] * dt; p["y"] += p["vy"] * dt; p["life"] -= dt
            if p["life"] <= 0 or p["x"] < -50 or p["x"] > WIDTH + 100:
                if p in self.particles: self.particles.remove(p)
                continue
            if current_level == 3: pygame.draw.line(SCREEN, p["color"], (int(p["x"]), int(p["y"])), (int(p["x"] + p["size"] * 4), int(p["y"])), 2)
            else: pygame.draw.circle(SCREEN, p["color"], (int(p["x"]), int(p["y"])), p["size"])

@dataclass
class DynamicBackground:
    layer_far_x: float = 0.0
    layer_mid_x: float = 0.0
    layer_near_x: float = 0.0
    floor_scroll_x: float = 0.0
    window_matrix: list = field(default_factory=lambda: [[random.choice([True, False, False]) for _ in range(12)] for _ in range(6)])

    def update(self, dt, speed):
        base = (speed * 45) * dt
        self.layer_far_x = (self.layer_far_x - base * 0.15) % -1200
        self.layer_mid_x = (self.layer_mid_x - base * 0.40) % -1200
        self.layer_near_x = (self.layer_near_x - base * 0.85) % -1200
        self.floor_scroll_x = (self.floor_scroll_x - base) % -200
    def draw(self, score):
        if score < 1000:
            SCREEN.fill(PALETTE["wall"])
            for i in range(3):
                fx = self.layer_mid_x + (i * 600)
                pygame.draw.rect(SCREEN, (210, 198, 178), (int(fx + 50), 80, 200, 250))
                pygame.draw.rect(SCREEN, PALETTE["glare"], (int(fx + 60), 90, 180, 230))
                pygame.draw.line(SCREEN, (210, 198, 178), (int(fx + 150), 90), (int(fx + 150), 320), 4)
                pygame.draw.line(SCREEN, (210, 198, 178), (int(fx + 60), 200), (int(fx + 240), 200), 4)
                pygame.draw.rect(SCREEN, PALETTE["pillar"], (int(fx + 380), 0, 70, GROUND_Y))
                pygame.draw.rect(SCREEN, (175, 160, 140), (int(fx + 380), 0, 8, GROUND_Y))
            for i in range(5):
                mx = self.layer_near_x + (i * 350)
                for l in range(3):
                    lx = mx + (l * 45)
                    if lx < WIDTH + 100:
                        pygame.draw.rect(SCREEN, PALETTE["locker"], (int(lx), 180, 42, GROUND_Y - 204), border_radius=2)
                        pygame.draw.rect(SCREEN, PALETTE["locker_d"], (int(lx), 180, 42, GROUND_Y - 204), 2, border_radius=2)
                        pygame.draw.line(SCREEN, PALETTE["locker_d"], (int(lx + 10), 195), (int(lx + 32), 195), 2)
                        pygame.draw.line(SCREEN, PALETTE["locker_d"], (int(lx + 10), 202), (int(lx + 32), 202), 2)
                        pygame.draw.circle(SCREEN, (90, 90, 90), (int(lx + 34), 250), 3)
            pygame.draw.rect(SCREEN, PALETTE["baseboard"], (0, GROUND_Y - 24, WIDTH, 24))
            pygame.draw.rect(SCREEN, PALETTE["tile_a"], (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
            for xt in range(int(self.floor_scroll_x) - 200, WIDTH + 200, 120):
                pygame.draw.rect(SCREEN, PALETTE["tile_b"], (xt, GROUND_Y, 60, HEIGHT - GROUND_Y))
                for ox, th in [(0, -80), (60, -20)]: pygame.draw.line(SCREEN, (110, 100, 90), (xt + ox, GROUND_Y), (xt + th, HEIGHT), 2)
        elif score < 2000:
            SCREEN.fill(PALETTE["det_wall"])
            for i in range(3):
                fx = self.layer_far_x + (i * 500)
                pygame.draw.polygon(SCREEN, PALETTE["cyber_bg"], [(int(fx), GROUND_Y), (int(fx + 150), 150), (int(fx + 300), GROUND_Y)])
                pygame.draw.polygon(SCREEN, PALETTE["grid_far"], [(int(fx), GROUND_Y), (int(fx + 150), 150), (int(fx + 300), GROUND_Y)], 1)
            for i in range(4):
                mx = self.layer_mid_x + (i * 400)
                pygame.draw.line(SCREEN, PALETTE["grid_far"], (int(mx), 100), (int(mx + 120), 100), 2)
                pygame.draw.line(SCREEN, PALETTE["grid_far"], (int(mx + 120), 100), (int(mx + 180), 220), 2)
                pygame.draw.circle(SCREEN, PALETTE["det_glow"], (int(mx), 100), 4)
                pygame.draw.circle(SCREEN, PALETTE["nodes"], (int(mx + 180), 220), 4)
            pygame.draw.rect(SCREEN, PALETTE["det_base"], (0, GROUND_Y - 16, WIDTH, 16))
            pygame.draw.rect(SCREEN, PALETTE["det_line"], (0, GROUND_Y - 6, WIDTH, 6))
            pygame.draw.rect(SCREEN, (22, 16, 36), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
            for gy in range(GROUND_Y, HEIGHT, 25): pygame.draw.line(SCREEN, (60, 10, 85), (0, gy), (WIDTH, gy), 1)
            for xl in range(int(self.floor_scroll_x) - 200, WIDTH + 200, 90):
                pygame.draw.line(SCREEN, PALETTE["det_glow"], (xl, GROUND_Y), (xl - 150, HEIGHT), 2)
                pygame.draw.circle(SCREEN, PALETTE["det_line"], (int(xl - 50), int(GROUND_Y + 40)), 3)
        else:
            SCREEN.fill(PALETTE["sky"])
            for star in range(15): pygame.draw.circle(SCREEN, (255, 255, 255), ((star * 93) % WIDTH, (star * 47) % 200), 1 if star % 2 == 0 else 2)
            for i in range(5):
                bx = self.layer_far_x + (i * 380)
                pygame.draw.rect(SCREEN, PALETTE["sil_far"], (int(bx), 220, 220, 400))
                pygame.draw.rect(SCREEN, PALETTE["sil_near"], (int(bx + 140), 140, 180, 500))
                for r in range(8):
                    for c in range(4):
                        w_col = PALETTE["win_on"] if self.window_matrix[r % 6][c % 12] else PALETTE["win_off"]
                        pygame.draw.rect(SCREEN, w_col, (int(bx + 165 + c * 32), int(180 + r * 40), 14, 20))
            pygame.draw.rect(SCREEN, PALETTE["roof_d"], (0, GROUND_Y - 20, WIDTH, 20))
            pygame.draw.rect(SCREEN, (20, 22, 28), (0, GROUND_Y - 8, WIDTH, 8))
            pygame.draw.rect(SCREEN, PALETTE["roof_f"], (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
            for xl in range(int(self.floor_scroll_x) - 200, WIDTH + 200, 160):
                pygame.draw.rect(SCREEN, PALETTE["roof_d"], (xl, GROUND_Y, 8, HEIGHT - GROUND_Y))
                pygame.draw.line(SCREEN, (35, 38, 44), (xl, GROUND_Y), (xl - 100, HEIGHT), 4)
                pygame.draw.line(SCREEN, PALETTE["orange"], (xl + 60, GROUND_Y), (xl + 10, HEIGHT), 2)

@dataclass
class BannerNotification:
    text: str = ""
    timer: float = 0.0

    def trigger(self, title_text): self.text, self.timer = title_text, 2.5  
    def update(self, dt):
        if self.timer > 0: self.timer -= dt
    def draw(self):
        if self.timer <= 0: return
        surf = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        surf.fill((0, 0, 0, int(min(1.0, self.timer * 2.0) * 220)))
        lbl = HUGE_FONT.render(self.text, True, PALETTE["cyan"] if "ROOFTOP" in self.text else PALETTE["det_line"])
        surf.blit(lbl, lbl.get_rect(center=(WIDTH // 2, 45)))
        SCREEN.blit(surf, (0, HEIGHT // 3 - 50))

@dataclass
class IntroChase:
    x: float = PLAYER_X - 60
    y: float = GROUND_Y - 130
    active: bool = True

    def update(self, dt, current_speed):
        self.x -= (current_speed * 50) * dt
        if self.x < -100: self.active = False
    def draw(self):
        if self.active: draw_teacher_sprite(self.x, self.y)

@dataclass
class Player:
    skin: str = "default"
    width: int = 46
    height: int = 104
    x: int = PLAYER_X
    y: float = field(init=False)
    vertical_velocity: float = 0.0
    jumping: bool = False
    sliding: bool = False
    score: int = 0
    distance: float = 0.0
    pages_collected: int = 0
    current_floor_y: int = GROUND_Y
    coffee_boost_timer: float = 0.0
    magnet_timer: float = 0.0
    boots_timer: float = 0.0

    def __post_init__(self):
        self.y = GROUND_Y - self.height

    def get_rect(self):
        h = 44 if self.sliding else self.height
        y_pos = (self.current_floor_y - h) if (self.sliding and not self.jumping) else self.y
        return pygame.Rect(int(self.x + (6 if self.sliding else 8)), int(y_pos), int(self.width - (6 if self.sliding else 8)), int(h))

    def update(self, keys, obstacles, dt):
        for attr in ["coffee_boost_timer", "magnet_timer", "boots_timer"]:
            if getattr(self, attr) > 0: setattr(self, attr, getattr(self, attr) - dt)
        self.sliding = bool(keys[pygame.K_DOWN] or keys[pygame.K_s])
        if not self.jumping and not self.sliding and (keys[pygame.K_UP] or keys[pygame.K_w]):
            self.vertical_velocity, self.jumping = (JUMP_SPEED - 5) if self.boots_timer > 0 else JUMP_SPEED, True
        self.vertical_velocity += GRAVITY
        self.y += self.vertical_velocity
        
        target_floor = GROUND_Y
        p_rect = self.get_rect()
        for obs in obstacles:
            o_rect = obs.get_rect()
            if o_rect.left <= p_rect.centerx <= o_rect.right and obs.kind not in ["ink", "vent", "laser_gate", "popquiz_high", "drone"]:
                if p_rect.bottom <= o_rect.top + 30 and self.vertical_velocity >= 0:
                    target_floor = o_rect.top; break
        self.current_floor_y = target_floor
        curr_h = 44 if self.sliding else self.height
        if self.y + curr_h >= self.current_floor_y:
            self.y, self.vertical_velocity, self.jumping = self.current_floor_y - curr_h, 0, False
        elif self.vertical_velocity != 0 and not self.jumping: self.jumping = True

    def draw(self):
        base_y = (self.current_floor_y - 44) if self.sliding and not self.jumping else self.y
        bottom_y = base_y + 44 if self.sliding else base_y + self.height
        body_h = 18 if self.sliding else 46
        cfg = {
            "varsity_gold": ((245, 190, 25), (190, 20, 35), (25, 25, 30), (255, 225, 80)),
            "cyber_suit": ((12, 18, 32), PALETTE["det_glow"], (18, 22, 36), PALETTE["det_line"]),
            "default": ((220, 70, 70), (45, 50, 70), (40, 60, 110), (110, 50, 160))
        }.get(self.skin, ((220, 70, 70), (45, 50, 70), (40, 60, 110), (110, 50, 160)))
        shirt_c, overlay_c, pants_c, backpack_c = cfg

        bp = pygame.Rect(int(self.x - 12), int(base_y + (6 if self.sliding else 18)), 18, int(26 if self.sliding else 52))
        pygame.draw.rect(SCREEN, backpack_c, bp, border_radius=6)
        pygame.draw.rect(SCREEN, (30, 30, 35), bp, 2, border_radius=6)
        pygame.draw.rect(SCREEN, (100, 104, 120), (bp.x + 3, bp.bottom - 4, 12, 6), border_radius=2)
        if self.skin == "cyber_suit":
            for oy in [10, 24]: pygame.draw.line(SCREEN, PALETTE["det_glow"], (bp.x + 4, bp.y + oy), (bp.x + 14, bp.y + oy), 2)
        elif self.skin == "varsity_gold": 
            pygame.draw.circle(SCREEN, (255, 255, 255), (bp.centerx, bp.y + 14), 3)

        hd = pygame.Rect(int(self.x + 8), int(base_y - 24), 30, 26)
        pygame.draw.rect(SCREEN, PALETTE["skin"], hd, border_radius=10)
        if self.skin == "cyber_suit":
            pygame.draw.rect(SCREEN, (20, 30, 50), hd, border_radius=10)
            pygame.draw.rect(SCREEN, overlay_c, (hd.left + 8, hd.top + 6, hd.width - 10, 10), border_radius=4)
        elif self.skin == "varsity_gold": 
            pygame.draw.rect(SCREEN, (245, 245, 240), (hd.left, hd.top - 4, hd.width, 14), border_radius=6)
            pygame.draw.rect(SCREEN, (20, 20, 25), (hd.right - 14, hd.top + 8, 12, 6), border_radius=2)
        else:
            pygame.draw.rect(SCREEN, (45, 35, 25), (hd.left, hd.top, hd.width, 10), border_radius=8)
            pygame.draw.circle(SCREEN, (25, 25, 25), (int(hd.right - 8), int(hd.centery)), 4)

        torso = pygame.Rect(int(self.x + 6), int(base_y + 8), 30, body_h)
        pygame.draw.rect(SCREEN, shirt_c, torso, border_radius=10)
        if self.skin == "cyber_suit":
            pygame.draw.rect(SCREEN, overlay_c, (torso.x + 3, torso.y + 3, torso.width - 6, torso.height - 6), 2, border_radius=8)
        elif self.skin == "varsity_gold": 
            pygame.draw.rect(SCREEN, overlay_c, (torso.x + 5, torso.y, torso.width - 10, torso.height), border_radius=4)
        else:
            pygame.draw.rect(SCREEN, overlay_c, (torso.x, torso.y, 8, torso.height), border_radius=2)

        pants = pygame.Rect(int(self.x + 8), int(bottom_y - (12 if self.sliding else 34)), 28, int(12 if self.sliding else 34))
        pygame.draw.rect(SCREEN, pants_c, pants, border_radius=8)
        shoe_c = (0, 255, 100) if self.boots_timer > 0 else (0, 255, 230) if self.skin == "cyber_suit" else (255, 220, 30) if self.skin == "varsity_gold" else PALETTE["shoe"]
        for ox in [5, 25]:
            pygame.draw.rect(SCREEN, shoe_c, (int(self.x + ox), int(bottom_y - 10), 14, 9), border_radius=4)
            if self.boots_timer > 0 or self.skin in ["cyber_suit", "varsity_gold"]: pygame.draw.rect(SCREEN, (255, 255, 255), (int(self.x + ox + 2), int(bottom_y - 4), 10, 3))

class CaughtAnimation:
    def __init__(self, tx, ty): self.teacher_x, self.teacher_y, self.player_x, self.player_y, self.phase = -150, GROUND_Y - 130, tx, ty, "APPROACH"
    def update(self, dt):
        if self.phase == "APPROACH":
            if self.teacher_x < self.player_x - 55: self.teacher_x += 350 * dt
            else: self.teacher_x, self.phase = self.player_x - 55, "DRAG"
        elif self.phase == "DRAG":
            self.teacher_x -= 240 * dt; self.player_x -= 240 * dt
            if self.player_x < -100: self.phase = "DONE"
    def draw(self):
        pygame.draw.rect(SCREEN, PALETTE["skin"], (int(self.player_x + 8), int(self.player_y - 26), 30, 28), border_radius=10)
        pygame.draw.rect(SCREEN, PALETTE["glare"], (int(self.player_x + 6), int(self.player_y + 10), 30, 46), border_radius=10)
        pygame.draw.rect(SCREEN, (40, 60, 110), (int(self.player_x + 8), int(self.player_y + 56), 28, 34), border_radius=8)
        draw_teacher_sprite(self.teacher_x, self.teacher_y)

class Obstacle:
    def __init__(self, kind):
        self.kind, self.x, self.speed, self.timer = kind, WIDTH + random.randint(250, 480), 320, random.random() * 10  
        cfg = {
            "pipe": (random.choice([80, 110, 140]), random.choice([95, 120, 145]), 0),
            "low": (random.choice([100, 135, 170]), random.choice([75, 90]), 0),
            "ink": (random.choice([90, 120, 150]), 20, 0), "vent": (random.choice([90, 120, 150]), 35, 0),
            "popquiz_high": (75, 70, 52),     
            "laser_gate": (40, 80, 52),       
            "drone": (random.choice([70, 95]), 65, 52) 
        }[kind]
        self.width, self.height = cfg[0], cfg[1]
        self.y = GROUND_Y - self.height - cfg[2] if cfg[2] else GROUND_Y - self.height
    def update(self, dt, speed): self.x -= (self.speed + speed * 16) * dt; self.timer += dt
    def get_rect(self):
        hover = int(math.sin(self.timer * 6) * 15) if self.kind in ["popquiz_high", "drone"] else 0
        return pygame.Rect(int(self.x), int(self.y + hover), int(self.width), int(self.height))
    def draw(self, is_lvl2):
        rect = self.get_rect()
        if self.kind == "pipe":
            pygame.draw.rect(SCREEN, PALETTE["orange"] if is_lvl2 else (160, 40, 40), rect, border_radius=6)
            pygame.draw.rect(SCREEN, (255, 255, 255), rect, 2, border_radius=6) 
        elif self.kind == "low":
            pygame.draw.rect(SCREEN, PALETTE["orange"] if is_lvl2 else (190, 130, 80), (rect.x, rect.y, rect.width, 18), border_radius=3)
            for ox in [12, rect.width - 22]: pygame.draw.rect(SCREEN, (240, 240, 250), (rect.x + ox, rect.y + 18, 10, rect.height - 18))
        elif self.kind == "ink":
            pygame.draw.ellipse(SCREEN, PALETTE["cyan"], rect); pygame.draw.ellipse(SCREEN, (255, 255, 255), rect, 2) 
        elif self.kind == "popquiz_high":
            pygame.draw.rect(SCREEN, PALETTE["pink"], rect, border_radius=8); f_lbl = LARGE_FONT.render("SLIDE!", True, (255, 255, 255))
            SCREEN.blit(f_lbl, (rect.x + 4, rect.y + 18))
        elif self.kind == "laser_gate":
            pygame.draw.rect(SCREEN, PALETTE["pink"], rect, border_radius=4); pygame.draw.rect(SCREEN, (255, 255, 255), (rect.x + 10, rect.y, rect.width - 20, rect.height))
        elif self.kind == "vent": pygame.draw.rect(SCREEN, PALETTE["orange"], rect, border_radius=4)
        elif self.kind == "drone":
            pygame.draw.rect(SCREEN, PALETTE["pink"], rect, border_radius=8); pygame.draw.circle(SCREEN, (255, 255, 255), (rect.centerx, rect.centery), 10) 
    def check_headon_crash(self, p_rect, player):
        obs_rect = self.get_rect()
        if not obs_rect.colliderect(p_rect): return False
        if self.kind in ["popquiz_high", "laser_gate", "drone", "low"] and player.sliding: return False  
        if p_rect.bottom <= obs_rect.top + 30 and player.vertical_velocity >= 0: return self.kind in ["ink", "vent"]
        return p_rect.right > obs_rect.left + 12 and p_rect.left < obs_rect.right - 12

class Page:
    def __init__(self): self.x, self.y, self.width, self.height, self.speed, self.bob_timer = WIDTH + random.randint(120, 420), GROUND_Y - random.choice([40, 110, 190, 260]), 24, 32, 320, random.random() * 10
    def update(self, dt, speed, player_ref=None):
        self.bob_timer += dt
        if player_ref and player_ref.magnet_timer > 0:
            dx, dy = player_ref.x - self.x, player_ref.y - self.y
            dist = math.hypot(dx, dy)
            if dist < 350: self.x += (dx / dist) * 480 * dt; self.y += (dy / dist) * 480 * dt; return
        self.x -= (self.speed + speed * 16) * dt
    def get_rect(self): return pygame.Rect(int(self.x - self.width // 2), int((self.y - self.height // 2) + int(math.sin(self.bob_timer * 5) * 5)), int(self.width), int(self.height))
    def draw(self): pygame.draw.rect(SCREEN, PALETTE["page"], self.get_rect(), border_radius=2)

class InGamePowerupItem:
    def __init__(self, kind): self.kind, self.x, self.y, self.width, self.height, self.speed, self.timer = kind, WIDTH + random.randint(300, 600), GROUND_Y - random.choice([60, 160]), 32, 32, 320, random.random() * 5
    def update(self, dt, speed): self.x -= (self.speed + speed * 16) * dt; self.timer += dt
    def get_rect(self): return pygame.Rect(int(self.x), int(self.y + int(math.sin(self.timer * 4) * 6)), self.width, self.height)
    def draw(self):
        r = self.get_rect()
        if self.kind == "coffee":
            pygame.draw.rect(SCREEN, PALETTE["coffee_c"], r, border_radius=6); pygame.draw.rect(SCREEN, PALETTE["coffee_b"], (r.x + 4, r.y + 4, r.width - 8, 8))
        elif self.kind == "magnet":
            pygame.draw.arc(SCREEN, (240, 30, 30), r, 0, math.pi, 6)
        elif self.kind == "boots":
            pygame.draw.rect(SCREEN, (0, 220, 100), r, border_radius=4); pygame.draw.circle(SCREEN, (255, 255, 255), (r.centerx, r.centery), 6)

def draw_hud(player, speed):
    score = player.score if player else 0
    col = (255, 255, 255) if score >= 1000 else PALETTE["text"]
    lbl = "ZONE 1: SCHOOL HALLWAY" if score < 1000 else "ZONE 2: ARCADE CYBER GRID" if score < 2000 else "ZONE 3: METROPOLIS ROOFTOP"
    for i, t in enumerate([f"Score: {score}", f"Distance: {int(player.distance)} m", f"Speed: {speed:.1f}", lbl]):
        SCREEN.blit(FONT.render(t, True, col if i < 3 else PALETTE["cyan"] if score >= 2000 else PALETTE["pink"]), (20, 20 + i * 30))
    offset = 0
    for timer, text, color in [(player.coffee_boost_timer, "COFFEE SLOW", (230, 150, 20)), (player.magnet_timer, "MAGNET ACTIVE", (220, 40, 40)), (player.boots_timer, "BOUNCE BOOTS", (20, 210, 90))]:
        if timer > 0:
            pygame.draw.rect(SCREEN, color, (20, 150 + offset, int(timer * 15), 12))
            SCREEN.blit(FONT.render(text, True, (240, 240, 245)), (25, 148 + offset)); offset += 20
    pygame.draw.rect(SCREEN, (30, 25, 40) if score >= 1000 else (240, 240, 245), (WIDTH - 200, 20, 180, 50), border_radius=8)
    SCREEN.blit(FONT.render(f"Pages: {player.pages_collected}", True, col), (WIDTH - 165, 31))

def draw_home_menu(bg, hs, tp):
    bg.draw(0)
    tr = pygame.Rect(WIDTH // 2 - 270, HEIGHT // 2 - 180, 540, 85)
    pygame.draw.rect(SCREEN, (255, 255, 255), tr, border_radius=10)
    lbl = LARGE_FONT.render("ENDLESS HALLWAY RUNNER", True, (200, 40, 40))
    SCREEN.blit(lbl, lbl.get_rect(center=tr.center))
    p = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 50, 500, 100)
    pygame.draw.rect(SCREEN, (245, 240, 230), p, border_radius=12)
    SCREEN.blit(FONT.render(f"High Score Value: {hs}", True, PALETTE["text"]), (WIDTH // 2 - 100, p.top + 20))
    SCREEN.blit(FONT.render(f"Total Banked Pages: {tp}", True, (210, 60, 60)), (WIDTH // 2 - 100, p.top + 55))
    m = pygame.mouse.get_pos()
    r_btn = pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 + 90, 240, 65)
    s_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 90, 240, 65)
    pygame.draw.rect(SCREEN, PALETTE["btn_h"] if r_btn.collidepoint(m) else PALETTE["btn"], r_btn, border_radius=12)
    pygame.draw.rect(SCREEN, PALETTE["shop_h"] if s_btn.collidepoint(m) else PALETTE["shop"], s_btn, border_radius=12)
    for b, text in [(r_btn, "RUN ENGINE"), (s_btn, "OPEN UNIFIED SHOP")]:
        l = LARGE_FONT.render(text, True, (255, 255, 255)); SCREEN.blit(l, l.get_rect(center=b.center))
    return {"start_run": r_btn, "go_shop": s_btn}

def draw_unified_shop(total_pages, unlocked_items, active_skin, upgrade_levels):
    SCREEN.fill((22, 24, 34)); pygame.draw.rect(SCREEN, (15, 16, 24), (0, 0, WIDTH, 85))
    SCREEN.blit(LARGE_FONT.render("CAMPUS STORE: CUSTOM GEAR & UPGRADES", True, (255, 255, 255)), (40, 26))
    pygame.draw.rect(SCREEN, (40, 45, 65), (WIDTH - 280, 18, 240, 46), border_radius=8)
    SCREEN.blit(FONT.render(f"Available Pages: {total_pages}", True, (0, 255, 200)), (WIDTH - 235, 32))
    m, clicks = pygame.mouse.get_pos(), {}
    
    SCREEN.blit(LARGE_FONT.render("CHARACTER SKINS", True, PALETTE["cyan"]), (50, 115))
    catalog = [
        ("varsity_gold", "Varsity Gold Jacket", 5, "Prestige metallic trim, shades, & crimson decals.", 0),
        ("cyber_suit", "Neon Cyber-Mesh Suit", 12, "Obsidian tactical plating & high-frequency visors.", 1)
    ]
    for s_id, name, cost, desc, idx in catalog:
        box = pygame.Rect(50, 160 + (idx * 140), 520, 120)
        pygame.draw.rect(SCREEN, (32, 35, 48), box, border_radius=10)
        SCREEN.blit(LARGE_FONT.render(name, True, (255, 255, 255)), (70, box.top + 22))
        SCREEN.blit(FONT.render(desc, True, (160, 165, 185)), (70, box.top + 68))
        btn = pygame.Rect(box.right - 180, box.top + 30, 155, 60)
        if s_id in unlocked_items:
            pygame.draw.rect(SCREEN, (70, 75, 85) if active_skin == s_id else (PALETTE["shop_h"] if btn.collidepoint(m) else PALETTE["shop"]), btn, border_radius=8)
            txt = "EQUIPPED" if active_skin == s_id else "EQUIP"
        else:
            pygame.draw.rect(SCREEN, PALETTE["btn_h"] if btn.collidepoint(m) else PALETTE["btn"], btn, border_radius=8)
            txt = f"BUY: {cost}"
        lbl = FONT.render(txt, True, (255, 255, 255)); SCREEN.blit(lbl, lbl.get_rect(center=btn.center))
        clicks[f"skin_{s_id}"] = {"rect": btn, "cost": cost, "type": "skin"}

    SCREEN.blit(LARGE_FONT.render("POWERUP MODIFIERS", True, PALETTE["pink"]), (630, 115))
    powerups = [
        ("coffee_duration", "Caffeine Slow Extender", 4, "Prolong coffee slow down tier.", 0),
        ("magnet_range", "High-Grade Page Magnet", 6, "Pull far away pages effortlessly.", 1)
    ]
    for u_id, name, b_cost, desc, idx in powerups:
        box = pygame.Rect(630, 160 + (idx * 140), 520, 120)
        pygame.draw.rect(SCREEN, (32, 35, 48), box, border_radius=10)
        lvl = upgrade_levels.get(u_id, 1); cost = b_cost * lvl
        
        title_surf = LARGE_FONT.render(name, True, (255, 255, 255))
        SCREEN.blit(title_surf, (642, box.top + 26))
        
        lvl_surf = LARGE_FONT.render(f" (Lvl {lvl})", True, PALETTE["cyan"])
        SCREEN.blit(lvl_surf, (642 + title_surf.get_width(), box.top + 26))
        
        SCREEN.blit(FONT.render(desc, True, (160, 165, 185)), (642, box.top + 68))
        btn = pygame.Rect(box.right - 180, box.top + 30, 155, 60)
        if lvl >= 5: pygame.draw.rect(SCREEN, (50, 55, 60), btn, border_radius=8); txt = "MAX LEVEL"
        else: pygame.draw.rect(SCREEN, PALETTE["btn_h"] if btn.collidepoint(m) else PALETTE["btn"], btn, border_radius=8); txt = f"UPGRADE: {cost}"
        lbl = FONT.render(txt, True, (255, 255, 255)); SCREEN.blit(lbl, lbl.get_rect(center=btn.center))
        clicks[f"upg_{u_id}"] = {"rect": btn, "cost": cost, "type": "upgrade", "id": u_id}

    back = pygame.Rect(50, HEIGHT - 90, 300, 55)
    pygame.draw.rect(SCREEN, PALETTE["warn_h"] if back.collidepoint(m) else PALETTE["warn"], back, border_radius=8)
    lbl = FONT.render("RETURN TO MAIN MENU", True, (255, 255, 255)); SCREEN.blit(lbl, lbl.get_rect(center=back.center))
    return {"clickables": clicks, "back_btn": back}

def main():
    global CURRENT_PLAYING_CHANNEL, CURRENT_MUSIC_ID
    state, high_score, total_pages, unlocked_items, active_skin, upgrade_levels = "MENU", 0, 15, ["default"], "default", {"coffee_duration": 1, "magnet_range": 1}
    final_score = pages_run = 0; lvl2_t = lvl3_t = False; cooldown = 0.0  
    bg, particles, banners = DynamicBackground(), ParticleSystem(), BannerNotification()
    player = None; speed = 5.0; obstacles, pages, powerups = [], [], []; spawn_t = 1.2; running = True; caught, intro = None, None 

    while running:
        dt = min(0.04, max(0.001, CLOCK.tick(60) / 1000.0))
        mouse_c = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1: mouse_c = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running = False
                if state == "PLAYING" and e.key == pygame.K_r: state = "PAUSED"
                elif state == "PAUSED" and e.key == pygame.K_r: state = "PLAYING"
                elif state == "GAMEOVER" and e.key == pygame.K_r: state = "MENU"

        if state in ["MENU", "SHOP_SCREEN"]: play_soundtrack(MUSIC_LOBBY, "lobby")
        elif state == "PLAYING": play_soundtrack(MUSIC_ZONE3 if player.score >= 2000 else MUSIC_ZONE2 if player.score >= 1000 else MUSIC_ZONE1, "z3" if player.score >= 2000 else "z2" if player.score >= 1000 else "z1")
        elif state in ["CAUGHT_SCENE", "GAMEOVER", "PAUSED"] and CURRENT_PLAYING_CHANNEL:
            CURRENT_PLAYING_CHANNEL.stop(); CURRENT_PLAYING_CHANNEL = CURRENT_MUSIC_ID = None

        if state == "MENU":
            act = draw_home_menu(bg, high_score, total_pages)
            if mouse_c:
                m = pygame.mouse.get_pos()
                if act["start_run"].collidepoint(m):
                    player, intro, speed = Player(skin=active_skin), IntroChase(), 5.0
                    obstacles, pages, powerups, lvl2_t, lvl3_t, cooldown = [], [], [], False, False, 0.0
                    state = "PLAYING"
                elif act["go_shop"].collidepoint(m): state = "SHOP_SCREEN"

        elif state == "SHOP_SCREEN":
            node = draw_unified_shop(total_pages, unlocked_items, active_skin, upgrade_levels)
            if mouse_c:
                m = pygame.mouse.get_pos()
                if node["back_btn"].collidepoint(m): state = "MENU"
                for kid, inf in node["clickables"].items():
                    if inf["rect"].collidepoint(m):
                        if inf["type"] == "skin":
                            sid = kid.replace("skin_", "")
                            if sid in unlocked_items: active_skin = sid
                            elif total_pages >= inf["cost"]: total_pages -= inf["cost"]; unlocked_items.append(sid); active_skin = sid
                        elif inf["type"] == "upgrade":
                            uid = inf["id"]; clvl = upgrade_levels.get(uid, 1)
                            if clvl < 5 and total_pages >= inf["cost"]: total_pages -= inf["cost"]; upgrade_levels[uid] = clvl + 1

        elif state == "PLAYING":
            if cooldown > 0: cooldown -= dt; continue
            player.update(pygame.key.get_pressed(), obstacles, dt)
            speed = min(MAX_SPEED, speed + ACCELERATION)
            eff_speed = speed * 0.5 if player.coffee_boost_timer > 0 else speed
            player.distance += eff_speed * 12 * dt
            player.score = int((player.distance * 1.5) / 15.0) + (player.pages_collected * 50)
            high_score = max(high_score, player.score)
            lvl_id = 3 if player.score >= 2000 else 2 if player.score >= 1000 else 1

            if lvl_id == 3 and not lvl3_t: obstacles.clear(); pages.clear(); powerups.clear(); banners.trigger("LEVEL 3: ROOFTOP CHASE!"); lvl3_t = True; cooldown = 0.2
            elif lvl_id == 2 and not lvl2_t: obstacles.clear(); pages.clear(); powerups.clear(); banners.trigger("LEVEL 2: CYBER GRID!"); lvl2_t = True; cooldown = 0.2

            bg.update(dt, eff_speed); banners.update(dt)
            if intro and intro.active: intro.update(dt, eff_speed)

            spawn_t -= dt
            if spawn_t <= 0:
                spawn_t = max(0.65 if lvl_id == 3 else 0.85, 1.6 - speed * 0.04)
                obstacles.append(Obstacle(random.choice(["pipe", "vent", "drone", "laser_gate"]) if lvl_id == 3 else random.choice(["pipe", "low", "ink", "popquiz_high", "laser_gate"]) if lvl_id == 2 else random.choice(["pipe", "low", "popquiz_high"])))
                if random.random() < 0.6: pages.append(Page())
                if random.random() < 0.15: powerups.append(InGamePowerupItem(random.choice(["coffee", "magnet", "boots"])))

            for obs in obstacles[:]:
                obs.update(dt, eff_speed)
                if obs.x + obs.width < -150: obstacles.remove(obs)
                elif obs.check_headon_crash(player.get_rect(), player):
                    SFX_CATCH_DEATH.play(); caught = CaughtAnimation(player.x, player.y)
                    final_score, pages_run = player.score, player.pages_collected
                    total_pages += pages_run; state = "CAUGHT_SCENE"

            for pg in pages[:]:
                pg.update(dt, eff_speed, player); p_rect = player.get_rect()
                if pg.x + 20 < -100: pages.remove(pg)
                elif pg.get_rect().colliderect(p_rect): player.pages_collected += 1; pages.remove(pg)

            for item in powerups[:]:
                item.update(dt, eff_speed)
                if item.x + 40 < -100: powerups.remove(item)
                elif item.get_rect().colliderect(player.get_rect()):
                    if item.kind == "coffee": player.coffee_boost_timer = 4.0 + upgrade_levels.get("coffee_duration", 1) * 1.5
                    elif item.kind == "magnet": player.magnet_timer = 6.0 + upgrade_levels.get("magnet_range", 1) * 1.2
                    elif item.kind == "boots": player.boots_timer = 7.0
                    powerups.remove(item)

            bg.draw(player.score); particles.update_and_draw(dt, eff_speed, lvl_id, player.coffee_boost_timer > 0)
            for el in pages + powerups: el.draw()
            for obs in obstacles: obs.draw(player.score >= 1000)
            if intro and intro.active: intro.draw()
            player.draw(); draw_hud(player, speed); banners.draw()

        elif state == "CAUGHT_SCENE":
            bg.draw(final_score); caught.update(dt); caught.draw()
            if caught.phase == "DONE": state = "GAMEOVER"

        elif state in ["PAUSED", "GAMEOVER"]:
            SCREEN.fill((40, 40, 45) if state == "PAUSED" else (15, 12, 22))
            if state == "PAUSED":
                l = LARGE_FONT.render("ENGINE PAUSED - PRESS 'R' TO RESUME RUN", True, (255,255,255))
                SCREEN.blit(l, l.get_rect(center=(WIDTH//2, HEIGHT//2)))
            else:
                l1 = LARGE_FONT.render("Run Termination - Caught!", True, (255, 0, 70))
                l2 = FONT.render(f"Final Score: {final_score} | Banked Pages: +{pages_run}", True, (255,255,255))
                l3 = FONT.render("Press 'R' to return to Main Menu", True, (180,180,180))
                for i, l in enumerate([l1, l2, l3]): SCREEN.blit(l, l.get_rect(center=(WIDTH // 2, HEIGHT // 2 + (-40 if i==0 else 15 if i==1 else 65))))

        pygame.display.flip()
    pygame.quit(); sys.exit()

if __name__ == "__main__": main()