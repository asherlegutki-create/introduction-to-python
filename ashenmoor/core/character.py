"""
ashenmoor.core.character
────────────────────────
Base Character class.
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
        lines = [
            f"&+WCharacter sheet for &N{self.name}\n",
            f"&wRace:&N  {self.race}",
            f"&wClass:&N {self.cclass}",
            f"&wLevel:&N {self.level}",
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
