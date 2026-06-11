"""
ashenmoor.engine.combat
────────────────────────
Unified d20 combat system, 0-100 AC scale.

combat_round()        — player attacks their current target
mob_counter_attacks() — one mob swings back, parry resolves here
attempt_parry()       — passive parry for Fighter/Ranger
apply_damage()        — drain temp_hp first, then real hp
trigger_riposte()     — fires when parry succeeds with riposte armed
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
    if not hasattr(char, "temp_hp"):
        char.temp_hp = 0

def apply_damage(char, amount: int) -> int:
    """
    Apply damage, draining temp_hp before real hp.
    Returns the amount of real hp damage taken.
    """
    if amount <= 0:
        return 0
    temp = getattr(char, "temp_hp", 0)
    if temp > 0:
        absorbed     = min(temp, amount)
        char.temp_hp = temp - absorbed
        amount      -= absorbed
    if amount > 0:
        char.hp = max(0, char.hp - amount)
    return amount

def hp_bar(hp: int, max_hp: int, temp_hp: int = 0, width: int = 10) -> str:
    max_hp  = max(1, max_hp)
    real_hp = max(0, min(hp, max_hp))
    pct     = real_hp / max_hp
    filled  = int(pct * width)
    empty   = width - filled

    if temp_hp > 0:
        bar_color = "&M"
    elif pct > 0.66:
        bar_color = "&+G"
    elif pct > 0.33:
        bar_color = "&+Y"
    else:
        bar_color = "&+R"

    return f"[{bar_color}{'|' * filled}&x{'.' * empty}&N]"

def hp_status(char) -> str:
    hp   = getattr(char, "hp",      0)
    mhp  = getattr(char, "max_hp",  1)
    temp = getattr(char, "temp_hp", 0)

    if temp > 0:
        hp_color   = "&M"
        hp_display = hp + temp
    else:
        pct      = hp / max(1, mhp)
        hp_color = "&+G" if pct > 0.66 else ("&+Y" if pct > 0.33 else "&+R")
        hp_display = hp

    bar = hp_bar(hp, mhp, temp)
    return f"&w{char.name}&N {bar} {hp_color}{hp_display}&w/&W{mhp}&w hp&N"

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

# ── Combat stance detection ───────────────────────────────────────────────────

def get_combat_stance(char) -> str:
    """
    Return the player's current combat stance based on equipment.

    Returns one of:
        "shield"     — shield in secondary hand
        "two_handed" — two-handed weapon in primary hand
        "dual"       — weapons in both hands (no shield)
        "standard"   — one weapon (or unarmed), no special stance
    """
    eq      = getattr(char, "equipment", {})
    primary = eq.get("primary_hand")
    offhand = eq.get("secondary_hand")

    if offhand is not None and getattr(offhand, "is_shield", False):
        return "shield"
    if primary is not None and getattr(primary, "two_handed", False):
        return "two_handed"
    from ..world.objects import Weapon as _Weapon
    if (primary is not None and isinstance(primary, _Weapon)
            and offhand is not None and isinstance(offhand, _Weapon)):
        return "dual"
    return "standard"


# ── Level thresholds for defensive abilities ──────────────────────────────────

PARRY_LEVEL        = 5    # Fighters unlock passive parry at level 5
SHIELD_BLOCK_LEVEL = 15   # Fighters unlock shield block at level 15

# ── Shield Block ──────────────────────────────────────────────────────────────

_SHIELD_BLOCK_CLASSES = frozenset({"fighter", "warrior"})

def attempt_shield_block(char, attack_score: int) -> dict:
    """
    Shield block — passive, fires before parry when a shield is equipped.

    Available to Fighters/Warriors at level 15+.
    Champion adds proficiency bonus to the roll.

    Roll: (d20 + STR_mod [+ prof if Champion]) × 5  vs  attack_score
    On success: ALL damage absorbed, but player loses 1 attack this tick
                (tracked via dnd["shield_block_used"] = True).

    Returns the same shape dict as attempt_parry:
        {
            "success":   bool,
            "reduction": int,   — 99999 on success (absorbs everything)
            "shrug":     False, — shield block never triggers shrug
            "msg":       str,
        }
    """
    from ..dnd.abilities import char_modifier, proficiency_bonus as _prof

    cclass = getattr(char, "cclass", "").lower()
    if cclass not in _SHIELD_BLOCK_CLASSES:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    if char.level < SHIELD_BLOCK_LEVEL:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    if get_combat_stance(char) != "shield":
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    dnd      = getattr(char, "dnd", {}) or {}
    subclass = dnd.get("subclass", "")
    str_mod  = char_modifier(char, "str")
    bonus    = _prof(char.level) if subclass == "champion" else 0

    block_score = (random.randint(1, 20) + str_mod + bonus) * 5

    if block_score < attack_score:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    # Block succeeded — mark that one attack is lost this round
    dnd["shield_block_used"] = True

    msg = "&+WYou raise your shield, blocking the blow completely!&N"
    return {"success": True, "reduction": 99999, "shrug": False, "msg": msg}


# ── Parry ─────────────────────────────────────────────────────────────────────

_PARRY_CLASSES = frozenset({"fighter", "warrior", "ranger"})

def attempt_parry(char, attack_score: int) -> dict:
    """
    Passive parry — resolves automatically on every incoming melee hit
    when shield block is unavailable or has failed.

    Available to Fighters/Warriors/Rangers at level 5+.
    Champion adds proficiency bonus to the roll.

    Roll: (d20 + DEX_mod [+ prof if Champion]) × 5  vs  attack_score
    On success: damage reduced by max(0, 2d6 + DEX_mod)
    Champion shrug: 1-in-4 chance on success → zero damage

    Returns:
        {
            "success":   bool,
            "reduction": int,
            "shrug":     bool,
            "msg":       str,
        }
    """
    from ..dnd.abilities import char_modifier, proficiency_bonus as _prof

    cclass = getattr(char, "cclass", "").lower()
    if cclass not in _PARRY_CLASSES:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    if char.level < PARRY_LEVEL:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    dnd      = getattr(char, "dnd", {}) or {}
    subclass = dnd.get("subclass", "")
    dex_mod  = char_modifier(char, "dex")
    bonus    = _prof(char.level) if subclass == "champion" else 0

    parry_score = (random.randint(1, 20) + dex_mod + bonus) * 5

    if parry_score < attack_score:
        return {"success": False, "reduction": 0, "shrug": False, "msg": ""}

    # Parry succeeded — calculate reduction
    reduction = max(0, roll_dice("2d6") + dex_mod)

    # Champion shrug check
    shrug = False
    if subclass == "champion" and random.randint(1, 4) == 4:
        shrug     = True
        reduction = 99999   # absorbs everything

    if shrug:
        msg = "&+WYou deflect your opponent's attack entirely!&N"
    else:
        msg = "&wYou deflect your opponent's attack.&N"

    return {"success": True, "reduction": reduction, "shrug": shrug, "msg": msg}

# ── Riposte ───────────────────────────────────────────────────────────────────

def trigger_riposte(player, target, dnd: dict) -> tuple[list[str], list[str]]:
    """
    Fire a riposte bonus attack after a successful parry.
    Consumes 1 SD from the Battle Master pool.
    Returns (player_msgs, room_msgs).
    """
    from ..dnd.abilities import char_modifier

    dnd["riposte_armed"]    = False   # consumed
    sd_size                 = dnd.get("superiority_die_size", 8)
    dnd["superiority_dice"] = max(0, dnd.get("superiority_dice", 0) - 1)

    sd_roll  = random.randint(1, sd_size)
    str_mod  = char_modifier(player, "str")
    weapon   = (player.equipment.get("primary_hand")
                if hasattr(player, "equipment") else None)
    base_dmg = calc_damage(player)
    total    = max(1, base_dmg + sd_roll)

    apply_damage(target, total)

    p_msg = (
        f"&+WYou deflect your opponent's attack striking back at them! "
        f"(&W{total}&+W dmg, +{sd_roll} SD)&N"
    )
    r_msg = (
        f"&+W{player.name}&N deflects the blow and answers with a devastating counter! "
        f"(&W{total}&+W dmg)&N"
    )
    return [p_msg], [r_msg]

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

    # Precision Attack maneuver — adds SD roll to attack this tick
    dnd = getattr(attacker, "dnd", {}) or {}
    precision_bonus = dnd.pop("precision_bonus", 0)

    return att_mod + prof + magic + precision_bonus

def _accumulated_damroll(attacker) -> int:
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
        finesse = getattr(weapon, "finesse",    False)
        rolls   = [random.randint(1, s) for _ in range(n * (2 if crit else 1))]

        if dnd.get("fighting_style") == "great_weapon" and two_h:
            from ..dnd.classes.fighter import great_weapon_reroll
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

# ── Crit range ────────────────────────────────────────────────────────────────

def _crit_threshold(attacker) -> int:
    """Minimum d20 roll that counts as a critical hit."""
    from ..dnd.classes.fighter import crit_range
    return crit_range(attacker)

# ── Single attack ─────────────────────────────────────────────────────────────

def one_attack(attacker, defender) -> tuple[int, int, str]:
    """
    Resolve one attack swing.
    Attack score = (d20 + ability_modifier) × 5
    Hit if attack_score ≥ target AC (0-100)
    """
    from ..dnd.armor import get_ac

    roll      = random.randint(1, 20)
    ac        = get_ac(defender)
    crit_min  = _crit_threshold(attacker)

    # Adjust AC for any target debuffs (from maneuvers)
    dnd_atk  = getattr(attacker, "dnd", {}) or {}
    debuffs  = dnd_atk.get("target_debuffs", {})
    ac       = max(0, ac - debuffs.get("ac_penalty", 0))

    if roll == 1:
        return (0, MISS,
                f"&w{attacker.name}&N fumbles and misses completely!&N")

    if roll >= crit_min:
        dmg = calc_damage(attacker, crit=True)
        from ..world.effects import apply_dr
        dmg = apply_dr(defender, dmg)
        apply_damage(defender, dmg)
        return (dmg, CRIT,
                f"&+W[CRITICAL HIT!] &w{attacker.name}&N devastates "
                f"&N{defender.name}&w for &W{dmg}&w damage!&N")

    att_mod = _attack_mod(attacker)
    # Apply hit penalty debuff (from disarm)
    att_mod -= debuffs.get("hit_penalty", 0)
    attack_score = (roll + att_mod) * 5

    if attack_score < ac:
        return (0, MISS,
                f"&w{attacker.name}&N misses &N{defender.name}&w "
                f"(score &W{attack_score}&w vs AC &W{ac}&w).&N")

    dmg = calc_damage(attacker, crit=False)
    from ..world.effects import apply_dr
    dmg = apply_dr(defender, dmg)
    apply_damage(defender, dmg)
    verb = _damage_verb(dmg, getattr(defender, "max_hp", dmg))

    return (dmg, HIT,
            f"&w{attacker.name}&N {verb} &N{defender.name}&w "
            f"(&W{dmg}&w dmg | score &W{attack_score}&w vs AC &W{ac}&w)&N")

# ── Weapon proc ───────────────────────────────────────────────────────────────

def _fire_weapon_proc(attacker, defender, player_msgs, room_msgs,
                      slot: str = "primary_hand") -> None:
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
        return
    extra_msgs = proc_fn(attacker, defender, weapon=weapon)
    if extra_msgs:
        for m in extra_msgs:
            if isinstance(m, tuple) and len(m) == 2:
                player_msgs.append(m[0])
                room_msgs.append(m[1])
            else:
                s = str(m)
                player_msgs.append(s)
                room_msgs.append(s)

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

    roll      = random.randint(1, 20)
    ac        = get_ac(defender)
    crit_min  = _crit_threshold(attacker)

    if roll == 1:
        return (0, MISS, f"&w{attacker.name}&N's off-hand swing misses entirely!&N")

    if roll >= crit_min:
        n, s        = parse_dice(weapon.dice)
        dmg         = sum(random.randint(1, s) for _ in range(n * 2))
        dmg         = max(1, dmg + getattr(weapon, "damroll", 0))
        apply_damage(defender, dmg)
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

    dmg  = max(1, base)
    apply_damage(defender, dmg)
    verb = _damage_verb(dmg, getattr(defender, "max_hp", dmg))

    return (dmg, HIT,
            f"&w{attacker.name}&N {verb} &N{defender.name}&w off-hand "
            f"(&W{dmg}&w dmg | score &W{att_score}&w vs AC &W{ac}&w)&N")

# ── Player attack round ───────────────────────────────────────────────────────

def combat_round(player, target, extra_attacks: int = 0) -> tuple[list[str], list[str]]:
    """
    Player's attack round against their current target.
    Clears maneuver_used and decrements maneuver cooldowns at the START.

    If shield_block_used is set (a block landed last tick), the player
    loses 1 attack swing this round — the shield arm was committed to
    the block and isn't free for an instant counter.

    Returns (player_msgs, room_msgs).
    """
    ensure_hp(player)
    ensure_hp(target)

    player_msgs: list[str] = []
    room_msgs:   list[str] = []

    # ── Clear per-tick maneuver state ─────────────────────────────────────
    dnd = getattr(player, "dnd", {}) or {}
    dnd["maneuver_used"] = False

    # Decrement maneuver cooldowns
    cooldowns = dnd.get("maneuver_cooldowns", {})
    for key in cooldowns:
        if cooldowns[key] > 0:
            cooldowns[key] -= 1

    # Clear target debuffs from last tick
    debuffs = dnd.get("target_debuffs", {})
    debuffs["ac_penalty"]  = 0
    debuffs["hit_penalty"] = 0
    # no_counter cleared in mob_counter_attacks after use

    # ── Shield block penalty: lose 1 attack if a block landed last tick ───
    # Champion's combat mastery lets them recover instantly — no penalty.
    block_penalty = 0
    if dnd.pop("shield_block_used", False):
        if dnd.get("subclass") != "champion":
            block_penalty = 1

    # ── Determine attack count ────────────────────────────────────────────
    if dnd.get("class") in ("fighter", "warrior"):
        from ..dnd.classes.fighter import attack_count
        n_attacks = max(1, attack_count(player.level) + extra_attacks - block_penalty)
    else:
        n_attacks = max(1, 1 + extra_attacks - block_penalty)

    if block_penalty:
        player_msgs.append(
            "&xYour shield arm is recovering — one less attack this round.&N"
        )

    for _ in range(n_attacks):
        if target.hp <= 0:
            break
        dmg, hit_type, msg = one_attack(player, target)
        player_msgs.append(msg)
        room_msgs.append(msg)

        if hit_type != MISS and target.hp > 0:
            _fire_weapon_proc(player, target, player_msgs, room_msgs,
                              slot="primary_hand")

    if target.hp > 0:
        result = off_hand_attack(player, target)
        if result:
            dmg, hit_type, msg = result
            player_msgs.append(msg)
            room_msgs.append(msg)
            if hit_type != MISS and target.hp > 0:
                _fire_weapon_proc(player, target, player_msgs, room_msgs,
                                  slot="secondary_hand")

    return player_msgs, room_msgs


# ── Mob counter-attack ────────────────────────────────────────────────────────

def mob_counter_attacks(mob, player) -> tuple[list[str], list[str]]:
    """
    One mob swings back at a player.

    Defence resolution order:
      1. Shield block (Fighter lvl 15+, STR save, absorbs all, costs 1 attack)
      2. Parry (Fighter/Ranger lvl 5+, DEX save, partial reduction)
      3. Riposte fires on successful parry if armed (Battle Master)
    Menace blocks the counter entirely.
    """
    from ..dnd.armor import get_ac

    ensure_hp(mob)
    ensure_hp(player)

    player_msgs: list[str] = []
    room_msgs:   list[str] = []

    dnd     = getattr(player, "dnd", {}) or {}
    debuffs = dnd.get("target_debuffs", {})

    # ── Menacing Attack block ─────────────────────────────────────────────
    if debuffs.get("no_counter"):
        debuffs["no_counter"] = False
        p_msg = "&+WYour menacing strike leaves your foe momentarily frozen — they cannot counter!&N"
        r_msg = f"&+W{player.name}'s menacing strike leaves their foe frozen!&N"
        return [p_msg], [r_msg]

    # ── Roll mob attack ───────────────────────────────────────────────────
    roll         = random.randint(1, 20)
    ac           = get_ac(player)
    att_mod      = _attack_mod(mob)
    attack_score = (roll + att_mod) * 5

    if roll == 1:
        msg = f"&w{mob.name}&N fumbles and misses you completely!&N"
        return [msg], [msg]

    # Crit check — uses base 20 for mobs
    is_crit = (roll == 20)

    if attack_score < ac and not is_crit:
        msg = (f"&w{mob.name}&N misses you "
               f"(score &W{attack_score}&w vs AC &W{ac}&w).&N")
        return [msg], [msg]

    # Hit — calculate raw damage
    dmg = calc_damage(mob, crit=is_crit)
    from ..world.effects import apply_dr
    dmg = apply_dr(player, dmg)

    # ── Defence: shield block first, parry as fallback ────────────────────
    #
    # Shield block (level 15+, STR):
    #   Success → absorbs ALL damage, marks dnd["shield_block_used"] so
    #   combat_round() removes one attack swing this tick.
    #
    # Parry (level 5+, DEX):
    #   Only checked when shield block is unavailable or failed.
    #   Success → partial damage reduction; Champion can shrug to zero.
    #   Riposte triggers on any parry success if armed.

    shield = attempt_shield_block(player, attack_score)
    if shield["success"]:
        player_msgs.append(shield["msg"])
        room_msgs.append(
            f"&w{player.name}&N raises their shield, blocking {mob.name}'s attack!&N"
        )
        dmg = 0
        # Shield block doesn't trigger riposte — you're committed to the block
    else:
        parry = attempt_parry(player, attack_score)
        if parry["success"]:
            player_msgs.append(parry["msg"])
            room_msgs.append(
                f"&w{player.name}&N deflects {mob.name}'s attack.&N"
                if not parry["shrug"] else
                f"&w{player.name}&N shrugs off {mob.name}'s attack entirely!&N"
            )
            dmg = max(0, dmg - parry["reduction"])

            # ── Riposte trigger ───────────────────────────────────────────
            if dnd.get("riposte_armed"):
                sd_pool = dnd.get("superiority_dice", 0)
                if sd_pool > 0:
                    rp, rr = trigger_riposte(player, mob, dnd)
                    player_msgs.extend(rp)
                    room_msgs.extend(rr)

    if dmg > 0:
        apply_damage(player, dmg)
        verb  = _damage_verb(dmg, getattr(player, "max_hp", dmg))
        p_msg = (f"&w{mob.name}&N {verb} you "
                 f"(&W{dmg}&w dmg | score &W{attack_score}&w vs AC &W{ac}&w)&N")
        r_msg = (f"&w{mob.name}&N {verb} &w{player.name}&N "
                 f"(&W{dmg}&w dmg)&N")
        if is_crit:
            p_msg = f"&+W[CRITICAL HIT!] &N" + p_msg
            r_msg = f"&+W[CRITICAL HIT!] &N" + r_msg
        player_msgs.append(p_msg)
        room_msgs.append(r_msg)

    return player_msgs, room_msgs
