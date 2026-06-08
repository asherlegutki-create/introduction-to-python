"""
ashenmoor.world.mob
───────────────────
Mob — a non-player character controlled by the game engine.
"""

from __future__ import annotations
import random
import re

from ..core.character import Character


def _roll(dice_str: str) -> int:
    m = re.fullmatch(r"(\d+)d(\d+)([+-]\d+)?", dice_str.strip())
    if not m:
        return 1
    n, s = int(m.group(1)), int(m.group(2))
    bonus = int(m.group(3)) if m.group(3) else 0
    return sum(random.randint(1, s) for _ in range(n)) + bonus


def _resolve_hp(template: dict) -> int:
    level = max(1, int(template.get("level", 1)))
    return level * 8 * 5


class Mob(Character):

    def __init__(self, template: dict, races: dict | None = None) -> None:
        hp_val = _resolve_hp(template)

        if races is None:
            from ..core.race import RACES as _default_races
            races = _default_races

        raw_race  = template.get("race", "Human")
        safe_race = raw_race if raw_race in races else "Human"

        from ..dnd.abilities import CLASS_SAVE_PROFS
        raw_class  = template.get("cclass", template.get("class", "Fighter"))
        safe_class = raw_class if raw_class.lower() in CLASS_SAVE_PROFS else "Fighter"

        char_dict: dict = {
            "name":      template.get("name",      "something"),
            "race":      safe_race,
            "class":     safe_class,
            "level":     template.get("level",      1),
            "stats":     list(template.get("stats", [75] * 6)),
            "max_hp":    hp_val,
            "hp":        hp_val,
            "alignment": template.get("alignment",  0),
            "position":  template.get("position",   "standing"),
        }
        super().__init__(char_dict, races=races)

        self.room_description: str = template.get(
            "room_description",
            template.get("room_desc", f"{self.name} is here.")
        )
        self.key_words: tuple = tuple(template.get("key_words", ()))
        desc = template.get("description", "")
        self.description: str = "\n".join(desc) if isinstance(desc, (tuple, list)) else desc

        if "ac" in template:
            self.ac: int = int(template["ac"])

        self.damage_dice: str  = template.get("damage_dice", "1d4+0")
        self.hit_dice:    str  = template.get("hit_dice",    "1d6+0")
        self.coins:       dict = dict(template.get("coins", {}))

        self.aggressive: bool     = template.get("aggro", template.get("aggressive", False))
        self.memory:     set[str] = set()
        self.perception_prof: bool = template.get("perception_prof", False)
        self.killable:   bool      = template.get("killable",   True)
        self.has_dialog: bool      = template.get("has_dialog", False)

        self._template: dict = template

        self.responses = {k.lower(): v for k, v in template.get("responses", {}).items()}

        # ── Multi-combat tracking ─────────────────────────────────────────────
        # primary_target: the player this mob focuses counter-attacks on
        # attackers:      set of player names currently hitting this mob
        self.primary_target: str | None = None
        self.attackers:      set[str]   = set()

        from .corpse import load_mob_gear
        load_mob_gear(self, template)

    # ── Multi-combat helpers ──────────────────────────────────────────────────

    def add_attacker(self, player_name: str) -> None:
        """Register a player as attacking this mob."""
        self.attackers.add(player_name)
        if self.primary_target is None:
            self.primary_target = player_name

    def remove_attacker(self, player_name: str) -> None:
        """Remove a player from this mob's attacker set."""
        self.attackers.discard(player_name)
        if self.primary_target == player_name:
            # Hand focus to the next attacker if any
            self.primary_target = next(iter(self.attackers), None)

    # ── D&D Passive Perception ────────────────────────────────────────────────

    def passive_perception(self) -> int:
        from ..dnd.abilities import modifier, proficiency_bonus
        pp = 10 + modifier(self.computed_stat("wis"))
        if self.perception_prof:
            pp += proficiency_bonus(self.level)
        return pp

    # ── Aggression helpers ────────────────────────────────────────────────────

    def remember(self, player_name: str) -> None:
        self.memory.add(player_name)

    def is_hostile_to(self, player_name: str) -> bool:
        return self.aggressive or (player_name in self.memory)

    # ── Combat helpers ────────────────────────────────────────────────────────

    def roll_damage(self) -> int:
        return max(1, _roll(self.damage_dice))

    def is_alive(self) -> bool:
        return self.hp > 0

    def matches(self, keyword: str) -> bool:
        kw = keyword.lower()
        if kw in self.name.lower():
            return True
        return any(kw in k.lower() for k in self.key_words)

    def position_str(self) -> str:
        base = self.room_description.rstrip(".")
        labels = {
            "sitting":  "sitting here",
            "resting":  "resting here",
            "kneeling": "kneeling here",
            "reclined": "lying here",
        }
        if self.position == "standing":
            return self.room_description
        return f"{base}, {labels.get(self.position, self.position)}."

    def reset(self) -> None:
        self.max_hp = _resolve_hp(self._template)
        self.hp     = self.max_hp
        self.memory.clear()
        self.attackers.clear()
        self.primary_target = None
        self.inventory.clear()
        self.equipment.clear()
        from .corpse import load_mob_gear
        load_mob_gear(self, self._template)

    def __repr__(self) -> str:
        return (f"Mob(name={self.name!r}, level={self.level}, "
                f"hp={self.hp}/{self.max_hp}, killable={self.killable})")
