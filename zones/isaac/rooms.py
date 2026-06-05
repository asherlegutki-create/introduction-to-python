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
            "name": "&WNW&N &GOregon&N",
            "description": (
                "This area is covered in &Ggreen trees&N.",
                "&GAbundant grass&N &wand&N &Gmoss&N is soft under your feet.",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "south", "roomId": 2},
                {"direction": "east", "roomId": 3},
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
            "name": "&WSW&N &GOregon&N",
            "description": (
                "This area is covered in &Ggreen trees&N.",
                "&GAbundant grass&N &wand&N &Gmoss&N is soft under your feet.",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "east", "roomId": 4},
            ],
            "objects": [
                # O.spawn(),
            ],
            "mobs": [
                M.spawn("duck"),
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "&WNE&N &GOregon&N",
            "description": (
                "There are no trees here.",
                "There is sand, but it's &Ggreen&N for some reason...",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "west", "roomId": 1},
                {"direction": "south", "roomId": 4},
            ],
            "objects": [O.spawn("street_lamp")],  # make new object later
            "mobs": [
                M.spawn("unicorn_blob"),
                M.spawn("unicorn_blob"),
                M.spawn("unicorn_blob"),
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "&WSW&N &GOregon&N",
            "description": (
                "There are no trees here.",
                "There is sand, but it's &Ggreen&N for some reason...",
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "west", "roomId": 2},
                {"direction": "north", "roomId": 3},
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
    # 2: Room(
    #    {
    #        "number": 2,
    #        "name": "&bWater&N",
    #        "description": (
    #            "&BWATER. . . WATER EVERYWHERE. . .&N\n"
    #            "&BYOU ARE SWIMMING IN AN ENDLESS NOTHING. . .&N\n"
    #            "&BALL YOU SEE IS BLUE. . .&N                                                                                                                                      &X<><&N\n"
    #            "&BWATER. . . WATER EVERYWHERE. . .&N\n"
    #        ),
    #        "indoors": False,
    #        "terrain": "no ground",
    #        "exits": [
    #            {"direction": "north", "roomId": 2},
    #            {"direction": "south", "roomId": 2},
    #            {"direction": "east", "roomId": 2},
    #            {"direction": "west", "roomId": 2},
    #            {"direction": "up", "roomId": 12},
    #            {"direction": "down", "roomId": 2},
    #        ],
    #    }
    # ),
}
