"""
ashenmoor.world.procs
─────────────────────
Weapon and item special procedures (procs).

A proc is attached to a weapon by name in the zone template:
    "proc": "windsong"

Procs are called from combat_round() after each successful hit.
They receive (attacker, defender) and return a list of diku-coloured
message strings.
"""

from __future__ import annotations
import random


_WINDSONG_ALLOWED: frozenset[str] = frozenset({
    "ranger", "warrior", "fighter",
})

# Outer proc (normal attack): 1-in-20
_WINDSONG_OUTER_CHANCE = 20

# Inner proc (proc-generated swing): 1-in-10
_WINDSONG_INNER_CHANCE = 10

# Hard recursion cap
_WINDSONG_MAX_DEPTH = 6

# Depth counter — safe in asyncio (single-threaded)
_windsong_depth: int = 0

# When True the trigger check is bypassed (set by the active power)
_windsong_force: bool = False


def windsong(attacker, defender) -> list[str]:
    """
    The Windsong proc — a glittering elven scimitar.

    Architecture
    ────────────
    Once the trigger fires (or is forced by the active power):
      1. Flash of light message always shows.
      2. At least 1 extra swing always fires.
      3. Each extra swing independently rolls the inner 1-in-10 trigger.

    Passive trigger rates:
      Outer (depth 0, normal attack hit): 1-in-20
      Inner (depth 1+, proc-generated):   1-in-10

    Active power (_windsong_force = True): skips trigger check entirely.

    Extra swings per trigger:
      Grey Elf  +3 base, then three random rolls
      Half Elf  +2 on first branch if 1/3 misses
      All       1/3 +1,  1/3 +1,  1/4 +1  (floor at 1)
    """
    global _windsong_depth, _windsong_force
    from ..engine.combat import one_attack, MISS

    msgs: list[str] = []

    # ── Class restriction — fires on every hit ────────────────────────────
    cclass = getattr(attacker, "cclass", "").lower()
    if cclass not in _WINDSONG_ALLOWED:
        dmg         = max(1, getattr(attacker, "max_hp", 20) // 2)
        attacker.hp = max(1, attacker.hp - dmg)
        eq = getattr(attacker, "equipment", {})
        for slot in ("primary_hand", "secondary_hand"):
            item = eq.get(slot)
            if item and getattr(item, "proc", None) == "windsong":
                del eq[slot]
                attacker.inventory.append(item)
                msgs.append(
                    f"&cYour &N{item.name}&c sends waves of pain "
                    f"through your body!\n&cYou drop the weapon.&N"
                )
                break
        return msgs

    # ── Depth cap ─────────────────────────────────────────────────────────
    if _windsong_depth >= _WINDSONG_MAX_DEPTH:
        return []

    # ── Trigger check — skipped when force-activated ──────────────────────
    is_outer = (_windsong_depth == 0)
    if not _windsong_force:
        chance = _WINDSONG_OUTER_CHANCE if is_outer else _WINDSONG_INNER_CHANCE
        if random.randint(0, chance - 1) != 0:
            return []

    # Force only applies to this one call — reset before recursive swings
    # so inner chains use the normal 1-in-10 trigger, not guaranteed fire.
    _windsong_force = False

    # ── Extra swings — always at least 1 ─────────────────────────────────
    race         = getattr(attacker, "race", "")
    extra_swings = 0

    if race == "Grey Elf":
        extra_swings += 3

    if random.randint(0, 2) == 0:    # 1/3 chance
        extra_swings += 1
    elif race == "Half Elf":
        extra_swings += 2

    if random.randint(0, 2) == 0:    # 1/3 chance
        extra_swings += 1
    if random.randint(0, 3) == 0:    # 1/4 chance
        extra_swings += 1

    # Guarantee at least 1 swing on the initial trigger only.
    # Inner triggers (depth > 0) can roll 0 and return silently —
    # this prevents exponential chain growth.
    if is_outer:
        extra_swings = max(1, extra_swings)
    elif extra_swings == 0:
        return []

    # ── Visual message ─────────────────────────────────────────────────────
    if is_outer:
        msgs.append(
            "&cThere is a &Wflash of light&N&c at the tip of your scimitar\n"
            "&cas &cw&Ca&N&cv&Ce&N&cs &Co&N&cf &Ce&N&cn&Ce&N&cr&Cg&N&cy&N&c "
            "flow down its blade and enter your body.\n"
            "&cYour vision &Lfad&N&wes t&Wo &N&wa b&Llur&N&c "
            "as your blade comes to life!&N"
        )
    else:
        msgs.append(
            "&cIn a &Lblu&N&wr o&Wf&N &wstri&Lkes&n&c, you turn on your heel "
            "reversing your swing.&N"
        )

    # ── Extra swings — each rolls the inner trigger ────────────────────────
    _windsong_depth += 1
    try:
        for _ in range(extra_swings):
            if defender.hp <= 0:
                break
            dmg, hit_type, hit_msg = one_attack(attacker, defender)
            msgs.append(hit_msg)
            if hit_type != MISS and defender.hp > 0:
                chain_msgs = windsong(attacker, defender)
                msgs.extend(chain_msgs)
    finally:
        _windsong_depth -= 1

    return msgs


# ── Proc registry ─────────────────────────────────────────────────────────────

PROCS: dict[str, callable] = {
    "windsong": windsong,
}
