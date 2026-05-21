"""
zones.the_planes.objects
──────────────────────
Object templates for The Planes zone.

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
    "Assorted_Bottles__Full": {
        "spawn_as":         Item,
        "name":             "Assorted bottles",
        "key_words":        ("bottles"),
        "room_description": "A few &gc&Bo&Yl&Co&Mr&Rf&Gu&bl&N &Wglass&N &Yb&co&mt&rt&gl&Be&Ms&N are on the &ycounter&N of the bar, they are all filled with different kinds of liquids.",
        "description":      "Five assorted &gc&Bo&Yl&Co&Mr&Rf&Gu&bl&N and &yunlabeled&N &Wglass bottles&N are siting on the counter.\nIt might &rnot&N be the best idea to drink these,as you don't know what is in them, but you do you.",
    },

    

    
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
