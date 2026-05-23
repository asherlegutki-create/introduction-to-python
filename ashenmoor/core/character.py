"""
ashenmoor.core.character
────────────────────────
Base Character class.

HP is derived from CON and level when not specified in the dict:
    max_hp = (CON // 5) × level  +  level × 5
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .stats import Stats

if TYPE_CHECKING:
    from .race import Race


class Character:
    def __init__(self, d: dict, races: dict | None = None):
        self.name:      str  = d.get("name",     "Unknown")
        self.stats:     list = d.get("stats",    [80]*6)
        self.race:      str  = d.get("race",     "Human")
        self.level:     int  = d.get("level",    1)
        self.position:  str  = d.get("position", "standing")
        self.cclass:    str  = d.get("class",    "Warrior")
        self.powers:    list = d.get("powers",   [])
        self.inventory: list = list(d.get("inventory", []))
        self.equipment: dict = dict(d.get("equipment", {}))
        # inventory  — list of Item instances being carried (not equipped)
        # equipment  — slot_key → Item  (dual slots store list[Item, max 2])

        # ── Hit Points ────────────────────────────────────────────────────────
        # max_hp can be set explicitly in the dict, or is computed from CON/level.
        # hp starts at max_hp (full health) unless overridden.
        con     = self.stats[Stats.CONSTITUTION.value] if len(self.stats) > Stats.CONSTITUTION.value else 75
        default_max  = max(10, (con // 5) * max(1, self.level) + max(1, self.level) * 5)
        self.max_hp: int = d.get("max_hp", default_max)
        self.hp:     int = d.get("hp",     self.max_hp)

        if races is None:
            from .race import RACES
            races = RACES
        self._races = races

    def get_stat(self, stat) -> int:
        if isinstance(stat, int):   return self.stats[stat]
        if isinstance(stat, Stats): return self.stats[stat.value]
        if isinstance(stat, str):
            for s in Stats:
                if stat.lower() == s.abv: return self.stats[s.value]
        raise ValueError(f"Unknown stat: {stat!r}")

    def computed_stat(self, stat) -> int:
        race = self._races.get(self.race)
        if race is None: return self.get_stat(stat)
        return int(self.get_stat(stat) * race.get_mod(stat))

    def character_sheet(self) -> str:
        hp_pct = int(self.hp / max(1, self.max_hp) * 100)
        lines = [
            f"&+WCharacter sheet for &N{self.name}\n",
            f"&wRace:&N  {self.race}",
            f"&wClass:&N {self.cclass}",
            f"&wLevel:&N {self.level}",
            f"&wHP:&N    {self.hp}/{self.max_hp}  ({hp_pct}%)",
            "&wStats:&N",
            (f"  &wStrength:&N     {self.get_stat('str'):>3}    "
             f"&wIntelligence:&N {self.get_stat('int'):>3}"),
            (f"  &wDexterity:&N    {self.get_stat('dex'):>3}    "
             f"&wWisdom:&N       {self.get_stat('wis'):>3}"),
            (f"  &wConstitution:&N {self.get_stat('con'):>3}    "
             f"&wCharisma:&N     {self.get_stat('cha'):>3}"),
        ]
        if self.powers:
            lines.append("&wPowers:&N  " +
                         ", ".join(p.get("name","?") for p in self.powers))
        return "\n".join(lines)

    def pcs(self):
        from ..color import cprint
        cprint(self.character_sheet())

    def __str__(self):  return self.character_sheet()
    def __repr__(self): return (f"Character(name={self.name!r}, race={self.race!r}, "
                                f"class={self.cclass!r}, level={self.level})")
