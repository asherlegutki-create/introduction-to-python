"""
ashenmoor.engine.commands.items
────────────────────────────────
Item interaction commands: get, drop, put, open, close, lock, unlock,
inventory, equipment, wear, remove, offhand.
"""

from __future__ import annotations

from .helpers import (
    max_inventory, stack_items, merge_coins, item_matches,
    find_container, find_in_container, find_in_inventory,
    find_in_equipment, look_in_container, examine_container,
    slot_full_msg,
)


# ── Inventory / Equipment display ─────────────────────────────────────────────

def cmd_inventory(state) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    if not char.inventory:
        return "&wYou are carrying nothing.&N"
    lines = stack_items(list(reversed(char.inventory)))
    return "\n".join(["&wYou are carrying:&N"] + [f"  {l}" for l in lines])


def cmd_equipment(state) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...world.equipment import SLOTS, DUAL_SLOTS, is_blocking_secondary, hand_label

    primary     = char.equipment.get("primary_hand")
    sec_blocked = primary and is_blocking_secondary(primary)
    lines       = ["&+WYou are wearing:&N"]
    anything    = False

    for slot in SLOTS:
        equipped = char.equipment.get(slot)

        if slot == "secondary_hand" and sec_blocked and not equipped:
            label = "<wielding two-handed>  "
            lines.append(f"  &w{label}&N &x(both hands in use)&N")
            anything = True
            continue

        if not equipped:
            continue

        anything = True
        if slot in DUAL_SLOTS:
            for it in (equipped if isinstance(equipped, list) else [equipped]):
                label = hand_label(slot, it)
                lines.append(f"  &w{label}&N {it.name}")
        else:
            label = hand_label(slot, equipped)
            lines.append(f"  &w{label}&N {equipped.name}")

    if not anything:
        return "&wYou are wearing nothing.&N"
    return "\n".join(lines)


# ── Get ───────────────────────────────────────────────────────────────────────

def cmd_get(state, args: list) -> str:
    if not args:
        return "&wGet what?&N"
    char = state.characters.get(state._player)
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    if args[0].lower().startswith("all"):
        return _cmd_get_all(state, args, char, room)

    if "from" in args:
        sep      = args.index("from")
        item_str = " ".join(args[:sep])
        cont_str = " ".join(args[sep+1:])
    elif len(args) >= 2 and find_container(args[-1], char, room) is not None:
        item_str = " ".join(args[:-1])
        cont_str = args[-1]
    else:
        item_str = None
        cont_str = None

    if item_str is not None:
        from ...world.objects import Container as ContClass
        container = find_container(cont_str, char, room)
        if container is None:
            return f"&wYou don't see any container called '&W{cont_str}&w'.&N"
        if not isinstance(container, ContClass):
            return f"&w{container.name}&w is not a container.&N"
        if not container.is_open:
            return f"&wThe &N{container.name}&w is closed.&N"
        item = find_in_container(item_str, container)
        if item is None:
            return f"&wYou don't see '&W{item_str}&w' in &N{container.name}&w.&N"
        if len(char.inventory) >= max_inventory(char):
            return "&wYou can hold no more items.&N"
        container.contents.remove(item)
        if getattr(item, "_is_coins", False):
            merge_coins(char, item)
            return f"&wYou pick up {item.name}.&N"
        char.inventory.append(item)
        return f"&wYou take &N{item.name}&w from &N{container.name}&w.&N"

    from ..targeting import find_target
    item = find_target(" ".join(args), room, state.locations, state.characters)
    if item is None:
        return f"&wYou don't see any '&W{' '.join(args)}&w' here.&N"
    if not getattr(item, "take", False):
        return "&wYou can't pick that up.&N"
    if len(char.inventory) >= max_inventory(char):
        return "&wYou can hold no more items.&N"
    room.objects.remove(item)
    char.inventory.append(item)
    return f"&wYou pick up &N{item.name}&w.&N"


def _cmd_get_all(state, args, char, room) -> str:
    from ...world.objects import Container as ContClass
    spec    = args[0].lower()
    keyword = spec.split(".", 1)[1].strip() if "." in spec else None

    container = None
    if len(args) >= 2:
        cont_str  = " ".join(args[1:])
        container = find_container(cont_str, char, room)
        if container is None:
            return f"&wYou don't see any container called '&W{cont_str}&w'.&N"
        if not isinstance(container, ContClass):
            return f"&w{container.name}&w is not a container.&N"
        if not container.is_open:
            return f"&wThe &N{container.name}&w is closed.&N"
        source = list(container.contents)
    else:
        source = list(room.objects)

    max_inv = max_inventory(char)
    msgs    = []

    for item in source:
        if keyword and not item_matches(item, keyword):
            continue
        if not getattr(item, "take", False):
            continue
        if len(char.inventory) >= max_inv:
            msgs.append("&wYou can hold no more items.&N")
            break
        if container:
            container.contents.remove(item)
        else:
            room.objects.remove(item)
        if getattr(item, "_is_coins", False):
            merge_coins(char, item)
            msgs.append(f"&wYou pick up {item.name}.&N")
        else:
            char.inventory.append(item)
            msgs.append(f"&wYou pick up &N{item.name}&w.&N")

    if not msgs:
        src  = f"&N{container.name}" if container else "the room"
        what = f"'{keyword}'" if keyword else "anything"
        return f"&wYou don't see {what} to take{' in ' + src if container else ' here'}.&N"
    return "\n".join(msgs)


