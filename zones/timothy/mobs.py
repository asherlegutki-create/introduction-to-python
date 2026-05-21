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
    "Brumplin Minor": {
        "name": "Brumplin Minor",
        "key_words": ("Brumplin"),
        "room_description": "&wA Brumplin Minor bounces about.&N",
        "description": (
            "A little ball of brambles with two glowing white eyes.\n"
        ),
        "race": "Brumplin",
        "level": 1,
        "stats": [10, 40, 30, 10, 10, 60],
        "aggro": False,
        "wander": True,
    },
    "Brumplin Alpha": {
        "name": "Brumplin Alpha",
        "key_words": ("Brumplin"),
        "room_description": "&gA Brumplin Alpha&n howels a &rdeathly&n screech.&N",
        "description": (
            "The final stage of the &gBrumplin&n race.\n"
            "&rvery&n aggressive"
        ),
        "race": "Brumplin",
        "level": 20,
        "stats": [80, 70, 30, 10, 10, 10],
        "aggro": True,
        "wander": True,
    },
    "Acursed Man": {
        "name": "Acursed Man",
        "key_words": ("Acursed", "Man"),
        "room_description": "&wAn Acursed Man stares blankly.&N",
        "description": (
            "A thin man with an empty look in his eyes.\n"
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
     "Magnea": {
        "name": "Magnea",
        "key_words": ("Magnea"),
        "room_description": "&rA Magnea &Xscuddles around.&N",
        "description": (
            "A large spider with rocks protruding from its back.\n"
        ),
        "race": "Monster spider",
        "class": "mob",
        "level": 40,
        "stats": [80, 90, 80, 10, 10, 0],
        "aggro": True,
        "wander": True,
    },
     "Terramagnea The Earthen Arachnid": {
        "name": "&rTerramagnea The Earthen Arachnid",
        "key_words": ("Terramagnea"),
        "room_description": "&rTerramagnea The Earthen Arachnid &Xwatches silently.&N",
        "description": (
            "A massive spider with jagged black rocks protruding from all angles.\n"
        ),
        "race": "Monster spider",
        "class": "boss",
        "level": 60,
        "stats": [90, 90, 90, 10, 10, 0],
        "aggro": True,
        "wander": False,
    },
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)