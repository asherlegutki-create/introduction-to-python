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
        "description":      "The bag looks simple. It is a brown canvas. When you look inside you see a &Xblack void&N.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
    },
    "sword_that_seals_the_darkness" : {
        "spawn_as":         Weapon,
        'name': "&CT&Bh&Ce &BS&Cw&Bo&Cr&Bd &Ct&Bh&Ca&Bt &CS&Be&Ca&Bl&Cs &Bt&Ch&Be &CD&Ba&Cr&Bk&Cn&Be&Cs&Bs&N",
        'key_words': ('sword', 'seals', 'darkness'),
        'room_description': "&CT&Bh&Ce &BS&Cw&Bo&Cr&Bd &Ct&Bh&Ca&Bt &CS&Be&Ca&Bl&Cs &Bt&Ch&Be &CD&Ba&Cr&Bk&Cn&Be&Cs&Bs&N lies here. Its light &Willuminates&N the ground around it.",
        'description': "The sword is beautiful. It was forged by the &GElves&N as a tool against the &rGreat Darkness&N. It glows softly with &Bbluish&N &Wlight&N",
        "weight":           25,
        "dice":             "3d3",
        "hitroll":          5,
        "damroll":          5,
    },
    "hanging_tree" : {
        "spawn_as":         Object,
        'name': "The Hanging Tree",
        'key_words': ('tree', 'hanging'),
        'room_description': "An &Xominous&N, sad looking tree towers above you.",
        'description': "A &Xhanging tree&N, where they strung up a man they say &rmurdered&N three.",
    },
    "pile_of_goo" : {
        "spawn_as":         Item,
        'name': "a pile of goo",
        'key_words': ('pile', 'goo'),
        'room_description': "A pile of &mgoo&N lies on the ground.",
        'description': "The goo is slightly, and disgustingly, warm. It has an odd, mildewy scent.",
    },
    "falcon_feather" : {
        "spawn_as":         Item,
        'name': "a falcon feather",
        'key_words': ('feather', 'falcon'),
        'room_description': "A &xdark&N colored feather lies on the ground.",
        'description': "The feather is dark, from a falcon.",
    },
    "ethereal_cloak" : {
        "spawn_as":         Item, 
        "name": "an &methereal cloak&N",
        "key_words": ("ethereal", "cloak"),
        "room_description": "a discarded cloak lies on the ground",
        "description": "There is nothing special about the cloak, yet you seem to feel a presence of &bdark magic&N.",
        "wear_on":   "on_body",
        "armor_type": "cloth",
        "weight":    10.0,
        "cost":      200,
        "stat_mods": {"dex": 10},
        "save_mods": {},
    },
    # "health_potion" : {
    #     "spawn_as":           Item,
    #     "name":      "a health potion",
    #     "key_words": ("health", "potion"),
    #     "room_description": "A glass bottle filled with a &Rlight red liquid&N lies here",
    #     "description": "A glass, round bottle filled with a potion that refills your health. It smells sweet, like cherries",
    #     "wear_on":   "held",
    #     "liquid":       "potion",
    #     "capacity":     5,
    #     "current":      5,
    #     "poisoned":     False,
    #     "thirst":       0,
    #     "weight":    1,
    #     "cost":      5,
    #     "stat_mods": {},
    #     "save_mods": {},
    # },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
