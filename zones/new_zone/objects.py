"""
zones.new_zone.objects
"""

from ashenmoor.world import Object, Item, Weapon, Container
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
        "name":                "&ca dimensional vault&N",
        "key_words":           ("dimensional", "vault"),
        "room_description":    "&cA dimensional vault floats here, humming softly.&N",
        "description":         "A shimmering vault that exists partially outside this dimension.\nIt can hold an extraordinary amount without adding to your burden.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
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
            }
        ],
    },
}

spawn = make_spawner(TEMPLATES, lambda: Object)
