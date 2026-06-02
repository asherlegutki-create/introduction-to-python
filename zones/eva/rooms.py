"""
zones.eva.rooms
"""

from ashenmoor.world import Room
from . import objects as O
from . import mobs    as M

ROOMS: dict[int, Room] = {
    123: Room({
        "number": 123,
        "name": "Room_template",
        "description": "its a room!",
        "indoors": True,
        "terrain": "ground type",
        "exits": [
            {"direction": "north", "roomId": 123},
            {"direction": "south", "roomId": 123},
        ],
        "objects": [
            O.spawn("object_template"),
            O.spawn("Item_template"),
        ],
        "mobs": [M.spawn("mob_template")],
    }),



    1: Room({
        "number": 1,
        "name": "The Withered-Rose Tavern",
        "description": "An average &yroadside tavern&N, it sits at the edge of a &gconiferous forest&N.\nThe interior is warmed by a large &rfireplace&N on the left wall and the scents of &mvarious&N &Yalcohols&N waft about the room.&N",
        "indoors": True,
        "terrain": "wooden floor",
        "exits": [
            {"direction": "east", "roomId": 99003,"external": True}, 
            #to the other rooms ^

            #{"direction": "north", "roomId": 3}, #to dark woods at a later point
            {"direction": "south", "roomId": 2},
        ],
        "objects": [
            O.spawn("Assorted_Bottles__Full"),
            O.spawn("Silver_Sword"),
        ],
        "mobs": [                           # was [spawn1][spawn2] — that's list subscription, not a list
            M.spawn("fanciful_Bard"),
            M.spawn("Red kobold"),
            
        ],
        }),
        2: Room({
        "number": 2,
        "name": "Tavern Courtyard",
        "description": "This courtyard, which is a bit larger than the tavern itself, has a perimeter of &gshrubbery&N that connects to the back of the tavern wall.\nA &Xcobblestone path&N stretches from the door and surrounds a &ggiant oak&N in the middle of the room, the rest of the courtyard is covered in &Gshort grass&N.\nThe ancient &goak tree&N in the center provides a sense if safety and the patches of &YW&yy&Wl&Yd&yf&Wl&Yo&yw&We&Yr&ys&N dotted about give it a light and cheery atmosphere.",
        "indoors": False,
        "terrain": "grass",
        "exits": [
            {"direction": "north", "roomId": 1},
        ],
        "objects": [
            O.spawn("Giant_Oak_Tree"),
            O.spawn("Tables"),
            O.spawn("Wyldflowers"),
        ],
        "mobs": [
            M.spawn("Excited_Child"),
            M.spawn("Large_Orange_Cat"),
            M.spawn("Eclectic_Rouge"),
         ], 
##############################################################################################################################################

    # 3: Room({
    #     "number": 3,
    #     "name": "Dark Woods Entrance",
    #     "description": "        12345       ",
    #     "indoors": False,
    #     "terrain": "woodland",
    #     "exits": [
    #         {"direction": "north", "roomId": 4},
    #         {"direction": "south", "roomId": 2},
    #     ],
    #     "objects": [
    #         O.spawn("Dark_Wood_trees"),
    #     ], 
    #     "mobs": [
    #         M.spawn("Sheep"),
    #         M.spawn("Sheep"),
    #      ], 

    # 4: Room({
    #     "number": 4,
    #     "name": "Dark Woods Continued",
    #     "description": "        12345       ",
    #     "indoors": False,
    #     "terrain": "woodland",
    #     "exits": [
    #         {"direction": "north", "roomId": 6},
    #         {"direction": "south", "roomId": 3},
    #         {"direction": "down", "roomId": 5},
    #     ],
    #     "objects": [
    #         O.spawn("Dark_Wood_trees"),
    #     ], 
    #     "mobs": [
    #         M.spawn("Sheep"),
    #         M.spawn("Cow"),
    #      ], 

    # 5: Room({
    #     "number": 5,
    #     "name": "Woodland Crypt",
    #     "description": "        12345       ",
    #     "indoors": True,
    #     "terrain": "stone",
    #     "exits": [
    #         {"direction": "up", "roomId": 4},
           
    #     ],
    #     "objects": [
    #         O.spawn("Wooden_Chest"),
    #     ], 
    #     "mobs": [
    #         M.spawn("Abolish"),
           
    #      ], 

    # 6: Room({
    #         "number": 6,
    #         "name": "End of Dark Woods",
    #         "description": "        12345       ",
    #         "indoors": False,
    #         "terrain": "woodland",
    #         "exits": [
    #             {"direction": "north", "roomId": 7},
    #             {"direction": "south", "roomId": 4},
                
    #         ],
    #         "objects": [
    #             O.spawn("Dark_Wood_trees"),
    #         ], 
    #         "mobs": [
    #             M.spawn("Nervous_Sheep"),
                
    #         ], 

    # 7: Room({
    #         "number": 7,
    #         "name": "Beginning of the Crumbling Bridge",
    #         "description": "        12345       ",
    #         "indoors": False,
    #         "terrain": "crumbling stone",
    #         "exits": [
    #             {"direction": "west", "roomId": 6},
    #             {"direction": "east", "roomId": 8},
    #         ],
    #         "objects": [
    #             O.spawn("crumbling stone"),
            
    #         ],
            
    #  8: Room({
    #         "number": 8,
    #         "name": "End of the Crumbling Bridge",
    #         "description": "        12345       ",
    #         "indoors": False,
    #         "terrain": "crumbling stone",
    #         "exits": [
    #             {"direction": "west", "roomId": 7},
    #             {"direction": "east", "roomId": 9},
    #         ],
    #         "objects": [
    #             O.spawn("crumbling stone"),
            
    #         ],
            
    #     }),




    }),
 }
