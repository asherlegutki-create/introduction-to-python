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

# Types of Items: Weapon, Item, Object

TEMPLATES: dict[str, dict] = {
    "traffic_cone": {
        "spawn_as": Weapon,
        "name": "A &ytraffic cone&N",
        "key_words": ("traffic", "cone"),
        "room_description": "A &ytraffic cone&N blocks your path.",
        "description": (
            "    The &ycone&N, as a weapon, can be worn like a boxing glove for stabbing.",
            "It can also be used as a trumpet for loud deafening blasts or for sweet symphonies.",
        ),
        "weight": 2,
        "dice": "1d4",
        "hitroll": 2,
        "damroll": 1,
    },
    "street_lamp": {  # finish
        "spawn_as": Object,
        "name": "",
        "key_words": ("", "", ""),
        "room_description": "",
        "description": "",
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)

# "green_marker": {
#    "spawn_as": Object,  # Technically the marker should be an item but i digress
#    "name": "a &ggreen expo marker&N",
#    "key_words": ("green", "expo", "marker"),
#    "room_description": "a {g&wgreen expo marker&N has been carelessly discarded here.",
#    "description": "A forest green low-scent dry-erase marker, about half used.",
# },
# "silken_sack": {
#    "spawn_as": Item,
#    "name": "a &+rtattered &+csilken sack&N",
#    "key_words": ("tattered", "silken", "sack"),
#    "room_description": "A &+rtattered &+csilken sack&N lies here, discarded.",
#    "description": "This sack seems to be in an awful condition.",
#    "weight": 2,
# },
# "windsong": {
#    "spawn_as": Weapon,
#    "name": "&+ga &wg&Wl&wi&Wtt&wer&Wi&wng &N&+gelven scimitar&N",
#    "key_words": ("scimitar", "elven", "glittering"),
#    "room_description": "&+gA glittering elven scimitar is lying on the ground here.&N",
#    "description": """&+gIts blade encrusted with diamond dust, this magically light
# &+gelven blade glitters in the sunlight and seems to hum softly
# &+gwhen wielded in battle.&N""",
#    "weight": 3,
#    "dice": "2d8",
#    "hitroll": 2,
#    "damroll": 4,
# },
