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
    "Acursed Elk": {
        "name": "Acursed Elk",
        "key_words": ("Acursed", "Elk"),
        "room_description": "&wAn Acursed Elk stands here.&N",
        "description": (
            "A pale thin Elk with mangled antlers.\n"
        ),
        "race": "Elk",
        "class": "Animal",
        "level": 1,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "wander": True,
    },
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
    "Brumplin": {
        "name": "Brumplin",
        "key_words": ("Brumplin"),
        "room_description": "&wA Brumplin bounces about.&N",
        "description": (
            "A little ball of brambles with two glowing white eyes.\n"
        ),
        "race": "Brumplin",
        "level": 1,
        "stats": [10, 40, 30, 10, 10, 60],
        "aggro": True,
        "wander": True,
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)