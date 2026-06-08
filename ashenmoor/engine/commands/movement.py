"""
ashenmoor.engine.commands.movement
────────────────────────────────────
Movement commands and aggro checking.
"""

from __future__ import annotations
import random


_OPPOSITE = {
    "north": "south", "south": "north",
    "east":  "west",  "west":  "east",
    "up":    "down",  "down":  "up",
}


def go(character, locations, rooms, direction):
    from ..game import _expand_direction
    direction = _expand_direction(direction)
    room      = rooms[locations[character]]
    dest_id   = room.exit_room_id(direction)
    if dest_id is not None and dest_id in rooms:
        locations[character] = dest_id
        return rooms[dest_id]
    return "&NAlas, you cannot go that way. . . ."


def cmd_move(state, direction: str) -> str:
    if state._player in state.fighting:
        return "&wYou cannot move while in combat — use &Wflee&w to escape!&N"
    state._resting.pop(state._player, None)

    char        = state.characters.get(state._player)
    old_room_id = state.locations.get(state._player)

    result = go(state._player, state.locations, state.rooms, direction)
    if isinstance(result, str):
        return result

    if char and old_room_id is not None:
        state._broadcast_to_room(
            f"&w{char.name}&N leaves to the {direction}.&N",
            room_id=old_room_id,
        )

    state._save_location()

    if char:
        from_dir = _OPPOSITE.get(direction, direction)
        state._broadcast_to_room(
            f"&w{char.name}&N arrives from the {from_dir}.&N"
        )

    parts = [cmd_look(state, [])]
    aggro = check_aggro(state)
    if aggro:
        parts.append(aggro)
    return "\n".join(parts)


def cmd_look(state, args: list) -> str:
    from ..targeting import find_target
    from .helpers   import find_in_inventory, item_matches, look_in_container
    from ..game     import _expand_direction

    _ALL_DIRS = frozenset({
        "north","south","east","west","up","down",
        "northeast","northwest","southeast","southwest",
        "n","s","e","w","u","d","ne","nw","se","sw",
    })

    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"
    if not args:
        return room.render(state.locations, state.characters, state.fighting, viewer=state._player)

    token = args[0].lower()
    if token in _ALL_DIRS:
        dest, blocked, msg = room.peek(_expand_direction(token), state.rooms)
        if msg:
            return msg
        return dest.render(state.locations, state.characters, state.fighting, viewer=state._player)

    if token == "in" and len(args) >= 2:
        char       = state.characters.get(state._player)
        target_str = " ".join(args[1:])
        container  = find_container_local(target_str, char, room)
        if container is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        from ...world.objects import Container
        if not isinstance(container, Container):
            return f"&w{container.name}&w is not a container.&N"
        return look_in_container(container)

    target_str = " ".join(args)
    instance   = find_target(target_str, room, state.locations, state.characters)
    if instance is None:
        char = state.characters.get(state._player)
        if char:
            instance = find_in_inventory(target_str, char)
    if instance is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    return describe(state, instance, detailed=False)


def cmd_scan(state) -> str:
    from ..game import _expand_direction
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"
    sections: list[str] = []
    for d, label in [("n","north"),("e","east"),("s","south"),("w","west"),("u","up"),("d","down")]:
        vnum = room.exit_room_id(d)
        if vnum is None or vnum not in state.rooms:
            continue
        sections.append(
            f"&+WYou look {label}&N\n{state.rooms[vnum].render(state.locations, state.characters, state.fighting, viewer=state._player)}"
        )
    if not sections:
        return "&wYou see no exits from here.&N"
    return ("\n&w" + "─" * 40 + "&N\n").join(sections)


def cmd_examine(state, args: list) -> str:
    from ..targeting import find_target
    from .helpers   import find_in_inventory
    if not args:
        return "&wExamine what?&N"
    char       = state.characters.get(state._player)
    room       = state.current_room
    target_str = " ".join(args)
    instance   = find_target(target_str, room, state.locations, state.characters) if room else None
    if instance is None and char:
        instance = find_in_inventory(target_str, char)
    if instance is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    if getattr(instance, "is_corpse", False):
        return instance.examine()
    return describe(state, instance, detailed=True)


def describe(state, instance, detailed=False) -> str:
    from ...world.objects   import Container, Object
    from ...world.mob       import Mob
    from ...core.character  import Character
    from .helpers           import examine_container
    from ..targeting        import target_name

    if isinstance(instance, Container):
        if detailed:
            return examine_container(instance)
        desc = getattr(instance, "description", "")
        return desc if desc else f"You see nothing special about {target_name(instance)}."
    if isinstance(instance, Mob):
        return instance.description or f"You see nothing special about {instance.name}."
    if isinstance(instance, Character):
        if detailed:
            return instance.character_sheet()
        pos = getattr(instance, "position", "standing")
        pos_str = {
            "standing": "is standing here.",
            "sitting":  "is sitting here.",
            "resting":  "is here, resting.",
            "kneeling": "is here, kneeling.",
            "reclined": "is here, lying down.",
        }.get(pos, "is here.")
        return f"&w{instance.name}&N {pos_str}"
    if isinstance(instance, Object):
        desc = getattr(instance, "description", "")
        return desc if desc else f"You see nothing special about {target_name(instance)}."
    return str(instance)


def check_aggro(state) -> str | None:
    from ...world.mob       import Mob
    from ...dnd.abilities   import modifier
    from ..combat           import combat_round, ensure_hp
    from .helpers           import personalize_msg

    if state._player in state.fighting:
        return None
    room = state.current_room
    if room is None:
        return None
    char = state.characters.get(state._player)
    if char is None:
        return None

    dex_mod = modifier(char.computed_stat("dex"))

    for mob in getattr(room, "mobs", []):
        if not isinstance(mob, Mob):
            continue
        if not mob.is_alive() or not mob.killable:
            continue
        if not mob.is_hostile_to(state._player):
            continue

        stealth = random.randint(1, 20) + dex_mod
        pp      = mob.passive_perception()
        if state._player in mob.memory:
            pp = max(pp, pp + random.randint(0, 5))
        if stealth >= pp:
            continue

        state.fighting[state._player] = mob
        state._resting.pop(state._player, None)
        mob.add_attacker(state._player)

        # All other hostile mobs in the room pile on immediately
        from .combat import _aggro_dogpile
        _aggro_dogpile(state, room, exclude=mob)

        aggro_msg = (
            f"&+R{mob.name}&w notices you and attacks!&N\n&x(Auto-attack fires every 4 seconds.)&N"
            if mob.aggressive else
            f"&+R{mob.name}&w recognises you and attacks!&N\n&x(Auto-attack fires every 4 seconds.)&N"
        )
        room_aggro = (
            f"&+R{mob.name}&w notices &w{state._player}&N and attacks!&N"
            if mob.aggressive else
            f"&+R{mob.name}&w recognises &w{state._player}&N and attacks!&N"
        )
        state._broadcast_to_room(room_aggro)
        first_out, first_room, first_hp = state._combat_tick_inner()
        if first_room:
            state._broadcast_to_room(first_room)
        parts = [aggro_msg]
        if first_out:
            parts.append(first_out)
        if first_hp:
            parts.append(first_hp)
        return "\n".join(parts)

    return None


# local helper to avoid circular import with helpers.py
def find_container_local(target_str, char, room):
    from .helpers import find_container
    return find_container(target_str, char, room)
