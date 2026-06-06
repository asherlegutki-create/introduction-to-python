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
    "AAA Battery": {
        "spawn_as": Item,
        "name": "a &CAAA &GBattery&N",
        "key_words": ("AAA", "Battery"),
        "room_description": "A &CAAA &GBattery&N lies here, discarded.",
        "description": "The battery seems worn",
        "weight": 1,
    },
    "Dragons Talon": {
        "spawn_as": Weapon,
        "name": "&Ga &Ws&Nh&Wa&Nrp&We&Ns&Wt &N&Rrusty&N karambit knife&N",
        "key_words": ("Dragons", "Talon", "knife"),
        "room_description": "&WA rusty&N &Ckarambit knife&N &Wthat is a&N &Rreddish&N color and &Gfolds.&N",
        "description": """&+gIts blade is made of a crystalline structure that has been carefully molded
&+git has a weird glow whenever danger is near
&+gor it does it randomly&N""",
        "weight": 1,
        "dice": "2d8",
        "hitroll": 2,
        "damroll": 4,
    },
    "Glass": {
        "spawn_as": Item,
        "name": "a &WGlass&N",
        "key_words": ("Glass"),
        "room_description": "&W a &wclear &Gglass for &Cdrinking",
        "description": "&W a &wclear &Gglass",
        "weight": 0.3,
    },
    "Arm canon": {
        "spawn_as": Weapon,
        "name": "&WDouble barrel &Rarm&N canon",
        "key_words": ("Arm", "canon", "double"),
        "room_description": "&WAn {m&RArm canon{n &Wthat is able to sit on your arm lays here... obviously.",
        "description": """&WIt's&N canon &Wis of &Mmagenta &Wcoloration and is a &Cstrong, &Wlightweight&N metal.
&WIt looks like it can shoot &Ybullets &Wof pure {m&Mplasma&N
&WIt is &Mmagenta&N, not &Rpink&N""",
        "weight": 7,
        "dice": "4d8",
        "hitroll": 1,
        "damroll": 2,
    },
    "Uranium Rod": {
        "spawn_as": Item,
        "name": "&GRadioactive Uranium&N rod",
        "key_words": ("Radioactive", "Uranium", "rod"),
        "room_description": "&WA {g&WRadioactive Uranium&N rod &Wlies here. please do not go near it.",
        "description": "A &GRadioactive Uranium&N rod&W. what else to explain&N",
        "weight": 2,
    },
    "Sword of Coral": {
        "spawn_as": Weapon,
        "name": "&WA &CSword &Wof &+RC&+Yo&+Cr&+Ba&+Ml",
        "key_words": ("Sword", "Coral", "sc"),
        "room_description": "&WA &CSword &Wof &+RC&+Yo&+Cr&+Ba&+Ml &Wlays here untouched, or mildly worn",
        "description": """&WA sword made out of various colorations of &+RC&+Yo&+Cr&+Ba&+Ml
&WIt seems strong yet weak
&WVery colorful as well&N""",
        "weight": 7,
        "dice": "4d4",
        "hitroll": 2,
        "damroll": 4,
    },
    "Gold Engraved Helmet": {
        "spawn_as": Item,
        "name": "&XA &YGold &REngraved&N Helmet",
        "room_desc": "&XA &YGold &REngraved&N Helmet &Wlies here&N",
        "key_words": ("Gold", "Engraved", "Helmet"),
        "description": (
            "&WA&N titanium helmet &Rengraved &Wwith &YGold&N  "
            "&WIt is pretty heavy, but also light due to the&N titanium"
        ),
        "wear_on": "head",
        "armor_type": "engraved",
        "ac_bonus": 30,
        "weight": 19.0,
        "cost": 95,
        "stat_mods": {"str": 7},
        "save_mods": {"par": 3},
    },
    "Gold Engraved Chestplate": {
        "spawn_as": Item,
        "name": "&XA &YGold &REngraved&N Chestplate",
        "room_desc": "&XA &YGold &REngraved&N Chestplate &Wlies here&N",
        "key_words": ("Gold", "Engraved", "Chestplate"),
        "description": (
            "&WA&N titanium chestplate &Rengraved &Wwith &YGold&N  "
            "&WIt is pretty heavy, but also light due to the&N titanium"
        ),
        "wear_on": "on_body",
        "armor_type": "engraved",
        "ac_bonus": 40,
        "weight": 28.0,
        "cost": 185,
        "stat_mods": {"str": 10},
        "save_mods": {"par": 6},
    },
    "Gold Engraved Leggings": {
        "spawn_as": Item,
        "name": "&XSome &YGold &REngraved&N Leggins",
        "room_desc": "&XSome &YGold &REngraved&N Leggings &Wlie here&N",
        "key_words": ("Gold", "Engraved", "Leggings"),
        "description": (
            "&WSome&N titanium leggings &Rengraved &Wwith &YGold&N  "
            "&WThey cover your legs well"
        ),
        "wear_on": "legs",
        "armor_type": "engraved",
        "ac_bonus": 35,
        "weight": 25.0,
        "cost": 155,
        "stat_mods": {"str": 8},
        "save_mods": {"par": 4},
    },
    "Gold Engraved Vambraces": {
        "spawn_as": Item,
        "name": "&XSome &YGold &REngraved&N Vambraces",
        "room_desc": "&XSome &YGold &REngraved&N Vambraces &Wlie here&N",
        "key_words": ("Gold", "Engraved", "vambraces"),
        "description": (
            "&WSome&N titanium vambraces &Rengraved &Wwith &YGold&N  "
            "&WThey are just for show"
        ),
        "wear_on": "arms",
        "armor_type": "engraved",
        "ac_bonus": 9,
        "weight": 4.0,
        "cost": 50,
        "stat_mods": {"str": 0},
        "save_mods": {"par": 0},
    },
    "Gold Engraved Boots": {
        "spawn_as": Item,
        "name": "&XSome &YGold &REngraved&N Boots",
        "room_desc": "&XSome &YGold &REngraved&N Boots &Wlie here&N",
        "key_words": ("Gold", "Engraved", "Boots"),
        "description": (
            "&WSome&N titanium boots &Rengraved &Wwith &YGold&N  " "&WJust boots"
        ),
        "wear_on": "feet",
        "armor_type": "engraved",
        "ac_bonus": 12,
        "weight": 13.0,
        "cost": 75,
        "stat_mods": {"str": 1},
        "save_mods": {"par": 0},
    },
    "Gold Engraved Gauntlets": {
        "spawn_as": Item,
        "name": "&XSome &YGold &REngraved&N Gauntlets",
        "room_desc": "&XSome &YGold &REngraved&N Gauntlets &Wlie here&N",
        "key_words": ("Gold", "Engraved", "Gauntlets"),
        "description": (
            "&WSome&N titanium gauntlets &Rengraved &Wwith &YGold&N  "
            "&WLight gauntlets"
        ),
        "wear_on": "hands",
        "armor_type": "engraved",
        "ac_bonus": 5,
        "weight": 2.0,
        "cost": 35,
        "stat_mods": {"str": 3},
        "save_mods": {"par": 0},
    },
    "Velvet and Fur Cape": {
        "spawn_as": Item,
        "name": "&XA &rVelvet &yFur &CCape",
        "room_desc": "&XA &rVelvet &yFur &CCape &Wlies here&N",
        "key_words": ("Gold", "Engraved", "Boots"),
        "description": (
            "&WA &rVelvet &yFur &CCape that looks pretty&N  "
            "&WIt is a cape just for show"
        ),
        "wear_on": "about_body",
        "armor_type": "fur_guilded",
        "ac_bonus": 0,
        "weight": .3,
        "cost": 5,
        "stat_mods": {"str": 0},
        "save_mods": {"par": 0},
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
