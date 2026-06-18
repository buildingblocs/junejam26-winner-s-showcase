import asyncio
import pygame, sys, random, os, re

pygame.init()

# ==================== Changed game title ====================
pygame.display.set_caption("FootBottle")

# ==================== Constants ====================
SCREEN_W = 800
SCREEN_H = 500
FLOOR_Y = 420

GAME_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Load background image if available
BACKGROUND_IMAGE = None
background_filenames_to_try = [
    "background.jpeg", "background.jpg", "background.png",
    "backgroung.jpeg", "backgroung.jpg", "backgroung.png",
]
for bg_filename in background_filenames_to_try:
    bg_path = os.path.join(GAME_FOLDER, bg_filename)
    if os.path.isfile(bg_path):
        try:
            raw_image = pygame.image.load(bg_path).convert()
            BACKGROUND_IMAGE = pygame.transform.smoothscale(raw_image, (SCREEN_W, SCREEN_H))
            print(f"Background loaded: {bg_filename}")
            break
        except Exception as err:
            print(f"Could not load background {bg_filename}: {err}")

# Initialize screen
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()

# Fonts
font_big = pygame.font.SysFont("arial", 96, bold=True)
font_mid = pygame.font.SysFont("arial", 48, bold=True)
font_score = pygame.font.SysFont("arial", 36, bold=True)
font_small = pygame.font.SysFont("arial", 28)
font_label = pygame.font.SysFont("arial", 18, bold=True)

# Colors
GREEN = (45, 160, 45)
DARK_GREEN = (30, 110, 30)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (210, 60, 60)
BLUE = (60, 60, 210)
YELLOW = (255, 230, 50)
GREY = (130, 130, 130)
DARK_GREY = (80, 80, 80)
LIGHT_GREY = (180, 180, 180)
BOTTLE_BLUE = (190, 220, 255)
BOTTLE_CAP = (220, 50, 50)
BOTTLE_LBL = (80, 160, 240)

HUD_BG = (0, 0, 0, 160)
HUD_P1_COL = (180, 40, 40)
HUD_P2_COL = (40, 40, 180)
HUD_TIMER_BG = (30, 30, 30)
HUD_DIVIDER = (255, 255, 255, 60)

# Game settings
GOALS_TO_WIN = 5
MATCH_SECONDS = 300
GRAVITY = 0.45
BOUNCE = 0.52
FLOOR_FRIC = 0.93
PLAYER_SPEED = 3
JUMP_MIN = -10
JUMP_MAX = -17
JUMP_HOLD = -0.40
JUMP_FRAMES = 20
RESUME_WAIT = 3

# Bins
BIN_WIDTH = 60
BIN_HEIGHT = 80
BIN1_X = 90
BIN2_X = 710
BIN_CENTRES = (BIN1_X, BIN2_X)

def get_bin_rect(centre_x):
    left = centre_x - BIN_WIDTH // 2
    top = FLOOR_Y - BIN_HEIGHT
    return pygame.Rect(left, top, BIN_WIDTH, BIN_HEIGHT)

def get_bin_mouth_rect(centre_x):
    mouth_width = BIN_WIDTH - 10
    left = centre_x - mouth_width // 2
    top = FLOOR_Y - BIN_HEIGHT
    return pygame.Rect(left, top, mouth_width, 14)

