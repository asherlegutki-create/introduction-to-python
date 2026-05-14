"""
zones.the_planes.rooms
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
        123: Room(
            {
            "number": 1,
            "name": "Room_template",
            "description": "its a room!",
            "indoors": True,
            "terrain": "ground  type",
            "exits": [
                {"direction": "north", "roomId": 123},
                {"direction": "south", "roomId": 123},
            ],
            "objects": [
                O.spawn("object_template"),
                O.spawn("Item_template"),
            ],
            "mobs": [M.spawn("mob_template")]
        }
     ),
     1: Room(
           {
            "number": 2,
            "name": "The Withered-Rose Tavern ",
            "description": "An average &yroadside tavern&N, it sits at the edge of a &gconiferous forest&N.\nThe interior is warmed by a large &rfireplace&N on the left wall and the scents of &mvarious&N &Yalcohols&N waft about the room.&N",
            "indoors": True,
            "terrain": "wooden floor",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 2},
            ],
            "objects": [
                O.spawn("Large_Orange_Cat"),
                O.spawn("Assorted_Bottles__Full"),
            ],
            "mobs": [M.spawn("fanciful_bard")]
        },
        
    ),
}
