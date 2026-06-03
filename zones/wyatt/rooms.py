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
                {"direction": "up", "roomId": 6},
            ],
            "objects": [
                O.spawn("Sword of Coral"),
            ],
            "mobs": [
                M.spawn("Flappers the Super Dolphin"),
            ],
        }
    ),
    6: Room(
        {
            "number": 6,
            "name": "Oceania beach",
            "description": "&WA &yBeach &W with a buried metal sign that says &BOceania &yBeach&N",
            "indoors": False,
            "terrain": "sand",
            "exits": [
                {"direction": "north", "roomId": 7},
                {"direction": "down", "roomId": 5},
            ],
            "objects": [],
            "mobs": [],
        }
    ),
    7: Room(
        {
            "number": 7,
            "name": "Poison Forest Path",
            "description": "&WIt is a long &GForest path &Wthat seems to lead somewhere strange&N",
            "indoors": False,
            "terrain": "dirt, wood",
            "exits": [
                {"direction": "west", "roomId": 8},
                {"direction": "south", "roomId": 6},
            ],
            "objects": [],
            "mobs": [
                M.spawn("Poison Thorn Bush"),
                M.spawn("Poison Thorn Bush"),
                M.spawn("Poison Thorn Bush"),
            ],
        }
    ),
    8: Room(
        {
            "number": 8,
            "name": "&GForest&N Arena",
            "description": "&WIt is a large arena, around 4.5 football fields, with a &mpurple crystal &Wcenter and two stone pillars displaying health&N",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "east", "roomId": 7},
                {"direction": "north", "roomId": 9},
            ],
            "objects": [
                O.spawn("Arm canon"),
            ],
            "mobs": [
                M.spawn("Malice"),
                M.spawn("Mayhem"),
            ],
        }
    ),
    9: Room(
        {
            "number": 9,
            "name": "Oak Forest Path",
            "description": "&WA narrow path in the forest right next to the &GForest Arena&N. &WIt is almost overgrown and seems like it has been unkempt for years.&N",
            "indoors": False,
            "terrain": "dirt, wood",
            "exits": [
                {"direction": "south", "roomId": 8},
                {"direction": "west", "roomId": 10},
            ],
            "objects": [O.spawn("AAA Battery")],
            "mobs": [M.spawn("Skellington")],
        }
    ),
    10: Room(
        {
            "number": 10,
            "name": "&YSand &WDunes&N",
            "description": "&WIt is a &YSand Dune &W desert that has some small and large footsteps in the &Ysand&N&N",
            "indoors": False,
            "terrain": "sand, dirt",
            "exits": [
                {"direction": "east", "roomId": 9},
            ],
            "objects": [],
            "mobs": [],
        }
    ),
    11: Room(
        {
            "number": 11,
            "name": "&yOak &CVillage&N",
            "description": "&WIt is a small &yOak &CVillage &Wwith around 15-20 villagers&N",
            "indoors": False,
            "terrain": "wood, dirt",
            "stone"
            "exits": [
                {"direction": "west", "roomId": 9},
            ],
            "objects": [],
            "mobs": [
                M.spawn("Villager"),
                M.spawn("Villager"),
                M.spawn("Villager"),
                M.spawn("Villager"),
                M.spawn("Villager"),
            ],
        }
    ),
}
