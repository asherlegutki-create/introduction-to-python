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
    "shadow_gremlin": {
        "name": "a shadow gremlin",
        "key_words": ("shadow", "gremlin", "thing"),
        "room_description": "a small black thing scurries about",
        "description": ("This small creature is called a &Xshadow gremlin&N. It is almost completely black except for its tiny white eyes"),
        "race": "Gremlin",
        "class": "",
        "level": 15,
        "stats": [75, 75, 75, 75, 75, 75],
        "aggro": False,
        "wander": False,
    },
        "void_dragon": {
        "name": "Inanis the Void Dragon",
        "key_words": ("inanis", "void", "dragon"),
        "room_description": "&mInanis&N the &XVoid&N &mDragon&N stands here looking &Ragitated&N.",
        "description": ("This large &Mpurple&N and &Xblack&N dragon seems to have a shroud of &Xdarkness&N around it. Its eyes appear to be pits of &Xblackness&N"),
        "race": "Dragon",
        "class": "Watcher",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": False,
    },
        "dark_mage": {
            "name": "a dark mage",
            "key_words": ("dark", "mage"),
            "room_description": "A &bdark mage&N cloaked in &Xblack&N stands here at attention. It looks angry, so you look away as to not anger it further.",
            "description": ("This powerful looking being is a henchman of the &rGreat Darkness&N."),
            "race": "Fallen Elf",
            "class": "Mage",
            "level": 30,
            "stats": [90, 90, 90, 90, 90, 90],
            "aggro": False,
            "wander": False,
    },
        "dark_glob": {
            "name": "a dark glob",
            "key_words": ("dark", "glob"),
            "room_description": "A &bdark glob&N hops around, making a gross sound.",
            "description": ("The blob is entirely a &gstrange&N, &mpurplish goo."),
            "race": "Slime",
            "class": "Jump",
            "level": 5,
            "stats": [80, 80, 80, 80, 80, 80],
            "aggro": False,
            "wander": False,
    },
        "falcon_spy": {
            "name": "a falcon spy",
            "key_words": ("falcon", "spy"),
            "room_description": "A &Xdarkly colored&N falcon sits alert.",
            "description": ("This bird was created to collect information for the &rGreat Darkness&N."),
            "race": "Bird",
            "class": "Watcher",
            "level": 20,
            "stats": [90, 90, 90, 90, 90, 90],
            "aggro": False,
            "wander": False,
    },
}


# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)