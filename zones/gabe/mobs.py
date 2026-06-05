"""
zones.the_void.mobs
───────────────────
Mob templates for The Void zone.

Add an entry to TEMPLATES for every NPC type that can appear in this zone.
Call spawn(key) to get a fresh independent Mob instance — place as many


copies in rooms as you like, each is independent.
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "the cheese monster": {
        "name": "the cheese monster",
        "key_words": ("cheese", "monster", "m"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&Ye&N&ys&Ye&N &bmonster &Wsleeps here&N",
        "description": (
            "a cheese monster thinking into space "
            "most likely thinking about &msleep..."
        ),
        "race": "cheese",
        "class": "scary guy",
        "level": 29,
        "stats": [46, 59, 65, 55, 75, 80],
        "aggro": False,
        "wander": False,
    },

     "the cheez sniffer": {
        "name": "the &yc&Yh&N&ye&Ye&N&ys&Ye&N sniffer",
        "key_words": ("cheese", "sniffer", "s"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&Ye&N&ys&Ye&N &bsniffer &Wsniffs around here&N",
        "description": (
            "a cheese sniffer sniffing around "
            "most likely sniffing around for crumbs to eat"
        ),
        "race": "cheese",
        "class": "sniffr guy",
        "level": 14,
        "stats": [10 ,48 ,23 ,92 ,16 ,82],
        "aggro": False,
        "wander": False,
        },

    "the cheese spirit": {
        "name": "the cheese spirit",
        "key_words": ("cheese", "spirit", "sp"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&Ye&N&ys&Ye&N &bspirit &Rhaunts&N &Wthis place&N",
        "description": (
            "a cheese spirit haunting this place "
            "most likely &Rhaunting&N  The &YC&N&yh&Y&Ne&ye&Ys&N&ye&N monsters &msleep..."
        ),
        "race": "cheese",
        "class": "spirit guy",
        "level": 50,
        "stats": [100, 80, 80, 80, 80, 80],
        "aggro": False,
        "wander": False,
        },

    "the cheesy bird": {
        "name": "the &Yc&N&yh&Ye&N&ye&Ys&N&yy&Y&N &Bbird",
        "key_words": ("cheesy", "bird"),
        "room_description": "&Wthe&N &Yc&N&yh&Ye&N&ye&Ys&N&yy&Y&N &Bbird &Wchirps here&N",
        "description": (
            "a cheesy bird chirping around "
            "seems like hes chirping around for fun but who knows maybe hes looking for cheese crumbs to eat"
        ),
        "race": "cheese",
        "class": "bird guy",
        "level": 7,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "wander": True,
        },

    "the cheez fih": {
        "name": "&Wthe&N &ycheez&N &bfih&N",
        "key_words": ("cheese", "fih"),
        "room_description": "&Wthe&N &ycheese&N &bfih&N&W swims here&N",
        "description": (
            "a cheese fih swimming around "
            "trying to find his fren."
        ),
        "race": "cheese",
        "class": "fih guy",
        "level": 20,
        "stats": [35, 10, 25, 15, 40, 100],
        "aggro": False,
        "wander": True,
    },

    "the cheese librarian": {
        "name": "&Wthe&N &bunderwater&N &Yc&N&yh&Y&N&ye&ye&Ys&N&ye&N &Blibrarian",
        "key_words": ("cheese", "librarian"),
        "room_description": "&Wthe&N &Yc&N&yh&Y&N&ye&ye&Ys&N&ye&N &Blibrarian &Wsits thinking about a secret person that must hold a lot of secrets",
        "description": (
            "a cheese librarian sitting here thinking about a secret person that must hold a lot of secrets "
        ),
        "race": "cheese",
        "class": "librarian guy",
        "level": 30,
        "stats": [50, 50, 50, 50, 50, 50],
        "aggro": False,
        "wander": False,

    },

}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
