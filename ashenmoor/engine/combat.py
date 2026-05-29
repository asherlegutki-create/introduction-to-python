"""
ashenmoor.engine.combat
────────────────────────
Unified d20 combat system, 0-100 AC scale.
"""

from __future__ import annotations
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.character import Character

# ── Dice helpers ──────────────────────────────────────────────────────────────

def parse_dice(dice_str: str) -> tuple[int, int]:
    n, s = dice_str.lower().split("d")
    return int(n), int(s)

def roll_dice(dice_str: str) -> int:
    n, s = parse_dice(dice_str)
    return sum(random.randint(1, s) for _ in range(n))

# ── Hit type constants ────────────────────────────────────────────────────────

MISS = 0
HIT  = 1
CRIT = 2

# ── HP helpers ────────────────────────────────────────────────────────────────

def compute_max_hp(char) -> int:
    from ..dnd.abilities import char_modifier
    con_mod = char_modifier(char, "con")
    level   = max(1, char.level)
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

# ── Attack modifier ───────────────────────────────────────────────────────────

def _attack_mod(attacker) -> int:
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

# ── Accumulated damroll ───────────────────────────────────────────────────────

def _accumulated_damroll(attacker) -> int:
    """
    Sum damroll from every equipped weapon (primary + secondary hand).

    Both weapons contribute to the damage pool on every hit — matching
    what the 'att' display already shows.  STR modifier is handled
    separately and applied per-hit based on fighting style.
    """
    eq    = getattr(attacker, "equipment", {})
    total = 0
    for slot in ("primary_hand", "secondary_hand"):
        item = eq.get(slot)
        if item is not None:
            total += getattr(item, "damroll", 0)
    return total

# ── Damage roll ───────────────────────────────────────────────────────────────

def calc_damage(attacker, crit: bool = False) -> int:
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
        rolls   = [random.randint(1, s) for _ in range(n * (2 if crit else 1))]

        if dnd.get("fighting_style") == "great_weapon" and two_h:
            from ..dnd.classes.warrior import great_weapon_reroll
            rolls = great_weapon_reroll(rolls, s)

        base    = sum(rolls)
        magic   = _accumulated_damroll(attacker)
        dam_mod = max(str_mod, dex_mod) if finesse else str_mod

        if (not two_h and not finesse
                and dnd.get("fighting_style") == "dueling"
                and not eq.get("secondary_hand")):
            dam_mod += 2

        return max(1, base + magic + dam_mod)
    else:
        sides   = max(1, attacker.level // 5)
        rolls   = [random.randint(1, sides) for _ in range(2 if crit else 1)]
        str_mod = char_modifier(attacker, "str")
        return max(1, sum(rolls) + str_mod)

# ── Damage verbs ──────────────────────────────────────────────────────────────

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

# ── Single attack ─────────────────────────────────────────────────────────────

def one_attack(attacker, defender) -> tuple[int, int, str]:
    """
    Resolve one attack swing.  Returns (damage, hit_type, message).
    Does NOT fire weapon procs — procs are only checked in combat_round().
    """
    from ..dnd.armor import get_ac

    roll = random.randint(1, 20)
    ac   = get_ac(defender)

    if roll == 1:
        return (0, MISS,
                f"&w{attacker.name}&N fumbles and misses completely!&N")

    if roll == 20:
        dmg         = calc_damage(attacker, crit=True)
        defender.hp = max(0, defender.hp - dmg)
        return (dmg, CRIT,
                f"&+W[CRITICAL HIT!] &w{attacker.name}&N devastates "
                f"&N{defender.name}&w for &W{dmg}&w damage!&N")

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

# ── Weapon proc ───────────────────────────────────────────────────────────────

def _fire_weapon_proc(attacker, defender, msgs: list,
                      slot: str = "primary_hand") -> None:
    """
    Look up and fire the weapon proc for the given equipment slot.

    slot defaults to "primary_hand" for main attacks.
    Pass slot="secondary_hand" for off-hand attacks.

    The proc key is stored as a string on weapon.proc and resolved at
    call time from world.procs.PROCS to avoid circular imports.
    """
    eq     = getattr(attacker, "equipment", {})
    weapon = eq.get(slot)
    if weapon is None:
        return
    proc_key = getattr(weapon, "proc", None)
    if not proc_key:
        return

    from ..world.procs import PROCS
    proc_fn = PROCS.get(proc_key) if isinstance(proc_key, str) else proc_key
    if proc_fn is None:
        print(f"[warn] unknown weapon proc key: {proc_key!r}", flush=True)
        return

    extra_msgs = proc_fn(attacker, defender)
    if extra_msgs:
        msgs.extend(extra_msgs)

# ── Off-hand attack ───────────────────────────────────────────────────────────

def off_hand_attack(attacker, defender) -> tuple[int, int, str] | None:
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

    dnd       = getattr(attacker, "dnd", {}) or {}
    prof      = proficiency_bonus(attacker.level)
    magic     = getattr(weapon, "hitroll", 0)
    att_score = (roll + prof + magic) * 5

    if att_score < ac:
        return (0, MISS,
                f"&w{attacker.name}&N's off-hand swing misses "
                f"(score &W{att_score}&w vs AC &W{ac}&w).&N")

    n, s  = parse_dice(weapon.dice)
    rolls = [random.randint(1, s) for _ in range(n)]
    base  = sum(rolls) + _accumulated_damroll(attacker)

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

# ── Combat round ──────────────────────────────────────────────────────────────

def combat_round(player, target, extra_attacks: int = 0) -> list[str]:
    """
    One full combat round: player attacks → weapon procs → off-hand → target.

    Weapon procs fire after each successful hit, on both primary and
    off-hand weapons independently.  Extra hits generated by a proc call
    one_attack() directly and do not re-trigger procs.
    """
    ensure_hp(player)
    ensure_hp(target)

    msgs: list[str] = []

    # ── Player main attacks + primary-hand proc ───────────────────────────
    dnd = getattr(player, "dnd", {}) or {}
    if dnd.get("class") == "warrior":
        from ..dnd.classes.warrior import attack_count
        n_attacks = attack_count(player.level) + extra_attacks
    else:
        n_attacks = 1 + extra_attacks

    for _ in range(n_attacks):
        if target.hp <= 0:
            break
        dmg, hit_type, msg = one_attack(player, target)
        msgs.append(msg)

        if hit_type != MISS and target.hp > 0:
            _fire_weapon_proc(player, target, msgs, slot="primary_hand")

    # ── Off-hand attack + off-hand proc ──────────────────────────────────
    if target.hp > 0:
        result = off_hand_attack(player, target)
        if result:
            dmg, hit_type, msg = result
            msgs.append(msg)

            if hit_type != MISS and target.hp > 0:
                _fire_weapon_proc(player, target, msgs, slot="secondary_hand")

    # ── Target counter-attacks ────────────────────────────────────────────
    if target.hp > 0:
        _, _, msg = one_attack(target, player)
        msgs.append(msg)

    return msgs
