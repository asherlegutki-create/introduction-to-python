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
     2: Room(
        {
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
