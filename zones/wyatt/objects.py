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
    "Titan Battery": {
        "spawn_as": Item,
        "name": "a &CTitan &GBattery&N",
        "key_words": ("Titan", "Battery"),
        "room_description": "A &CTitan &GBattery&N lies here, discarded.",
        "description": "The battery seems worn",
        "weight": 7,
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
        "dice": "20d40",
        "hitroll": 36,
        "damroll": 50,
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
        "dice": "40d80",
        "hitroll": 12,
        "damroll": 24,
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
