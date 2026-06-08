"""
zones.abyssal.mobs
──────────────────
Abyssal spider mob templates.

Three tiers:
  abyssal_spider_1  level 10  — pale blue-white, minor threat
  abyssal_spider_2  level 20  — deeper colour, more dangerous
  abyssal_spider_3  level 30  — magenta-black, venom fangs weapon with
                                random_poison proc (1-in-30 per hit, 5 ticks)
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {

    "abyssal_spider_1": {
        "name":             "&Lan abyssal spider&N",
        "key_words":        ("abyssal", "spider"),
        "room_description": "&LA pale abyssal spider&N skitters across the ground.",
        "description": (
            "A pale &Labyssal spider&N, its translucent body glowing faintly with\n"
            "an eerie blue-white light. Eight eyes reflect your movement."
        ),
        "race":    "Spider",
        "class":   "Fighter",
        "level":   10,
        "stats":   [70, 85, 65, 30, 50, 20],
        "aggro":   True,
        "wander":  True,
        "killable": True,
        "damage_dice": "1d6+0",
        "coins":   {"gold": 0, "silver": 2, "copper": 5},
    },

    "abyssal_spider_2": {
        "name":             "&La large &N&mabyssal mspider&N",
        "key_words":        ("abyssal", "large", "spider"),
        "room_description": "&LA large abyssal &N&mspider&N lurks in the shadows.",
        "description": (
            "A larger &Labyssal &N&mspider&N, its abdomen swollen with venom.\n"
            "Faint &mpurple light&N pulses beneath its chitin."
        ),
        "race":    "Spider",
        "class":   "Fighter",
        "level":   20,
        "stats":   [80, 90, 75, 35, 55, 20],
        "aggro":   True,
        "wander":  True,
        "killable": True,
        "damage_dice": "1d8+2",
        "coins":   {"gold": 1, "silver": 5, "copper": 0},
    },

    "abyssal_spider_3": {
        "name":             "&La massive &Mabyssal spider&N",
        "key_words":        ("abyssal", "massive", "spider"),
        "room_description": "&LA massive abyssal &Mspider&N crouches here, fangs dripping.",
        "description": (
            "A massive &Labyssal &Mspider&N, its body wreathed in &Mmagenta shadow&N.\n"
            "Viscous venom drips from its enormous fangs, burning where it falls.\n"
            "This creature is the apex of its kin — and it knows it."
        ),
        "race":    "Spider",
        "class":   "Fighter",
        "level":   30,
        "stats":   [90, 95, 85, 40, 60, 20],
        "aggro":   True,
        "wander":  False,
        "killable": True,
        "damage_dice": "1d10+4",
        "coins":   {"gold": 5, "silver": 10, "copper": 0},
        "equipment": {
            "primary_hand": {
                "type":             "Weapon",
                "name":             "&Mvenom fangs&N",
                "key_words":        ("venom", "fangs"),
                "room_description": "",
                "description":      "A pair of massive dripping fangs.",
                "dice":             "1d6",
                "hitroll":          2,
                "damroll":          3,
                "two_handed":       False,
                "weight":           0,
                "proc":             "random_poison",
                # no_take handled by killable mob — fangs stay on the corpse
                # but since they have no wear_on they can't be equipped by players
            },
        },
    },

}

spawn = make_spawner(TEMPLATES, lambda: Mob)
