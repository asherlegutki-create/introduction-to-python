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
            "name": "&cfih land&N",
            "description": "It is a land of wonderful fih",
            "indoors": False,
            "terrain": "water",
            "exits": [
                {"direction": "east", "roomId": 99002, "external": True},
            ],
            "objects": [
                O.spawn("tennis_racket"),
            ],
            "mobs": [M.spawn("fabulous_fih")
            ],
        }
    ),
}
