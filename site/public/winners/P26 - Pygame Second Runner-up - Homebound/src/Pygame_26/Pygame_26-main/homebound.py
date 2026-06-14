# required dependencies
import pygame
import random
from pygame import mixer

# initialise pygame
pygame.init()
mixer.init()

# configuration
screen = pygame.display.set_mode() 
pygame.display.set_caption('Homebound') 

# load images
bg = pygame.image.load('./assets/images/bg.png')
room = pygame.image.load('./assets/images/room.png')
room2 = pygame.image.load('./assets/images/room2.png')
agent = pygame.image.load('./assets/images/agent.png')
agent2 = pygame.image.load('./assets/images/agent2.png')
dinner = pygame.image.load('./assets/images/dinner.png')
bedroom = pygame.image.load('./assets/images/bedroom.png')
day_bg = pygame.image.load('./assets/images/day.png')
shop_icon = pygame.image.load('./assets/icons/shop_icon.png')
shop = pygame.image.load('./assets/images/shop.png')
coin_icon = pygame.image.load('./assets/icons/coins.png')
close_icon = pygame.image.load('./assets/icons/cross.png')
mosquito_img = pygame.image.load('./assets/images/mosquito.png')
rice_drop_bg = pygame.image.load('./assets/images/background_v6.jpg')

# load audios
mixer.music.load("./assets/audio/bg.mp3")
knock = mixer.Sound("./assets/audio/knock.mp3")
mosquito_sound = mixer.Sound("./assets/audio/mosquito.mp3")
impact_sound = mixer.Sound("./assets/audio/impact.mp3")
impact_channel = pygame.mixer.Channel(2)
explosion_sound = mixer.Sound('./assets/audio/explosion.wav')

# play bg music infinitely
mixer.music.set_volume(0.3)
mixer.music.play(-1)

# icons
# get width and height of screen
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

shop_icon_rect = shop_icon.get_rect()
shop_icon_rect.topright = (SCREEN_WIDTH - 100, 10)

coin_rect = coin_icon.get_rect()
coin_rect.midright = (
    shop_icon_rect.left - 120, 
    shop_icon_rect.centery
)

close_rect = close_icon.get_rect(topright=(SCREEN_WIDTH - 15, 10))

# scale bedroom
bedroom = pygame.transform.scale(bedroom, (SCREEN_WIDTH, SCREEN_HEIGHT))

# initialise variables
font_colour = (0, 0, 0)
font = pygame.font.SysFont('Arial', 50)
text = font.render('Play', True, font_colour)
show_button = True
day = 1
coins = 0
knock_played = False
show_day_text = False
day_text_timer = 0
DAY_TEXT_DURATION = 5
clock = pygame.time.Clock()
current_bg = bg
previous_bg = room
play = False
game_minutes = 17 * 60
REAL_SECONDS_PER_TICK = 5
GAME_MINUTES_PER_TICK = 15
time_passed = 0
mosquito_sound_playing = True
minigame_played = False

mosquitoes = []
mosquito_rects = []
mosquito_active = False
MOSQUITO_COIN_REWARD = 5

# helper functions
def spawn_mosquitoes():
    global mosquitoes, mosquito_rects, mosquito_active

    mosquitoes.clear()
    mosquito_rects.clear()

    n = random.randint(1, 5)

    for _ in range(n):
        rect = mosquito_img.get_rect()
        rect.x = random.randint(50, SCREEN_WIDTH - rect.width - 50)
        rect.y = random.randint(80, SCREEN_HEIGHT - rect.height - 50)

        mosquitoes.append(mosquito_img)
        mosquito_rects.append(rect)
    
    mosquito_active = True

