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
    "mr_mob": {
        "name": "Mr Mob",
        "key_words": ("mr", "mob"),
        "room_description": "wondering in the forest",
        "description": ("This mob was spawned from homework"),
        "race": "Human",
        "class": "Student",
        "level": 10,
        "stats": [70, 65, 60, 80, 70, 95],
        "aggro": False,
        "wander": True,
    }
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)