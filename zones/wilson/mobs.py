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
    "George_Washington": {
        "name": "George_Washington",
        "key_words": ("Washington", "George"),
        "room_description": "&wA He stands forever in the position he was in crossing the Deleware.&N",
        "description": (
            "A man lost in the past.\n"
        ),
        "race": "Human",
        "class": "President",
        "level": 1,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": False,
    },
        "Steve": {
        "name": "Steve",
        "key_words": ("Steve"),
        "room_description": "&GSteve&N stands here.",
        "description": (
            ".\n"
        ),
        "race": "Minecraft",
        "class": "Steve",
        "level": 1000000000000000000000,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": True,
    }
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)