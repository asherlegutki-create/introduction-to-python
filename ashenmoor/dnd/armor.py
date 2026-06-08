"""
ashenmoor.dnd.armor
───────────────────
Armor Class calculation.

AC is built entirely from per-item ac_bonus values that stack additively.
Unarmored AC is 0. There is no cap.

Every item in any equipment slot may carry an ac_bonus field (int).
Dual slots (ring, neck, wrist, earring) hold lists — all are summed.

Active status effects may also contribute via char.effect_ac.

Attack roll interaction
───────────────────────
  Attack score = (d20 + attacker_modifier) × 5
  Hit if attack_score ≥ target AC  (nat 1 = auto-miss, nat 20 = crit)
"""


def get_ac(target) -> int:
    """
    Return the Armor Class of any character or mob.

    Priority:
      1. Explicit 'ac' field on the target (mob template override).
      2. Sum of ac_bonus across all equipped items (no cap).
      3. Plus char.effect_ac from active status effects.

    Unarmored AC is 0.
    """
    # ── Mob/NPC explicit AC override ──────────────────────────────────────
    explicit = getattr(target, "ac", None)
    if explicit is not None:
        return int(explicit)

    equipped = getattr(target, "equipment", {})

    ac = 0

    # ── Sum ac_bonus from every equipped item ─────────────────────────────
    for item in equipped.values():
        if isinstance(item, list):
            for sub in item:
                if sub is not None:
                    ac += getattr(sub, "ac_bonus", 0)
        else:
            if item is not None:
                ac += getattr(item, "ac_bonus", 0)

    # ── Active status effect AC modifier ──────────────────────────────────
    ac += getattr(target, "effect_ac", 0)

    return ac
