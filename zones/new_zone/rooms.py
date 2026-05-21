from ashenmoor.world import Room
from . import objects as O
from . import mobs as M

ROOMS: dict[int, Room] = {
    1: Room({
        "number": 1,
        "name": "&CThe Beginning of the World!&N",
        "description": (
            "   A vast open area in the wood with paths leading to the &cNorth&N, &cEast&N, &cSouth&N, and &cWest&N.",
            "As you look to the &cNorth&N you can't help but think of &RAsher&N, &GArcher&N, &CCharlotte&N and &mDamien&n.",
            "Looking down the path that leads to the &cWest&N your mind is filled with thoughts of &XDrew&N, &YEva&N, &cGabe&N",
            "and &rIsaac&N. Looking further to the &cEast&N you are overwhelmed with the impression of &MJordan&N, &BJoshua&N",
            "&CLindi&N and &gReese&N. Your thoughts drift to &yTimothy&N, &bWilson&N, and &WWyatt&N to the &cSouth&N."),
        "indoors": False,
        "terrain": "forest",
        "exits": [
            {"direction": "north", "roomId": 2},
            {"direction": "west",  "roomId": 3},
            {"direction": "east",  "roomId": 4},
            {"direction": "south", "roomId": 5},
        ],
        "objects": [
            O.spawn("silken_sack"),
            O.spawn("windsong"),
        ],
        "mobs": [M.spawn("wandering_student")],   # escbaalion is not in this zone's mobs.py
    }),
    2: Room({
        "number": 2,
        "name": "&MOne North&N",
        "description": (
        ),
        "indoors": False,
        "terrain": "forest",
        "exits": [
            {"direction": "north", "roomId": 1001, "external": True},
            {"direction": "west",  "roomId": 2001, "external": True},
            {"direction": "east",  "roomId": 3001, "external": True},
            {"direction": "south", "roomId": 1},
            {"direction": "up", "roomId": 4001, "external": True},
        ],
    }),
    3: Room({
        "number": 3,
        "name": "&MOne West&N",
        "description": (
        ),
        "indoors": False,
        "terrain": "forest",
        "exits": [
            {"direction": "north", "roomId": 5001, "external": True},
            {"direction": "west",  "roomId": 6001, "external": True},
            {"direction": "east",  "roomId": 1},
            {"direction": "south", "roomId": 7001, "external": True},
            {"direction": "up", "roomId": 15001, "external": True},
        ],
    }),
    4: Room({
        "number": 4,
        "name": "&MOne East&N",
        "description": (
        ),
        "indoors": False,
        "terrain": "forest",
        "exits": [
            {"direction": "north", "roomId": 8001, "external": True},
            {"direction": "west",  "roomId": 1, "external": True}, # external value being True is directing to external room 1 (The Void) instead of local room 1 (The Beginning of the World!)
            {"direction": "east",  "roomId": 10001, "external": True},
            {"direction": "south", "roomId": 9001, "external": True},
            {"direction": "down", "roomId": 11001, "external": True},
        ],
    }),
    5: Room({
        "number": 5,
        "name": "&MOne South&N",
        "description": (
        ),
        "indoors": False,
        "terrain": "forest",
        "exits": [
            {"direction": "north", "roomId": 1},
            {"direction": "west",  "roomId": 13001, "external": True},
            {"direction": "east",  "roomId": 14001, "external": True},
            {"direction": "south", "roomId": 12001, "external": True},
        ],
    }),
}
