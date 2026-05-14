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
            "name": "Garden of Eden",
            "description": "There is a huge garden streching for miles.There is a &Gtree&N in the middle of the Garden.\n God is watching over his creation.",
            "indoors": False,
            "terrain": "rolling grass hills",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "south", "roomId": 5},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 6},
                {"direction": "down", "roomId": 7},
            ],
            "objects": [
                O.spawn("Banana"),
                O.spawn("green leaf"),
                O.spawn("The Fruit"),
            ],
            "mobs": [
                M.spawn("Adam"),
                M.spawn("Eve"),
                M.spawn("Slippery Serpant")],  # two independent students
        }
    ),
2: Room(
        {
            "number": 2,
            "name": "Jericho",
            "description": "This is a city with a huge wall going around it to protect it.",
            "indoors": False,
            "terrain": "grass plane",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "south", "roomId": 5},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 6},
                {"direction": "down", "roomId": 7},
            ],
            "objects": [
                O.spawn("The Horn"),
            ],
            "mobs": [],  # two independent students
        }
    ),
}
