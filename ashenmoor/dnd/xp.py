"""
ashenmoor.dnd.xp
────────────────
Experience point system derived from explicit kill-count targets.

Design targets
──────────────
  Levels 1–20   25 kills of same-level mobs to advance one level
  Levels 21–40  50 kills of same-level mobs
  Levels 41–49  100 kills of (player_level + 8) mobs  ← endgame content

  Level-difference multipliers anchored to the level-1 example:
    diff  0  →  1.000×  (same level, 25 kills)
    diff +4  →  1.923×  (13 kills   — exactly 25/13)
    diff +9  →  5.000×   (5 kills   — exactly 25/5)

  These three points uniquely determine a quadratic:
    mult(d) = 0.04274 d² + 0.05980 d + 1   for d ≥ 0
  Verified:
    mult(4) = 0.04274×16 + 0.05980×4 + 1 = 0.684 + 0.239 + 1 = 1.923  ✓
    mult(9) = 0.04274×81 + 0.05980×9 + 1 = 3.462 + 0.538 + 1 = 5.000  ✓

  Negative diffs (mob weaker than player) use exponential decay so
  farming trivially easy mobs rewards less and less XP.

XP interval construction
────────────────────────
  base_mob_xp(L) = 100 × L   (same-level mob XP, scales linearly)

  interval(L) = kills_target × base_mob_xp(target_mob_level) × mult(diff)

  Phases:
    L  1–20: 25 × base_mob_xp(L)           same-level content
    L 21–40: 50 × base_mob_xp(L)           doubled grind
    L 41–49: 100 × base_mob_xp(L+8) × mult(8)   endgame content

  mob_xp_award() reverses this so killing the right mob always gives
  exactly 1/N of the interval (where N is the phase kill target).

Example verification
────────────────────
  Level 1→2 (interval = 25 × 100 = 2,500 XP):
    Kill L1  (diff 0):  2500 / (100 × 1.000) = 25 kills  ✓
    Kill L5  (diff 4):  2500 / (100 × 1.923) = 13 kills  ✓
    Kill L10 (diff 9):  2500 / (100 × 5.000) =  5 kills  ✓

  Level 25→26 (interval = 50 × 2,500 = 125,000 XP):
    Kill L25 (diff 0):  125000 / (2500 × 1.000) = 50 kills  ✓
    Kill L29 (diff 4):  125000 / (2500 × 1.923) = 26 kills  ✓
    Kill L34 (diff 9):  125000 / (2500 × 5.000) = 10 kills  ✓

  Level 49→50 (100 × base(57) × mult(8) ≈ 2,401,000 XP):
    Kill L57 (diff 8):  2401000 / (5700 × 4.213) = 100 kills ✓
    Kill L49 (diff 0):  same interval / 5700     = 421 kills  (intentional — fight harder!)
"""

from __future__ import annotations
import math

MAX_LEVEL: int = 50

# ── Level-difference multiplier ───────────────────────────────────────────────
# Quadratic fitted to: mult(0)=1.0  mult(4)=25/13≈1.923  mult(9)=5.0
_A = 0.04274   # d² coefficient
_B = 0.05980   # d  coefficient


def diff_mult(d: int) -> float:
    """
    XP multiplier for a level difference of *d* (mob_level - player_level).

    Positive d  → mob is stronger → more XP (quadratic growth, capped at 8.0)
    Negative d  → mob is weaker  → less XP (exponential decay, floor 0.05)
    """
    if d >= 0:
        capped = min(d, 12)           # beyond 12 player likely cannot survive
        return min(8.0, _A * capped * capped + _B * capped + 1.0)
    else:
        capped = max(d, -15)
        return max(0.05, math.exp(0.19 * capped))


# Pre-compute a reference table for display and tuning
DIFF_MULT_TABLE: dict[int, float] = {
    d: round(diff_mult(d), 3) for d in range(-10, 13)
}

# ── Base mob XP (same-level mob, scales with level) ───────────────────────────
def _base_mob_xp(mob_level: int) -> int:
    """Raw XP for a mob of *mob_level* before diff adjustment."""
    return 100 * max(1, mob_level)


# ── XP interval per level (how much XP a full level costs) ───────────────────
def _xp_interval(L: int) -> int:
    """XP required to advance FROM level L to L+1."""
    if L <= 0:
        return 0
    if L <= 20:
        # 25 kills of same-level mob
        return 25 * _base_mob_xp(L)
    elif L <= 40:
        # 50 kills of same-level mob
        return 50 * _base_mob_xp(L)
    else:
        # 100 kills of (L+8) endgame content
        return int(100 * _base_mob_xp(L + 8) * diff_mult(8))


# ── XP table (cumulative totals) ──────────────────────────────────────────────
XP_TABLE: dict[int, int] = {1: 0}
for _lvl in range(1, MAX_LEVEL + 1):
    XP_TABLE[_lvl + 1] = XP_TABLE[_lvl] + _xp_interval(_lvl)


# ── Public API ────────────────────────────────────────────────────────────────

