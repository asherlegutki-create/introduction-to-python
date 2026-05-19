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
    "whiteboard_marker": {
        "spawn_as":         Object,
        "name":             "a &gexpo marker&N",
        "key_words":        ("green", "expo", "marker"),
        "room_description": "an &gexpo marker&N sits here&N.",
        "description":      "A &gforest green&N low-scent dry-erase marker, about half used.",
    },

    "pencil": {
        "spawn_as":         Item,
        "name":             "a &Ypencil&N",
        "key_words":        ("pencil", "yellow"),
        "room_description": "A &Yyellow pencil&N lies here.",
        "description":      "the &Ypencil&N seems lightly used and decently sharp.",
        "weight":           1,
    },
    "Mrs.Allisons_syth" : {
        "spawn_as":         Weapon,
        'name': "an old &ysyth&N",
        'key_words': ('old', 'syth'),
        'room_description': "an &yold syth&N sits propped up against the wall.&N",
        'description': """the blades are &yrusted&N and it seems to belong at least a century before your time""",
        "weight":           4,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
