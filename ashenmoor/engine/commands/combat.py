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


def cmd_kill(state, args: list) -> str:
    if not args:
        return "&wKill what?&N"
    if state._player in state.fighting:
        return "&wYou are already in combat!&N"

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
    state.fighting[state._player] = target
    if not getattr(target, "primary_target", None):
        target.primary_target = state._player

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
    angry_mob   = state.fighting.get(state._player)
    if angry_mob is not None and hasattr(angry_mob, "remember"):
        angry_mob.remember(state._player)

    if angry_mob and getattr(angry_mob, "primary_target", None) == state._player:
        other = next(
            (n for n, m in state.fighting.items()
             if m is angry_mob and n != state._player),
            None,
        )
        angry_mob.primary_target = other

    state.fighting.pop(state._player, None)
    state.locations[state._player] = exit_choice["roomId"]
    state._save_location()
    dest = state.rooms[exit_choice["roomId"]]
    return (
        f"&wYou flee in a panic to the {exit_choice['direction']}!&N\n"
        f"{dest.render(state.locations, state.characters)}"
    )


def cmd_consider(state, args: list) -> str:
    if not args:
        return "&wConsider whom?&N"

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
        return f"&w{target_name(target)}&w is not something you can fight.&N"

    ensure_hp(target)
    diff = target.level - char.level
    if   diff <= -10: diff_str = "&+Gcompletely helpless before you&N"
    elif diff <=  -5: diff_str = "&+Gvery easy&N"
    elif diff <=  -2: diff_str = "&Geasy&N"
    elif diff <=   2: diff_str = "&Yan even match&N"
    elif diff <=   5: diff_str = "&Ychallenging&N"
    elif diff <=  10: diff_str = "&Rdangerous&N"
    else:             diff_str = "&+RSUICIDAL&N"

    return "\n".join([
        f"&wYou size up &N{target.name}&w:&N",
        f"  &wDifficulty:&N {diff_str}",
        f"  &wCondition:&N  {condition_str(target)}",
        f"  &wLevel:&N      &W{target.level}&N",
        f"  &wRace:&N       {target.race}",
        f"  &wClass:&N      {target.cclass}",
    ])


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