def level_for_xp(xp: int) -> tuple[int, int]:
    """
    Return (level, pct) for a raw XP total.

    pct  = 0-100 (progress toward next level).
    At MAX_LEVEL the pct continues past 100 (capped-character accumulation).

    Example
    -------
    Interval for level 2→3 is 3,000.  Character has 3,500 XP.
    → level 2, pct = (3500-2500)/3000 × 100 = 33%
    """
    level = 1
    for n in range(MAX_LEVEL, 0, -1):
        if xp >= XP_TABLE[n]:
            level = n
            break

    floor    = XP_TABLE[level]
    ceiling  = XP_TABLE[level + 1]    # always defined (+1 row pre-built)
    interval = ceiling - floor
    pct      = int((xp - floor) / interval * 100) if interval > 0 else 0
    return level, pct


def mob_xp_award(mob_level: int, player_level: int) -> int:
    """
    XP to award for killing a mob.

    Derived from the player's current XP interval so that killing
    the "intended" content always advances the player at the designed rate:

      Levels 1-20  → same-level mobs   = 1/25 of the interval
      Levels 21-40 → same-level mobs   = 1/50 of the interval
      Levels 41-49 → (L+8)-level mobs  = 1/100 of the interval

    Scaled by diff_mult(mob_level - player_level).
    """
    pl     = max(1, min(player_level, MAX_LEVEL))
    floor  = XP_TABLE.get(pl, 0)
    ceil_  = XP_TABLE.get(pl + 1, XP_TABLE[MAX_LEVEL + 1])
    interval = ceil_ - floor

    # Base XP = "one kill worth of XP at intended difficulty"
    if pl <= 20:
        base_xp = interval / 25
    elif pl <= 40:
        base_xp = interval / 50
    else:
        # Phase 3: base is interval / (100 × mult(8))
        base_xp = interval / (100 * diff_mult(8))

    diff = max(-15, min(12, mob_level - player_level))
    return max(1, int(base_xp * diff_mult(diff)))


# ── Skills gained on level-up ─────────────────────────────────────────────────
LEVEL_UP_SKILLS: dict[str, dict[int, str]] = {
    "warrior": {
        3:  "Improved Critical Strike",
        5:  "Extra Attack",
        7:  "Know Your Enemy",
        9:  "Indomitable",
        11: "Relentless Endurance",
        13: "Battle Hardened",
        15: "Legendary Toughness",
        17: "Improved Action Surge",
        20: "Master at Arms",
        25: "Unbreakable",
        30: "Warlord's Presence",
        40: "Avatar of War",
        50: "Eternal Champion",
    },
    "rogue": {
        3:  "Cunning Action",
        5:  "Uncanny Dodge",
        7:  "Evasion",
        11: "Reliable Talent",
        15: "Slippery Mind",
        18: "Elusive",
        20: "Stroke of Luck",
    },
    "wizard": {
        3:  "Arcane Recovery",
        5:  "Advanced Spellcasting",
        10: "Empowered Spells",
        15: "Overchannel",
        20: "Signature Spells",
    },
    "shaman": {
        3:  "Spirit Bond",
        5:  "Ancestral Blessing",
        10: "Totemic Focus",
        15: "Elder Wisdom",
        20: "Spirit Walker",
    },
    "cleric": {
        3:  "Channel Divinity",
        5:  "Divine Strike",
        10: "Potent Spellcasting",
        14: "Divine Intervention",
        20: "Supreme Healing",
    },
}


def skills_gained_at(cclass: str, level: int) -> str | None:
    """Return the skill name unlocked at *level* for *cclass*, or None."""
    return LEVEL_UP_SKILLS.get(cclass.lower(), {}).get(level)


# ── Level-up handler ──────────────────────────────────────────────────────────

def apply_level_up(char) -> list[str]:
    """
    Apply all pending level-ups for *char* based on their current xp.

    Returns a list of coloured announcement strings.

    Side effects:
      char.level incremented
      char.max_hp increased by (5 + CON modifier), min 1
      char.hp restored by the same amount (capped at max_hp)
      Warrior hit_dice_remaining gains 1
    """
    from ..dnd.abilities import char_modifier

    msgs: list[str] = []

    while char.level < MAX_LEVEL:
        needed = XP_TABLE.get(char.level + 1, 0)
        if char.xp < needed:
            break

        char.level += 1
        con_mod    = char_modifier(char, "con")
        hp_gain    = max(1, 5 + con_mod)
        char.max_hp += hp_gain
        char.hp      = min(char.hp + hp_gain, char.max_hp)

        # Give warriors an extra hit die per level
        dnd = getattr(char, "dnd", None) or {}
        if dnd.get("class") == "warrior":
            dnd["hit_dice_remaining"] = min(
                char.level,
                dnd.get("hit_dice_remaining", 0) + 1,
            )

        skill = skills_gained_at(char.cclass, char.level)
        msgs.append(
            f"&+WYou raise a level!&N"
        )
        if skill:
            msgs.append(f"&+G  New ability: &W{skill}&+G!&N")

    return msgs
