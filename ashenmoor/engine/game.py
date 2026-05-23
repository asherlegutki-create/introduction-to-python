"""
ashenmoor.engine.game
─────────────────────
Command resolution and combat state management.

Combat is driven by the ticker (ashenmoor.engine.ticker):
  • auto_crepl() calls state.combat_tick() every 4 seconds automatically.
  • handle() processes player commands — it does NOT run combat rounds.

Power system
────────────
  Powers fire IMMEDIATELY when typed, subject to their individual cooldown.
  If the power is still recharging the player sees:
      "You're not ready to perform another action!"
  If it is ready it fires right away — auto-attacks still happen every tick.
  This means a player can get off a power between any two auto-attack rounds.
"""

from __future__ import annotations
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room     import Room
    from ..core.character import Character

from .targeting import find_target, target_name, parse_target
from .combat    import (
    combat_round, one_attack, ensure_hp,
    compute_max_hp, hp_status, condition_str, calc_damage,
)

DIRECTIONS = frozenset({"north","south","east","west","up","down"})
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


# ── Command resolution ────────────────────────────────────────────────────────

_COMMAND_MAP: dict[str, str] = {
    "quit": "quit",  "exit": "quit",  "q": "quit",
    "camp": "quit",  "leave": "quit",
    "north": "north", "south": "south", "east": "east",
    "west":  "west",  "up":    "up",    "down": "down",  "go": "go",
    "n": "north", "s": "south", "e": "east",
    "w": "west",  "u": "up",    "d": "down",
    "look":    "look",    "l":  "look",
    "examine": "examine", "ex": "examine", "x": "examine",
    "get": "get", "take": "get",
    "drop": "drop",
    "put": "put", "put_on": "wear",
    "open": "open", "close": "close",
    "wear":   "wear", "wield": "wear", "hold": "wear",
    "remove": "remove", "rem": "remove", "unequip": "remove",
    "inventory": "inventory", "inv": "inventory", "i": "inventory",
    "equipment": "equipment", "eq":  "equipment",
    "powers":    "powers", "spells":    "powers",
    "skills":    "powers", "abilities": "powers",
    "who":   "who",
    "score": "score", "stats": "score", "stat": "score",
    "kill":     "kill",     "k":   "kill", "attack": "kill",
    "flee":     "flee",     "fl":  "flee",
    "consider": "consider", "con": "consider",
}


def _resolve_verb(verb: str) -> str | list | None:
    if verb in _COMMAND_MAP:
        return _COMMAND_MAP[verb]
    matched: dict[str, str] = {}
    for word, canonical in _COMMAND_MAP.items():
        if "_" not in word and word.startswith(verb):
            matched.setdefault(canonical, word)
    if len(matched) == 1:
        return next(iter(matched))
    if len(matched) > 1:
        return sorted(matched.keys())
    return None


# ── GameState ─────────────────────────────────────────────────────────────────

