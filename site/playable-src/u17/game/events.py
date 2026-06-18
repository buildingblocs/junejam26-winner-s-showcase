
from __future__ import annotations

import random
import pygame

from .config import RED, YELLOW


class Particle:
    def __init__(self, x, y):

        self.x = x
        self.y = y

        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

        self.life = random.randint(15, 35)
        self.size = random.randint(2, 5)

    def update(self):

        self.x += self.vx
        self.y += self.vy

        self.life -= 1

        return self.life > 0

    def draw(self, surface):

        pygame.draw.circle(
            surface,
            (255, 80, 80),
            (int(self.x), int(self.y)),
            self.size,
        )


class Hazard:
    def __init__(
        self,
        rect,
        damage,
        color,
        lifetime_ms,
        created_ms,
        label,
        falling=False,
        speed=8,
    ):

        self.rect = rect
        self.damage = damage
        self.color = color

        self.expires = created_ms + lifetime_ms

        self.label = label

        self.falling = falling
        self.speed = speed

        self.triggered = set()

        self.particles = []

    def update(
        self,
        players,
        now_ms,
    ):

        if self.falling:
            self.rect.y += self.speed

            # Spawn particles
            for _ in range(3):

                self.particles.append(
                    Particle(
                        self.rect.centerx,
                        self.rect.centery,
                    )
                )

        self.particles = [
            p
            for p in self.particles
            if p.update()
        ]

        if now_ms >= self.expires:
            return False

        for player in players:

            if (
                player.alive
                and player not in self.triggered
                and self.rect.colliderect(player.rect)
            ):

                player.damage()

                self.triggered.add(player)

        return True

    def draw(
        self,
        surface,
        font,
    ):

        for particle in self.particles:
            particle.draw(surface)

        pygame.draw.circle(
            surface,
            self.color,
            self.rect.center,
            self.rect.width // 2,
        )

        pygame.draw.circle(
            surface,
            (255, 255, 255),
            self.rect.center,
            self.rect.width // 2,
            2,
        )


class EventSpawner:
    def __init__(self):

        self.hazards = []

        self.random = random.Random()

        self.next_event_ms = 5000

        self.round_start_ms = 0

        self.message = ""
        self.message_until = 0

    def reset_for_round(
        self,
        now_ms,
        round_number,
    ):

        self.hazards.clear()

        self.round_start_ms = now_ms

        self.next_event_ms = now_ms + 5000

    def get_spawn_count(
        self,
        elapsed,
    ):

        if elapsed < 30:
            return 1

        elif elapsed < 45:
            return self.random.randint(1, 2)

        elif elapsed < 55:
            return 2

        elif elapsed < 60:
            return self.random.randint(2, 3)

        elif elapsed < 65:
            return 3

        return 4 + int((elapsed - 65) / 5)

    def update(
        self,
        players,
        blocks,
        now_ms,
        round_number,
    ):

        self.hazards = [
            h
            for h in self.hazards
            if h.update(
                players,
                now_ms,
            )
        ]

        if now_ms >= self.next_event_ms:

            elapsed = (
                now_ms - self.round_start_ms
            ) / 1000

            count = self.get_spawn_count(
                elapsed
            )

            for _ in range(count):

                self.spawn_malware(
                    now_ms,
                    round_number,
                )

            self.next_event_ms += 5000

    def spawn_malware(
        self,
        now_ms,
        round_number,
    ):

        size = 60 + round_number * 4

        x = self.random.randint(
            60,
            1000,
        )

        self.hazards.append(

            Hazard(

                pygame.Rect(
                    x,
                    -80,
                    size,
                    size,
                ),

                1,

                RED,

                12000,

                now_ms,

                "MALWARE",

                falling=True,

                speed=6 + round_number,
            )

        )

    def draw(
        self,
        surface,
        font,
        now_ms,
    ):

        for hazard in self.hazards:

            hazard.draw(
                surface,
                font,
            )

        if now_ms < self.message_until:

            text = font.render(
                self.message,
                True,
                YELLOW,
            )

            surface.blit(
                text,
                (
                    550
                    - text.get_width() // 2,
                    40,
                ),
            )
