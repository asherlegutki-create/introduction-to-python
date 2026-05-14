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
    "cheese wheel": {
        "spawn_as":         Item,
        "name":             "a &Ya cheese wheel&N",
        "key_words":        ("cheese", "wheel"),
        "room_description": "a &Ya cheese wheel&N is laid here, looking very delicious.",
        "description":      "a delicious-looking wheel of cheese.",
        "weight":           5,
    },

    "toy cheese": {
        "spawn_as":         Object,
        "name":             "a toy cheese",
        "key_words":        ("toy", "cheese"),
        "room_description": "a &mtoy &Ycheese&N is lying on the ground here.",
        "description":      "A cheese-shaped toy, made of wood and painted yellow.\n It looks like it would be fun to throw.",
        "weight":           2,
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
