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
            "description": "The Front doors is the entrance to the school. There are two doors that open in. These doors may or may not be locked for safety./n  west is the office, east is the wall, south is the parking lot,up is the exit out of my rooms, and down is carpet.",
            "indoors": False,                        
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "up", "roomId": 99002, "external": True}
                
            ],
            "objects": [
              #  O.spawn(""),
              #  O.spawn(""),
              #  O.spawn(""),
            ],
            "mobs": [
               # M.spawn("") ,
               # M.spawn(""),],  # two independent students
            ],
        }
    ),
2: Room(
        {
            "number": 2,
            "name": "Hallway",
            "description": "This hallway is one of many and leads to the bathrooms, teacher lounge ,office,and janitors closet #1./n West is the office north is still same hallway, east is the wall, up is ceiling, down is the floor.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "west", "roomId": 3},
                {"direction": "north", "roomId": 4},
            ],
            "objects": [
              #  O.spawn(""),
              # O.spawn("")
            ],
            "mobs": [  
                #M.spawn("") ,
                #M.spawn(""),
                #M.spawn("")
            ],  
        }
    ),
3: Room(
        {
            "number": 3,
            "name": "Office",
            "description": "This is the office where Mrs.stacey spends most of the day. To the west again is Mr.Carlson's office, east is the hallway,",
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
