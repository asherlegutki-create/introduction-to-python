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

        if verb in ("look","l"):              return self._cmd_look(args)
        if verb in ("examine","ex","x"):      return self._cmd_examine(args)
        if verb in ("get","take"):            return self._cmd_get(args)
        if verb == "drop":                    return self._cmd_drop(args)
        if verb == "put":                     return self._cmd_put(args)
        if verb == "open":                    return self._cmd_open(args)
        if verb == "close":                   return self._cmd_close(args)
        if verb in ("wear","wield","hold","equip","put_on"): return self._cmd_wear(args)
        if verb in ("remove","rem","unequip"):              return self._cmd_remove(args)
        if verb in ("inventory","inv","i"):                 return self._cmd_inventory()
        if verb in ("equipment","eq"):                      return self._cmd_equipment()
        if verb in ("powers","spells","skills","abilities"): return self._cmd_powers()
        if verb == "who":                     return self._who()
        if verb in ("score","stats","stat"):
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"

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

    # ── get / drop / put ─────────────────────────────────────────────────────

    def _cmd_get(self, args):
        """
        get <item>                   — pick up from room
        get <item> from <container>  — take from container (explicit)
        get <item> <container>       — take from container (implicit: last word)
        """
        if not args: return "&wGet what?&N"
        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        # Resolve item_str / cont_str
        if "from" in args:
            sep      = args.index("from")
            item_str = " ".join(args[:sep])
            cont_str = " ".join(args[sep+1:])
        elif len(args) >= 2 and _find_container(args[-1], char, room) is not None:
            item_str = " ".join(args[:-1])
            cont_str = args[-1]
        else:
            item_str = None
            cont_str = None

        # ── container mode ────────────────────────────────────────────────────
        if item_str is not None:
            from ..world.objects import Container as ContClass
            container = _find_container(cont_str, char, room)
            if container is None:
                return f"&wYou don't see any container called '&W{cont_str}&w'.&N"
            if not isinstance(container, ContClass):
                return f"&w{container.name}&w is not a container.&N"
            if not container.is_open:
                return f"&wThe &N{container.name}&w is closed.&N"
            item = _find_in_container(item_str, container)
            if item is None:
                return f"&wYou don't see '&W{item_str}&w' in &N{container.name}&w.&N"
            container.contents.remove(item)
            char.inventory.append(item)
            return f"&wYou take &N{item.name}&w from &N{container.name}&w.&N"

        # ── room pickup ───────────────────────────────────────────────────────
        item = find_target(" ".join(args), room, self.locations, self.characters)
        if item is None:
            return f"&wYou don't see any '&W{' '.join(args)}&w' here.&N"
        if not getattr(item, "take", False):
            return "&wYou can't pick that up.&N"
        room.objects.remove(item)
        char.inventory.append(item)
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

    def _cmd_put(self, args):
        """
        put <item> in <container>  — explicit
        put <item> <container>     — implicit: last word is container
        """
        if not args: return "&wPut what?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"
        room = self.current_room

        if len(args) < 2:
            return "&wUsage: &Wput <item> <container>&N"

        if "in" in args:
            sep      = args.index("in")
            item_str = " ".join(args[:sep])
            cont_str = " ".join(args[sep+1:])
        else:
            item_str = " ".join(args[:-1])
            cont_str = args[-1]

        item = _find_in_inventory(item_str, char)
        if item is None:
            return f"&wYou're not carrying '&W{item_str}&w'.&N"

        container = _find_container(cont_str, char, room)
        if container is None:
            return f"&wYou don't see any container called '&W{cont_str}&w'.&N"

        from ..world.objects import Container
        if not isinstance(container, Container):
            return f"&w{container.name}&w is not a container.&N"
        if container is item:
            return "&wYou can't put something inside itself.&N"
        if not container.is_open:
            return f"&wThe &N{container.name}&w is closed.&N"
        if not container.can_fit(item):
            return (f"&w{container.name}&w is too full — "
                    f"only &W{int(container.available_capacity)}&w lbs remaining.&N")

        char.inventory.remove(item)
        container.contents.append(item)
        return f"&wYou put &N{item.name}&w into &N{container.name}&w.&N"

    # ── open / close ──────────────────────────────────────────────────────────

    def _cmd_open(self, args):
        if not args: return "&wOpen what?&N"
        char = self.characters.get(self.player)
        room = self.current_room

        from ..world.objects import Container
        target_str = " ".join(args)
        container  = _find_container(target_str, char, room)

        if container is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        if not isinstance(container, Container):
            return f"&w{container.name}&w is not something you can open.&N"
        if container.is_open:
            return f"&w{container.name}&w is already open.&N"

        container.is_open = True
        return f"&wYou open &N{container.name}&w.&N"

    def _cmd_close(self, args):
        if not args: return "&wClose what?&N"
        char = self.characters.get(self.player)
        room = self.current_room

        from ..world.objects import Container
        target_str = " ".join(args)
        container  = _find_container(target_str, char, room)

        if container is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        if not isinstance(container, Container):
            return f"&w{container.name}&w is not something you can close.&N"
        if not container.is_open:
            return f"&w{container.name}&w is already closed.&N"

        container.is_open = False
        return f"&wYou close &N{container.name}&w.&N"

    # ── examine ───────────────────────────────────────────────────────────────

    def _cmd_examine(self, args):
        """
        examine <target>

        Searches: room mobs/chars/objects, then player inventory.
        Containers show description + capacity info + contents list.
        """
        if not args: return "&wExamine what?&N"

        char       = self.characters.get(self.player)
        room       = self.current_room
        target_str = " ".join(args)

        instance = find_target(target_str, room, self.locations, self.characters) if room else None

        if instance is None and char:
            instance = _find_in_inventory(target_str, char)

        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"

        return self._describe(instance, detailed=True)

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

        slot  = actual_slot(wear_on)
        two_h = is_blocking_secondary(item)
        msgs  = []
        char.inventory.remove(item)

        if two_h:
            for s in ("secondary_hand", "primary_hand"):
                if s in char.equipment:
                    old = char.equipment.pop(s)
                    char.inventory.append(old)
                    msgs.append(f"&wYou must free your secondary hand — &N{old.name}&w goes to inventory.&N")
            char.equipment["primary_hand"] = item
            msgs.append(f"&wYou wield &N{item.name}&w with both hands.&N")

        elif slot == "secondary_hand":
            primary = char.equipment.get("primary_hand")
            if primary and is_blocking_secondary(primary):
                char.inventory.append(item)
                return (f"&wYour primary hand is occupied with the two-handed "
                        f"&N{primary.name}&w.&N")
            if "secondary_hand" in char.equipment:
                old = char.equipment.pop("secondary_hand")
                char.inventory.append(old)
                msgs.append(f"&wYou remove &N{old.name}&w.&N")
            char.equipment["secondary_hand"] = item
            verb = "block with" if wear_on == "shield" else "hold in your off hand"
            msgs.append(f"&wYou {verb} &N{item.name}&w.&N")

        elif slot in DUAL_SLOTS:
            current = char.equipment.get(slot, [])
            if not isinstance(current, list): current = [current]
            if len(current) >= 2:
                bumped = current.pop(0)
                char.inventory.append(bumped)
                msgs.append(f"&wYou remove &N{bumped.name}&w to make room.&N")
            current.append(item)
            char.equipment[slot] = current
            msgs.append(f"&wYou wear &N{item.name}&w on your {SLOTS.get(slot,slot).lower()}.&N")

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

    # ── inventory / equipment ─────────────────────────────────────────────────

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
        primary  = char.equipment.get("primary_hand")
        sec_blocked = primary and is_blocking_secondary(primary)
        lines    = ["&+WYou are wearing:&N"]
        anything = False
        for slot, label in SLOTS.items():
            equipped = char.equipment.get(slot)
            if slot == "secondary_hand" and sec_blocked and not equipped:
                lines.append(f"  &w{label:<16}&N &x(both hands in use)&N")
                anything = True
                continue
            if not equipped: continue
            anything = True
            if slot in DUAL_SLOTS:
                for it in (equipped if isinstance(equipped, list) else [equipped]):
                    lines.append(f"  &w{label:<16}&N {it.name}")
            else:
                lines.append(f"  &w{label:<16}&N {equipped.name}")
        if not anything: return "&wYou are wearing nothing.&N"
        return "\n".join(lines)

    # ── look ─────────────────────────────────────────────────────────────────

    _ALL_DIRS = frozenset({
        "north","south","east","west","up","down",
        "northeast","northwest","southeast","southwest",
        "n","s","e","w","u","d","ne","nw","se","sw",
    })

    def _cmd_look(self, args):
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        # bare look — render the room
        if not args:
            return room.render(self.locations, self.characters)

        # look <direction>
        token = args[0].lower()
        if token in self._ALL_DIRS:
            direction = _expand_direction(token)
            dest, blocked, msg = room.peek(direction, self.rooms)
            if msg: return msg
            return dest.render(self.locations, self.characters)

        # look in <container>  — show contents
        if token == "in" and len(args) >= 2:
            char       = self.characters.get(self.player)
            target_str = " ".join(args[1:])
            container  = _find_container(target_str, char, room)
            if container is None:
                return f"&wYou don't see any '&W{target_str}&w' here.&N"
            from ..world.objects import Container
            if not isinstance(container, Container):
                return f"&w{container.name}&w is not a container.&N"
            return _look_in_container(container)

        # look <target>  — show description of the thing
        target_str = " ".join(args)
        instance   = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            # also check inventory
            char = self.characters.get(self.player)
            if char:
                instance = _find_in_inventory(target_str, char)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance, detailed=False)

    # ── describe ──────────────────────────────────────────────────────────────

    def _describe(self, instance, detailed=False) -> str:
        from ..world.objects import Container, Object
        from ..world.mob import Mob
        from ..core.character import Character

        if isinstance(instance, Container):
            if detailed:
                return _examine_container(instance)
            # look <container> — just the description
            desc = getattr(instance, "description", "")
            return desc if desc else f"You see nothing special about {target_name(instance)}."

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


