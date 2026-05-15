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
    "Titan Battery": {
        "spawn_as":         Item,
        "name":             "a &CTitan &GBattery&N",
        "key_words":        ("Titan", "Battery"),
        "room_description": "A &CTitan &GBattery&N lies here, discarded.",
        "description":      "The battery seems worn",
        "weight":           7,
    },
    "Raptors claw" : {
        "spawn_as":         Weapon,
        'name': "&+ga &ws&Wh&wa&Wrp&we&Ws&wt &N&+grusty karambit knife&N",
        'key_words': ('Raptors', 'Claw', 'knife'),
        'room_description': "&WA rusty&N &Ckarambit knife&N &Wthat is a&N &Rreddish&N color and &Gfolds.&N",
        'description': """&+gIts blade is made of a crystalline structure that has been carefully molded
&+git has a weird glow whenever danger is near
&+gor it does it randomly&N""",
        "weight":           1,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },
        "Glass": {
        "spawn_as":         Item,
        "name":             "a &WGlass&N",
        "key_words":        ("Glass"),
        "room_description": "&WA &wclear &Gglass",
        "description":      "&W a &wclear &Gglass for &Cdrinking",
        "weight":           .3,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
