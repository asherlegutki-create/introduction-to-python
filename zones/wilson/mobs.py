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
    "wandering cheezi student": {
        "name": "a wandering student",
        "key_words": ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.\n"
            "Or possibly just lost."
        ),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
<<<<<<< HEAD




        "the cheese monster": {
        "name": "the cheese monster",
        "key_words": ("cheese", "monster"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&Ye&N&ys&Ye&N &bmonster &Wsleeps here&N",
        "description": (
            "a cheese monster thinking into space "
            "most likely thinking about &msleep..."
        ),
        "race": "cheese",
        "class": "scary guy",
        "level": "29",
        "stats": [46, 59, 65, 55, 75, 80],
        "aggro": False,
        "wander": False,
    },

     "the cheez sniffer": {
        "name": "the &yc&Yh&N&ye&Ye&N&ys&Ye&N sniffer",
        "key_words": ("cheese", "sniffer"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&N&ys&Ye&N &bsniffer &Wsniffs around here&N",
        "description": (
            "a cheese sniffer sniffing around "
            "most likely sniffing about &msleep..."
        ),
        "race": "cheese",
        "class": "sniffr guy",
        "level": "14",
        "stats": [10 ,48 ,23 ,92 ,16 ,82 ],
        "aggro": False,
        "wander": True,
        },

=======
    "Shrimpman": {
        "name": "Shrimpman",
        "key_words": ("shrimp"),
        "room_description": "&wA Shrimpman is backflipping.&N",
        "description": ("very pink.\n" "Shrimp."),
        "race": "humanoid",
        "class": "monk",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
>>>>>>> 7e6b0d66c56fcf65e146dc459fdf2278a582c9be
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)