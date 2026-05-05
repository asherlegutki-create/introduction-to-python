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
    "void_dragon": {
        "name": "Inanis the Void Dragon",
        "key_words": ("inanis"),
        "room_description": "A large &Mdragon&N stands here looking around &Ragitated&N.",
        "description": (
            "This large purple and black dragon seems to have a shroud of darkness around it. Its eyes appear to be pits of blackness"
        ),
        "race":     "Human",
        "class":    "Student",
        "level":    1,
        "stats":    [60, 65, 60, 80, 70, 75],
        "aggro":    False,
        "wander":   True,
    },
    "Mr. Carlson": {
        "name":             "Mr. Carlson",
        "key_words":        ("Mr.", "Carlson"),
        "room_description": "&g Mr. Carlson is taking to a student in the hall.&N",
        "description": (
            "The principal of the school. \n"
            "Very tall. He is wearing a blue jacket with a tie that has elk on it."
        ),
        "race":     "Human",
        "class":    "Principal",
        "level":    70,
        "stats":    [71, 75, 80, 84, 79, 73],
        "aggro":    True,
        "wander":   False,
    },
    "Red kobold": {
        "name":             "Jremblen",
        "key_words":        ("kobold"),
        "room_description": "a red kobold that is looking through a bag stands here.&N",
        "description": (
            "A kobold stands here looking through his bag, it it filled with several different types of moss.\n"
            "His scales are garnet red."
        ),
        "race":     "Humanoid",
        "class":    "rouge",
        "level":    1,
        "stats":    [40, 50 ,40, 30, 20, 40],
        "aggro":    False,
        "wander":   False,
    },
        "my_friend": {
        "name":             "a student",
        "key_words":        ("student", "friend"),
        "room_description": "&wA weanders about aimlessly.&N",
        "description": (
            "A student with a faraway look,\n"
            "Or  just lost."
        ),
        "race": "Elf",
        "class": "Shortone",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
    "Shrimpman": {
        "name":             "Shrimpman",
        "key_words":        ("shrimp"),
        "room_description": "&wA Shrimpman is backflipping.&N",
        "description": (
            "very pink.\n"
            "Shrimp."
        ),
        "race":     "humanoid",
        "class":    "monk",
        "level":    1,
        "stats":    [60, 65, 60, 80, 70, 75],
        "aggro":    False,
        "wander":   True,
    },
    "weasel": {
        "name":             "weasel",
        "key_words":        ("weasel"),
        "room_description": "&wA Weasel floats here randomly.&N",
        "description": (
            "It is very soft and chubby.\n"
            "It seems like it standing on some cheese."
        ),
        "race":     "Human",
        "class":    "Student",
        "level":    1,
        "stats":    [60, 65, 60, 80, 70, 75],
        "aggro":    False,
        "wander":   True,
    },

    "wandering_teacher": {
        "name":             "a wandering teacher",
        "key_words":        ("teacher", "wandering"),
        "room_description": "&wA wandering teacher roams the halls in search of loose students.&N",
        "description": (
            "A teacher with a focused look, awaiting an opportunity to dish out detention.\n"
            "Or possibly just avoiding teacher duties."
        ),
        "race":     "Human",
        "class":    "Teacher",
        "level":    1,
        "stats":    [60, 65, 60, 80, 70, 75],
        "aggro":    False,
        "wander":   True,
    },

    "my_friend": {
        "name":             "a wandering student",
        "key_words":        ("student", "wandering"),
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
<<<<<<< HEAD
    "Adam Sandler": {
        "name":             "Adam Sandler",
        "key_words":        ("Adam", "Sandler"),
        "room_description": "&wAdam Sandler wanders about aimlessly.&N",
        "description": (
            "A comedian with a faraway look, clearly lost in thought.\n"
            "Or possibly just drunk."
        ),
        "race":     "Human",
        "class":    "Comedian",
        "level":    10,
        "stats":    [0, 16, 60, 32, 7, 7],
        "aggro":    True,
        "wander":   True,
=======
    # kill=False — combat system refuses killing blow on this mob.
    "moted_pc": {
        "name": "Moted",
        "key_words": ("moted", "dwarf"),
        "room_description": "&wMoted the Dwarf is here.&N",
        "description": "A weathered Dwarven shaman. Best not to cross him.",
        "race": "Dwarf",
        "class": "Shaman",
        "level": 24,
        "stats": [88, 80, 80, 80, 80, 80],
        "aggro": False,
        "wander": False,
        "kill": False,
>>>>>>> f4af659054a31016cf2b6a834f0a41b7a144682f
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
