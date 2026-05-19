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
            "name": "&gThe Seomra&N",  # Irish for Room
            "description": (
                "The floor is covered with ripped-up &Yyellow warning tape&N and littered with &ytraffic cones&N.\n"
                "The room is shaped like a triangle, painted &Ggreen&N with two &xiron doors&N on the far walls.\n"
                "A &ywooden trap door&N on the floor seems inviting."
            ),
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 3},
                {"direction": "west", "roomId": 4},
                {"direction": "down", "roomId": 2},
            ],
            "objects": [
                O.spawn("traffic_cone"),
                O.spawn("traffic_cone"),
                O.spawn("traffic_cone"),
                O.spawn("traffic_cone"),
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
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 2},
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "This is a Random Room",
            "description": "Hi.",
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
}
