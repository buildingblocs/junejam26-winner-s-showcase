
from __future__ import annotations

import pygame

from .config import BLOCK_SIZE, WHITE


class ArenaBlock:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(
            x,
            y,
            BLOCK_SIZE,
            BLOCK_SIZE,
        )

        self.hp = 100
        self.alive = True

    def hit(self, damage: float):
        self.hp -= damage

        if self.hp <= 0:
            self.alive = False

    def draw(self, surface, font):

        pygame.draw.rect(
            surface,
            (100, 100, 100),
            self.rect,
            border_radius=6,
        )

        pygame.draw.rect(
            surface,
            WHITE,
            self.rect,
            2,
            border_radius=6,
        )


class BlockPlacer:
    def __init__(self):
        self.blocks = []

    def place_block(self, player):

        # Spawn one block in front of player
        offset = BLOCK_SIZE + 20

        x = player.rect.centerx + player.facing * offset
        y = player.rect.centery

        # Snap to grid
        x = round(x / BLOCK_SIZE) * BLOCK_SIZE
        y = round(y / BLOCK_SIZE) * BLOCK_SIZE

        new_rect = pygame.Rect(
            x,
            y,
            BLOCK_SIZE,
            BLOCK_SIZE,
        )

        # Prevent overlapping blocks
        for block in self.blocks:
            if block.rect.colliderect(new_rect):
                return

        self.blocks.append(
            ArenaBlock(
                int(x),
                int(y),
            )
        )

    def clear(self):
        self.blocks.clear()

    def update(self):

        self.blocks = [
            block
            for block in self.blocks
            if block.alive
        ]

    def draw(self, surface, font):

        self.update()

        for block in self.blocks:
            block.draw(surface, font)