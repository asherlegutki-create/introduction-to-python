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
    "escbaalion": {
        "name": "&gEscbaalion&N",  # The c is silent
        "key_words": ("Escbaalion", "lizard", "lizardman"),
        "room_description": "&gEscbaalion&N licks his eyeball.",
        "description": (
            "(The 'c' is silent)\n"
            "A humanoid lizard. He is &gdark-green&N, and has a short\n",
            "&Ccyan sail&N that runs from the top of his head to the end of his tail.\n",
            "He wears an almost &Xblack cloak&N, but wears &Rno&N pants.\n",
            "A &ybrown leather satchel&N is slung over his shoulder.\n",
            "Only &ghe&N knows what is inside his &ybag&N. . . .",
        ),
        "race": "Lizaroid",
        "class": "Sorcerer",
        "level": 2,
        "stats": [80, 50, 200, 90, 90, 70],
        "aggro": False,
        "wander": False,
        "killable": True,
    },
    "unicorn_blob": {
        "name": "&MUnicorn Blob&N",
        "key_words": ("unicorn", "blob"),
        "room_description": "&MUnicorn Blob&N wanders without a care in the world.",
        "description": (
            "It is a &Mpurple blob of&N &mjelly&N.\n",
            "A &Ygolden unicorn horn&N protrudes from its forehead.\n",
            "Its eyes are cute and sparkly and &Xsouless&N.\n",
            "\n",
            "\n",
            "\n",
            "I wonder what it tastes like...?",
        ),
        "race": "Slime",
        "class": "",
        "level": 1,
        "stats": [70, 50, 160, 20, 20, 100],
        "aggro": False,
        "wander": True,
        "killable": True,
    },
}

spawn = make_spawner(TEMPLATES, lambda: Mob)
