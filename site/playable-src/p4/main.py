import asyncio
import pygame
from Objects import *
import random

try:
    import webbrowser
except Exception:
    webbrowser = None

pygame.init()

# =========================
# WINDOW
# =========================
WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fractured Light")
clock = pygame.time.Clock()

# =========================
# SETUP
# =========================
player = Player(100, 100)
room = Room(20, 12)

# Emitters – only the first one starts powered
emitters = [
    Emitter(128, 0, "down", emitter_id=1, starts_powered=True),
    Emitter(196, 660, "right", emitter_id=2, starts_powered=False),
    Emitter(384, 596, "up", emitter_id=3, starts_powered=False),
    Emitter(832, 0, "right", emitter_id=4, starts_powered=False),
]

receivers = [
    Receiver(128, 660, receiver_id=1),
    Receiver(384, 660, receiver_id=2),
    Receiver(768, 0, receiver_id=3),
    Receiver(1152, 640, receiver_id=4),
]

mirrors = [
    Mirror(1152, 256),
    Mirror(384, 384, angle=45),
    Mirror(128, 128),
    Mirror(1152,386)
]

glasses = [
    Glass(512, 256),
    Glass(512, 320),
    Glass(960, 256),
    Glass(960, 512),
]

walls = [
    Wall(320,0),
    Wall(320, 64),
    Wall(320, 128),
    Wall(320, 192),
    Wall(320, 256),
    Wall(320, 320),
    Wall(320, 384),
    Wall(320, 448),
    Wall(320, 512),
    Wall(320, 576),

    Wall(448,640),
    Wall(448, 64),
    Wall(448, 128),
    Wall(448, 192),
    Wall(448, 256),
    Wall(448, 320),
    Wall(448, 384),
    Wall(448, 448),
    Wall(448, 512),
    Wall(448, 576),

    Wall(768,640),
    Wall(768, 64),
    Wall(768, 128),
    Wall(768, 192),
    Wall(768, 256),
    Wall(768, 320),
    Wall(768, 384),
    Wall(768, 448),
    Wall(768, 512),
    Wall(768, 576),

    Wall(1088,320),
    Wall(1024,320),
    Wall(960,320),
    Wall(1216,320),
    Wall(1152,320),
]

# All objects that block movement (for collision and push/pull)
all_obstacles = walls + mirrors + glasses + emitters + receivers

