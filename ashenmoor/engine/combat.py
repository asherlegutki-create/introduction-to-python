"""
ashenmoor.engine.combat
────────────────────────
Combat math and round resolution.

Inspired by classic Diku/ROM-style THAC0 hit systems.

Hit resolution  (d100 roll vs hit_chance 5–95)
────────────────────────────────────────────────
  roll  1–3   → CRIT   (heavy damage + message)
  roll < chance → HIT
  roll ≥ 99   → FUMBLE (attacker stumbles, loses the attack)
  else        → MISS

Damage formula
──────────────
  weapon dice  (from Weapon.dice, e.g. "2d8")
  + damroll    (from Weapon.damroll)
  + STR bonus  (every 10 pts above 75 = +1)
  crits add an extra weapon die and ×1.5 multiplier

HP formula  (if not set in the character/mob dict)
──────────────────────────────────────────────────
  max_hp = (CON // 5) × level  +  level × 5
  level 1  CON 80  →  21 hp
  level 20 CON 90  →  460 hp
  level 50 CON 100 →  1250 hp
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.character import Character

# ── Dice ──────────────────────────────────────────────────────────────────────

def parse_dice(dice_str: str) -> tuple[int, int]:
    """'2d8' → (2, 8)"""
    n, s = dice_str.lower().split("d")
    return int(n), int(s)

def roll_dice(dice_str: str) -> int:
    """Roll the dice string and return the total."""
    n, s = parse_dice(dice_str)
    return sum(random.randint(1, s) for _ in range(n))

# ── Hit type constants ─────────────────────────────────────────────────────────

MISS   = 0
HIT    = 1
CRIT   = 2
FUMBLE = 3

# ── HP helpers ─────────────────────────────────────────────────────────────────

def compute_max_hp(char) -> int:
    """Derive max HP from CON and level when not specified in the template."""
    con   = char.get_stat("con")
    level = max(1, char.level)
    return max(10, (con // 5) * level + level * 5)


def ensure_hp(char) -> None:
    """Lazy-init hp/max_hp on a character or mob if missing."""
    if not getattr(char, "max_hp", 0):
        char.max_hp = compute_max_hp(char)
    if not hasattr(char, "hp"):
        char.hp = char.max_hp


def hp_bar(hp: int, max_hp: int, width: int = 10) -> str:
    """Return a Diku-colored bar: [|||||.....] sized to width."""
    max_hp = max(1, max_hp)
    hp     = max(0, min(hp, max_hp))
    pct    = hp / max_hp
    filled = int(pct * width)
    empty  = width - filled
    if pct > 0.66:
        color = "&+G"
    elif pct > 0.33:
        color = "&+Y"
    else:
        color = "&+R"
    bar = f"{color}{'|' * filled}&x{'.' * empty}&N"
    return f"[{bar}]"


def hp_status(char) -> str:
    """'Name [||||......] 80/200 hp'"""
    hp  = getattr(char, "hp",     0)
    mhp = getattr(char, "max_hp", 1)
    return f"&w{char.name}&N {hp_bar(hp, mhp)} &W{hp}&w/&W{mhp}&w hp&N"


def condition_str(char) -> str:
    """Verbal HP description used by 'consider'."""
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

# ── Hit chance (THAC0-style) ───────────────────────────────────────────────────

def calc_hit_chance(attacker, defender) -> int:
    """
    Return integer % chance to hit, bounded 5–95.

    Attacker adds: STR bonus, DEX bonus, level × 2, weapon hitroll.
    Defender subtracts: DEX-based dodge bonus.
    Large level gaps apply a quadratic penalty to the attacker.
    """
    str_bonus = attacker.get_stat("str") // 5      # 0–20+
    dex_bonus = attacker.get_stat("dex") // 10     # 0–10+
    lvl_bonus = attacker.level * 2                  # scales with level

    weapon  = (attacker.equipment.get("primary_hand")
               if hasattr(attacker, "equipment") else None)
    hitroll = getattr(weapon, "hitroll", 0) if weapon else 0

    # Defender's DEX reduces attacker's chance
    def_dodge = -(defender.get_stat("dex") // 10)  # 0 to -10+

    # Quadratic penalty when target is much higher level
    acceptable = attacker.level * 3 // 5
    excess      = max(0, defender.level - attacker.level - acceptable)
    lvl_penalty = excess * excess

    chance = str_bonus + dex_bonus + lvl_bonus + hitroll + def_dodge - lvl_penalty
    return max(5, min(95, chance))

# ── Single attack ──────────────────────────────────────────────────────────────

def calc_damage(attacker, crit: bool = False) -> int:
    """
    Weapon dice + damroll + STR bonus.
    Crits add an extra weapon die roll and multiply by 1.5.
    Unarmed damage scales as 1d(2 + level // 5).
    """
    weapon  = (attacker.equipment.get("primary_hand")
               if hasattr(attacker, "equipment") else None)

    if weapon and hasattr(weapon, "dice"):
        base    = roll_dice(weapon.dice)
        damroll = getattr(weapon, "damroll", 0)
        extra   = roll_dice(weapon.dice) if crit else 0
    else:
        # Bare-hand: grows a little with level
        sides   = max(2, 2 + attacker.level // 5)
        base    = random.randint(1, sides)
        damroll = 0
        extra   = random.randint(1, sides) if crit else 0

    # STR bonus: each 10 points above 75 adds 1 damage
    str_bonus = max(0, (attacker.get_stat("str") - 75) // 10)

    total = base + damroll + str_bonus + extra
    if crit:
        total = int(total * 1.5)
    return max(1, total)


# Damage verbs — indexed by damage as % of target's current HP
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

def _damage_verb(damage: int, target_hp: int) -> str:
    """Return the verb phrase matching damage as % of target's current HP."""
    pct = (damage * 100) // max(1, target_hp)
    for threshold, verb in _DAM_VERBS:
        if pct <= threshold:
            return verb
    return "&+ROBLITERATES&N"


def one_attack(attacker, defender) -> tuple[int, int, str]:
    """
    Resolve one attack swing.

    Returns
    -------
    (damage, hit_type, diku_colored_message)
      damage   = 0 on miss/fumble
      hit_type = MISS | HIT | CRIT | FUMBLE
    """
    chance = calc_hit_chance(attacker, defender)
    roll   = random.randint(1, 100)

    fumble = roll >= 99
    crit   = (not fumble) and roll <= 3
    hit    = (not fumble) and (crit or roll < chance)

    if fumble:
        return (0, FUMBLE,
                f"&w{attacker.name}&N stumbles and swings wildly!&N")

    if not hit:
        return (0, MISS,
                f"&w{attacker.name}&N misses &N{defender.name}&w.&N")

    dmg = calc_damage(attacker, crit=crit)

    old_hp      = defender.hp
    defender.hp = max(0, defender.hp - dmg)
    verb        = _damage_verb(dmg, old_hp)

    prefix = "&+W[CRITICAL HIT] &N" if crit else ""
    msg    = (f"{prefix}&w{attacker.name}&N {verb} "
              f"&N{defender.name}&w (&W{dmg}&w damage)&N")

    return dmg, CRIT if crit else HIT, msg

# ── Full combat round ──────────────────────────────────────────────────────────

def combat_round(player, target) -> list[str]:
    """
    One full round: player swings, then (if target survives) target hits back.

    Returns a list of Diku-colored message strings in order.
    Does NOT remove dead combatants — the caller handles that.
    """
    ensure_hp(player)
    ensure_hp(target)

    msgs: list[str] = []

    # Player's attack
    _, _, msg = one_attack(player, target)
    msgs.append(msg)

    # Counter-attack only if target is still standing
    if target.hp > 0:
        _, _, msg = one_attack(target, player)
        msgs.append(msg)

    return msgs
