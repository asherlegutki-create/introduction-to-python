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
            "name": "The Front Doors",#this is the Front doors
            "description": "The Front doors is the entrance to the school. There are two doors that open in. These doors may or may not be locked for safety./n  left is the office, right is the wall, south is the",
            "indoors": False,                        
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "west", "roomId": 99002, "external": True}
                
            ],
            "objects": [
              #  O.spawn(""),
              #  O.spawn(""),
              #  O.spawn(""),
            ],
            "mobs": [],
               # M.spawn("") ,
               # M.spawn(""),],  # two independent students

        }
    ),
2: Room(
        {
            "number": 2,
            "name": "",
            "description": "",
            "indoors": False,
            "terrain": "",
            "exits": [
                {"direction": "east", "roomId": 1},
                {"direction": "north", "roomId": 3},
            ],
            "objects": [
              #  O.spawn("The Horn"),
              # O.spawn("Tunic")
            ],
            "mobs": [  
                #M.spawn("Joshua") ,
                #M.spawn("Israelite"),
                #M.spawn("Trumpet Player")
            ],  # two independent students
        }
    ),
3: Room(
        {
            "number": 3,
            "name": "",
            "description": ".",
            "indoors": True,
            "terrain": "",
            "exits": [
                {"direction": "south", "roomId": 2},
                {"direction": "north", "roomId": 4},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),
}
