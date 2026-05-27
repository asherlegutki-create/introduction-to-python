"""
ashenmoor.dnd.classes.warrior
──────────────────────────────
Fighter class — D&D 5.5e.

Hit Die: d10
Primary abilities: Strength, Constitution
Saving throws: Strength, Constitution
Armor: all armor and shields
Weapons: all simple and martial weapons

Features by level
─────────────────
  1   Fighting Style, Second Wind
  2   Action Surge (1 use / short rest)
  3   Martial Archetype (subclass)
  4   Ability Score Improvement
  5   Extra Attack (2 attacks / round)
  6   Ability Score Improvement
  7   Archetype feature
  8   Ability Score Improvement
  9   Indomitable (1 use / long rest)
  10  Archetype feature
  11  Extra Attack (3 attacks / round)
  12  Ability Score Improvement
  13  Indomitable (2 uses)
  14  Ability Score Improvement
  15  Archetype feature
  16  Ability Score Improvement
  17  Action Surge (2 uses / short rest)
  18  Archetype feature
  19  Ability Score Improvement / Epic Boon
  20  Extra Attack (4 attacks / round)

Fighting Styles
───────────────
  defense       +1 AC while wearing armor
  dueling       +2 damage with one-handed weapon (no other weapon in hand)
  great_weapon  reroll 1s and 2s on two-handed weapon damage dice
  archery       +2 to attack rolls with ranged weapons
  two_weapon    add ability modifier to off-hand attack damage
  protection    impose disadvantage on attacks against adjacent allies

Powers  (charged via rest, not time-cooldown)
──────────────────────────────────────────────
  second wind   heal 1d10 + level  (1/short rest)
  action surge  extra attacks next tick  (1/short rest, 2 at lvl 17)
  indomitable   reroll a failed saving throw  (1/long rest, +1 at 13 and 17)
"""

import random

# ── Proficiency table ─────────────────────────────────────────────────────────

def proficiency_bonus(level: int) -> int:
    return max(2, (level - 1) // 4 + 2)

# ── Attack count ──────────────────────────────────────────────────────────────

def attack_count(level: int) -> int:
    """Number of auto-attacks per combat round for this fighter level."""
    if level >= 20: return 4
    if level >= 11: return 3
    if level >= 5:  return 2
    return 1

# ── Fighting styles ───────────────────────────────────────────────────────────

FIGHTING_STYLES: dict[str, str] = {
    "archery":      "+2 to attack rolls with ranged weapons.",
    "defense":      "+1 AC while wearing armor.",
    "dueling":      "+2 damage when wielding one weapon with no other weapon.",
    "great_weapon": "Reroll 1s and 2s on two-handed weapon damage dice.",
    "protection":   "Use reaction to impose disadvantage on nearby attacks.",
    "two_weapon":   "Add ability modifier to the off-hand attack damage roll.",
}

# ── Features by level ─────────────────────────────────────────────────────────

_FEATURES: dict[int, list[str]] = {
    1:  ["Fighting Style", "Second Wind"],
    2:  ["Action Surge"],
    3:  ["Martial Archetype"],
    4:  ["Ability Score Improvement"],
    5:  ["Extra Attack (×2)"],
    6:  ["Ability Score Improvement"],
    9:  ["Indomitable"],
    11: ["Extra Attack (×3)"],
    13: ["Indomitable (2 uses)"],
    17: ["Action Surge (2 uses)"],
    19: ["Ability Score Improvement / Epic Boon"],
    20: ["Extra Attack (×4)"],
}

def active_features(level: int) -> list[str]:
    """All Fighter features available at *level*."""
    feats = []
    for lvl in sorted(_FEATURES):
        if level >= lvl:
            feats.extend(_FEATURES[lvl])
    return feats

# ── Default DND state dict ────────────────────────────────────────────────────

def new_warrior_dnd(
    level:          int = 1,
    fighting_style: str = "dueling",
) -> dict:
    """
    Return a fresh dnd state dict for a new Warrior character.

    Pass this as the "dnd" key inside the Character dict in main.py:

        Character({
            "name": "Aegis",
            "class": "Warrior",
            "level": 5,
            "dnd": new_warrior_dnd(level=5, fighting_style="defense"),
            "stats": [80]*6,   # kept for legacy compat
        })

    Stats come from char.stats (the legacy 1-100 scale).
    Adjust them to reflect the character's point buy or rolled stats.
    """
    surge_uses = 2 if level >= 17 else (1 if level >= 2 else 0)
    indom_uses = (3 if level >= 17 else 2 if level >= 13 else 1) if level >= 9 else 0

    return {
        "class":    "warrior",
        "subclass": None,       # set to "champion", "battle_master", etc.

        # Hit dice
        "hit_die":            10,
        "hit_dice_remaining": level,   # starts at maximum

        # Fighting style
        "fighting_style": fighting_style,

        # Saving throw proficiencies
        "saving_throw_proficiencies": ["str", "con"],

        # Short-rest abilities
        "second_wind_uses": 1,
        "second_wind_max":  1,
        "action_surge_uses": surge_uses,
        "action_surge_max":  surge_uses,
        "action_surge_active": False,   # True → extra attacks next tick

        # Long-rest abilities
        "indomitable_uses": indom_uses,
        "indomitable_max":  indom_uses,
    }

# ── Warrior power definitions ─────────────────────────────────────────────────
#
# These use the "charges_key" system instead of time-based cooldowns.
# _execute_power() in game.py checks charges_key and deducts accordingly.

WARRIOR_POWERS: list[dict] = [

    {
        "keywords":    ("secondwind", "sw"),
        "name":        "Second Wind",
        "charges_key": "second_wind_uses",
        "rest_type":   "short",
        "effect":      "second_wind",       # heal 1d10 + level
        "user_msg":    "&+GYou draw on your fighting spirit to recover some health!&N",
        "room_msg":    "&+G{name} draws on inner strength and looks healthier!&N",
    },

    {
        "keywords":    ("actionsurge", "surge", "as"),
        "name":        "Action Surge",
        "charges_key": "action_surge_uses",
        "rest_type":   "short",
        "effect":      "action_surge",      # doubles attack count next tick
        "user_msg":    "&+WYou surge with unstoppable energy — "
                       "your next round of attacks will be devastating!&N",
        "room_msg":    "&+W{name} surges with terrifying energy!&N",
    },

    {
        "keywords":    ("indomitable", "ind"),
        "name":        "Indomitable",
        "charges_key": "indomitable_uses",
        "rest_type":   "long",
        "effect":      "indomitable",       # placeholder; reroll saving throws
        "user_msg":    "&+YYour indomitable will refuses to yield!&N",
        "room_msg":    "&+Y{name}'s indomitable spirit steels them against defeat!&N",
    },

]

# ── Great Weapon Fighting reroll helper ───────────────────────────────────────

def great_weapon_reroll(dice_results: list[int], die_size: int) -> list[int]:
    """
    Reroll any 1s or 2s for the Great Weapon Fighting style.
    Each die is only rerolled once (5.5e rule).
    """
    return [
        random.randint(1, die_size) if d <= 2 else d
        for d in dice_results
    ]
