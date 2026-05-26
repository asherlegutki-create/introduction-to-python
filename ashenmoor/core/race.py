"""
ashenmoor.core.race
────────────────────
Race definitions — multiplier-based backend scaling on the 1-100 display scale.

Display vs. backend
────────────────────
  Every stat is DISPLAYED on a 1-100 scale for all races.
  Equipment bonuses add to the displayed value, capped at 100.

  In the backend, a racial multiplier is applied to the displayed value
  to get the effective stat used for all modifier calculations.

  displayed_stat  =  min(base + equipment_bonus, 100)     [what you see]
  effective_stat  =  int(displayed_stat × racial_mult)     [used in combat]
  modifier        =  (effective_stat − 75) // 5

  Example — Ring of STR +10 worn by both a Human and an Ogre (base STR 90):
    Human : displayed 100 × 1.0 = 100  → modifier +5
    Ogre  : displayed 100 × 1.5 = 150  → modifier +15

  The same item benefits the Ogre more because their racial multiplier
  amplifies the identical displayed value to a higher effective stat.

Designing multipliers
─────────────────────
  Human        → 1.0 on everything (neutral reference point)
  Races > 1.0  → exceed human capability in that attribute
  Races < 1.0  → limited compared to a human in that attribute

  At displayed-max (100):
    × 1.0  effective 100  modifier +5    (human peak)
    × 1.1  effective 110  modifier +7
    × 1.2  effective 120  modifier +9
    × 1.3  effective 130  modifier +11
    × 1.5  effective 150  modifier +15   (ogre-tier)
    × 0.8  effective  80  modifier +1
    × 0.7  effective  70  modifier -1    (elven frailty vs strength)
    × 0.6  effective  60  modifier -3
    × 0.5  effective  50  modifier -5
"""

from .stats import Stats

_DEFAULT_MULT = 1.0


class Race:
    """
    A playable or NPC race defined by per-stat multipliers.

    Parameters
    ----------
    d : dict
        name              str               Display name.
        stat_multiplier   dict[str, float]  Per-ability scale factor.
                                            Any stat not listed defaults to 1.0.
    """

    def __init__(self, d: dict):
        self.name: str  = d.get("name", "Unknown")
        self.size: str  = d.get("size", "Medium")   # Fine/Tiny/Small/Medium/Large/Huge/Gargantuan
        raw: dict       = d.get("stat_multiplier", {})
        self._mult: dict[str, float] = {
            k.lower(): float(v) for k, v in raw.items()
        }

    def get_multiplier(self, stat) -> float:
        """Return the racial multiplier for *stat* (default 1.0)."""
        if isinstance(stat, Stats):
            key = stat.abv
        elif isinstance(stat, int):
            key = list(Stats)[stat].abv
        else:
            key = str(stat).lower()
        return self._mult.get(key, _DEFAULT_MULT)

    def __repr__(self):
        return f"Race({self.name!r})"


# ── Canonical race table ───────────────────────────────────────────────────────
#
# Multiplier reference at displayed max (100):
#   × 1.5 → effective 150 → modifier +15
#   × 1.3 → effective 130 → modifier +11
#   × 1.2 → effective 120 → modifier  +9
#   × 1.1 → effective 110 → modifier  +7
#   × 1.0 → effective 100 → modifier  +5
#   × 0.8 → effective  80 → modifier  +1
#   × 0.7 → effective  70 → modifier  -1
#   × 0.6 → effective  60 → modifier  -3
#   × 0.5 → effective  50 → modifier  -5

RACES: dict[str, Race] = {

    "Human": Race({
        "name": "Human",
        "stat_multiplier": {
            # Neutral — the reference point for all other races
            "str": 1.0, "dex": 1.0, "con": 1.0,
            "int": 1.0, "wis": 1.0, "cha": 1.0,
        },
    }),

    "Dwarf": Race({
        "name": "Dwarf",
        "stat_multiplier": {
            "str": 1.1,   # burly — eff 110 → +7
            "dex": 1.0,   # average agility
            "con": 1.3,   # very tough — eff 130 → +11
            "int": 0.9,   # capable, not scholarly — eff 90 → +3
            "wis": 1.0,   # steady
            "cha": 0.8,   # dour — eff 80 → +1
        },
    }),

    "Grey Elf": Race({
        "name": "Grey Elf",
        "stat_multiplier": {
            "str": 0.7,   # lithe, not powerful — eff 70 → -1
            "dex": 1.2,   # supernaturally quick — eff 120 → +9
            "con": 0.8,   # physically fragile — eff 80 → +1
            "int": 1.2,   # deeply intelligent — eff 120 → +9
            "wis": 1.1,   # perceptive — eff 110 → +7
            "cha": 1.1,   # effortlessly graceful — eff 110 → +7
        },
    }),

    "Ogre": Race({
        "name": "Ogre",
        "stat_multiplier": {
            "str": 1.5,   # monstrous strength — eff 150 → +15
            "dex": 0.6,   # ponderous — eff 60 → -3
            "con": 1.5,   # incredibly tough — eff 150 → +15
            "int": 0.5,   # dim-witted — eff 50 → -5
            "wis": 0.6,   # impulsive — eff 60 → -3
            "cha": 0.6,   # fearsome, not likable — eff 60 → -3
        },
    }),
}
