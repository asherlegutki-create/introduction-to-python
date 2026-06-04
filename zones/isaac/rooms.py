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
            "number": 1,
            "name": "&gOregon&N",
            "description": (
                "Oregon",
                "This room is covered in green trees.",
                "Abundant grass and moss is soft under your feet.",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 3},
                {"direction": "west", "roomId": 11},
                {"direction": "down", "roomId": 99003, "external": True},
            ],
            "objects": [
                O.spawn("duckzooka"),
            ],
            "mobs": [
                M.spawn("escbaalion"),
                M.spawn("unicorn_blob"),
            ],
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "&bWater&N",
            "description": (
                "&BWATER. . . WATER EVERYWHERE. . .&N\n"
                "&BYOU ARE SWIMMING IN AN ENDLESS NOTHING. . .&N\n"
                "&BALL YOU SEE IS BLUE. . .&N                                                                                                                                      &X<><&N\n"
                "&BWATER. . . WATER EVERYWHERE. . .&N\n"
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 2},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 2},
                {"direction": "up", "roomId": 12},
                {"direction": "down", "roomId": 2},
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "Washington",
            "description": (
                "Washington",
                "",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "south", "roomId": 1},
                # {"direction": "east", "roomId": 2},
                # {"direction": "west", "roomId": 3},
                # {"direction": "up", "roomId": 1},
                # {"direction": "down", "roomId": 2},
            ],
            "objects": [O.spawn("street_lamp")],  # make new object later
            "mobs": [
                M.spawn("unicorn_blob"),
                M.spawn("unicorn_blob"),
                M.spawn("unicorn_blob"),
            ],
        }
    ),
    11: Room(
        {
            "number": 11,
            "name": "ROOM_<11>",
            "description": ("Metal."),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "east", "roomId": 1},
                {"direction": "south", "roomId": 12},
            ],
            "objects": [
                O.spawn("metal_pipe"),
                O.spawn("gear"),
                O.spawn("gear"),
            ],  # objects include metal shards,
            "mobs": [
                M.spawn("glitch"),
            ],
        }
    ),
    12: Room(
        {
            "number": 12,
            "name": "Unnamed",
            "description": ("A &ywooden trap door&N on the floor seems inviting."),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 11},
                # {"direction": "west", "roomId": 4},
                {"direction": "down", "roomId": 2},
            ],
            "objects": [],
            "mobs": [],
        }
    ),
}