# ── Container helpers ─────────────────────────────────────────────────────────

def _look_in_container(c) -> str:
    """
    'look in sack' — show what is inside the container.

    Output:
        You look in a tattered silken sack, it contains:
          <item name>
          <item name>
        OR
        A tattered silken sack is closed.
    """
    if not c.is_open:
        return f"&N{c.name}&w is closed.&N"
    if not c.contents:
        return f"&wYou look in &N{c.name}&w, it is empty.&N"
    lines = [f"&wYou look in &N{c.name}&w, it contains:&N"]
    for item in c.contents:
        lines.append(f"  {item.name}")
    return "\n".join(lines)


def _examine_container(c) -> str:
    """
    'examine sack' — description, capacity remaining, then the look-in view.
    """
    lines = []

    if c.description:
        lines.append(c.description)

    avail = int(c.available_capacity)
    lines.append(f"&wIt can hold about &W{avail}&w more lbs.&N")

    lines.append(_look_in_container(c))

    return "\n".join(lines)


# ── Search helpers ────────────────────────────────────────────────────────────

def _find_container(target_str: str, char, room) -> object | None:
    """
    Find a container by keyword.  Searches:
      1. Room objects
      2. Player inventory
    """
    _, keyword = parse_target(target_str)

    if room is not None:
        for obj in room.objects:
            if _item_matches(obj, keyword):
                return obj

    if char is not None:
        for item in char.inventory:
            if _item_matches(item, keyword):
                return item

    return None


def _find_in_container(target_str: str, container) -> object | None:
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in container.contents:
        if _item_matches(item, keyword):
            matches += 1
            if matches == idx: return item
    return None


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
            for item in (equipped if isinstance(equipped, list) else [equipped]):
                if _item_matches(item, keyword): return item, slot
        else:
            if _item_matches(equipped, keyword): return equipped, slot
    return None, None


def _item_matches(item, keyword: str) -> bool:
    if hasattr(item, "key_words"):
        if keyword in (k.lower() for k in item.key_words): return True
    return keyword in item.name.lower()
