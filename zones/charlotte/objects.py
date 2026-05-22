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
        "spawn_as": Item,
        "name": "a &ggreen&N &Gleaf&N",
        "key_words": ("green", "leaf"),
        "room_description": "a &Gg&N&gr&N&Ge&N&ge&N&Gn&N &gl&N&Ge&N&ga&N&Gf&N has been carelessly &Rdiscarded&N here.",
        "description": "A forest green leaf is lying on the ground.",
    },

    "Banana": {
        "spawn_as": Item,
        "name": " &Ybanana&N",
        "key_words": ("banana"),
        "room_description": "A &Yb&N&ya&N&Yn&N&yn&N&Ya&N&yn&N&Yn&N&yn&N&Ya&N is hanging of a &Gb&N&gu&N&Gs&N&gh&N.",
        "description": "This &Yb&N&ya&N&Yn&N&yn&N&Ya&N&yn&N&Yn&N&yn&N&Ya&N seems to be very tasty.",
    },

    "The Fruit": {
        "spawn_as": Item,
        "name": "&RT&N&Yh&N&Ge&N &CF&N&Rr&N&Yu&N&Gi&N&Ct&N",
        "key_words": ("Fruit"),
        "room_description": "The &CF&N&Rr&N&Yu&N&Gi&N&Ct&N is hanging from a branch on a tree.",
        "description": "This is the &CF&N&Rr&N&Yu&N&Gi&N&Ct&N that Adam and Eve ate. This &CF&N&Rr&N&Yu&N&Gi&N&Ct&N caused the first sin.",
    },

    "The Horn": {
        "spawn_as": Item,
        "name": "&WH&N&wo&N&Wr&N&wn&N",
        "key_words": ("Horn"),
        "room_description": "The &WH&N&wo&N&Wr&N&wn&N is on a table in an Israelite tent.",
        "description": "The &WH&N&wo&N&Wr&N&wn&N has been use to make loud noises while marching around the city of Jericho.",
    },

    "Tunic": {
        "spawn_as": Item,
        "name": " &WIsraelite Tunic&N",
        "key_words": ("Tunic","Israelite"),
        "room_description": "A &WIsraelite Tunic&N is folded nicely on a bench.",
        "description": "This &WIsraelite Tunic&N will disguise you to look like a Israelite because a &WTunic&N is what was mainly worn back in the day.",
    },

     "Holy Grail": {
        "spawn_as": Item,
        "name": "The Holy Grail",
        "key_words": ("Holy","Grail"),
        "room_description": "The Holy Grail sits at one end of the table in the middle of the room.",
        "description": "This is the cup that Jesus Christ drank from during the passover. /n It looks just like any other clay cup from back then, but is said to have healing powers.",
    },

     "Bread": {
        "spawn_as": Item,
        "name": " Unleaven Bread",
        "key_words": ("Unleaven","Bread"),
        "room_description": "The bread is stacked neatly on the table.",
        "description": "The bread was broken and given to Judas. Judas than ran away to the temple to help the pharasees capture Jesus Christ./n The bread represents the body of Jesus. ",
    },

     "Wine": {
        "spawn_as": Item,
        "name": "Wine",
        "key_words": ("Wine"),
        "room_description": "The Wine is sitting on the table next to the bread.",
        "description": " The bread was broken and dipped into the wine.The wine represents the blood of Jesus",
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