class GameState:

    def __init__(self):
        self.rooms:            dict = {}
        self.characters:       dict = {}
        self.locations:        dict = {}
        self.player:           str  = ""
        self.object_templates: dict = {}
        self.mob_templates:    dict = {}
        # combat state
        self.fighting:         dict = {}  # player_name → target mob
        self._power_cooldowns: dict = {}  # power_name → timestamp when ready

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

    # ── Main command handler ──────────────────────────────────────────────────

    def handle(self, raw: str):
        tokens = raw.strip().lower().split()
        if not tokens: return None
        verb, *args = tokens

        # Powers fire immediately — cooldown check is inside _execute_power.
        result = self._try_power(verb, args)
        if result is not None:
            return result

        resolved = _resolve_verb(verb)
        if resolved is None:
            return "&NPardon?"
        if isinstance(resolved, list):
            opts = "&w, &W".join(resolved)
            return f"&wAmbiguous command — did you mean: &W{opts}&w?&N"
        verb = resolved

        if verb == "quit":     return "quit"
        if verb == "kill":     return self._cmd_kill(args)
        if verb == "flee":     return self._cmd_flee()
        if verb == "consider": return self._cmd_consider(args)

        if verb in DIRECTIONS or verb == "go":
            if self.player in self.fighting:
                return "&wYou cannot move while in combat — use &Wflee&w to escape!&N"
            if verb == "go":
                return go(self.player, self.locations, self.rooms,
                          args[0] if args else "")
            return go(self.player, self.locations, self.rooms, verb)

        if   verb == "look":      return self._cmd_look(args)
        elif verb == "examine":   return self._cmd_examine(args)
        elif verb == "get":       return self._cmd_get(args)
        elif verb == "drop":      return self._cmd_drop(args)
        elif verb == "put":       return self._cmd_put(args)
        elif verb == "open":      return self._cmd_open(args)
        elif verb == "close":     return self._cmd_close(args)
        elif verb == "wear":      return self._cmd_wear(args)
        elif verb == "remove":    return self._cmd_remove(args)
        elif verb == "inventory": return self._cmd_inventory()
        elif verb == "equipment": return self._cmd_equipment()
        elif verb == "powers":    return self._cmd_powers()
        elif verb == "who":       return self._who()
        elif verb == "score":
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"
        return "&NPardon?"

    # ── Auto-combat tick ──────────────────────────────────────────────────────

    def combat_tick(self) -> str | None:
        """
        Called by the ticker every 4 seconds while fighting.
        Runs one auto-attack round then checks for death.
        Powers fire immediately when typed — they are NOT handled here.
        """
        target = self.fighting.get(self.player)
        if not target: return None

        player = self.characters.get(self.player)
        if not player: return None

        room = self.current_room
        if room is None or target not in room.mobs:
            self.fighting.pop(self.player, None)
            return "&wYour opponent is no longer here.&N"

        ensure_hp(player)
        ensure_hp(target)

        msgs: list[str] = []

        # Auto-attack round
        msgs.extend(combat_round(player, target))

        # Death checks
        if target.hp <= 0:
            self.fighting.pop(self.player, None)
            room.mobs.remove(target)
            exp = target.level * 50
            msgs.append(f"&+W{target.name}&w crumples and dies!&N")
            msgs.append(f"&wYou gain &W{exp}&w experience points.&N")

        elif player.hp <= 0:
            self.fighting.pop(self.player, None)
            player.hp = max(1, player.max_hp // 4)
            msgs.append("&+RYOU HAVE BEEN SLAIN!&N")
            msgs.append("&wYou somehow cling to life...&N")

        else:
            msgs.append(f"{hp_status(player)}   {hp_status(target)}")

        return "\n".join(msgs)

    # ── Powers ────────────────────────────────────────────────────────────────

    def _try_power(self, verb, args):
        """Check if verb matches a power keyword and fire it immediately."""
        char = self.characters.get(self.player)
        if not char or not char.powers: return None
        for power in char.powers:
            kws = power.get("keywords", ())
            if isinstance(kws, str): kws = (kws,)
            if verb in (k.lower() for k in kws):
                return self._execute_power(power)
        return None

    def _execute_power(self, power) -> str:
        """
        Fire a power immediately.

        If the power is still on cooldown, return the 'not ready' message.
        Otherwise fire it, apply any combat effect, and set the cooldown.
        """
        name     = power.get("name", "power")
        now      = time.monotonic()
        ready_at = self._power_cooldowns.get(name, 0)

        # Cooldown check — same message whether in or out of combat
        if now < ready_at:
            return "&wYou're not ready to perform another action!&N"

        # Set cooldown
        cooldown = power.get("cooldown", 8)
        self._power_cooldowns[name] = now + cooldown

        char     = self.characters.get(self.player)
        n        = char.name if char else "Someone"
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=n)

        parts: list[str] = []
        if user_msg: parts.append(user_msg)
        if room_msg: parts.append(f"&w(others see)&N {room_msg}")

        # Apply combat effect immediately if we are fighting
        if self.player in self.fighting and char:
            target = self.fighting.get(self.player)
            room   = self.current_room
            if target and target.hp > 0:
                ensure_hp(char)
                ensure_hp(target)
                effect_msg = self._apply_power_effect(power, char, target)
                if effect_msg:
                    parts.append(effect_msg)

                # Check if power killed the target
                if target.hp <= 0:
                    self.fighting.pop(self.player, None)
                    if room and target in room.mobs:
                        room.mobs.remove(target)
                    exp = target.level * 50
                    parts.append(f"&+W{target.name}&w crumples and dies!&N")
                    parts.append(f"&wYou gain &W{exp}&w experience points.&N")
                else:
                    parts.append(f"{hp_status(char)}   {hp_status(target)}")

        return "\n".join(p for p in parts if p)

    def _apply_power_effect(self, power, player, target) -> str | None:
        """Apply the combat effect of a power (damage bonus or healing)."""
        effect = power.get("effect")

        if effect == "heal":
            pct    = power.get("heal_pct", 0.20)
            amount = int(player.max_hp * pct)
            player.hp = min(player.max_hp, player.hp + amount)
            return f"&+GYou recover &W{amount}&+G hit points.&N"

        if effect == "damage":
            mult   = power.get("damage_mult", 1.5)
            dmg    = max(1, int(calc_damage(player) * mult))
            target.hp = max(0, target.hp - dmg)
            return (f"&+WYour power strikes &N{target.name}&+W for "
                    f"&W{dmg}&+W bonus damage!&N")

        return None

    def _cmd_powers(self):
        char = self.characters.get(self.player)
        if not char:        return "&RNo character found.&N"
        if not char.powers: return "&wYou have no powers.&N"

        now   = time.monotonic()
        lines = [
            f"&+W{'Power':<20} {'Keywords':<22} Status&N",
            "&w" + "─"*56 + "&N",
        ]
        for p in char.powers:
            name     = p.get("name", "?")
            keywords = ", ".join(p.get("keywords", ()))
            cooldown = p.get("cooldown", 8)
            ready_at = self._power_cooldowns.get(name, 0)
            if now >= ready_at:
                status = f"&+Gready&N &x({cooldown}s cooldown)&N"
            else:
                remaining = int(ready_at - now)
                status    = f"&+R{remaining}s remaining&N"
            lines.append(f"{name:<20} &c{keywords:<22}&N {status}")
        return "\n".join(lines)

    # ── Combat commands ───────────────────────────────────────────────────────

    def _cmd_kill(self, args) -> str:
        if not args: return "&wKill what?&N"
        if self.player in self.fighting:
            return "&wYou are already in combat!&N"

        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        from ..world.mob import Mob

        target_str = " ".join(args)
        target = find_target(target_str, room, self.locations, self.characters)

        if target is None:
            return f"&wYou don't see '&W{target_str}&w' here.&N"
        if not isinstance(target, Mob):
            return f"&w{target_name(target)}&w is not something you can attack.&N"
        if not target.killable:
            return f"&w{target.name}&w is protected — you cannot attack it.&N"

        ensure_hp(char)
        ensure_hp(target)
        self.fighting[self.player] = target

        return (
            f"&wYou engage &+W{target.name}&w in combat!&N\n"
            f"&wThey appear to be &N{condition_str(target)}&w.&N\n"
            f"&x(Auto-attack fires every 4 seconds. "
            f"Type a power to use it immediately.)&N"
        )

    def _cmd_flee(self) -> str:
        import random

        if self.player not in self.fighting:
            return "&wYou aren't fighting anyone.&N"

        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        dex      = char.get_stat("dex") if char else 75
        flee_pct = 50 + max(0, (dex - 75) // 5)

        if random.randint(1, 100) > flee_pct:
            target = self.fighting.get(self.player)
            if target:
                ensure_hp(char)
                ensure_hp(target)
                _, _, hit_msg = one_attack(target, char)
                msgs = ["&wYou attempt to flee, but stumble!&N", hit_msg]
                if char.hp <= 0:
                    self.fighting.pop(self.player, None)
                    char.hp = max(1, char.max_hp // 4)
                    msgs.append("&+RYOU HAVE BEEN SLAIN trying to flee!&N")
                    msgs.append("&wYou collapse… and somehow cling to life.&N")
                return "\n".join(msgs)
            return "&wYou attempt to flee, but stumble!&N"

        open_exits = [
            ex for ex in room.exits
            if not room.exit_is_blocked(ex["direction"])
            and ex["roomId"] in self.rooms
        ]
        if not open_exits:
            return "&wThere's nowhere to run!&N"

        exit_choice = random.choice(open_exits)
        self.fighting.pop(self.player, None)
        self.locations[self.player] = exit_choice["roomId"]
        dest = self.rooms[exit_choice["roomId"]]

        return (f"&wYou flee in a panic to the {exit_choice['direction']}!&N\n"
                f"{dest.render(self.locations, self.characters)}")

    def _cmd_consider(self, args) -> str:
        if not args: return "&wConsider whom?&N"

        char   = self.characters.get(self.player)
        room   = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        from ..world.mob import Mob

        target_str = " ".join(args)
        target = find_target(target_str, room, self.locations, self.characters)

        if target is None:
            return f"&wYou don't see '&W{target_str}&w' here.&N"
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

    # ── get / drop / put ─────────────────────────────────────────────────────

    def _cmd_get(self, args):
        if not args: return "&wGet what?&N"
        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

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
        if not args: return "&wPut what?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"
        room = self.current_room
        if len(args) < 2: return "&wUsage: &Wput <item> <container>&N"

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

        if " ".join(args) == "all":
            wearable = [it for it in list(char.inventory)
                        if getattr(it, "wear_on", None) is not None]
            if not wearable: return "&wYou have nothing to wear.&N"
            for it in wearable:
                if it in char.inventory:
                    self._wear_one(char, it)
            return "&wYou wear your equipment.&N"

        item = _find_in_inventory(" ".join(args), char)
        if item is None:
            return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
        return self._wear_one(char, item)

    def _wear_one(self, char, item) -> str:
        wear_on = getattr(item, "wear_on", None)
        if wear_on is None:
            return f"&wYou can't wear or hold &N{item.name}&w.&N"

        from ..world.equipment import (
            DUAL_SLOTS, SLOTS, is_blocking_secondary, actual_slot
        )

        slot  = actual_slot(wear_on)
        two_h = is_blocking_secondary(item)
        msgs  = []
        char.inventory.remove(item)

        if two_h:
            for s in ("secondary_hand", "primary_hand"):
                if s in char.equipment:
                    bumped = char.equipment.pop(s)
                    char.inventory.append(bumped)
                    msgs.append(f"&wYou must free your hands — &N{bumped.name}&w goes to inventory.&N")
            char.equipment["primary_hand"] = item
            msgs.append(f"&wYou wield &N{item.name}&w with both hands.&N")

        elif slot == "secondary_hand":
            primary = char.equipment.get("primary_hand")
            if primary and is_blocking_secondary(primary):
                char.inventory.append(item)
                return (f"&wYour primary hand is occupied with the two-handed "
                        f"&N{primary.name}&w — &N{item.name}&w stays in inventory.&N")
            if "secondary_hand" in char.equipment:
                bumped = char.equipment.pop("secondary_hand")
                char.inventory.append(bumped)
                msgs.append(f"&wYou remove &N{bumped.name}&w.&N")
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
            msgs.append(f"&wYou wear &N{item.name}&w on your {SLOTS.get(slot, slot).lower()}.&N")

        else:
            if slot in char.equipment:
                bumped = char.equipment.pop(slot)
                char.inventory.append(bumped)
                msgs.append(f"&wYou remove &N{bumped.name}&w.&N")
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
        primary     = char.equipment.get("primary_hand")
        sec_blocked = primary and is_blocking_secondary(primary)
        lines       = ["&+WYou are wearing:&N"]
        anything    = False
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

        if not args:
            return room.render(self.locations, self.characters)

        token = args[0].lower()
        if token in self._ALL_DIRS:
            direction = _expand_direction(token)
            dest, blocked, msg = room.peek(direction, self.rooms)
            if msg: return msg
            return dest.render(self.locations, self.characters)

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

        target_str = " ".join(args)
        instance   = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
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
            if detailed: return _examine_container(instance)
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
    if not c.is_open:
        return f"&N{c.name}&w is closed.&N"
    if not c.contents:
        return f"&wYou look in &N{c.name}&w, it is empty.&N"
    lines = [f"&wYou look in &N{c.name}&w, it contains:&N"]
    for item in c.contents:
        lines.append(f"  {item.name}")
    return "\n".join(lines)

def _examine_container(c) -> str:
    lines = []
    if c.description:
        lines.append(c.description)
    lines.append(f"&wIt can hold about &W{int(c.available_capacity)}&w more lbs.&N")
    lines.append(_look_in_container(c))
    return "\n".join(lines)

# ── Search helpers ────────────────────────────────────────────────────────────

def _find_container(target_str, char, room):
    _, keyword = parse_target(target_str)
    if room is not None:
        for obj in room.objects:
            if _item_matches(obj, keyword): return obj
    if char is not None:
        for item in char.inventory:
            if _item_matches(item, keyword): return item
    return None

def _find_in_container(target_str, container):
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in container.contents:
        if _item_matches(item, keyword):
            matches += 1
            if matches == idx: return item
    return None

def _find_in_inventory(target_str, char):
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in char.inventory:
        if _item_matches(item, keyword):
            matches += 1
            if matches == idx: return item
    return None

def _find_in_equipment(target_str, char):
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
