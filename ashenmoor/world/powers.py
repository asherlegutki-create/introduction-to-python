"""
ashenmoor.world.powers
──────────────────────
Power (ability / spell / skill) definitions.

Required keys
─────────────
  keywords   tuple[str]   words the player types to activate
  name       str          display name shown in power listings
  user_msg   str          Diku-colored message shown to the player
  room_msg   str          message shown to everyone else  ({name} = player)

Combat keys (optional)
──────────────────────
  cooldown   int          seconds before the power can be used again
                          Default: 8 seconds (2 ticks).
                          Low-cost: 4 s (1 tick).  High-power: 12–20 s.
  effect     str          "damage" or "heal" — what happens in combat
  damage_mult float       for effect="damage": multiplier on a normal hit
  heal_pct    float       for effect="heal":   fraction of max_hp restored

Powers outside combat fire instantly.
Powers typed during combat are queued and fire on the next tick.
"""

POWERS: dict[str, dict] = {

    # ── Arcane ────────────────────────────────────────────────────────────────

    "fireball": {
        "keywords":    ("fireball", "fire"),
        "name":        "Fireball",
        "cooldown":    12,
        "effect":      "damage",
        "damage_mult": 2.5,
        "user_msg": "&RYou draw the heat from the air and hurl a blazing fireball!&N",
        "room_msg": "&R{name} draws the heat from the air and hurls a blazing fireball!&N",
    },

    "frost_bolt": {
        "keywords":    ("frostbolt", "frost"),
        "name":        "Frost Bolt",
        "cooldown":    12,
        "effect":      "damage",
        "damage_mult": 2.0,
        "user_msg": "&BA bolt of crackling ice shoots from your fingertips!&N",
        "room_msg": "&BA bolt of crackling ice shoots from {name}'s fingertips!&N",
    },

    "arcane_missile": {
        "keywords":    ("missile", "arcane"),
        "name":        "Arcane Missile",
        "cooldown":    8,
        "effect":      "damage",
        "damage_mult": 1.5,
        "user_msg": "&mYou launch a streak of pure arcane energy!&N",
        "room_msg": "&m{name} launches a streak of pure arcane energy!&N",
    },

    # ── Divine ────────────────────────────────────────────────────────────────

    "heal": {
        "keywords":  ("heal",),
        "name":      "Heal",
        "cooldown":  12,
        "effect":    "heal",
        "heal_pct":  0.30,
        "user_msg": "&+GWarm light flows through you, knitting your wounds closed.&N",
        "room_msg": "&+GWarm light flows through {name}, knitting wounds closed.&N",
    },

    "smite": {
        "keywords":    ("smite",),
        "name":        "Divine Smite",
        "cooldown":    12,
        "effect":      "damage",
        "damage_mult": 2.0,
        "user_msg": "&YYour weapon blazes with divine light as you bring it down!&N",
        "room_msg": "&Y{name}'s weapon blazes with divine light!&N",
    },

    "bless": {
        "keywords": ("bless",),
        "name":     "Bless",
        "cooldown": 16,
        "user_msg": "&YYou call upon the divine and feel strength pour into you.&N",
        "room_msg": "&YA holy light surrounds {name} as they receive a blessing.&N",
    },

    # ── Nature ────────────────────────────────────────────────────────────────

    "entangle": {
        "keywords": ("entangle", "roots"),
        "name":     "Entangle",
        "cooldown": 16,
        "user_msg": "&GRoots burst from the ground at your command!&N",
        "room_msg": "&GRoots burst from the ground at {name}'s command!&N",
    },

    "barkskin": {
        "keywords": ("barkskin", "bark"),
        "name":     "Barkskin",
        "cooldown": 20,
        "user_msg": "&GYour skin hardens like rough bark, toughening your body.&N",
        "room_msg": "&G{name}'s skin hardens and takes on the rough texture of bark.&N",
    },

    "Rockstab": {
        "keywords":    ("Rockstab", "Rock"),
        "name":        "Rockstab",
        "cooldown":    8,
        "effect":      "damage",
        "damage_mult": 1.5,
        "user_msg": "&GYou launch &xRock&N&WSpikes&N out of the &yground&N",
        "room_msg": "&G{name} launches &xRock&N&WSpikes&N out of the &yground&N",
    },

    # ── Shadow ────────────────────────────────────────────────────────────────

    "shadowstep": {
        "keywords":    ("shadowstep", "shadow"),
        "name":        "Shadowstep",
        "cooldown":    12,
        "effect":      "damage",
        "damage_mult": 2.5,
        "user_msg": "&XYou melt into the shadows and reappear behind your target.&N",
        "room_msg": "&X{name} melts into the shadows and vanishes.&N",
    },

    "backstab": {
        "keywords":    ("backstab", "stab"),
        "name":        "Backstab",
        "cooldown":    8,
        "effect":      "damage",
        "damage_mult": 2.0,
        "user_msg": "&xYou drive your blade deep into an unguarded back!&N",
        "room_msg": "&x{name} drives a blade into an unguarded back!&N",
    },

    # ── Utility ───────────────────────────────────────────────────────────────

    "shout": {
        "keywords": ("shout",),
        "name":     "Shout",
        "cooldown": 4,
        "user_msg": "&WYou let out a thunderous battle cry!&N",
        "room_msg": "&W{name} lets out a thunderous battle cry!&N",
    },

    "meditate": {
        "keywords": ("meditate", "med"),
        "name":     "Meditate",
        "cooldown": 8,
        "effect":   "heal",
        "heal_pct": 0.15,
        "user_msg": "&cYou close your eyes and focus inward, restoring your concentration.&N",
        "room_msg": "&c{name} closes their eyes and enters a deep meditative state.&N",
    },
}
