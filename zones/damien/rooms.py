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
                {"direction": "east", "roomId": 10},
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
                {"direction": "east", "roomId": 11},
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
                            "In the middle of the room there is a triangular stone platform."),
            "indoors": False,
            "terrain": "cloud",
            "exits": [
                {"direction": "down", "roomId": 1},
            ],
            "mobs": [
                M.spawn("void_dragon"),
            ],
            "objects": [
                O.spawn("sword_that_seals_the_darkness"),
                O.spawn("sword_that_seals_the_darkness")
            ]
        }
    ),
    9: Room(
        {
            "number": 9,
            "name": "Stone Pathway",
            "description":  ("You follow a wide, stoney path to the large city gates of Umbrurb."),
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 10},
                {"direction": "south", "roomId": 11},                
                {"direction": "east", "roomId": 12},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
    10: Room(
        {
            "number": 10,
            "name": "Garden",
            "description":  ("Outside of the city next to the pathway is a large &ggarden&N.",
                             "It is filled with many &mflowers."),
            "indoors": False,
            "terrain": "flowers",
            "exits": [
                {"direction": "south", "roomId": 9},
                {"direction": "west", "roomId": 2},
            ],
        }
    ),
    11: Room(
        {
            "number":11,
            "name": "Garden",
            "description":  ("Outside of the city next to the pathway is a large &ggarden&N.",
                             "It is filled with many &mflowers."),
            "indoors": False,
            "terrain": "flowers",
            "exits": [
                {"direction": "north", "roomId": 9},
                {"direction": "west", "roomId": 3},
            ],
        }
    ),
    12: Room(
        {
            "number":12,
            "name": "City Gates",
            "description":  ("Before you is a large, black gate.",
                             "Across the top of the gate are large letters that say 'Welcome to Vacivus'."),
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "west", "roomId": 9},
                {"direction": "east", "roomId": 13},
            ],
        }
    ),
    13: Room(
        {
            "number":13,
            "name": "Inside the City Walls",
            "description":  ("The thick protective wall are hollow, and soldiers stand at attention.",
                             "You see doors on either side, and you hear the sound of swords clanking. Soldiers must be training."),
            "indoors": True,
            "terrain": "stone",
            "exits": [
                {"direction": "west", "roomId": 12},
                {"direction": "up", "roomId": 14},
            ],
            "mobs": [
                M.spawn("vacivus_soldier"),
                M.spawn("vacivus_soldier"),
                M.spawn("vacivus_soldier"),
                M.spawn("vacivus_soldier"),
            ],
        }
    ),
    14: Room(
        {
            "number":14,
            "name": "On Top of the City Walls",
            "description":  ("You climb up the ladder and see archers, ready for an attack.",
                             "The view is breathtaking, and you see the &ggardens&N below you."),
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "down", "roomId": 13},
            ],
            "mobs": [
                M.spawn("vacivus_archer"),
                M.spawn("vacivus_archer"),
                M.spawn("vacivus_archer"),
                M.spawn("vacivus_archer"),
            ],
        }
    ),
}
