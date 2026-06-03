"""
zones.Oakhurst.objects
──────────────────────
Object templates for The Planes zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "object_template": {
        "spawn_as":         Object,
        "name":             "object",
        "key_words":        ("1", "2",),
        "room_description": "object is here.",
        "description":      "can't take.",
    },
    "Item_template": {
        "spawn_as":         Item,
        "name":             "item",
        "key_words":        ("1", "2",),
        "room_description": "item sets here.",
        "description":      "can take.",
    },
    "Weapon_template" : {
        "spawn_as":         Weapon,
        'name': "thing",
        'key_words': ("1", "2"),
        'room_description': "a weapon sets here.",
        'description': "bonk",
        "weight":           3,
        "dice":             "2d8",
        "hitroll":          2,
        "damroll":          4,
    },



    "Assorted_Bottles__Full": {
        "spawn_as":         Item,
        "name":             "Assorted bottles",
        "key_words":        ("bottles"),
        "room_description": "A few &gc&Bo&Yl&Co&Mr&Rf&Gu&bl&N &Wglass&N &Yb&co&mt&rt&gl&Be&Ms&N are on the &ycounter&N of the bar, they are all filled with different kinds of liquids.",
        "description":      "Five assorted &gc&Bo&Yl&Co&Mr&Rf&Gu&bl&N and &yunlabeled&N &Wglass bottles&N are siting on the counter.\nIt might &rnot&N be the best idea to drink these,as you don't know what is in them, but you do you.",
    },
    "Silver_Sword" : {
        "spawn_as":         Weapon,
        'name': "Silver Sword",
        'key_words': ("sword", "silver", "silver sword"),
        'room_description': "A &Wsilver sword&N rests against the side of the bar.",
        'description': "A &Wsilver sword&N leans, abandoned, against the tavern's counter.\nIt seems it would be effective against &rc&Xr&re&Xa&rt&Xu&rr&Xe&rs &Xo&rf &Xt&rh&Xe &rn&Xi&rg&Xh&rt&N",
        "weight":           3,
        "dice":             "1d6",
        "hitroll":          2,
        "damroll":          2,
    },

    
"Giant_Pine_Tree": {
        "spawn_as":         Object,
        "name":             "Giant Oak Tree",
        "key_words":        ("oak", "tree",),
        "room_description": "An extremely large &goak tree&N sits deeply rooted in the center of the courtyard.",
        "description":      "This &ggiant oak&N towers over all else near it, it's &gb&yr&ga&yn&gc&yh&ye&gs&N covering the courtyard in a pleasant dappled shade.\nIts &yroots&N have started to disrupt some of the &Xcobblestone bricks&N in the path surrounding it.",
    },
    "Tables": {
        "spawn_as":         Object,
        "name":             "empty tables",
        "key_words":        ("table", "tables"),
        "room_description": "A few &ytables&N are strewn about the &Ggrass&N, all but one are empty.",
        "description":      "Four &ytables&N with varying amounts of &ychairs&N sit in the &Ggrassy&N part of the courtyard.\nAt one rests a solitary rouge, the rest remain empty.",
    },
   "Wyldflowers": {
        "spawn_as":         Item,
        "name":             "Wyldflowers",
        "key_words":        ("wyldflowers","flowers",),
        "room_description": "Sparse patches of &YW&yy&Wl&Yd&yf&Wl&Yo&yw&We&Yr&ys&N are dotted around the courtyard.",
        "description":      "As you look closer at one of the smatterings of &YW&yy&Wl&Yd&yf&Wl&Yo&yw&We&Yr&ys&N you see that they are ruffled and delicate, about the size of a adult human's palm.\nIt seems the &Yf&yl&Wo&Yw&ye&Wr&Ys&N come in three distinct colors: &Yyellow&N, &yorange&N, and &Wwhite&N.",
    },


  

    
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
