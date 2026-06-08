"""
ashenmoor.world.equipment
─────────────────────────
Slot definitions and routing for the wear/remove system.

Dual slots (ring, neck, wrist, earring)
────────────────────────────────────────
Each of these slots holds a list of up to 2 items in char.equipment.
Zone items may declare wear_on with a number suffix (ring1, ring2, neck1 …)
or without (ring, neck, wrist).  actual_slot() collapses all variants to
the bare canonical name so _wear_one() always stores into the same key
and the list-of-2 logic fires correctly.

Slot ordering in SLOTS
──────────────────────
The dict is insertion-ordered (Python 3.7+).  _cmd_equipment() iterates
SLOTS top-to-bottom to display worn items, so the order here is the
display order shown to players.
"""

# ── Canonical slot → display label ───────────────────────────────────────────

SLOTS: dict[str, str] = {
    "head":           "<worn on head>         ",
    "eyes":           "<worn on eyes>         ",
    "earring":        "<worn in ear>          ",
    "face":           "<worn on face>         ",
    "neck":           "<worn around neck>     ",
    "on_body":        "<worn on body>         ",
    "about_body":     "<worn about body>      ",
    "back":           "<worn on back>         ",
    "waist":          "<worn about waist>     ",
    "arms":           "<worn on arms>         ",
    "wrist":          "<worn on wrist>        ",
    "hands":          "<worn on hands>        ",
    "ring":           "<worn on finger>       ",
    "primary_hand":   "<primary weapon>       ",
    "secondary_hand": "<secondary weapon>     ",
    "legs":           "<worn on legs>         ",
    "feet":           "<worn on feet>         ",
}

# ── Dual slots: each holds a list[item] of up to 2 items ─────────────────────

DUAL_SLOTS: frozenset[str] = frozenset({
    "ring",
    "neck",
    "wrist",
    "earring",
})

# ── wear_on alias map ─────────────────────────────────────────────────────────

_SLOT_MAP: dict[str, str] = {
    # ── Primary / secondary hand ──────────────────────────────────────────────
    "primary_hand":   "primary_hand",
    "weapon":         "primary_hand",
    "wield":          "primary_hand",
    "secondary_hand": "secondary_hand",
    "shield":         "secondary_hand",
    "held":           "secondary_hand",
    "offhand":        "secondary_hand",
    # ── Head / face ───────────────────────────────────────────────────────────
    "head":           "head",
    "helmet":         "head",
    "hat":            "head",
    "face":           "face",
    "mask":           "face",
    "goggles":        "face",
    # ── Neck (dual) ───────────────────────────────────────────────────────────
    "neck":           "neck",
    "neck1":          "neck",
    "neck2":          "neck",
    "necklace":       "neck",
    "amulet":         "neck",
    "collar":         "neck",
    # ── Body ──────────────────────────────────────────────────────────────────
    "on_body":        "on_body",
    "body":           "on_body",
    "torso":          "on_body",
    "chest":          "on_body",
    "armor":          "on_body",
    "about_body":     "about_body",
    "cloak":          "about_body",
    "cape":           "about_body",
    "back":           "back",
    # ── Arms / hands / legs / feet ────────────────────────────────────────────
    "arms":           "arms",
    "sleeves":        "arms",
    "hands":          "hands",
    "gloves":         "hands",
    "gauntlets":      "hands",
    "waist":          "waist",
    "belt":           "waist",
    "legs":           "legs",
    "pants":          "legs",
    "greaves":        "legs",
    "feet":           "feet",
    "boots":          "feet",
    "shoes":          "feet",
    # ── Wrist (dual) ──────────────────────────────────────────────────────────
    "wrist":          "wrist",
    "wrist1":         "wrist",
    "wrist2":         "wrist",
    "bracelet":       "wrist",
    "bracer":         "wrist",
    "bangle":         "wrist",
    # ── Ring / finger (dual) ──────────────────────────────────────────────────
    "ring":           "ring",
    "ring1":          "ring",
    "ring2":          "ring",
    "finger":         "ring",
    "band":           "ring",
    # ── Earring (dual) ────────────────────────────────────────────────────────
    "earring":        "earring",
    "earring1":       "earring",
    "earring2":       "earring",
    "ear":            "earring",
    "stud":           "earring",
    # ── Misc ──────────────────────────────────────────────────────────────────
    "light":          "light",
    "torch":          "light",
    "lantern":        "light",
    "floating":       "floating",
    "hover":          "floating",
}

# Build VALID_WEAR_ON from _SLOT_MAP keys
VALID_WEAR_ON: frozenset[str] = frozenset(_SLOT_MAP.keys())


# ── Helper functions ──────────────────────────────────────────────────────────

def actual_slot(wear_on: str) -> str:
    return _SLOT_MAP.get(wear_on, wear_on)


def is_blocking_secondary(item) -> bool:
    return getattr(item, "two_handed", False)


def hand_label(slot: str, item) -> str:
    """
    Return the contextual display label for a hand slot based on what
    is actually equipped there.

      primary_hand:
        two_handed weapon  → <wielding two-handed>
        otherwise          → <primary weapon>

      secondary_hand:
        shield             → <held as shield>
        weapon (off-hand)  → <secondary weapon>
        other held item    → <held>
    """
    from .objects import Weapon

    if slot == "primary_hand":
        if isinstance(item, Weapon) and getattr(item, "two_handed", False):
            return "<wielding two-handed>  "
        return "<primary weapon>       "

    if slot == "secondary_hand":
        if getattr(item, "is_shield", False):
            return "<held as shield>       "
        if isinstance(item, Weapon):
            return "<secondary weapon>     "
        return "<held>                 "

    return SLOTS.get(slot, f"<{slot}>")
