"""
ashenmoor.dnd.abilities
───────────────────────
D&D modifier math adapted to the ashenmoor 1-100 legacy stat scale.

Scale design
────────────
  Player stats are rolled or point-bought on a 1-100 scale.
  Racial multipliers are applied on top, so computed stats can exceed 100.

  Baseline: 75  =  +0 modifier  (average adult human — same role as D&D 10)
  Interval: every 5 points above or below 75  =  ±1 to the modifier

  Legacy stat → modifier
  ──────────────────────
    50  → -5     weak
    60  → -3     below average
    70  → -1     slightly below
    75  →  0     average
    80  → +1     above average
    85  → +2     trained
    90  → +3     skilled
    95  → +4     exceptional
   100  → +5     human maximum (≈ D&D STR 20)

  With racial multipliers (computed_stat = base × racial_mod):
    Dwarf  CON 80 × 1.30 = 104  → +5   sturdy constitution
    Ogre   STR 100 × 1.50 = 150 → +15  monstrous strength
    Elf    STR 100 × 0.70 =  70 → -1   lithe but not strong

Proficiency bonus  (level-based, same as standard 5e)
─────────────────
  Levels  1-4  → +2
  Levels  5-8  → +3
  Levels  9-12 → +4
  Levels 13-16 → +5
  Levels 17-20 → +6
  Levels 21+   → +7  (epic / beyond level cap)
"""

# ── Core functions ────────────────────────────────────────────────────────────

def modifier(stat: int) -> int:
    """
    Convert a stat value (legacy scale, racial modifiers already applied)
    to an ability modifier.

    modifier(75)  →  0   (average)
    modifier(90)  → +3   (skilled human)
    modifier(150) → +15  (max-strength Ogre)
    modifier(60)  → -3   (weak)
    """
    return (stat - 75) // 5


def char_modifier(char, ability: str) -> int:
    """
    Return the ability modifier for a character using their computed stat.

    Uses computed_stat() so racial multipliers are automatically included.
    Works for both D&D characters and legacy NPCs — no separate path needed.
    """
    return modifier(char.computed_stat(ability))


def proficiency_bonus(level: int) -> int:
    """
    Standard proficiency bonus by character/creature level.
    Increases by +1 every four levels starting at +2.
    """
    if level <= 0:  return 2
    if level >= 21: return 7
    return (level - 1) // 4 + 2


def saving_throw_bonus(char, ability: str) -> int:
    """
    Total saving throw modifier:
        ability_modifier + proficiency_bonus (if proficient)

    Proficiency list lives in char.dnd["saving_throw_proficiencies"].
    """
    base  = char_modifier(char, ability)
    dnd   = getattr(char, "dnd", {}) or {}
    profs = dnd.get("saving_throw_proficiencies", [])
    if ability in profs:
        base += proficiency_bonus(char.level)
    return base


# ── Stat display helper ───────────────────────────────────────────────────────

def stat_line(char, ability: str) -> str:
    """
    Return a formatted stat line showing base, computed, and modifier.

    Example outputs:
      "STR  90        (+3)"      — Human, no racial change
      "STR  88 → 96  (+4)"      — Dwarf, 1.1× racial modifier
    """
    raw      = char.get_stat(ability)
    computed = char.computed_stat(ability)
    mod      = modifier(computed)
    sign     = "+" if mod >= 0 else ""

    if computed != raw:
        return f"{ability.upper():<3}  {raw:>3} → {computed:>3}  ({sign}{mod})"
    return f"{ability.upper():<3}  {raw:>3}        ({sign}{mod})"


# ── Experience percentage ─────────────────────────────────────────────────────

def xp_for_level(n: int) -> int:
    """
    Total XP accumulated to reach level n from level 1.

    Formula: each level n requires n × 1000 XP to advance through.
      Level 1→2 :  1,000 XP
      Level 2→3 :  2,000 XP
      Level n→n+1: n × 1000 XP
    Cumulative: xp_for(n) = 1000 × n × (n-1) / 2
    """
    if n <= 1: return 0
    return 500 * n * (n - 1)


def xp_percent(level: int, xp: int, max_level: int = 50) -> int:
    """
    Percentage progress through the current level toward the next.

    At max level the interval is still computed (level+1 threshold),
    so a capped character shows > 100% when they keep accumulating XP.

    Examples
    --------
      Level 5,  500 XP into the interval  →  10 %
      Level 50, 5.62 × the 50,000 XP interval  →  562 %
    """
    floor    = xp_for_level(level)
    ceiling  = xp_for_level(level + 1)   # also works past max_level
    interval = ceiling - floor            # = level × 1000
    if interval <= 0:
        return 0
    raw = (xp - floor) / interval * 100
    return max(0, int(raw))


