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
    "OBJ template": {
        "spawn_as":         Object,
        "name":             "a thing",
        "key_words":        ("stuff"),
        "room_description": "",
        "description":      "",
    },

    "silken_sack": {
        "spawn_as":         Item,
        "name":             "a &+rtattered &+csilken sack&N",
        "key_words":        ("tattered", "silken", "sack"),
        "room_description": "A &+rtattered &+csilken sack&N lies here, discarded.",
        "description":      "This sack seems to be in an awful condition.",
        "weight":           2,
    },
    "windsong" : {
        "spawn_as":         Weapon,
        'name': "&+ga &wg&Wl&wi&Wtt&wer&Wi&wng &N&+gelven scimitar&N",
        'key_words': ('scimitar', 'elven', 'glittering'),
        'room_description': "&+gA glittering elven scimitar is lying on the ground here.&N",
        'description': """&+gIts blade encrusted with diamond dust, this magically light
&+gelven blade glitters in the sunlight and seems to hum softly
&+gwhen wielded in battle.&N""",
        "weight":           3,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },
    "Brumplin husk": {
        "spawn_as":         Object,
        "name":             "Brumplin husk",
        "key_words":        ("Brumplin", "husk"),
        "room_description": "A ball of brambles",
        "description":      "A light ball of brambles",
    },
     "Acursed Elk Stake": {
        "spawn_as":         Object,
        "name":             "Acursed Elk Stake",
        "key_words":        ("Acursed", "Elk", "Stake"),
        "room_description": "a slab of &mpurpleish meat",
        "description":      "an unappealing stake"
                                "&Wthe key to immortality, &Xbut not a good one",
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
