"""
zones.the_void.rooms
────────────────────
Room definitions for The Void zone.  Vnum range: 1 – 13.

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
            "name": "&BThe Farlands&N",
            "description": "Lots of repeating glitched &Gterrian&N.",
            "indoors": True,
            "terrain": "ground",
            "exits": [
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 1},
                {"direction": "down", "roomId": 99005, "external": True},
            ],
            "objects": [
                O.spawn("Nuke_Shot"),
            ],
            "mobs": [M.spawn("Steve")],  # two independent students
        }
    ),

    2: Room(
        {
            "number": 2,
            "name": "&BThe Fartherlands&N",
            "description": "A &Gland&N beyond the &BFarlands&N with even crazier &Gterrian&N.",
            "indoors": False,
            "terrain": "ground",
            "exits": [
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 2},
                {"direction": "down", "roomId": 99005, "external": True},
            ],
            "objects": [
                O.spawn("Stab_Shot"),
            ],
            #"mobs": [M.spawn("Steve")],  # two independent students
        }
    ),

}
