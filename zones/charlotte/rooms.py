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
            "name": "The Front Doors",#this is the Front doors
            "description": "The Front doors is the entrance to the school.\n There are two doors that open in. These doors may or may not be locked for safety.\n  west is the office, east is the wall, south is the parking lot,\n up is the exit out of my rooms, and down is carpet.",
            "indoors": False,                        
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "up", "roomId": 99002, "external": True}
                
            ],
            "objects": [
              #  O.spawn(""),
              #  O.spawn(""),
              #  O.spawn(""),
            ],
            "mobs": [
               # M.spawn("") ,
               # M.spawn(""),],  # two independent students
            ],
        }
    ),
2: Room(
        {
            "number": 2,
            "name": "Hallway",
            "description": "This hallway is one of many and leads to \n the bathrooms, teacher lounge ,office,and janitors closet #1.\n West is the office north is still same hallway, east is the wall,\n up is ceiling, down is the floor.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "west", "roomId": 3},
                {"direction": "north", "roomId": 4},
                 {"direction": "south", "roomId": 1},
            ],
            "objects": [
              #  O.spawn(""),
              # O.spawn("")
            ],
            "mobs": [  
                #M.spawn("") ,
                #M.spawn(""),
                #M.spawn("")
            ],  
        }
    ),
3: Room(
        {
            "number": 3,
            "name": "Office",
            "description": "This is the office where Mrs.stacey spends most of the day.\n To the west again is Mr.Carlson's office,\n east is the hallway, and north is the teachers lounge.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 2},
                {"direction": "north", "roomId": 6},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the bathrooms,\n teacher lounge ,office,and janitors closet #1.\n To the west is the teachers lounge,to the north is more hallway, east is a wall,\n up is the ceiling, /n down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 2},
                {"direction": "north", "roomId": 6},
                {"direction": "north", "roomId": 7},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),
    5: Room(
        {
            "number": 5,
            "name": "Mr. Carlson's office",
            "description": "Mr.C office is in side of the regular office.\n Mr.Carlson's office has a sword hanging on the wall. \nTo the west is a wall,to the north is the regular office, east is a wall, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 3},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     6: Room(
        {
            "number": 6,
            "name": "teacher's lounge",
            "description": "The teachers lounge is where teachers hang around when not teaching.\n To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, \n down is the floor, and south is the office.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "south", "roomId": 3},
                {"direction": "east", "roomId": 4},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     7: Room(
        {
            "number": 7,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the bathrooms,\n teacher lounge ,office,and janitors closet #1. To the west is the teacher lounge,to the north is more hallway, \neast is more hallway, up is the ceiling,  down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 15},
                {"direction": "south", "roomId": 4},
                {"direction": "east", "roomId": 8},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     8: Room(
        {
            "number": 8,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the bathrooms,\n teacher lounge ,office,and janitors closet #1. To the west is the boys bathroom, \nto the north is more hallway, east is a wall, up is the ceiling, \n down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 12},
                {"direction": "south", "roomId": 7},
                {"direction": "north", "roomId": 9},

                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     9: Room( 
        {
            "number": 9,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the bathrooms, \nteacher lounge ,office,and janitors closet #1. To the west is the janitor,\n to the north is more hallway, east is a wall, up is the ceiling, \n down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 13},
                {"direction": "south", "roomId": 8},
                {"direction": "north", "roomId": 10},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     10: Room(
        {
            "number": 10,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the bathrooms,\n teacher lounge ,office,and janitors closet #1. To the west is the girls bathroom,\n to the north is the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "west", "roomId": 14},
                {"direction": "north", "roomId": 11},
                {"direction": "south", "roomId": 9},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     11: Room(
        {
            "number": 11,
            "name": "blacktop",
            "description": "The blacktop is a black cement parking lot where kids play during lunch. \nThere are no cars. To the west is more blacktop, to the north is more blacktop, \neast is more blacktop, up is nothing but air, down is the blacktop, and \nsouth is the hallway inside of the school.",
            "indoors": False,
            "terrain": "concrete",
            "exits": [
                {"direction": "south", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     12: Room(   
         {
            "number": 12,
            "name": "boy's bathroom",
            "description": "This is the boy's bathroom. To the west is a wall,to the north is a wall, \neast is the hallway, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 8},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     13: Room(
        {
            "number": 13,
            "name": "Janitor's closet #1",
            "description": "The janitor's closet is where all the cleaning\n stuff is stored. Some students are routinely come in to get a rag \nand spray or a vacuum. To the west is a wall,to the north is a wall, \neast is the hallway, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "east", "roomId": 9},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
     14: Room(
        {
            "number": 14,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls.\n To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    15: Room(
        {
            "number": 15,
            "name": "hallway",
            "description": "This hallway is one of many and leads to the \n3rd grade, 2nd grade, Mr.D's office, preschool, kindergarten, 4th grade,\n and 6th grade classrooms as well as more hallways.\n To the west is a hallway, to the north is 3rd grade classroom, east is \nthe hallway, up is the ceiling, /n down is the floor, and\n south is the 2nd grade classroom.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "west", "roomId": 7},
                {"direction": "east", "roomId": 29},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    16: Room(
        {
            "number": 16,
            "name": "2rd grade classroom",
            "description": "This is Mrs.Hollands 2nd grade classroom.\n There is a bunch of 2nd graders running around on their break.\n To the west is a wall,to the north is a hallway, \neast is the kindergarten classroom, up is the ceiling, \n down is the floor, and south is a door out of the building.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 18},
                {"direction": "north", "roomId": 15},
                {"direction": "east", "roomId": 50},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    17: Room(
        {
            "number": 17,
            "name": "3rd grade classroom",
            "description": "This is Mrs.Mollers 3rd grade classroom. To the west\n is a wall, to the north is a door to the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "north", "roomId": 43},
                {"direction": "south", "roomId": 15}
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    18: Room(
        {
            "number": 18,
            "name": "Kindergarten",
            "description": "This is Mrs.Sylva's kindergarten classroom. To the\n west is the 2nd grade classroom, to the north is the hallway,\n east is a wall, up is the ceiling, /n down is the floor, and\n south is a door out of the building.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    19: Room(
        {
            "number": 19,
            "name": "Mr.D's office",
            "description": "This is Mr.D's Office.Its is a small room used \nfor counseling and for talking to naughty trouble makers. To\n the west is a wall,to the north is a wall, east is a \nwall, up is the ceiling, /n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "south", "roomId": 29},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    20: Room(
        {
            "number": 20,
            "name": "6th grade classroom",
            "description": "This is Mrs.Harlukowicz's 6th grade classroom.\n The 6th graders are playing games on their snack break.\n To the west is a wall,to the north is the hallway, east is a wall, up is the ceiling, \n down is the floor, and south is a door out of the building.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "south", "roomId": 52},
                {"direction": "north", "roomId": 30},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    21: Room(
        {
            "number": 21,
            "name": "Preschool classroom",
            "description": "This is the preschool classroom. A bunch of 4-5 year olds are coloring. To the west \nis a wall,to the north is a door to the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "south", "roomId": 29},
                {"direction": "north", "roomId": 42},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    22: Room(
        {
            "number": 22,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n To the west is a wall,to the north is the hallway, east is a wall, up is the ceiling, \n down is the floor, and south is a door to the outside of building.",
            "indoors": True,
            "terrain": "concrete floor",
            "exits": [
                {"direction": "south", "roomId": 53},
                {"direction": "north", "roomId": 31},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    23: Room(
        {
            "number": 23,
            "name": "4th grade classroom",
            "description": "This is Mrs.Vrooman's 4th grade classroom. There is a small library\n int he corner of the room with a few graphic novels. To the west is a wall\n,to the north is a door to the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "north", "roomId": 41},
                {"direction": "south", "roomId": 30},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    24: Room(
        {
            "number": 24,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway\n. To the west is a wall,to the north is a door to the black top, east is a wall of bathrooms (the bathrooms are not open yet), up is the ceiling, /n down is the floor, and south is more hallway.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 40},
                {"direction": "south", "roomId": 31},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    25: Room(
        {
            "number": 25,
            "name": "Mr. Westmark's office",
            "description": "This is Mr. Westmark's office. A one weal is on the wall in this tiny little room.\n To the west is a wall,to the north is the hallway, east is a wall, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "north", "roomId": 32},
              
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    26: Room(
        {
            "number": 26,
            "name": "Highschool science lab",
            "description": "This is Mrs.Millers science lab. This room is a big room\n with circular tables and to tv's. To the west is a wall,\nto the north is the hallway, east is a wall, up is the ceiling, \n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 32},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    27: Room(
        {
            "number": 27,
            "name": "Highschool History classroom",
            "description": "This is Ms. Allison's highschool history \n classroom. Only boring highschoolers hang in here.\n To the west is a wall,to the north is a wall, east is a wall, up is the ceiling, \n down is the floor, and south is a door to the outside of the building.",         
            "indoors" True,
            "terrain": "concrete",
            "exits": [
                {"direction": "south", "roomId": 54},
                {"direction": "north", "roomId": 33},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    28: Room(
        {
            "number": 28,
            "name": "7th & 8th history classroom",
            "description": "this is Mrs.Allisons Jr high classroom. This is a\n dim light room with a very calm feeling. To the west is a wall,to the north\n is the hallway, east is a wall, up is the ceiling, \n down is the floor, and south is a door to the outside of the building.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "south", "roomId": 55},
                {"direction": "north", "roomId": 34},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    29: Room(
        {
            "number": 29,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n. To the west is more hallway, to the north is Mr.D's office and preschool, east is the hallway, up is the ceiling, \n down is the floor, and south is kindergarten.",
            "indoors": True,
            "terrain": "carpet",
            "exits": [
                {"direction": "east", "roomId": 15},
                {"direction": "west", "roomId": 30},
                {"direction": "north", "roomId": 19},
            #    {"direction": "north", "roomId": 21},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    30: Room(
        {
            "number": 30, 
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n To the west is more hallway,to the north is the 4th grade classroom, east is the hallway, up is the ceiling, \n down is the floor, and south is 6th grade classroom.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 31},
                {"direction": "west", "roomId": 29},
                {"direction": "north", "roomId": 23},
                {"direction": "south", "roomId": 20},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    31: Room(
        {
            "number": 31,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway. To the west\n is more hallway,to the north is more hallway, east is the hallway, up is the ceiling, \n down is the floor, and south is also more hallway.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "north", "roomId": 24},
                {"direction": "south", "roomId": 22},
                {"direction": "east", "roomId": 30},
                {"direction": "west", "roomId": 32},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    32: Room(
        {
            "number": 32,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n To the west is more hallway, to the north is the 7th-10th grade\n english room, east is the hallway, up is the ceiling, \n down is the floor, and south is Mr. Westmarks office and the highschool science lab.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "east", "roomId": 33},
                {"direction": "west", "roomId": 31},
                {"direction": "north", "roomId": 47},
                {"direction": "south", "roomId": 26},
              #  {"direction": "south", "roomId": 25},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    33: Room(
        {
            "number": 33,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n To the west is more hallway, to the north is\n 7th science classroom, east is the hallway, up is the ceiling, \n down is the floor, and south is highschool history classroom.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "north", "roomId": 48},
                {"direction": "south", "roomId": 27},
                {"direction": "east", "roomId": 34},
                {"direction": "west", "roomId": 32},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    34: Room(
        {
            "number": 34,
            "name": "hallway",
            "description": "This hallway is one of many and leads to a door outside \nof the building and the highschool bathrooms as well as another hallway.\n To the west is more hallway, to the north is Mr. Miller's classroom, east is a door to the outside, up is the ceiling, \n down is the floor, and south is 7th-8th grade history classroom.",
            "indoors": True,
            "terrain": "carpet floor",
            "exits": [
                {"direction": "north", "roomId": 49},
                {"direction": "south", "roomId": 28},
                {"direction": "east", "roomId": 35},
                {"direction": "west", "roomId": 33},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    35: Room(
        {
            "number": 35,
            "name": "Breeze way",
            "description": " This is the breeze way where the children\n will run and walk around the school.\n To the west is a door to the inside,to the north is soon to be more breeze way, east\n is nothing for now, up is the ceiling, \n down is the floor, and south is nothing for now.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "west", "roomId": 34},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
   # 36: Room(
      #  {
          #  "number": 36,
          #  "name": "Girls bathroom",
         #   "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
         #   "indoors": True,
          #  "terrain": "tile floor",
          #  "exits": [
          #      {"direction": "east", "roomId": 10},
                
          #  ],
          #  "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
          #  ],
          #  "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
        #    ],
       ##  ),  
    #37: Room(
      #  {
           # "number": 37,
          #  "name": "Girls bathroom",
         #   "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
         #   "indoors": True,
          #  "terrain": "tile floor",
          #  "exits": [
          #      {"direction": "east", "roomId": 10},
                
          #  ],
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
           # ],
          #  "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
         #   ],
       # }
   # ),  
   # 38: Room(
       # {
          #  "number": 38,
          #  "name": "Girls bathroom",
          #  "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
          #  "indoors": True,
          #  "terrain": "tile floor",
           # "exits": [
           #     {"direction": "east", "roomId": 10},
                
           # ],
        #    "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
        #    ],
        #    "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
       #     ],
     #   }
  #  ),  
  #  39: Room(
     #   {
          #  "number": 39,
       #     "name": "Girls bathroom",
       #     "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
        #    "indoors": True,
         #   "terrain": "tile floor",
          #  "exits": [
           #     {"direction": "east", "roomId": 10},
                
       #     ],
        #    "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
      #      ],
       #     "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
        #    ],
   #     }
  #  ),  
    40: Room(
        {
            "number": 40,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch.\n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "south", "roomId": 24},
                {"direction": "east", "roomId": 44},
                {"direction": "west", "roomId": 41},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    41: Room(
        {
            "number": 41,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch. \n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "terrain": "cement",
            "exits": [
                {"direction": "east", "roomId": 40},
                {"direction": "west", "roomId": 42},
                {"direction": "south", "roomId": 23},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    42: Room(
        {
            "number": 42,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch. \n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "east", "roomId": 41},
                {"direction": "west", "roomId": 43},
                {"direction": "south", "roomId": 21},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    43: Room(
        {
            "number": 43,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch. \n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "south", "roomId": 17},
                {"direction": "east", "roomId": 42},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    44: Room(
        {
            "number": 44,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch.\n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "south", "roomId": 47},
                {"direction": "east", "roomId": 45},
                {"direction": "west", "roomId": 40},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    45: Room(
        {
            "number": 45,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch. \n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "south", "roomId": 48},
                {"direction": "east", "roomId": 46},
                {"direction": "west", "roomId": 44},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    46: Room(
        {
            "number": 46,
            "name": "the blacktop",
            "description": "This is the blacktop a bit cement parking lot where everybody eats lunch.. \n To the west is more blacktop,to the north is nothing for know,\n east is more blacktop, up is the ceiling, \n down is the floor, and south is a door that leads to the hallway.",
            "indoors": True,
            "terrain": "cement",
            "exits": [
                {"direction": "south", "roomId": 49},
                {"direction": "west", "roomId": 45},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    47: Room(
        {
            "number": 47,
            "name": "7th-10th english classroom",
            "description": "This is Mrs.K's jr high and highschool english classroom.\n To the west is a wall,to the north is a door to the outside, \neast is a wall, up is the ceiling, /n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 44},
                {"direction": "south", "roomId": 32},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    48: Room(
        {
            "number": 48,
            "name": "7th science classroom",
            "description": "This is Mr.Stubblefield's 7th grade science classroom.\n Quite the big classroom for a few students.\n To the west is a wall, to the north is a door to the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is the hallway.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 45},
                {"direction": "south", "roomId": 33},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    49: Room(
        {
            "number": 49,
            "name": "Mr.Millers classroom",
            "description": "Mr. Millers classroom is the only class room that it is unknown\n what classes are taught in there. To the west is a wall,\nto the north is a door to the blacktop, east is a wall, up is the ceiling, \n down is the floor, and south is a the hallway.",
            "indoors": True,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 46},
                {"direction": "south", "roomId": 34},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    50: Room(
        {
            "number": 50,
            "name": "The outside ",
            "description": "This is the outside of the school.\n More of it will be unlocked shortly.\n To the west is the doors into the school, to the north \nis the 2nd grade classroom, east is  more of the out side, up is the ceiling, \n down is the floor, and south is nothing for now.",
            "indoors": False,
            "terrain": "concrete",
            "exits": [
                {"direction": "north", "roomId": 16},
                {"direction": "east", "roomId": 51},
                {"direction": "west", "roomId": 1},
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    51: Room(
        {
            "number": 51,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    52: Room(
        {
            "number": 52,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    53: Room(
        {
            "number": 53,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    54: Room(
        {
            "number": 54,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
    55: Room(
        {
            "number": 55,
            "name": "Girls bathroom",
            "description": "This is the girls bathroom only for girls. To the west is a wall,to the north is a wall, east is the hallway, up is the ceiling, /n down is the floor, and south is a wall.",
            "indoors": True,
            "terrain": "tile floor",
            "exits": [
                {"direction": "east", "roomId": 10},
                
            ],
            "objects": [
                #O.spawn(""),
                #O.spawn(""),
                #O.spawn("")
            ],
            "mobs": [  
#                M.spawn("") ,
#                M.spawn(""),
#                M.spawn(""),
#                
            ],
        }
    ),  
}
