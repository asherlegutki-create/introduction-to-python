"""
zones.Oakhurst.rooms
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
        "name": "The Oakhurst Tavern",
        "description": "A &yroadside tavern&N, it sits at the edge of a &gpinewood forest&N.\nThe interior is warmed by a large &rfireplace&N on the left wall and the scents of &mvarious&N &Yalcohols&N waft about the room.&N\nIt lt looks as if it may have been someones house at somepoint in the past ",
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
            M.spawn("Fanciful_Bard"),
            M.spawn("Red_Kobold"),
            
        ],
        }),
        2: Room({
        "number": 2,
        "name": "Tavern Courtyard",
        "description": "This courtyard, which is a bit larger than the tavern itself, has a perimeter of &gshrubbery&N that connects to the back of the tavern wall.\nA &Xcobblestone path&N stretches from the door and surrounds a &ggiant pine&N in the middle of the room, the rest of the courtyard is covered in &Gshort grass&N.\nThe ancient &gpine tree&N in the center provides a sense if safety and the patches of &YW&yy&Wl&Yd&yf&Wl&Yo&yw&We&Yr&ys&N dotted about give it a light and cheery atmosphere.",
        "indoors": False,
        "terrain": "grass",
        "exits": [
            {"direction": "north", "roomId": 1},
        ],
        "objects": [
            O.spawn("Giant_Pine_Tree"),
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
    #         O.spawn("Dark_Wood_Trees"),
    #     ], 
    #     "mobs": [
    #         M.spawn("Sheep"),
    #         M.spawn("Sheep")], 

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
    #         O.spawn("Dark_Wood_Trees"),
    #     ], 
    #     "mobs": [
    #         M.spawn("Sheep"),
    #         M.spawn("Cow")], 

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
    #     "mobs": [M.spawn("Abolish_Veylock")], 

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
    #             O.spawn("Dark_Wood_Trees"),
    #         ], 
    #         "mobs": [M.spawn("Timid_Sheep"),], 

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
    #             O.spawn("Crumbling_Stone"),
    #        ],
            
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
    #             O.spawn("Crumbling_Stone"),
            
    #         ],
    #  9: Room({
    #         "number": 9,
    #         "name": "Manor Entrance",
    #         "description": "        12345       ",
    #         "indoors": True,
    #         "terrain": "dark wooden floor",
    #         "exits": [
    #             {"direction": "west", "roomId": 8},
    #             {"direction": "east", "roomId": 10},
    #         ],
    #    "mobs": [M.spawn("Drift")]

    #   10: Room({
    #    "number": 10,
    #    "name": "Main Hall",
    #    "description": "        12345           ",
    #    "indoors": True,
    #    "terrain": "dark wooden floor",
    #    "exits": [
    #        {"direction": "west", "roomId":9},
    #        {"direction": "north", "roomId":12},
    #        {"direction": "south", "roomId":11},
    #    ],
    #    "objects": [
    #        O.spawn("Crimson_Banner"),
    #        O.spawn("Crimson_Beacon"),
    #        O.spawn("Grand_Dining_Table"),
    #    ],
    #    "mobs": [M.spawn("Scott_Goldsmith")],
    #    "mobs": [M.spawn("Avid_Goldsmith")],
    
    #   11: Room({
    #    "number": 11,
    #    "name": "Small Storage Room",
    #    "description": "        12345           ",
    #    "indoors": True,
    #    "terrain": "dark wooden floor",
    #    "exits": [
    #        {"direction": "north", "roomId":10},
    #    ],
    #    "objects": [
    #        O.spawn("Wooden_Chest"),
    #        O.spawn("Wooden_Chest"),
    #        O.spawn("Wooden_Chest")],
    #   
    
    #   12: Room({
    #    "number": 12,
    #    "name": "Grand Ballroom",
    #    "description": "        12345           ",
    #    "indoors": True,
    #    "terrain": "dark wooden floor",
    #    "exits": [
    #        {"direction": "south", "roomId":10},
    #        {"direction": "east", "roomId":13},
    #    ],
    #    "objects": [
    #        O.spawn("Large_Windows"),
    #        O.spawn("Fountain_Of_Crimson"),
    #    ],
    #    "mobs": [M.spawn("Shelby")],
    #    "mobs": [M.spawn("Mythical")],
    
    #   13: Room({
    #    "number": 13,
    #    "name": "Livestock Room",
    #    "description": "        12345           ",
    #    "indoors": False,
    #    "terrain": "dark wooden floor",
    #    "exits": [
    #        {"direction": "west", "roomId":12},
    #        {"direction": "down", "roomId":14},
    #    ],
    #    "objects": [
    #        O.spawn("Chicken_Coop"),
    #        O.spawn("Cow_Pen"),
    #        O.spawn("Sheep_Pen"),
    #    ],
    #    "mobs": [M.spawn("Timid_Sheep")],
    #    "mobs": [M.spawn("Timid_Cow")],
    
    #   14: Room({
    #    "number": 14,
    #    "name": "Manor crypt",
    #    "description": "        12345           ",
    #    "indoors": True,
    #    "terrain": "smooth stone floor",
    #    "exits": [
    #        {"direction": "up", "roomId":13},
    #    ],
    #    "objects": [
    #        O.spawn("Neat_Room"),       #Drift
    #        O.spawn("Cheerful_Room"),   #Shelby
    #        O.spawn("Eclectic_Room"),   #Mythical
    #        O.spawn("Abandoned_Room"),  #Pyro(dead)
    #        O.spawn("Fanciful_Room"),   #Scott and Avid
    #        O.spawn("Ancient_Coffin"),
    #    ],
    
    





    #         ],
            
    #     }),




    }),
 }
