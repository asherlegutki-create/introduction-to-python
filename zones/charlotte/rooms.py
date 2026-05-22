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
            "name": "The &CO&N&Bf&N&Cf&N&Bi&N&Cc&N&Be&N",#this is the office
            "description": "The office is where &BM&N&R&R&N&BS&N&R.S&N&Bt&N&Ra&N&Bc&N&Re&N&By&N stays during the day. The Office is at the front of the school./n To the left is Mr. Carlson's Office. To the right is a wall with pictures of all the teachers. Up is the celling with lose tiles that might be moveable./n Down is the carpet floor not for much use. Forward is a pack hall way.",
            "indoors": True,                        #Mrs.Stacey^
            "terrain": "carpet floor",
            "exits": [
                {"direction": "west", "roomId": 2},
                {"direction": "down", "roomId": 99002, "external": True}
                
            ],
            "objects": [
              #  O.spawn("Pencil"),
            #    O.spawn("Key"),
              #  O.spawn("Computer"),
            ],
            "mobs": [
               # M.spawn("MRS.Stacey") ,
               # M.spawn("MRS.Stublefield"),],  # two independent students

        }
    ),
2: Room(
        {
            "number": 2,
            "name": "",
            "description": "&wThis is a city with a huge wall going around it to protect it.&N",
            "indoors": False,
            "terrain": "grass plane",
            "exits": [
                {"direction": "east", "roomId": 1},
                {"direction": "north", "roomId": 3},
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
            "name": "&wU&N&Wp&N&wp&N&We&N&wr&N &WR&N&Wo&N&wo&N&Wm&N",
            "description": "&WThis is the very room that Jesus and his disciples ate in during the last supper.&N",
            "indoors": True,
            "terrain": "Clay floor",
            "exits": [
                {"direction": "south", "roomId": 2},
                {"direction": "north", "roomId": 4},
            ],
            "objects": [
                O.spawn("Holy Grail"),
                O.spawn("Bread"),
                O.spawn("Wine")
            ],
            "mobs": [  
#                M.spawn("Jesus") ,
#                M.spawn("Peter"),
#                M.spawn("Matthew"),
#                M.spawn("Judas"),
#                M.spawn("John 1"),
#                M.spawn("John 2"),
#                M.spawn("Andrew"),
#                M.spawn("James"),
#                M.spawn("Philip"),
#                M.spawn("Bartholomew"),
            ],
        }
    ),
}
