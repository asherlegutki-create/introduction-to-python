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
    "Lucas": {
        "name": "Lucas",
        "key_words": ("Lucas"),
        "room_description": "&wLucas meanders about aimlessly.&N",
        "description": ("A student with a faraway look,\n" "Or  just lost."),
        "race": "Elf",
        "class": "Shortone",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
    "The_Inn_Maid": {
        "name": "Maudie, the inn's maid",
        "key_words": ("Maudie", "inn's", "maid"),
        "room_description": "&wMaudie, the inn's maid, cleans the inn thoroughly and happily.&N",
        "description": ("A nice lady with a smile on her face"),
        "race": "Human",
        "class": "Cleric",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    }
}


# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)