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
            "name": "Garden of Eden",
            "description": "There is a huge garden streching for miles.There is a &Gtree&N in the middle of the Garden.\n God is watching over his creation.",
            "indoors": False,
            "terrain": "rolling grass hills",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "south", "roomId": 5},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 6},
                {"direction": "down", "roomId": 7},
            ],
            "objects": [
                O.spawn("Banana"),
                O.spawn("green leaf"),
                O.spawn("The Fruit"),
            ],
            "mobs": [
                M.spawn("Adam") ,
                M.spawn("Eve"),
                M.spawn("Slippery Serpant")],  # two independent students

        }
    ),
2: Room(
        {
            "number": 2,
            "name": "Jericho",
            "description": "This is a city with a huge wall going around it to protect it.",
            "indoors": False,
            "terrain": "grass plane",
            "exits": [
                {"direction": "north", "roomId": 8},
                {"direction": "south", "roomId": 9},
                {"direction": "east", "roomId": 10},
                {"direction": "west", "roomId": 11},
                {"direction": "up", "roomId": 12},
                {"direction": "down", "roomId": 13},
            ],
            "objects": [
                O.spawn("The Horn"),
                O.spawn("Tunic")
            ],
            "mobs": [  
                M.spawn("Joshua") ,
                M.spawn("Israelite"),
                M.spawn("Trumpet Player")
            ],  # two independent students
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "Upper Room",
            "description": "This is the very room that Jesus and his disciples ate in during the last supper.",
            "indoors": True,
            "terrain": "Clay floor",
            "exits": [
                {"direction": "north", "roomId": 14},
                {"direction": "south", "roomId": 15},
                {"direction": "east", "roomId": 16},
                {"direction": "west", "roomId": 17},
                {"direction": "up", "roomId": 18},
                {"direction": "down", "roomId": 19},
            ],
            "objects": [
                O.spawn("The Holy Grail"),
                O.spawn("Bread"),
                Ospawn("Wine")
            ],
            "mobs": [  
                M.spawn("Jesus") ,
                M.spawn("Peter"),
                M.spawn("Matthew"),
                M.spawn("Judas"),
                M.spawn("John 1"),
                M.spawn("John 2"),
                M.spawn("Andrew"),
                M.spawn("James"),
                M.spawn("Philip"),
                M.spawn("Bartholomew")
            ],  # two independent students
        }
    ),
}
