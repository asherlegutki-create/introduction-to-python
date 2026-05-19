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
            "description": "There is a weird feeling in the air, almost a feeling of doom. The ground moves slightly when you walk, as if it is floating.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
                O.spawn("sword_that_seals_the_darkness"),
            ],
            "mobs": [
                M.spawn("void_dragon"),
                M.spawn("shadow_gremlin"),
                M.spawn("dark_mage"),
            ],  # two independent students
        }
    ),
}
