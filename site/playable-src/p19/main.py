import asyncio
import pygame
import random

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 800, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stationery Monster Hunt")

clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 35)

# ---------------- MUSIC ----------------
pygame.mixer.music.load("assets/music/gamemusic.ogg")
pygame.mixer.music.play(-1)

# ---------------- BACKGROUND ----------------
background = pygame.Surface((WIDTH, HEIGHT))
background.fill((210, 230, 255))

# ---------------- PLAYER ----------------
class Player:
    def __init__(self, img):
        self.x = 100
        self.y = 100 #this is top left coordinates instead of centre for some reason
        self.speed = 4
        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (80, 80)) # when you change this both values should be same for uniform scaling prolly
        self.rect = pygame.Rect(100, 100, 80, 80)

    def update_rect(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

pc = Player("assets/sprites/down.gif")
# ---------------- MONSTERS ----------------
monster_names = [
    "Pencil",
    "Ruler",
    "Eraser",
    "Notebook",
    "Stapler"
]

# ---------------- BOXES ----------------
boxes = []

for i in range(10):

    x = random.randint(80, WIDTH - 100)
    y = random.randint(80, HEIGHT - 100)

    boxes.append({
        "rect": pygame.Rect(x, y, 60, 60),
        "active": True,
        "monster": False,
        "name": ""
    })

monster_indices = random.sample(range(10), 5)

for i, idx in enumerate(monster_indices):

    boxes[idx]["monster"] = True
    boxes[idx]["name"] = monster_names[i]

# ---------------- GAME STATE ----------------
found = 0
message = ""

in_battle = False
battle_box = None
battle_name = ""
hp = 3

# ---------------- GAME STATE (loop vars) ----------------
running = True


# ---------------- LOOP ----------------
async def main():

    global running, found, message
    global in_battle, battle_box, battle_name, hp

    while running:

        clock.tick(60)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # TRIPLE CLICK SYSTEM
            if event.type == pygame.KEYDOWN:

                if in_battle and event.key == pygame.K_SPACE:
                    hp -= 1

        keys = pygame.key.get_pressed()

        # ---------------- BATTLE ----------------
        if in_battle:

            screen.fill((200, 200, 200))

            title = font.render(battle_name, True, (0, 0, 0))
            screen.blit(title, (250, 150))

            hp_text = small_font.render(f"HP: {hp}", True, (0, 0, 0))
            screen.blit(hp_text, (370, 300))

            info = small_font.render("Press SPACE 3 times!", True, (0, 0, 0))
            screen.blit(info, (240, 380))

            if hp <= 0:

                if battle_box["monster"]:
                    message = f"Defeated {battle_name} Monster!"
                    found += 1
                else:
                    message = "It was just a normal object!"

                battle_box["active"] = False
                in_battle = False
                hp = 3

            pygame.display.update()
            await asyncio.sleep(0)
            continue

        # ---------------- MOVEMENT ----------------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pc.x -= pc.speed
            pc.img = pygame.image.load("assets/sprites/left.gif").convert_alpha()
        if keys[pygame.K_RIGHT]:
            pc.x += pc.speed
            pc.img = pygame.image.load("assets/sprites/right.gif").convert_alpha()
        if keys[pygame.K_UP]:
            pc.y -= pc.speed
            pc.img = pygame.image.load("assets/sprites/up.gif").convert_alpha()
        if keys[pygame.K_DOWN]:
            pc.y += pc.speed
            pc.img = pygame.image.load("assets/sprites/down.gif").convert_alpha()

        pc.img = pygame.transform.scale(pc.img, (80, 80))
        pc.update_rect()

        if pc.x < 0:
            pc.x = 0
        if pc.x > 720:
            pc.x = 720
        if pc.y < 0:
            pc.y = 0
        if pc.y > 620:
            pc.y = 620

        # ---------------- INTERACTION ----------------
        if keys[pygame.K_RETURN]:

            for b in boxes:

                if b["active"] and pc.rect.colliderect(b["rect"]):

                    in_battle = True
                    battle_box = b
                    battle_name = b["name"] if b["monster"] else "Unknown Object"
                    hp = 3

        # ---------------- DRAW ----------------
        screen.blit(background, (0, 0))

        # boxes
        for b in boxes:

            if b["active"]:

                pygame.draw.rect(screen, (170, 170, 170), b["rect"])

                label = small_font.render("?", True, (0, 0, 0))
                screen.blit(label, (b["rect"].x + 20, b["rect"].y + 10))

        # pc
        #pygame.draw.rect(screen, (0, 0, 255), pc)
        pc.draw(screen)

        # UI
        counter = small_font.render(f"Found: {found}/5", True, (0, 0, 0))
        screen.blit(counter, (10, 10))

        msg = small_font.render(message, True, (0, 0, 0))
        screen.blit(msg, (10, 50))

        # WIN
        if found == 5:

            win = font.render("YOU WIN!", True, (0, 180, 0))
            screen.blit(win, (250, 300))

        pygame.display.update()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())