"""
ashenmoor.world.procs
─────────────────────
Weapon and item special procedures (procs).

A proc is attached to a weapon by name in the zone template:
    "proc": "windsong"
    "proc": "random_poison"

Procs are called from combat_round() after each successful hit.
They receive (attacker, defender, weapon=None) and return a list of
diku-coloured message strings or (player_msg, room_msg) tuples.
"""

from __future__ import annotations
import random


# ── Windsong ──────────────────────────────────────────────────────────────────

_WINDSONG_ALLOWED: frozenset[str] = frozenset({
    "ranger", "warrior", "fighter",
})

_WINDSONG_OUTER_CHANCE = 20
_WINDSONG_INNER_CHANCE = 10
_WINDSONG_MAX_DEPTH    = 6

_windsong_depth: int  = 0
_windsong_force: bool = False


def windsong(attacker, defender, weapon=None) -> list:
    """
    The Windsong proc — a glittering elven scimitar.

    Returns a list where each element is either:
      str          — same message shown to wielder and room observers
      (str, str)   — (player_msg, room_msg) — different for each audience
    """
    global _windsong_depth, _windsong_force
    from ..engine.combat import one_attack, MISS

    msgs: list = []

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

    if _windsong_depth >= _WINDSONG_MAX_DEPTH:
        return []

    is_outer = (_windsong_depth == 0)
    if not _windsong_force:
        chance = _WINDSONG_OUTER_CHANCE if is_outer else _WINDSONG_INNER_CHANCE
        if random.randint(0, chance - 1) != 0:
            return []

    _windsong_force = False

    race         = getattr(attacker, "race", "")
    extra_swings = 0

    if race == "Human":
        extra_swings += 3

    if random.randint(0, 2) == 0:
        extra_swings += 1
    elif race == "Half Elf":
        extra_swings += 2

    if random.randint(0, 2) == 0:
        extra_swings += 1
    if random.randint(0, 3) == 0:
        extra_swings += 1

    if is_outer:
        extra_swings = max(1, extra_swings)
    elif extra_swings == 0:
        return []

    if is_outer:
        weapon_name  = getattr(weapon, "name", "the scimitar") if weapon else "the scimitar"
        player_flash = (
            "&cThere is a &Wflash of light&N&c at the tip of your scimitar\n"
            "&cas &cw&Ca&N&cv&Ce&N&cs &Co&N&cf &Ce&N&cn&Ce&N&cr&Cg&N&cy&N&c "
            "flow down its blade and enter your body.\n"
            "&cYour vision &Lfad&N&wes t&Wo &N&wa b&Llur&N&c "
            "as your blade comes to life!&N"
        )
        room_flash = (
            f"&cThere is a &Wflash of light&N&c at the tip of {weapon_name}\n"
            f"&cas waves of energy flow down its blade and enter &w{attacker.name}&N&c, whose\n"
            f"&cmovements &Lfad&N&wes t&Wo &N&wa b&Llur&N&c as it comes to life!&N"
        )
        msgs.append((player_flash, room_flash))
    else:
        msgs.append((
            "&cIn a &wb&Llur&N&c of strikes, you turn on your heel "
            "reversing your swing.&N",
            "&cIn a &wb&Llur&N&c of strikes, &w{attacker.name}&N&c turns on his heel "
            "reversing his swing.&N",
        ))

    _windsong_depth += 1
    try:
        for _ in range(extra_swings):
            if defender.hp <= 0:
                break
            dmg, hit_type, hit_msg = one_attack(attacker, defender)
            msgs.append(hit_msg)
            if hit_type != MISS and defender.hp > 0:
                chain_msgs = windsong(attacker, defender, weapon=weapon)
                msgs.extend(chain_msgs)
    finally:
        _windsong_depth -= 1

    return msgs


# ── Random Poison ─────────────────────────────────────────────────────────────

def random_poison(attacker, defender, weapon=None) -> list:
    """
    1-in-30 chance on each successful hit to inject poison into the defender.
    Applies poison for 5 ticks (20 seconds).

    Used by the abyssal spider's fangs and similar venom weapons.
    """
    if random.randint(0, 29) != 0:
        return []

    from ..world.effects import POISON, apply_effect
    import copy

    poison          = copy.deepcopy(POISON)
    poison["duration"] = 5

    already_poisoned = any(
        e.get("id") == "poisoned"
        for e in getattr(defender, "status_effects", [])
    )
    if already_poisoned:
        return []

    apply_effect(defender, poison)

    def_name = getattr(defender, "name", "your target")
    player_msg = f"&cYour venom seeps into &N{def_name}&c's wounds!&N"
    room_msg   = f"&c{attacker.name}&N&c's venom seeps into &N{def_name}&c's wounds!&N"
    return [(player_msg, room_msg)]


# ── Proc registry ─────────────────────────────────────────────────────────────

PROCS: dict[str, callable] = {
    "windsong":     windsong,
    "random_poison": random_poison,
}