# ── Saving throw system ──────────────────────────────────────────────────────

# DIKU save key → D&D ability score used for base modifier
SAVE_STAT: dict[str, str] = {
    "par": "con",   # Paralysis          — Constitution
    "rod": "dex",   # Rods / Wands       — Dexterity
    "pet": "con",   # Petrification      — Constitution
    "bre": "dex",   # Breath weapon      — Dexterity
    "spe": "int",   # Spells (override per class via SPELL_SAVE_STAT below)
}

# Spell save uses a different ability depending on how the class casts
SPELL_SAVE_STAT: dict[str, str] = {
    "wizard":    "int",
    "mage":      "int",
    "sorcerer":  "cha",
    "warlock":   "cha",
    "bard":      "cha",
    "cleric":    "wis",
    "druid":     "wis",
    "shaman":    "wis",
    "paladin":   "cha",
    "ranger":    "wis",
    # Martial classes default to INT (rare saves, low bonus is intentional)
}

# Class proficient saving throws — adds proficiency_bonus to that save
CLASS_SAVE_PROFS: dict[str, frozenset] = {
    "warrior":   frozenset({"str", "con"}),
    "fighter":   frozenset({"str", "con"}),
    "barbarian": frozenset({"str", "con"}),
    "paladin":   frozenset({"wis", "cha"}),
    "ranger":    frozenset({"str", "dex"}),
    "monk":      frozenset({"str", "dex"}),
    "rogue":     frozenset({"dex", "int"}),
    "wizard":    frozenset({"int", "wis"}),
    "mage":      frozenset({"int", "wis"}),
    "sorcerer":  frozenset({"con", "cha"}),
    "warlock":   frozenset({"wis", "cha"}),
    "bard":      frozenset({"dex", "cha"}),
    "cleric":    frozenset({"wis", "cha"}),
    "druid":     frozenset({"int", "wis"}),
    "shaman":    frozenset({"wis", "con"}),
}


def saving_throw(char, save_key: str,
                 equip_bonus: int = 0,
                 effect_bonus: int = 0) -> int:
    """
    Calculate a DIKU-style saving throw total for a character.

    Formula
    -------
    total = stat_modifier [+ proficiency if class is proficient] + equip_bonus + effect_bonus

    Save key → ability mapping
    --------------------------
      PAR → CON    ROD → DEX    PET → CON
      BRE → DEX    SPE → class-dependent (see SPELL_SAVE_STAT)

    Class proficiencies
    -------------------
      Warrior / Fighter  : STR, CON   (PAR and PET get +prof)
      Rogue              : DEX, INT   (ROD and BRE get +prof)
      Wizard / Mage      : INT, WIS   (SPE gets +prof)
      Cleric / Shaman    : WIS, CON   (SPE and PAR/PET share)
      etc.

    Equipment and active effects stack on top as flat bonuses.
    """
    save_key = save_key.lower()

    # Determine which stat drives this save
    cls_lower = char.cclass.lower() if hasattr(char, "cclass") else ""
    if save_key == "spe":
        stat = SPELL_SAVE_STAT.get(cls_lower, "int")
    else:
        stat = SAVE_STAT.get(save_key, "con")

    base = modifier(char.computed_stat(stat))

    # Proficiency bonus if the class is proficient in this stat's save
    profs = CLASS_SAVE_PROFS.get(cls_lower, frozenset())
    if stat in profs:
        base += proficiency_bonus(char.level)

    return base + equip_bonus + effect_bonus


# ── Point buy helper (1-100 scale) ───────────────────────────────────────────

POINT_BUY_BUDGET = 27   # standard 5e budget

# Cost to raise one stat from 75 (baseline) to the given value,
# mapped from the D&D 8→15 range onto our 75→100 range.
_COST: dict[int, int] = {
    75: 0,   # 8 in D&D  — free
    80: 1,   # 9
    85: 2,   # 10
    90: 3,   # 11
    95: 4,   # 12
    # Non-linear above here (mirrors D&D 5e cost increase)
    97: 5,   # 13
   100: 7,   # 14  (maps to D&D 14 = 7 pts)
   103: 9,   # 15  (human max before racial, costs 9 pts)
}

def point_buy_cost(value: int) -> int:
    """
    Cost in points to raise a stat from 75 to *value* during character creation.
    Values not in the table cost 999 (invalid).
    """
    return _COST.get(value, 999)
