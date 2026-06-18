import asyncio
import pygame
import sys
import time
import random
import math

# Initialize pygame
pygame.init()

# ── Global Setup & Framework Configurations ───────────────────────────────────
# Base game dimensions
BASE_SW, BASE_SH = 600, 400
# Grid Wars dimensions
GW_SW, GW_SH = 1160, 700

screen = pygame.display.set_mode((BASE_SW, BASE_SH))
pygame.display.set_caption("School Day Adventure - Featuring Grid Wars")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 28)
F_BIG  = pygame.font.SysFont("consolas", 32, bold=True)
F_MED  = pygame.font.SysFont("consolas", 18, bold=True)
F_SM   = pygame.font.SysFont("consolas", 13)
F_TINY = pygame.font.SysFont("consolas", 11)

# Grid Wars Layout Definitions
COLS, ROWS = 13, 10
CELL = 58
GX, GY = 10, 10
PNL  = GX + COLS * CELL + 12
PNW  = GW_SW - PNL - 10

# Color Palettes
BG        = (10,  10,  18)
C_DARK    = (14,  14,  24)
C_LIGHT   = (18,  18,  30)
C_LINE    = (26,  26,  42)
C_PLAYER  = (55,  200, 135)
C_ENEMY   = (210, 60,  60)
C_MOVE    = (50,  130, 215)
C_SHOOT   = (210, 185, 35)
C_SEL     = (255, 235, 70)
C_HIT     = (255, 65,  25)
C_DODGE   = (35,  215, 255)
C_HEAL    = (80,  230, 130)
C_AOE     = (230, 130, 30)
C_SMOKE   = (160, 160, 190)
C_ABILITY = (180, 100, 230)
C_WHITE   = (225, 225, 240)
C_DIM     = (75,  75,  100)
C_PANEL   = (12,  12,  20)

DEFS = {
    "SCOUT":     (3,  3, 3, 1, 1.20, None,       (55,  200, 135)),
    "SOLDIER":   (5,  2, 4, 2, 0.90, None,       (100, 180, 230)),
    "TANK":      (9,  1, 5, 3, 0.65, None,       (200, 150, 60)),
    "MEDIC":     (4,  2, 3, 1, 1.00, "HEAL",     (80,  230, 130)),
    "SNIPER":    (3,  1, 7, 3, 0.80, "OVERWATCH",(220, 200, 80)),
    "GRENADIER": (5,  2, 3, 2, 0.75, "GRENADE",  (230, 110, 40)),
    "RECON":     (3,  4, 3, 1, 1.30, "SMOKE",    (160, 140, 220)),
}
GLYPHS = {"SCOUT":"S","SOLDIER":"O","TANK":"T","MEDIC":"M","SNIPER":"N","GRENADIER":"G","RECON":"R"}

DIFFICULTY = {
    "EASY":  {"enemy_count":3,"dodge_mult":1.40,"ai_smart":False,"ai_ability":False,"ai_dodge_chance":0.00,"label":"EASY",  "col":(70,200,100)},
    "NORMAL":{"enemy_count":5,"dodge_mult":1.00,"ai_smart":True, "ai_ability":False,"ai_dodge_chance":0.20,"label":"NORMAL","col":(200,190,60)},
    "HARD":  {"enemy_count":6,"dodge_mult":0.70,"ai_smart":True, "ai_ability":True, "ai_dodge_chance":0.50,"label":"HARD",  "col":(220,120,40)},
}

