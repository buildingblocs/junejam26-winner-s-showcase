import asyncio
import pygame
import random
import os
import sys
#Setup
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Pygame Text Input")
clock = pygame.time.Clock()
base_font = pygame.font.SysFont("ocra", 32)
vs_font=pygame.font.SysFont("ocra", 18)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('gray15')
color = color_passive
input_box_color=color
state="Start"
shoot_sound=pygame.mixer.Sound("game_asset/sounds/pew.ogg")
gameplay_music=pygame.mixer.Sound("game_asset/sounds/gameplaymusic.ogg")

def draw_text(text,font,text_col,x,y):
    img=base_font.render(text,True,text_col)
    screen.blit(img,(x,y))
input_rect = pygame.Rect(200, 950, 200, 50)
user_text = ''
active = False



#Start Screen
earth_bg = pygame.image.load("game_asset/vs_sprites/bg_1.png").convert_alpha()
earth_bg = pygame.transform.scale(earth_bg, (1920, 1080))

# Background scene2
rain_bg = pygame.image.load("game_asset/vs_sprites/bg_2.png").convert_alpha()
rain_bg = pygame.transform.scale(rain_bg, (1920, 1080))

# Background scene3
comp_bg = pygame.image.load("game_asset/vs_sprites/bg_3_off.png").convert_alpha()
comp_bg = pygame.transform.scale(comp_bg, (1920, 1080))

# Background scene3 
cog_bg_zoomed = pygame.image.load("game_asset/vs_sprites/bg_3_on.png").convert_alpha()
cog_bg_zoomed = pygame.transform.scale(cog_bg_zoomed, (1920, 1080))

# Background scene4
office_bg = pygame.image.load("game_asset/vs_sprites/bg_4.png").convert_alpha()
office_bg = pygame.transform.scale(office_bg, (1920, 1080))

current_bg = earth_bg

# Ending backgrounds
try:
    ending1_bg = pygame.image.load("game_asset/vs_sprites/ending2.png").convert()
    ending1_bg = pygame.transform.scale(ending1_bg, (1920, 1080))
except pygame.error:
    ending1_bg = pygame.Surface((1920, 1080))
    ending1_bg.fill((20, 20, 40))

try:
    ending2_bg = pygame.image.load("game_asset/vs_sprites/ending1.png").convert()
    ending2_bg = pygame.transform.scale(ending2_bg, (1920, 1080))
except pygame.error:
    ending2_bg = pygame.Surface((1920, 1080))
    ending2_bg.fill((40, 20, 20))

# Character
boss_serious = pygame.image.load("game_asset/vs_sprites/boss/boss_serious.png").convert_alpha()
boss_serious = pygame.transform.scale(boss_serious, (600, 700))

boss_upset = pygame.image.load("game_asset/vs_sprites/boss/boss_upset.png").convert_alpha()
boss_upset = pygame.transform.scale(boss_upset, (600, 700))

boss_satisfied = pygame.image.load("game_asset/vs_sprites/boss/boss_satisfied.png").convert_alpha()
boss_satisfied = pygame.transform.scale(boss_satisfied, (600, 700))

boss_sprite = boss_serious
show_boss = False

show_cog_overlay = False

# 3. Input Box
input_rect1 = pygame.Rect(830, 400, 200, 50)
user_text1 = ''
active1 = False
registered = False
registration_time = 0
user_name = ''

# Text Box
box_width = 1200
box_height = 110
box_x = (screen.get_width() - box_width) // 2
box_y = screen.get_height() - box_height - 220

# SCENE 1
dialogues_1 = [
    "The fact that you exist here today, dear reader, is a statistical miracle.",
    "A long, long time ago, something happened. Then something else. And then another thing.",
    "One event gave rise to the next, until different chains across ages linked, however improbably, to you.",
    "And this happened for billions of others as well.",
    "In the far flung corner of the universe, a vast range of beings capable of living and experiencing emerged.",
    "Amongst them, the most intelligent species - Homo Sapiens, Latin for “wise man”",
    "learned to master nature to its will.",
    "It replaced lush forests with towering skyscrapers.",
    "It constructed abstract ideas, split the atom, even reaching beyond the skies.",
    "But don’t you consider it such a pity how they antagonise each other?",
    "How they incessantly fight amongst themselves?",
    "They constantly seek meaning through identities and divisions.",
    "Like genders and nations.",
    "No matter how far human technology advances,",
    "they can’t let go of the need to prove that they are worthier than other humans.",
    "In fact, humanity uses its own tools created for its own benefit against itself.",
    "So, is humanity truly progressing,",
    "or are they merely repeating the same conflict cycle with increasingly sophisticated tools?",
    "Peace is just a temporary state that gives purpose until the next conflict arrives,",
    "and history repeats itself.",
    "It won’t be long before the doomsday clock reaches zero."
]

# SCENE 2
dialogues_2 = [
    "N: October 1970, People’s Republic of Arteniza.",
    "[USER] And when that happens…",
    "[USER] (wakes up)",
    "You are facing the window. It is a rainy day.",
    "You find yourself slumped over your desk in your private office at CISA.",
    "CISA is a statutory board under the People’s Republic of Arteniza’s Ministry of Defence.",
    "It stands for the Cybersecurity and Information Systems Agency.",
    "[USER] Did I fall asleep at work?",
    "[USER] (grumbles) Ugh, I’m not in a good mood whatsoever.",
    "[USER] Another day of war.",
    "[USER] Another day of people killing each other. Over what? Lines on a map.",
    "For the past six years, People’s Republic of Arteniza and the Republic of Boldenlandt,",
    "have remained in armed conflict over the Vost River Basin, a resource-rich region claimed by both nations.",
    "[USER] Boldenlandt says it’s theirs…Arteniza says it’s ours.",
    "[USER] I’m not taking sides. I hate both parties. There shouldn’t be a war at all.",
    "[USER] I don’t understand why it’s so difficult to just share what common land we have.",
    "[USER] …And I was basically forced here. I can’t even leave my job without arousing suspicion.",
    "[USER] My beloved motherland would accuse me of “betrayal” when I stop being useful to them."
]

