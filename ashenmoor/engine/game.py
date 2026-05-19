"""
ashenmoor.engine.game
─────────────────────
Command resolution: powers → system commands → "Pardon?"
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room     import Room
    from ..core.character import Character

from .targeting import find_target, target_name, parse_target

DIRECTIONS = frozenset({"north","south","east","west","up","down","n","s","e","w","u","d"})
_DIR_EXPAND = {"n":"north","s":"south","e":"east","w":"west","u":"up","d":"down"}

def _expand_direction(d): return _DIR_EXPAND.get(d.lower(), d.lower())

def go(character, locations, rooms, direction):
    direction = _expand_direction(direction)
    room      = rooms[locations[character]]
    dest_id   = room.exit_room_id(direction)
    if dest_id is not None and dest_id in rooms:
        locations[character] = dest_id
        return rooms[dest_id]
    return "&NAlas, you cannot go that way. . . ."


class GameState:

    def __init__(self):
        self.rooms            = {}
        self.characters       = {}
        self.locations        = {}
        self.player           = ""
        self.object_templates = {}
        self.mob_templates    = {}

    def load_world(self, rooms, characters, locations, player=""):
        self.rooms      = rooms
        self.characters = characters
        self.locations  = locations
        self.player     = player or (next(iter(characters)) if characters else "")

    def load_zone(self, zone):
        collisions = set(zone.rooms) & set(self.rooms)
        if collisions:
            import warnings
            warnings.warn(f"Zone '{zone.name}' overwrites room numbers: {sorted(collisions)}", stacklevel=2)
        self.rooms.update(zone.rooms)
        self.object_templates.update(zone.object_templates)
        self.mob_templates.update(zone.mob_templates)

    @property
    def current_room(self):
        room_id = self.locations.get(self.player)
        return self.rooms.get(room_id) if room_id is not None else None

    def _target(self, target_str):
        room = self.current_room
        if room is None: return None
        return find_target(target_str, room, self.locations, self.characters)

    # ── Command handler ───────────────────────────────────────────────────────

    def handle(self, raw: str):
        tokens = raw.strip().lower().split()
        if not tokens: return None
        verb, *args = tokens

        # 1. Player powers
        result = self._try_power(verb, args)
        if result is not None: return result

        # 2. System commands
        if verb in ("quit","exit","leave","q","camp"):   return "quit"
        if verb in DIRECTIONS or verb == "go":
            return go(self.player, self.locations, self.rooms,
                      args[0] if verb == "go" and args else verb)
        if verb in ("look","l"):            return self._cmd_look(args)
        if verb in ("examine","ex","x"):    return self._cmd_examine(args)
        if verb in ("get","take"):          return self._cmd_get(args)
        if verb == "drop":                  return self._cmd_drop(args)
        if verb in ("wear","wield","hold","equip","put"): return self._cmd_wear(args)
        if verb in ("remove","rem","unequip"):            return self._cmd_remove(args)
        if verb in ("inventory","inv","i"):               return self._cmd_inventory()
        if verb in ("equipment","eq"):                    return self._cmd_equipment()
        if verb in ("powers","spells","skills","abilities"): return self._cmd_powers()
        if verb == "who":                   return self._who()
        if verb in ("score","stats","stat"):
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"

        # 3. Unknown
        return "&NPardon?"

    # ── Powers ────────────────────────────────────────────────────────────────

    def _try_power(self, verb, args):
        char = self.characters.get(self.player)
        if not char or not char.powers: return None
        for power in char.powers:
            kws = power.get("keywords", ())
            if isinstance(kws, str): kws = (kws,)
            if verb in (k.lower() for k in kws):
                return self._execute_power(power)
        return None

    def _execute_power(self, power):
        char     = self.characters.get(self.player)
        name     = char.name if char else "Someone"
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=name)
        parts = []
        if user_msg: parts.append(user_msg)
        if room_msg: parts.append(f"&w(others see)&N {room_msg}")
        return "\n".join(parts)

    def _cmd_powers(self):
        char = self.characters.get(self.player)
        if not char:        return "&RNo character found.&N"
        if not char.powers: return "&wYou have no powers.&N"
        lines = [f"&+W{'Power':<20} {'Keywords'}&N", "&w" + "─"*46 + "&N"]
        for p in char.powers:
            lines.append(f"{p.get('name','?'):<20} &c{', '.join(p.get('keywords',()))}&N")
        return "\n".join(lines)

    # ── get / drop ────────────────────────────────────────────────────────────

    def _cmd_get(self, args):
        if not args: return "&wGet what?&N"
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"
        target_str = " ".join(args)
        item = find_target(target_str, room, self.locations, self.characters)
        if item is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        if not getattr(item, "take", False):
            return "&wYou can't pick that up.&N"
        room.objects.remove(item)
        self.characters[self.player].inventory.append(item)
        return f"&wYou pick up &N{item.name}&w.&N"

    def _cmd_drop(self, args):
        if not args: return "&wDrop what?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"
        item = _find_in_inventory(" ".join(args), char)
        if item is None:
            return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
        char.inventory.remove(item)
        room.objects.append(item)
        return f"&wYou drop &N{item.name}&w.&N"

    # ── wear / remove ─────────────────────────────────────────────────────────

    def _cmd_wear(self, args):
        if not args: return "&wWear what?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        item = _find_in_inventory(" ".join(args), char)
        if item is None:
            return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"

        wear_on = getattr(item, "wear_on", None)
        if wear_on is None:
            return f"&wYou can't wear or hold &N{item.name}&w.&N"

        from ..world.equipment import (
            DUAL_SLOTS, WEAR_ON_ALIAS, SLOTS, is_blocking_secondary, actual_slot
        )

        slot   = actual_slot(wear_on)          # resolve alias → real slot
        two_h  = is_blocking_secondary(item)   # does this need both hands?
        msgs   = []

        char.inventory.remove(item)

        # ── Two-handed: goes to primary_hand, clears secondary ────────────────
        if two_h:
            if "secondary_hand" in char.equipment:
                old = char.equipment.pop("secondary_hand")
                char.inventory.append(old)
                msgs.append(f"&wYou must free your secondary hand — &N{old.name}&w goes to inventory.&N")
            if "primary_hand" in char.equipment:
                old = char.equipment.pop("primary_hand")
                char.inventory.append(old)
                msgs.append(f"&wYou remove &N{old.name}&w.&N")
            char.equipment["primary_hand"] = item
            label = SLOTS.get("primary_hand", "primary hand")
            msgs.append(f"&wYou wield &N{item.name}&w with both hands.&N")

        # ── Secondary hand: check primary isn't two-handed ────────────────────
        elif slot == "secondary_hand":
            primary = char.equipment.get("primary_hand")
            if primary and is_blocking_secondary(primary):
                char.inventory.append(item)   # give it back
                return (f"&wYour primary hand is occupied with the two-handed "
                        f"&N{primary.name}&w — you need both hands for that.&N")
            if "secondary_hand" in char.equipment:
                old = char.equipment.pop("secondary_hand")
                char.inventory.append(old)
                msgs.append(f"&wYou remove &N{old.name}&w.&N")
            char.equipment["secondary_hand"] = item
            verb = "block with" if wear_on == "shield" else "hold in your off hand"
            msgs.append(f"&wYou {verb} &N{item.name}&w.&N")

        # ── Dual slot (earring / neck / wrist / finger) ───────────────────────
        elif slot in DUAL_SLOTS:
            current = char.equipment.get(slot, [])
            if not isinstance(current, list): current = [current]
            if len(current) >= 2:
                bumped = current.pop(0)
                char.inventory.append(bumped)
                msgs.append(f"&wYou remove &N{bumped.name}&w to make room.&N")
            current.append(item)
            char.equipment[slot] = current
            label = SLOTS.get(slot, slot).lower()
            msgs.append(f"&wYou wear &N{item.name}&w on your {label}.&N")

        # ── Single slot ───────────────────────────────────────────────────────
        else:
            if slot in char.equipment:
                old = char.equipment.pop(slot)
                char.inventory.append(old)
                msgs.append(f"&wYou remove &N{old.name}&w.&N")
            char.equipment[slot] = item
            verb = "wield" if slot == "primary_hand" else "wear"
            msgs.append(f"&wYou {verb} &N{item.name}&w.&N")

        return "\n".join(msgs)

    def _cmd_remove(self, args):
        if not args: return "&wRemove what?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        item, slot = _find_in_equipment(" ".join(args), char)
        if item is None:
            return f"&wYou're not wearing '&W{' '.join(args)}&w'.&N"

        from ..world.equipment import DUAL_SLOTS
        if slot in DUAL_SLOTS:
            lst = char.equipment[slot]
            lst.remove(item)
            if not lst: del char.equipment[slot]
        else:
            del char.equipment[slot]

        char.inventory.append(item)
        return f"&wYou remove &N{item.name}&w.&N"

    # ── inventory / equipment display ─────────────────────────────────────────

    def _cmd_inventory(self):
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"
        if not char.inventory: return "&wYou are carrying nothing.&N"
        lines = ["&wYou are carrying:&N"]
        for item in char.inventory:
            lines.append(f"  {item.name}")
        return "\n".join(lines)

    def _cmd_equipment(self):
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        from ..world.equipment import SLOTS, DUAL_SLOTS, is_blocking_secondary

        primary = char.equipment.get("primary_hand")
        secondary_blocked = primary and is_blocking_secondary(primary)

        lines = ["&+WYou are wearing:&N"]
        anything = False

        for slot, label in SLOTS.items():
            equipped = char.equipment.get(slot)

            if slot == "secondary_hand" and secondary_blocked and not equipped:
                lines.append(f"  &w{label:<16}&N &x(both hands in use)&N")
                anything = True
                continue

            if not equipped: continue
            anything = True

            if slot in DUAL_SLOTS:
                items = equipped if isinstance(equipped, list) else [equipped]
                for it in items:
                    lines.append(f"  &w{label:<16}&N {it.name}")
            else:
                lines.append(f"  &w{label:<16}&N {equipped.name}")

        if not anything:
            return "&wYou are wearing nothing.&N"
        return "\n".join(lines)

    # ── look / examine ────────────────────────────────────────────────────────

    _ALL_DIRS = frozenset({
        "north","south","east","west","up","down",
        "northeast","northwest","southeast","southwest",
        "n","s","e","w","u","d","ne","nw","se","sw",
    })

    def _cmd_look(self, args):
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"
        if not args: return room.render(self.locations, self.characters)
        token = args[0].lower()
        if token in self._ALL_DIRS:
            direction = _expand_direction(token)
            dest, blocked, msg = room.peek(direction, self.rooms)
            if msg: return msg
            return dest.render(self.locations, self.characters)
        target_str = " ".join(args)
        instance = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance)

    def _cmd_examine(self, args):
        if not args: return "&wExamine what?&N"
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"
        target_str = " ".join(args)
        instance = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance)

    def _describe(self, instance):
        from ..world.mob import Mob
        from ..core.character import Character
        from ..world.objects import Object
        if isinstance(instance, Mob):
            return instance.description or f"You see nothing special about {instance.name}."
        if isinstance(instance, Character):
            return instance.character_sheet()
        if isinstance(instance, Object):
            desc = getattr(instance, "description", "")
            return desc if desc else f"You see nothing special about {target_name(instance)}."
        return str(instance)

    def _who(self):
        if not self.characters: return "&wNobody is here.&N"
        lines = [f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5}&N"]
        lines.append("&w" + "─"*46 + "&N")
        for char in self.characters.values():
            lines.append(f"{char.name:<15} {char.race:<12} {char.cclass:<10} {char.level:>5}")
        return "\n".join(lines)

    def character_list(self): return self._who()


# ── Inventory / equipment search helpers ──────────────────────────────────────

def _find_in_inventory(target_str: str, char) -> object | None:
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in char.inventory:
        if _item_matches(item, keyword):
            matches += 1
            if matches == idx: return item
    return None


def _find_in_equipment(target_str: str, char) -> tuple:
    from ..world.equipment import DUAL_SLOTS
    _, keyword = parse_target(target_str)
    for slot, equipped in char.equipment.items():
        if slot in DUAL_SLOTS:
            items = equipped if isinstance(equipped, list) else [equipped]
            for item in items:
                if _item_matches(item, keyword): return item, slot
        else:
            if _item_matches(equipped, keyword): return equipped, slot
    return None, None


def _item_matches(item, keyword: str) -> bool:
    if hasattr(item, "key_words"):
        if keyword in (k.lower() for k in item.key_words): return True
    return keyword in item.name.lower()
