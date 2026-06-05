"""
zones.the_void.objects
──────────────────────
Object templates for The Void zone.

Add an entry to TEMPLATES for every object that can appear in this zone.
The "class" key picks the instantiation class (Object / Item / Weapon).
Omitting "class" defaults to Object.

Call spawn(key) to get a fresh independent instance.
"""

from ashenmoor.world import Object, Container, Item, Weapon
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "Illrigger Mage Robe": {
    "spawn_as":   Item,
    "name":      "Illrigger Mage Robe",
    "room_description": "This robe glistens with a &Mpurple aura&N",
    "key_words": ("armour", "mage", "robe", "illrigger"),
    "wear_on":   "body",
    "armor_type": "linen",
    "weight":    10.0,
    "cost":      200,
    "stat_mods": {},
    "save_mods": {},

    },
   
    "Copper Sword": {
        "spawn_as":     Weapon,
        "name":      "&yCopper Sword&N",
        "room_description": "A &yCopper Sword&N lies here.",
        "key_words": ("copper", "sword",),
        "wear_on":   "primary_hand",
        "dice":    "2d3", 
        "hitroll": 5,   
        "damroll": 5,  
    },
   
    "Sack of the Void": {
    "spawn_as":     Container,
    "name":      "This sack is radiating with &Mv&bo&Mi&bd&N aura",
    "room_description": "A mythical sack lies here",
    "key_words": ("sack", "of", "the", "void"),
    "wear_on":   "held",
    "capacity":           100.0,  
    "weightless_capacity": 100.0, 
    "is_open":            True, 
    },

    "Spruce Chest": {
        "spawn_as":        Container,
        "name":            "Spruce Chest",
        "key_words":       ("spruce", "chest"),
        "room_description": "A sturdy spruce chest lies here unopened.",
        "no_take":         True,       
        "is_open":         False,      
        "locked":          True,      
        "key_name":        "chest key",
        "capacity":        50.0,
        "weight":          20.0,
        "contents": [    
         "Copper Sword",
            "Gold Nugget", "Gold Nugget", "Gold Nugget", "Gold Nugget",
            "Gold Nugget", "Gold Nugget", "Gold Nugget", "Gold Nugget",
        ],
    },
   
    "Gold Nugget": {
    "spawn_as":  Item,
    "name":      "&YGold Nuggets&N",
    "room_description": "&YGold Nuggets&N shimmer against the light",
    "key_words": ("gem", "gold", "nuggets"),
    "wear_on":   None,
    "weight":    0.1,
    "cost":      500,
    "stat_mods": {},
    "save_mods": {},
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
