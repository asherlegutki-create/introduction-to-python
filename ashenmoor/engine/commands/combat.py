"""
ashenmoor.engine.commands.combat
─────────────────────────────────
Combat commands and tick handlers.
"""

from __future__ import annotations
import random

from ..combat import (
    combat_round, one_attack, ensure_hp,
    hp_status, condition_str, calc_damage,
)


def _aggro_dogpile(state, room, exclude=None) -> None:
    """
    Make every hostile mob in the room (other than exclude) immediately
    join combat against the player. Called when combat starts so aggro
    mobs pile on without waiting for the next awareness tick.
    """
    from ...world.mob import Mob
    for mob in list(getattr(room, "mobs", [])):
        if not isinstance(mob, Mob):
            continue
        if mob is exclude:
            continue
        if not mob.is_alive() or not mob.killable:
            continue
        if not mob.is_hostile_to(state._player):
            continue
        # Already attacking — don't double-add
        if state._player in getattr(mob, "attackers", set()):
            continue
        mob.add_attacker(state._player)
        state._broadcast_to_room(
            f"&+R{mob.name}&w joins the fight!&N"
        )


def cmd_kill(state, args: list) -> str:
    if not args:
        return "&wKill what?&N"

    from ...world.mob   import Mob
    from ..targeting    import find_target, target_name

    char = state.characters.get(state._player)
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    target = find_target(" ".join(args), room, state.locations, state.characters)
    if target is None:
        return f"&wYou don't see '&W{' '.join(args)}&w' here.&N"
    if not isinstance(target, Mob):
        return f"&w{target_name(target)}&w is not something you can attack.&N"
    if not target.killable:
        return f"&w{target.name}&w is protected — you cannot attack it.&N"

    ensure_hp(char)
    ensure_hp(target)
    state._resting.pop(state._player, None)

    # If already in combat check if switching or already on this target
    prev_target = state.fighting.get(state._player)
    if prev_target is not None:
        if prev_target is target:
            return "&CYou are already fighting them.&N"
        # Switch targets
        state.fighting[state._player] = target
        target.add_attacker(state._player)
        switch_msg = "&CYou switch opponents.&N"
        first_out, first_room, first_hp = state._combat_tick_inner()
        if first_room:
            state._broadcast_to_room(first_room)
        parts = [switch_msg]
        if first_out:
            parts.append(first_out)
        if first_hp:
            parts.append(first_hp)
        return "\n".join(parts)

    state.fighting[state._player] = target
    target.add_attacker(state._player)

    # All other hostile mobs in the room pile on immediately
    _aggro_dogpile(state, room, exclude=target)

    engage_msg = (
        f"&wYou engage &+W{target.name}&w in combat!&N\n"
        f"&wThey appear to be &N{condition_str(target)}&w.&N\n"
        f"&x(Auto-attack fires every 4 seconds. Type a power to use it immediately.)&N"
    )
    state._broadcast_to_room(
        f"&w{char.name}&N engages &+W{target.name}&w in combat!&N"
    )

    first_out, first_room, first_hp = state._combat_tick_inner()
    if first_room:
        state._broadcast_to_room(first_room)
    parts = [engage_msg]
    if first_out:
        parts.append(first_out)
    if first_hp:
        parts.append(first_hp)
    return "\n".join(parts)


def cmd_flee(state) -> str:
    if state._player not in state.fighting:
        return "&wYou aren't fighting anyone.&N"

    char = state.characters.get(state._player)
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    dex      = char.get_stat("dex") if char else 75
    flee_pct = 50 + max(0, (dex - 75) // 5)

    if random.randint(1, 100) > flee_pct:
        target = state.fighting.get(state._player)
        if target:
            ensure_hp(char)
            ensure_hp(target)
            _, _, hit_msg = one_attack(target, char)
            msgs = ["&wYou attempt to flee, but stumble!&N", hit_msg]
            if char.hp <= 0:
                state.fighting.pop(state._player, None)
                char.hp = max(1, char.max_hp // 4)
                msgs += [
                    "&+RYOU HAVE BEEN SLAIN trying to flee!&N",
                    "&wYou collapse… and somehow cling to life.&N",
                ]
            return "\n".join(msgs)
        return "&wYou attempt to flee, but stumble!&N"

    open_exits = [
        ex for ex in room.exits
        if not room.exit_is_blocked(ex["direction"])
        and ex["roomId"] in state.rooms
    ]
    if not open_exits:
        return "&wThere's nowhere to run!&N"

    exit_choice = random.choice(open_exits)

    # Remove player from all mob attacker sets in this room
    for mob in list(getattr(room, "mobs", [])):
        if hasattr(mob, "remember") and state._player in getattr(mob, "attackers", set()):
            mob.remember(state._player)
        if hasattr(mob, "remove_attacker"):
            mob.remove_attacker(state._player)

    state.fighting.pop(state._player, None)
    state.locations[state._player] = exit_choice["roomId"]
    state._save_location()
    dest = state.rooms[exit_choice["roomId"]]
    return (
        f"&wYou flee in a panic to the {exit_choice['direction']}!&N\n"
        f"{dest.render(state.locations, state.characters, state.fighting, viewer=state._player)}"
    )


def cmd_consider(state, args: list) -> str:
    if not args:
        return "Consider killing who?"

    from ...world.mob   import Mob
    from ..targeting    import find_target

    char = state.characters.get(state._player)
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    target = find_target(" ".join(args), room, state.locations, state.characters)
    if target is None:
        return f"Consider killing who?"

    # Non-killable mobs get the PC message
    if not isinstance(target, Mob) or not target.killable:
        return "Would you like to borrow a cross and a shovel?"

    diff = target.level - char.level

    if   diff <= -10: return "That creature appears to be no match for you!"
    elif diff <=  -5: return "You could do it with a needle!"
    elif diff <=  -2: return "Easy."
    elif diff <=  -1: return "Fairly easy."
    elif diff ==   0: return "The perfect match!"
    elif diff <=   1: return "You would need some luck!"
    elif diff <=   2: return "You would need a lot of luck!"
    elif diff <=   3: return "You would need a lot of luck and great equipment!"
    elif diff <=   5: return "Do you feel lucky, punk?"
    elif diff <=  10: return "Are you mad!?"
    elif diff <=  15: return "You ARE mad!"
    elif diff <=  20: return "Why don't you just lie down and pretend you're dead instead?"
    elif diff <=  25: return "What do you want your epitaph to say?!?"
    else:             return "LAUGH This thing will kill you so fast, its not EVEN funny!"


def cmd_rest(state, args: list) -> str:
    if state._player in state.fighting:
        return "&wYou can't rest while in combat!&N"

    if args and args[0].lower() in ("cancel", "stop", "c"):
        if state._player in state._resting:
            del state._resting[state._player]
            return "&wYou stop resting.&N"
        return "&wYou are not currently resting.&N"

    if state._player in state._resting:
        ticks = state._resting[state._player]["ticks"]
        if ticks < 4:
            return f"&wYou are resting. (&W{4-ticks}&w tick{'s' if 4-ticks!=1 else ''} to short-rest abilities)&N"
        elif ticks < 8:
            return f"&wYou are resting. (&W{8-ticks}&w tick{'s' if 8-ticks!=1 else ''} to long-rest abilities)&N"
        else:
            return "&wYou are resting. Type &Wstand&w when ready.&N"

    state._resting[state._player] = {"ticks": 0}
    return "&wYou begin resting.&N"
