"""
ashenmoor.engine.game
─────────────────────
GameState: world container, tick handlers, power system, and command dispatch.
All command implementations live in ashenmoor.engine.commands.*
"""

from __future__ import annotations
import contextvars as _cv
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

# ── Tick / power constants ────────────────────────────────────────────────────

_TICK_INTERVAL: float = 4.0

_SLOT_LABELS: dict[str, str] = {
    "primary_hand":   "main hand",
    "secondary_hand": "off hand",
}

def _power_cooldown_secs(power: dict) -> float:
    if "cooldown_ticks" in power:
        return float(power["cooldown_ticks"]) * _TICK_INTERVAL
    return float(power.get("cooldown", 8))

def _power_cooldown_ticks(power: dict) -> float:
    if "cooldown_ticks" in power:
        return float(power["cooldown_ticks"])
    return power.get("cooldown", 8) / _TICK_INTERVAL

def _power_key(power: dict) -> str:
    name = power.get("name", "?")
    slot = power.get("_slot")
    return f"{name}:{slot}" if slot else name

def _collect_tagged_powers(char) -> list[dict]:
    result: list[dict] = []
    for p in (char.powers or []):
        result.append(p)
    for slot, item in char.equipment.items():
        items = item if isinstance(item, list) else ([item] if item else [])
        for it in items:
            for p in (getattr(it, "powers", None) or []):
                tagged        = dict(p)
                tagged["_slot"] = slot
                result.append(tagged)
    return result

# ── Direction helpers ─────────────────────────────────────────────────────────

DIRECTIONS = frozenset({"north","south","east","west","up","down"})
_DIR_EXPAND = {"n":"north","s":"south","e":"east","w":"west","u":"up","d":"down"}

def _expand_direction(d: str) -> str:
    return _DIR_EXPAND.get(d.lower(), d.lower())

def go(character, locations, rooms, direction):
    from .commands.movement import go as _go
    return _go(character, locations, rooms, direction)

# ── Active-player context var ─────────────────────────────────────────────────

_active_player: _cv.ContextVar[str] = _cv.ContextVar("_active_player")

