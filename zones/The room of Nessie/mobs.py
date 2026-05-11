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
    "Pink Nessie": {
        "name": "Pink Nessie",
        "key_words": ("Pink", "Nessie"),
        "room_description": "&gA very strange pink coloration of a Nessie.&N",
        "description": (
            "It sits there... menacingly.\n"
            "Or it is just sitting there without a single thought in that head."
        ),
        "race": "Nessie",
        "class": "Animal",
        "level": 1,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": False,
    },

    "Nessie": {
    "name": "Nessie",
    "key_words": ("Nessloc", "Nessie"),
    "room_description": "&wA A green animal that swims in The Void peacefully and powerfully.&N",
    "description": (
        "A green creature that has a cute look to it's face.\n",
        "It seems to be eating a metallic weapon... or just a radioactive core.",
    ),
    "race": "non_human",
    "class": "Nessie",
    "level": 50,
    "stats": [100, 100, 100, 90, 90, 100],
    "aggro": False,
    "wander": False,
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)