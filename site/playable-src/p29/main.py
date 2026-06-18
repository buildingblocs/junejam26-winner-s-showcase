import pygame
import sys
import random
import os
import asyncio

# ==========================================
# 1. INITIALIZATION & SETUP
# ==========================================
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ninten's Grand Adventure")

clock = pygame.time.Clock()
FPS = 60

COLOR_SKY = (107, 140, 255)
COLOR_GRASS = (34, 139, 34)
COLOR_DIRT = (139, 69, 19)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)

ui_font = pygame.font.SysFont("Courier", 36, bold=True)
small_font = pygame.font.SysFont("Courier", 24, bold=True)
large_font = pygame.font.SysFont("Courier", 48, bold=True)

# ==========================================
# 2. ADVANCED FLEXIBLE IMAGE LOADER
# ==========================================
FORCED_FOLDER_PATH = r"C:\Users\user\Desktop\Ammads Assignments\player_files"

def load_game_image_flexible(base_name, width, height, fallback_color):
    try:
        # Get everything in the folder
        folder_files = os.listdir(FORCED_FOLDER_PATH)
        
        # Look for any file that starts with the character name (ignoring extensions)
        matched_filename = None
        for filename in folder_files:
            if filename.lower().startswith(base_name.lower()):
                matched_filename = filename
                break
                
        if matched_filename:
            full_path = os.path.join(FORCED_FOLDER_PATH, matched_filename)
            image = pygame.image.load(full_path).convert_alpha()
            print(f"SUCCESS: Found and loaded '{matched_filename}' for {base_name}!")
            return pygame.transform.scale(image, (width, height))
        else:
            raise FileNotFoundError()
            
    except Exception as e:
        print(f"ERROR: Could not load any file starting with '{base_name}'.")
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(fallback_color)
        return surface

# Just provide the base name; the function handles all chaotic extensions automatically!
player_base_image = load_game_image_flexible('player', 60, 65, (0, 0, 255))
kermit_image = load_game_image_flexible('kermit', 55, 55, (0, 255, 0))
boss_image = load_game_image_flexible('boss', 135, 170, (255, 0, 0))

# ==========================================
# 3. GAME OBJECTS (SPRITE CLASSES)
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, base_img):
        super().__init__()
        self.right_image = base_img
        self.left_image = pygame.transform.flip(base_img, True, False)
        
        self.image = self.right_image
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.bottom = SCREEN_HEIGHT - 70 
        
        self.vel_y = 0
        self.speed = 6
        self.is_jumping = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.image = self.left_image  
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.image = self.right_image 

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and not self.is_jumping:
            self.vel_y = -21  
            self.is_jumping = True

    def update(self):
        self.vel_y += 0.8
        self.rect.y += self.vel_y

        if self.rect.bottom >= SCREEN_HEIGHT - 70:
            self.rect.bottom = SCREEN_HEIGHT - 70
            self.vel_y = 0
            self.is_jumping = False

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

    def get_collision_rect(self):
        # Return a smaller rect used for collisions (reduces hitbox)
        col = self.rect.copy()
        shrink_w = int(self.rect.width * 0.30)
        shrink_h = int(self.rect.height * 0.25)
        col.inflate_ip(-shrink_w, -shrink_h)
        col.center = self.rect.center
        return col


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, speed, img, is_boss=False):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.is_boss = is_boss
        self.rect.x = x
        self.rect.bottom = SCREEN_HEIGHT - 70
        self.speed = speed
        self.base_speed = speed
        self.vel_y = 0
        # only used for boss behavior
        if self.is_boss:
            self.jump_timer = random.randint(60, 180)
        self.hit_flash = 0  # For visual feedback when hit

    def update(self):
        self.rect.x -= self.speed
        
        if self.rect.left < 0:
            self.rect.left = 0
            self.speed = -self.speed 

        if self.rect.right > SCREEN_WIDTH and not self.is_boss:
            if self.speed < 0: 
                self.speed = -self.speed

        # Boss-specific vertical physics and jump behavior
        if self.is_boss:
            # gravity
            self.vel_y += 0.8
            self.rect.y += self.vel_y

            # countdown to next jump every frame
            self.jump_timer -= 1

            # landed on ground
            if self.rect.bottom >= SCREEN_HEIGHT - 70:
                self.rect.bottom = SCREEN_HEIGHT - 70
                if self.vel_y != 0:
                    self.vel_y = 0

                # if timer expired, perform a jump
                if self.jump_timer <= 0:
                    self.vel_y = -18
                    # bias horizontal movement toward the player when jumping
                    try:
                        if hero.rect.centerx < self.rect.centerx:
                            self.speed = abs(self.base_speed)
                        else:
                            self.speed = -abs(self.base_speed)
                    except Exception:
                        pass
                    self.jump_timer = random.randint(90, 180)
        
        # Handle hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= 1

