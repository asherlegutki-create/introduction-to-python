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
<<<<<<< HEAD:zones/Lindi/mobs.py
    "Gods angel": {
        "name": "Gods angel",
        "key_words": ("angel"),
        "room_description": "&wA bright and mighty being sings for the Lord.&N",
        "description": (
            "An angel of grace and light, here to bring the good news.\n"
        ),
        "race": "angel",
        "class": "holy",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
=======
    "mob_template": {
        "name": "",
        "key_words": (),
        "room_description": "",
        "description": (),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
>>>>>>> 11e70b33019f967e2fc9da798de5af78ddcf47f4:zones/sample/mobs.py
        "aggro": False,
        "wander": True,
    }
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)