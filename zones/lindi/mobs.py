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
    "purple beanbag": {
        "name": " purple beanbag",
        "key_words": ("purple", "beanbag"),
        "room_description": "&wa &Pbeanbag&N sits in a corner.&N",
        "description": (
            "behold it is actually a monster.\n"
        ),
        "race": "Human",
        "class": "Student",
        "level": 19,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "killable": True,
        "wander": False
    },
    "grey beanbag": {
        "name": "grey beanbag",
        "key_words": ("grey", "beanbag"),
        "room_description": "&wa &Xbeanbag&N sits in a corner.&N",
        "description": (
            "you have been fooled, tis a monster!\n"
        ),
        "race": "Human",
        "class": "Student",
        "level": 19,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "killable": True,
        "wander": False
    },
    "Mr. Carlson": {
        "name": "Mr. Carlson",
        "key_words": ("carlson", "principal"),
        "room_description": "&wth principal, mr. carlson, stands ominously in the room.&N",
        "description": (
            "a .\n"
            "."
        ),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "killable": False,
        "wander": True
    },
    "Enemy": {
        "name": "Enemy",
        "key_words": ("Enemy"),
        "room_description": "&wa &Xdark&N figure stands with &rhate&N in his posture.&N",
        "description": (
            "this being is the schools strongest nemesis, he has fought with the attendants for centuries."
        ),
        "race": "Celestial",
        "class": "Enemy",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": True,
        "killable": True,
        "wander": True,
    },
    "The Beast of Geometry and Algebra": {
        "name": "The Beast of Geometry and Algebra",
        "key_words": ("beast", "geometry", "algebra"),
        "room_description": "&wa &Xdark&N and large dragon sits upon its spoil.&N",
        "description": (
            "its body is littered with shapes and letters, a steamy breath escapes its nose"
        ),
        "race": "Dragon",
        "class": "Enemy",
        "level": 60,
        "stats": [1000, 100, 1000, 1000, 1000, 100],
        "aggro": True,
        "killable": True,
        "wander": True,
    },
    "late work": {
        "name": "late work",
        "key_words": ("late", "work"),
        "room_description": "a late work monster scurries in the room.&N",
        "description": (
            "this is a large eight legged piece of paper, is hisses like a roach"
        ),
        "race": "Monster",
        "class": "Enemy",
        "level": 30,
        "stats": [50, 50, 50, 50, 50, 50],
        "aggro": True,
        "killable": True,
        "wander": True,
    },
    "malcom": {
        "name": "malcom",
        "key_words": ("malcom"),
        "room_description": "malcom sits near the closet.&N",
        "description": (
            "malcom is a small lego man, made of the more unusual of legos"
        ),
        "race": "Lego",
        "class": "Peaceful",
        "level": 50,
        "stats": [50, 50, 50, 50, 50, 50],
        "aggro": False,
        "killable": False,
        "wander": False,
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)