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
    "object_template": {
        "spawn_as":         Object,
        "name":             "object",
        "key_words":        ("1", "2",),
        "room_description": "object is here.",
        "description":      "can't interact with.",
    },
    "Item_template": {
        "spawn_as":         Item,
        "name":             "item",
        "key_words":        ("1", "2",),
        "room_description": "item sets here.",
        "description":      "can interact with.",
    },
    "Weapon_template" : {
        "spawn_as":         Weapon,
        'name': "thing",
        'key_words': ("1", "2"),
        'room_description': "a weapon sets here.",
        'description': "bonk",
        "weight":           3,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },
    "Brumplin Seed": {
        "spawn_as":         Object,
        "name":             "Brumplin Seed",
        "key_words":        ("Brumplin", "Seed"),
        "room_description": "A &gball of brambles&n sticks out of the mud",
        "description":      "A light ball of brambles",
    },
     "Acursed Elk Steak": {
        "spawn_as":         Item,
        "name":             "Acursed Elk Steak",
        "key_words":        ("Acursed", "Elk", "Steak"),
        "room_description": "a slab of &mpurpleish meat",
        "description":      "an unappealing steak"
                                "&Wthe key to immortality, &Xbut not a good one",
    },
     "Magnea Pounder" : {
        "spawn_as":         Weapon,
        'name': "Magnea pounder",
        'key_words': ("Magnea", "pounder"),
        'room_description': "A writhing leg with a large rock attached lies here.",
        'description': "A long furry black leg with a large black rock stuck at the end",
        "weight":           3,
        "dice":             "2d10",
        "hitroll":          2,
        "damroll":          4,
    },
     "Ebony Cleaver" : {
        "spawn_as":         Weapon,
        'name': "Ebony Cleaver",
        'key_words': ("Ebony", "Cleaver"),
        'room_description': "An &XEbony Cleaver&n lies here.",
        'description': "A &Mroyal&n cleaver made of ebony",
        "weight":           10,
        "dice":             "2d10",
        "hitroll":          2,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