# ── Drop ──────────────────────────────────────────────────────────────────────

def cmd_drop(state, args: list) -> str:
    if not args:
        return "&wDrop what?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    if args[0].lower() == "all":
        keyword = args[0][4:].strip() if len(args[0]) > 3 and "." in args[0] else None
        to_drop = [i for i in list(char.inventory) if not keyword or item_matches(i, keyword)]
        if not to_drop:
            what = f"'{keyword}'" if keyword else "anything"
            return f"&wYou have nothing matching {what} to drop.&N"
        msgs = []
        for item in to_drop:
            char.inventory.remove(item)
            room.objects.append(item)
            msgs.append(f"&wYou drop &N{item.name}&w.&N")
        return "\n".join(msgs)

    item = find_in_inventory(" ".join(args), char)
    if item is None:
        return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
    char.inventory.remove(item)
    room.objects.append(item)
    return f"&wYou drop &N{item.name}&w.&N"


# ── Put ───────────────────────────────────────────────────────────────────────

def cmd_put(state, args: list) -> str:
    if not args:
        return "&wPut what?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    room = state.current_room

    if args[0].lower().startswith("all"):
        return _cmd_put_all(state, args, char, room)

    if len(args) < 2:
        return "&wUsage: &Wput <item> <container>&N"

    if "in" in args:
        sep      = args.index("in")
        item_str = " ".join(args[:sep])
        cont_str = " ".join(args[sep+1:])
    else:
        item_str = " ".join(args[:-1])
        cont_str = args[-1]

    item = find_in_inventory(item_str, char)
    if item is None:
        return f"&wYou're not carrying '&W{item_str}&w'.&N"

    from ...world.objects import Container
    container = find_container(cont_str, char, room)
    if container is None:
        return f"&wYou don't see any container called '&W{cont_str}&w'.&N"
    if not isinstance(container, Container):
        return f"&w{container.name}&w is not a container.&N"
    if container is item:
        return "&wYou can't put something inside itself.&N"
    if not container.is_open:
        return f"&wThe &N{container.name}&w is closed.&N"
    if not container.can_fit(item):
        return f"&w{container.name}&w is too full — only &W{int(container.available_capacity)}&w lbs remaining.&N"

    char.inventory.remove(item)
    container.contents.append(item)
    return f"&wYou put &N{item.name}&w into &N{container.name}&w.&N"


def _cmd_put_all(state, args, char, room) -> str:
    from ...world.objects import Container as ContClass
    spec    = args[0].lower()
    keyword = spec.split(".", 1)[1].strip() if "." in spec else None

    if len(args) < 2:
        return "&wPut all into what?&N"

    cont_str  = " ".join(args[1:])
    container = find_container(cont_str, char, room)
    if container is None:
        return f"&wYou don't see any container called '&W{cont_str}&w'.&N"
    if not isinstance(container, ContClass):
        return f"&w{container.name}&w is not a container.&N"
    if not container.is_open:
        return f"&wThe &N{container.name}&w is closed.&N"

    to_put = [
        i for i in list(char.inventory)
        if i is not container and (not keyword or item_matches(i, keyword))
    ]
    if not to_put:
        what = f"'{keyword}'" if keyword else "anything"
        return f"&wYou have nothing matching {what} to put away.&N"

    msgs = []
    for item in to_put:
        if not container.can_fit(item):
            msgs.append(f"&w{container.name}&w is too full for &N{item.name}&w.&N")
            break
        char.inventory.remove(item)
        container.contents.append(item)
        msgs.append(f"&wYou put &N{item.name}&w into &N{container.name}&w.&N")
    return "\n".join(msgs)


# ── Open / Close / Lock / Unlock ──────────────────────────────────────────────

