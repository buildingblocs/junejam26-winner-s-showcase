from __future__ import annotations

import random
from .data import ITEMS, UPGRADES, BLOCKS, Pick


class ItemSystem:
    def __init__(self):
        self.random = random.Random()

    def generate_loser_picks(self) -> list[Pick]:
        categories = ["item", "block", "upgrade"]
        picks: list[Pick] = []
        for category in categories:
            if category == "item":
                item = self.random.choice(ITEMS)
                picks.append(Pick("item", item.name, f"{item.slot.upper()} / {item.flavor}: {item.description}", item))
            elif category == "block":
                block = self.random.choice(BLOCKS)
                picks.append(Pick("block", block.name, block.description, block))
            else:
                upgrade = self.random.choice(UPGRADES)
                picks.append(Pick("upgrade", upgrade.name, upgrade.description, upgrade))
        self.random.shuffle(picks)
        return picks

    def apply_pick(self, pick: Pick, player, player_index: int, block_placer):
        if pick.category == "item":
            player.equip_item(pick.payload)
            return f"{player.name} equipped {pick.name}."
        if pick.category == "upgrade":
            player.apply_upgrade(pick.payload)
            return f"{player.name} gained permanent upgrade {pick.name}."
        if pick.category == "block":
            block_placer.add_block_pick(pick.payload, player_index)
            return f"{player.name} placed permanent arena block {pick.name}."
        return "No pick applied."
