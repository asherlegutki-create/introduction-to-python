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
    "green_marker": {
        "spawn_as":         Object,
        "name":             "a &ggreen expo marker&N",
        "key_words":        ("green", "expo", "marker"),
        "room_description": "a {g&wgreen expo marker&N has been carelessly discarded here.",
        "description":      "A forest green low-scent dry-erase marker, about half used.",
    },

    "sack_of_darkness": {
        "spawn_as":         Item,
        "name":             "a sack of darkness",
        "key_words":        ("darkness", "sack"),
        "room_description": "A plain looking sack lies on the ground.",
        "description":      "The bag looks simple. It is a brown canvas. When you look inside you see a black void.",
        "weight":           2,
    },
    "sword_that_seals_the_darkness" : {
        "spawn_as":         Weapon,
        'name': "&WT&Yh&We &YS&Ww&Yo&Wr&Yd &Wt&Yh&Wa&Yt &WS&Ye&Wa&Yl&Ws &Yt&Wh&Ye &RDarkness&N",
        'key_words': ('sword', 'seals', 'darkness'),
        'room_description': "&WT&Yh&We &YS&Ww&Yo&Wr&Yd &Wt&Yh&Wa&Yt &WS&Ye&Wa&Yl&Ws &Yt&Wh&Ye &WD&Ya&Wr&Yk&Wn&Ye&Ws&Ys&N lies here. Its light &Cilluminates&N the ground around it.",
        'description': "The sword is beautiful. It was forged by the Elves as a tool against the Great Darkness. It glows softly with divine, bluish light",
        "weight":           5,
        "dice":             "6d8",
        "hitroll":          4,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
