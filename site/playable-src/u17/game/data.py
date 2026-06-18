from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Stats:
    max_hp: int = 0
    speed: float = 0.0
    jump_power: float = 0.0
    gravity: float = 0.0
    damage_mult: float = 0.0
    defense: float = 0.0
    fire_rate_mult: float = 0.0
    projectile_speed_mult: float = 0.0
    extra_jumps: int = 0

    def copy(self) -> "Stats":
        return Stats(**self.__dict__)


@dataclass
class Weapon:
    name: str
    damage: int
    cooldown_ms: int
    projectile_speed: float
    color: tuple[int, int, int]
    description: str


@dataclass
class Item:
    name: str
    slot: str
    flavor: str
    description: str
    stat_mod: Stats = field(default_factory=Stats)
    weapon: Optional[Weapon] = None


@dataclass
class Upgrade:
    name: str
    description: str
    stat_mod: Stats


@dataclass
class BlockType:
    name: str
    color: tuple[int, int, int]
    hp: int
    description: str


@dataclass
class Pick:
    category: str
    name: str
    description: str
    payload: object


DEFAULT_WEAPON = Weapon(
    "Packet Pistol",
    damage=10,
    cooldown_ms=430,
    projectile_speed=8.5,
    color=(0, 230, 255),
    description="Reliable neutral starter weapon."
)

WEAPONS = [
    DEFAULT_WEAPON,
    Weapon("Syntax Shotgun", 8, 720, 7.0, (255, 225, 80), "Heavy burst-style close pressure."),
    Weapon("Exploit Rail", 18, 850, 12.5, (255, 70, 90), "Slow-firing offensive rail packet."),
    Weapon("Firewall Wand", 7, 310, 8.0, (70, 255, 120), "Defensive rapid low-damage bolts."),
]

ITEMS = [
    Item("Python Hoodie", "body", "neutral/programming", "+15 max HP and a clean async vibe.", Stats(max_hp=15)),
    Item("Bug Boots", "boots", "neutral/programming", "+1 extra jump for chaotic dodges.", Stats(extra_jumps=1)),
    Item("Overclock Chip", "util", "offensive", "+20% fire rate, -5 effective HP tradeoff.", Stats(max_hp=-5, fire_rate_mult=1.2)),
    Item("DDoS Gloves", "weapon", "offensive", "Equip the Exploit Rail.", weapon=WEAPONS[2]),
    Item("Firewall Vest", "body", "defensive", "+18 HP and +10% damage reduction.", Stats(max_hp=18, defense=0.10)),
    Item("Safe Mode Boots", "boots", "defensive", "+15% speed and +5% defense.", Stats(speed=0.65, defense=0.05)),
    Item("Syntax Shotgun", "weapon", "offensive", "Equip the Syntax Shotgun.", weapon=WEAPONS[1]),
    Item("Firewall Wand", "weapon", "defensive", "Equip the Firewall Wand.", weapon=WEAPONS[3]),
    Item("Debugger Drone", "util", "neutral/programming", "+8 HP, +10% projectile speed.", Stats(max_hp=8, projectile_speed_mult=1.1)),
]

UPGRADES = [
    Upgrade("Patch Notes", "+12 permanent max HP.", Stats(max_hp=12)),
    Upgrade("Fiber Optics", "+0.55 permanent movement speed.", Stats(speed=0.55)),
    Upgrade("Hot Reload", "+10% permanent fire rate.", Stats(fire_rate_mult=1.1)),
    Upgrade("Sharper Packets", "+12% permanent damage.", Stats(damage_mult=0.12)),
    Upgrade("Sandbox Armor", "+8% permanent defense.", Stats(defense=0.08)),
    Upgrade("Rocket Legs", "+1.2 permanent jump power.", Stats(jump_power=1.2)),
]

BLOCKS = [
    BlockType("Code Wall", (80, 130, 255), 999, "Permanent hard cover."),
    BlockType("Glitch Brick", (165, 90, 255), 140, "Breakable purple cover."),
    BlockType("Firewall Block", (255, 95, 35), 999, "Hot cover that shapes dangerous lanes."),
    BlockType("Bounce Pad", (70, 255, 120), 999, "Jump boost platform."),
]
