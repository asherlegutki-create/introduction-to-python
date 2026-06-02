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
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 3},
                {"direction": "east", "roomId": 9},
                {"direction": "west", "roomId": 4},
                {"direction": "down", "roomId": 99002, "external": True},
                {"direction": "up", "roomId": 8},
            ],
            "objects": [
                O.spawn('hanging_tree'),  
                O.spawn('ethereal_cloak'),
            ],
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "A Destroyed House",
            "description":  ("You look around you at the devastated home.",
                            "The roof is caved in, and there is dirty furniture and trinkets littered around the ground.",
                            "There is a trapdoor in the floor in the back"),
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "south", "roomId": 1},
                {"direction": "west", "roomId": 5},
                {"direction": "down", "roomId": 7},
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
            ],          
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "A Large Crater",
            "description":  "You see a giant round hole in the ground. There is purple rocks scattered around.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "west", "roomId": 6},
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "Gooey Plains",
            "description":  "It appears that this area used to be covered in grass, but now an &godd&N &mpurple&N &gslime&N covers the ground",
            "indoors": False,
            "terrain": "slime",
            "exits": [
                {"direction": "north", "roomId": 5},
                {"direction": "south", "roomId": 6},
                {"direction": "east", "roomId": 1},
            ],
            "objects": [
                O.spawn("pile_of_goo"),
            ],                       
            "mobs": [
                M.spawn("dark_glob"),
            ],            
        }
    ),
    5: Room(
        {
            "number": 5,
            "name": "Falcon Nest",
            "description":  "In the middle of a field there is a large tree. Upon it rests a bowl shaped collection of hay, sticks, mud, and other natural items.",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "south", "roomId": 4},
                {"direction": "east", "roomId": 2},
            ],
            "objects": [
                O.spawn("falcon_feather"),
            ],                       
            "mobs": [
                M.spawn("falcon_spy"),
            ],     
        }
    ),
    6: Room(
        {
            "number": 6,
            "name": "A Cave",
            "description":  "You enter a cave. It is entirely stone, and you see light from deeper down the path, possibly another exit.",
            "indoors": True,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "east", "roomId": 3},
            ],
            "mobs": [
                M.spawn("shadow"),
            ],     
        }
    ),
    7: Room(
        {
            "number": 7,
            "name": "Mage's Dungeon",
            "description":  ("You climb down the ladder into a small, stone room.",
                            "There is a workbench with various contraptions, and many shelves with &Mw&Ge&Yi&Cr&Md&Gl&Yy &Cc&Mo&Gl&Yo&Cr&Me&Gd &Yl&Ci&Mq&Gu&Yi&Cd&Ms."),
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "up", "roomId": 2},
            ],
            "objects": [
                O.spawn("health_potion"),
            ],
            "mobs": [
                M.spawn("dark_mage"),
            ],
        }
    ),
    8: Room(
        {
            "number": 8,
            "name": "Sword Shrine",
            "description":  ("You ascend into the room and look around. You are walking on &Xdark&N &Wclouds&N.",
                            "In the middle of the room there is a stone triangular stone platform with a &Bshining&N &Csword&N in the middle.",
                            "Behind the platform lies &mInanis&N the &XVoid&N &mDragon&N, protecting the &Bshining&N &Csword&N."),
            "indoors": False,
            "terrain": "cloud",
            "exits": [
                {"direction": "down", "roomId": 1},
            ],
            "mobs": [
                M.spawn("void_dragon"),
            ],
            "objects": [
                O.spawn("sword_that_seals_the_darkness")
            ]
        }
    ),
    9: Room(
        {
            "number": 9,
            "name": "Invisible Room",
            "description":  ("You enter a door and look around at nothingness.",
                            "There is nothing here. It's empty.",
                            "You take a tentative step and discover your feet become safely planted on the emptiness before you."),
            "indoors": False,
            "terrain": "nothing",
            "exits": [
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
}
