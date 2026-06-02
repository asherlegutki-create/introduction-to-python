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
    "pencil": {
        "spawn_as":         Item,
        "name":             "pencil",
        "key_words":        ("pencil", "yellow"),
        "room_description": "A &Yyellow&N &wpencil&N lies here.",
        "description":      "the &Ypencil&N seems lightly used and decently sharp.",
        "weight":           1,
    },
    "syth" : {
        "spawn_as":         Weapon,
        'name': "syth",
        'key_words': ('old', 'syth'),
        'room_description': "an &yold syth&N sits propped up against the wall.&N",
        'description': """the blades are &yr&wu&ys&wt&ye&wd&N and it seems to belong at least a century before your time""",
        "weight":           4,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },
    "water bottle" : {
         "spawn_as":         Weapon,
         'name': "&Bwater bottle&N",
         'key_words': ('water bottle', 'bottle'),
         'room_description': "a &Bwater bottle&N sits, half full\n or half empty depending on the person",
         'description': "a light bottle of water, seems &Wclean&N and &Bdrinkable&N, could possibly cause &rdamage&N with its &Xmetal&N exterior",
         "weight":           1,
     },
      
      "math sword" : {
         "spawn_as":         Weapon,
         'name': "math sword",
         'key_words': ('math', 'sword'),
         'room_description': "a &rrusty &ypitch fork&N sits propped against th wall\n could cause sufficient &rdamage&N to an opponent",
         'description': "this old wooden fork stands taller than the average student, would most likely bring &ytetanus&N upon its victim",
         "weight":           4,
     },
    },




# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
