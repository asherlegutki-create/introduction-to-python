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
            "name": "&wDark Bramble Woods",
            "description": "A foggy woods with brambles scattered about.",
            "indoors": False,
            "terrain": "grassy",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
            ],
            "objects": [
                O.spawn("Brumplin husk"),
            ],
            "mobs": [M.spawn("Brumplin")],  # two independent students
        }
    ),
}
