from ashenmoor.world import Room
from . import objects as O
from . import mobs as M

ROOMS: dict[int, Room] = {
    1: Room({
        "number": 1,
        "name": "&CThe Beginning of the World!&N",
        "description": "",
        "indoors": False,
        "terrain": "no ground",
        "exits": [
            {"direction": "north", "roomId": 1},
            {"direction": "south", "roomId": 1},
            {"direction": "east",  "roomId": 2},
            {"direction": "west",  "roomId": 3},
            {"direction": "up",    "roomId": 1},
            {"direction": "down",  "roomId": 1},
        ],
        "objects": [
            O.spawn("silken_sack"),
            O.spawn("windsong"),
        ],
        "mobs": [M.spawn("wandering_student")],   # escbaalion is not in this zone's mobs.py
    }),
}