# SCENE 3
dialogues_3 = [
    "[USER] Also, I have to deal with Kolya. That crusty old man. Every. single. day.",
    "[USER] I guess it’s just part of my job.",
    "[USER] Fortunately, ever since the invention of The Cognitor, my work has become easier.",
    "The Cognitor rings.",
    "You have received an immediate mail from your boss, Kolya. It needs to be attended to at once.",
    "[USER] But it also means Kolya gives me more work…",
    "You power on The Cognitor.",
    "The Cognitor is a programmable computer capable of various tasks,",
    "including storing, processing, and retrieving information, accessing the Internet, and so much more.",
    "The layout of The Cognitor is quite simple looking. But it isn’t an issue since it’s user friendly."
]

# SCENE 4 
dialogues_4 = [
    "Kolya: You’re here.",                        
    "Kolya: Listen carefully.",                   
    "Kolya: At 01:56 local time last night, CISA detected",
    "a self-propagating electronic virus in the Cognitor operating system.", 
    "(01:56…)",                                   
    "(He really doesn’t sleep.)",              
    "Kolya: As you know, every Cognitor in Arteniza uses the same operating system.", 
    "Nearly all civilian services depend on it.", 
    "Kolya: The system connects users to a national network.",
    "Kolya: It also has access to the global Internet.", 
    "Kolya: The virus entered through that external connection and is now spreading across our national network.",
    "Kolya: Records, communications, and controls - all of it is affected.",
    "Kolya: Evidence has been pointing at The Republic of Boldenlandt being responsible for the attack.",
    "Kolya: Fortunately, the CISA operates under a separate isolated network.", 
    "Kolya: But we need to neutralise the virus at once. ",
    "And I have selected you to help me in doing so, because I believe that you can do the job.", 
    "Kolya: Do not waste time.",                   
    "User: …",                                     
    "Kolya: Understood?",                        
    "User: Yeah, Kolya…I mean, Director.",         
    "The fate of the Arteniza is in your hands.",  
    "Your first assignment is ready.",           
    "Good luck."                                   
]

# SCENE 5
dialogues_5 = [
    "Kolya: We managed to secure the computer directly linked to the initial network intrusion point.",
    "Kolya: Luckily, the terminal is completely unlocked.",
    "[USER] (Wow. Finally some good news.)",
    "Kolya: However, we have a different problem.",
    "Kolya: The core directories require a master override key to access the logs, and we don't have it",
    "SHOW_NOTE_TRIGGER",
    "Kolya: We found a note beside it. The previous user left it behind.",
    "Kolya: But nobody leaves their password like this in the open.",
    "Kolya: What do you think they are?",
    "[USER] Numbers?",
    "Kolya: …",
    "Kolya: Try to decode them."
]

# SCENE 6
dialogues_6 = [
    "Kolya: Nice job on completing the first task.",
    "Kolya: Now, we need to break into the secondary terminal to bounce our signal",
    "[USER] Oh no... What do I need to do?",
    "Kolya: The system is going to flood us with raw data traffic to try and crash our connection.",
    "Kolya: You have to sort it fast.",
    "Kolya: Files will drop from the top of the screen.",
    "Kolya: Move your terminal left and right and blast them with matching data-type bullets",
    "Kolya: to delete them before they hit the bottom.",
    "Kolya: Match whole numbers like 32 with Integer bullets,",
    "Kolya: decimals like 5.0 with Float,",
    "Kolya: text like \"apple\" with String,",
    "Kolya: and True/False with Boolean bullets.",
    "Kolya: Defend the system until you reach a score of 100.",
    "Kolya: Goodluck."
]

# ENDING 1 (Win)
dialogues_ending1 = [
    "November 1970, People's Republic of Arteniza.",
    "Within days, both the People's Republic of Arteniza ",
    "and the Republic of Boldenlandt declare a mutual peace agreement.",
    "However, both countries will suffer from the economic consequences of the crisis.",
    "[USER] Funny.",
    "[USER] All these years of killing and people insisting they were right.",
    "[USER] In the end, they just sat down and talked.",
    "[USER] I still don't understand. Why are we still like this??",
    "[USER] Since the earliest periods of history, we've always been like this.",
    "[USER] I don't think humanity is cruel. Maybe that's not quite right.",
    "[USER] Humans are capable of incredible kindness.",
    "[USER] But we keep finding reasons to divide ourselves.",
    "[USER] We create tools to improve our lives, then use the same tools against each other.",
    "[USER] Isn't that incredibly tragic?",
    "[USER] A species, so full of potential…and so eager to waste it.",
    "[USER] Still…at least, fewer mothers will receive bad news,",
    "[USER] and fewer children will grow up without parents.",
    "The rain stops outside."
]

