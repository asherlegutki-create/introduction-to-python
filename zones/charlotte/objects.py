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
    "green leaf": {
        "spawn_as": Object,
        "name": "a &ggreen&N &Gleaf&N",
        "key_words": ("green", "leaf"),
        "room_description": "a green leaf has been carelessly discarded here.",
        "description": "A forest green leaf is lying on the ground.",
    },

    "Banana": {
        "spawn_as": Object,
        "name": " &Ybanana&N",
        "key_words": ("banana"),
        "room_description": "A &Yb&N&ya&N&Yn&N&yn&N&Ya&N&yn&N&Yn&N&yn&N&Ya&N is hanging of a &Gb&N&gu&N&Gs&N&gh&N.",
        "description": "This banana seems to be very tasty.",
    },

    "The Fruit": {
        "spawn_as": Object,
        "name": "&RT&N&Yh&N&Ge&N &CF&N&Rr&N&Yu&N&Gi&N&Ct&N",
        "key_words": ("Fruit"),
        "room_description": "The Fruit is hanging from a branch on a tree.",
        "description": "This is the Fruit that adam and eve ate. THis fruit caused the first sin.",
    },

    "The Horn": {
        "spawn_as": Object,
        "name": "Horn",
        "key_words": ("Horn"),
        "room_description": "The Horn is on a table in an Israelite tent.",
        "description": "The Horn has been use to make loud noises while marching around the city of Jericho.",
    },

    "Tunic": {
        "spawn_as": Object,
        "name": " Israelite Tunic",
        "key_words": ("Tunic","Israelite"),
        "room_description": "A Israelite Tunic is folden nicely on a bench.",
        "description": "This tunic will disguise you to look like a Israelite because a tunic is what was mainly worn back in the day.",
    },

     "Holy Grail": {
        "spawn_as": Object,
        "name": "The Holy Grail",
        "key_words": ("Holy","Grail"),
        "room_description": "The Holy Grail sits at one end of the table in the middle of the room.",
        "description": "This is the cup that Jesus Christ drank from during the passover. /n It looks just like any other clay cup from back then, but is said to have healing powers.",
    },

     "Bread": {
        "spawn_as": Object,
        "name": " Unleaven Bread",
        "key_words": ("Unleaven","Bread"),
        "room_description": "The bread is stacked neatly on the table.",
        "description": "The bread was broken and given to Judas. Judas than ran away to the temple to help the pharasees capture Jesus Christ./n The bread represents the body of Jesus. ",
    },

     "Wine": {
        "spawn_as": Object,
        "name": "Wine",
        "key_words": ("Wine"),
        "room_description": "The Wine is sitting on the table next to the bread.",
        "description": " The bread was broken and dipped into the wine.The wine represents the blood of Jesus",
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