def cell_rect(c,r): return pygame.Rect(GX+c*CELL, GY+r*CELL, CELL, CELL)
def cell_center(c,r): rc=cell_rect(c,r); return rc.centerx, rc.centery
def mdist(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

# Helper utility to wrap text cleanly within a pixel width boundary limit
def wrap_text(text, font_obj, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font_obj.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# ── Grid Wars VFX Infrastructure ──────────────────────────────────────────────
class Bullet:
    def __init__(self,sx,sy,tx,ty,col,on_arrive,size=5):
        self.x,self.y=float(sx),float(sy)
        self.tx,self.ty=float(tx),float(ty)
        d=math.hypot(tx-sx,ty-sy) or 1
        self.vx=(tx-sx)/d*10; self.vy=(ty-sy)/d*10
        self.col=col; self.on_arrive=on_arrive
        self.done=False; self.trail=[]; self.size=size
    def update(self):
        self.trail.append((self.x,self.y))
        if len(self.trail)>8: self.trail.pop(0)
        self.x+=self.vx; self.y+=self.vy
        if math.hypot(self.x-self.tx,self.y-self.ty)<10: self.done=True
    def draw(self,surf):
        for i,(tx,ty) in enumerate(self.trail):
            a=int(i/len(self.trail)*150)
            s=pygame.Surface((8,8),pygame.SRCALPHA)
            pygame.draw.circle(s,(*self.col,a),(4,4),self.size-2)
            surf.blit(s,(int(tx)-4,int(ty)-4))
        pygame.draw.circle(surf,self.col,(int(self.x),int(self.y)),self.size)

class Burst:
    def __init__(self,x,y,col,n=14):
        self.ps=[]
        for _ in range(n):
            a=random.uniform(0,math.tau); sp=random.uniform(1,4.5)
            self.ps.append([float(x),float(y),math.cos(a)*sp,math.sin(a)*sp,col,random.uniform(0.7,1.0)])
    def update(self):
        for p in self.ps: p[0]+=p[2];p[1]+=p[3];p[3]+=0.12;p[5]-=0.025
        self.ps=[p for p in self.ps if p[5]>0]
    def draw(self,surf):
        for p in self.ps:
            a=int(p[5]*255); r=max(1,int(p[5]*4))
            s=pygame.Surface((r*2+2,r*2+2),pygame.SRCALPHA)
            pygame.draw.circle(s,(*p[4],a),(r+1,r+1),r)
            surf.blit(s,(int(p[0])-r-1,int(p[1])-r-1))
    @property
    def alive(self): return bool(self.ps)

class FloatText:
    def __init__(self,x,y,txt,col):
        self.x,self.y=float(x),float(y); self.txt=txt; self.col=col; self.life=1.0
    def update(self): self.y-=1.1; self.life-=0.022
    def draw(self,surf):
        lbl=F_MED.render(self.txt,True,self.col)
        s=pygame.Surface(lbl.get_size(),pygame.SRCALPHA)
        s.set_alpha(int(self.life*255)); s.blit(lbl,(0,0))
        surf.blit(s,(int(self.x)-lbl.get_width()//2,int(self.y)))
    @property
    def alive(self): return self.life>0

# ── Grid Wars Unit Engine ─────────────────────────────────────────────────────
class Unit:
    def __init__(self,kind,col,row,team):
        hp,mov,rng,dmg,dw,ability,tint=DEFS[kind]
        self.kind=kind; self.col=col; self.row=row; self.team=team
        self.hp=hp; self.mhp=hp; self.mov=mov; self.rng=rng
        self.dmg=dmg; self.dw=dw; self.ability=ability; self.tint=tint
        self.moved=False; self.shot=False; self.ability_used=False
        self.flash=0; self.shake=0; self.smoke=0; self.overwatch=False
        self.glyph=GLYPHS[kind]

    def alive(self): return self.hp>0
    def pos(self): return (self.col,self.row)
    def done(self): return self.moved and self.shot
    def reset(self):
        self.moved=False; self.shot=False; self.ability_used=False
        self.overwatch=False
        if self.smoke>0: self.smoke-=1
    def effective_range(self): return self.rng+(3 if self.overwatch else 0)

    def draw(self,surf,selected=False,ability_mode=False):
        rc=cell_rect(self.col,self.row)
        sy_off=random.randint(-3,3) if self.shake>0 else 0
        if self.shake>0: self.shake-=1
        ry=rc.y+sy_off
        dim=(self.moved and self.shot)
        is_player = (self.team == "player")
        team_bg   = (20, 60, 80)   if is_player else (80, 18, 18)
        team_rim  = (50, 190, 230) if is_player else (230, 55, 55)
        team_dim_rim=(25,90,110)   if is_player else (110,30,30)

        if self.smoke>0:
            ss=pygame.Surface((CELL+12,CELL+12),pygame.SRCALPHA)
            pygame.draw.rect(ss,(*C_SMOKE,50),(0,0,CELL+12,CELL+12),border_radius=9)
            surf.blit(ss,(rc.x-6,ry-6))

        s=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
        br = 10 if is_player else 3
        bg_alpha = 110 if not dim else 55
        pygame.draw.rect(s,(*team_bg, bg_alpha),(0,0,CELL,CELL),border_radius=br)

        if ability_mode:
            pygame.draw.rect(s,(*C_ABILITY,220),(0,0,CELL,CELL),3,border_radius=br)
        elif selected:
            pygame.draw.rect(s,(*C_SEL,255),(0,0,CELL,CELL),4,border_radius=br)
        else:
            rim = team_dim_rim if dim else team_rim
            pygame.draw.rect(s,(*rim,200 if not dim else 100),(0,0,CELL,CELL),3,border_radius=br)

        bar_col = team_rim if not dim else team_dim_rim
        pygame.draw.rect(s,(*bar_col,160),(2,2,CELL-4,5),border_radius=2)
        surf.blit(s,(rc.x,ry))

        if self.flash>0:
            fs=pygame.Surface((CELL,CELL),pygame.SRCALPHA)
            pygame.draw.rect(fs,(*C_HIT,self.flash*18),(0,0,CELL,CELL),border_radius=br)
            surf.blit(fs,(rc.x,ry)); self.flash-=1

        gc  = (140,140,160) if dim else ((220,240,255) if is_player else (255,210,210))
        gl  = F_MED.render(self.glyph,True,gc)
        surf.blit(gl,(rc.x+CELL//2-gl.get_width()//2,ry+CELL//2-gl.get_height()//2-2))

        bx=rc.x+4; by=ry+CELL-10; bw=CELL-8
        pygame.draw.rect(surf,(20,20,35),(bx,by,bw,6),border_radius=2)
        ratio=self.hp/self.mhp
        hc=(50,210,160) if is_player else (210,80,50)
        pygame.draw.rect(surf,hc,(bx,by,int(bw*ratio),6),border_radius=2)

# ── Core Player Class ─────────────────────────────────────────────────────────
class Player:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.speed = 4
        self.points = 0
        self.inventory = []
        self.size = 40
        self.color = (0, 200, 255)

    def move(self, keys, screen_width, screen_height):
        if keys[pygame.K_UP]: self.y -= self.speed
        if keys[pygame.K_DOWN]: self.y += self.speed
        if keys[pygame.K_LEFT]: self.x -= self.speed
        if keys[pygame.K_RIGHT]: self.x += self.speed

        if self.x < 0: self.x = 0
        if self.y < 0: self.y = 0
        if self.x > screen_width - self.size: self.x = screen_width - self.size
        if self.y > screen_height - self.size: self.y = screen_height - self.size

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

# ── Integrated Task Homework List System ──────────────────────────────────────
class QuizManager:
    def __init__(self):
        self.subjects = {
            "Math": {
                "Easy": [
                    ("2 + 2 = ?", "4", "Think basic single-digit addition. Add 2 items to another group of 2."),
                    ("5 - 3 = ?", "2", "Subtract carefully. If you have 5 fingers and tuck 3 away, count what remains."),
                    ("10 + 5 = ?", "15", "Simple double-digit addition. Combine a full ten stack with five units."),
                    ("4 * 2 = ?", "8", "Think about adding 4 twice. It is double the amount of 4."),
                    ("9 - 4 = ?", "5", "Count down from 9 by taking away 4 units completely."),
                    ("3 + 7 = ?", "10", "Forms a perfect ten. What number completes 3 to make a full decade?")
                ],
                "Medium": [
                    ("12 / 3 = ?", "4", "What multiplied by 3 gives 12? Think of splitting 12 into three equal parts."),
                    ("sqrt(16) = ?", "4", "What square number gives 16? Find a value that equals 16 when multiplied by itself."),
                    ("15 * 4 = ?", "60", "Double 15 twice. First doubling gives 30, now double that final result."),
                    ("7 * 8 = ?", "56", "Classic multiplication table check. It is just one step below 7 * 9 (63)."),
                    ("5^2 = ?", "25", "Multiply 5 by itself. Think of a common quarter value out of 100."),
                    ("100 - 37 = ?", "63", "Careful with borrowing values. 100 minus 30 is 70, then count back 7 more.")
                ],
                "Hard": [
                    ("Integral of x dx? (Express like 0.5x^2)", "0.5x^2", "Use calculus power rule inversion. Raise power to 2 and divide by that new exponent."),
                    ("Derivative of sin(x)?", "cos(x)", "Trigonometric rates of change. The derivative of sine is positive cosine, not negative."),
                    ("Derivative of x^2? (w.r.t x)", "2x", "Standard power rule application. Bring the exponent to the front and reduce the power by 1."),
                    ("Solve for x: 2x + 5 = 15", "5", "Isolate the variable by subtracting 5 first to get 2x = 10, then divide by 2."),
                    ("Log10(100) = ?", "2", "10 raised to what power is 100? Count how many zeros follow the 1."),
                    ("Derivative of e^x?", "e^x", "The function remains completely unique and unchanged through differentiation.")
                ]
            },
            "Science": {
                "Easy": [
                    ("Water formula?", "H2O", "Two hydrogen atoms paired up with exactly one oxygen atom."),
                    ("Planet closest to the Sun?", "Mercury", "The smallest rocky planet in our system, named after the Roman messenger god."),
                    ("What gas do humans breathe in?", "Oxygen", "O2 chemical representation. The essential gas that binds with our blood cells."),
                    ("Color of leaves due to chlorophyll?", "Green", "Reflected light frequency. It is the primary color of nature and forests."),
                    ("How many legs does a spider have?", "8", "Classic arachnid characteristic. Twice the amount of an ordinary quadruped mammal.")
                ],
                "Medium": [
                    ("Speed of light exponent: 3*10^? m/s", "8", "Approximately 300,000,000 meters per second. The exponent is the number of zeros."),
                    ("Human DNA shape?", "Double helix", "Looks like a twisted ladder layout or an intertwined spiral structure."),
                    ("Main gas in Earth's atmosphere?", "Nitrogen", "Accounts for roughly 78% of ambient air, outnumbering oxygen significantly."),
                    ("What planet is known as the Red Planet?", "Mars", "Rich in iron-oxide surfaces. Named after the Roman god of war."),
                    ("Boiling point of water in Celsius?", "100", "Standard atmospheric pressure liquid state. The exact base cap of the Celsius system.")
                ],
                "Hard": [
                    ("Einstein's equation? (E=...)", "E=mc^2", "Mass-energy equivalence law. Energy equals mass multiplied by the speed of light squared."),
                    ("Atomic number of Carbon?", "6", "Basis of organic molecules. Sits between Boron (5) and Nitrogen (7) on the periodic table."),
                    ("Chemical symbol for Gold?", "Au", "Derived from the Latin word 'Aurum', meaning shining dawn."),
                    ("Uncharged particle in an atom?", "Neutron", "Found directly inside the core nucleus alongside positive protons."),
                    ("Most abundant element in the universe?", "Hydrogen", "Element number one on the periodic table. It forms the core fueling process of stars.")
                ]
            },
            "Grid Wars Tasks": { "Easy": [], "Medium": [], "Hard": [] }
        }
        self.active = False
        self.menu_open = False
        self.energy_prompt = False
        self.snack_prompt = False
        
        self.subject = None
        self.difficulty = None
        self.questions = []
        self.current_index = 0
        self.user_answer = ""
        self.correct_count = 0
        self.start_time = None
        self.time_limit = 30
        self.selected_subject = 0
        self.selected_difficulty = 0
        
        self.hint_revealed = False  # Track if a hint scroll is active for the current question

    def open_menu(self):
        self.menu_open = True
        self.selected_subject = 0
        self.selected_difficulty = 0

    def navigate_menu(self, event):
        if self.menu_open and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_subject = (self.selected_subject - 1) % len(self.subjects)
            elif event.key == pygame.K_DOWN:
                self.selected_subject = (self.selected_subject + 1) % len(self.subjects)
            elif event.key == pygame.K_LEFT:
                self.selected_difficulty = (self.selected_difficulty - 1) % 3
            elif event.key == pygame.K_RIGHT:
                self.selected_difficulty = (self.selected_difficulty + 1) % 3
            elif event.key == pygame.K_RETURN:
                subject = list(self.subjects.keys())[self.selected_subject]
                difficulty = ["Easy","Medium","Hard"][self.selected_difficulty]
                return subject, difficulty
            elif event.key == pygame.K_ESCAPE:
                self.menu_open = False
                return "Closed homework menu"
        return None

    def start_quiz(self, subject, difficulty, player):
        self.subject = subject
        self.difficulty = difficulty
        self.current_index = 0
        self.user_answer = ""
        self.correct_count = 0
        self.time_limit = 30
        self.menu_open = False
        self.hint_revealed = False
        
        pool_questions = self.subjects[subject][difficulty]
        self.questions = random.sample(pool_questions, min(3, len(pool_questions)))
        
        if "Energy Drink" in player.inventory:
            self.energy_prompt = True
        else:
            self.start_actual_quiz()

    def start_actual_quiz(self):
        self.active = True
        self.start_time = time.time()

    def update_timer(self, player):
        if self.active and self.subject != "Grid Wars Tasks":
            elapsed = time.time() - self.start_time
            if elapsed >= self.time_limit:
                self.active = False
                if self.correct_count < len(self.questions) and "Snack" in player.inventory:
                    self.snack_prompt = True
                    return "Time's up! Use your Snacks to restore missed answers or press 'F' to finish."
                else:
                    return self.finish_quiz(player)
        return None

    def type_answer(self, event, player):
        if event.type != pygame.KEYDOWN:
            return None

        # State 1: Energy Drink pre-game buff prompt
        if self.energy_prompt:
            if event.key == pygame.K_d:
                if "Energy Drink" in player.inventory:
                    player.inventory.remove("Energy Drink")
                    self.time_limit += 5
                    return f"Drank an Energy Drink! +5s added. Total: {self.time_limit}s"
            elif event.key == pygame.K_s:
                self.energy_prompt = False
                self.start_actual_quiz()
                return f"Started {self.subject} assignment ({self.difficulty})!"
            return None

        # State 2: Snack item backup recovery prompt
        if self.snack_prompt:
            if event.key == pygame.K_e:
                missed = len(self.questions) - self.correct_count
                snack_cost = {"Easy": 1, "Medium": 2, "Hard": 3}[self.difficulty]
                
                if missed > 0 and player.inventory.count("Snack") >= snack_cost:
                    for _ in range(snack_cost):
                        player.inventory.remove("Snack")
                    self.correct_count += 1
                    return f"Ate {snack_cost} Snacks! Question restored ({self.correct_count}/{len(self.questions)} correct)"
                elif missed > 0:
                    return f"Not enough Snacks! Requires {snack_cost} for {self.difficulty} difficulty."
            elif event.key == pygame.K_f:
                return self.finish_quiz(player)
            return None

        # State 3: Base Active Playing Screen
        if self.active:
            # Check for hint scroll activation first using LEFT SHIFT (Leaves 'H' open for regular typing)
            if event.key == pygame.K_LSHIFT and not self.hint_revealed:
                if "Hint Scroll" in player.inventory:
                    player.inventory.remove("Hint Scroll")
                    self.hint_revealed = True
                    return "Used Hint Scroll! A helpful clue has been unrolled below."
                else:
                    return "No Hint Scrolls left in your inventory!"

            if event.key == pygame.K_RETURN:
                if self.current_index < len(self.questions):
                    q, ans, hint = self.questions[self.current_index]
                    if self.user_answer.strip().lower() == ans.lower():
                        self.correct_count += 1
                    self.current_index += 1
                    self.user_answer = ""
                    self.hint_revealed = False
                    
                    if self.current_index >= len(self.questions):
                        self.active = False
                        if self.correct_count < len(self.questions) and "Snack" in player.inventory:
                            self.snack_prompt = True
                            return "Assignment completed! Press 'E' to use Snacks on missed options, or 'F' to claim score."
                        else:
                            return self.finish_quiz(player)
            elif event.key == pygame.K_BACKSPACE:
                self.user_answer = self.user_answer[:-1]
            else:
                if event.unicode.isprintable():
                    self.user_answer += event.unicode
        return None

    def finish_quiz(self, player):
        points_per_correct = {"Easy": 4, "Medium": 7, "Hard": 12}[self.difficulty]
        earned_points = self.correct_count * points_per_correct
        
        player.points += earned_points
        self.active = False
        self.snack_prompt = False
        return f"Task complete! Correct: {self.correct_count}/{len(self.questions)} → +{earned_points} points!"

    def draw(self, screen, player):
        if self.menu_open:
            pygame.draw.rect(screen, (50,50,50), (100,80,400,240))
            pygame.draw.rect(screen, (255,255,255), (100,80,400,240), 2)
            title = font.render("Choose Subject & Difficulty", True, (255,255,255))
            screen.blit(title, (140,90))
            for i, subject in enumerate(self.subjects.keys()):
                color = (255,255,0) if i == self.selected_subject else (255,255,255)
                text = font.render(subject, True, color)
                screen.blit(text, (130,130+i*35))
            diff_text = font.render("Difficulty (< >): " + ["Easy","Medium","Hard"][self.selected_difficulty], True, (255,255,0))
            screen.blit(diff_text, (130,270))
            
        elif self.energy_prompt:
            pygame.draw.rect(screen, (30,45,65), (80,90,440,220))
            pygame.draw.rect(screen, (0,220,255), (80,90,440,220), 2)
            drink_count = player.inventory.count("Energy Drink")
            t1 = font.render("=== ENERGY DRINK INJECTOR ===", True, (0,255,255))
            t2 = font.render(f"Inventory: {drink_count} Energy Drink(s)", True, (255,255,255))
            t3 = font.render(f"Allocated Timer: {self.time_limit} seconds", True, (255,255,100))
            t4 = font.render("Press 'D' to Drink (+5 seconds / stackable)", True, (100,255,120))
            t5 = font.render("Press 'S' to Start Assignment", True, (255,160,60))
            screen.blit(t1, (100, 110))
            screen.blit(t2, (100, 145))
            screen.blit(t3, (100, 175))
            screen.blit(t4, (100, 215))
            screen.blit(t5, (100, 255))

        elif self.snack_prompt:
            pygame.draw.rect(screen, (60,40,40), (80,90,440,220))
            pygame.draw.rect(screen, (255,110,110), (80,90,440,220), 2)
            snack_count = player.inventory.count("Snack")
            missed = len(self.questions) - self.correct_count
            snack_cost = {"Easy": 1, "Medium": 2, "Hard": 3}[self.difficulty]
            
            t1 = font.render("=== SNACK RECOVERY MENU ===", True, (255,160,0))
            t2 = font.render(f"Inventory: {snack_count} Snack(s) | Missed: {missed}", True, (255,255,255))
            t3 = font.render(f"Current Base Score: {self.correct_count} / {len(self.questions)}", True, (255,255,100))
            t4 = font.render(f"Press 'E' to eat {snack_cost} snacks (Restores 1 missed Q)", True, (120,255,120))
            t5 = font.render("Press 'F' to Finish and calculate final rewards", True, (255,140,80))
            screen.blit(t1, (100, 110))
            screen.blit(t2, (100, 145))
            screen.blit(t3, (100, 175))
            screen.blit(t4, (100, 215))
            screen.blit(t5, (100, 255))
            
        elif self.active and self.subject != "Grid Wars Tasks" and self.current_index < len(self.questions):
            elapsed = time.time() - self.start_time
            remaining = max(0, int(self.time_limit - elapsed))
            q, ans, hint = self.questions[self.current_index]
            
            q_text = font.render(f"Q: {q}", True, (255,255,255))
            ans_text = font.render(f"Your Answer: {self.user_answer}", True, (0,255,0))
            timer_text = font.render(f"Time left: {remaining}s", True, (255,50,50))
            
            screen.blit(q_text, (15,110))
            screen.blit(ans_text, (15,240))
            screen.blit(timer_text, (15,270))

            # --- Upgraded Dynamic Wrapping Hint Section ---
            max_text_width = BASE_SW - 30 
            current_y = 140
            
            if self.hint_revealed:
                # Wrap long scrolls into multiple lines to fit on screen
                wrapped_lines = wrap_text(f"Scroll Hint: {hint}", font, max_text_width)
                for line in wrapped_lines:
                    hint_surface = font.render(line, True, (100, 255, 150))
                    screen.blit(hint_surface, (15, current_y))
                    current_y += 24
            else:
                hint_surface = font.render("Press 'Left Shift' to use a Hint Scroll!", True, (160,160,160))
                screen.blit(hint_surface, (15, current_y))

# ── Vending Machine ───────────────────────────────────────────────────────────
class VendingMachine:
    def __init__(self):
        self.items = [("Energy Drink", 10), ("Snack", 5), ("Hint Scroll", 15)]
        self.x, self.y, self.w, self.h = 450, 120, 80, 120
        self.color = (255,200,0)
        self.shop_open = False
        self.selected_index = 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.w,self.h))
        label = font.render("SHOP (E)", True, (0,0,0))
        screen.blit(label, (self.x, self.y - 20))

    def player_nearby(self, player):
        return (player.x < self.x+self.w and player.x+player.size > self.x and
                player.y < self.y+self.h and player.y+player.size > self.y)

    def navigate(self, event, player):
        if self.shop_open and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index-1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index+1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                item,cost = self.items[self.selected_index]
                if player.points >= cost:
                    player.points -= cost
                    player.inventory.append(item)
                    return f"Bought {item}! Remaining points: {player.points}"
                else:
                    return "Not enough points!"
            elif event.key == pygame.K_ESCAPE:
                self.shop_open = False
                return "Closed vending machine"
        return None

    def draw_shop(self, screen):
        if self.shop_open:
            pygame.draw.rect(screen,(50,50,50),(100,80,400,240))
            pygame.draw.rect(screen,(255,255,255),(100,80,400,240), 2)
            title = font.render("Vending Machine (Press Enter to Buy)",True,(255,255,255))
            screen.blit(title,(120,90))
            for i,(item,cost) in enumerate(self.items):
                color = (255,255,0) if i==self.selected_index else (255,255,255)
                text = font.render(f"{item} - {cost} pts",True,color)
                screen.blit(text,(150,130+i*40))

# ── Integrated Grid Wars Gameplay Context Wrapper ─────────────────────────────
class IntegratedGridWars:
    def __init__(self, difficulty_setting):
        setting_map = {"Easy": "EASY", "Medium": "NORMAL", "Hard": "HARD"}
        self.diff_key = setting_map.get(difficulty_setting, "NORMAL")
        self.diff = DIFFICULTY[self.diff_key]
        self.total_enemies_spawned = self.diff["enemy_count"]
        self.units = []
        self._setup()
        self.state = "PLAYER_SELECT"
        self.selected = None
        self.ability_mode = False
        self.move_tiles, self.shoot_tiles, self.ability_tiles = [], [], []
        self.bullets, self.bursts, self.floats = [], [], []
        self.winner = None
        self.dodge_target = None
        self.dodge_timer, self.dodge_window = 0.0, 0.0
        self.dodged = False
        self.enemy_q = []
        self.enemy_delay = 0.0
        self.screen_shake = 0

    def _setup(self):
        for kind,c,r in [("TANK",1,4),("SOLDIER",1,2),("MEDIC",1,7),("SNIPER",2,0),("GRENADIER",2,9)]:
            self.units.append(Unit(kind,c,r,"player"))
        all_e = [("TANK",11,5),("SOLDIER",11,2),("SOLDIER",11,7),("SCOUT",10,0),("SCOUT",10,9),("RECON",10,3)]
        for kind,c,r in all_e[:self.total_enemies_spawned]:
            self.units.append(Unit(kind,c,r,"enemy"))

    def alive(self, team=None): return [u for u in self.units if u.alive() and (team is None or u.team==team)]
    def unit_at(self, c, r):
        for u in self.units:
            if u.alive() and u.col==c and u.row==r: return u
        return None

    def reachable(self, unit):
        tiles, visited, q = [], {unit.pos()}, [(unit.col,unit.row,0)]
        while q:
            c,r,d = q.pop(0)
            for dc,dr in [(-1,0),(1,0),(0,-1),(0,1)]:
                nc,nr = c+dc,r+dr
                if (nc,nr) in visited or not(0<=nc<COLS and 0<=nr<ROWS): continue
                visited.add((nc,nr))
                if not self.unit_at(nc,nr):
                    tiles.append((nc,nr))
                    if d+1<unit.mov: q.append((nc,nr,d+1))
        return tiles

    def targets_in_range(self, unit):
        opp = "enemy" if unit.team=="player" else "player"
        return [e for e in self.alive(opp) if mdist(unit.pos(),e.pos())<=unit.effective_range() and e.smoke==0]

    def float_at(self, col, row, txt, c):
        cx,cy = cell_center(col,row)
        self.floats.append(FloatText(cx,cy-8,txt,c))

    def click(self, c, r, right=False):
        if self.state not in ("PLAYER_SELECT","PLAYER_MOVE","PLAYER_SHOOT"): return
        u = self.unit_at(c,r)

        if self.state=="PLAYER_SELECT":
            if u and u.team=="player" and not u.done():
                self.selected=u; self.move_tiles=self.reachable(u)
                self.state="PLAYER_MOVE"
        elif self.state=="PLAYER_MOVE":
            if (c,r) in self.move_tiles:
                self.selected.col, self.selected.row = c, r
                self.selected.moved=True; self.move_tiles=[]
                tgts = self.targets_in_range(self.selected)
                if tgts: self.shoot_tiles=[t.pos() for t in tgts]; self.state="PLAYER_SHOOT"
                else: self.selected.shot=True; self.after_unit_acts()
            elif u==self.selected:
                self.selected.moved=True; self.move_tiles=[]
                tgts = self.targets_in_range(self.selected)
                if tgts: self.shoot_tiles=[t.pos() for t in tgts]; self.state="PLAYER_SHOOT"
                else: self.selected.shot=True; self.after_unit_acts()
            else: self.selected=None; self.move_tiles=[]; self.state="PLAYER_SELECT"
        elif self.state=="PLAYER_SHOOT":
            if (c,r) in self.shoot_tiles:
                tgt = self.unit_at(c,r)
                if tgt: self.fire_player_bullet(self.selected,tgt)
            elif u==self.selected:
                self.selected.shot=True; self.shoot_tiles=[]; self.after_unit_acts()
            else: self.selected=None; self.shoot_tiles=[]; self.state="PLAYER_SELECT"

    def fire_player_bullet(self, shooter, target):
        sx,sy = cell_center(shooter.col,shooter.row)
        tx,ty = cell_center(target.col,target.row)
        dmg, ai_dodge_chance = shooter.dmg, self.diff["ai_dodge_chance"]
        will_dodge = random.random() < ai_dodge_chance

        self.shoot_tiles=[]; self.state="BULLET_PLAYER"

        def arrive():
            if will_dodge:
                self.float_at(target.col,target.row,"EVADED!",C_DODGE)
            else:
                target.hp-=dmg; target.flash=8; target.shake=5
                self.float_at(target.col,target.row,f"-{dmg}",C_HIT)
                self.screen_shake=4
            shooter.shot=True
            self.after_unit_acts()

        self.bullets.append(Bullet(sx,sy,tx,ty,C_PLAYER,arrive))

    def fire_enemy_bullet(self, shooter, target):
        sx,sy = cell_center(shooter.col,shooter.row)
        tx,ty = cell_center(target.col,target.row)
        dmg, dw = shooter.dmg, target.dw*self.diff["dodge_mult"]

        self.state="BULLET_ENEMY"
        self.dodge_target=target; self.dodge_timer=dw; self.dodge_window=dw; self.dodged=False

        def arrive():
            if not self.dodged:
                target.hp-=dmg; target.flash=8; target.shake=5
                self.float_at(target.col,target.row,f"-{dmg}",C_HIT)
                self.screen_shake=4
            else:
                self.float_at(target.col,target.row,"DODGED!",C_DODGE)
            self.dodge_target=None
            self.check_win()
            if self.state!="GAMEOVER": self.state="ENEMY_THINK"; self.enemy_delay=0.4

        self.bullets.append(Bullet(sx,sy,tx,ty,C_ENEMY,arrive))

    def space_pressed(self):
        if self.state=="BULLET_ENEMY" and self.dodge_timer>0: self.dodged=True

    def after_unit_acts(self):
        self.selected=None; self.move_tiles, self.shoot_tiles = [], []
        self.check_win()
        if self.state=="GAMEOVER": return
        if any(not u.done() for u in self.alive("player")): self.state="PLAYER_SELECT"
        else:
            self.enemy_q=list(self.alive("enemy")); self.state="ENEMY_THINK"; self.enemy_delay=0.7

    def enemy_think(self):
        if not self.enemy_q: self.end_enemy_turn(); return
        e = self.enemy_q.pop(0)
        if not e.alive(): self.enemy_think(); return
        players = self.alive("player")
        if not players: self.end_enemy_turn(); return

        smart = self.diff["ai_smart"]
        target = min(players,key=lambda p: p.hp) if smart else min(players,key=lambda p:mdist(e.pos(),p.pos()))

        best, best_d = None, mdist(e.pos(),target.pos())
        for tc,tr in self.reachable(e):
            d = mdist((tc,tr),target.pos())
            if d<best_d: best_d=d; best=(tc,tr)
        if best: e.col,e.row=best
        e.moved=True

        in_range = [p for p in players if mdist(e.pos(),p.pos())<=e.effective_range()]
        if in_range:
            st = in_range[0]
            e.shot=True; self.fire_enemy_bullet(e,st)
        else: e.shot=True; self.state="ENEMY_THINK"; self.enemy_delay=0.35

    def end_enemy_turn(self):
        for u in self.alive(): u.reset()
        self.state="PLAYER_SELECT"

    def check_win(self):
        if not self.alive("enemy"): self.winner="player"; self.state="GAMEOVER"
        elif not self.alive("player"): self.winner="enemy"; self.state="GAMEOVER"

    def update(self, dt):
        for b in self.bullets: b.update()
        arrived = [b for b in self.bullets if b.done]
        self.bullets = [b for b in self.bullets if not b.done]
        for b in arrived: b.on_arrive()
        if self.state=="BULLET_ENEMY" and self.dodge_timer>0: self.dodge_timer-=dt
        for x in self.bursts: x.update()
        for x in self.floats: x.update()
        if self.screen_shake>0: self.screen_shake-=1
        if self.state=="ENEMY_THINK":
            self.enemy_delay-=dt
            if self.enemy_delay<=0: self.enemy_think()

    def draw(self):
        screen.fill(BG)
        ox = random.randint(-2,2) if self.screen_shake>0 else 0
        oy = random.randint(-2,2) if self.screen_shake>0 else 0

        for r in range(ROWS):
            for c in range(COLS):
                rc = cell_rect(c,r); rc.move_ip(ox,oy)
                pygame.draw.rect(screen,C_DARK if(c+r)%2==0 else C_LIGHT,rc)
                pygame.draw.rect(screen,C_LINE,rc,1)

        for tiles,col in [(self.move_tiles,C_MOVE),(self.shoot_tiles,C_SHOOT)]:
            for(c,r) in tiles:
                s = pygame.Surface((CELL,CELL),pygame.SRCALPHA)
                pygame.draw.rect(s,(*col,65),(0,0,CELL,CELL),border_radius=5)
                rc = cell_rect(c,r); rc.move_ip(ox,oy)
                screen.blit(s,rc.topleft)

        for u in self.units:
            if u.alive(): u.draw(screen,selected=(u==self.selected))

        for b in self.bullets: b.draw(screen)
        for b in self.bursts:  b.draw(screen)
        for f in self.floats:  f.draw(screen)

        if self.state=="BULLET_ENEMY" and self.dodge_timer>0: self._draw_dodge_bar()
        self._draw_panel()
        if self.state=="GAMEOVER": self._draw_gameover()

    def _draw_dodge_bar(self):
        bw,bh=360,52; bx=PNL//2-bw//2; by=6
        pct=self.dodge_timer/self.dodge_window
        pygame.draw.rect(screen,(28,28,50),(bx,by+26,bw,12),border_radius=4)
        pygame.draw.rect(screen,C_DODGE,(bx,by+26,int(bw*pct),12),border_radius=4)
        lbl=F_BIG.render(">> SPACE TO DODGE! <<",True,C_DODGE)
        screen.blit(lbl,(bx+bw//2-lbl.get_width()//2,by+2))

    def _draw_panel(self):
        pygame.draw.rect(screen,C_PANEL,(PNL,0,PNW,GW_SH))
        pygame.draw.line(screen,C_LINE,(PNL,0),(PNL,GW_SH),1)
        y=10; cx2=PNL+PNW//2

        def t(txt,f,col,center=False):
            nonlocal y
            lbl=f.render(txt,True,col)
            x=cx2-lbl.get_width()//2 if center else PNL+12
            screen.blit(lbl,(x,y)); y+=lbl.get_height()+3

        t("GRID WARS", F_BIG, C_PLAYER, True)
        t(f"Killed: {self.get_killed_count()} / {self.total_enemies_spawned}", F_MED, C_HIT, True)
        t(f"Difficulty: {self.diff_key}", F_MED, (255,235,70), True)
        y += 10

        t("== HOW TO PLAY ==", F_MED, C_MOVE)
        t("1. Click a GREEN unit to select it", F_SM, C_WHITE)
        t("2. Click a BLUE tile to move your unit", F_SM, C_WHITE)
        t("3. Click a YELLOW tile to target an enemy", F_SM, C_WHITE)
        t("4. Click selected unit twice to skip moving", F_SM, C_WHITE)
        t("5. Enemy turns happen automatically next", F_SM, C_WHITE)
        t("6. Hit SPACE BAR instantly when attacked to DODGE!", F_SM, C_DODGE)
        y += 15

        t("== UNIT REGISTRY ==", F_MED, C_SHOOT)
        registry_items = [
            ("S - Scout",     "Fast 3-move. Fragile but has easiest dodge windows."),
            ("O - Soldier",   "Balanced 2-move tactical front-line fighter."),
            ("T - Tank",      "Slow 1-move armor. Massive HP and heavy attack dmg."),
            ("M - Medic",     "Heals adjacent allies +3 HP automatically."),
            ("N - Sniper",    "Long-range cover fire (+3 map reach if stationary)."),
            ("G - Grenadier", "Deals 1 damage to ALL targets inside a 3x3 layout."),
            ("R - Recon",     "Uses smoke screens to block incoming sight-lines.")
        ]
        for name, desc in registry_items:
            t(name, F_MED, (100, 200, 255))
            t(desc, F_SM, (170, 170, 185))
            y += 2
        
        y = GW_SH - 30
        t("Press ENTER on GameOver to drop back out", F_TINY, C_DIM, True)

    def _draw_gameover(self):
        ov = pygame.Surface((PNL,GW_SH),pygame.SRCALPHA)
        ov.fill((8,8,16,185)); screen.blit(ov,(0,0))
        earned_points = self.calculate_reward_points()
        
        if self.winner=="player":
            t1 = F_BIG.render("VICTORY!",True,C_PLAYER)
            t2 = F_MED.render(f"Cleared! Earned +{earned_points} points",True,C_WHITE)
        else:
            t1 = F_BIG.render("DEFEATED",True,C_ENEMY)
            t2 = F_MED.render(f"Wiped out. Earned 0 points",True,C_WHITE)
            
        t3 = F_SM.render("Press ENTER to return to your school map",True,C_DIM)
        cx = PNL//2
        screen.blit(t1,(cx-t1.get_width()//2,GW_SH//2-60))
        screen.blit(t2,(cx-t2.get_width()//2,GW_SH//2-4))
        screen.blit(t3,(cx-t3.get_width()//2,GW_SH//2+44))

    def get_killed_count(self):
        current_alive_enemies = len([u for u in self.units if u.team=="enemy" and u.alive()])
        return self.total_enemies_spawned - current_alive_enemies

    def calculate_reward_points(self):
        if self.winner != "player":
            return 0
        kills = self.get_killed_count()
        if self.diff_key == "EASY": points = kills * 1.0 + 2.0
        elif self.diff_key == "NORMAL": points = kills * 1.5 + 2.5
        else: points = kills * 2.0 + 3.0
        return min(15, int(points))

# ── Main Runtime Flow Manager ────────────────────────────────────────────────
async def main():
    global screen

    player = Player("Student", 200, 200)
    quiz = QuizManager()
    vending = VendingMachine()

    active_game_scene = "BASE_MAP"
    grid_wars_instance = None
    message = "Press 'H' to complete assignments. Move to Vending Machine and press 'E' to shop."

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        if active_game_scene == "BASE_MAP":
            timeout_msg = quiz.update_timer(player)
            if timeout_msg:
                message = timeout_msg

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h and not quiz.active and not quiz.menu_open and not quiz.energy_prompt and not quiz.snack_prompt and not vending.shop_open:
                        quiz.open_menu()
                        message = "Select a task assignment!"
                    elif event.key == pygame.K_e and vending.player_nearby(player) and not quiz.active and not quiz.energy_prompt and not quiz.snack_prompt:
                        vending.shop_open = not vending.shop_open
                        message = "Welcome to the school shop!" if vending.shop_open else "Closed shop"

                result = quiz.type_answer(event, player)
                if result: message = result

                choice = quiz.navigate_menu(event)
                if choice:
                    subject, difficulty = choice
                    if subject == "Grid Wars Tasks":
                        active_game_scene = "GRID_WARS"
                        grid_wars_instance = IntegratedGridWars(difficulty)
                        quiz.menu_open = False
                        screen = pygame.display.set_mode((GW_SW, GW_SH))
                    else:
                        quiz.start_quiz(subject, difficulty, player)
                        if quiz.energy_prompt:
                            message = "Consume Energy Drinks to boost your countdown timer!"
                        else:
                            message = f"Started {subject} assignment ({difficulty})!"

                vend_result = vending.navigate(event, player)
                if vend_result: message = vend_result

            keys = pygame.key.get_pressed()
            if not quiz.active and not quiz.menu_open and not quiz.energy_prompt and not quiz.snack_prompt and not vending.shop_open:
                player.move(keys, BASE_SW, BASE_SH)

            screen.fill((30,30,30))
            player.draw(screen)
            vending.draw(screen)

            points_text = font.render(f"Points: {player.points}", True, (255,255,255))
            screen.blit(points_text, (10,10))

            inv_counts = {item: player.inventory.count(item) for item in set(player.inventory)}
            inv_str = ", ".join([f"{k} (x{v})" for k, v in inv_counts.items()]) if player.inventory else "Empty"
            inv_text = font.render(f"Inventory: {inv_str}", True, (200,200,200))
            screen.blit(inv_text, (10,35))

            msg_lines = message.split("\n")
            for i, line in enumerate(msg_lines):
                msg_text = font.render(line, True, (255,255,0))
                screen.blit(msg_text, (10, 70 + i * 25))

            vending.draw_shop(screen)
            quiz.draw(screen, player)

        elif active_game_scene == "GRID_WARS":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if grid_wars_instance.state == "GAMEOVER":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        reward = grid_wars_instance.calculate_reward_points()
                        player.points += reward

                        grid_wars_instance = None
                        active_game_scene = "BASE_MAP"
                        screen = pygame.display.set_mode((BASE_SW, BASE_SH))
                        if reward > 0: message = f"Victory! Task cleared. Received +{reward} points!"
                        else: message = "Defeated! Task failed. Earned 0 points."
                        break

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    grid_wars_instance.space_pressed()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    c = (mx - GX) // CELL
                    r = (my - GY) // CELL
                    if 0 <= c < COLS and 0 <= r < ROWS:
                        grid_wars_instance.click(c, r, right=False)

            if grid_wars_instance:
                grid_wars_instance.update(dt)
                grid_wars_instance.draw()

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())