class Background:
    def __init__(self):
        self.image = None
        for bg_filename in [
            "background.jpeg", "background.jpg", "background.png",
            "backgroung.jpeg", "backgroung.jpg", "backgroung.png",
        ]:
            path = os.path.join(GAME_FOLDER, bg_filename)
            if os.path.isfile(path):
                try:
                    raw_image = pygame.image.load(path).convert()
                    self.image = pygame.transform.smoothscale(raw_image, (SCREEN_W, SCREEN_H))
                    print(f"Background loaded: {bg_filename}")
                    break
                except Exception as err:
                    print(f"Could not load background {bg_filename}: {err}")

    def draw(self):
        if self.image:
            screen.blit(self.image, (0, 0))
        else:
            screen.fill(GREEN)
        pygame.draw.line(screen, DARK_GREEN, (0, FLOOR_Y), (SCREEN_W, FLOOR_Y), 3)
        pygame.draw.line(screen, DARK_GREEN, (SCREEN_W // 2, FLOOR_Y - 4), (SCREEN_W // 2, FLOOR_Y), 4)

class Player:
    def __init__(self, start_x, start_facing, colour):
        self.x = start_x
        self.y = FLOOR_Y
        self.vx = 0
        self.vy = 0
        self.on_floor = True
        self.facing = start_facing
        self.colour = colour
        self.w = 32
        self.h = 52
        self.frames = []  # sprite images not used
        self.anim_timer = 0
        self.anim_frame = 0
        self.kicking = False
        self.kick_timer = 0
        self.jump_held = 0
        self.charging = False

    def get_rect(self):
        left = self.x - self.w // 2
        top = self.y - self.h
        return pygame.Rect(left, top, self.w, self.h)

    def draw(self):
        x = int(self.x)
        y = int(self.y)
        if self.frames:
            # sprite drawing skipped
            pass
        else:
            col = self.colour
            w = self.w
            h = self.h
            pygame.draw.rect(screen, col, (x - w // 2, y - h, w, h - 14))
            pygame.draw.circle(screen, col, (x, y - h - 10), 14)
            # legs
            pygame.draw.rect(screen, col, (x - w // 2, y - 14, w // 2 - 1, 14))
            pygame.draw.rect(screen, col, (x + 1, y - 14, w // 2 - 1, 14))
            # kicking leg during kick animation
            if self.kicking and self.kick_timer < 12:
                kick_leg_x = x + self.facing * (w // 2 + 10)
                pygame.draw.rect(screen, col, (kick_leg_x - 6, y - 18, 12, 10))

class Bottle:
    def __init__(self):
        self.x = SCREEN_W // 2
        self.y = 180
        self.vx = random.choice([-2.5, 2.5])
        self.vy = 0

    def update(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        # Bounce off floor
        if self.y >= FLOOR_Y - 10:
            self.y = FLOOR_Y - 10
            self.vy *= -BOUNCE
            self.vx *= FLOOR_FRIC
            if abs(self.vy) < 1.5:
                self.vy = 0

        # Bounce off walls
        if self.x < 12:
            self.x = 12
            self.vx = abs(self.vx) * 0.7
        if self.x > SCREEN_W - 12:
            self.x = SCREEN_W - 12
            self.vx = -abs(self.vx) * 0.7

    def draw(self):
        x = int(self.x)
        y = int(self.y)
        pygame.draw.rect(screen, BOTTLE_BLUE, (x - 11, y - 30, 22, 30))
        pygame.draw.rect(screen, BOTTLE_BLUE, (x - 6, y - 44, 12, 16))
        pygame.draw.rect(screen, BOTTLE_CAP, (x - 6, y - 50, 12, 8))
        pygame.draw.rect(screen, BOTTLE_LBL, (x - 11, y - 22, 22, 9))

def push_bottle_out_of_rect(bottle, rect):
    BOTTLE_HALF = 10
    bx = bottle.x
    by = bottle.y - 20
    overlap_x = (BOTTLE_HALF + rect.w // 2) - abs(bx - rect.centerx)
    overlap_y = (BOTTLE_HALF + rect.h // 2) - abs(by - rect.centery)
    if overlap_x <= 0 or overlap_y <= 0:
        return False
    if overlap_x < overlap_y:
        if bx < rect.centerx:
            bottle.x -= overlap_x
        else:
            bottle.x += overlap_x
        bottle.vx *= -0.6
    else:
        if by < rect.centery:
            bottle.y -= overlap_y
        else:
            bottle.y += overlap_y
        bottle.vy *= -0.5
    return True

def bounce_bottle_off_player(bottle, player):
    if bottle.x >= player.x:
        direction = 1
    else:
        direction = -1
    if player.on_floor:
        min_speed = 4
        up_speed = -4
    else:
        min_speed = 5
        up_speed = -6
    horizontal_speed = max(abs(bottle.vx), min_speed)
    bottle.vx = direction * horizontal_speed + random.uniform(-1, 1)
    bottle.vy = up_speed

def try_kick(player, bottle):
    if not player.kicking:
        return False
    if not (4 <= player.kick_timer <= 10):
        return False
    foot_x = player.x + player.facing * (player.w // 2 + 14)
    foot_y = player.y - 16
    dx = bottle.x - foot_x
    dy = (bottle.y - 20) - foot_y
    if dx * player.facing < 0:
        return False
    distance = (dx * dx + dy * dy) ** 0.5
    if distance > 42:
        return False
    # Connect kick
    bottle.vx = player.facing * 9 + random.uniform(-1.5, 1.5)
    bottle.vy = random.uniform(-14, -11)
    return True

def update_player(player, keys, left_key, right_key, jump_key):
    moving = False
    if not player.kicking:
        if keys[left_key] and player.x - player.w // 2 > 0:
            player.x -= PLAYER_SPEED
            player.facing = -1
            moving = True
        if keys[right_key] and player.x + player.w // 2 < SCREEN_W:
            player.x += PLAYER_SPEED
            player.facing = 1
            moving = True
    # Jumping
    if keys[jump_key] and player.on_floor:
        player.charging = True
        player.jump_held = 1
        player.on_floor = False
        player.vy = JUMP_MIN
    elif player.charging and keys[jump_key] and player.vy < 0 and player.jump_held < JUMP_FRAMES:
        player.jump_held += 1
        player.vy += JUMP_HOLD
    elif player.charging:
        player.charging = False
    # Animation
    if player.frames:
        # sprite code skipped
        pass
    else:
        if player.kicking:
            player.anim_frame = min(player.kick_timer // 5, 3)
        elif not player.on_floor:
            player.anim_frame = 3
        elif moving:
            player.anim_timer += 1
            if player.anim_timer >= 10:
                player.anim_timer = 0
                player.anim_frame = (player.anim_frame + 1) % 4
        else:
            player.anim_frame = 0
    # Gravity
    player.vy += GRAVITY
    player.y += player.vy
    if player.y >= FLOOR_Y:
        player.y = FLOOR_Y
        player.vy = 0
        player.on_floor = True
    # Kick timer
    if player.kicking:
        player.kick_timer += 1
        if player.kick_timer > 18:
            player.kicking = False
            player.kick_timer = 0

class HUD:
    def __init__(self):
        pass

    def draw(self, score1, score2, time_left):
        hud_h = 54
        panel_w = 180
        timer_w = 120
        hud_y = 0
        p1_x = 0
        timer_x = (SCREEN_W - timer_w) // 2
        p2_x = SCREEN_W - panel_w

        hud_bar = pygame.Surface((SCREEN_W, hud_h), pygame.SRCALPHA)
        hud_bar.fill(HUD_BG)
        screen.blit(hud_bar, (0, hud_y))

        # Player 1 panel
        p1_panel = pygame.Surface((panel_w, hud_h), pygame.SRCALPHA)
        p1_panel.fill((*HUD_P1_COL, 220))
        screen.blit(p1_panel, (p1_x, hud_y))
        label1 = font_label.render("P1", True, (255, 200, 200))
        screen.blit(label1, (p1_x + 14, hud_y + 8))
        score1_text = font_score.render(str(score1), True, WHITE)
        screen.blit(score1_text, (p1_x + panel_w - score1_text.get_width() - 14, hud_y + 10))
        pygame.draw.line(screen, (255, 255, 255, 80), (p1_x + panel_w - 1, hud_y), (p1_x + panel_w - 1, hud_y + hud_h), 1)

        # Player 2 panel
        p2_panel = pygame.Surface((panel_w, hud_h), pygame.SRCALPHA)
        p2_panel.fill((*HUD_P2_COL, 220))
        screen.blit(p2_panel, (p2_x, hud_y))
        label2 = font_label.render("P2", True, (200, 200, 255))
        screen.blit(label2, (p2_x + panel_w - label2.get_width() - 14, hud_y + 8))
        score2_text = font_score.render(str(score2), True, WHITE)
        screen.blit(score2_text, (p2_x + 14, hud_y + 10))
        pygame.draw.line(screen, (255, 255, 255, 80), (p2_x, hud_y), (p2_x, hud_y + hud_h), 1)

        # Timer
        timer_panel = pygame.Surface((timer_w, hud_h), pygame.SRCALPHA)
        timer_panel.fill((*HUD_TIMER_BG, 230))
        screen.blit(timer_panel, (timer_x, hud_y))
        mins = time_left // 60
        secs = time_left % 60
        time_str = f"{mins}:{secs:02d}"
        timer_colour = (255, 80, 80) if time_left < 60 else WHITE
        timer_text = font_mid.render(time_str, True, timer_colour)
        tx = timer_x + (timer_w - timer_text.get_width()) // 2
        ty = hud_y + (hud_h - timer_text.get_height()) // 2
        screen.blit(timer_text, (tx, ty))
        pygame.draw.line(screen, (255, 255, 255, 60), (0, hud_y + hud_h - 1), (SCREEN_W, hud_y + hud_h - 1), 1)

        # Goal dots
        dot_y = hud_h + 4
        dot_spacing = 14
        dot_r = 4
        dots_start_x1 = timer_x - (GOALS_TO_WIN * dot_spacing)
        for i in range(GOALS_TO_WIN):
            dot_x = dots_start_x1 + i * dot_spacing
            filled = i < score1
            color = (220, 80, 80) if filled else (80, 30, 30)
            pygame.draw.circle(screen, color, (dot_x, dot_y), dot_r)
            pygame.draw.circle(screen, (255, 100, 100), (dot_x, dot_y), dot_r, 1)
        dots_start_x2 = timer_x + timer_w + dot_spacing
        for i in range(GOALS_TO_WIN):
            dot_x = dots_start_x2 + i * dot_spacing
            filled = i < score2
            color = (80, 80, 220) if filled else (30, 30, 80)
            pygame.draw.circle(screen, color, (dot_x, dot_y), dot_r)
            pygame.draw.circle(screen, (100, 100, 255), (dot_x, dot_y), dot_r, 1)

def draw_bin(centre_x):
    r = get_bin_rect(centre_x)
    pygame.draw.rect(screen, DARK_GREY, r)
    pygame.draw.rect(screen, (55, 55, 55), (r.x - 3, r.y - 6, r.w + 6, 10))
    gap = r.w // 4
    for i in range(1, 4):
        rib_x = r.x + i * gap
        pygame.draw.rect(screen, GREY, (rib_x, r.y + 6, 5, r.h - 10))

def draw_bottle(bottle):
    bottle.draw()

def draw_player(player):
    player.draw()

def draw_charge_bar(player):
    if not player.charging or not player.on_floor:
        return
    fill_amount = min(player.jump_held / JUMP_FRAMES, 1.0)
    bar_width = 34
    bar_x = int(player.x) - bar_width // 2
    bar_y = int(player.y) - player.h - 24
    pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, 5))
    r = int(255 * (1 - fill_amount))
    g = int(200 * fill_amount + 55)
    pygame.draw.rect(screen, (r, g, 0), (bar_x, bar_y, int(bar_width * fill_amount), 5))

def draw_text_centred(text, font, colour, y):
    surface = font.render(text, True, colour)
    screen.blit(surface, (SCREEN_W // 2 - surface.get_width() // 2, y))

# ==================== Define the Game class BEFORE main ====================
class Game:
    def __init__(self):
        self.background = Background()
        self.hud = HUD()
        self.p1 = Player(130, 1, RED)
        self.p2 = Player(670, -1, BLUE)
        self.bottle = Bottle()
        self.score1 = 0
        self.score2 = 0
        self.p1_kicked = False
        self.p2_kicked = False
        self.start_ms = pygame.time.get_ticks()
        self.total_paused_ms = 0
        self.paused = False
        self.pause_start_ms = None
        self.resume_start_ms = None
        self.game_over = False
        self.result_text = ""
        self.clock = pygame.time.Clock()

    async def run(self):
        while True:
            await asyncio.sleep(0)
            self.clock.tick(60)
            now_ms = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return
                    if not self.game_over:
                        if event.key == pygame.K_p:
                            if not self.paused:
                                self.paused = True
                                self.pause_start_ms = now_ms
                            elif self.resume_start_ms is None:
                                self.resume_start_ms = now_ms
                        if not self.paused:
                            if event.key == pygame.K_e and not self.p1.kicking:
                                self.p1.kicking = True
                                self.p1.kick_timer = 0
                                self.p1_kicked = False
                            if event.key == pygame.K_u and not self.p2.kicking:
                                self.p2.kicking = True
                                self.p2.kick_timer = 0
                                self.p2_kicked = False

            if self.paused and self.resume_start_ms is not None:
                if now_ms - self.resume_start_ms >= RESUME_WAIT * 1000:
                    self.total_paused_ms += now_ms - self.pause_start_ms
                    self.pause_start_ms = None
                    self.resume_start_ms = None
                    self.paused = False

            timer_now = self.pause_start_ms if self.paused else now_ms
            time_left = max(0, MATCH_SECONDS - (timer_now - self.start_ms - self.total_paused_ms) // 1000)

            if self.game_over:
                self.draw_scene(time_left)
                self.draw_game_over()
                pygame.display.flip()
                continue
            if self.paused:
                self.draw_scene(time_left)
                if self.resume_start_ms is not None:
                    secs = max(0, RESUME_WAIT - int((now_ms - self.resume_start_ms) / 1000))
                    self.draw_pause_overlay(secs)
                else:
                    self.draw_pause_overlay()
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()

            update_player(self.p1, keys, pygame.K_a, pygame.K_d, pygame.K_w)
            update_player(self.p2, keys, pygame.K_j, pygame.K_l, pygame.K_i)

            # Update bottle
            self.bottle.update()

            # Collisions with walls and bins
            for cx in BIN_CENTRES:
                rect = get_bin_rect(cx)
                for wall in [pygame.Rect(rect.x, rect.y, 5, rect.h), pygame.Rect(rect.right - 5, rect.y, 5, rect.h), pygame.Rect(rect.x, rect.bottom - 5, rect.w, rect.h)]:
                    push_bottle_out_of_rect(self.bottle, wall)

            # Collisions with players
            for player in [self.p1, self.p2]:
                rect = player.get_rect()
                if push_bottle_out_of_rect(self.bottle, rect):
                    bounce_bottle_off_player(self.bottle, player)

            # Kicks
            if not self.p1_kicked and try_kick(self.p1, self.bottle):
                self.p1_kicked = True
            if not self.p2_kicked and try_kick(self.p2, self.bottle):
                self.p2_kicked = True

            # Goal check
            for cx, who_scores in [(BIN1_X, "p2"), (BIN2_X, "p1")]:
                mouth = get_bin_mouth_rect(cx)
                bottle_x = int(self.bottle.x)
                bottle_y = int(self.bottle.y) - 20
                if self.bottle.vy > 0 and mouth.collidepoint(bottle_x, bottle_y):
                    if who_scores == "p1":
                        self.score1 += 1
                    else:
                        self.score2 += 1
                    self.bottle = Bottle()
                    self.p1_kicked = False
                    self.p2_kicked = False
                    break

            # Win or time up
            if self.score1 >= GOALS_TO_WIN:
                self.game_over = True
                self.result_text = "P1 WINS!"
            elif self.score2 >= GOALS_TO_WIN:
                self.game_over = True
                self.result_text = "P2 WINS!"
            elif time_left == 0:
                self.game_over = True
                if self.score1 > self.score2:
                    self.result_text = "P1 WINS!"
                elif self.score2 > self.score1:
                    self.result_text = "P2 WINS!"
                else:
                    self.result_text = "DRAW!"

            # Draw everything
            self.draw_scene(time_left)
            pygame.display.flip()

    def draw_scene(self, time_left):
        self.background.draw()
        for cx in BIN_CENTRES:
            draw_bin(cx)
        self.bottle.draw()
        self.p1.draw()
        self.p2.draw()
        if not self.game_over:
            self.draw_bars()
        self.hud.draw(self.score1, self.score2, time_left)

    def draw_bars(self):
        # draw charge bars if charging
        if self.p1.charging:
            draw_charge_bar(self.p1)
        if self.p2.charging:
            draw_charge_bar(self.p2)

    def draw_game_over(self):
        big_text = font_big.render(self.result_text, True, YELLOW)
        hint_text = font_small.render("press R to play again", True, LIGHT_GREY)
        screen.blit(big_text, (SCREEN_W // 2 - big_text.get_width() // 2, 175))
        screen.blit(hint_text, (SCREEN_W // 2 - hint_text.get_width() // 2, 285))

    def draw_pause_overlay(self, countdown=None):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        if countdown is None:
            draw_text_centred("PAUSED", font_big, WHITE, SCREEN_H // 2 - 60)
        else:
            draw_text_centred(f"RESUMING IN {countdown}", font_big, YELLOW, SCREEN_H // 2 - 60)

# ==================== Main game loop ====================
async def main():
    while True:
        game = Game()
        result = await game.run()
        if result == "quit":
            break
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
