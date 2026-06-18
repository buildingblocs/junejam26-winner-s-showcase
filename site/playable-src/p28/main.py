# pylint: disable=no-member
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
#pylint: disable=invalid-name
#pylint: disable=pointless-string-statement
#pylint: disable=line-too-long
#pylint: disable=unreachable
#pylint: disable=undefined-loop-variable
import asyncio
import pygame
pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Eraser Buddy")
clock = pygame.time.Clock()
current_scene = "main_menu"




def draw_classroom():
    classroom_surface = pygame.image.load("assets/classroom.jpg").convert_alpha()
    classroom_surface = pygame.transform.scale(classroom_surface, (800, 600))
    screen.blit(classroom_surface, (0, 0))

#So text isn't on a single line
def draw_wrapped_text(surface, text, fonts, color, x, y, max_width):
    words = text.split(" ")
    line = ""
    line_y = y

    for word in words:
        test_line = line + word + " "
        if fonts.size(test_line)[0] > max_width:
            text_surfaces = fonts.render(line, True, color)
            surface.blit(text_surfaces, (x, line_y))
            line = word + " "
            line_y += fonts.get_linesize()

        else:
            line = test_line

    text_surfaces = fonts.render(line, True, color)
    surface.blit(text_surfaces, (x, line_y))

#game variables
game_paused = False
key_pressed = False


# pictures
main_menu_surface = pygame.image.load("assets/roomblur.png").convert_alpha()
main_menu_surface = pygame.transform.scale(main_menu_surface, (800, 600))

#textbox image
textbox_image = pygame.image.load("assets/textbox.png").convert_alpha()
textbox_image = pygame.transform.scale(textbox_image, (600, 130))

#button
button_image = pygame.image.load("assets/button.png").convert_alpha()
button_image = pygame.transform.scale(button_image, (400, 130))




# Player name input variables
font_textbox = pygame.font.Font(None, 40)
player_name = ""
textbox_active = True

#fonts
textbox_font = pygame.font.SysFont("Arialblack", 18)
name_font = pygame.font.SysFont("Arialblack", 30)
font = pygame.font.SysFont("Arialblack", 60)
text_surface = font.render("Eraser Buddy", True, ('black'))


#diaglogue box variables
dialogue_index = 0
text_index = 0

#dialogue images
dialogue_images = {
    "assets/eraser.png": pygame.transform.scale(
        pygame.image.load("assets/eraser.png").convert_alpha(), (300, 300)
    ),
    "assets/eraserface.png": pygame.transform.scale(
        pygame.image.load("assets/eraserface.png").convert_alpha(), (300, 300)
    ),
    "assets/rng.png": pygame.transform.scale(
        pygame.image.load("assets/rng.png").convert_alpha(), (300, 300)
    ),
        "assets/wink.png": pygame.transform.scale(
        pygame.image.load("assets/wink.png").convert_alpha(), (300, 300)
    ),


}

#dialogue box
N = {"name": "Narrator"}
E = {"name": "Eraser"}
A = {"name": "Ashley"}
P = {"name": "Me"}

