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
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
    },

    "tennis_racket": {
        "spawn_as":         Object,
        "name":             "&Gtennis racket&N",
        "key_words":        ("tennis", "racket"),
        "room_description": "A tennis racket lies here",
        "description":      "Its just a tennis racket what could you do with it \n maybe wack someone with it?",
    },

    "green_marker": {
        "spawn_as":         Object,
        "name":             "a &ggreen expo marker&N",
        "key_words":        ("green", "expo", "marker"),
        "room_description": "a {g&wgreen expo marker&N has been carelessly discarded here.",
        "description":      "A forest green low-scent dry-erase marker, about half used.",
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
