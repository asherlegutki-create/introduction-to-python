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
            "name": "&CTierra del Camino&N",
            "description": "The Land of the Way.\nYou will soon learn of the Way.",
            "indoors": False,
            "terrain": "A flat expanse of mostly flat ground",
            "exits": [
                {"direction": "north", "roomId": 99004, "external": True},
            ],
            "objects": [
                O.spawn("mr_mob_sword"),
            ],
            "mobs": [M.spawn("mr_mob")],  # two independent students
        }
    ),
}