# ENDING 2 (Lose)
dialogues_ending2 = [
    "November 1970, People's Republic of Arteniza.",
    "You failed to quarantine the virus.",
    "The virus spreads through the national network. It is everywhere.",
    "Sensitive data from governments, civilians, private organisations - all of it is seized.",
    "Kolya: We've lost control.",
    "Within days, foreign \"stabilisation forces\" enter Artenizan territory.",
    "The People's Republic of Arteniza ceases independent command of its national network.",
    "A new administration is declared.",
    "President Donaldus Trumpus of the Republic of Boldenlandt announces",
    "\"full stabilisation of the region\". Order is restored under new oversight.",
    "The Cognitor remains as the standard computer in Arteniza, but all users are monitored.",
    "[USER] Funny.",
    "[USER] It feels oddly peaceful. After all that suffocating pressure from Arteniza…",
    "[USER] in fact, I feel relieved. It's quite a blessing in disguise.",
    "[USER] But I still don't understand. Why are we still like this???",
    "[USER] Since the earliest periods of history, we've always been like this.",
    "[USER] We keep finding reasons to divide ourselves.",
    "[USER] We create tools to improve our lives, then use the same tools against each other.",
    "[USER] Isn't that incredibly tragic?",
    "[USER] A species, so full of potential…and so eager to waste it.",
    "[USER] Still…at least, fewer mothers will receive bad news,",
    "[USER] and fewer children will grow up without parents.",
    "The rain stops outside."
]

# Email lines 
email_text_lines = [
    "Electronic mails.",
    "-------------------------------",
    "Sender: 0193409132",
    "Recipient: 0127398483",
    "Report to my office immediately.",
    "All current work is suspended.",
    "-------------------------------"
]

# Color Text
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
USER_COLOUR = (0, 0, 139)  
BOSS_COLOUR = (139, 0, 0) 

def get_text_color(text):
    if text.startswith("[USER]") or text.startswith("User:"):
        return USER_COLOUR
    elif text.startswith("Kolya:"):
        return BOSS_COLOUR
    return BLACK

def clean_dialogue_line(text, current_username):
    """Strips out visual scene script tags and inserts the configured player name or dynamic prefix."""
    display_name = current_username if current_username != '' else "[USER]"

    if text.startswith("[USER]"):
        return text.replace("[USER]", display_name)
    elif text.startswith("User:"):
        return text.replace("User:", f"{display_name}:")
    elif text.startswith("Kolya:"):
        return text
    elif text.startswith("N:"):
        return text.replace("N:", "").strip()
    return text

# Text movement
stage = 1
dialogues = dialogues_1
active_dialogue = 0
dialogue = dialogues[active_dialogue]

counter = 0
speed = 1
done = False
show_dialogue = True

switching = False
switch_timer = 0




#First Game
class Folder:
    def __init__(self,x,y,name):
        self.x=x
        self.y=y
        self.name=name 
        self.img="game_asset/puzzles/1/folder.png"
        self.img = pygame.image.load(self.img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (200, 200))
    def draw(self,screen):
        screen.blit(self.img, (self.x, self.y))

class File:
    def __init__(self,x,y,name,virus):
        self.x=x
        self.y=y
        self.virus=virus
        color_passive = (238,238,238)
        color_active = (68,85,90)
        self.textcolor=(0,0,0)
        self.name=name
        self.rect=pygame.Rect(self.x, self.y, 600, 50)
        self.active=False
        if self.active==False:
            color=color_passive
        else:
            color=color_active
        self.boxcolor=color
    def draw(self,screen):
        pygame.draw.rect(screen, self.boxcolor, self.rect)
        draw_text(self.name,base_font,self.textcolor,self.x,self.y)

class DeleteBox:   
    def __init__(self,x,y,name,folder,index):
        self.x=x
        self.y=y
        self.name=name
        self.folder=folder
        self.index=index
        self.textcolor=(255,255,255)
        self.rect=pygame.Rect(self.x, self.y, 200, 50)
        self.boxcolor=(255,0,0)
    def draw(self,screen):
        pygame.draw.rect(screen, self.boxcolor, self.rect)
        draw_text("Delete",base_font,self.textcolor,self.x,self.y)

Folder1=Folder(250,150,"Downloads")
Folder2=Folder(470,150,"Local_Disk")
Folder3=Folder(690,150,"New_Volume")
Folder4=Folder(910,150,"Employees")
Folder5=Folder(1130,150,"Documents")
Folder6=Folder(1350,150,"System")
folders=[Folder1,Folder2,Folder3,Folder4,Folder5,Folder6]
folders_names=["Downloads","LocalDisk","NewVolume","Employees","Documents","System"]

download_1=File(250,150,"SubmarineBlueprint.pdf",False)
download_2=File(250,210,"CognitorBlueprint.pdf",False)
download_3=File(250,270,"TelecommunicatorDesign.jpg",False)
download_4=File(250,330,"TankBlueprint.exe",True)
download_5=File(250,390,"JetBlueprint.pdf",False)
download_6=File(250,450,"WarshipBlueprint.exe",True)
download_7=File(250,510,"SubmarineTorpedo.pdf",False)
downloads_files=[download_1,download_2,download_3,download_4,download_5,download_6,download_7]

localdisk_1=File(250,150,"BerlinUltimatum.txt",False)
localdisk_2=File(250,210,"OperationOverlordPlan.pdf",False)
localdisk_3=File(250,270,"U2SpyReport.bin",True)
localdisk_4=File(250,330,"KremlinCommunications.exe",True)
localdisk_5=File(250,390,"CubanMissileCrisis.pdf",False)
localdisk_6=File(250,450,"IronCurtainAnalysis.jpg",False)
localdisk_7=File(250,510,"IronCurtainData.pdf",False)
localdisk_files=[localdisk_1,localdisk_2,localdisk_3,localdisk_4,localdisk_5,localdisk_6,localdisk_7]

