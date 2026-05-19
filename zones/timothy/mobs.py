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
    "Acursed Elk": {
        "name": "Acursed Elk",
        "key_words": ("Acursed", "Elk"),
        "room_description": "&wAn Acursed Elk stands here.&N",
        "description": (
            "A pale thin Elk with spiked antlers.\n"
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
        "race": "Shrimple",
        "class": "monk",
        "level": 30,
        "stats": [80, 80, 70, 60, 70, 75],
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
    },
    "Acursed Man": {
        "name": "Acursed Man",
        "key_words": ("Acursed", "Man"),
        "room_description": "&wAn Acursed Man stares blankly.&N",
        "description": (
            "A starved man with an empty look in his eyes.\n"
        ),
        "race": "Human",
        "class": "none",
        "level": 1,
        "stats": [5, 10, 80, 10, 10, 10],
        "aggro": False,
        "wander": True,
    },
     "Pale Shaman": {
        "name": "The Pale Shaman",
        "key_words": ("Pale", "Shaman"),
        "room_description": "&WThe Pale Shaman seems to be in prayer.&N",
        "description": (
            "A pale bald grey cloaked woman .\n"
        ),
        "race": "Human",
        "class": "shaman",
        "level": 60,
        "stats": [30, 30, 60, 80, 70, 40],
        "aggro": True,
        "wander": False,
    },
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)