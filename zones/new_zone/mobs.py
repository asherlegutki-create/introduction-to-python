"""
zones.the_void.mobs
───────────────────
Mob templates for The Void zone.

Add an entry to TEMPLATES for every NPC type that can appear in this zone.
Call spawn(key) to get a fresh independent Mob instance — place as many
copies in rooms as you like, each is independent.
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner


#def _merchant_buy(state, char, mob):
#    # Could check char inventory, give items, etc.
#    from ashenmoor.world.objects import Item
#    potion = Item({"name": "health potion", ...})
#    char.inventory.append(potion)
#    return "&GThe merchant hands you a health potion.&N"

def _student_attack(state, char, mob):
    state.fighting[char.name] = mob
    return f"{mob.name}&N cries because of the insult, then turns in a &rrage and attacks!!&N"


TEMPLATES: dict[str, dict] = {
    "wandering_student": {
        "name": "&wa wandering student&N",
        "key_words": ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.",
            "Or possibly just lost."
        ),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "wander": True,
        "responses": {
            "hi": ("&wa wandering student&W looks at you helplessly.&N",
                   "He asks you '&LCan you help me find my way to class?&N'"),
            "class": ("He replies '&LI am a student in Mrs. Allison's class, or is it Miss Allison?&N'"),
            "grade": ("He replies '&L'Oh I'm in 7th grade thank you!&N'"),
            "looser": _student_attack
            }
    }
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)
