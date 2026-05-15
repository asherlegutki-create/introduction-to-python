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

    "Adam": {
        "name": "Adam",
        "key_words": ("Adam"),
        "room_description": "Adam is standing around animals nameing each one.",
        "description": ( "Adam is the first man. \n He has been givin the job of taking care of the earth. He is wearing nothing because he doesn't know what is right from wrong."),
        "race": "Human",
        "class": "Male",
        "level": 7,
        "stats": [71, 75, 80, 84, 79, 73],
        "aggro": False,
        "wander": False,
    },
    "Eve": {
        "name": "Eve",
        "key_words": ("Eve"),
        "room_description": "Eve is standing here talking to a serpent.",
        "description": ( "Eve is the first woman. \n She has been givin the job of taking care of the earth. She is wearing nothing because she doesn't know what is right from wrong."),
        "race": "Human",
        "class": "Female",
        "level": 7,
        "stats": [70, 65, 81, 74, 89, 93],
        "aggro": False,
        "wander": False,
    },
     "Slippery Serpant": {
        "name": "Slipery Serpent",
        "key_words": ("Slippery","Serpant"),
        "room_description": "The Serpant is resting on the end of the tree branch Tricking the woman.",
        "description": ( "Satan takes the form of this serpant. \n The serpant is lying to the woman."),
        "race": "Snake",
        "class": "Male",
        "level": 10,
        "stats": [80, 90, 80, 84, 80, 0],
        "aggro": False,
        "wander": False,
    }, 
     "Joshua": {
        "name": "Joshua",
        "key_words": ("Joshua"),
        "room_description": "Joshua is kneeling here praying to God.",
        "description": ( "Joshua was chosen by God after moses died."),
        "race": "Human",
        "class": "Male",
        "level": 19,
        "stats": [90, 90, 80, 84, 80, 100],
        "aggro": False,
        "wander": False,
    }, 
    "Israelite": { 
        "name": "Israelite",
        "key_words": ("ISraelite"),
        "room_description": "This Israelite wanders around the room.",
        "description": ( "The Israelite is one of the men that walked around the city of Jericho."),
        "race": "Human",
        "class": "Female",
        "level": 40,
        "stats": [70, 60, 70, 64, 70, 100],
        "aggro": False,
        "wander": False,
},
 "Trumpet Player": { 
        "name": "Bob",
        "key_words": ("Bob","Trumpet","Player"),
        "room_description": "The Trumpet in his hand Bob stands here ready to play his trumpet for God.",
        "description": ( "This man got to play his trumpet on the last lap around jericho. The city fell down slowly after."),
        "race": "Human",
        "class": "male",
        "level": 3,
        "stats": [80, 90, 80, 44, 60, 5],
        "aggro": False,
        "wander": False,
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)