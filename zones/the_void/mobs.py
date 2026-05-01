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
        "name":             "a wandering student",
        "key_words":        ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.\n"
            "Or possibly just lost."
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
        "my_friend": {
        "name":             "a wandering student",
        "key_words":        ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.\n"
            "Or possibly just lost."
        ),
        "race":     "Human",
        "class":    "Student",
        "level":    1,
        "stats":    [60, 65, 60, 80, 70, 75],
        "aggro":    False,
        "wander":   True,
    },

    "void_guardian": {
        "name":             "the Void Guardian",
        "key_words":        ("guardian", "void"),
        "room_description": (
            "&XThe &+WVoid Guardian&N&X stands watch, unblinking.&N"
        ),
        "description": (
            "&XA towering figure of condensed darkness.\n"
            "Its eyes are two cold points of &+Wwhite light&N&X.&N"
        ),
        "race":     "Unknown",
        "class":    "Guardian",
        "level":    50,
        "stats":    [120, 100, 130, 90, 110, 50],
        "aggro":    False,
        "wander":   False,
        "position": "standing",
    },

}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
