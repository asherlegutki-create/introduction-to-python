"""
zones.the_void.mobs
───────────────────
Mob templates for The Void zone.

Add an entry to TEMPLATES for every NPC type that can appear in this zone.
Call spawn(key) to get a fresh independent Mob instance — place as many
copies in rooms as you like, each is independent.
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "&MIllrigger Mage&N": {
        "name": "Illrigger",
        "key_words": ("illrigger", "mage"),
        "room_description": "&MIllriggers &Wwander these parts, searching for any intruders.&N",
        "description": (
            "&MIllrigger Mage, &Wit is clearly mastering the arts of &xDark Magic&N."
        ),
        "race": "Illrigger",
        "class": "Mage",
        "level": 18,
        "stats": [25, 12, 35, 72, 45, 10],
        "aggro": True,
        "wander": True,
        "killable": True,

    },
        
        "&RIllrigger Rogue&N": {
        "name": "Illrigger Rogue" ,
        "key_words": ("illrigger", "rogue"),
        "room_description": "&RIllriggers &Wwander these parts, searching for any intruders.&N",
        "description": (
            "&xIllrigger Rogue, &Wit's trying to guard the chest room&N",
        ),
        "race": "Illrigger",
        "class": "Rogue",
        "level": 12,
        "stats": [25, 19, 35, 62, 45, 10],
        "aggro": True,
        "wander": True,
        "killable": True,

    },
    
     "&yImprisoned Illrigger&N": {
        "name": "&yImprisoned Illrigger&N" ,
        "key_words": ("imprisoned", "illrigger"),
        "room_description": "You found this &yIllrigger&N in his cell in the Prison Room.",
        "description": (
            "this &yIllrigger&N is sulking in his cell, pondering, planning his revenge",
        ),
        "race": "Illrigger",
        "class": "Bard",
        "level": 24,
        "stats": [55, 79, 53, 62, 85, 10],
        "aggro": False,
        "wander": False,
        "killable": True,
        "responses": {
            "hi": ("the Imprisoned Illrigger Bard looks at you with irritation.",
                   "He asks you '&wthey put you in here too? Tch, typical&N'"),
            "prison": ("He replies'&wI saw the &YKing &MSlime&N, &wI failed to play for him, but I will have my revenge&N.'"
                   "he looks at you again '&wBut I guess you want to know where the &YKing &MSlime&N is, huh?&N'"),
            "loser": ("he gets up, his blood is &Rboiling with rage&N 'WHAT DID YOU SAY, SHORTSTACK?!'"),
            "cell": ("He replies'&wI saw the &YKing &MSlime&N, &wI failed to play for him, but I will have my revenge&N.'"
                   "he looks at you again '&wBut I guess you want to know where the &YKing &MSlime&N is, huh?&N'"),
            "directions": ("He sighs, deeply '&wif you go to the entrance, then go up, then go to the guest room with the &Ggreen bed&N. There you'll find multiple secret rooms'"),
            }

    },

    "&MPink Slime&N": {
        "name": "Pink Slime" ,
        "key_words": ("pink", "slime"),
        "room_description": "&Mpink&N sticky blobs of slimes, they're filled with &GX&MP&N",
        "description": (
            "Slimy idiots with zero intelligence...",
        ),
        "race": "Unknown",
        "class": "Unknown",
        "level": 3,
        "stats": [0, 0, 0, 0, 1, 0],
        "aggro": False,
        "wander": True,
        "killable": True,
    },

    "&BBlue Slime&N": {
        "name": "Blue Slime" ,
        "key_words": ("blue", "slime"),
        "room_description": "&Bblue&N sticky blobs of slimes, they're filled with &GX&MP&N, and appearently bigger than the &MPink Slime&N",
        "description": (
            "Slimy idiots with zero intelligence...",
        ),
        "race": "Unknown",
        "class": "Unknown",
        "level": 5,
        "stats": [1, 1, 1, 0, 2, 0],
        "aggro": False,
        "wander": True,
        "killable": True,
    },

    "&GGreen Slime&N": {
        "name": "Green Slime" ,
        "key_words": ("green", "slime"),
        "room_description": "&GGreen&N sticky blobs of slimes, they're filled with &GX&MP&N, and appearently bigger than both the &BBlue Slime&N and the &MPink Slime&N",
        "description": (
            "Slimy idiots with zero intelligence...",
        ),
        "race": "Unknown",
        "class": "Unknown",
        "level": 7,
        "stats": [2, 2, 2, 0, 3, 0],
        "aggro": False,
        "wander": True,
        "killable": True,
    },

    "&YKing &MSlime&N": {
        "name": "King Slime" ,
        "key_words": ("king", "slime"),
        "room_description": "oooh! a boss battle with a hefty reward of &GX&MP...",
        "description": (
            "the King of the Slimy idiots with zero intelligence...",
        ),
        "race": "Unknown",
        "class": "Unknown",
        "level": 89,
        "stats": [78, 45, 98, 69, 78, 0],
        "aggro": True,
        "wander": True,
        "killable": True,
    },

    "Zombie": {
        "name": "Zombie" ,
        "key_words": ("zombie"),
        "room_description": "looks like these Zombies are hungry",
        "description": (
            "they may eat brains but I dont think it makes them smarter",
        ),
        "race": "Undead",
        "class": "Barbarian",
        "level": 30,
        "stats": [24, 45, 38, 29, 8, 0],
        "aggro": True,
        "wander": True,
        "killable": True,
    },

     "Cap": {
        "name": "Cap" ,
        "key_words": ("cap", "spirit"),
        "room_description": "looks like you found a stowaway",
        "description": (
            "Caps are little spirits that like hiding in chests"
        ),
        "race": "Spirit",
        "class": "Unknown",
        "level": 2,
        "stats": [4, 5, 8, 9, 3, 0],
        "aggro": False,
        "wander": False,
        "killable": True,
        "responses": {
            "hi": ("The Cap looks at you with big wide eyes, &Mmagenta&N body with tiny little wings.",
                   "'squeek!'"),
            "loser": ("it cries softly at you calling it a crude name"),
        },
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
