from ashenmoor.world import Room
from . import objects as O
from . import mobs    as M

ROOMS: dict[int, Room] = {
    1: Room({
        "number": 1,
        "name": "room j",
        "description": "the room is filled with tables and chairs.\n the interactive board glows softly in the front",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "north", "roomId": 1},
            {"direction": "south", "roomId": 1},
            {"direction": "west",  "roomId": 1},   # was "roomid" (lowercase d) — typo fixed
        ],
        "objects": [
            O.spawn("pencil"),
            O.spawn("whiteboard_marker"),
        ],
        "mobs": [M.spawn("wandering_student")],
    }),
    2: Room({
        "number": 2,
        "name": "room h",
        "description": "a well decorated room, filled with historical artifacts.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "north", "roomId": 1},
            {"direction": "south", "roomId": 1},
        ],
        "objects": [
            O.spawn("Mrs.Allisons_syth"),
        ],
        "mobs": [M.spawn("fellow_student")],
    }),
}
