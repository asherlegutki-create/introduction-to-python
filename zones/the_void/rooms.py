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
            "name": "The Void",
            "description": "There is nothing here but the sound of rushing of wind.\nWe are waiting for the Spirit of God to move over it.",
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 1},
            ],
            "mobs": [M.spawn("escbaalion")],  # two independent students
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "Not The Void",
            "description": "You left\nSo sorry",
            "indoors": False,
            "terrain": "no ground",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
            ],
            "objects": [
                O.spawn("silken_sack"),
                O.spawn("windsong"),
            ],
            "mobs": [
                M.spawn("wandering_student"),
                M.spawn("wandering_student"),  # two independent students
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "Not the Not The Void",
            "description": "Now you stuck",
            "indoors": False,
            "terrain": "no ground",
            "exits": [],
            "objects": [O.spawn("red_marker"), O.spawn("green_marker")],
        }
    ),
}
