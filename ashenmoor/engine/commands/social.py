"""
ashenmoor.engine.commands.social
──────────────────────────────────
Social and item-use commands: say, ask, quaff, recite, and item effect application.
"""

from __future__ import annotations

_POTION_WINDOW = 12 * 3600
_POTION_MAX    = 6


def cmd_say(state, args: list) -> str:
    if not args:
        return "&wSay what?&N"
    char    = state.characters.get(state._player)
    name    = char.name if char else state._player
    message = " ".join(args)

    # Broadcast to everyone else in the room
    state._broadcast_to_room(f"&w{name} says '{message}'&N")

    # Echo back to the speaker
    return f"&wYou say '{message}'&N"


def cmd_tell(state, args: list) -> str:
    if len(args) < 2:
        return "&wUsage: &Wtell <person> <message>&N"

    char = state.characters.get(state._player)
    name = char.name if char else state._player

    target_name = args[0].lower()
    message     = " ".join(args[1:])

    # Find the target anywhere on the mud
    target_char = None
    target_key  = None
    for pname, ch in state.characters.items():
        if pname.lower() == target_name:
            target_char = ch
            target_key  = pname
            break

    if target_char is None:
        return f"&WThere is no one named '{args[0]}' here.&N"

    if target_key == state._player:
        return "&WYou can't tell yourself something.&N"

    # Deliver to recipient via their outbox if connected
    srv = getattr(state, "_server", None)
    if srv is not None:
        client = getattr(srv, "_clients", {}).get(target_key)
        if client and not getattr(client, "_closed", True):
            try:
                client._outbox.put_nowait(
                    f"&W{name} tells you '{message}'&N"
                )
            except Exception:
                pass

    # Echo back to sender
    return f"&WYou tell {target_char.name} '{message}'&N"


def cmd_ask(state, args: list) -> str:
    if len(args) < 2:
        return "&wAsk whom, and what?&N"

    from ...world.mob   import Mob
    from ..targeting    import find_target, target_name

    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    target = find_target(args[0], room, state.locations, state.characters)
    if target is None:
        return f"&wYou don't see '&W{args[0]}&w' here.&N"
    if not isinstance(target, Mob):
        return f"&w{target_name(target)}&w looks at you blankly.&N"

    message   = " ".join(args[1:]).lower()
    msg_words = set(message.split())
    parts     = [f"&wYou ask &W{target.name}&w '&w{message}&w'.&N"]

    responses = getattr(target, "responses", {})
    response  = None
    for key, reply in responses.items():
        if key.lower() in msg_words:
            response = reply
            break

    if response:
        if callable(response):
            char   = state.characters.get(state._player)
            result = response(state, char, target)
            if result:
                parts.append(result)
        elif isinstance(response, (tuple, list)):
            parts.append("\n".join(response))
        else:
            parts.append(response)

    return "\n".join(parts)


def cmd_quaff(state, args: list) -> str:
    if not args:
        return "&wQuaff what?&N"
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...world.objects import Potion
    import time as _rt

    keyword = args[0].lower()
    potion  = next(
        (i for i in char.inventory
         if isinstance(i, Potion)
         and any(keyword in kw.lower() for kw in i.key_words)),
        None,
    )
    if potion is None:
        return f"&wYou don't have any '&W{keyword}&w' to quaff.&N"

    now = _rt.time()
    log = [t for t in getattr(char, "potion_log", []) if now - t < _POTION_WINDOW]
    if len(log) >= _POTION_MAX:
        return "&cYou couldn't possibly use another now, your blood is half potion already!&N"

    char.inventory.remove(potion)
    log.append(now)
    char.potion_log = log

    msgs = apply_item_effects(state, potion._data, char, char)
    return "\n".join(msgs) if msgs else ""


def cmd_recite(state, args: list) -> str:
    if not args:
        return "&wRecite what?&N"
    if state._player in state.fighting:
        return "&wYou cannot recite scrolls while in combat!&N"

    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    room = state.current_room
    if room is None:
        return "&RYou are nowhere.&N"

    from ...world.objects import Scroll
    from ..targeting      import find_target

    scroll_kw = args[0].lower()
    scroll    = next(
        (i for i in char.inventory
         if isinstance(i, Scroll)
         and any(scroll_kw in kw.lower() for kw in i.key_words)),
        None,
    )
    if scroll is None:
        return f"&wYou don't have any scroll matching '&W{scroll_kw}&w'.&N"

    target_args = args[1:]
    if target_args:
        target_str = " ".join(target_args).lower()
        if target_str in ("me", "self", "myself", "i"):
            target = char
        else:
            target = find_target(target_str, room, state.locations, state.characters)
            if target is None:
                return f"&wYou don't see '&W{target_str}&w' here.&N"
    else:
        target = char

    target_name_str = getattr(target, "name", "you")
    char.inventory.remove(scroll)

    parts = []
    if target is char:
        parts.append(f"&wYou recite &W{scroll.name}&w.&N")
    else:
        parts.append(f"&wYou recite &W{scroll.name}&w looking at &W{target_name_str}&w.&N")

    if scroll.apply_msg:
        parts.append(scroll.apply_msg)

    parts.extend(apply_item_effects(state, scroll._data, char, target))
    return "\n".join(p for p in parts if p)


def apply_item_effects(state, data: dict, caster, target) -> list[str]:
    """Apply all effects from a potion or scroll data dict."""
    effects = data.get("effects")
    if effects is None:
        effects = [data] if data.get("effect") else []
    msgs = []
    for eff in effects:
        msg = _apply_one_effect(state, eff, caster, target)
        if msg:
            msgs.append(msg)
    return msgs


def _apply_one_effect(state, data: dict, caster, target) -> str | None:
    import copy
    effect = data.get("effect", "")

    if effect == "heal":
        pct    = data.get("heal_pct",  0.0)
        flat   = data.get("heal_flat", 0)
        amount = int(getattr(target, "max_hp", 0) * pct) + flat
        amount = max(1, amount)
        target.hp = min(getattr(target, "max_hp", target.hp), target.hp + amount)
        name = "You" if target is caster else target.name
        verb = "recover" if target is caster else "recovers"
        return f"&G{name} {verb} &W{amount}&G hit points.&N"

    if effect == "damage":
        from ...engine.combat import calc_damage
        mult = data.get("damage_mult", 1.5)
        dmg  = max(1, int(calc_damage(caster) * mult))
        target.hp = max(0, target.hp - dmg)
        return f"&RThe magic strikes &N{target.name}&R for &W{dmg}&R damage!&N"

    if effect.startswith("cure_"):
        effect_id = effect[5:]
        from ...world.effects import remove_effect
        return remove_effect(target, effect_id) or f"&G{target.name} is cleansed of {effect_id}.&N"

    if effect.startswith("apply_"):
        effect_id = effect[6:]
        from ...world.effects import EFFECTS, apply_effect
        template = EFFECTS.get(effect_id)
        if template is None:
            return f"&R[Unknown effect: {effect_id}]&N"
        override = copy.deepcopy(template)
        if "duration" in data:
            override["duration"] = data["duration"]
        return apply_effect(target, override)

    return None