newvolume_1=File(250,150,"ChernobylLeak.exe",True)
newvolume_2=File(250,210,"StasiIntelligence.bin",True)
newvolume_3=File(250,270,"FallofBerlinTranscript.txt",False)
newvolume_4=File(250,330,"NixonTapes.pdf",False)
newvolume_5=File(250,390,"VietnamWarLogs.pdf",False)
newvolume_6=File(250,450,"PeaceTreatyDraft.doc",False)
newvolume_7=File(250,510,"BrinkmanshipManifesto.pdf",False)
newvolume_files=[newvolume_1,newvolume_2,newvolume_3,newvolume_4,newvolume_5,newvolume_6,newvolume_7]

employees_1=File(250,150,"CIA_Operatives.xlsx",False)
employees_2=File(250,210,"KGB_Agents.bin",True)
employees_3=File(250,270,"MI6_Contacts.exe",True)
employees_4=File(250,330,"EspionageManual.pdf",False)
employees_5=File(250,390,"DefectionReports.txt",False)
employees_6=File(250,450,"SpyNetworkMap.png",False)
employees_7=File(250,510,"DoubleAgentProtocol.jpg",False)
employees_files=[employees_1,employees_2,employees_3,employees_4,employees_5,employees_6,employees_7]

documents_1=File(250,150,"NATO_Treaty.pdf",False)
documents_2=File(250,210,"WarsawPact.txt",False)
documents_3=File(250,270,"NuclearCodes.exe",True)
documents_4=File(250,330,"ProxyWarStrategies.bin",True)
documents_5=File(250,390,"DetenteFailure.pdf",False)
documents_6=File(250,450,"ArmsRaceData.pdf",False)
documents_7=File(250,510,"ContainmentPolicy.txt",False)
documents_files=[documents_1,documents_2,documents_3,documents_4,documents_5,documents_6,documents_7]

system_1=File(250,150,"NORAD_Status.bin",True)
system_2=File(250,210,"MAD_Doctrine.exe",True)
system_3=File(250,270,"SatelliteIntel.pdf",False)
system_4=File(250,330,"SubmarineTracker.txt",False)
system_5=File(250,390,"RadarInstallations.jpg",False)
system_6=File(250,450,"LaunchCodes.pdf",False)
system_7=File(250,510,"CabinetMinutes.pdf",False)
system_files=[system_1,system_2,system_3,system_4,system_5,system_6,system_7]

running=True
position="Home"
log=[]
x=0
delete_box=[]
malwares=12
memories=3