# ── Command map ───────────────────────────────────────────────────────────────

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
    "lock": "lock", "unlock": "unlock",
    "wear":   "wear", "wield": "wear", "hold": "wear",
    "offhand":    "offhand",    "oh":  "offhand",
    "attributes": "attributes", "att": "attributes",
    "wimpy":      "wimpy",
    "remove": "remove", "rem": "remove", "unequip": "remove",
    "inventory": "inventory", "inv": "inventory", "i": "inventory",
    "equipment": "equipment", "eq":  "equipment",
    "powers":    "powers", "spells":    "powers",
    "skills":    "powers", "abilities": "powers",
    "who":    "who",
    "scan":   "scan",
    "wiz":    "wiz",
    "time":   "time",
    "toggle": "toggle", "tog": "toggle",
    "score": "score", "stats": "score", "sc": "score",
    "stand": "stand", "st": "stand", "wake": "stand",
    "sit":   "sit",
    "rest":  "rest",
    "kneel": "kneel",
    "sleep": "sleep", "recline": "sleep", "lie": "sleep",
    "kill":     "kill",     "k":   "kill",
    "flee":     "flee",     "fl":  "flee",
    "consider": "consider", "con": "consider",
    "ask":      "ask",
    "quaff":    "quaff",    "qu": "quaff",
    "recite":   "recite",   "re": "recite",
    "say":  "say",
    "tell": "tell",
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
        self.fighting:         dict = {}
        self._power_cooldowns: dict = {}
        self._resting:         dict = {}
        self._db               = None
        self._server           = None
        self._session_start: float = time.time()
        from ..world.calendar import GameTime
        self.game_time: GameTime = GameTime(0)

    @property
    def _player(self) -> str:
        try:
            return _active_player.get()
        except LookupError:
            return self.player

    def load_world(self, rooms, characters, locations, player=""):
        self.rooms      = rooms
        self.characters = characters
        self.locations  = locations
        self.player     = player or (next(iter(characters)) if characters else "")

    def load_zone(self, zone):
        collisions = set(zone.rooms) & set(self.rooms)
        if collisions:
            import warnings
            warnings.warn(
                f"Zone '{zone.name}' overwrites room numbers: {sorted(collisions)}",
                stacklevel=2,
            )
        self.rooms.update(zone.rooms)
        if not isinstance(zone.object_templates, dict):
            raise TypeError(
                f"Zone '{zone.name}' object_templates is "
                f"{type(zone.object_templates).__name__}, expected dict."
            )
        self.object_templates.update(zone.object_templates)
        self.mob_templates.update(zone.mob_templates)

    def init_persistence(self, db_path: str = "ashenmoor.db") -> None:
        from .persist import open_db, load_character, load_world_time
        self._db = open_db(db_path)
        self.game_time.total_minutes = load_world_time(self._db)
        char = self.characters.get(self._player)
        if char is None:
            return
        saved_location = load_character(self._db, self._player, char)
        if saved_location is not None and saved_location in self.rooms:
            self.locations[self._player] = saved_location
            print(f"[db] Restored {self._player} from {db_path} (room {saved_location})")
        else:
            self._save_player()
            print(f"[db] New character {self._player} saved to {db_path}")

    def _save_player(self, include_hp: bool = False) -> None:
        if self._db is None:
            return
        from .persist import save_character
        char     = self.characters.get(self._player)
        location = self.locations.get(self._player, 0)
        if char is None:
            return
        try:
            save_character(self._db, char, location, include_hp=include_hp)
        except Exception as exc:
            import warnings
            warnings.warn(f"DB save failed: {exc}")

    def _save_location(self) -> None:
        if self._db is None:
            return
        location = self.locations.get(self._player, 0)
        try:
            with self._db:
                self._db.execute(
                    "UPDATE characters SET location = ?, updated_at = ? WHERE name = ?",
                    (location, time.time(), self._player),
                )
        except Exception:
            pass

    def _broadcast_to_room(self, msg: str, room_id: int | None = None) -> None:
        srv = getattr(self, "_server", None)
        if srv is None:
            return
        rid     = room_id if room_id is not None else self.locations.get(self._player)
        sender  = self._player
        for name, client in list(getattr(srv, "_clients", {}).items()):
            if name == sender or getattr(client, "_closed", True):
                continue
            if self.locations.get(name) == rid:
                try:
                    client._outbox.put_nowait(msg)
                except Exception:
                    pass

    @property
    def current_room(self):
        room_id = self.locations.get(self._player)
        return self.rooms.get(room_id) if room_id is not None else None

    # ── Command handler ───────────────────────────────────────────────────────

    def handle(self, raw: str, player_name: str | None = None):
        if player_name is not None:
            _tok = _active_player.set(player_name)
        else:
            _tok = None
        try:
            return self._handle_inner(raw)
        finally:
            if _tok is not None:
                _active_player.reset(_tok)

    def _handle_inner(self, raw: str):
        from .commands.movement   import cmd_move, cmd_look, cmd_scan, cmd_examine
        from .commands.combat     import cmd_kill, cmd_flee, cmd_consider, cmd_rest
        from .commands.items      import (
            cmd_inventory, cmd_equipment, cmd_get, cmd_drop, cmd_put,
            cmd_open, cmd_close, cmd_lock, cmd_unlock,
            cmd_wear, cmd_remove, cmd_offhand,
        )
        from .commands.character  import (
            cmd_score, cmd_attributes, cmd_wimpy, cmd_position,
            cmd_powers, cmd_who, cmd_toggle,
        )
        from .commands.social     import cmd_say, cmd_ask, cmd_quaff, cmd_recite, cmd_tell
        from .commands.admin      import cmd_wiz, cmd_time

        tokens = raw.strip().lower().split()
        if not tokens:
            return None
        verb, *args = tokens

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

        if verb == "quit":
            self._save_player(include_hp=True)
            return "quit"

        if verb == "kill":     return cmd_kill(self, args)
        if verb == "flee":     return cmd_flee(self)
        if verb == "consider": return cmd_consider(self, args)
        if verb == "rest":     return cmd_rest(self, args)
        if verb == "ask":      return cmd_ask(self, args)
        if verb == "say":      return cmd_say(self, args)
        if verb == "tell":     return cmd_tell(self, args)
        if verb == "quaff":    return cmd_quaff(self, args)
        if verb == "recite":   return cmd_recite(self, args)
        if verb == "wiz":      return cmd_wiz(self, args)
        if verb == "time":     return cmd_time(self)
        if verb == "toggle":   return cmd_toggle(self, args)
        if verb == "score":    return cmd_score(self)
        if verb == "attributes": return cmd_attributes(self)
        if verb == "wimpy":    return cmd_wimpy(self, args)
        if verb == "who":      return cmd_who(self)
        if verb == "scan":     return cmd_scan(self)
        if verb == "powers":   return cmd_powers(self)
        if verb == "look":     return cmd_look(self, args)
        if verb == "examine":  return cmd_examine(self, args)
        if verb == "inventory": return cmd_inventory(self)
        if verb == "equipment": return cmd_equipment(self)

        if verb == "stand":   return cmd_position(self, "standing")
        if verb == "sit":     return cmd_position(self, "sitting")
        if verb == "kneel":   return cmd_position(self, "kneeling")
        if verb == "sleep":   return cmd_position(self, "reclined")

        if verb in DIRECTIONS or verb == "go":
            direction = args[0] if (verb == "go" and args) else verb
            return cmd_move(self, _expand_direction(direction))

        if verb == "get":
            result = cmd_get(self, args); self._save_player(); return result
        if verb == "drop":
            result = cmd_drop(self, args); self._save_player(); return result
        if verb == "put":
            result = cmd_put(self, args); self._save_player(); return result
        if verb == "open":
            result = cmd_open(self, args); self._save_player(); return result
        if verb == "close":
            result = cmd_close(self, args); self._save_player(); return result
        if verb == "lock":
            result = cmd_lock(self, args); self._save_player(); return result
        if verb == "unlock":
            result = cmd_unlock(self, args); self._save_player(); return result
        if verb == "wear":
            result = cmd_wear(self, args); self._save_player(); return result
        if verb == "remove":
            result = cmd_remove(self, args); self._save_player(); return result
        if verb == "offhand":
            result = cmd_offhand(self, args); self._save_player(); return result

        return "&NPardon?"

    # ── Tick handlers ─────────────────────────────────────────────────────────

    def effect_tick(self, player_name: str | None = None) -> str | None:
        if player_name is not None:
            tok = _active_player.set(player_name)
            try:
                return self._effect_tick()
            finally:
                _active_player.reset(tok)
        return self._effect_tick()

    def combat_tick(self, player_name: str | None = None) -> tuple[str | None, str | None, str | None]:
        if player_name is not None:
            tok = _active_player.set(player_name)
            try:
                return self._combat_tick_inner()
            finally:
                _active_player.reset(tok)
        return self._combat_tick_inner()

    def _effect_tick(self) -> str | None:
        player = self.characters.get(self._player)
        if not player:
            return None
        from ..world.effects import tick_effects as _tick_fx
        self_msgs, room_msgs = _tick_fx(player)
        if room_msgs:
            self._broadcast_to_room("\n".join(room_msgs))
        return "\n".join(self_msgs) if self_msgs else None

    def _combat_tick_inner(self) -> tuple[str | None, str | None, str | None]:
        from ..dnd.xp       import mob_xp_award, level_for_xp, apply_level_up
        from ..world.corpse import Corpse
        from .commands.helpers import personalize_msg

        target = self.fighting.get(self._player)
        if not target:
            return None, None, None
        player = self.characters.get(self._player)
        if not player:
            return None, None, None
        room = self.current_room
        if room is None or target not in room.mobs:
            self.fighting.pop(self._player, None)
            return "&wYour opponent is no longer here.&N", None, None

        ensure_hp(player)
        ensure_hp(target)

        hp_status_line: str | None = None

        if not getattr(target, "primary_target", None):
            target.primary_target = self._player
        is_primary = (getattr(target, "primary_target", None) == self._player)

        dnd_state  = getattr(player, "dnd", {}) or {}
        extra_atks = 0
        surge_msg  = None
        if dnd_state.get("action_surge_active"):
            from ..dnd.classes.warrior import attack_count
            extra_atks = attack_count(player.level)
            dnd_state["action_surge_active"] = False
            surge_msg = "&+W[ACTION SURGE]&N"

        round_player, round_room = combat_round(
            player, target,
            extra_attacks=extra_atks,
            mob_retaliates=is_primary,
        )

        player_msgs: list[str] = []
        if surge_msg:
            player_msgs.append(surge_msg)
        player_msgs.extend(personalize_msg(m, player.name) for m in round_player)

        room_msgs: list[str] = []
        if surge_msg:
            room_msgs.append(surge_msg)
        room_msgs.extend(round_room)

        from ..world.effects import tick_effects as _tick_mob_fx
        mob_self, mob_room = _tick_mob_fx(target)
        player_msgs.extend(mob_room)
        room_msgs.extend(mob_room)

        if target.hp <= 0:
            self.fighting.pop(self._player, None)
            room.mobs.remove(target)
            exp        = mob_xp_award(target.level, player.level)
            player.xp  = getattr(player, "xp", 0) + exp
            _, pct     = level_for_xp(player.xp)
            kill_msg   = f"&+W{target.name}&w crumples and dies!&N"
            player_msgs.append(kill_msg)
            room_msgs.append(kill_msg)
            xp_msg = (
                f"&wYou gain &W{exp:,}&w xp  "
                f"(&W{player.xp:,}&w total | &W{pct}&w% into level)&N"
            )
            player_msgs.append(xp_msg)
            player_msgs.extend(apply_level_up(player))
            corpse = Corpse(target)
            room.objects.append(corpse)
            if corpse.contents:
                player_msgs.append(
                    "&xA corpse is left behind. Type &Wexa corpse&x to search it.&N"
                )
                room_msgs.append(f"&xThe corpse of {target.name}&x lies here.&N")
            else:
                player_msgs.append("&xA corpse is left behind.&N")
                room_msgs.append(f"&xThe corpse of {target.name}&x lies here.&N")
            self._save_player()

        elif player.hp <= 0:
            self.fighting.pop(self._player, None)
            player.hp = max(1, player.max_hp // 4)
            if getattr(target, "primary_target", None) == self._player:
                other = next(
                    (n for n, m in self.fighting.items() if m is target), None
                )
                target.primary_target = other
            player_msgs.append("&+RYOU HAVE BEEN SLAIN!&N")
            player_msgs.append("&wYou somehow cling to life...&N")
            room_msgs.append(f"&+R{player.name} has been slain!&N")

        else:
            hp_status_line = f"{hp_status(player)}   {hp_status(target)}"

        player_out = "\n".join(player_msgs) if player_msgs else None
        room_out   = "\n".join(room_msgs)   if room_msgs   else None
        return player_out, room_out, hp_status_line

    def mob_aggro_tick(self, player_name: str | None = None) -> str | None:
        if player_name is not None:
            tok = _active_player.set(player_name)
            try:
                return self._mob_aggro_tick_inner()
            finally:
                _active_player.reset(tok)
        return self._mob_aggro_tick_inner()

    def _mob_aggro_tick_inner(self) -> str | None:
        import random
        if self._player in self.fighting:
            return None
        room = self.current_room
        if room is None:
            return None
        char = self.characters.get(self._player)
        if char is None:
            return None

        from ..world.mob     import Mob
        from ..dnd.abilities import modifier

        dex_mod = modifier(char.computed_stat("dex"))
        player_passive_stealth = 10 + dex_mod

        for mob in getattr(room, "mobs", []):
            if not isinstance(mob, Mob):
                continue
            if not mob.is_alive() or not mob.killable:
                continue
            if not mob.is_hostile_to(self._player):
                continue

            wis     = mob.stats[4] if len(mob.stats) > 4 else 75
            wis_mod = (wis - 75) // 5
            if mob.perception_prof:
                wis_mod += (max(1, mob.level) - 1) // 4 + 2
            mob_perception = random.randint(1, 20) + wis_mod

            if mob_perception < player_passive_stealth:
                continue

            self.fighting[self._player] = mob
            self._resting.pop(self._player, None)
            if not getattr(mob, "primary_target", None):
                mob.primary_target = self._player

            aggro_msg = (
                f"&+R{mob.name}&w spots you and attacks!&N\n&x(Auto-attack fires every 4 seconds.)&N"
                if mob.aggressive else
                f"&+R{mob.name}&w sees you and attacks!&N\n&x(Auto-attack fires every 4 seconds.)&N"
            )
            room_aggro = (
                f"&+R{mob.name}&w spots &w{self._player}&N and attacks!&N"
                if mob.aggressive else
                f"&+R{mob.name}&w sees &w{self._player}&N and attacks!&N"
            )
            self._broadcast_to_room(room_aggro)
            first_out, first_room, first_hp = self._combat_tick_inner()
            if first_room:
                self._broadcast_to_room(first_room)
            parts = [aggro_msg]
            if first_out:
                parts.append(first_out)
            if first_hp:
                parts.append(first_hp)
            return "\n".join(parts)

        return None

    def rest_tick(self, player_name: str | None = None) -> str | None:
        name = player_name or self._player
        rest = self._resting.get(name)
        if not rest:
            return None
        if name in self.fighting:
            del self._resting[name]
            return "&wYour rest is interrupted!&N"

        rest["ticks"] += 1
        ticks = rest["ticks"]
        char  = self.characters.get(name)
        if not char:
            return None

        dnd  = getattr(char, "dnd", {}) or {}
        msgs = []

        if ticks == 4:
            for uses_key, max_key, label in [
                ("second_wind_uses",  "second_wind_max",  "Second Wind"),
                ("action_surge_uses", "action_surge_max", "Action Surge"),
            ]:
                if uses_key in dnd:
                    max_val = dnd.get(max_key, 1)
                    if dnd[uses_key] < max_val:
                        dnd[uses_key] = max_val
                        msgs.append(f"&+GYour &W{label}&+G is now available.&N")
            dnd["action_surge_active"] = False

        if ticks == 8:
            for uses_key, max_key, label in [
                ("indomitable_uses", "indomitable_max", "Indomitable"),
            ]:
                if uses_key in dnd:
                    max_val = dnd.get(max_key, 0)
                    if dnd[uses_key] < max_val:
                        dnd[uses_key] = max_val
                        msgs.append(f"&+GYour &W{label}&+G is now available.&N")

            hd_max = char.level
            hd_cur = dnd.get("hit_dice_remaining", 0)
            new_hd = min(hd_max, hd_cur + max(1, hd_max // 2))
            if new_hd > hd_cur:
                dnd["hit_dice_remaining"] = new_hd

            if char.hp < char.max_hp:
                char.hp = char.max_hp
                msgs.append(f"&+GYou feel fully rested. (&W{char.max_hp}&+G hp restored)&N")

            if getattr(char, "potion_log", []):
                char.potion_log = []
                msgs.append("&+GYou feel ready to benefit from potions again.&N")

            if player_name is not None:
                tok = _active_player.set(player_name)
                try:
                    self._save_player(include_hp=True)
                finally:
                    _active_player.reset(tok)
            else:
                self._save_player(include_hp=True)

        return "\n".join(msgs) if msgs else None

    def hp_regen_tick(self, player_name: str | None = None) -> None:
        name = player_name or self._player
        if name in self.fighting:
            return
        char = self.characters.get(name)
        if not char or char.hp >= char.max_hp:
            return
        import random
        from ..dnd.abilities import modifier
        con_mod = modifier(char.computed_stat("con"))
        die_max = max(1, min(4, 1 + con_mod))
        regen   = random.randint(1, die_max)
        char.hp = min(char.max_hp, char.hp + regen)

    # ── Power system ──────────────────────────────────────────────────────────

    def _try_power(self, verb, args):
        char = self.characters.get(self._player)
        if not char:
            return None

        all_powers = _collect_tagged_powers(char)
        matches = [
            p for p in all_powers
            if verb in (k.lower() for k in (
                (p["keywords"],) if isinstance(p.get("keywords"), str)
                else p.get("keywords", ())
            ))
        ]
        if not matches:
            return None

        now = time.monotonic()
        for power in matches:
            if now >= self._power_cooldowns.get(_power_key(power), 0):
                return self._execute_power(power)

        soonest = min(matches, key=lambda p: self._power_cooldowns.get(_power_key(p), 0))
        rem     = (self._power_cooldowns.get(_power_key(soonest), 0) - now) / _TICK_INTERVAL
        name    = soonest.get("name", "power")
        return f"&w{name}&w is not ready yet ({rem:.1f} ticks remaining).&N"

    def _execute_power(self, power) -> str:
        name = power.get("name", "power")
        char = self.characters.get(self._player)

        charges_key = power.get("charges_key")
        if charges_key:
            dnd     = getattr(char, "dnd", {}) if char else {}
            charges = dnd.get(charges_key, 0)
            if charges <= 0:
                return f"&w{name}&w has no charges remaining. &wRest to restore it.&N"
            dnd[charges_key] = charges - 1
            return self._execute_charge_power(power, char, dnd)

        now      = time.monotonic()
        pkey     = _power_key(power)
        ready_at = self._power_cooldowns.get(pkey, 0)
        if now < ready_at:
            remaining = (ready_at - now) / _TICK_INTERVAL
            return f"&w{name}&w is not ready yet ({remaining:.1f} ticks remaining).&N"

        cooldown = _power_cooldown_secs(power)
        self._power_cooldowns[pkey] = now + cooldown

        n        = char.name if char else "Someone"
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=n)
        parts: list[str] = []
        if user_msg:
            parts.append(user_msg)
        if room_msg:
            self._broadcast_to_room(room_msg)

        if self._player in self.fighting and char:
            target = self.fighting.get(self._player)
            room   = self.current_room
            if target and target.hp > 0:
                ensure_hp(char)
                ensure_hp(target)
                effect_msg = self._apply_power_effect(power, char, target)
                if effect_msg:
                    parts.append(effect_msg)
                if target.hp <= 0:
                    self.fighting.pop(self._player, None)
                    if room and target in room.mobs:
                        room.mobs.remove(target)
                    from ..dnd.xp       import mob_xp_award, level_for_xp, apply_level_up
                    from ..world.corpse import Corpse
                    exp        = mob_xp_award(target.level, char.level)
                    char.xp    = getattr(char, "xp", 0) + exp
                    _, pct     = level_for_xp(char.xp)
                    parts.append(f"&+W{target.name}&w crumples and dies!&N")
                    parts.append(
                        f"&wYou gain &W{exp:,}&w xp  "
                        f"(&W{char.xp:,}&w total | &W{pct}&w% into level)&N"
                    )
                    parts.extend(apply_level_up(char))
                    corpse = Corpse(target)
                    if room:
                        room.objects.append(corpse)
                    if corpse.contents:
                        parts.append(
                            "&xA corpse is left behind. Type &Wexa corpse&x to search it.&N"
                        )
                    else:
                        parts.append("&xA corpse is left behind.&N")
                    self._save_player()
                else:
                    parts.append(f"{hp_status(char)}   {hp_status(target)}")

        return "\n".join(p for p in parts if p)

    def _execute_charge_power(self, power: dict, char, dnd: dict) -> str:
        import random as _random
        effect   = power.get("effect")
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=getattr(char, "name", "?"))
        parts: list[str] = []
        if user_msg:
            parts.append(user_msg)

        if effect == "second_wind":
            hit_die = dnd.get("hit_die", 10)
            from ..dnd.abilities import modifier
            con_mod = modifier(char.computed_stat("con"))
            amount  = max(1, _random.randint(1, hit_die) + char.level + con_mod)
            char.hp = min(char.max_hp, char.hp + amount)
            parts.append(
                f"&+GYou recover &W{amount}&+G HP "
                f"(1d{hit_die} + level {char.level} + CON {con_mod:+}).&N"
            )
            parts.append(f"&wHP: &W{char.hp}&w/&W{char.max_hp}&N")
        elif effect == "action_surge":
            dnd["action_surge_active"] = True
            parts.append("&+WYour next combat round will have double attacks!&N")
        elif effect == "indomitable":
            parts.append("&+YYour indomitable will steels you.&N")

        if self._player in self.fighting:
            target = self.fighting.get(self._player)
            if target:
                parts.append(f"{hp_status(char)}   {hp_status(target)}")

        return "\n".join(p for p in parts if p)

    def _apply_power_effect(self, power, player, target) -> str | None:
        effect = power.get("effect")
        if effect == "heal":
            amount = int(player.max_hp * power.get("heal_pct", 0.20))
            player.hp = min(player.max_hp, player.hp + amount)
            return f"&+GYou recover &W{amount}&+G hit points.&N"
        if effect == "damage":
            dmg = max(1, int(calc_damage(player) * power.get("damage_mult", 1.5)))
            target.hp = max(0, target.hp - dmg)
            return f"&+WYour power strikes &N{target.name}&+W for &W{dmg}&+W bonus damage!&N"
        if effect == "apply_poison":
            from ..world.effects import POISON, apply_effect
            import copy
            poison = copy.deepcopy(POISON)
            if "duration"  in power: poison["duration"]  = power["duration"]
            if "dot_dice"  in power: poison["dot_dice"]  = power["dot_dice"]
            apply_effect(target, poison)
            return f"&cThe poison takes hold of &N{target.name}&c!&N"
        if effect == "windsong_burst":
            import ashenmoor.world.procs as _procs_mod
            weapon = (player.equipment.get("primary_hand")
                      if hasattr(player, "equipment") else None)
            old_force          = _procs_mod._windsong_force
            _procs_mod._windsong_force = True
            try:
                raw = _procs_mod.windsong(player, target, weapon=weapon)
            finally:
                _procs_mod._windsong_force = old_force
            player_out, room_out = [], []
            for m in (raw or []):
                if isinstance(m, tuple) and len(m) == 2:
                    player_out.append(m[0])
                    room_out.append(m[1])
                else:
                    s = str(m)
                    player_out.append(s)
                    room_out.append(s)
            if room_out:
                self._broadcast_to_room("\n".join(room_out))
            return "\n".join(player_out) if player_out else None
        return None

    # ── Convenience aliases ───────────────────────────────────────────────────

    def character_list(self):
        from .commands.character import cmd_who
        return cmd_who(self)
