"""
zones.the_void.objects
──────────────────────
Object templates for The Void zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "mr_mob_sword": {
        "spawn_as":         Object,
        "name":             "a &RMr Mob's Sword&N",
        "key_words":        ("mr", "mob", "sword"),
        "room_description": "Mr Mob's &RSword&N lays here, seeming to long for him.",
        "description":      "The great &Rsword&N once wielded by Mr Mob.",
    },

    "sword_of_the_way" : {
        "spawn_as":         Weapon,
        'name': "&RSword&N &BOf The Way&N",
        'key_words': ('sword', 'sword of the way'),
        'room_description': "A mighty &Rsword&N of &Btruth&N lays here, ready for use",
        'description': "The &RSword&N Of The &BWay&N",
        "weight":           6,
        "dice":             "2d8",
        "hitroll":          4,
        "damroll":          8,
    }
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
