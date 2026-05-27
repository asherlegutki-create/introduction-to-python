"""
ashenmoor.dnd.rest
──────────────────
Short rest and long rest for D&D 5.5e characters.

Short rest  (command: rest short)
──────────────────────────────────
  • Spend any number of Hit Dice to recover HP.
    Each die rolled: 1d{hit_die} + CON modifier.
  • Restores: Second Wind charges, Action Surge charges.
  • Does NOT restore: Indomitable, spell slots (future).

Long rest  (command: rest long)
────────────────────────────────
  • Recover all HP.
  • Recover up to half your maximum Hit Dice (minimum 1).
  • Restores: all short-rest abilities + Indomitable.
  • Cannot benefit more than once every 24 hours (not enforced here yet).
"""

import random


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ability_display_name(key: str) -> str:
    """'second_wind_uses' → 'Second Wind'"""
    return key.replace("_uses", "").replace("_", " ").title()


def _default_max(key: str, level: int) -> int:
    """Default maximum charges for a Warrior ability at the given level."""
    if key == "second_wind_uses":
        return 1
    if key == "action_surge_uses":
        return 2 if level >= 17 else 1
    if key == "indomitable_uses":
        if level >= 17: return 3
        if level >= 13: return 2
        if level >= 9:  return 1
        return 0
    return 1


# ── Short rest ────────────────────────────────────────────────────────────────

def short_rest(char) -> str:
    """
    Resolve a short rest for *char*.

    Spends all remaining Hit Dice to heal, then restores short-rest ability
    charges (Second Wind, Action Surge).

    Returns a Diku-colored output string.
    """
    dnd = getattr(char, "dnd", {})
    if not dnd:
        return "&wOnly D&D characters can take a structured rest.&N"

    msgs = ["&wYou settle down and take a short rest...&N"]

    # ── Spend Hit Dice to heal ────────────────────────────────────────────
    hd_remaining = dnd.get("hit_dice_remaining", 0)
    hit_die      = dnd.get("hit_die", 10)

    from .abilities import modifier
    con_mod = modifier(char.computed_stat("con"))

    if hd_remaining > 0 and char.hp < char.max_hp:
        healed = 0
        spent  = 0
        while hd_remaining > 0 and char.hp < char.max_hp:
            roll    = random.randint(1, hit_die) + con_mod
            roll    = max(1, roll)
            char.hp = min(char.max_hp, char.hp + roll)
            healed += roll
            hd_remaining -= 1
            spent  += 1

        dnd["hit_dice_remaining"] = hd_remaining
        msgs.append(
            f"&wYou spend &W{spent}&w Hit {'Die' if spent == 1 else 'Dice'}, "
            f"recovering &W{healed}&w HP.&N"
        )
    elif char.hp >= char.max_hp:
        msgs.append("&wYou are already at full health.&N")
    else:
        msgs.append("&wYou have no Hit Dice remaining to spend.&N")

    msgs.append(
        f"&wHP: &W{char.hp}&w/&W{char.max_hp}&N  "
        f"Hit Dice: &W{dnd.get('hit_dice_remaining', 0)}&w/&W{char.level}&N"
    )

    # ── Restore short-rest abilities ──────────────────────────────────────
    SHORT_REST_KEYS = ("second_wind_uses", "action_surge_uses")
    restored = []
    for key in SHORT_REST_KEYS:
        if key in dnd:
            max_val = dnd.get(key.replace("_uses", "_max"),
                              _default_max(key, char.level))
            if dnd[key] < max_val:
                dnd[key] = max_val
                restored.append(_ability_display_name(key))

    dnd["action_surge_active"] = False   # clear any pending surge

    if restored:
        msgs.append(f"&+GRestored: &W{', '.join(restored)}&N")

    return "\n".join(msgs)


# ── Long rest ─────────────────────────────────────────────────────────────────

def long_rest(char) -> str:
    """
    Resolve a long rest for *char*.

    Restores full HP, recovers Hit Dice (up to half max, minimum 1),
    and restores all ability charges.

    Returns a Diku-colored output string.
    """
    dnd = getattr(char, "dnd", {})
    if not dnd:
        return "&wOnly D&D characters can take a structured rest.&N"

    msgs = ["&wYou take a long rest, sleeping deeply...&N"]

    # ── Restore HP ────────────────────────────────────────────────────────
    healed  = char.max_hp - char.hp
    char.hp = char.max_hp
    if healed > 0:
        msgs.append(f"&+GYou recover &W{healed}&+G HP — fully restored.&N")
    else:
        msgs.append("&+GYou wake up fully rested.&N")

    # ── Recover Hit Dice ──────────────────────────────────────────────────
    hd_max       = char.level
    hd_current   = dnd.get("hit_dice_remaining", 0)
    hd_restore   = max(1, hd_max // 2)
    new_hd       = min(hd_max, hd_current + hd_restore)
    dnd["hit_dice_remaining"] = new_hd
    msgs.append(
        f"&wHit Dice: &W{new_hd}&w/&W{hd_max}&N  "
        f"(&W{new_hd - hd_current}&w recovered)&N"
    )

    # ── Restore all abilities ─────────────────────────────────────────────
    ALL_REST_KEYS = (
        "second_wind_uses",
        "action_surge_uses",
        "indomitable_uses",
    )
    restored = []
    for key in ALL_REST_KEYS:
        if key in dnd:
            max_val = dnd.get(key.replace("_uses", "_max"),
                              _default_max(key, char.level))
            if dnd[key] < max_val:
                dnd[key] = max_val
                restored.append(_ability_display_name(key))

    dnd["action_surge_active"] = False

    if restored:
        msgs.append(f"&+GRestored: &W{', '.join(restored)}&N")

    return "\n".join(msgs)
