`"""
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
    "wandering_student": {
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


    "weasel": {
        "name": "weasel",
        "key_words": ("weasel"),
        "room_description": "&wA Weasel floats here randomly.&N",
        "description": (
            "It is very soft and chubby.\n",
            "It seems like it standing on some cheese."

            ),

            "race": "non_human",
            "class": "Weasel",
            "level": 50,
            "stats": [100, 100, 100, 90, 90, 100],
            "aggro": False,
            "wander": False,


        }
                }

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)