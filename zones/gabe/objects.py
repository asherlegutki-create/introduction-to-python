"""
zones.the_void.objects
──────────────────────
Object templates for The Void zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "cheese wheel": {
        "spawn_as":         Item,
        "name":             "a &Ya cheese wheel&N",
        "key_words":        ("cheese", "wheel"),
        "room_description": "a &Ya cheese wheel&N is laid here, looking very delicious.",
        "description":      "a delicious-looking wheel of cheese.",
        "weight":           5,
    },

    "toy cheese": {
        "spawn_as":         Object,
        "name":             "a toy cheese",
        "key_words":        ("toy", "cheese"),
        "room_description": "a &mtoy &Ycheese&N is lying on the ground here.",
        "description":      "A cheese-shaped toy, made of wood and painted yellow.\n It looks like it would be fun to throw.",
        "weight":           2,
    },
    "cheese surfboard": {
        "spawn_as":         Object,
        "name":             "a cheese surfboard",
        "key_words":        ("cheese", "surfboard"),
        "room_description": "a &Ycheese&N &Bsurf&N&yboard &Wis propped up against the wall here.&N",
        "description":      "A surfboard made of cheese. It looks like it would be fun to ride, but also like it would be very messy.",
        "weight":           10,
    },
    "cheese sack": {
        "spawn_as":         Object,
        "name":             "a cheese sack",
        "key_words":        ("cheese", "sack"),
        "room_description": "a &Ycheese sack&N is lying on the ground here.",
        "description":      "A sack made of cheese. It looks like it would be fun to carry things in, may also be fun to eat.",
        "weight":           3,
    },
    "cheese bucket": {
        "spawn_as":         Object,
        "name":             "a cheese bucket",
        "key_words":        ("cheese", "bucket"),
        "room_description": "a &Ycheese bucket&N is sitting here, filled with something that looks like more guess what? &Yc&N&yh&Ye&N&ye&Ys&N&ye&Y&N       .",
        "description":      "A bucket made of cheese. It looks like it would be fun to carry things in, may also be fun to eat.",
        "weight":           4,
    },
        "chez destroyer": {
        "spawn_as": Weapon,
        "name": "&Ychez&N &Rd&N&re&Rs&N&rt&Rr&N&ro&N&ry&Re&N&rr&N",
        "key_words": ("chez", "cheese", "destroyer"),
        "room_description": "the &Ychez&N &Rd&N&re&Rs&N&rt&Rr&N&ro&N&ry&Re&N&rr&N sits here thinking about the &Rarm&N &Wcanon&N",
        "description": "a &Ychez&N &Rd&N&re&Rs&N&rt&Rr&N&ro&N&ry&Re&N&rr&N is laying here",
        "weight": 5,
        "dice": "7d10",
        "hitroll": 4,
        "damroll": 8,
        "proc": "windsong",
        "powers": [
            {
                "keywords":       ("SolarSlash", "ss"),
                "name":           "Solar Slash",
                "cooldown_ticks": 4,
                "effect":         "apply_damage",
                "user_msg": (
                    "&W your &Ychez&N &Rd&N&re&Rs&N&rt&Rr&N&ro&N&ry&Re&N&rr&N &Wglows brightly&N as it unleashes a blazing slash!&N"
                    "&WThe air around the attack shimmers with intense &rheat&N, and a wave of &Rfire&N surges forward, engulfing the target in &Rf&N&rl&N&Ra&N&rm&N&Re&N&rs&N!&N"
                ),
                "room_msg": (
                    "&c wan_juans &Ychez&N &Rd&N&re&Rs&N&rt&Rr&N&ro&N&ry&Re&N&rr&N &Wglows brightly&N as it unleashes a blazing slash!&N"
                    "A &Rf&N&rl&N&Ra&N&rm&N&Re&N&rs&N!&N &cEnergy surges through it!&N"
                ),
            },
        ]

    },
    "cheese scroll": {
        "spawn_as": Item,
        "name": "a cheese scroll",
        "key_words": ("cheese", "scroll"),
        "room_description": "an &bunderwater&N &Ycheese scroll&N is lying on the ground here.",
        "description": "&WThis ancient scroll says that there is a secret &Rrecipe&N for the best&N &ycheese&N &Win the&N &Gw&N&Bo&N&Gr&N&Bl&N&Gd&N &Whidden somewhere in this zone. It also says that the recipe is written in a &gcode&N that can only be deciphered by someone who likes reading&N &bbooks&N.",
        "weight": 25,
     },
     "cheese book": {
        "spawn_as": Object,
        "name": "a cheese book",
        "key_words": ("cheese", "book"),
        "room_description": "an &bunderwater &Ycheese book&N is lying on the ground here.",
        "description": "This book is about cheese. It has pictures of different types of cheese.",
        "weight": 2,}

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
