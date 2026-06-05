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
            "name": "&WThe &yc&Yh&N&ye&Ye&N&ys&Ye&N Layer&N",
            "description": "&WYou are in the &Ycheese&N &Wlayer of the&N &yw&Go&N&yr&Gl&N&yd.\n &N&yc&Yh&N&ye&Ye&N&ys&Ye&N &Wis everywhere, in all shapes and sizes.&N\n &WThe air smells &N&rstrongly &Wof &yc&Yh&N&ye&Ye&N&ys&Ye&N,&W and you can see little&N &ybits &Wof it floating in the air.&N\n\n",
            "indoors": False,
            "terrain": "cheese",
            "exits": [
                {"direction": "north", "roomId": 99003, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 1},
            ],
            "objects": [
                O.spawn("cheese wheel"),
                O.spawn("toy cheese"),
            ],
            "mobs": [
                M.spawn("the cheese monster"),
                M.spawn("the cheez sniffer"),
                M.spawn("the cheese spirit"),
            ],


        },

    ),
    2: Room(
        {
            "number": 2,
            "name": "The &YC&N&yh&Y&N&ye&ye&Ys&N&ye&N &BOasis&N",
            "description": "The &YC&N&yh&Y&N&ye&ye&Ys&N&ye&N &BO&N&yr&Gl&N&yd is a &Rbig&N patch of &Ggrass&N surrounded by &YC&N&yh&Y&N&ye&ye&Ys&N&ye&N. \n The &Ggrass&N is surprisingly &Ggreen&N and &Blush&N, and there is a &msmall &Bpond&N in the center.\n  The air smells &Wfresher&N here, and you can hear the sound of &YC&N&yh&Y&N&ye&ye&Ys&N&ye&N &mbirds &Wchirping.&N\n\n",
            "indoors": False,
            "terrain": "no ground",
            "exits": [


                {"direction": "north", "roomId": 99003, "external": True},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 3},
            ],
            "objects": [
                O.spawn("cheese surfboard"),
                O.spawn("chez destroyer"),
            ],
            "mobs": [
                M.spawn("the cheesy bird"),
            ],

        },
    ),
    3: Room(
        {
            "number": 3,
            "name": "The &bUnderwater&N &ycheese&N &Wof&N &BAtlantis&N",
            "description": "The &bUnderwater&N &ycheese&N &Wof&N &BAtlantis&N &Wis a city under the&N &YCheese&N &BOasis&N &Wwhere the people who &RDARE&N surf in the&N &Ycheese&N &Boasis&N",
            "indoors": False,
            "terrain": "under-the-sea",
            "exits": [
                {"direction": "north",  "roomId":3},
                 {"direction": "south", "roomId":3},
                {"direction": "east",   "roomId":4},
                {"direction": "west",   "roomId":3},
                {"direction": "up",     "roomId":2},
                {"direction": "down",   "roomId":3},
            ],
            "mobs": [
                M.spawn("the cheez fih"),
            ],


        },
    ),
    4: Room(
        {
            "number": 4,
            "name": "&Wthe&N &bunderwater&N &ycheese&N &Wlibrary&N",
            "description": "The &bunderwater&N &WCheese&N &yLibrary&N &Wis a&N &mquiet&N &Wplace filled with shelves of books made of&N &ycheese.&N &WThe air is thick with the scent of aged&N &Ycheddar&N &Wand the sound of pages turning. The library is a haven for those seeking&N &Gk&N&bn&N&Go&N&bw&N&Gl&N&be&N&Gd&N&bg&N&Ge&N &Wabout all things&N &ycheese&N-&Wrelated.&N",
            "indoors": True,
            "terrain": "library",
            "exits": [
                {"direction": "north", "roomId": 3},
                {"direction": "south", "roomId": 3},
                {"direction": "east",  "roomId": 3},
                {"direction": "west",  "roomId": 3},
                {"direction": "up",    "roomId": 3},
                {"direction": "down",  "roomId": 3},
            ],
            "objects": [
                O.spawn("cheese book"),
                O.spawn("cheese scroll"),
            ],
                "mobs": [
                    M.spawn("the cheese librarian"),
                ],


        },
    ),
}