# ==========================================
# 4. STATE & ENVIRONMENT INITIALIZATION
# ==========================================
player_group = pygame.sprite.GroupSingle()
hero = Player(player_base_image)
player_group.add(hero)

enemy_group = pygame.sprite.Group()

score = 0
boss_hp = 200
game_state = "WAVE_1"
wave_transition_timer = 0  # For wave transition delays
current_wave = 1

def spawn_wave(count, speed, img):
    enemy_group.empty()
    for i in range(count):
        spawn_x = 400 + (i * 140)
        kermit = Enemy(spawn_x, speed, img, is_boss=False)
        enemy_group.add(kermit)

spawn_wave(3, speed=3, img=kermit_image)

# ==========================================
# 5. MAIN LOOP
# ==========================================
async def main():
    global score, boss_hp, game_state, wave_transition_timer, current_wave

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
        # Handle wave transitions
        if wave_transition_timer > 0:
            wave_transition_timer -= 1
    
        if game_state in ["WAVE_1", "WAVE_2", "BOSS"]:
            hero.handle_input()
            player_group.update()
            enemy_group.update()

            for enemy in enemy_group:
                col_rect = hero.get_collision_rect()
                if col_rect.colliderect(enemy.rect):
                    # Check if jumping on top of enemy (use collision rect bottom)
                    if hero.vel_y > 0 and col_rect.bottom <= enemy.rect.top + 25:
                        hero.vel_y = -12  
                        enemy.hit_flash = 10  # Visual feedback
                    
                        if enemy.is_boss:
                            boss_hp -= 1
                            if boss_hp <= 0:
                                enemy.kill()
                                score += 250
                        else:
                            enemy.kill()
                            score += 100
                    # Hit from side or head - handle appropriately (use collision rect sides)
                    elif col_rect.right > enemy.rect.left and col_rect.left < enemy.rect.right:
                        # If player hit the enemy from below (head bump) while moving up,
                        # bounce the player downward instead of marking game over.
                        if hero.vel_y < 0 and col_rect.top < enemy.rect.bottom - 5:
                            hero.vel_y = 6
                        else:
                            # side collision -> game over
                            if not (hero.vel_y > 0 and col_rect.bottom <= enemy.rect.top + 25):
                                game_state = "GAME_OVER"

        # Wave completion logic
        if game_state == "WAVE_1" and len(enemy_group) == 0 and wave_transition_timer == 0:
            game_state = "WAVE_1_COMPLETE"
            wave_transition_timer = 180  # 3 seconds at 60 FPS
        
        elif game_state == "WAVE_1_COMPLETE" and wave_transition_timer == 0:
            game_state = "WAVE_2"
            current_wave = 2
            spawn_wave(4, speed=4, img=kermit_image) 
        
        elif game_state == "WAVE_2" and len(enemy_group) == 0 and wave_transition_timer == 0:
            game_state = "WAVE_2_COMPLETE"
            wave_transition_timer = 180
        
        elif game_state == "WAVE_2_COMPLETE" and wave_transition_timer == 0:
            game_state = "BOSS"
            saheer_boss = Enemy(SCREEN_WIDTH - 180, speed=1, img=boss_image, is_boss=True)
            boss_hp = 10
            enemy_group.add(saheer_boss)
        
        elif game_state == "BOSS" and boss_hp <= 0:
            game_state = "WIN"

        # --- Frame Render Layout ---
        screen.fill(COLOR_SKY)
    
        pygame.draw.rect(screen, COLOR_GRASS, (0, SCREEN_HEIGHT - 70, SCREEN_WIDTH, 25))
        pygame.draw.rect(screen, COLOR_DIRT, (0, SCREEN_HEIGHT - 45, SCREEN_WIDTH, 45))

        player_group.draw(screen)
        enemy_group.draw(screen)

        # ===== UI DISPLAY =====
        score_display = ui_font.render(f"SCORE: {str(score).zfill(5)}", True, COLOR_BLACK)
        screen.blit(score_display, (20, 20))

        # Wave indicator
        if game_state in ["WAVE_1", "WAVE_1_COMPLETE", "WAVE_2", "WAVE_2_COMPLETE", "BOSS"]:
            if game_state in ["WAVE_1_COMPLETE", "WAVE_2_COMPLETE"]:
                current_display = "COMPLETED" if "COMPLETE" in game_state else "ACTIVE"
                wave_label = ui_font.render(f"WAVE {current_wave} {current_display}", True, COLOR_GREEN)
            elif game_state == "BOSS":
                wave_label = ui_font.render("BOSS BATTLE!", True, COLOR_RED)
            else:
                wave_label = ui_font.render(f"WAVE {current_wave}: {len(enemy_group)} ENEMIES", True, COLOR_BLACK)
            screen.blit(wave_label, (SCREEN_WIDTH - 380, 20))

        # Boss HP bar
        if game_state == "BOSS":
            boss_label = ui_font.render(f"BOSS HP: {str(max(0, boss_hp)).zfill(2)}", True, COLOR_RED)
            screen.blit(boss_label, (SCREEN_WIDTH - 260, 70))
            pygame.draw.rect(screen, COLOR_BLACK, (SCREEN_WIDTH - 260, 110, 200, 20))
            pygame.draw.rect(screen, COLOR_RED, (SCREEN_WIDTH - 260, 110, max(0, boss_hp) * 40, 20))

        # On-screen controls display
        controls_y = SCREEN_HEIGHT - 110
        controls = [
            "CONTROLS:",
            "[ARROW KEYS / WASD] Move Left/Right",
            "[SPACE / UP / W] Jump",
            "[JUMP ON ENEMIES] To Defeat Them"
        ]
        for i, control in enumerate(controls):
            control_text = small_font.render(control, True, COLOR_BLACK)
            screen.blit(control_text, (20, controls_y + i * 25))

        # Wave completion screen
        if "COMPLETE" in game_state:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))
        
            complete_text = large_font.render("WAVE COMPLETE!", True, COLOR_YELLOW)
            complete_rect = complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(complete_text, complete_rect)
        
            next_text = small_font.render("Next Wave Starting...", True, COLOR_GREEN)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(next_text, next_rect)

        # Win screen
        if game_state == "WIN":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))
        
            win_display = large_font.render("You Have saved the world", True, COLOR_YELLOW)
            win_rect = win_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(win_display, win_rect)
        
            final_score = ui_font.render(f"FINAL SCORE: {score}", True, COLOR_WHITE)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(final_score, score_rect)

        # Game over screen
        elif game_state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BLACK)
            screen.blit(overlay, (0, 0))
        
            loss_display = large_font.render("GAME OVER", True, COLOR_RED)
            loss_rect = loss_display.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(loss_display, loss_rect)
        
            final_score = ui_font.render(f"FINAL SCORE: {score}", True, COLOR_WHITE)
            score_rect = final_score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(final_score, score_rect)

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
