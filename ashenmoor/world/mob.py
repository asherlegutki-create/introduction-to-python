"""
ashenmoor.world.mob
───────────────────
Mob — a non-player character controlled by the game engine.

Mob inherits from Character so all stat and combat machinery works
identically whether the target is a player or an NPC:

  • computed_stat()     stat access with racial multiplier
  • get_ac()           DEX-based AC (overridden if ac= is in template)
  • saving_throw()     save rolls driven by class + stats
  • char_modifier()    works on Mob unchanged — combat.py stays clean
  • equipment / inventory  mobs can carry and wear items

Template dict keys
──────────────────
Identity:
  name              str   colour-coded short name
  room_description  str   what appears in the room list  (also: room_desc)
  key_words         list  targeting keywords  ["goblin", "hob"]
  description       str   seen when you look AT the mob
  race              str   defaults "Unknown"
  class / cclass    str   class label, defaults "Fighter"
  level             int   defaults 1
  stats             list  [STR DEX CON INT WIS CHA] 1-100 scale
  alignment         int   -1000 … +1000
  position          str   "standing" | "sitting" | …

HP  (first match wins):
  max_hp      int   explicit max HP
  hp          int   alias for max_hp
  hit_dice    str   "NdS+K" rolled once at spawn
  (none)            fallback: level × 8

AC:
  ac          int   explicit override on 0-100 scale;
                    omit to let get_ac() calculate from DEX + gear.

Combat:
  damage_dice str   melee damage per hit, default "1d4+0"
  coins       dict  {"gold": N, …}  dropped on death

Behaviour:
  aggro / aggressive  bool  attacks any player in room (default False)
  killable            bool  False → cannot be attacked (default True)
  perception_prof     bool  adds proficiency bonus to Passive Perception
  has_dialog          bool  True if DIALOGS table has entries for vnum
"""

from __future__ import annotations
import random
import re

from ..core.character import Character


# ── helpers ───────────────────────────────────────────────────────────────────

def _roll(dice_str: str) -> int:
    m = re.fullmatch(r"(\d+)d(\d+)([+-]\d+)?", dice_str.strip())
    if not m:
        return 1
    n, s = int(m.group(1)), int(m.group(2))
    bonus = int(m.group(3)) if m.group(3) else 0
    return sum(random.randint(1, s) for _ in range(n)) + bonus


def _resolve_hp(template: dict) -> int:
    """
    Calculate mob max HP from level only.

    Template values (hp, max_hp, hit_dice) are intentionally ignored
    so all mobs scale consistently regardless of what zone authors put
    in their dictionaries.

    Formula: level × 8 × 5
      Level  1 →   40 HP
      Level  5 →  200 HP
      Level 10 →  400 HP
      Level 20 →  800 HP
      Level 30 → 1200 HP
      Level 50 → 2000 HP
    """
    level = max(1, int(template.get("level", 1)))
    return level * 8 * 5


# ── Mob ───────────────────────────────────────────────────────────────────────

class Mob(Character):
    """
    Non-player character.

    Inherits all of Character's stat, save, and AC machinery.
    Adds mob-specific fields for room presence, AI control, and
    combat behaviour.
    """

    def __init__(self, template: dict, races: dict | None = None) -> None:
        hp_val = _resolve_hp(template)

        # Resolve races dict so we can validate the mob's race.
        if races is None:
            from ..core.race import RACES as _default_races
            races = _default_races

        # Normalise race — if the template uses a race we haven't
        # implemented (e.g. "Humanoid", "Beast", "Undead"), fall back to
        # "Human" so computed_stat() applies no racial multiplier.
        raw_race  = template.get("race", "Human")
        safe_race = raw_race if raw_race in races else "Human"

        # Normalise class — unknown classes (e.g. "Guard", "NPC", "Critter")
        # fall back to "Fighter" which has STR/CON saves and basic combat.
        # Mobs never have a dnd-dict so class only affects saving throws.
        from ..dnd.abilities import CLASS_SAVE_PROFS
        raw_class  = template.get("cclass", template.get("class", "Fighter"))
        safe_class = raw_class if raw_class.lower() in CLASS_SAVE_PROFS else "Fighter"

        # Build the Character init dict from the template
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

        # ── Room presence ─────────────────────────────────────────────────
        self.room_description: str = template.get(
            "room_description",
            template.get("room_desc", f"{self.name} is here.")
        )
        self.key_words: tuple = tuple(template.get("key_words", ()))
        desc = template.get("description", "")
        self.description:      str   = "\n".join(desc) if isinstance(desc, (tuple, list)) else desc

        # ── AC override ───────────────────────────────────────────────────
        # If the template supplies ac=, store it so combat.py's get_ac()
        # call picks it up via hasattr(mob, 'ac').
        # If absent, get_ac() calculates from DEX stat + equipment as normal.
        if "ac" in template:
            self.ac: int = int(template["ac"])

        # ── Combat ────────────────────────────────────────────────────────
        self.damage_dice: str = template.get("damage_dice", "1d4+0")
        self.hit_dice:    str = template.get("hit_dice",    "1d6+0")
        self.coins:       dict = dict(template.get("coins", {}))

        # ── Aggression / awareness ────────────────────────────────────────
        self.aggressive: bool = template.get("aggro",
                                template.get("aggressive", False))
        self.memory:     set[str] = set()
        self.perception_prof: bool = template.get("perception_prof", False)
        self.killable:   bool = template.get("killable",   True)
        self.has_dialog: bool = template.get("has_dialog", False)

        # ── Respawn reference ─────────────────────────────────────────────
        self._template: dict = template

        # ── Interraction with Mobs ────────────────────────────────────────
        self.responses = {k.lower(): v for k, v in template.get("responses", {}).items()}

    # ── D&D Passive Perception ────────────────────────────────────────────

    def passive_perception(self) -> int:
        """
        Passive Perception = 10 + WIS modifier [+ proficiency bonus].

        Baseline 75 WIS → modifier 0 → PP 10.
        """
        from ..dnd.abilities import modifier, proficiency_bonus
        pp = 10 + modifier(self.computed_stat("wis"))
        if self.perception_prof:
            pp += proficiency_bonus(self.level)
        return pp

    # ── Aggression helpers ────────────────────────────────────────────────────

    def remember(self, player_name: str) -> None:
        """Mark *player_name* as a combat target (attacked and fled)."""
        self.memory.add(player_name)

    def is_hostile_to(self, player_name: str) -> bool:
        """True if this mob will auto-attack *player_name*."""
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
        """Restore to full health on zone reset."""
        self.max_hp = _resolve_hp(self._template)
        self.hp     = self.max_hp
        self.memory.clear()

    def __repr__(self) -> str:
        return (f"Mob(name={self.name!r}, level={self.level}, "
                f"hp={self.hp}/{self.max_hp}, killable={self.killable})")
