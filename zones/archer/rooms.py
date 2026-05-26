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
            "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor",
            "description": "A heavily fortified mansion, your currently surrounded by Illriggers, the exit is due &Yeast&N",
            "indoors": True,
            "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 3},
                {"direction": "east", "roomId": 99002, "external": True},
                {"direction": "west", "roomId": 4},
            ],
            "mobs": [ 
                M.spawn("&MIllrigger Mage&N"),
                M.spawn("&RIllrigger Rogue&N"),
            ],
        }
    ),


    
    2: Room(
            {
                "number": 2,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Chest Room",
                "description": "A gaint room full of chests filled with treasures beyond your wildest dreams /nIt is guarded by an &RIllrigger&N",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "north", "roomId": 3},
                    {"direction": "south", "roomId": 1},
                    {"direction": "east", "roomId": 4},
                    {"direction": "west", "roomId": 5},
                ],
                "objects": [
                    O.spawn("Potion of Turtle Master"),
                ],
                "mobs": [ 
                    M.spawn("&RIllrigger Rogue&N"),
                ],
            }
        ),


    3: Room(
            {
                "number": 3,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Prison Room",
                "description": "a room full of empty cells except one, the one with the &yprisoner&N inside",
                "indoors": True,
                "terrain": "floors, cells, ceiling, and walls",
                "exits": [
                    {"direction": "north", "roomId": 1}
                ],
                "mobs": [ 
                    M.spawn("&yImprisoned Illrigger&N"),
                ],
            }
        ),
        4: Room(
            {
                "number": 4,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Library",
                "description": "A gaint room filled with books and shelves",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "south", "roomId": 1},
                ],
                "mobs": [ 
                    M.spawn("&MIllrigger Mage&N"),
                ],
            }
        ),
        5: Room(
            {
                "number": 5,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Guest Room",
                "description": "A cozy room with &Rcozy beds&N, stay as long as you need...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "south", "roomId": 2},
                ],
                 "objects": [
                    O.spawn("Potion of Strength II"),
                 ],
            }
        ),
}