# game loop
running = True
while running:
    # update clock 
    dt = clock.tick() / 1000

    # scale and set bg image
    scaled_bg = pygame.transform.scale(current_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_bg, (0, 0))

    # display close button
    screen.blit(close_icon, close_rect)

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # user clicked
        if event.type == pygame.MOUSEBUTTONDOWN:
            # user clicked on play button
            if (SCREEN_WIDTH / 2 + 200) <= mouse[0] <= (SCREEN_WIDTH / 2 + 200 + 140) and (SCREEN_HEIGHT/2 - 150) <= mouse[1] <= (SCREEN_HEIGHT / 2 - 150 + 60):
                current_bg = room
                show_button = False
                play = True
            
            # left click
            elif event.button == 1: 
                # user clicked on shop icon
                if shop_icon_rect.collidepoint(event.pos):
                    previous_bg = current_bg
                    current_bg = shop
                elif close_rect.collidepoint(event.pos):
                    running = False
                    pygame.quit()
                elif mosquito_active:
                    for rect in mosquito_rects[:]:
                        if rect.collidepoint(event.pos):
                            impact_channel.play(impact_sound)
                            mosquito_rects.remove(rect)
                            coins += MOSQUITO_COIN_REWARD
                            break
                    
                    if len(mosquito_rects) == 0:
                        mosquito_active = False
                        mosquito_sound.stop()
                        mosquito_sound_playing = False

        # user pressed the escape key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and current_bg == shop:
                current_bg = previous_bg
            
    if play:
        time_passed += dt

        # update in-game time every 15 mins
        if time_passed >= REAL_SECONDS_PER_TICK:
            game_minutes += GAME_MINUTES_PER_TICK
            time_passed = 0
        
        if show_day_text:
            day_text_timer += dt

        # display coin and time in light or dark mode
        if game_minutes < 23 * 60 and current_bg != shop:
            if (current_bg != agent and current_bg != agent2): 
                time_surface = font.render(time_text, True, (255, 255, 255))
                coin_text_surface = font.render(str(coins), True, (255, 255, 255))
                coin_text_rect = coin_text_surface.get_rect(
                    midleft=(coin_rect.right + 15, coin_rect.centery)
                )
            else:
                time_surface = font.render(time_text, True, (0, 0, 0))
                coin_text_surface = font.render(str(coins), True, (0, 0, 0))
                coin_text_rect = coin_text_surface.get_rect(
                    midleft=(coin_rect.right + 15, coin_rect.centery)
                )
        
            screen.blit(time_surface, (10, 10))

        # background logic
        if current_bg != shop and current_bg != day_bg:
            # draw icons on screen
            screen.blit(shop_icon, shop_icon_rect)
            screen.blit(coin_icon, coin_rect)
            screen.blit(coin_text_surface, coin_text_rect)

            if (game_minutes == (17 * 60 + 30) and game_minutes <= (17 * 60 + 45)):
                current_bg = room2
            elif (game_minutes > (17 * 60 + 45) and game_minutes < (18 * 60)):
                current_bg = room
            elif (game_minutes == (18 * 60)):
                if not knock_played:
                    # play knock sound
                    knock.play()
                    knock_played = True
                
                current_bg = agent
            elif (game_minutes >= (18 * 60 + 15) and game_minutes < (19 * 60)):
                knock_played = False
                current_bg = agent2
            elif (game_minutes == (19 * 60)):
                current_bg = dinner
            elif (((game_minutes >= (19 * 60 + 15)) and (game_minutes < (21 * 60))) and minigame_played == False):
                background = pygame.image.load("./assets/images/background_v6.jpg")
                background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

                class Player:
                    def __init__(self, img):
                        self.x = 110
                        self.y = 700
                        self.health = 100

                        self.img = pygame.image.load("./assets/images/Paper.jpeg").convert_alpha()
                        player_width = 64
                        player_height = 64
                        self.img = pygame.transform.scale(self.img, (player_width, player_height))
                        self.rect = pygame.Rect(self.x, self.y, player_width, player_height)

                    def draw(self, x, y):
                        screen.blit(self.img, (x, y))
                        self.rect.x = self.x
                        self.rect.y = self.y

                # Player
                paper = Player("Paper.jpeg")
                player_rect = paper.rect

                class RHand:
                    def __init__(self, img):
                        self.x = paper.x
                        self.y = paper.y
                        self.health = 10
                        self.img = pygame.image.load("./assets/images/hand.png").convert_alpha()
                        RHand_width = 128
                        RHand_height = 128
                        self.img = pygame.transform.scale(self.img, (RHand_width, RHand_height))
                        self.rect = pygame.Rect(self.x, self.y, RHand_width, RHand_height)

                    def draw(self, x, y):
                        screen.blit(self.img, (x, y))
                        self.rect.x = self.x
                        self.rect.y = self.y

                # Hand
                hand = RHand("hand.png")
                hand.x = paper.x
                hand.y = paper.y
                RHandX_change = 2.1
                RHandY_change = 0
                # Ready - you can't see the bullet on the screen
                RHand_state = "ready"

                # Fire - Bullet is currently moving
                def RHand(x, y):
                    global RHand_state
                    RHand_state = "fire"
                    hand.draw(hand.x + 64, hand.y)

                def isCollision():
                    if hand.rect.colliderect(ant.rect):
                        return True
                    else:
                        return False

                class Ant:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y
                        self.speed = 0.5
                        self.health = 10
                        self.width = 64
                        self.height = 64
                        self.img = pygame.image.load("./assets/images/beginner_ant.png").convert_alpha()
                        self.img = pygame.transform.scale(self.img, (self.width, self.height))
                        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

                    def draw(self):
                        screen.blit(self.img, (self.x, self.y))
                        self.rect.x = self.x
                        self.rect.y = self.y

                    def chase_player(self, player):
                        dx = player.x - self.x
                        dy = player.y - self.y

                        if dx > 0:
                            self.x += self.speed
                        if dx < 0:
                            self.x -= self.speed
                        if dy > 0:
                            self.y += self.speed
                        if dy < 0:
                            self.y -= self.speed

                # CREATE 10 ANTS
                ants = []

                for i in range(10):
                    x = random.randint(350, 1450)
                    y = random.randint(0, 400)
                    ants.append(Ant(x, y))

                class Rice:
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y
                        self.speed = 1
                        self.health = 10
                        self.width = 64
                        self.height = 64
                        self.img = pygame.image.load("./assets/images/Rice.png").convert_alpha()
                        self.img = pygame.transform.scale(self.img, (self.width, self.height))
                        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

                    def draw(self):
                        screen.blit(self.img, (self.x, self.y))
                        self.rect.x = self.x
                        self.rect.y = self.y

                    def run_away(self, player):
                        dx = player.x - self.x
                        dy = player.y - self.y

                        if dx > 0:
                            self.x -= self.speed
                        if dx < 0:
                            self.x += self.speed
                        if dy > 0:
                            self.y -= self.speed
                        if dy < 0:
                            self.y += self.speed

                # CREATE 10 RICE
                rices = []

                for i in range(10):
                    x = random.randint(0, 1450)
                    y = random.randint(0, 700)
                    rices.append(Rice(x, y))

                # Score
                score_value = 0
                minigame_font = pygame.font.Font("freesansbold.ttf", 32)
                textX = 10
                textY = 10

                def show_score(x, y):
                    score = minigame_font.render("Score: " + str(score_value), True, (255, 255, 255))
                    screen.blit(score, (x, y))

                def draw_RHand_button():
                    RHand_Button = pygame.image.load("./assets/images/RHand Button.png")
                    RHand_Button_img = pygame.transform.scale(RHand_Button, (200, 200))
                    screen.blit(RHand_Button_img, (1200, 570))

                def draw_RHand_button_Grey():
                    RHand_Button = pygame.image.load("./assets/images/RHand Button Grey.png")
                    RHand_Button_img = pygame.transform.scale(RHand_Button, (200, 200))
                    screen.blit(RHand_Button_img, (1200, 570))

                # GAME LOOP
                game_result = None
                minigame_running = True
                while minigame_running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            minigame_running = False

                    # Player boundaries
                    if paper.x <= 0:
                        paper.x = 0
                    elif paper.x >= 1500:
                        paper.x = 1500

                    if paper.y <= 0:
                        paper.y = 0
                    elif paper.y >= 750:
                        paper.y = 750

                    # Rice boundaries
                    for rice in rices:
                        if rice.x <= 0:
                            rice.x = 0
                        elif rice.x >= 1500:
                            rice.x = 1500
                        if rice.y <= 0:
                            rice.y = 0
                        elif rice.y >= 750:
                            rice.y = 750

                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        paper.x -= 2

                    if keys[pygame.K_c]:
                        if RHand_state == "ready":
                            Hand_sound = mixer.Sound('./assets/audio/laser.wav')
                            Hand_sound.play()
                            hand.x = paper.x
                            hand.y = paper.y
                            RHand(hand.x, hand.y)

                    if keys[pygame.K_RIGHT]:
                        paper.x += 2

                    if keys[pygame.K_UP]:
                        paper.y -= 2

                    if keys[pygame.K_DOWN]:
                        paper.y += 2

                    screen.blit(background, (0, 0))
                    draw_RHand_button()
                    paper.draw(paper.x, paper.y)

                    for ant in ants:
                        ant.chase_player(paper)
                        ant.draw()
                        if paper.rect.colliderect(ant.rect):
                            paper.health -= 10
                            ant.health -= 10
                            for i in range(1):
                                x = random.randint(0, 1450)
                                y = random.randint(0, 700)
                                ants.append(Ant(x, y))
                        # Collision (RHand with ant)
                        collision = isCollision()
                        if collision:
                            explosion_sound = mixer.Sound('./assets/audio/explosion.wav')
                            explosion_sound.play()
                            hand.x = paper.x
                            hand.y = paper.y
                            hand.health -= 10
                            RHand_state = "ready"
                            ant.health -= 10
                            score_value += 10
                            for i in range(1):
                                x = random.randint(1300, 1450)
                                y = random.randint(0, 100)
                                ants.append(Ant(x, y))

                        if ant.health <= 0:
                            ants.remove(ant)

                    for rice in rices:
                        rice.draw()
                        if paper.rect.colliderect(rice.rect):
                            rice.health -= 1

                        if rice.health <= 0:
                            score_value += 10
                            rices.remove(rice)

                    # Bullet movement
                    if hand.x >= 1450:
                        draw_RHand_button()
                        hand.x = paper.x
                        RHand_state = "ready"

                    if RHand_state == "fire":
                        RHand(hand.x, hand.y)
                        hand.x += RHandX_change
                        draw_RHand_button_Grey()

                    # Win and Lose Condition
                    if paper.health <= 0:
                        game_minutes = 20 * 60 + 45
                        minigame_played = True
                        break
                    
                    if score_value >= 100:
                        coins += 10
                        game_minutes = 20 * 60 + 45
                        minigame_played = True
                        break

                    show_score(textX, textY)
                    pygame.display.update()
            elif game_minutes == (21 * 60):
                current_bg = bedroom
                if not mosquito_active:
                    spawn_mosquitoes()
            elif ((game_minutes >= (21 * 60)) and (game_minutes < (23 * 60))):
                current_bg = bedroom 

                if mosquito_sound_playing:
                    mosquito_sound.play()

        if mosquito_active:
            for rect in mosquito_rects:
                screen.blit(mosquito_img, rect)
        
        # handle new day
        if game_minutes >= 23*60 and not show_day_text:
            day += 1
            show_day_text = True
            day_text_timer = 0
            current_bg = day_bg
            mosquito_sound.stop()
            mosquito_sound_playing = False
        
        # reset variables for the new day
        if show_day_text and day_text_timer >= DAY_TEXT_DURATION:
            show_day_text = False
            day_text_timer = 0

            game_minutes = 17 * 60
            time_passed = 0
            current_bg = room

            mosquito_active = False
            mosquitoes.clear()
            mosquito_rects.clear()

            minigame_played = False

        # text on day_bg
        day_surface = font.render(f"Day {day}", True, (0, 0, 0))
        day_rect = day_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # display day text on day_bg
        if current_bg == day_bg and show_day_text:
            screen.blit(day_surface, day_rect)

    # calculate in-game hours and mins
    hours = int(game_minutes // 60) % 24
    minutes = int(game_minutes % 60)

    # format in-game time
    display_hour = hours % 12 or 12
    ampm = "PM" if hours >= 12 else "AM"
    time_text = f"{display_hour}:{minutes:02d} {ampm}"
    
    # get mouse position
    mouse = pygame.mouse.get_pos()

    # show play button
    if (show_button == True):
        pygame.draw.rect(screen, (255, 255, 255), [SCREEN_WIDTH/2 + 200, SCREEN_HEIGHT/2 - 150, 140, 60])
        screen.blit(text, (SCREEN_WIDTH/2 + 230, SCREEN_HEIGHT/2 - 150))

    # update screen
    pygame.display.update()

pygame.quit()