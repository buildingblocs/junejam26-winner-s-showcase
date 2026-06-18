
from __future__ import annotations

import pygame


class RoundManager:
    """
    Continuous game mode.

    - No rounds.
    - No round transitions.
    - No winner screen.
    - When a player loses one life they instantly respawn.
    - When HP reaches 0 they reset back to 3 lives.
    """

    def __init__(
        self,
        players,
        event_spawner,
        block_placer,
    ):

        self.players = players
        self.event_spawner = event_spawner
        self.block_placer = block_placer

        self.round_number = 1

    def start_round(
        self,
        now_ms,
    ):

        self.event_spawner.reset_for_round(
            now_ms,
            self.round_number,
        )

        for player in self.players:

            player.rect.x = player.spawn_x
            player.rect.y = (
                player.rect.height + 520
            )

            player.vel_y = 0
            player.alive = True
            player.control_invert_until = 0
            player.stun_until = 0

    def update(
        self,
        now_ms,
    ):

        for player in self.players:

            # Respawn after losing one life
            if not player.alive:

                if player.hp > 0:

                    player.rect.x = player.spawn_x
                    player.rect.y = (
                        player.rect.height + 520
                    )

                    player.vel_y = 0
                    player.alive = True

                else:

                    # Out of lives

                    player.hp = 3

                    player.rect.x = player.spawn_x
                    player.rect.y = (
                        player.rect.height + 520
                    )

                    player.vel_y = 0
                    player.alive = True

        # Slowly increase event difficulty

        self.round_number = max(
            1,
            now_ms // 30000 + 1,
        )

    def handle_pick_input(
        self,
        event,
        now_ms,
    ):
        # Picks removed
        pass

    def draw_scoreboard(
        self,
        surface,
        font,
        big_font,
    ):
        # No text UI
        pass

    def draw_health(
        self,
        surface,
        font,
    ):
        # Health dots are already drawn
        # above each player.
        pass

    def draw_pick_overlay(
        self,
        surface,
        font,
        big_font,
    ):
        pass

    def draw_match_over(
        self,
        surface,
        big_font,
    ):
        pass
