"""
ashenmoor.world.powers
──────────────────────
Power (ability / spell / skill) definitions.

A power is a plain dict.  Required keys:

    keywords  tuple[str]   words the player types to activate this power
    name      str          display name shown in power listings
    user_msg  str          Diku-colored message shown to the player
    room_msg  str          Diku-colored message shown to everyone else in the room
                           Use {name} as a placeholder for the player's name.

Optional keys (for future combat expansion):

    target    str          "none" | "mob" | "character" | "any"   default "none"
    cost      int          resource cost (mana, stamina, etc.)     default 0
    cooldown  int          seconds before reuse                    default 0

Example
───────
    {
        "keywords": ("fireball", "fire"),
        "name":     "Fireball",
        "user_msg": "&RYou draw the heat from the air and hurl a blazing fireball!&N",
        "room_msg": "&R{name}&R draws the heat from the air and hurls a blazing fireball!&N",
        "target":   "mob",
        "cost":     10,
    }

Assigning powers to a character
────────────────────────────────
    from ashenmoor.world.powers import POWERS

    char.powers = [
        POWERS["fireball"],
        POWERS["heal"],
    ]

Or inline in a character dict (e.g. during creation):

    char.powers = [
        {
            "keywords": ("smite",),
            "name":     "Divine Smite",
            "user_msg": "&YYour weapon blazes with divine light!&N",
            "room_msg": "&Y{name}'s weapon blazes with divine light!&N",
        }
    ]
"""


# ── Power registry ────────────────────────────────────────────────────────────
# Pull from here when assigning powers to races / classes / characters.
# Keys are short identifiers; values are the full power dicts.

POWERS: dict[str, dict] = {

    # ── Arcane ────────────────────────────────────────────────────────────────

    "fireball": {
        "keywords": ("fireball", "fire"),
        "name":     "Fireball",
        "user_msg": "&RYou draw the heat from the air and hurl a blazing fireball!&N",
        "room_msg": "&R{name} draws the heat from the air and hurls a blazing fireball!&N",
        "target":   "mob",
        "cost":     10,
    },

    "frost_bolt": {
        "keywords": ("frostbolt", "frost"),
        "name":     "Frost Bolt",
        "user_msg": "&BA bolt of crackling ice shoots from your fingertips!&N",
        "room_msg": "&BA bolt of crackling ice shoots from {name}'s fingertips!&N",
        "target":   "mob",
        "cost":     8,
    },

    "arcane_missile": {
        "keywords": ("missile", "arcane"),
        "name":     "Arcane Missile",
        "user_msg": "&mYou launch a streak of pure arcane energy!&N",
        "room_msg": "&m{name} launches a streak of pure arcane energy!&N",
        "target":   "mob",
        "cost":     5,
    },

    # ── Divine ────────────────────────────────────────────────────────────────

    "heal": {
        "keywords": ("heal",),
        "name":     "Heal",
        "user_msg": "&+GWarm light flows through you, knitting your wounds closed.&N",
        "room_msg": "&+GWarm light flows through {name}, knitting wounds closed.&N",
        "target":   "none",
        "cost":     12,
    },

    "smite": {
        "keywords": ("smite",),
        "name":     "Divine Smite",
        "user_msg": "&YYour weapon blazes with divine light as you bring it down!&N",
        "room_msg": "&Y{name}'s weapon blazes with divine light!&N",
        "target":   "mob",
        "cost":     8,
    },

    "bless": {
        "keywords": ("bless",),
        "name":     "Bless",
        "user_msg": "&YYou call upon the divine and feel strength pour into you.&N",
        "room_msg": "&YA holy light surrounds {name} as they receive a blessing.&N",
        "target":   "none",
        "cost":     6,
    },

    # ── Nature ────────────────────────────────────────────────────────────────

    "entangle": {
        "keywords": ("entangle", "roots"),
        "name":     "Entangle",
        "user_msg": "&GRoots burst from the ground at your command!&N",
        "room_msg": "&GRoots burst from the ground at {name}'s command!&N",
        "target":   "mob",
        "cost":     7,
    },

    "barkskin": {
        "keywords": ("barkskin", "bark"),
        "name":     "Barkskin",
        "user_msg": "&GYour skin hardens like rough bark, toughening your body.&N",
        "room_msg": "&G{name}'s skin hardens and takes on the rough texture of bark.&N",
        "target":   "none",
        "cost":     6,
    },

    # ── Shadow ────────────────────────────────────────────────────────────────

    "shadowstep": {
        "keywords": ("shadowstep", "shadow"),
        "name":     "Shadowstep",
        "user_msg": "&XYou melt into the shadows and reappear behind your target.&N",
        "room_msg": "&X{name} melts into the shadows and vanishes.&N",
        "target":   "mob",
        "cost":     9,
    },

    "backstab": {
        "keywords": ("backstab", "stab"),
        "name":     "Backstab",
        "user_msg": "&xYou drive your blade deep into an unguarded back!&N",
        "room_msg": "&x{name} drives a blade into an unguarded back!&N",
        "target":   "mob",
        "cost":     5,
    },

    # ── Utility ───────────────────────────────────────────────────────────────

    "shout": {
        "keywords": ("shout",),
        "name":     "Shout",
        "user_msg": "&WYou let out a thunderous battle cry!&N",
        "room_msg": "&W{name} lets out a thunderous battle cry!&N",
        "target":   "none",
        "cost":     2,
    },

    "meditate": {
        "keywords": ("meditate", "med"),
        "name":     "Meditate",
        "user_msg": "&cYou close your eyes and focus inward, restoring your concentration.&N",
        "room_msg": "&c{name} closes their eyes and enters a deep meditative state.&N",
        "target":   "none",
        "cost":     0,
    },
}
