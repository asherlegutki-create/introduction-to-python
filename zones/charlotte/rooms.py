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
            "name": "&GGarden&N of &gEden&N",
            "description": "&GThere&N &gis&N &Ga huge garden&N streching for miles.There is a &Gtree&N in the &gmiddle of the Garden&N.\n &YG&N&yo&N&Yd&N is watching over his creation.",
            "indoors": False,
            "terrain": "rolling grass hills",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "west", "roomId": 99002, "external": True}
                
            ],
            "objects": [
                O.spawn("Banana"),
                O.spawn("green leaf"),
                O.spawn("The Fruit"),
            ],
            "mobs": [
                M.spawn("Adam") ,
                M.spawn("Eve"),
                M.spawn("Slippery Serpant")],  # two independent students

        }
    ),
2: Room(
        {
            "number": 2,
            "name": "&CJ&N&ce&N&Cr&N&ci&N&Cc&N&ch&N&Co&N",
            "description": "&wThis is a city with a huge wall going around it to protect it.&N",
            "indoors": False,
            "terrain": "grass plane",
            "exits": [
                {"direction": "south", "roomId": 1},
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