#Second game
def get_random_image(folder):
    images = [f for f in os.listdir(f"game_asset/puzzles/2/enemies/{folder}") if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return random.choice(images) if images else None
class Player:
    def __init__(self, img):
        self.x = 960
        self.y = 900
        self.health = 10
        self.speed = 1
        self.shoot_timer = 0

        self.img = pygame.image.load(img).convert_alpha()
        self.img = pygame.transform.scale(self.img, (100, 100))
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
class Enemy:
    def __init__(self,type):
        self.x = 560 + random.randint(0, 4) * 200
        self.y = 100
        self.speed = random.randint(50, 150)/100 *3
        self.type = type
        self.rect = pygame.Rect(self.x, self.y, 75, 75)
        if self.type == 1:
            img_name = get_random_image("integers")
            self.img = pygame.image.load(f"game_asset/puzzles/2/enemies/integers/{img_name}").convert_alpha()
        elif self.type == 2:
            img_name = get_random_image("floats")
            self.img = pygame.image.load(f"game_asset/puzzles/2/enemies/floats/{img_name}").convert_alpha()
        elif self.type == 3:
            img_name = get_random_image("strings")
            self.img = pygame.image.load(f"game_asset/puzzles/2/enemies/strings/{img_name}").convert_alpha()
        elif self.type == 4:
            img_name = get_random_image("booleans")
            self.img = pygame.image.load(f"game_asset/puzzles/2/enemies/booleans/{img_name}").convert_alpha()
        self.img = pygame.transform.scale(self.img, (75, 75))
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
    def update(self):
        self.y += self.speed
        self.rect.y = self.y
class Bullet:
    def __init__(self, type):
        self.x = player.x+25
        self.y = player.y
        self.type = type
        self.speed = 600
        self.rect = pygame.Rect(self.x, self.y, 50, 50)
        if self.type == 1:
            self.img = pygame.image.load("game_asset/puzzles/2/bullets/int.png").convert_alpha()
        elif self.type == 2:
            self.img = pygame.image.load("game_asset/puzzles/2/bullets/float.png").convert_alpha()
        elif self.type == 3:
            self.img = pygame.image.load("game_asset/puzzles/2/bullets/str.png").convert_alpha()
        elif self.type == 4:
            self.img = pygame.image.load("game_asset/puzzles/2/bullets/bool.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (50, 50))
    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
    def updaterect(self):
         self.rect.x = self.x
         self.rect.y = self.y
    def move(self, dt):
        self.y -= self.speed*dt
        self.updaterect()
        if self.y < 0:
            bullets.remove(self)



player=Player("game_asset/puzzles/2/py.png")
shoot_delay = 0.0
spawn_timer = 10
clock = pygame.time.Clock()
running=True
acceleration = 5
notification_timer = 0.75
#Lists
bullets=[]
notifications=[]
enemies=[]
effects=[]
streak=0
score=0
















async def main():
    global acceleration, active, active_dialogue, boss_sprite, color
    global counter, current_bg, dialogue, dialogues, done
    global input_box_color, input_rect, malwares, memories, notification_timer
    global position, registered, registration_time, running, score
    global shoot_delay, show_boss, show_cog_overlay, show_dialogue, spawn_timer
    global stage, state, streak, switch_timer, switching
    global user_name, user_text, x
    while running:
        while running and state=="Start":
            await asyncio.sleep(0)
            clock.tick(60)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load("game_asset/sounds/novelmusic.ogg")
                pygame.mixer.music.play(-1)
            if stage == 4:
                if active_dialogue in [2, 4]:
                    boss_sprite = boss_upset
                elif active_dialogue == 13:   
                    boss_sprite = boss_satisfied
                else:
                    boss_sprite = boss_serious

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                # Handle Mouse Clicks for Input Box
                if event.type == pygame.MOUSEBUTTONDOWN and show_cog_overlay and not registered:
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    input_box_color = color_active if active else color_passive

                if event.type == pygame.KEYDOWN:
                    # Handle Keyboard Input during identity configuration
                    if show_cog_overlay and active and not registered:
                        if event.key == pygame.K_RETURN:
                            if user_text.strip() == "":
                                user_name = "User" 
                            else:
                                user_name = user_text.strip()
                            print(f"User registered as: {user_name}")
                            registered = True
                            registration_time = pygame.time.get_ticks() 
                            user_text = ''
                            active = False
                        elif event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                        else:
                            if len(user_text) < 20: 
                                user_text += event.unicode
                
                    # Dialogue navigation progression
                    elif event.key == pygame.K_RETURN and done:
                        if active_dialogue < len(dialogues) - 1:
                            active_dialogue += 1
                            dialogue = dialogues[active_dialogue]
                            counter = 0
                            done = False
                            if stage == 3 and active_dialogue == 5: 
                                show_cog_overlay = True
                                current_bg = cog_bg_zoomed
                        else:
                            if stage in [1, 2, 3]:
                                switching = True
                                switch_timer = pygame.time.get_ticks()
                                show_dialogue = False
                            else:
                                # End of stage 4 → transition to Scene5 (password puzzle briefing)
                                show_dialogue = False
                                state = "Scene5"

            # Background
            screen.blit(current_bg, (0, 40))

            # boss spawing
            if show_boss:
                screen.blit(boss_sprite, (710, 160))

            # Cognitor screen
            input_rect = pygame.Rect(830, 400, 200, 50)
            if show_cog_overlay:
                if not registered:
                    draw_text('What is your name?', base_font, BLACK, 830, 340)
                
                    text_surface = base_font.render(user_text, True, BLACK)
                    pygame.draw.rect(screen, input_box_color, input_rect, 2)
                    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
                    input_rect.w = max(200, text_surface.get_width() + 10)
                else:
                    time_elapsed = pygame.time.get_ticks() - registration_time
                
                    if time_elapsed < 2000:
                        draw_text("Welcome " + user_name, base_font, BLACK, 830, 340)
                    elif time_elapsed < 6000:
                        start_y = 230
                        line_spacing = 40
                        for i, line in enumerate(email_text_lines):
                            draw_text(line, vs_font, BLACK, 620, start_y +100 + (i * line_spacing))
                    else:
                        # Transition
                        show_cog_overlay = False
                        current_bg = office_bg
                        show_boss = True
                        stage = 4
                        dialogues = dialogues_4
                        active_dialogue = 0
                        dialogue = dialogues[0]
                        counter = 0
                        done = False
                        show_dialogue = True

            # Scene switching
            if switching:
                if pygame.time.get_ticks() - switch_timer > 1000:
                    if stage == 1:
                        current_bg = rain_bg
                        stage = 2
                        dialogues = dialogues_2
                    elif stage == 2:
                        current_bg = comp_bg
                        stage = 3
                        dialogues = dialogues_3
                    elif stage == 3:
                        current_bg = office_bg
                        stage = 4
                        dialogues = dialogues_4

                    active_dialogue = 0
                    dialogue = dialogues[0]
                    counter = 0
                    done = False
                    show_dialogue = True
                    switching = False

            # Dialogue box
            if show_dialogue and not show_cog_overlay:
                pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
                pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)

                cleaned_line = clean_dialogue_line(dialogue, user_name)

                if counter < speed * len(cleaned_line):
                    counter += 1
                else:
                    done = True

                visible_text = cleaned_line[0:counter // speed]
                color = get_text_color(dialogue)

                text_surface = vs_font.render(visible_text, True, color)
                screen.blit(text_surface, (box_x + 35, box_y + 30))
        
            pygame.display.update()            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

        # ── SCENE 5 ── Password-puzzle briefing (between Start and Terminal) ──────
        scene5_dialogue_idx = 0
        scene5_counter = 0
        scene5_done = False
        scene5_show_note = False
        scene5_boss_sprite = boss_serious

        while running and state == "Scene5":
            await asyncio.sleep(0)
            clock.tick(60)
            screen.blit(office_bg, (0, 40))

            # Boss expression
            if scene5_dialogue_idx == 10:
                scene5_boss_sprite = boss_upset
            else:
                scene5_boss_sprite = boss_serious
            screen.blit(scene5_boss_sprite, (710, 160))

            # Sticky note
            if scene5_show_note:
                note_box = pygame.Rect(1300, 200, 550, 180)
                pygame.draw.rect(screen, (253, 253, 150), note_box)
                pygame.draw.rect(screen, (220, 220, 100), note_box, 3)
                draw_text("Note Found:", vs_font, BLACK, 1320, 220)
                draw_text("84 101 114 109 105 110 97 108", vs_font, BLACK, 1320, 280)

            # Dialogue box
            raw_line = dialogues_5[scene5_dialogue_idx]
            cleaned = clean_dialogue_line(raw_line, user_name)
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
            if scene5_counter < speed * len(cleaned):
                scene5_counter += 1
            else:
                scene5_done = True
            visible = cleaned[0:scene5_counter // speed]
            screen.blit(vs_font.render(visible, True, get_text_color(raw_line)), (box_x + 35, box_y + 30))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and scene5_done:
                    scene5_dialogue_idx += 1
                    # Handle the sticky note trigger mid-list
                    if scene5_dialogue_idx < len(dialogues_5) and dialogues_5[scene5_dialogue_idx] == "SHOW_NOTE_TRIGGER":
                        scene5_show_note = True
                        scene5_dialogue_idx += 1
                    if scene5_dialogue_idx >= len(dialogues_5):
                        state = "Terminal"
                    else:
                        scene5_counter = 0
                        scene5_done = False

            pygame.display.update()

        while running and state=="Terminal":
            await asyncio.sleep(0)
            clock.tick(60)
            screen.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = True
                    else:
                        active = False
                    color = color_active if active else color_passive

                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            x+=1
                            delete_box.clear()
                            if user_text[0:3]=="cd ":
                                log.insert(0,[user_text,(0,255,0),x])
                                if user_text[3:] in folders_names:
                                    position=user_text[3:]
                                elif user_text[3:]=="Home" or user_text[3:]=="":
                                    position="Home"
                                else:
                                    log.insert(0,["Error: Folder not found",(255,0,0),x])
                            else:
                                log.insert(0,["Syntax Error",(255,0,0),x])
                            user_text = ''
                        elif event.key == pygame.K_BACKSPACE:
                            user_text = user_text[:-1]
                        else:
                            if len(user_text) < 60: 
                                user_text += event.unicode
            input_rect = pygame.Rect(200, 950, 200, 50)
            text_surface = base_font.render(user_text, True, (0, 255, 0))
            pygame.draw.rect(screen, color, input_rect, 2)
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            input_rect.w = max(140, text_surface.get_width() + 10)
            pygame.draw.line(screen, (0, 255, 0), (0, 1000), (1920, 1000), 3)
            pygame.draw.line(screen, (0, 255, 0), (0, 600), (1920, 600), 3)

            if len(log)>11:
                log.pop(-1)

            if position=="Home":
                draw_text("Home",base_font,(255,255,255),250,100)
                draw_text("Downloads",base_font,(255,255,255),260,330)
                draw_text("LocalDisk",base_font,(255,255,255),480,330)
                draw_text("NewVolume",base_font,(255,255,255),700,330)
                draw_text("Employees",base_font,(255,255,255),920,330)
                draw_text("Documents",base_font,(255,255,255),1130,330)
                draw_text("System",base_font,(255,255,255),1390,330)
                for folder in folders:
                    folder.draw(screen)

            if position=="Downloads":
                draw_text("Home//Downloads",base_font,(255,255,255),250,100)
                for file in downloads_files:
                    file.draw(screen)
                for download_file in downloads_files:
                    if download_file.rect.collidepoint(pygame.mouse.get_pos()):
                        download_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((download_file.x+620),download_file.y,download_file.name,"downloads",downloads_files.index(download_file)))

            if position=="LocalDisk":
                draw_text("Home//LocalDisk",base_font,(255,255,255),250,100)
                for file in localdisk_files:
                    file.draw(screen)
                for localdisk_file in localdisk_files:
                    if localdisk_file.rect.collidepoint(pygame.mouse.get_pos()):
                        localdisk_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((localdisk_file.x+620),localdisk_file.y,localdisk_file.name,"localdisk",localdisk_files.index(localdisk_file)))

            if position=="NewVolume":
                draw_text("Home//NewVolume",base_font,(255,255,255),250,100)
                for file in newvolume_files:
                    file.draw(screen)
                for newvolume_file in newvolume_files:
                    if newvolume_file.rect.collidepoint(pygame.mouse.get_pos()):
                        newvolume_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((newvolume_file.x+620),newvolume_file.y,newvolume_file.name,"newvolume",newvolume_files.index(newvolume_file)))

            if position=="Employees":
                draw_text("Home//Employees",base_font,(255,255,255),250,100)
                for file in employees_files:
                    file.draw(screen)
                for employees_file in employees_files:
                    if employees_file.rect.collidepoint(pygame.mouse.get_pos()):
                        employees_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((employees_file.x+620),employees_file.y,employees_file.name,"employees",employees_files.index(employees_file)))

            if position=="Documents":
                draw_text("Home//Documents",base_font,(255,255,255),250,100)
                for file in documents_files:
                    file.draw(screen)
                for documents_file in documents_files:
                    if documents_file.rect.collidepoint(pygame.mouse.get_pos()):
                        documents_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((documents_file.x+620),documents_file.y,documents_file.name,"documents",documents_files.index(documents_file)))

            if position=="System":
                draw_text("Home//System",base_font,(255,255,255),250,100)
                for file in system_files:
                    file.draw(screen)
                for system_file in system_files:
                    if system_file.rect.collidepoint(pygame.mouse.get_pos()):
                        system_file.active=True
                        if pygame.mouse.get_pressed()[0]:
                            delete_box.append(DeleteBox((system_file.x+620),system_file.y,system_file.name,"system",system_files.index(system_file)))

            for notification in log:
                draw_text(notification[0],base_font,notification[1],200,900-30*log.index(notification))

            for delete in delete_box:
                delete.draw(screen)
                if delete.rect.collidepoint(pygame.mouse.get_pos()):
                    if pygame.mouse.get_pressed()[0]:
                        if delete.folder=="downloads":
                            if downloads_files[delete.index].virus==True:
                                downloads_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        elif delete.folder=="localdisk":
                            if localdisk_files[delete.index].virus==True:
                                localdisk_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        elif delete.folder=="newvolume":
                            if newvolume_files[delete.index].virus==True:
                                newvolume_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        elif delete.folder=="employees":
                            if employees_files[delete.index].virus==True:
                                employees_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        elif delete.folder=="documents":
                            if documents_files[delete.index].virus==True:
                                documents_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        elif delete.folder=="system":
                            if system_files[delete.index].virus==True:
                                system_files.pop(delete.index)
                                malwares-=1
                                log.insert(0,["Malware Deleted SuccessFully. The number of remaining Malwares is: "+str(malwares),(0,255,0),x])
                            else:
                                memories-=1
                                log.insert(0,["Incorrect. Important File Deleted. The number of remaining Memories is: "+str(memories),(255,0,0),x])
                        delete_box.clear()
        
            if (player.health <= 0 or memories <= 0) and state == "DataType":
                state = "Ending2"
                gameplay_music.stop()
                pygame.mixer.music.load("game_asset/sounds/novelmusic.ogg")
                pygame.mixer.music.play(-1)
        
        
        
            pygame.display.update()
            # When all malware is cleared, move to Scene 6 briefing
            if malwares <= 0:
                state = "Scene6"

        #Scene 6
        scene6_dialogue_idx = 0
        scene6_counter = 0
        scene6_done = False
        scene6_boss_sprite = boss_serious

        while running and state == "Scene6":
            await asyncio.sleep(0)
            clock.tick(60)
            screen.blit(office_bg, (0, 40))

            # Boss expression switches at line 4 (Kolya explains the task)
            if scene6_dialogue_idx >= 4:
                scene6_boss_sprite = boss_satisfied
            else:
                scene6_boss_sprite = boss_serious
            screen.blit(scene6_boss_sprite, (710, 160))

            # Dialogue box
            raw_line = dialogues_6[scene6_dialogue_idx]
            cleaned = clean_dialogue_line(raw_line, user_name)
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
            if scene6_counter < speed * len(cleaned):
                scene6_counter += 1
            else:
                scene6_done = True
            visible = cleaned[0:scene6_counter // speed]
            screen.blit(vs_font.render(visible, True, get_text_color(raw_line)), (box_x + 35, box_y + 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and scene6_done:
                    scene6_dialogue_idx += 1
                    if scene6_dialogue_idx >= len(dialogues_6):
                        state = "DataType"
                        pygame.mixer.music.stop()
                        gameplay_music.play(-1)
                    else:
                        scene6_counter = 0
                        scene6_done = False

            pygame.display.update()

        #DataType
        while running and state=="DataType":
            await asyncio.sleep(0)
            dt = clock.tick(60) / 1000
            screen.fill((0, 0, 0))
            for lane_x in [510,710, 910, 1110, 1310,1510]:
                pygame.draw.line(screen, (0, 255, 0), (lane_x, 100), (lane_x, 980), 3)
            draw_text("1:Integer",base_font,(255,255,255),10,135)

            #Event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        player.x -= 200
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.x += 200
                    if player.x < 960-2*200:
                        player.x = 960-2*200
                    elif player.x > 960+2*200:
                        player.x = 960+2*200
                    if shoot_delay <= 0:
                        if event.key == pygame.K_1:
                            bullets.append(Bullet(1))
                            shoot_delay = 0.4
                            shoot_sound.play()
                        elif event.key == pygame.K_2:
                            bullets.append(Bullet(2))
                            shoot_delay = 0.4
                            shoot_sound.play()
                        elif event.key == pygame.K_3:
                            bullets.append(Bullet(3))
                            shoot_delay = 0.4
                            shoot_sound.play()
                        elif event.key == pygame.K_4:
                            bullets.append(Bullet(4))
                            shoot_delay = 0.4
                            shoot_sound.play()
            #Spawning
            spawn_timer -= dt
            notification_timer -= dt
            if notification_timer <= 0:
                notification_timer = 1
                if len(notifications) > 0:
                    notifications.pop(0)
                if len(effects) > 0:
                    effects.pop(0)
            if shoot_delay > 0:
                shoot_delay -= dt
            if spawn_timer <= 0:
                enemies.append(Enemy(random.randint(1, 4)))
                spawn_timer = 10-acceleration
                acceleration += 0.3
                if acceleration > 9:
                    acceleration = 9
        
            #Updating Enemies
            for enemy in enemies[:]:
                enemy.update()
                enemy.draw(screen)
                if enemy.y > 1000:
                    enemies.remove(enemy)
                    player.health -= 1
                    streak = 0
                    lose_hp=pygame.image.load("game_asset/puzzles/2/bg.png").convert_alpha()
                    lose_hp = pygame.transform.scale(lose_hp, (1800, 1080))
                    effects.append(lose_hp)
                    print(f"Player health: {player.health}")

            bullets_to_remove = []
            enemies_to_remove = []
            for bullet in bullets[:]:
                bullet.move(dt)
                for enemy in enemies:
                    if bullet.type == enemy.type:
                        if bullet.rect.colliderect(enemy.rect):
                            bullets_to_remove.append(bullet)
                            enemies_to_remove.append(enemy)
                            notifications.append(["Correct!",(0,255,0),enemy.x,enemy.y])
                            streak += 1
                            score += 1
                            break
                    else:
                        if bullet.rect.colliderect(enemy.rect):
                            bullets_to_remove.append(bullet)
                            notifications.append(["Wrong!",(255,0,0),enemy.x,enemy.y])
                            streak = 0
                            break
            for enemy in enemies_to_remove:
                if enemy in enemies:
                    enemies.remove(enemy)
            for bullet in bullets_to_remove:
                if bullet in bullets:
                    bullets.remove(bullet)

            for bullet in bullets[:]:
                bullet.draw(screen)
            for efect in effects:
                screen.blit(efect, (50, 0))

            player.draw(screen)
            for notification in notifications:
                draw_text(notification[0],base_font,notification[1],notification[2],notification[3])
        
        
            #UI
            draw_text("Streak: "+str(streak),base_font,(255,255,255),250,900)
            draw_text("Score: "+str(score),base_font,(255,255,255),250,850)
            draw_text("Health: "+str(player.health),base_font,(255,255,255),250,800)
            draw_text("Key:",base_font,(255,255,255),250,100)
            draw_text("Integer:1",base_font,(255,255,255),250,150)
            draw_text("Float:2",base_font,(255,255,255),250,200)
            draw_text("String:3",base_font,(255,255,255),250,250)
            draw_text("Boolean:4",base_font,(255,255,255),250,300)
            if score >= 100 and state == "DataType":
                state = "Ending1"
                gameplay_music.stop()
                pygame.mixer.music.load("game_asset/sounds/novelmusic.ogg")
                pygame.mixer.music.play(-1)
            pygame.display.flip()

            # Check win/loss conditions → transition to ending scenes
            if (player.health <= 0 or memories <= 0) and state == "DataType":
                state = "Ending2"
                gameplay_music.stop()
                pygame.mixer.music.load("game_asset/sounds/novelmusic.ogg")
                pygame.mixer.music.play(-1)
            if score >= 200 and state == "DataType":
                state = "Ending1"
                gameplay_music.stop()
                pygame.mixer.music.load("game_asset/sounds/novelmusic.ogg")
                pygame.mixer.music.play(-1)
            pygame.display.flip()

        #Ending 1
        end1_dialogue_idx = 0
        end1_counter = 0
        end1_done = False

        while running and state == "Ending1":
            await asyncio.sleep(0)
            clock.tick(60)
            screen.blit(ending1_bg, (0, 0))

            # Boss expression
            if end1_dialogue_idx in [0, 1, 2]:
                screen.blit(boss_serious, (710, 160))
            elif end1_dialogue_idx in [3, 4, 5, 6, 7]:
                screen.blit(boss_upset, (710, 160))
            elif end1_dialogue_idx in [8, 9, 10, 11]:
                screen.blit(boss_serious, (710, 160))
            else:
                screen.blit(boss_satisfied, (710, 160))

            raw_line = dialogues_ending1[end1_dialogue_idx]
            cleaned = clean_dialogue_line(raw_line, user_name)
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
            if end1_counter < speed * len(cleaned):
                end1_counter += 1
            else:
                end1_done = True
            visible = cleaned[0:end1_counter // speed]
            screen.blit(vs_font.render(visible, True, get_text_color(raw_line)), (box_x + 35, box_y + 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and end1_done:
                    end1_dialogue_idx += 1
                    if end1_dialogue_idx >= len(dialogues_ending1):
                        running = False
                    else:
                        end1_counter = 0
                        end1_done = False

                pygame.display.update()

        #Ending 2
        end2_dialogue_idx = 0
        end2_counter = 0
        end2_done = False

        while running and state == "Ending2":
            await asyncio.sleep(0)
            clock.tick(60)
            screen.blit(ending2_bg, (0, 0))

            # Boss expression
            if end2_dialogue_idx in [0, 1, 2, 3]:
                screen.blit(boss_serious, (710, 160))
            elif end2_dialogue_idx in [4]:
                screen.blit(boss_upset, (710, 160))
            elif end2_dialogue_idx in range(5, 11):
                screen.blit(boss_serious, (710, 160))
            elif end2_dialogue_idx in range(11, 20):
                screen.blit(boss_upset, (710, 160))
            else:
                screen.blit(boss_satisfied, (710, 160))

            raw_line = dialogues_ending2[end2_dialogue_idx]
            cleaned = clean_dialogue_line(raw_line, user_name)
            pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height), 3)
            if end2_counter < speed * len(cleaned):
                end2_counter += 1
            else:
                end2_done = True
            visible = cleaned[0:end2_counter // speed]
            screen.blit(vs_font.render(visible, True, get_text_color(raw_line)), (box_x + 35, box_y + 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and end2_done:
                    end2_dialogue_idx += 1
                    if end2_dialogue_idx >= len(dialogues_ending2):
                        running = False
                    else:
                        end2_counter = 0
                        end2_done = False
            pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