def cmd_open(state, args: list) -> str:
    if not args:
        return "&wOpen what?&N"
    char = state.characters.get(state._player)
    room = state.current_room
    from ...world.objects import Container
    target_str = " ".join(args)
    container  = find_container(target_str, char, room)
    if container is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    if not isinstance(container, Container):
        return f"&w{container.name}&w is not something you can open.&N"
    if container.is_open:
        return f"&w{container.name}&w is already open.&N"
    if getattr(container, "locked", False):
        return f"&w{container.name}&w is locked.&N"
    container.is_open = True
    return f"&wYou open &N{container.name}&w.&N"


def cmd_close(state, args: list) -> str:
    if not args:
        return "&wClose what?&N"
    char = state.characters.get(state._player)
    room = state.current_room
    from ...world.objects import Container
    target_str = " ".join(args)
    container  = find_container(target_str, char, room)
    if container is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    if not isinstance(container, Container):
        return f"&w{container.name}&w is not something you can close.&N"
    if not container.is_open:
        return f"&w{container.name}&w is already closed.&N"
    container.is_open = False
    return f"&wYou close &N{container.name}&w.&N"


def cmd_unlock(state, args: list) -> str:
    if not args:
        return "&wUnlock what?&N"
    char = state.characters.get(state._player)
    room = state.current_room
    from ...world.objects import Container
    target_str = " ".join(args)
    container  = find_container(target_str, char, room)
    if container is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    if not isinstance(container, Container):
        return f"&w{container.name}&w is not something you can unlock.&N"
    if not getattr(container, "locked", False):
        return f"&w{container.name}&w is not locked.&N"
    key_name = getattr(container, "key_name", None)
    if not key_name:
        return f"&w{container.name}&w has no keyhole.&N"
    key = next(
        (i for i in char.inventory
         if getattr(i, "is_key", False) and getattr(i, "key_name", None) == key_name),
        None,
    )
    if key is None:
        return f"&wYou don't have the right key for &N{container.name}&w.&N"
    container.locked = False
    return f"&wYou unlock &N{container.name}&w with &N{key.name}&w.&N"


def cmd_lock(state, args: list) -> str:
    if not args:
        return "&wLock what?&N"
    char = state.characters.get(state._player)
    room = state.current_room
    from ...world.objects import Container
    target_str = " ".join(args)
    container  = find_container(target_str, char, room)
    if container is None:
        return f"&wYou don't see any '&W{target_str}&w' here.&N"
    if not isinstance(container, Container):
        return f"&w{container.name}&w is not something you can lock.&N"
    if getattr(container, "locked", False):
        return f"&w{container.name}&w is already locked.&N"
    key_name = getattr(container, "key_name", None)
    if not key_name:
        return f"&w{container.name}&w has no keyhole.&N"
    key = next(
        (i for i in char.inventory
         if getattr(i, "is_key", False) and getattr(i, "key_name", None) == key_name),
        None,
    )
    if key is None:
        return f"&wYou don't have the right key for &N{container.name}&w.&N"
    if container.is_open:
        container.is_open = False
    container.locked = True
    return f"&wYou lock &N{container.name}&w with &N{key.name}&w.&N"


# ── Wear / Remove / Offhand ───────────────────────────────────────────────────

def cmd_wear(state, args: list) -> str:
    if not args:
        return "&wWear what?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    if " ".join(args) == "all":
        wearable = [it for it in list(char.inventory) if getattr(it, "wear_on", None) is not None]
        if not wearable:
            return "&wYou have nothing to wear.&N"
        msgs = []
        for it in wearable:
            if it in char.inventory:
                msgs.append(_wear_one(char, it))
        return "\n".join(msgs) if msgs else "&wNothing could be worn.&N"

    item = find_in_inventory(" ".join(args), char)
    if item is None:
        return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
    return _wear_one(char, item)


