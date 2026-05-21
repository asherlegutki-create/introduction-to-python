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
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 4},
                {"direction": "down", "roomId": 99002, "external": True}
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
                O.spawn("sword_that_seals_the_darkness"),
            ],
            "mobs": [
                M.spawn("void_dragon"),
                M.spawn("shadow_gremlin"),
                M.spawn("dark_mage"),
            ],
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "A Destroyed House",
            "description": "You look around you at the devastated home. The roof is caved in, and there is dirty furniture and trinkets littered around the ground.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 5},
            ],
            "mobs": [
                M.spawn("shadow_gremlin"),
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "A Large Crater",
            "description": "You see a giant round hole in the ground. There is purple rocks scattered around.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 6},
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
            ],
            "mobs": [
                M.spawn("dark_mage"),
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "Dead Fields",
            "description": "The field is flat and covered with dead, brownish grass",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "north", "roomId": 5},
                {"direction": "south", "roomId": 6},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
    5: Room(
        {
            "number": 5,
            "name": "Dead Fields",
            "description": "The field is flat and covered with dead, brownish grass",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 4},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
    6: Room(
        {
            "number": 6,
            "name": "Dead Fields",
            "description": "The field is flat and covered with dead, brownish grass",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 3},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
}