# Initial beams (only from emitters that start powered)
beams = []
for emitter in emitters:
    if emitter.starts_powered:
        grid_x = (emitter.x // TILE_SIZE) * TILE_SIZE
        grid_y = (emitter.y // TILE_SIZE) * TILE_SIZE
        beams.append(Beam(grid_x, grid_y, emitter.direction, strength=12))

# Win state variables
game_won = False
win_timer = 0
video_opened = False
win_font = pygame.font.Font(None, 120)
sub_font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 40)

# YouTube video URL
YOUTUBE_URL = "https://www.youtube.com/watch?v=YAgJ9XugGBo"

# =========================
# MAIN LOOP
# =========================
async def main():
    global beams, game_won, win_timer, video_opened

    running = True
    while running:
        # -------------------------
        # EVENTS
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
                # Space to restart after winning
                if event.key == pygame.K_SPACE and game_won:
                    game_won = False
                    win_timer = 0
                    video_opened = False
                    for receiver in receivers:
                        receiver.powered = False
                    for emitter in emitters:
                        if not emitter.starts_powered:
                            emitter.powered = False
                    beams = []
                    for emitter in emitters:
                        if emitter.starts_powered:
                            beams.append(Beam(emitter.x, emitter.y, emitter.direction, strength=12))

                if not game_won:
                    # Rotate mirrors
                    if event.key == pygame.K_RIGHT:
                        for mirror in mirrors:
                            if object_near_player(player, mirror):
                                mirror.angle -= 27.5
                                mirror.angle %= 360
                    if event.key == pygame.K_LEFT:
                        for mirror in mirrors:
                            if object_near_player(player, mirror):
                                mirror.angle += 27.5
                                mirror.angle %= 360

                    # Push (E)
                    if event.key == pygame.K_e:
                        for glass in glasses:
                            if object_near_player(player, glass):
                                move_object(player, glass, all_obstacles)
                        for mirror in mirrors:
                            if object_near_player(player, mirror):
                                move_object(player, mirror, all_obstacles)

                    # Pull (Q)
                    if event.key == pygame.K_q:
                        for glass in glasses:
                            if object_near_player(player, glass):
                                pull_object(player, glass, all_obstacles)
                        for mirror in mirrors:
                            if object_near_player(player, mirror):
                                pull_object(player, mirror, all_obstacles)

        # -------------------------
        # UPDATE
        # -------------------------
        if not game_won:
            player.update(walls, mirrors, glasses, emitters, receivers)

            # Keep player inside window
            player.x = max(0, min(player.x, WIDTH - player.width))
            player.y = max(0, min(player.y, HEIGHT - player.height))

            # Refresh beams based on current receiver/emitter state
            beams = update_emitter_power(emitters, receivers, beams, walls, glasses, mirrors)

            # Check win condition: ALL receivers powered
            all_powered = all(receiver.powered for receiver in receivers)
        
            if all_powered and len(receivers) > 0:
                game_won = True
                win_timer = pygame.time.get_ticks()

        # -------------------------
        # DRAW
        # -------------------------
        if not game_won:
            # Normal game screen
            screen.fill((200, 200, 200))

            # Floor
            for tile in room.floors:
                tile.draw(screen)

            # Draw beams (including reflections)
            all_child_beams = []
            for beam in beams:
                child_beams = beam.draw(screen, walls, glasses, mirrors)
                all_child_beams.extend(child_beams)

            depth = 0
            while all_child_beams and depth < 10:
                next_beams = []
                for child in all_child_beams:
                    result = child.draw(screen, walls, glasses, mirrors)
                    if result:
                        next_beams.extend(result)
                all_child_beams = next_beams
                depth += 1

            # Draw objects
            for emitter in emitters:
                emitter.draw(screen)
            for receiver in receivers:
                receiver.draw(screen)
            for glass in glasses:
                glass.draw(screen)
            for mirror in mirrors:
                mirror.draw(screen)
            for wall in walls:
                wall.draw(screen)
            player.draw(screen)
    
        else:
            # WIN SCREEN
            current_time = pygame.time.get_ticks()
            elapsed = current_time - win_timer
        
            # Open YouTube video once
            if not video_opened:
                if webbrowser is not None:
                    try:
                        webbrowser.open(YOUTUBE_URL)
                    except Exception:
                        pass
                video_opened = True
        
            # Black background
            screen.fill((0, 0, 0))
        
            # Pulsing green "YOU WIN!" text
            pulse = (abs((elapsed % 1000) - 500)) / 500  # 0 to 1
            green_val = int(100 + 155 * pulse)
            color = (0, green_val, 0)
            glow_color = (0, int(green_val * 0.3), 0)
        
            # Glow effect (drawn first, behind main text)
            for offset in range(8, 0, -2):
                glow_text = win_font.render("YOU WIN!", True, glow_color)
                glow_rect = glow_text.get_rect(center=(WIDTH // 2 + offset, HEIGHT // 2 - 50 + offset))
                screen.blit(glow_text, glow_rect)
        
            # Main win text
            win_text = win_font.render("YOU WIN!", True, color)
            win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(win_text, win_rect)
        
            # Subtitle
            sub_text = sub_font.render("All Receivers Powered!", True, (255, 255, 255))
            sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(sub_text, sub_rect)
        
            # YouTube link text
            link_text = small_font.render("Check your browser for a surprise!", True, (200, 200, 200))
            link_rect = link_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 110))
            screen.blit(link_text, link_rect)
        
            # Restart instruction (blinking)
            if (elapsed // 800) % 2 == 0:
                restart_text = small_font.render("Press SPACE to play again", True, (150, 150, 150))
                restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 170))
                screen.blit(restart_text, restart_rect)
        
            # Sparkle particles
            for i in range(30):
                random.seed(i * 123 + elapsed // 50)
                sparkle_x = random.randint(0, WIDTH)
                sparkle_y = random.randint(0, HEIGHT)
                sparkle_size = random.randint(2, 6)
                sparkle_alpha = random.randint(50, 200)
            
                sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surf, (0, 255, 0, sparkle_alpha), 
                                 (sparkle_size, sparkle_size), sparkle_size)
                screen.blit(sparkle_surf, (sparkle_x, sparkle_y))
        
            # Confetti-like rectangles
            for i in range(15):
                random.seed(i * 456 + elapsed // 30)
                confetti_x = random.randint(0, WIDTH)
                confetti_y = random.randint(0, HEIGHT)
                confetti_w = random.randint(10, 30)
                confetti_h = random.randint(5, 15)
                confetti_color = random.choice([(0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)])
                confetti_alpha = random.randint(100, 200)
            
                confetti_surf = pygame.Surface((confetti_w, confetti_h), pygame.SRCALPHA)
                confetti_surf.fill((*confetti_color, confetti_alpha))
                screen.blit(confetti_surf, (confetti_x, confetti_y))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())