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
            "number": 14,
            "name": "Crystal Caverns",
            "description": "&WIt is a&N dark &Wcave with minimal light coming off of the luminescent&N &Ccrystals&N.\nThe &Ccrystals&N are of &rv&ga&Cr&Bi&Ro&Yu&Gs&N &Wcolors&N",
            "indoors": True,
            "terrain": "rock",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 3},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 2},
                {"direction": "up", "roomId": 3},
                {"direction": "down", "roomId": 2},
            ],
            "objects": [
                O.spawn("Raptors claw"),
            ],
            "mobs": [M.spawn("Green Nessie")],  # two independent students
        }
    ),
}
