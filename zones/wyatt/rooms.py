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
            "name": "Crystal Caverns",
            "description": "&WIt is a&N dark &Wcave with minimal light coming off of the luminescent&N &Ccrystals&N.\nThe &Ccrystals&N are of &rv&ga&Cr&Bi&Ro&Yu&Gs&N &Wcolors&N",
            "indoors": True,
            "terrain": "rock",
            "exits": [
                {"direction": "west", "roomId": 99005, "external": True},
                {"direction": "south", "roomId": 2},
            ],
            "objects": [
                O.spawn("Dragons Talon"),
                O.spawn("Arm canon"),
                O.spawn("Uranium Rod"),
            ],
            "mobs": [M.spawn("Green Nessie")],  # two independent students
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "Travelers Tavern",
            "description": "&WA &rsmall &Wbuilding that says '&CT&Gr&Ya&Rv&Be&rl&ge&Wr&ws &CTavern'&N &Wright on the top\nIt seems old",
            "indoors": True,
            "terrain": "wood",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "west", "roomId": 3},
            ],
            "objects": [
                O.spawn("Glass"),
                O.spawn("Glass"),
                O.spawn("Glass"),
                O.spawn("Glass"),
                O.spawn("Glass"),
            ],
            "mobs": [M.spawn("Alisa Macailnov")],  # two independent students
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "&Clearning &GJu&gng&Gle",
            "description": "&WIt is a jungle that has, what almost seems like, an unlimited amount of trees and shrubs\n It goes pretty far",
            "indoors": False,
            "terrain": "dirt",
            "exits": [
                {"direction": "east", "roomId": 2},
                {"direction": "north", "roomId": 4},
            ],
            "objects": [],
            "mobs": [
                M.spawn("Gobbles the Learnosaur"),
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "&CW&Ba&Ct&Be&Cr &GWorld&N",
            "description": "&WA &Gworld &Wof endless &CW&Ba&Ct&Be&Cr\n&WIt has tons of life ",
            "indoors": False,
            "terrain": "water",
            "exits": [
                {"direction": "north", "roomId": 5},
                {"direction": "south", "roomId": 3},
            ],
            "objects": [],
            "mobs": [
                M.spawn("Pedro the Sea Urchin"),
                M.spawn("Doug the Hermit Crab"),
            ],
        }
    ),
    5: Room(
        {
            "number": 5,
            "name": "&RC&Co&Gr&Ya&Ml &WReef City",
            "description": "&WA city with hundreds of sea creature civilians around&N",
            "indoors": False,
            "terrain": "water, rock",
            "exits": [
                {"direction": "south", "roomId": 4},
            ],
            "objects": [O.spawn("Sword of Coral"),],
            "mobs": [
                M.spawn("Flappers the Super Dolphin"),
            ],
        }
    ),
}
