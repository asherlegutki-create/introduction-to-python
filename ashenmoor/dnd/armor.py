"""
ashenmoor.dnd.armor
───────────────────
Armor Class on the 0-100 scale.

  0   = completely unprotected (training dummy standing still)
  25  = average unarmored adult human
  50  = fast unarmored character (DEX maxed at 100)
  40-65 = light/medium armor range
  65-80 = heavy armor range
  80-95 = magical/legendary protection
  100 = theoretical absolute cap (nearly impossible to hit)

Unarmored formula
─────────────────
  AC = max(0, 25 + DEX_modifier × 5)

  DEX 75  (mod  0)  → AC 25   average human
  DEX 100 (mod +5)  → AC 50   very agile
  DEX 120 (mod +9)  → AC 70   elven grace (gear-maxed Grey Elf)
  DEX 60  (mod −3)  → AC 10   clumsy
  DEX 50  (mod −5)  → AC  0   almost helpless

Armor items add a base AC value; some allow partial DEX contribution.
  Add "armor_type": "<key>" to any Item/Weapon template.
  Add "is_shield": True to a secondary-hand item for +10 AC.

Attack roll interaction
───────────────────────
  Attack score = (d20 + attacker_modifier) × 5
  Hit if attack_score ≥ target AC  (nat 1 = auto-miss, nat 20 = crit)

  Fighter mod +3 vs AC 50:
    avg d20 = 10  →  (10+3)×5 = 65  → hits   ✓
  Fighter mod +3 vs AC 75:
    need (d20+3)×5 ≥ 75  →  d20 ≥ 12  →  ~45% chance
"""

from .abilities import char_modifier

# ── Armor table ───────────────────────────────────────────────────────────────
#
# (base_ac, uses_dex, dex_mod_cap)
#   base_ac      flat AC before DEX modifier is added
#   uses_dex     True: add DEX modifier × 5 (up to cap if set)
#   dex_mod_cap  max modifier points added (None = no cap)

ARMOR_TABLE: dict[str, tuple[int, bool, int | None]] = {
    # ── Light (full DEX, no cap) ──────────────────────────────────────────
    "padded":       (30, True,  None),
    "leather":      (35, True,  None),
    "studded":      (40, True,  None),
    # ── Medium (DEX capped at +5 modifier = up to +25 AC) ─────────────────
    "hide":         (45, True,  5),
    "chain_shirt":  (50, True,  5),
    "scale_mail":   (55, True,  5),
    "breastplate":  (55, True,  5),
    "half_plate":   (60, True,  5),
    # ── Heavy (no DEX bonus) ───────────────────────────────────────────────
    "ring_mail":    (60, False, 0),
    "chain_mail":   (65, False, 0),
    "splint":       (70, False, 0),
    "plate":        (75, False, 0),
}

SHIELD_AC   = 10    # flat bonus for a shield in secondary_hand
DEFENSE_AC  = 5     # bonus from Defense fighting style (while armored)


# ── AC calculation ────────────────────────────────────────────────────────────

def get_ac(target) -> int:
    """
    Return the Armor Class (0-100) of any character or mob.

    Priority:
      1. Explicit 'ac' field on the target (mob template override).
      2. Equipped body armor (on_body slot) from ARMOR_TABLE.
      3. Unarmored base: max(0, 25 + DEX_modifier × 5).
    """
    # ── Mob/NPC explicit AC override ──────────────────────────────────────
    explicit = getattr(target, "ac", None)
    if explicit is not None:
        return int(explicit)

    dex_mod  = char_modifier(target, "dex")
    equipped = getattr(target, "equipment", {})
    dnd      = getattr(target, "dnd", {}) or {}

    # ── Equipped body armor ───────────────────────────────────────────────
    armor      = equipped.get("on_body")
    armor_type = getattr(armor, "armor_type", None) if armor else None

    if armor_type and armor_type in ARMOR_TABLE:
        base_ac, uses_dex, cap = ARMOR_TABLE[armor_type]
        if uses_dex:
            capped_mod = min(dex_mod, cap) if cap is not None else dex_mod
            ac = base_ac + capped_mod * 5
        else:
            ac = base_ac

        # Defense fighting style: +5 AC while wearing any armor
        if dnd.get("fighting_style") == "defense":
            ac += DEFENSE_AC

    else:
        # ── Unarmored ─────────────────────────────────────────────────────
        unarmored = dnd.get("unarmored_defense")
        if unarmored == "barbarian":
            con_mod = char_modifier(target, "con")
            ac = max(0, 25 + (dex_mod + con_mod) * 5)
        elif unarmored == "monk":
            wis_mod = char_modifier(target, "wis")
            ac = max(0, 25 + (dex_mod + wis_mod) * 5)
        else:
            ac = max(0, 25 + dex_mod * 5)

    # ── Shield in secondary_hand ──────────────────────────────────────────
    shield = equipped.get("secondary_hand")
    if shield and getattr(shield, "is_shield", False):
        ac += SHIELD_AC

    # ── ac_bonus from every equipped item ────────────────────────────────
    # Any item in any slot may carry an ac_bonus field (int).  These stack
    # additively on top of the base armor calculation above.
    # Dual slots (ring, neck, wrist, earring) hold lists — iterate both.
    for item in equipped.values():
        if isinstance(item, list):
            for sub in item:
                ac += getattr(sub, "ac_bonus", 0)
        else:
            ac += getattr(item, "ac_bonus", 0)

    base_ac =  min(100, ac)
    return base_ac + getattr(target, "effect_ac", 0)
