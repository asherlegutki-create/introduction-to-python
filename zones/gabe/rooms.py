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
            "name": "&WThe &yc&Yh&N&ye&Ye&N&ys&Ye&N Layer&N",
            "description": "&WYou are in the &Ycheese&N &Wlayer of the&N &yw&Go&N&yr&Gl&N&yd.\n &N&yc&Yh&N&ye&Ye&N&ys&Ye&N &Wis everywhere, in all shapes and sizes.&N\n &WThe air smells &N&rstrongly &Wof &yc&Yh&N&ye&Ye&N&ys&Ye&N,&W and you can see little&N &ybits &Wof it floating in the air.&N\n\n",
            "indoors": False,
            "terrain": "cheese",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 1},
            ],
            "objects": [
                O.spawn("cheese wheel"),
                O.spawn("toy cheese"),
            ],
            "mobs": [M.spawn("the cheese monster"), M.spawn("the cheez sniffer"), M.spawn("the cheese spirit")],
        },
    ),
}
