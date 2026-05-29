from ashenmoor.world import Room
from . import objects as O
from . import mobs    as M

ROOMS: dict[int, Room] = {
    5: Room({
        "number": 5,
        "name": "Mrs.Allisons class",
        "description": "",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "south", "roomId": 1},
        ],
        "objects": [O.spawn("water bottle"), O.spawn("pitch fork")],
        "mobs": [],
    }),
    6: Room({
        "number": 6,
        "name": "Miss Allisons",
        "description": "a room, filled with modern decor, accompanied by historical papers and a wooden map",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "south", "roomId": 2},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    9: Room({
        "number": 9,
        "name": "Mr. Millers",
        "description": "a bland room with geometrically shaped desks and animal tanks.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "north", "roomId": 1},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    8: Room({
        "number": 8,
        "name": "Mr. Westmarks",
        "description": "a small office litters with books and trinkets, one cluttered desk sits with three office chairs",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "south", "roomId": 4},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    7: Room({
        "number": 7,
        "name": "Mrs. Millers class",
        "description": "a bland room with few decorations, two couches sit in the back.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "south", "roomId": 3},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    10: Room({
        "number": 10,
        "name": "Mr. Stubblefield",
        "description": "a bland room with some decorations, a cluttered desk sits in the corner along with two cluttered counters in the back",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "east", "roomId": 9},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    11: Room({
        "number": 11,
        "name": "Mrs. Kralicek",
        "description": "a well decorated room filled with a sweet smell, many literature related posters sit on the walls",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "north", "roomId": 3},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    1: Room({
        "number": 1,
        "name": "hallway seg 1",
        "description": "lockers line the walls on the west, accompanied by a door.\nbackpacks hangs nest to another door on the east",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "east", "roomId": 2},
            {"direction": "south", "roomId": 9},
            {"direction": "north", "roomId": 5},
            {"direction": "west", "roomId": 99004},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    2: Room({
        "number": 2,
        "name": "hallway seg 2",
        "description": "lockers line the walls on the west, accompanied by a door.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "east", "roomId": 3},
            {"direction": "south", "roomId": 10},
            {"direction": "west", "roomId": 1},
            {"direction": "north", "roomId": 6},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    3: Room({
        "number": 3,
        "name": "hallway seg 3",
        "description": "lockers line the walls on the west, accompanied by a door.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "east", "roomId": 4},
            {"direction": "south", "roomId": 11},
            {"direction": "west", "roomId": 2},
            {"direction": "north", "roomId": 7},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),
    4: Room({
        "number": 4,
        "name": "hallway seg 4",
        "description": "lockers line the walls on the west, accompanied by a door.",
        "indoors": True,
        "terrain": "ground",
        "exits": [
            {"direction": "north", "roomId": 8},
        ],
        "objects": [
            
        ],
        "mobs": [],
    }),

}
