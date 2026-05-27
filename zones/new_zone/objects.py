"""
zones.the_void.objects
──────────────────────
Object templates for The Void zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Item, Weapon, Container
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "object_template": {
        "spawn_as":         Object,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
    },

    "item_template": {
        "spawn_as":         Item,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
        "weight":              0,
    },

    "silken_sack": {
        "spawn_as":         Container,
        "name":             "a &+rtattered &+csilken sack&N",
        "key_words":        ("tattered", "silken", "sack"),
        "room_description": "A &+rtattered &+csilken sack&N lies here, discarded.",
        "description":      "This sack seems to be in an awful condition.",
        "capacity":            200.0,
        "weightless_capacity": 100.0,
        "weight":              0,
        "is_open":             True,
    },

    "dimensional_vault": {
        "spawn_as":            Container,
        "name":                "&+ca dimensional vault&N",
        "key_words":           ("dimensional", "vault"),
        "room_description":    "&+cA dimensional vault floats here, humming softly.&N",
        "description":         "A shimmering vault that exists partially outside this dimension.\nIt can hold an extraordinary amount without adding to your burden.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
    },

    "windsong" : {
        "spawn_as":         Weapon,
        'name': "&+ga &wg&Wl&N&wi&Wtt&N&wer&Wi&N&wng&N &gelven scimitar&N",
        'key_words': ('scimitar', 'elven', 'glittering', 'windsong'),
        'room_description': "&+gA glittering elven scimitar is lying on the ground here.&N",
        'description': ("&+gIts blade encrusted with diamond dust, this magically light",
            "&+gelven blade glitters in the sunlight and seems to hum softly",
            "&+gwhen wielded in battle.&N"),
        "hitroll":          2,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
