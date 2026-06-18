
import asyncio

import pygame

from game.config import (
    WIDTH,
    HEIGHT,
    FPS,
    ARENA_RECT,
    GROUND_Y,
    BLACK,
    WHITE,
    GRAY,
    DARK,
    CYAN,
    MAGENTA,
)

from game.player import SpriteController
from game.blocks import BlockPlacer
from game.events import EventSpawner
from game.rounds import RoundManager


def draw_arena(screen):

    screen.fill(BLACK)

    # Arena background
    pygame.draw.rect(
        screen,
        DARK,
        pygame.Rect(*ARENA_RECT),
        border_radius=12,
    )

    pygame.draw.rect(
        screen,
        GRAY,
        pygame.Rect(*ARENA_RECT),
        3,
        border_radius=12,
    )

    # Thick floor
    pygame.draw.rect(
        screen,
        (80, 80, 80),
        (
            0,
            GROUND_Y,
            WIDTH,
            12,
        ),
    )


async def main():

    pygame.init()

    pygame.display.set_caption(
        "Cyber Chick Horse"
    )

    screen = pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT,
        )
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "consolas",
        18,
    )

    big_font = pygame.font.SysFont(
        "consolas",
        28,
        bold=True,
    )


    try:

        pygame.mixer.init()

        pygame.mixer.music.load(
            "sounds/ambient.ogg"
        )

        pygame.mixer.music.set_volume(
            0.4
        )

        pygame.mixer.music.play(-1)

    except:

        print(
            "No ambient music found."
        )

   

    p1_controls = {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
    }

    p2_controls = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
    }

    players = [

        SpriteController(
            "P1",
            180,
            CYAN,
            p1_controls,
        ),

        SpriteController(
            "P2",
            860,
            MAGENTA,
            p2_controls,
        ),

    ]

    block_placer = BlockPlacer()

    event_spawner = EventSpawner()

    rounds = RoundManager(
        players,
        event_spawner,
        block_placer,
    )

    rounds.start_round(
        pygame.time.get_ticks()
    )

    running = True

    while running:

        now_ms = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                running = False

            if event.type == pygame.KEYDOWN:

                # Player 1 places block

                if event.key == pygame.K_e:

                    block_placer.place_block(
                        players[0]
                    )

                # Player 2 places block

                if event.key == pygame.K_RSHIFT:

                    block_placer.place_block(
                        players[1]
                    )


        for player in players:

            player.update(
                keys,
                block_placer.blocks,
                now_ms,
            )

        event_spawner.update(
            players,
            block_placer.blocks,
            now_ms,
            rounds.round_number,
        )

        rounds.update(
            now_ms,
        )



        draw_arena(screen)

        block_placer.draw(
            screen,
            font,
        )

        event_spawner.draw(
            screen,
            font,
            now_ms,
        )

        for player in players:

            player.draw(
                screen,
                font,
            )

        pygame.display.flip()

        clock.tick(FPS)

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
