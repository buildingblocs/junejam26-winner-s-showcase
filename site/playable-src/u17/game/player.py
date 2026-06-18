
from __future__ import annotations

import pygame

from .config import GROUND_Y, PLAYER_SIZE, WHITE
from .data import Stats


class SpriteController:
    def __init__(
        self,
        name: str,
        x: int,
        color: tuple[int, int, int],
        controls: dict[str, int],
    ):
        self.name = name
        self.color = color
        self.controls = controls

        self.base_stats = Stats(
            max_hp=3,
            speed=5,
            jump_power=13,
            gravity=0.65,
            damage_mult=1,
            defense=0,
            fire_rate_mult=1,
            projectile_speed_mult=1,
            extra_jumps=0,
        )

        self.stats = self.base_stats.copy()

        self.spawn_x = x

        self.rect = pygame.Rect(
            x,
            GROUND_Y - PLAYER_SIZE[1],
            *PLAYER_SIZE,
        )

        self.vel_y = 0
        self.facing = 1

        self.jump_held = False
        self.jumps_left = 1

        # 3 lives only
        self.hp = 3
        self.alive = True

        self.control_invert_until = 0
        self.stun_until = 0

    def reset_for_round(self):

        self.rect.x = self.spawn_x
        self.rect.y = GROUND_Y - PLAYER_SIZE[1]

        self.vel_y = 0

        self.alive = True

        self.jumps_left = 1

        self.control_invert_until = 0
        self.stun_until = 0

    def damage(self, amount=1):

        if not self.alive:
            return

        # Lose ONE life immediately
        self.hp -= 1

        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def update(
        self,
        keys,
        blocks,
        now_ms,
    ):

        if not self.alive:
            return

        if now_ms < self.stun_until:
            self._apply_gravity(blocks)
            return

        left = keys[self.controls["left"]]
        right = keys[self.controls["right"]]
        jump = keys[self.controls["jump"]]

        invert = now_ms < self.control_invert_until

        direction = 0

        if left:
            direction -= 1

        if right:
            direction += 1

        if invert:
            direction *= -1

        self.rect.x += int(direction * self.stats.speed)

        if direction != 0:
            self.facing = 1 if direction > 0 else -1

        self._resolve_horizontal(blocks)

        if (
            jump
            and self.jumps_left > 0
            and not self.jump_held
        ):
            self.vel_y = -self.stats.jump_power
            self.jumps_left -= 1

        self.jump_held = jump

        self._apply_gravity(blocks)

    def _apply_gravity(
        self,
        blocks,
    ):

        self.vel_y += self.stats.gravity

        self.rect.y += int(self.vel_y)

        grounded = False

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            grounded = True

        for block in blocks:

            if self.rect.colliderect(block.rect):

                # Landing
                if (
                    self.vel_y > 0
                    and self.rect.bottom - block.rect.top < 28
                ):

                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    grounded = True

                # Hit underside
                elif self.vel_y < 0:

                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

        if grounded:
            self.jumps_left = 1

        self.rect.clamp_ip(
            pygame.Rect(
                40,
                40,
                1020,
                620,
            )
        )

    def _resolve_horizontal(
        self,
        blocks,
    ):

        for block in blocks:

            if self.rect.colliderect(block.rect):

                if self.rect.centerx < block.rect.centerx:
                    self.rect.right = block.rect.left
                else:
                    self.rect.left = block.rect.right

    def draw(
        self,
        surface,
        font,
    ):

        # Draw player as a ball
        pygame.draw.circle(
            surface,
            self.color,
            self.rect.center,
            self.rect.width // 2,
        )

        pygame.draw.circle(
            surface,
            WHITE,
            self.rect.center,
            self.rect.width // 2,
            2,
        )

        # Draw 3 life dots above player
        radius = 5

        for i in range(3):

            if i < self.hp:
                color = (0, 255, 0)
            else:
                color = (70, 70, 70)

            pygame.draw.circle(
                surface,
                color,
                (
                    self.rect.centerx - 15 + i * 15,
                    self.rect.y - 15,
                ),
                radius,
            )