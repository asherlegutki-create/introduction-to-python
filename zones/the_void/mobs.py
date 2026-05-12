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
    "wandering_student": {
        "name": "a wandering student",
        "key_words": ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.\n"
            "Or possibly just lost."
        ),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
    "escbaalion": {
        "name": "Escbaalion",  # The c is silent
        "key_words": ("Escbaalion"),
        "room_description": "&gEscbaalion&N &wlicks his eyeball.&N",
        "description": (
            "A humanoid lizard. He is &gdark-green&N, and has a short\n"
            "&Ccyan sail&N that runs from the top of his head to the end of his tail.\n"
            "He wears an almost &Xblack cloak&N, but wears &rno&N pants.\n"
            "A &ybrown leather satchel&N is slung over his shoulder.\n"
            "Only &ghe&N knows what is inside his &ybag&N. . . ."
        ),
        "race": "Lizaroid",
        "class": "Sorcerer",
        "level": 10,
        "stats": [80, 50, 200, 90, 90, 70],
    },
    "void_dragon": {
        "name": "Inanis the Void Dragon",
        "key_words": ("inanis"),
        "room_description": "A large &Mdragon&N stands here looking around &Ragitated&N.",
        "description": (
            "This large purple and black dragon seems to have a shroud of darkness around it. Its eyes appear to be pits of blackness"
        ),
        "race": "Dragon",
        "class": "Watcher",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": True,
    },
    "Lucas": {
        "name": "Lucas",
        "key_words": ("Lucas"),
        "room_description": "&wLucas meanders about aimlessly.&N",
        "description": ("A student with a faraway look,\n" "Or  just lost."),
        "race": "Elf",
        "class": "Shortone",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
    "Mr. Carlson": {
        "name": "Mr. Carlson",
        "key_words": ("Mr.", "Carlson"),
        "room_description": "&g Mr. Carlson is taking to a student in the hall.&N",
        "description": (
            "The principal of the school. \n"
            "Very tall. He is wearing a blue jacket with a tie that has elk on it."
        ),
        "race": "Human",
        "class": "Principal",
        "level": 70,
        "stats": [71, 75, 80, 84, 79, 73],
        "aggro": True,
        "wander": False,
    },
    "Red kobold": {
        "name": "Jremblen",
        "key_words": ("kobold"),
        "room_description": "a &rkobold&N stands here, looking through a &ybag&N full of &gm&Go&gs&Gs.&N",
        "description": (
            "A small &rkobold&n stands here looking through a &ybag&N, it seems to be filled with various different types of &gm&Go&gs&Gs&N.\n"
            "His scales are &rgarnet red&N."
        ),
        "race": "Humanoid",
        "class": "rouge",
        "level": 1,
        "stats": [40, 50, 40, 30, 20, 40],
        "aggro": False,
        "wander": False,
    },
    
    "weasel": {
        "name": "weasel",
        "key_words": ("weasel"),
        "room_description": "&wA &YWeasel&N floats here randomly.&N",
        "description": ("
            "It is very soft and chubby.\n",
            "It seems like it standing on some cheese."
        ),
        "race":     "animal",
        "class":    "weasel",
        "level":    50,
        "stats":    [60, 100, 60, 100, 75, 100],
        "aggro":    False,
        "wander":   False,
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
    "wandering_teacher": {
        "name": "a wandering teacher",
        "key_words": ("teacher", "wandering"),
        "room_description": "&wA wandering teacher roams the halls in search of loose students.&N",
        "description": (
            "A teacher with a focused look, awaiting an opportunity to dish out detention.\n"
            "Or possibly just avoiding teacher duties."
        ),
        "race": "Human",
        "class": "Teacher",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
    "my_friend": {
        "name": "a wandering student",
        "key_words": ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "race": "non-humanoid",
        "class": "",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": True,
        "wander": False,
    },
    "void_guardian": {
        "name": "the Void Guardian",
        "key_words": ("guardian", "void"),
        "room_description": ("&XThe &+WVoid Guardian&N&X stands watch, unblinking.&N"),
        "description": (
            "&XA towering figure of condensed darkness.\n"
            "Its eyes are two cold points of &+Wwhite light&N&X.&N"
        ),
        "race": "Unknown",
        "class": "Guardian",
        "level": 50,
        "stats": [120, 100, 130, 90, 110, 50],
        "aggro": False,
        "wander": False,
        "position": "standing",
    },
    "Citadel Guard": {
        "name": "Citadel Guard",
        "key_words": ("Guard", "Citadel"),
        "room_description": "&wA An armed guard wanders here.&N",
        "description": (
            "The Kings Guard looks very protective!\nHe seems on his lunch break"
        ),
        "race": "Hexblade",
        "class": "Guard",
        "level": 50,
        "stats": [100, 100, 100, 100, 1000, 100],
        "aggro": False,
        "wander": False,
    },
    "Adam Sandler": {
        "name": "Adam Sandler",
        "key_words": ("Adam", "Sandler"),
        "room_description": "&wAdam Sandler wanders about aimlessly.&N",
        "description": (
            "A comedian with a faraway look, clearly lost in thought.\n"
            "Or possibly just drunk."
        ),
        "race": "Human",
        "class": "Comedian",
        "level": 10,
        "stats": [0, 16, 60, 32, 7, 7],
        "aggro": True,
        "wander": True,
    },

    "the cheese monster": {
        "name": "the cheese monster",
        "key_words": ("cheese", "monster"),
        "room_description": "&Wthe&N &yc&Yh&N&ye&Ye&N&ys&Ye&N &bmonster &Wsleeps here&N",
        "description": (
            "a cheese monster thinking into space "
            "most likely thinking about &msleep..."
        ),
        "race": "cheese",
        "class": "scary guy",
        "level": "29",
        "stats": [46, 59, 65, 55, 75, 80],
        "aggro": False,
        "wander": False,
    },

    "Sand Puma": {
        "name": "Sand Puma",
        "key_words": ("puma"),
        "room_description": "&wA sand puma aimlesly being taken into the quick sand.&N",
        "description": ("rockyish sand color and yellow.\n" "puma +."),
        "race": "pumaish",
        "class": "sandy",
        "level": 1,
        "stats": [99, 68, 71, 87, 81, 100],
        "aggro": False,
        "wander": True,
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
