"""
zones.the_void.rooms
────────────────────
Room definitions for The Void zone.  Vnum range: 1 – 99.

Each room entry calls O.spawn() / M.spawn() to place fresh object and mob
instances.  Calling spawn() twice places two independent copies, so loot
or damage on one never affects the other.

Exit roomIds must match vnums defined here or in another loaded zone.
"""

from ashenmoor.world import Room
from . import objects as O
from . import mobs as M

ROOMS: dict[int, Room] = {
    1: Room(
        {
            'number': 1,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Ebony Cleaver"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ),
     2: Room(
        {
            'number': 2,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 3: Room(
        {
            'number': 3,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 4: Room(
        {
            'number': 4,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 5: Room(
        {
            'number': 5,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 6: Room(
        {
            'number': 6,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 7: Room(
        {
            'number': 7,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 8: Room(
        {
            'number': 8,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 9: Room(
        {
            'number': 9,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 10: Room(
        {
            'number': 10,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 11: Room(
        {
            'number': 11,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 12: Room(
        {
            'number': 12,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 13: Room(
        {
            'number': 13,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 14: Room(
        {
            'number': 14,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 15: Room(
        {
            'number': 15,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 16: Room(
        {
            'number': 16,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 17: Room(
        {
            'number': 17,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 18: Room(
        {
            'number': 18,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 19: Room(
        {
            'number': 19,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ), 20: Room(
        {
            'number': 20,
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin Seed"),
            ],
            "mobs": [
                M.spawn("Brumplin Minor"),
                M.spawn("Brumplin Alpha")
            ],  # two independent students
        }
    ),
}
