"""
zones.the_void.objects
──────────────────────
Object templates for The Void zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Container, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "sack_of_darkness": {
        "spawn_as":         Container,
        "name":             "a sack of &Xdarkness&N",
        "key_words":        ("darkness", "sack"),
        "room_description": "A plain looking sack lies on the ground.",
        "description":      "The bag looks simple. It is a brown canvas. When you look inside you see a &xblack void&N.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
    },
    "sword_that_seals_the_darkness" : {
        "spawn_as":         Weapon,
        'name': "&yThe Sword that Seals the Darkness&N",
        'key_words': ('sword', 'seals', 'darkness'),
        'room_description': "&yThe Sword that Seals the Darkness&N lies here. Its light &Willuminates&N the ground around it.",
        'description': "The sword is beautiful. It was forged by the Elves as a tool against the &rGreat Darkness&N. It glows softly with &ydivine&N &Wlight&N",
        "weight":           5,
        "dice":             "6d8",
        "hitroll":          4,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
