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
    "green_marker": {
        "spawn_as":         Object,
        "name":             "a &ggreen expo marker&N",
        "key_words":        ("green", "expo", "marker"),
        "room_description": "a {g&wgreen expo marker&N has been carelessly discarded here.",
        "description":      "A forest green low-scent dry-erase marker, about half used.",
    },

    "silken_sack": {
        "spawn_as":         Item,
        "name":             "a &+rtattered &+csilken sack&N",
        "key_words":        ("tattered", "silken", "sack"),
        "room_description": "A &+rtattered &+csilken sack&N lies here, discarded.",
        "description":      "This sack seems to be in an awful condition.",
        "weight":           2,
    },
    "Raptors claw" : {
        "spawn_as":         Weapon,
        'name': "&+ga &ws&Wh&wa&Wrp&we&Ws&wt &N&+grusty karambit knife&N",
        'key_words': ('Raptors', 'Claw', 'knife'),
        'room_description': "&+gA rusty karambit knife that is a reddish color and folds.&N",
        'description': """&+gIts blade is made of a crystalline structure that has been carefully molded
&+git has a weird glow whenever danger is near
&+gor just a monster&N""",
        "weight":           1,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
