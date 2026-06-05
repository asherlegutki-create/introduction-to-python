"""
zones.new_zone.objects
"""

from ashenmoor.world import Object, Item, Weapon, Container, Scroll, Potion
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "object_template": {
        "spawn_as":         Object,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
    },

    "item_template": {
        "spawn_as":         Item,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
        "weight":              0,
    },

    "treasure_chest": {
        "spawn_as":        Container,
        "name":            "&ya treasure chest&N",
        "key_words":       ("chest", "treasure"),
        "room_description":"A sturdy oak chest sits here.",
        "no_take":         True,       # can't pick it up
        "is_open":         False,      # starts closed
        "locked":          True,       # starts locked
        "key_name":        "chest key",
        "capacity":        50.0,
        "weight":          20.0,
        "contents": [                  # template keys — spawned automatically
           "windsong", "windsong",
            "cap", "visor", "armor", "cloak", "belt", "vambraces", "gloves", "leggings", "boots",
           "dimensional_vault",
           "stoneskin_scroll", "stoneskin_scroll", "stoneskin_scroll", "stoneskin_scroll", 
           "stoneskin_scroll", "stoneskin_scroll", "stoneskin_scroll" 
        ],
    },

    "chest_key": {
        "spawn_as":        Item,
        "name":            "&ya small brass key&N",
        "key_words":       ("key", "brass", "small"),
        "room_description":"A small &ybrass key&N lies here.",
        "is_key":          True,
        "key_name":        "chest key",   # must match chest's key_name exactly
        "weight":          0.1,
    },
    
    "heal_potion": {
    "spawn_as":    Potion,
    "name":    "a health potion",
    "key_words":       ("health", "potion"),
    "room_description":"A potion of health lies here.",
    "effect":  "heal",
    "heal_pct": 0.5,
},
#{
#    "type": "Potion",
#    "name": "a potion of fortitude",
#    "effects": [
#        {"effect": "heal",           "heal_pct": 0.4},
#        {"effect": "apply_barkskin", "duration": 8},
#        {"effect": "apply_stoneskin","duration": 8},
#    ],
#}


    "silken_sack": {
        "spawn_as":         Container,
        "name":             "a &rtattered &csilken sack&N",
        "key_words":        ("tattered", "silken", "sack"),
        "room_description": "A &rtattered &csilken sack&N lies here, discarded.",
        "description":      "This sack seems to be in an awful condition.",
        "capacity":            200.0,
        "weightless_capacity": 100.0,
        "weight":              0,
        "is_open":             True,
    },

    "dimensional_vault": {
        "spawn_as":            Container,
        "name":                "&La dimensional vault&N",
        "key_words":           ("dimensional", "vault"),
        "room_description":    "&LA dimensional vault floats here, humming softly.&N",
        "description":         "A shimmering vault that exists partially outside this dimension.\nIt can hold an extraordinary amount without adding to your burden.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
    },

    "stoneskin_scroll": {
        "spawn_as": Scroll,
        "name": "&wa &Lstoneskin&N &Yscroll&N",
        "key_words": ("parchment", "rolled", "stoneskin", "scroll"),
        "room_description": "&wa rolled up piece of &Yparchment&N lies here&N",
        "effects": [{"effect": "apply_stoneskin", "duration": 150},]

    },


    "windsong": {
        "spawn_as":         Weapon,
        "name":             "&ga &wg&Wl&N&wi&Wtt&N&wer&Wi&N&wng&N &gelven scimitar&N",
        "key_words":        ("scimitar", "elven", "glittering", "windsong"),
        "room_description": "&gA glittering elven scimitar lies here, humming softly.&N",
        "description": (
            "&gIts blade is encrusted with diamond dust.  This magically light\n"
            "&gelven blade glitters in the sunlight and seems to hum softly\n"
            "&gwhen wielded in battle.  Only a &WRanger&g may truly master it.&N"
        ),
        # Stats matching original: 3d4 base, +4 hit, +3 dam
        "dice":    "3d4",
        "hitroll": 4,
        "damroll": 3,
        "weight":  2,
        # Windsong proc: 1-in-33 chance per hit to fire extra swings.
        # Rangers only — non-rangers take damage and lose the weapon.
        # Grey Elf gets 3 bonus swings; Half Elf gets +2 on the first branch.
        "proc":    "windsong",
        # Active power — type 'windsong' or 'ws' while wielding.
        # Fires a guaranteed burst of extra swings (inner chaining still applies).
        # 4-tick (16 second) cooldown.
        "powers": [
            {
                "keywords":       ("windsong", "ws"),
                "name":           "Windsong",
                "cooldown_ticks": 4,
                "effect":         "windsong_burst",
                "user_msg": (
                    "&cYou channel your will through the scimitar — "
                    "&cw&Ca&N&cv&Ce&N&cs &Co&N&cf &Ce&N&cn&Ce&N&cr&Cg&N&cy&N&c "
                    "surge through the blade!&N"
                ),
                "room_msg": (
                    "&c{name}'s scimitar &Wflares&N&c as waves of "
                    "energy surge through it!&N"
                ),
            },
            {
                "keywords":       ("envenom", "en"),
                "name":           "Envenom",
                "cooldown_ticks": 3,
                "effect":         "apply_poison",
                "duration":       8,
                "dot_dice":       "1d6",
                "user_msg":       "&cYou envenom your strike with deadly poison!&N",
                "room_msg":       "&c{name} envenoms their strike with poison!&N",
            }
        ],
    },
    "cap" : {
        "spawn_as":        Item,
        "name":        "&Xa sturdy &N&yleather &Xcap&N",
        "room_desc":   "&XA sturdy &N&yleather &Xcap has been left here.&N",
        "key_words":   ("cap", "leather", "hat"),
        "description": (
            "A well-stitched leather cap with a short brim.  "
            "Simple, tough, and shaped to fit snugly without blocking your sight."
        ),
        "wear_on":   "head",
        "ac_bonus":  4,
        "weight":    1.0,
        "cost":      15,
        "stat_mods": {"dex": 5},
        "save_mods": {},
    },

    # ── FACE — 1 AC ──────────────────────────────────────────────────────────
    "visor" : {
        "spawn_as":        Item,
        "name":        "&Xa sturdy &N&yleather &Xvisor&N",
        "room_desc":   "&XA sturdy &N&yleather &Xvisor has been left here.&N",
        "key_words":   ("visor", "leather", "mask", "face"),
        "description": (
            "A narrow strip of hardened leather that guards the brow and cheeks.  "
            "Reinforced rivets run along the edge."
        ),
        "wear_on":   "face",
        "ac_bonus":  1,
        "weight":    0.5,
        "cost":      12,
        "stat_mods": {"dex": 3, "con": 2},
        "save_mods": {},
    },

    # ── ON_BODY — 15 AC ───────────────────────────────────────────────────────
    # armor_type gives the base AC from the armor table (studded = 40 + DEX).
    # ac_bonus is added on top of that.
    "armor" : {
        "spawn_as":        Item,
        "name":        "&Xa studded &N&yleather &Xarmor&N",
        "room_desc":   "&XA studded &N&yleather &Xarmor has been left here.&N",
        "key_words":   ("studded", "armor", "leather", "jacket"),
        "description": (
            "Thick hide stitched with close-set metal studs.  "
            "Heavier than plain leather but still light enough to move freely."
        ),
        "wear_on":    "on_body",
        "armor_type": "studded",
        "ac_bonus":   15,
        "weight":     13.0,
        "cost":       95,
        "stat_mods":  {"str": 3},
        "save_mods":  {"par": 1},
    },

    # ── ABOUT_BODY — 4 AC ─────────────────────────────────────────────────────
    "cloak" : {
        "spawn_as":        Item,
        "name":        "&Xa sturdy &N&yleather &Xcloak&N",
        "room_desc":   "&XA sturdy &N&yleather &Xcloak has been left here.&N",
        "key_words":   ("cloak", "leather", "cape"),
        "description": (
            "A knee-length cloak of oiled leather.  "
            "Rolls off rain and wind alike, with a broad hood stitched firm."
        ),
        "wear_on":   "about_body",
        "ac_bonus":  4,
        "weight":    3.0,
        "cost":      40,
        "stat_mods": {"str": 2, "con": 3},
        "save_mods": {},
    },

    # ── WAIST — 2 AC ──────────────────────────────────────────────────────────
    "belt" : {
        "spawn_as":        Item,
        "name":        "&Xa sturdy &N&yleather &Xbelt&N",
        "room_desc":   "&XA sturdy &N&yleather &Xbelt has been left here.&N",
        "key_words":   ("belt", "leather", "girdle"),
        "description": (
            "A broad belt of double-layered leather with a heavy iron buckle.  "
            "Good for keeping your kit tight and your back supported."
        ),
        "wear_on":   "waist",
        "ac_bonus":  2,
        "weight":    1.0,
        "cost":      20,
        "stat_mods": {"str": 5},
        "save_mods": {},
    },

    # ── ARMS — 3 AC ───────────────────────────────────────────────────────────
    "vambraces" : {
        "spawn_as":        Item,
        "name":        "&Xsome sturdy &N&yleather &Xvambraces&N",
        "room_desc":   "&XSome sturdy &N&yleather &Xvambraces have been left here.&N",
        "key_words":   ("vambraces", "vambrace", "leather", "arms", "bracers"),
        "description": (
            "Paired leather guards lashed from wrist to elbow.  "
            "The inside is padded with soft linen to prevent chafing."
        ),
        "wear_on":   "arms",
        "ac_bonus":  3,
        "weight":    2.0,
        "cost":      25,
        "stat_mods": {"dex": 2, "con": 2},
        "save_mods": {},
    },

    # ── HANDS — 3 AC ─────────────────────────────────────────────────────────
    "gloves" : {
        "spawn_as":        Item,
        "name":        "&Xa pair of sturdy &N&yleather &Xgloves&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xgloves have been left here.&N",
        "key_words":   ("gloves", "glove", "leather", "gauntlets", "hands"),
        "description": (
            "Close-fitting leather gloves with reinforced knuckles.  "
            "They improve your grip without dulling your feel for the weapon."
        ),
        "wear_on":   "hands",
        "ac_bonus":  3,
        "weight":    0.5,
        "cost":      18,
        "stat_mods": {"str": 3, "dex": 3},
        "save_mods": {},
    },

    # ── LEGS — 5 AC ───────────────────────────────────────────────────────────
    "leggings" : {
        "spawn_as":        Item,
        "name":        "&Xa pair of sturdy &N&yleather &Xleggings&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xleggings have been left here.&N",
        "key_words":   ("leggings", "legging", "leather", "pants", "legs"),
        "description": (
            "Thick leather leggings reinforced at the knee and thigh.  "
            "They move with you and take a lot of punishment."
        ),
        "wear_on":   "legs",
        "ac_bonus":  5,
        "weight":    4.0,
        "cost":      45,
        "stat_mods": {"con": 5},
        "save_mods": {},
    },

    # ── FEET — 3 AC ───────────────────────────────────────────────────────────
    "boots" : {
        "spawn_as":        Item,
        "name":        "&Xa pair of sturdy &N&yleather &Xboots&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xboots have been left here.&N",
        "key_words":   ("boots", "boot", "leather", "shoes", "feet"),
        "description": (
            "Ankle-high boots with thick soles and steel-capped toes.  "
            "Worn enough to be broken in, tough enough to last another year."
        ),
        "wear_on":   "feet",
        "ac_bonus":  3,
        "weight":    2.5,
        "cost":      35,
        "stat_mods": {"str": 2, "dex": 2, "con": 3},
        "save_mods": {},
    },

}

spawn = make_spawner(TEMPLATES, lambda: Object)
