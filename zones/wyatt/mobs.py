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
    "Pink Nessie": {
        "name": "Pink Nessie",
        "key_words": ("Pink", "Nessie"),
        "room_description": "&gA very strange pink coloration of a Nessie.&N",
        "description": (
            "It sits there... menacingly.\n"
            "Or it is just sitting there without a single thought in that head."
        ),
        "race": "Nessie",
        "class": "Animal",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": False,
    },
    "Green Nessie": {
        "name": "Green Nessie",
        "key_words": ("Green", "Nessie"),
        "room_description": "&CThe Nessie. It wades in the shallow water staring into space&N",
        "description": (
            "It is a very strange creature and sits there wisely\n"
            "Or it is just sitting there without a single thought in that head."
        ),
        "race": "Nessie",
        "class": "Animal",
        "level": 150000000000000000000000000000000000000000000000000000,
        "stats": [500000000000, 100, 100, 100, 100, 1000],
        "aggro": False,
        "wander": False,
    },
    "Alisa Macailnov": {
        "name": "Alisa Macailnov",
        "key_words": ("Alisa", "Macailnov"),
        "room_description": "Alisa keeps &Rev&Ger&Cyt&Bhi&Yng &Cshiny&N",
        "description": (
            "A woman that cleans and bartends simultaneously\n"
            "She talks to the customers swiftly; asking questions about them."
        ),
        "race": "human",
        "class": "Bartender",
        "level": 12,
        "stats": [64, 80, 78, 84, 87, 70],
        "aggro": False,
        "wander": False,
    },
    "Gobbles the Learnosaur": {
        "name": "Gobbles the Learnosaur",
        "key_words": ("Gobbles", "Learnosaur"),
        "room_description": "&MGobbles &Wsits here babbling about &+Rletters&N &Wand &CNumbers",
        "description": (
            "A dinosaur that plays with floating vowels\n"
            "He wanders around talking about learning"
        ),
        "race": "Learnosaur",
        "class": "Gobbles",
        "level": 21,
        "stats": [87, 80, 78, 84, 87, 63],
        "aggro": False,
        "wander": True,
    },
    "Pedro the Sea Urchin": {
        "name": "&WPedro the &CSea &WUrchin",
        "key_words": ("Pedro", "Urchin"),
        "room_description": "&WPedro rolls around asking everyone if they would like to play &WS&No&Wc&Nc&We&Nr &W with him as the ball",
        "description": (
            "A sea urchin that is rollable\n"
            "He asks people to play a game quite frequently"
        ),
        "race": "Urchin",
        "class": "Animal",
        "level": 9,
        "stats": [47, 56, 89, 67, 19, 29],
        "aggro": False,
        "wander": True,
    },
    "Doug the Heermit Crab": {
        "name": "&WDoug the &YHermit &RCrab",
        "key_words": ("Doug", "Hermit", "Crab"),
        "room_description": "&WDoug scuttles around with Pedro just following along like he doesn't give two craps about the world around him",
        "description": (
            "A Hermit Crab that is easily killable\n"
            "Why would you want to kill him you monster"
        ),
        "race": "Crab",
        "class": "Animal",
        "level": 6,
        "stats": [47, 56, 89, 67, 19, 29],
        "aggro": False,
        "wander": True,
    },
    "Flappers the Super Dolphin": {
        "name": "&CFlappers&N the &BSuper &WDolphin",
        "key_words": ("Flappers", "Super", "Dolphin"),
        "room_description": "&CFlappers &Wwanders around almost looking like he lives off of one single braincell\n He helps some individuals",
        "description": (
            "A dolphin that looks dumb yet powerful\n"
            "Don't even try man. It's not worth the kill gang"
        ),
        "race": "Dolphin",
        "class": "Animal",
        "level": 50,
        "stats": [98, 89, 92, 67, 43, 97],
        "aggro": False,
        "wander": True,
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