dialogue_list = [
    #day 1
    {"day": 1, **P, "text": "Another boring day at school...Mr Lim's voice is always so monotone, I can barely stay awake."},
    {"day": 1, **P, "text": "Ashley got to skip because of her overseas trip....eugh luckyy"},
    {"day": 1, **P, "text": "What a ditcher, leaving me table partnerless for the week."},
    {"day": 1, **P, "text": "I wish I could go home. At least this is the last lesson today but its going so slowly without anyone to talk to…"},
    {"day": 1, **N, "text": "You try and focus on the lesson and fighting the urge to close your eyes and fall asleep."},
    {"day": 1, **N, "text": "It's a losing battle."},
    {"day": 1, **N, "text": "But then a small rustling sound juts you awake."},
    {"day": 1, **N, "text": "You turn your head around and try to find the source of the sound but its gone."},
    {"day": 1, **P, "text": "Am I so bored that I'm going crazy…? At least lessons ending soon, I really want to go home…"},
    {"day": 1, **N, "text": "Suddenly you hear the sound again, this time, the rustling seems to be getting louder."},
    {"day": 1, **N, "text": "You try to pin point the sound of the noise and it seems to be coming from your… pencilcase???"},
    {"day": 1, **N, "text": "You unzip it and something pours out, you take a while to register what it is and you realise its your eraser??"},
    {"day": 1, **E, "text": "Hahhh… finally free, I was wondering when you were going to let me out, its so dark and stuffy in there","image": "assets/eraser.png"},
    {"day": 1, **P, "text": "WHAT!!! YOU CAN TALK?? ","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "You can't believe your ears or eyes as you watch your eraser, start jumping up and down. ","image": "assets/eraser.png"},
    {"day": 1, **E, "text": "Duh! I could always talk, {player_name}!","image": "assets/eraser.png"},
    {"day": 1, **P, "text": "You could?? Why have you never spoken before…and…wait. YOU KNOW MY NAME?","image": "assets/eraser.png"},
    {"day": 1, **E, "text": "??? Isn't it obvious, I've heard everyone call you that since forever...I have ears you know.","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "'…..no you don't.' You say, looking at the eraser in disbelief.","image": "assets/eraser.png"},
    {"day": 1, **E, "text": "You wouldn't get it.","image": "assets/eraser.png"},
    {"day": 1, **P, "text": "???? What is that supposed to —","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "Before you finish, a loud ringing noise echos throughout the class. It's the school bell. You're free.","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "You immediately get overcome by a sense of joy and start packing your stuff.","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "Your worksheets, your notebooks and of course your pencil case.","image": "assets/eraser.png"},
    {"day": 1, **E, "text": "HEY! WHAT ARE U DOING DONT PUT ME BACK IN! I STILL WANT TO TALK!","image": "assets/eraser.png"},
    {"day": 1, **P, "text": "We can do that at home, relax. Let's get out of here!!!","image": "assets/eraser.png"},
    {"day": 1, **E, "text": "NOO WE CA--","image": "assets/eraser.png"},
    {"day": 1, **N, "text": "You stuff your pencil case and its noisy contents inside your bag and rush out the school gates."},

    #day 2
    {"day": 2, **N, "text": "Arriving home, you rush into your room and crash onto bed."},
    {"day": 2, **N, "text": "You almost fall asleep before you remember your new friend."},
    {"day": 2, **N, "text": "You rush over and open up your bag expecting angry gripes directed at you but all you hear is silence…."},
    {"day": 2, **N, "text": "You probe and poke your eraser, thinking its trying to get revenge."},
    {"day": 2, **N, "text": "But after minutes of silence, you start to wonder if you were going crazy."},
    {"day": 2, **N, "text": "You head back to bed more confused than ever."},
    {"day": 2, **N, "text": "Back at your desk, your barely following Ms Tan's lecture on mirco-organisms…or was it mitosis???"},
    {"day": 2, **N, "text": "Anyway, your mind is definitely more preoccupied thinking of yesterday's events."},
    {"day": 2, **N, "text": "After a while, a familiar rustling sound snaps you out of your thoughts."},
    {"day": 2, **N, "text": "And sure enough, the noise is coming from your pencil case."},
    {"day": 2, **E, "text": "HEY WHY'D YOU CUT ME OFF YESTERDAY","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Well, I'm sorry alright?? But at least I didn't play dead the whole of yesterday.","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "I was starting to think you were a hallucination…","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "HEY! Its not my fault, I tried to warn you and you cut me off!","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "I'm still new to this talking thing.","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "I thought you said you could 'Always talk' yesterday…","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "That's different okay! Just because I could talk doesn't mean that I did","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Well okay fine. But why can you only talk to me in school??","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "Uhm..I'm not sure either…","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "........","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "You're useless…","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "You are so rude!","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Well it's true, you haven't told me anything so far! ","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Like how can you talk??? Can all erasers talk like you?? And…and do you have a name???","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "Woww....you expect me to answer after you insulted me??","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "I'm not tell you ANYTHING!","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Come on! Not even your name??","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "Nope!!","image": "assets/eraser.png"},
    {"day": 2, **P, "text": " Fine then..I'll name you myself!","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "I'm going to choose something lame..like..like......","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "ERASER!!","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "..that's insulting on so many levels...","image": "assets/eraser.png"},
    {"day": 2, **P, "text": "Well you deserve it.","image": "assets/eraser.png"},
    {"day": 2, **E, "text": "HEY???","image": "assets/eraser.png"},
    {"day": 2, **N, "text": "You bicker with your eraser for the rest of the day without end."},
    {"day": 2, **N, "text": "In an act of pettiness, you leave your eraser in class and go home."},

    #day 3
    {"day": 3, **N, "text": "The second you sit at your desk, you're met with a pitiful sight."},
    {"day": 3, **N, "text": "Your eraser seems to be shaking, but you're not sure if its actually sad or trying to guilt trip you","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "Nonetheless, you do feel guilty for abandoning your new friend yesterday.","image": "assets/eraser.png"},
    {"day": 3, **P, "text": "Listen…I'm sorry for leaving you here, I was annoyed at the time but what I did was still wrong.","image": "assets/eraser.png"},
    {"day": 3, **E, "text": ".…mmmmm","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "Eraser appears to be receptive of your apology, as it slowly stills and seemingly calm down. ","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "Well, at least you think so?","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "You don't exactly know how to read eraser body language. It doesn't even have a face.","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "An idea pops up in your head at that moment.","image": "assets/eraser.png"},
    {"day": 3, **P, "text": "Hey, we've been talking for two days now and it feels kinda weird that I'm talking to a blank eraser","image": "assets/eraser.png"},
    {"day": 3, **E, "text": "Wow…insulting me again after apologising??","image": "assets/eraser.png"},
    {"day": 3, **P, "text": "That's not what I meant! What I'm trying to say is…do you want me to give you a face??","image": "assets/eraser.png"},
    {"day": 3, **E, "text": " ??? You want to...give me a face??","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "'Yea, I'll draw one for you.' You say as you lift your pencil up.","image": "assets/eraser.png"},
    {"day": 3, **E, "text": "WHATT!!? NO NOT WITH THAT ITS SO SHARP YOU'RE GOING TO HURT ME!!","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "You flinch at the loud scream your eraser lets out.","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "Ahh! I'm sorry I didn't realise….hold on….","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "You dig through your pencil case for something else and come across your pen.","image": "assets/eraser.png"},
    {"day": 3, **P, "text": "Well, how about this? The tip is rounded and the ink's darker so I won't have to press as hard.","image": "assets/eraser.png"},
    {"day": 3, **E, "text": "Eraser goes silent for a second, seemingly studying the tip of the pen.","image": "assets/eraser.png"},
    {"day": 3, **E, "text": "Okay fine but be gentle, I don't want to get scratched….","image": "assets/eraser.png"},
    {"day": 3, **N, "text": "You concentrate and slowly draw your masterpiece, adjusting to the protests that come out when you accidentally press too hard.","image": "assets/eraser.png"},
    {"day": 3, **P, "text": "There done! You look great! Much cuter now.","image": "assets/eraserface.png"},
    {"day": 3, **E, "text": "Thanks…but I can't see it so I'm just have to trust you.","image": "assets/eraserface.png"},
    {"day": 3, **P, "text": "Oh wait I can take out my phone and show you.","image": "assets/eraserface.png"},
    {"day": 3, **E, "text": "No. I meant I literally cannot see. I am an eraser. We don't have eyes.","image": "assets/eraserface.png"},
    {"day": 3, **P, "text": "But…didn't you say you have ears….why don't you have eyes too??","image": "assets/eraserface.png"},
    {"day": 3, **E, "text": "Typical human, doesn't know eraser anatomy.","image": "assets/eraserface.png"},
    {"day": 3, **P, "text": " Who does??","image": "assets/eraserface.png"},
    {"day": 3, **E, "text": "Eugh.... so ignorant.","image": "assets/eraserface.png"},
    {"day": 3, **P, "text": "Fine then, tell me how eraser anatomy works?","image": "assets/eraserface.png"},
    {"day": 3, **N, "text": "Eraser jumps up, seemingly shocked to hear that from you.","image": "assets/eraserface.png"},
    {"day": 3, **E, "text": "You…you really want to know???","image": "assets/eraserface.png"},
    {"day": 3, **N, "text": "You nod and are suddenly hours into a lecture by a surprisingly enthusiastic teacher"},
    {"day": 3, **N, "text": "Although you can barely wrap your head around anything, with eraser biology seemingly contradicting every accepted biological theory,"},
    {"day": 3, **N, "text": "You have fun more fun than you've ever had learning and spend the rest of the day asking questions"},
    {"day": 3, **N, "text": "In the end, you go home with a brain full of knowledge"},

    #day 4
    {"day": 4, **N, "text": "Coming back to school today, you feel as if your bond with your eraser has gotten stronger."},
    {"day": 4, **N, "text": "Which is a weird statement but a truthful one nonetheless."},
    {"day": 4, **N, "text": "You walk into class and sit on your desk with a smile on your face."},
    {"day": 4, **N, "text": "You take out your pencil case from your bag and continue where yesterdays conversation left off."},
    {"day": 4, **N, "text": "Lessons go by quickly, until chemistry class and Mr Ang walks in holding a suspicious pile of worksheets."},
    {"day": 4, **N, "text": "...Its a pop quiz. And you haven't touched the textbook the whole year."},
    {"day": 4, **N, "text": "You're cooked."},
    {"day": 4, **N, "text": "On the bright side, its all MCQ."},
    {"day": 4, **N, "text": "On the not so bright side, you can barely understand any of them."},
    {"day": 4, **N, "text": "You struggle to finish each question, constantly writting and cancelling"},
    {"day": 4, **E, "text": "Are you almost done?? I've been waiting quietly for ages.","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "Nope...barely started..I don't understand anything...","image": "assets/eraserface.png"},
    {"day": 4, **N, "text": "You look up from your quiz and notice eraser with its face turned towards you.","image": "assets/eraserface.png"},
    {"day": 4, **N, "text": "Even though yesterdays extensive anatomy lesson taught you erasers don't have eyes, You still feel as though you are being judged for your incompetence","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "Wait…a minute…","image": "assets/eraserface.png"},
    {"day": 4, **N, "text": "You feel as though you've found a cheatsheet","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "Hey. you know how you have ears??","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "Have you been listening during chemistry??","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "I need help. Help me.","image": "assets/eraserface.png"},
    {"day": 4, **N, "text": "Eraser's face doesn't change ( it physically can't ) but you feel it's disappointment ","image": "assets/eraserface.png"},
    {"day": 4, **E, "text": "Yea I have, unlike a certain someone but I'm not helping you.","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "YES! Wait...what. Come on aren't we friends I need this…","image": "assets/eraserface.png"},
    {"day": 4, **E, "text": " I have morals.","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "Please...","image": "assets/eraserface.png"},
    {"day": 4, **E, "text": "Nope, figure it out yourself. Guess or something","image": "assets/eraserface.png"},
    {"day": 4, **P, "text": "….Guess…? Oh my god eraser I have an idea.","image": "assets/eraserface.png"},
    {"day": 4, **E, "text": "What??? HEYY—","image": "assets/eraserface.png"},
    {"day": 4, **N, "text": "With a pen in one hand and your very confused eraser in the other, you begin drawing."},
    {"day": 4, **N, "text": "Starting with one face, two…three…four…and done!"},
    {"day": 4, **N, "text": "You put eraser down and inspect your genius","image": "assets/rng.png"},
    {"day": 4, **E, "text": "Are you kidding. You're really going to use me to gamble on your questions","image": "assets/rng.png"},
    {"day": 4, **E, "text": "….","image": "assets/rng.png"},
    {"day": 4, **E, "text": "Fine but you better not throw too hard, now quick you barely have anymore time.","image": "assets/rng.png"},
    {"day": 4, **N, "text": "With that reminder, you pick up eraser and start rolling.","image": "assets/rng.png"},
    {"day": 4, **N, "text": "In the end, you manage to answer the last question just as Mr Ang starts collecting the papers."},
    {"day": 4, **N, "text": "Even though your most definitely not going to pass with flying colours, that was the most fun you had taking a quiz ever. "},

    #day 5
    {"day": 5, **N, "text": "As you walk into class that day, you notice someone occupying the seat next to yours."},
    {"day": 5, **P, "text": "ASHLEYYYYYYY OH MY GOD YOU'RE BACKKK!!!"},
    {"day": 5, **N, "text": "you run over and give your table partner a hug."},
    {"day": 5, **A, "text": "I AMMM!! How was school without me?? "},
    {"day": 5, **A, "text": "Was it boring?? I bet you fell asleep multiple times."},
    {"day": 5, **N, "text": "You feign offense and were about to refute Ashley's slander of your school work ethic when you were reminded of your new friend."},
    {"day": 5, **P, "text": "Actually, school was really fun. I met a new friend that kept me awake."},
    {"day": 5, **A, "text": "Actually?? Who??"},
    {"day": 5, **P, "text": "Not a who. A what. Wait you're not going to believe this let me show you."},
    {"day": 5, **N, "text": "As you slowly get eraser out of your bag, you describe the past week's event."},
    {"day": 5, **N, "text": "As you go on, Ashley's face morphs into a look of half amusement and half disbelief, probably thinking you went crazy while she was gone."},
    {"day": 5, **N, "text": "'And here's ERASER' you say as you take it out of your pencil case","image": "assets/rng.png"},
    {"day": 5, **N, "text": "You expect eraser to start jabbering on about finally talking to someone new or complaining that the pencil case was too stuffy.","image": "assets/rng.png"},
    {"day": 5, **N, "text": "However, all your met with is silence.","image": "assets/rng.png"},
    {"day": 5, **N, "text": "Ashley looks at you funny.","image": "assets/rng.png"},
    {"day": 5, **A, "text": "Uhmm…so is 'eraser' going to start talking anytime soon???","image": "assets/rng.png"},
    {"day": 5, **N, "text": "Uh…y-yea let me just wake them up...","image": "assets/rng.png"},
    {"day": 5, **N, "text": "You try everything. Poking, yelling and even threatening it with your sharpened pencil in hopes it would react.","image": "assets/rng.png"},
    {"day": 5, **N, "text": "But you're met with complete silence. No movement. No nothing.","image": "assets/rng.png"},
    {"day": 5, **N, "text": "As the minutes pass by like this you feel embarrassment welling up inside you."},
    {"day": 5, **N, "text": "You don't have to fake a whole story about a talking eraser..you even drew it a face."},
    {"day": 5, **N, "text": "It was NOT fake. Everything I told you was real. It did talk to me, it can hear everything we're saying—"},
    {"day": 5, **N, "text": "You ramble on about the eraser anatomy you learnt from eraser, trying to prove you weren't lying."},
    {"day": 5, **N, "text": "However the more you go on the more you feel Ashley looking at you with pity. Eventually she cuts you off."},
    {"day": 5, **A, "text": "Okay that's enough, fine I'll believe you okay. Come on sit down, I have so much stuff to update you about —-"},
    {"day": 5, **N, "text": "School continues like it normally would with Ashley, fun and easy, however not without you wondering if everything that happened was even real."},
    {"day": 5, **N, "text": "But although the school ended on a good note, with the two of you planning to go out for lunch, you can't help but feel heavy at the loss of your new friend."},
    {"day": 5, **N, "text": "As you pack your bag you give your eraser one last look before stuffing in into your pencil case.","image": "assets/rng.png"},
    {"day": 5, **N, "text": ".........","image": "assets/wink.png"},
    {"day": 5, **N, "text": ".........","image": "assets/rng.png"},

    ]


async def main():
    global current_scene, player_name, textbox_active
    global dialogue_index, text_index, key_pressed

    running = True
    while running:
        current = dialogue_list[dialogue_index]
        full_text = current["text"].replace("{player_name}", player_name)

        advanced = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            if  event.type == pygame.MOUSEBUTTONDOWN:
                if button_image.get_rect(topleft=(200, 340)).collidepoint(event.pos):
                    current_scene = "classroom"

            if event.type == pygame.KEYDOWN and textbox_active:

                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]

                elif event.key == pygame.K_RETURN:
                    textbox_active = False
                    print("Name entered:", player_name)

                else:
                    player_name += event.unicode

            if current_scene == 'classroom':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT and not key_pressed:
                        key_pressed = True
                        if int(text_index) < len(full_text):
                            # skip to full text
                            text_index = len(full_text)
                        else:
                            # advance to next dialogue

                            dialogue_index += 1
                            text_index = 0
                            advanced = True

                            if dialogue_index >= len(dialogue_list):
                                running = False

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT:
                        key_pressed = False

        if advanced:
            await asyncio.sleep(0)
            clock.tick(60)
            continue

        if current_scene == 'main_menu':
            screen.blit(main_menu_surface, (0, 0))
            screen.blit(text_surface, (180, 100))
            screen.blit(button_image, (200, 340))
            screen.blit(textbox_image, (100, 220))
            text_box = font_textbox.render(player_name, True, ('black'))
            screen.blit(text_box, (170, 270))


        elif current_scene == 'classroom':
            draw_classroom()
            current_image_key = current.get("image")
            if current_image_key and current_image_key in dialogue_images:
                img = dialogue_images[current_image_key]
                screen.blit(img, (250, 150))

        # text animation
            if text_index < len(full_text):
                text_index += 0.5

            displayed_text = full_text[:int(text_index)]




            # Dialogue box background
            pygame.draw.rect(screen, (29, 65, 50), (30, 450, 740, 130))
            pygame.draw.rect(screen, ('white'), (30, 450, 740, 130), 2)

            # Character name box
            pygame.draw.rect(screen, (29, 57, 46), (30, 415, 200, 40))
            pygame.draw.rect(screen, ('white'), (30, 415, 200, 40), 2)

            # Character name
            name_surface = name_font.render(current["name"], True, ('white'))
            screen.blit(name_surface, (40, 413))

            # Dialogue text
            draw_wrapped_text(screen, displayed_text, textbox_font, ('white'), 50, 465, 700)

            # indicator when text is fully shown
            if int(text_index) >= len(full_text):
                indicator = textbox_font.render("▶ click to continue", True, ('white'))
                screen.blit(indicator, (570, 550))

        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
