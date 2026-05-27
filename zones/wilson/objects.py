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
    "Nuke_Shot": {
        "spawn_as":         Item,
        "name":             "a &WNuke&N &RShot&N",
        "key_words":        ("Nuke", "Shot",),
        "room_description": "a &WN&N&Ru&N&Wk&N&Re&N &RS&N&Wh&N&Ro&N&Wt&N has been carelessly discarded here.",
        "description":      "A fishing rod that seems to be ready to pull.",
    }, 
     "Stab_Shot": {
        "spawn_as":         Item,
        "name":             "a &RStab&N &WShot&N",
        "key_words":        ("Stab", "Shot"),
        "room_description": "a &RS&N&Wt&N&Ra&N&Wb&N &RS&N&Wh&N&Ro&N&Wt&N has been carelessly discarded here.",
        "description":      "Pull it and you go boom.",
    },   
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
