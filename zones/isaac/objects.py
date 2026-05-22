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

# Types of Items: Weapon, Item, Object

TEMPLATES: dict[str, dict] = {
    "traffic_cone": {
        "spawn_as": Weapon,
        "name": "A &ytraffic cone&N",
        "key_words": ("traffic", "cone"),
        "room_description": "A &ytraffic cone&N blocks your path.",
        "description": (
            "    The &ycone&N, as a weapon, can be worn like a boxing glove for stabbing.",
            "It can also be used as a trumpet for loud deafening blasts or for sweet symphonies.",
        ),
        "weight": 2,
        "dice": "1d4",
        "hitroll": 2,
        "damroll": 1,
    },
    "street_lamp": {  # finish
        "spawn_as": Object,
        "name": "A &Xstreet&N &Ylamp&N",
        "key_words": ("street", "lamp", "lamppost"),
        "room_description": "A &Xstreet&N &Ylamp&N stands tall, &Yilluminating&N the room.",
        "description": (
            "The &Xstreet&N &Ylamp&N is made from durable black steel.\n"
            "No one knows what the lamp looks like, because it is too bright."
        ),
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
