"""
ashenmoor.world.equipment
─────────────────────────
Equipment slot definitions and two-handed blocking logic.

Slot list (17 slots, 4 dual pairs)
───────────────────────────────────
    head, eyes, earring×2, face, neck×2, on_body, about_body,
    quiver, waist, arms, wrist×2, hands, finger×2,
    primary_hand, secondary_hand, legs, feet

wear_on values
──────────────
Set wear_on on an Item/Weapon template to one of VALID_WEAR_ON:

  Direct slot key   — stored in that slot
  "shield"          — stored in secondary_hand
  "held_twohanded"  — stored in primary_hand; secondary_hand becomes unavailable

Two-handed weapons
──────────────────
A Weapon with two_handed=True also blocks secondary_hand when equipped.

Race-specific slots
───────────────────
For now all races share the same slot set.  In a future phase, each Race
will carry a set of available slots and the equip command will validate
against it.
"""

# Slot key → display label, in display order
SLOTS: dict[str, str] = {
    "head":           "Head",
    "eyes":           "Eyes",
    "earring":        "Earring",        # dual ×2
    "face":           "Face",
    "neck":           "Neck",           # dual ×2
    "on_body":        "On Body",
    "about_body":     "About Body",
    "quiver":         "Quiver",
    "waist":          "Waist",
    "arms":           "Arms",
    "wrist":          "Wrist",          # dual ×2
    "hands":          "Hands",
    "finger":         "Finger",         # dual ×2
    "primary_hand":   "Primary Hand",
    "secondary_hand": "Secondary Hand",
    "legs":           "Legs",
    "feet":           "Feet",
}

# Slots that hold exactly 2 items (stored as list[item])
DUAL_SLOTS: frozenset = frozenset({
    "earring", "neck", "wrist", "finger",
})

# Special wear_on aliases → actual slot where item is stored
WEAR_ON_ALIAS: dict[str, str] = {
    "shield":         "secondary_hand",
    "held_twohanded": "primary_hand",
}

# Every legal value for the wear_on field
VALID_WEAR_ON: frozenset = frozenset(SLOTS) | frozenset(WEAR_ON_ALIAS)


def is_blocking_secondary(item) -> bool:
    """
    True when this item, once in primary_hand, prevents use of secondary_hand.

    Triggered by:
      - Weapon with two_handed=True
      - Any item with wear_on="held_twohanded"
    """
    return (
        getattr(item, "two_handed", False)
        or getattr(item, "wear_on", None) == "held_twohanded"
    )


def actual_slot(wear_on: str) -> str:
    """Resolve a wear_on value to the real equipment dict key."""
    return WEAR_ON_ALIAS.get(wear_on, wear_on)
