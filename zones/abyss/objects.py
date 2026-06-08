"""
zones.abyssal.objects
─────────────────────
Object templates for the Abyssal Web zone.
"""

from ashenmoor.world import Object, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {

    "spider_silk": {
        "spawn_as":         Item,
        "name":             "&La strand of abyssal silk&N",
        "key_words":        ("abyssal", "silk", "strand"),
        "room_description": "&LA gossamer strand of abyssal silk&N floats here.",
        "description": (
            "A strand of impossibly fine silk, cool to the touch and faintly luminescent.\n"
            "It doesn't seem to stick to your fingers the way normal spider silk does."
        ),
        "weight": 0.1,
        "cost":   25,
    },

    "abyssal_egg_sac": {
        "spawn_as":         Object,
        "name":             "&Man abyssal egg sac&N",
        "key_words":        ("abyssal", "egg", "sac"),
        "room_description": "&MA pulsing abyssal egg sac&N clings to the wall.",
        "description": (
            "A bulging sac of &Mmagenta-black membrane&N, pulsing rhythmically.\n"
            "Something moves inside. You probably shouldn't touch it."
        ),
    },

    "venom_gland": {
        "spawn_as":         Item,
        "name":             "&Ma venom gland&N",
        "key_words":        ("venom", "gland"),
        "room_description": "&MA swollen venom gland&N lies here, still seeping.",
        "description": (
            "A grape-sized &Mpurple gland&N extracted from an abyssal spider.\n"
            "Handle carefully — the venom is potent even outside the body."
        ),
        "weight": 0.2,
        "cost":   50,
    },

}

spawn = make_spawner(TEMPLATES, lambda: Object)
