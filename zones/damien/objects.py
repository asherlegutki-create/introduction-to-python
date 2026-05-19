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
    "sack_of_darkness": {
        "spawn_as":         Item,
        "name":             "a sack of darkness",
        "key_words":        ("darkness", "sack"),
        "room_description": "A plain looking sack lies on the ground.",
        "description":      "The bag looks simple. It is a &ybrown&N canvas. When you look inside you see a black void.",
        "weight":           2,
    },
    "sword_that_seals_the_darkness" : {
        "spawn_as":         Weapon,
        'name': "The Sword that Seals the Darkness&N",
        'key_words': ('sword', 'seals', 'darkness'),
        'room_description': "&BT&ch&Be &cS&Bw&co&Br&cd &Bt&ch&Ba&ct &BS&ce&Ba&cl&Bs &ct&Bh&ce &BD&ca&Br&ck&Bn&ce&Bs&cs&N lies here. Its light &Cilluminates&N the ground around it.",
        'description': "The sword is beautiful. It was forged by the Elves as a tool against the &rGreat Darkness&N. It glows softly with divine, &Bbluish&N light",
        "weight":           5,
        "dice":             "6d8",
        "hitroll":          4,
        "damroll":          4,
    },

}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
