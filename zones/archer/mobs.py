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
    "&MIllrigger Mage&N": {
        "name": "Illrigger",
        "key_words": ("Illrigger"),
        "room_description": "&MIllriggers &Wwander these parts, searching for any intruders.&N",
        "description": (
            "&MIllrigger Mage, &Wit is clearly mastering the arts of &xDark Magic&N."
        ),
        "race": "Illrigger",
        "class": "Mage",
        "level": 39,
        "stats": [75, 92, 53, 72, 85, 10],
        "aggro": True,
        "wander": True,

    },
        
        "&RIllrigger Rogue&N": {
        "name": "Illrigger Rogue" ,
        "key_words": ("Illrigger", "Rogue"),
        "room_description": "&RIllriggers &Wwander these parts, searching for any intruders.&N",
        "description": (
            "&xIllrigger Rogue, &Wit's trying to guard the chest room&N",
        ),
        "race": "Illrigger",
        "class": "Rogue",
        "level": 24,
        "stats": [55, 79, 53, 62, 85, 10],
        "aggro": True,
        "wander": True,

        },
    }

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)