def _wear_one(char, item) -> str:
    from ...world.equipment import DUAL_SLOTS, SLOTS, is_blocking_secondary, actual_slot
    wear_on = getattr(item, "wear_on", None)
    if wear_on is None:
        return f"&wYou can't wear or hold &N{item.name}&w.&N"

    slot  = actual_slot(wear_on)
    two_h = is_blocking_secondary(item)

    if two_h:
        pri = char.equipment.get("primary_hand")
        sec = char.equipment.get("secondary_hand")
        if pri and sec:
            return f"&wYou must free both hands before wielding &N{item.name}&w.&N"
        if pri:
            return f"&wYou must remove &N{pri.name}&w before wielding a two-handed weapon.&N"
        if sec:
            return f"&wYou must remove &N{sec.name}&w from your off hand before wielding a two-handed weapon.&N"
        char.inventory.remove(item)
        char.equipment["primary_hand"] = item
        return f"&wYou wield &N{item.name}&w with both hands.&N"

    if slot == "secondary_hand":
        pri = char.equipment.get("primary_hand")
        if pri and is_blocking_secondary(pri):
            return f"&wYour primary hand is occupied with the two-handed &N{pri.name}&w.&N"
        sec = char.equipment.get("secondary_hand")
        if sec:
            if getattr(sec, "is_shield", False):
                return "&wYou are already wearing a shield.&N"
            return "&wYour off hand is already occupied.&N"
        char.inventory.remove(item)
        char.equipment["secondary_hand"] = item
        verb = "block with" if wear_on in ("shield", "secondary_hand") else "hold in your off hand"
        return f"&wYou {verb} &N{item.name}&w.&N"

    if slot == "primary_hand":
        pri = char.equipment.get("primary_hand")
        if pri and is_blocking_secondary(pri):
            return "&wYou may wield no more weapons.&N"
        if pri:
            sec = char.equipment.get("secondary_hand")
            if sec:
                return "&wYou may wield no more weapons.&N"
            char.inventory.remove(item)
            char.equipment["secondary_hand"] = item
            return f"&wYou wield &N{item.name}&w in your off hand.&N"
        char.inventory.remove(item)
        char.equipment["primary_hand"] = item
        return f"&wYou wield &N{item.name}&w.&N"

    if slot in DUAL_SLOTS:
        current = char.equipment.get(slot, [])
        if not isinstance(current, list):
            current = [current]
        if len(current) >= 2:
            return slot_full_msg(slot)
        char.inventory.remove(item)
        current.append(item)
        char.equipment[slot] = current
        return f"&wYou wear &N{item.name}&w on your {SLOTS.get(slot, slot).lower()}.&N"

    if slot in char.equipment:
        return slot_full_msg(slot)
    char.inventory.remove(item)
    char.equipment[slot] = item
    return f"&wYou wear &N{item.name}&w.&N"


def cmd_remove(state, args: list) -> str:
    if not args:
        return "&wRemove what?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...world.equipment import DUAL_SLOTS

    if args[0].lower() == "all":
        max_inv = max_inventory(char)
        msgs    = []
        for slot in list(char.equipment.keys()):
            equipped = char.equipment.get(slot)
            if equipped is None:
                continue
            items = equipped if isinstance(equipped, list) else [equipped]
            for item in list(items):
                if len(char.inventory) >= max_inv:
                    msgs.append("&wYou can hold no more items.&N")
                    return "\n".join(msgs) if msgs else "&wNothing to remove.&N"
                if slot in DUAL_SLOTS:
                    lst = char.equipment[slot]
                    lst.remove(item)
                    if not lst:
                        del char.equipment[slot]
                else:
                    del char.equipment[slot]
                char.inventory.append(item)
                msgs.append(f"&wYou remove &N{item.name}&w.&N")
        return "\n".join(msgs) if msgs else "&wYou are not wearing anything.&N"

    item, slot = find_in_equipment(" ".join(args), char)
    if item is None:
        return f"&wYou're not wearing '&W{' '.join(args)}&w'.&N"

    from ...world.equipment import DUAL_SLOTS
    if slot in DUAL_SLOTS:
        lst = char.equipment[slot]
        lst.remove(item)
        if not lst:
            del char.equipment[slot]
    else:
        del char.equipment[slot]
    char.inventory.append(item)
    return f"&wYou remove &N{item.name}&w.&N"


def cmd_offhand(state, args: list) -> str:
    if not args:
        return "&wWield what in your off hand?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...world.objects   import Weapon
    from ...world.equipment import is_blocking_secondary

    item = find_in_inventory(" ".join(args), char)
    if item is None:
        return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
    if not isinstance(item, Weapon):
        return f"&w{item.name}&w can't be wielded in your off hand.&N"
    if getattr(item, "two_handed", False):
        return f"&w{item.name}&w requires both hands.&N"

    primary = char.equipment.get("primary_hand")
    if primary and is_blocking_secondary(primary):
        return f"&wYour primary hand is busy with the two-handed &N{primary.name}&w.&N"

    msgs = []
    char.inventory.remove(item)
    if "secondary_hand" in char.equipment:
        bumped = char.equipment.pop("secondary_hand")
        char.inventory.append(bumped)
        msgs.append(f"&wYou move &N{bumped.name}&w back to your inventory.&N")
    char.equipment["secondary_hand"] = item
    msgs.append(f"&wYou wield &N{item.name}&w in your off hand.&N")

    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("class") == "warrior":
        if dnd.get("fighting_style") == "two_weapon":
            msgs.append("&x(Two-Weapon Fighting: off-hand damage includes your ability modifier.)&N")
        elif primary and not getattr(item, "light", False):
            msgs.append("&x(Note: for standard dual-wield both weapons should be Light, or take Two-Weapon Fighting style.)&N")
    return "\n".join(msgs)
