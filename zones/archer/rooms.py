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
            "description": "A heavily fortified mansion, your currently surrounded by Illriggers, the exit is due &BSouth&N",
            "indoors": True,
            "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 99001, "external": True},
                {"direction": "east", "roomId": 3},
                {"direction": "west", "roomId": 4},
                {"direction": "up", "roomId": 6},
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
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Chest Room (entrance)",
                "description": "A giant room full of chests filled with treasures beyond your wildest dreams /nIt is guarded by an &RIllrigger&N",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "north", "roomId": 16},
                    {"direction": "south", "roomId": 1},
                    {"direction": "east", "roomId": 4},
                    {"direction": "west", "roomId": 5},
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
                    {"direction": "west", "roomId": 1}
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
                "description": "A giant room filled with books and shelves",
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
                    O.spawn("Copper Sword"),
                ],
            }
        ),
        6: Room(
            {
                "number": 6,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Hallway Seg 1",
                "description": "&BEast&N is the room with the giant cat statue, &BSouth&N is another library, &BWest&N is another guest room and so is &BNorth&N",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "east", "roomId": 7},
                    {"direction": "south", "roomId": 8},
                    {"direction": "West", "roomId": 9},
                    {"direction": "north", "roomId": 10},
                    {"direction": "down", "roomId": 1},
                ],
                
            }
        ),
        7: Room(
            {
                "number": 7,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Cat Statue Room",
                "description": "A giant statue of a cat made of wool, totally not creepy at all",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "west", "roomId": 6},
                ],
                
            }
        ),
        8: Room(
            {
                "number": 8,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Library #2",
                "description": "another library with more books, endless amount of books and shelves",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "north", "roomId": 6},
                ],
                "mobs": [ 
                    M.spawn("&MIllrigger Mage&N"),
                ],
            }
        ),
        9: Room(
            {
                "number": 9,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Guest Room #2",
                "description": "A cozy room with &Mcozy beds&N, stay as long as you need...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "east", "roomId": 6},
                ],
                
            }
        ),
        10: Room(
            {
                "number": 10,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Guest Room #2",
                "description": "A cozy room with &Gcozy beds&N, stay as long as you need...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "south", "roomId": 6},
                    {"direction": "up", "roomId": 11},
                ],
                
            }
        ),
        11: Room(
            {
                "number": 11,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor (Secret Room!)",
                "description": "look! you found a secret room! but it doest look like your alone...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "down", "roomId": 10},
                    {"direction": "north", "roomId": 12},
                    {"direction": "south", "roomId": 13},
                    {"direction": "east", "roomId": 14},
                    {"direction": "west", "roomId": 15},
                ],
                "mobs": [ 
                    M.spawn("Zombie"),
                    M.spawn("Zombie"),
                    M.spawn("Zombie"),
                ],
            }
        ),
        12: Room(
            {
                "number": 12,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor (Secret Room!)",
                "description": "just a room with a few slimes...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "south", "roomId": 11},
                ],
                "mobs": [ 
                    M.spawn("&MPink Slime&N"),
                    M.spawn("&MPink Slime&N"),
                    M.spawn("&MPink Slime&N"),
                ],
            }
        ),
        13: Room(
            {
                "number": 13,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor (Secret Room!)",
                "description": "just an empty room...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "north", "roomId": 11},
                ],
                "mobs": [ 
                    M.spawn("&BBlue Slime&N"),
                ],
                "objects": [
                    O.spawn("Sack of the Void"),
                ],
            }
        ),
        14: Room(
            {
                "number": 14,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor (Secret Arena Room!)",
                "description": "its arena night, its time for your &RBoss Battle&N...",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "east", "roomId": 11},
                ],
                "mobs": [ 
                    M.spawn("&YKing &MSlime&N"),
                    M.spawn("Zombie"),
                    M.spawn("Zombie"),
                    M.spawn("&GGreen Slime&N"),
                    M.spawn("&GGreen Slime&N"),
                ],
            }
        ),
        15: Room(
            {
                "number": 15,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor (Secret Room!)",
                "description": "hey look! more &GX&MP&N!",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "west", "roomId": 11},
                ],
                "mobs": [ 
                    M.spawn("&MPink Slime&N"),
                    M.spawn("&MPink Slime&N"),
                    M.spawn("&GGreen Slime&N"),
                    M.spawn("&BBlue Slime&N"),
                ],
            }
        ),

        16: Room(
            {
                "number": 16,
                "name": "&xW&yo&xo&yd&xl&xa&yn&xd&N Manor Chest Room",
                "description": "A giant room full of chests filled with treasures beyond your wildest dreams /nIt is guarded by an &RIllrigger&N",
                "indoors": True,
                "terrain": "floors, rooms, stairs, hallways, ceiling, and walls",
                "exits": [
                    {"direction": "south", "roomId": 2},
                     ],
            "mobs": [ 
                M.spawn("Cap"),
                ],
             "objects": [ 
                 O.spawn("Spruce Chest"),
                 O.spawn("Spruce Chest"),
                 O.spawn("Spruce Chest"),
                ],
            }
        ),
}