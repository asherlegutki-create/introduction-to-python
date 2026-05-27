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
      "Potion of Strength II": {
        "spawn_as":         Item,
        "name":             "a Potion of &rStrength II&N",
        "key_words":        ("Potion", "Strength", "II"),
        "room_description": "a &wPotion of Strength II&N has been carelessly discarded here.&N",
        "description":      "A potion that grants double the usual strength, about empty.",
    },

  
  
    "Potion of Turtle Master": {
        "spawn_as":         Item,
        "name":             "a &wTurtle Master&N potion",
        "key_words":        ("Potion", "Turtle", "Master"),
        "room_description": "a &wPotion of Turtle Master&N has been carelessly discarded here.&N",
        "description":      "A potion that grants defense and slowness, about empty.",
    },
}

# Module-level spawn — rooms.py calls  O.spawn("red_marker")
spawn = make_spawner(TEMPLATES, lambda: Object)
