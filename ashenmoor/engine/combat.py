"""
ashenmoor.engine.combat
────────────────────────
Unified d20 combat system, 0-100 AC scale.

Attack resolution
─────────────────
  attack_score = (d20 + ability_modifier) × 5

  Compare to target AC (0-100):
    • Natural 20    → critical hit   (double dice, always hits)
    • Natural 1     → automatic miss (regardless of modifiers)
    • Otherwise     → hit if attack_score ≥ AC

  Why ×5?  The d20 range (1-20) × 5 = 5-100, which maps naturally onto
  the 0-100 AC scale.  A +5 modifier (human peak) adds 25 to the score,
  making it noticeably harder to miss but never a guarantee against high
  AC targets.  A maxed Ogre (+21 STR) effectively always hits anything
  not protected by divine magic.

Attack modifier
───────────────
  = STR modifier + proficiency_bonus + weapon_hitroll
  (DEX modifier used instead of STR when weapon has finesse AND DEX > STR)

Damage
──────
  Melee  :  weapon dice  + STR modifier  (DEX if finesse)
  Unarmed:  1d(level ÷ 5, min 1)  + STR modifier
  Crit   :  double weapon dice, then add modifiers once (5e rule)

Examples
────────
  Fighter  STR 90  → modifier +3   → base attack range (1+3)×5=20 to (20+3)×5=115
  Ogre     STR 180 → modifier +21  → base attack range 110 to 205   (capped at hit)
  AC 25    (unarmored DEX 75)   → needs attack_score ≥ 25 → very easy
  AC 65    (chain mail)         → needs d20+3 ≥ 13  →  ~40% hit chance for +3 fighter
  AC 80    (plate)              → needs d20+3 ≥ 16  →  ~25% hit chance
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.character import Character

# ── Dice helpers ───────────────────────────────────────────────────────────────

def parse_dice(dice_str: str) -> tuple[int, int]:
    """'2d8' → (2, 8)"""
    n, s = dice_str.lower().split("d")
    return int(n), int(s)

def roll_dice(dice_str: str) -> int:
    n, s = parse_dice(dice_str)
    return sum(random.randint(1, s) for _ in range(n))

# ── Hit type constants ─────────────────────────────────────────────────────────

MISS   = 0
HIT    = 1
CRIT   = 2

# ── HP helpers ─────────────────────────────────────────────────────────────────

def compute_max_hp(char) -> int:
    """Derive max HP from CON modifier and level when not set in the template."""
    from ..dnd.abilities import char_modifier
    con_mod = char_modifier(char, "con")
    level   = max(1, char.level)
    # Base 10 HP + (10 + CON modifier) per level, minimum 1 per level
    return max(level, 10 + (max(1, 10 + con_mod) * level))

def ensure_hp(char) -> None:
    if not getattr(char, "max_hp", 0):
        char.max_hp = compute_max_hp(char)
    if not hasattr(char, "hp"):
        char.hp = char.max_hp

def hp_bar(hp: int, max_hp: int, width: int = 10) -> str:
    max_hp = max(1, max_hp)
    hp     = max(0, min(hp, max_hp))
    pct    = hp / max_hp
    filled = int(pct * width)
    empty  = width - filled
    color  = "&+G" if pct > 0.66 else ("&+Y" if pct > 0.33 else "&+R")
    return f"[{color}{'|' * filled}&x{'.' * empty}&N]"

def hp_status(char) -> str:
    hp  = getattr(char, "hp",     0)
    mhp = getattr(char, "max_hp", 1)
    return f"&w{char.name}&N {hp_bar(hp, mhp)} &W{hp}&w/&W{mhp}&w hp&N"

def condition_str(char) -> str:
    hp  = getattr(char, "hp",     1)
    mhp = getattr(char, "max_hp", 1)
    pct = hp / max(1, mhp)
    if pct >= 1.00: return "&+Gin perfect health&N"
    if pct >= 0.90: return "&+Gslightly scratched&N"
    if pct >= 0.75: return "&Gwounded&N"
    if pct >= 0.50: return "&Ybadly wounded&N"
    if pct >= 0.25: return "&Rnastily wounded&N"
    if pct >  0.10: return "&+Rcritically wounded&N"
    return "&+RAT DEATH'S DOOR&N"

# ── Attack modifier ────────────────────────────────────────────────────────────

def _attack_mod(attacker) -> int:
    """
    Total attack bonus:
        ability_modifier + proficiency_bonus + weapon_hitroll

    Uses STR, or DEX if weapon has finesse AND DEX modifier is higher.
    """
    from ..dnd.abilities import char_modifier, proficiency_bonus

    str_mod = char_modifier(attacker, "str")
    dex_mod = char_modifier(attacker, "dex")
    prof    = proficiency_bonus(attacker.level)

    weapon  = (attacker.equipment.get("primary_hand")
               if hasattr(attacker, "equipment") else None)
    finesse = getattr(weapon, "finesse", False)
    att_mod = max(str_mod, dex_mod) if finesse else str_mod
    magic   = getattr(weapon, "hitroll", 0) if weapon else 0

    return att_mod + prof + magic


# ── Damage roll ────────────────────────────────────────────────────────────────

def calc_damage(attacker, crit: bool = False) -> int:
    """
    Roll damage for one hit (crit = double weapon dice, then add modifiers once).
    """
    from ..dnd.abilities import char_modifier

    str_mod = char_modifier(attacker, "str")
    dex_mod = char_modifier(attacker, "dex")
    weapon  = (attacker.equipment.get("primary_hand")
               if hasattr(attacker, "equipment") else None)
    dnd     = getattr(attacker, "dnd", {}) or {}
    eq      = getattr(attacker, "equipment", {})

    if weapon and hasattr(weapon, "dice"):
        n, s    = parse_dice(weapon.dice)
        two_h   = getattr(weapon, "two_handed", False)
        finesse = getattr(weapon, "finesse", False)

        rolls = [random.randint(1, s) for _ in range(n * (2 if crit else 1))]

        # Great Weapon Fighting: reroll 1s and 2s once on two-handers
        if dnd.get("fighting_style") == "great_weapon" and two_h:
            from ..dnd.classes.warrior import great_weapon_reroll
            rolls = great_weapon_reroll(rolls, s)

        base    = sum(rolls)
        magic   = getattr(weapon, "damroll", 0)
        dam_mod = max(str_mod, dex_mod) if finesse else str_mod

        # Dueling: +2 damage when wielding a one-hander with no off-hand weapon
        if (not two_h and not finesse
                and dnd.get("fighting_style") == "dueling"
                and not eq.get("secondary_hand")):
            dam_mod += 2

        return max(1, base + magic + dam_mod)

    else:
        # Unarmed — scales with level so mobs remain threatening at high level
        sides = max(1, attacker.level // 5)
        rolls = [random.randint(1, sides) for _ in range(2 if crit else 1)]
        return max(1, sum(rolls) + str_mod)


# ── Damage verbs (relative to target's max HP) ────────────────────────────────

_DAM_VERBS: list[tuple[int, str]] = [
    (2,   "&wbarely scratches&N"),
    (5,   "&wscratches&N"),
    (10,  "&chits&N"),
    (16,  "&chits hard&N"),
    (22,  "&Chits very hard&N"),
    (30,  "&Ydevastates&N"),
    (45,  "&+YMASSACRES&N"),
    (999, "&+RNEARLY SLAYS&N"),
]

def _damage_verb(damage: int, target_max_hp: int) -> str:
    pct = (damage * 100) // max(1, target_max_hp)
    for threshold, verb in _DAM_VERBS:
        if pct <= threshold:
            return verb
    return "&+ROBLITERATES&N"


# ── Single attack ──────────────────────────────────────────────────────────────

def one_attack(attacker, defender) -> tuple[int, int, str]:
    """
    Resolve one attack swing.

    Attack score = (d20 + ability_modifier) × 5
    Hit if attack_score ≥ target AC (0-100)

    Returns (damage, hit_type, diku_coloured_message).
    """
    from ..dnd.armor import get_ac

    roll = random.randint(1, 20)
    ac   = get_ac(defender)

    # Natural 1 — automatic miss
    if roll == 1:
        return (0, MISS,
                f"&w{attacker.name}&N fumbles and misses completely!&N")

    # Natural 20 — critical hit regardless of AC
    if roll == 20:
        dmg         = calc_damage(attacker, crit=True)
        defender.hp = max(0, defender.hp - dmg)
        return (dmg, CRIT,
                f"&+W[CRITICAL HIT!] &w{attacker.name}&N devastates "
                f"&N{defender.name}&w for &W{dmg}&w damage!&N")

    # Normal roll — attack score vs AC
    att_mod      = _attack_mod(attacker)
    attack_score = (roll + att_mod) * 5

    if attack_score < ac:
        return (0, MISS,
                f"&w{attacker.name}&N misses &N{defender.name}&w "
                f"(score &W{attack_score}&w vs AC &W{ac}&w).&N")

    dmg         = calc_damage(attacker, crit=False)
    defender.hp = max(0, defender.hp - dmg)
    verb        = _damage_verb(dmg, getattr(defender, "max_hp", dmg))

    return (dmg, HIT,
            f"&w{attacker.name}&N {verb} &N{defender.name}&w "
            f"(&W{dmg}&w dmg | score &W{attack_score}&w vs AC &W{ac}&w)&N")


# ── Off-hand attack ────────────────────────────────────────────────────────────

def off_hand_attack(attacker, defender) -> tuple[int, int, str] | None:
    """
    Bonus off-hand attack for dual-wielding.  Returns None if no off-hand weapon.

    Two-Weapon Fighting style  → add ability modifier to off-hand damage
    No style                   → no ability modifier on off-hand damage
    """
    from ..dnd.armor     import get_ac
    from ..dnd.abilities import char_modifier, proficiency_bonus

    eq     = getattr(attacker, "equipment", {})
    weapon = eq.get("secondary_hand")

    if weapon is None or not hasattr(weapon, "dice"):
        return None
    if getattr(weapon, "two_handed", False):
        return None

    roll = random.randint(1, 20)
    ac   = get_ac(defender)

    if roll == 1:
        return (0, MISS,
                f"&w{attacker.name}&N's off-hand swing misses entirely!&N")

    if roll == 20:
        n, s        = parse_dice(weapon.dice)
        dmg         = sum(random.randint(1, s) for _ in range(n * 2))
        dmg         = max(1, dmg + getattr(weapon, "damroll", 0))
        defender.hp = max(0, defender.hp - dmg)
        return (dmg, CRIT,
                f"&+W[CRIT OFF-HAND] &w{attacker.name}&N hits "
                f"&N{defender.name}&w for &W{dmg}&w damage!&N")

    dnd   = getattr(attacker, "dnd", {}) or {}
    prof  = proficiency_bonus(attacker.level)
    magic = getattr(weapon, "hitroll", 0)
    att_score = (roll + prof + magic) * 5

    if att_score < ac:
        return (0, MISS,
                f"&w{attacker.name}&N's off-hand swing misses "
                f"(score &W{att_score}&w vs AC &W{ac}&w).&N")

    n, s  = parse_dice(weapon.dice)
    rolls = [random.randint(1, s) for _ in range(n)]
    base  = sum(rolls) + getattr(weapon, "damroll", 0)

    # Two-Weapon Fighting adds ability modifier to off-hand damage
    if dnd.get("fighting_style") == "two_weapon":
        str_mod = char_modifier(attacker, "str")
        dex_mod = char_modifier(attacker, "dex")
        finesse = getattr(weapon, "finesse", False)
        base   += max(str_mod, dex_mod) if finesse else str_mod

    dmg         = max(1, base)
    defender.hp = max(0, defender.hp - dmg)
    verb        = _damage_verb(dmg, getattr(defender, "max_hp", dmg))

    return (dmg, HIT,
            f"&w{attacker.name}&N {verb} &N{defender.name}&w off-hand "
            f"(&W{dmg}&w dmg | score &W{att_score}&w vs AC &W{ac}&w)&N")


# ── Combat round ───────────────────────────────────────────────────────────────

def combat_round(player, target, extra_attacks: int = 0) -> list[str]:
    """
    One full combat round: player multi-attacks → off-hand → target replies.

    extra_attacks: added on top of normal count (Action Surge).
    """
    ensure_hp(player)
    ensure_hp(target)

    msgs: list[str] = []

    # ── Player main attacks ───────────────────────────────────────────────
    dnd = getattr(player, "dnd", {}) or {}
    if dnd.get("class") == "warrior":
        from ..dnd.classes.warrior import attack_count
        n_attacks = attack_count(player.level) + extra_attacks
    else:
        n_attacks = 1 + extra_attacks

    for _ in range(n_attacks):
        if target.hp <= 0: break
        _, _, msg = one_attack(player, target)
        msgs.append(msg)

    # ── Off-hand bonus attack ─────────────────────────────────────────────
    if target.hp > 0:
        result = off_hand_attack(player, target)
        if result:
            _, _, msg = result
            msgs.append(msg)

    # ── Target counter-attacks ────────────────────────────────────────────
    if target.hp > 0:
        _, _, msg = one_attack(target, player)
        msgs.append(msg)

    return msgs
