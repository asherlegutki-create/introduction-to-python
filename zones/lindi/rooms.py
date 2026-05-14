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
            "name": "room j",
            "description": "the room is filled with tables and chairs.\n the interactive board glows softly in the front",
            "indoors": True,
            "terrain": "ground",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "west", "roomid": 1},
            ],
            "objects": [
                O.spawn("pencil"),
                O.spawn("whiteboard_marker"),
            ],
            "mobs": [M.spawn("wandering_student")],  # two independent students
        }
    ),
   2: Room(
        {
            "number": 2,
            "name": "room h",
            "description": "a well decorated room, filled with historical artifacts.",
            "indoors": True,
            "terrain": "ground",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
            ],
            "objects": [
                O.spawn("Mrs.Allisons_syth"),
            ],
            "mobs": [M.spawn("fellow_student")],  # two independent students
        }
    ), 
}
