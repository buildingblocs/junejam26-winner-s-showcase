import pygame, sys
from dataclasses import dataclass, field

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("bleach rush")
clock = pygame.time.Clock()

bg_surf = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0.png").convert()
ground_surf = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0 (1).png").convert()
head_surf = pygame.Surface((800, 80))
head_surf.fill((255, 255, 255))

pygame.key.set_repeat(0)
#--------------------------CLASSES--------------------------
@dataclass
class Health:
    hp: int
    max_hp: int

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
        
    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

#-------------------------------------------------------------
@dataclass
class Player:
    x: int
    y: int
    color: tuple
    size: int
    health: Health = field(default_factory=lambda: Health(100, 100))

    def draw(self):
        model = pygame.image.load("C:\\Users\\User\\Downloads\\goodguyguy.png").convert_alpha()
        screen.blit(model, (self.x,self.y))

    def display_hp(self,pos):
        hp_surface = pygame.font.Font(None, 30).render(f'Your HP: {self.health.hp:.1f}/{self.health.max_hp}', True, (0,0,0))
        screen.blit(hp_surface, pos)
    
    def die(self):
        u_died = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0 (2).png").convert()
        screen.blit(u_died, (0,0))


player = Player(0, 200, (0, 0, 255), 50)
#-------------------------------------------------------------
@dataclass
class Enemy:
    x: int
    y: int
    color: tuple
    size: int
    health: Health = field(default_factory=lambda: Health(100, 100))

    def draw(self, surface):
        badguy = pygame.image.load("C:\\Users\\User\\OneDrive\\Pictures\\Screenshots\\Screenshot 2026-06-11 224756.png").convert_alpha()
        screen.blit(badguy, (self.x, self.y))

    def display_hp(self,pos):
        hp_surface = pygame.font.Font(None, 30).render(f'Enemy HP: {self.health.hp:.1f}/{self.health.max_hp}', True, (170,0,0))
        screen.blit(hp_surface, pos)
    

enemy = Enemy(400, 200, (255, 0, 0), 50)
#---------------------------COUNTERS-----------------------------
dead_counter = 5
p_def_counter = 0
e_def_counter = 0
counter1 = 0
counter2 = 0
kill_counter = 0
kill_counter_curr = kill_counter
cutscene_counter = 7
def display_counters():
    counter1_surface = pygame.font.Font(None, 30).render(f'Attack[1] cd: {counter1:.1f}', True, (75,75,255))
    counter2_surface = pygame.font.Font(None, 30).render(f'Heal[2] cd: {counter2:.1f}', True, (100,255,100))
    kill_counter_surface = pygame.font.Font(None, 30).render(f'Kills: {kill_counter_curr}', True, (0,0,0))
    screen.blit(counter1_surface, (10, 40))
    screen.blit(counter2_surface, (200, 40))
    screen.blit(kill_counter_surface, (700, 40))
#---------------------CUTSCENES-------------------------
cutscene1 = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0 (3).png").convert()
cutscene2 = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0 (4).png").convert()
cutscene3 = pygame.image.load("C:\\Users\\User\\Downloads\\pixil-frame-0 (5).png").convert()
cutscene1_done = False
cutscene2_done = False
#---------------------SOUNDS----------------------------------
pygame.mixer.init()
pygame.mixer_music.load("C:\\Users\\User\\Downloads\\sillystartingscreenmusic.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)
#----------------------MAIN GAME------------------------------
paused = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    while cutscene1_done == False:
        screen.blit(cutscene1, (0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    cutscene1_done = True
        pygame.display.update()

    while cutscene2_done == False:
        screen.blit(cutscene2, (0,0))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    cutscene2_done = True
                    pygame.mixer.music.stop()
                    pygame.mixer_music.load("C:\\Users\\User\\Downloads\\gamebgmusic.wav")
                    pygame.mixer.music.play(-1)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.update()

    if kill_counter == 10:
        pygame.mixer.music.stop()
        wasted_all_my_time_on_this = pygame.mixer.Sound("C:\\Users\\User\\Downloads\\wastedallmytimeforthis.wav")
        wasted_all_my_time_on_this.play()
        while cutscene_counter > 0:
            screen.blit(cutscene3,(0,0))
            cutscene_counter -= 1/60

            pygame.display.update()
            clock.tick(60)
        running = False

    if player.x < 250 or enemy.health.hp <= 0:
        player.x += 5
    else:
        player.x = 250

        if p_def_counter <= 0:
            p_def_counter = 0
        if e_def_counter <= 0:
            e_def_counter = 0
        if counter1 <= 0:
            counter1 = 0
        if counter2 <= 0:
            counter2 = 0

        if e_def_counter == 0:
            player.health.take_damage(5 + kill_counter*1.2)
            e_def_counter = 1.5
        if e_def_counter > 0:
            e_def_counter -= 1/60

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            if p_def_counter == 0:
                enemy.health.take_damage(3)
                p_def_counter = 0.2
        if p_def_counter > 0:
            p_def_counter -= 1/60
        if keys[pygame.K_1]:
            if counter1 == 0:
                enemy.health.take_damage(15 + kill_counter*0.5)
                counter1 = 10
        if counter1 > 0:
            counter1 -= 1/60
        if keys[pygame.K_2]:
            if counter2 == 0:
                player.health.heal(20 + kill_counter)
                counter2 = 7
        if counter2 > 0:
            counter2 -= 1/60

        if player.health.hp <= 0:
            player.die()
            pygame.display.update()
            paused = True
    if player.x >= 800:
        kill_counter += 1
        player.x = 0
        player.health.heal(30)
        counter1 = 0
        counter2 = 0
        enemy = Enemy(400, 200, (255, 0, 0), 50)
        enemy.health.max_hp += kill_counter*5
        enemy.health.hp = enemy.health.max_hp


    screen.fill((255,255,255))
    screen.blit(bg_surf, (0, 0))
    screen.blit(ground_surf, (0, 450))
    screen.blit(head_surf, (0, 0))
    player.draw()
    player.display_hp((10, 10))
    if enemy.health.hp > 0:
        enemy.draw(screen)
    elif kill_counter_curr == kill_counter:
        kill_counter_curr += 1
    enemy.display_hp((200, 10))
    display_counters()
    if paused == False:
        pygame.display.update()
    else:
        while dead_counter > 0:
            if dead_counter > 0:
                dead_counter -= 1/60
            clock.tick(60)
        running = False
    clock.tick(60)

pygame.quit()
sys.exit()