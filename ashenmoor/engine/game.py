"""
ashenmoor.engine.game
─────────────────────
Command resolution, combat state management, and persistence hooks.

Persistence strategy
────────────────────
  Semi-permanent state is written to SQLite after every action that
  changes it (inventory, equipment, xp, location).  Current HP is held
  in memory and only written on a clean quit.

  Call GameState.init_persistence(path) once after loading all zones
  to open the database, restore any saved player state, and override
  the starting location from main.py with the last saved one.

  The save helpers are:
      _save_player()           — full save, skips hp (called after item/xp changes)
      _save_player(hp=True)    — full save including hp (called on quit)
      _save_location()         — location-only update (called after movement)
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
    "offhand":    "offhand",    "oh":  "offhand",
    "attributes": "attributes", "att": "attributes",
    "wimpy":      "wimpy",
    "remove": "remove", "rem": "remove", "unequip": "remove",
    "inventory": "inventory", "inv": "inventory", "i": "inventory",
    "equipment": "equipment", "eq":  "equipment",
    "powers":    "powers", "spells":    "powers",
    "skills":    "powers", "abilities": "powers",
    "who":   "who",
    "goto":  "goto",
    "scan":  "scan",
    "scan":  "scan",
    "score": "score", "stats": "score", "stat": "score", "sc": "score",
    "stand": "stand", "wake": "stand",
    "sit":   "sit",
    "rest":  "rest",
    "kneel": "kneel",
    "sleep": "sleep", "recline": "sleep", "lie": "sleep",
    "kill":     "kill",     "k":   "kill",
    "flee":     "flee",     "fl":  "flee",
    "consider": "consider", "con": "consider",
    "rest": "rest",
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
        # combat
        self.fighting:         dict = {}
        self._power_cooldowns: dict = {}
        # persistence
        self._db = None   # sqlite3.Connection, set by init_persistence()
        import time as _t2
        self._session_start: float = _t2.time()

    # ── Loading ───────────────────────────────────────────────────────────────

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
        self.object_templates.update(zone.object_templates)
        self.mob_templates.update(zone.mob_templates)

    # ── Persistence ───────────────────────────────────────────────────────────

    def init_persistence(self, db_path: str = "ashenmoor.db") -> None:
        """
        Open the database, initialize the schema, and restore saved player
        state (if any).  Call this after all zones are loaded.

        If the player has a saved record:
          • Their level, XP, stats, HP, inventory, and equipment are restored.
          • Their last saved location replaces the default from main.py.

        If no saved record exists the character starts fresh with the
        defaults from main.py, and a new row will be written on first save.
        """
        from .persist import open_db, load_character

        self._db = open_db(db_path)
        char     = self.characters.get(self.player)
        if char is None:
            return

        saved_location = load_character(self._db, self.player, char)

        if saved_location is not None and saved_location in self.rooms:
            self.locations[self.player] = saved_location
            print(f"[db] Restored {self.player} from {db_path} "
                  f"(room {saved_location})")
        else:
            # New character — write their initial state to the DB.
            self._save_player()
            print(f"[db] New character {self.player} saved to {db_path}")

    def _save_player(self, include_hp: bool = False) -> None:
        """
        Write the current player's state to the database.

        include_hp=False  skips hp (called after inventory / XP changes).
        include_hp=True   writes hp too (called on clean quit).
        """
        if self._db is None:
            return
        from .persist import save_character
        char     = self.characters.get(self.player)
        location = self.locations.get(self.player, 0)
        if char is None:
            return
        try:
            save_character(self._db, char, location, include_hp=include_hp)
        except Exception as exc:
            import warnings
            warnings.warn(f"DB save failed: {exc}")

    def _save_location(self) -> None:
        """Fast location-only update (called after every successful move)."""
        if self._db is None:
            return
        location = self.locations.get(self.player, 0)
        try:
            with self._db:
                self._db.execute(
                    "UPDATE characters SET location = ?, updated_at = ? "
                    "WHERE name = ?",
                    (location, time.time(), self.player),
                )
        except Exception:
            pass

    @property
    def current_room(self):
        room_id = self.locations.get(self.player)
        return self.rooms.get(room_id) if room_id is not None else None

    # ── Main command handler ──────────────────────────────────────────────────

    def handle(self, raw: str):
        tokens = raw.strip().lower().split()
        if not tokens: return None
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

        # ── Quit: save HP then exit ───────────────────────────────────────
        if verb == "quit":
            self._save_player(include_hp=True)
            return "quit"

        if verb == "kill":     return self._cmd_kill(args)
        if verb == "flee":     return self._cmd_flee()
        if verb == "consider": return self._cmd_consider(args)
        if verb == "rest":     return self._cmd_rest(args)

        # ── Movement: blocked in combat; save location on success ─────────
        if verb in DIRECTIONS or verb == "go":
            if self.player in self.fighting:
                return "&wYou cannot move while in combat — use &Wflee&w to escape!&N"
            direction = args[0] if (verb == "go" and args) else verb
            result = go(self.player, self.locations, self.rooms, direction)
            if isinstance(result, str):
                return result
            self._save_location()
            parts = [self._cmd_look([])]
            aggro = self._check_aggro()
            if aggro:
                parts.append(aggro)
            return "\n".join(parts)

        # ── Standard commands ─────────────────────────────────────────────
        if   verb == "look":      return self._cmd_look(args)
        elif verb == "examine":   return self._cmd_examine(args)
        elif verb == "inventory": return self._cmd_inventory()
        elif verb == "equipment": return self._cmd_equipment()
        elif verb == "powers":    return self._cmd_powers()
        elif verb == "who":       return self._who()
        elif verb == "scan":   return self._cmd_scan()
        elif verb == "scan":   return self._cmd_scan()
        elif verb == "goto":   return self._cmd_goto(args)
        elif verb == "score":  return self._cmd_score()
        elif verb == "stand":  return self._cmd_position("standing")
        elif verb == "sit":    return self._cmd_position("sitting")
        elif verb == "rest":   return self._cmd_position("resting")
        elif verb == "kneel":  return self._cmd_position("kneeling")
        elif verb == "sleep":  return self._cmd_position("reclined")

        # ── Inventory-changing commands: save after execution ─────────────
        elif verb == "get":
            result = self._cmd_get(args)
            self._save_player()
            return result

        elif verb == "drop":
            result = self._cmd_drop(args)
            self._save_player()
            return result

        elif verb == "put":
            result = self._cmd_put(args)
            self._save_player()
            return result

        elif verb == "open":
            result = self._cmd_open(args)
            self._save_player()
            return result

        elif verb == "close":
            result = self._cmd_close(args)
            self._save_player()
            return result

        # ── Info commands (no save needed) ──────────────────────────────
        elif verb == "attributes": return self._cmd_attributes(args)
        elif verb == "wimpy":      return self._cmd_wimpy(args)

        # ── Equipment-changing commands: save after execution ─────────────
        elif verb == "offhand":
            result = self._cmd_offhand(args)
            self._save_player()
            return result

        elif verb == "wear":
            result = self._cmd_wear(args)
            self._save_player()
            return result

        elif verb == "remove":
            result = self._cmd_remove(args)
            self._save_player()
            return result


        return "&NPardon?"

    # ── Auto-combat tick ──────────────────────────────────────────────────────

    def combat_tick(self) -> str | None:
        """
        Called every TICK_INTERVAL seconds by the ticker.
        Runs one auto-attack round, checks death, saves XP on mob kill.
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
        # Check Action Surge — doubles attacks for this tick
        dnd_state   = getattr(player, "dnd", {}) or {}
        extra_atks  = 0
        if dnd_state.get("action_surge_active"):
            from ..dnd.classes.warrior import attack_count
            extra_atks = attack_count(player.level)
            dnd_state["action_surge_active"] = False
            msgs.append("&+W[ACTION SURGE]&N")
        msgs.extend(combat_round(player, target, extra_attacks=extra_atks))

        if target.hp <= 0:
            self.fighting.pop(self.player, None)
            room.mobs.remove(target)
            from ..dnd.xp import mob_xp_award, level_for_xp, apply_level_up
            exp = mob_xp_award(target.level, player.level)
            player.xp = getattr(player, "xp", 0) + exp
            _, pct = level_for_xp(player.xp)
            msgs.append(f"&+W{target.name}&w crumples and dies!&N")
            msgs.append(
                f"&wYou gain &W{exp:,}&w xp  "
                f"(&W{player.xp:,}&w total | &W{pct}&w% into level)&N"
            )
            lvlup_msgs = apply_level_up(player)
            msgs.extend(lvlup_msgs)
            self._save_player()

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

        Two systems:
          Charge-based (charges_key in power dict) — warrior abilities, rest-restored.
          Cooldown-based (cooldown in power dict)  — mage/druid spells, time-restored.
        """
        name = power.get("name", "power")
        char = self.characters.get(self.player)

        # ── Charge-based ability (Second Wind, Action Surge, etc.) ────────
        charges_key = power.get("charges_key")
        if charges_key:
            dnd     = getattr(char, "dnd", {}) if char else {}
            charges = dnd.get(charges_key, 0)
            if charges <= 0:
                rest_type = power.get("rest_type", "short")
                return (f"&w{name}&w has no charges remaining. "
                        f"Take a &W{rest_type} rest&w to restore it.&N")
            dnd[charges_key] = charges - 1
            return self._execute_charge_power(power, char, dnd)

        # ── Cooldown-based ability (existing system) ──────────────────────
        now      = time.monotonic()
        ready_at = self._power_cooldowns.get(name, 0)
        if now < ready_at:
            return "&wYou're not ready to perform another action!&N"

        cooldown = power.get("cooldown", 8)
        self._power_cooldowns[name] = now + cooldown

        n        = char.name if char else "Someone"
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=n)

        parts: list[str] = []
        if user_msg: parts.append(user_msg)
        if room_msg: parts.append(f"&w(others see)&N {room_msg}")

        if self.player in self.fighting and char:
            target = self.fighting.get(self.player)
            room   = self.current_room
            if target and target.hp > 0:
                ensure_hp(char)
                ensure_hp(target)
                effect_msg = self._apply_power_effect(power, char, target)
                if effect_msg:
                    parts.append(effect_msg)
                if target.hp <= 0:
                    self.fighting.pop(self.player, None)
                    if room and target in room.mobs:
                        room.mobs.remove(target)
                    from ..dnd.xp import mob_xp_award, level_for_xp, apply_level_up
                    exp = mob_xp_award(target.level, char.level)
                    char.xp = getattr(char, "xp", 0) + exp
                    _, pct = level_for_xp(char.xp)
                    parts.append(f"&+W{target.name}&w crumples and dies!&N")
                    parts.append(
                        f"&wYou gain &W{exp:,}&w xp  "
                        f"(&W{char.xp:,}&w total | &W{pct}&w% into level)&N"
                    )
                    lvlup_msgs = apply_level_up(char)
                    parts.extend(lvlup_msgs)
                    self._save_player()
                else:
                    parts.append(f"{hp_status(char)}   {hp_status(target)}")

        return "\n".join(p for p in parts if p)

    def _execute_charge_power(self, power: dict, char, dnd: dict) -> str:
        """Handle a rest-charged warrior ability."""
        import random as _random

        name     = power.get("name", "power")
        effect   = power.get("effect")
        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=getattr(char, "name", "?"))

        parts: list[str] = []
        if user_msg: parts.append(user_msg)

        # ── Second Wind ───────────────────────────────────────────────────
        if effect == "second_wind":
            hit_die = dnd.get("hit_die", 10)
            from ..dnd.abilities import modifier
            con_mod = modifier(char.computed_stat("con"))
            amount  = _random.randint(1, hit_die) + char.level + con_mod
            amount  = max(1, amount)
            char.hp = min(char.max_hp, char.hp + amount)
            parts.append(f"&+GYou recover &W{amount}&+G HP "
                         f"(1d{hit_die} + level {char.level} + CON {con_mod:+}).&N")
            parts.append(f"&wHP: &W{char.hp}&w/&W{char.max_hp}&N")

        # ── Action Surge ──────────────────────────────────────────────────
        elif effect == "action_surge":
            dnd["action_surge_active"] = True
            parts.append("&+WYour next combat round will have double attacks!&N")

        # ── Indomitable (placeholder) ─────────────────────────────────────
        elif effect == "indomitable":
            parts.append("&+YYour indomitable will steels you. "
                         "(Saving throw rerolls are not yet implemented.)&N")

        # ── In-combat HP display ──────────────────────────────────────────
        if self.player in self.fighting:
            target = self.fighting.get(self.player)
            if target:
                parts.append(f"{hp_status(char)}   {hp_status(target)}")

        return "\n".join(p for p in parts if p)

    def _apply_power_effect(self, power, player, target) -> str | None:
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

    _SCAN_DIRS = [
        ("n", "north"), ("e", "east"),  ("s", "south"),
        ("w", "west"),  ("u", "up"),    ("d", "down"),
    ]

    def _cmd_scan(self) -> str:
        """
        Look in every direction from the current room.

        For each direction that has an exit, print:
            You look <direction>
            <full room description>

        Directions with no exit are silently skipped.
        Blocked doors (closed/locked) show the exit but note it is blocked.
        """
        room = self.current_room
        if room is None:
            return "&RYou are nowhere.&N"

        sections: list[str] = []

        for short, full in self._SCAN_DIRS:
            dest, blocked, msg = room.peek(short, self.rooms)
            if dest is None:
                continue   # no exit in this direction — skip silently

            header = f"&wYou look &W{full}&w:&N"

            if blocked:
                sections.append(f"{header}\n&x(the way is blocked)&N")
            else:
                room_view = dest.render(self.locations, self.characters)
                sections.append(f"{header}\n{room_view}")

        if not sections:
            return "&wYou see no exits from here.&N"

        return "\n\n".join(sections)

    def _cmd_scan(self) -> str:
        """
        Peek into every adjacent room and display its full description.

        Directions are checked in order: N E S W U D.
        Directions with no exit are skipped silently.
        """
        room = self.current_room
        if room is None:
            return "&RYou are nowhere.&N"

        DIR_LABEL = [
            ("n", "north"), ("e", "east"),  ("s", "south"),
            ("w", "west"),  ("u", "up"),    ("d", "down"),
        ]

        sections: list[str] = []

        for d, label in DIR_LABEL:
            dest_vnum = room.exit_room_id(d)
            if dest_vnum is None or dest_vnum not in self.rooms:
                continue

            dest = self.rooms[dest_vnum]
            room_view = dest.render(self.locations, self.characters)

            sections.append(
                f"&+WYou look {label}&N\n"
                f"{room_view}"
            )

        if not sections:
            return "&wYou see no exits from here.&N"

        return ("\n&w" + "─" * 40 + "&N\n").join(sections)

    def _cmd_goto(self, args) -> str:
        """goto <vnum> — teleport to any room. Dev command, no access check yet."""
        if not args:
            return "&wUsage: &Wgoto <vnum>&N"
        try:
            vnum = int(args[0])
        except ValueError:
            return f"&w'{args[0]}' is not a valid vnum.&N"
        if vnum not in self.rooms:
            return f"&wNo room with vnum &W{vnum}&w exists.&N"
        self.locations[self.player] = vnum
        self._save_location()
        parts = [self._cmd_look([])]
        aggro = self._check_aggro()
        if aggro:
            parts.append(aggro)
        return "\n".join(parts)

    # ── score / position ─────────────────────────────────────────────────────

    def _cmd_score(self) -> str:
        """Classic MUD score sheet."""
        import time as _t
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        from ..dnd.xp import level_for_xp, XP_TABLE, MAX_LEVEL

        xp       = getattr(char, "xp", 0)
        level, xp_pct = level_for_xp(xp)
        # Keep char.level in sync if it drifted (edge case on load)
        if level != char.level and level <= MAX_LEVEL:
            char.level = level
        hp      = getattr(char, "hp",        char.max_hp)
        mhp     = getattr(char, "max_hp",    1)
        moves   = getattr(char, "moves",     100)
        mmoves  = getattr(char, "max_moves", 100)

        def _coin_line(label: str, c: dict) -> str:
            g   = c.get("gold",   0)
            s   = c.get("silver", 0)
            cu  = c.get("copper", 0)
            return (f"&w{label}&N"
                    f"&W{g:>6}&w gold  "
                    f"&W{s:>6}&w silver  "
                    f"&W{cu:>6}&w copper&N")

        coins      = getattr(char, "coins",      {"gold":0,"silver":0,"copper":0})
        bank_coins = getattr(char, "bank_coins", {"gold":0,"silver":0,"copper":0})

        session_secs = int(_t.time() - self._session_start)
        total_secs   = getattr(char, "play_time_seconds", 0) + session_secs
        days         = total_secs // 86400
        hours        = (total_secs % 86400) // 3600
        mins         = (total_secs % 3600) // 60

        title    = getattr(char, "title",    "")
        position = getattr(char, "position", "standing").capitalize() + "."
        detect   = "  ".join(getattr(char, "detect_flags",  []))
        protect  = "  ".join(getattr(char, "protect_flags", []))
        enchant  = "  ".join(getattr(char, "enchant_flags", []))

        effects = getattr(char, "active_effects", [])
        positive = [e for e in effects if e.get("type", "positive") == "positive"]
        negative = [e for e in effects if e.get("type") == "negative"]

        lines = [
            f"&+WScore information for &N{char.name}\n",
            f"&wLevel:&N {level:<5} &wRace:&N {char.race:<14} &wClass:&N {char.cclass}",
            (f"&wHit points:&N &W{hp}&w(&W{mhp}&w)  "
             f"&wMoves:&N &W{moves}&w(&W{mmoves}&w)"),
            f"&wExperience Progress:&N &W{xp_pct}&w %  "
            f"&x({xp:,} / {XP_TABLE.get(level+1, xp):,} xp)&N",
            _coin_line("Coins carried:   ", coins),
            _coin_line("Coins in bank:   ", bank_coins),
            f"&wPlaying time:&N {days} days / {hours} hours / {mins} minutes",
            f"&wTitle:&N {title}",
            f"&wStatus:&N  {position}",
            f"&wDetecting:&N       {detect}",
            f"&wProtected from:&N  {protect}",
            f"&wEnchantments:&N    {enchant}",
        ]

        if positive or negative:
            lines.append("")
            lines.append("&wActive Effects:&N")
            lines.append("&w---------------&N")
            for e in positive:
                lines.append(f"  &c{e['name']}&N")
            for e in negative:
                lines.append(f"  &+R{e['name']}&N")

        return "\n".join(lines)

    def _cmd_position(self, new_pos: str) -> str:
        """
        Set the character's position.

        Positions:
          standing — full movement and combat
          sitting  — no movement; can fight
          resting  — no movement; cannot initiate combat
          kneeling — no movement; can fight (prayer/respect pose)
          reclined — no movement; cannot fight; best recovery

        Moving or being attacked returns the character to standing.
        """
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        old_pos = getattr(char, "position", "standing")
        if old_pos == new_pos:
            return f"&wYou are already {new_pos}.&N"

        char.position = new_pos

        msgs = {
            "standing": "&wYou stand up.&N",
            "sitting":  "&wYou sit down.&N",
            "resting":  "&wYou begin to rest.&N",
            "kneeling": "&wYou kneel.&N",
            "reclined": "&wYou lie down.&N",
        }
        return msgs.get(new_pos, f"&wYou are now {new_pos}.&N")

    def mob_aggro_tick(self) -> str | None:
        """
        D&D 5e Active Perception check on each tick.

        The mob actively looks around (Search action equivalent).
        It rolls Wisdom (Perception) against the player's Passive Stealth.

        Formula
        ───────
          Mob active perception  = d20 + WIS modifier [+ proficiency]
          Player Passive Stealth = 10 + DEX modifier
          Detected if mob_roll >= player_passive_stealth

        This fires every 4 seconds regardless of how the player entered.
        The sneak mechanic (future) raises the player's Passive Stealth
        by adding a proficiency bonus, making them harder to find each tick.
        Without sneak there is no proficiency bonus — average DEX characters
        have Passive Stealth 10, which an alert mob beats more often than not.
        """
        import random
        if self.player in self.fighting:
            return None
        room = self.current_room
        if room is None:
            return None
        char = self.characters.get(self.player)
        if char is None:
            return None

        from ..world.mob import Mob
        from ..dnd.abilities import modifier

        dex_mod = modifier(char.computed_stat("dex"))
        # Passive Stealth = 10 + DEX modifier (no proficiency until sneak built)
        player_passive_stealth = 10 + dex_mod

        for mob in getattr(room, "mobs", []):
            if not isinstance(mob, Mob): continue
            if not mob.is_alive() or not mob.killable: continue
            if not mob.is_hostile_to(self.player): continue

            # Mob's active Wisdom (Perception) roll
            wis = mob.stats[4] if len(mob.stats) > 4 else 75
            wis_mod = (wis - 75) // 5
            if mob.perception_prof:
                prof = (max(1, mob.level) - 1) // 4 + 2
                wis_mod += prof
            mob_perception = random.randint(1, 20) + wis_mod

            if mob_perception < player_passive_stealth:
                continue   # mob didn't spot the player this tick

            # Detected
            self.fighting[self.player] = mob
            if mob.aggressive:
                return (f"&+R{mob.name}&w spots you and attacks!&N\n"
                        f"&x(Auto-attack fires every 4 seconds.)&N")
            return (f"&+R{mob.name}&w sees you and attacks!&N\n"
                    f"&x(Auto-attack fires every 4 seconds.)&N")
        return None

    def _check_aggro(self) -> str | None:
        """
        D&D 5e awareness check on room entry.

        The player rolls Dexterity (Stealth) against each hostile mob's
        Passive Perception.  If the player beats or ties the PP the mob
        doesn't notice them this moment.  If the roll fails the mob attacks.

        Formula
        ───────
          Player stealth roll  = d20 + DEX modifier
          Mob Passive Perception = 10 + WIS modifier [+ proficiency]
          Detected if stealth_roll < mob.passive_perception()

        Memory mobs (player previously fled) get Advantage on their PP:
        they are actively watching, so we take the higher of two d20 rolls.

        This check fires once on room entry and can be suppressed by the
        sneak mechanic (future).  mob_aggro_tick() is the fallback that
        fires every 4 seconds with an active Perception roll — much harder
        to avoid.
        """
        import random
        if self.player in self.fighting:
            return None
        room = self.current_room
        if room is None:
            return None
        char = self.characters.get(self.player)
        if char is None:
            return None

        from ..world.mob import Mob
        from ..dnd.abilities import modifier

        dex_mod = modifier(char.computed_stat("dex"))

        for mob in getattr(room, "mobs", []):
            if not isinstance(mob, Mob): continue
            if not mob.is_alive() or not mob.killable: continue
            if not mob.is_hostile_to(self.player): continue

            # Player stealth roll: d20 + DEX modifier.
            # Memory mob gets Advantage on PP (watching for this player):
            # represented as a bonus d20 kept if higher, simulating alertness.
            stealth = random.randint(1, 20) + dex_mod
            pp = mob.passive_perception()
            if self.player in mob.memory:
                # Advantage: mob rolls perception twice, takes the better
                pp = max(pp, pp + random.randint(0, 5))  # alert bonus

            if stealth >= pp:
                continue   # player slips by unnoticed

            # Detected — initiate combat
            self.fighting[self.player] = mob
            if mob.aggressive:
                return (f"&+R{mob.name}&w notices you and attacks!&N\n"
                        f"&x(Auto-attack fires every 4 seconds.)&N")
            return (f"&+R{mob.name}&w recognises you and attacks!&N\n"
                    f"&x(Auto-attack fires every 4 seconds.)&N")
        return None

    def _cmd_kill(self, args) -> str:
        if not args: return "&wKill what?&N"
        if self.player in self.fighting:
            return "&wYou are already in combat!&N"

        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"

        from ..world.mob import Mob

        target = find_target(" ".join(args), room, self.locations, self.characters)
        if target is None:
            return f"&wYou don't see '&W{' '.join(args)}&w' here.&N"
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

        import random
        exit_choice = random.choice(open_exits)
        # Mob remembers this player — will auto-attack on re-entry
        angry_mob = self.fighting.get(self.player)
        if angry_mob is not None and hasattr(angry_mob, "remember"):
            angry_mob.remember(self.player)

        self.fighting.pop(self.player, None)
        self.locations[self.player] = exit_choice["roomId"]
        self._save_location()
        dest = self.rooms[exit_choice["roomId"]]
        return (f"&wYou flee in a panic to the {exit_choice['direction']}!&N\n"
                f"{dest.render(self.locations, self.characters)}")

    def _cmd_rest(self, args) -> str:
        """Short or long rest — restores HP, Hit Dice, and ability charges."""
        if self.player in self.fighting:
            return "&wYou can't rest while in combat!&N"

        if not args:
            return (
                "&wRest how?&N\n"
                "  &Wrest short&N \u2014 spend Hit Dice, restore short-rest abilities\n"
                "  &Wrest long&N  \u2014 fully recover HP and all abilities"
            )

        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        rest_type = args[0].lower()
        from ..dnd.rest import short_rest, long_rest

        if rest_type in ("short", "s"):
            result = short_rest(char)
        elif rest_type in ("long", "l"):
            result = long_rest(char)
            self._save_player(include_hp=True)   # long rest fully restores HP → save it
        else:
            return "&wType &Wrest short&w or &Wrest long&w.&N"

        return result

    def _cmd_consider(self, args) -> str:
        if not args: return "&wConsider whom?&N"
        char = self.characters.get(self.player)
        room = self.current_room
        if room is None: return "&RYou are nowhere.&N"
        from ..world.mob import Mob
        target = find_target(" ".join(args), room, self.locations, self.characters)
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
        instance   = find_target(target_str, room, self.locations, self.characters) if room else None
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
        """
        Equip one item from inventory.  Slots never bump — they refuse.

        Full-slot responses follow classic DIKU phrasing:
          ring/neck/wrist/earring  "You can wear nothing more on your fingers."
          single body slots        "You can wear nothing more on your body."
          weapons                  "You may wield no more weapons."
          shield                   "You are already wearing a shield."
          two-hander               "You must free your hands first."
        """
        wear_on = getattr(item, "wear_on", None)
        if wear_on is None:
            return f"&wYou can't wear or hold &N{item.name}&w.&N"

        from ..world.equipment import DUAL_SLOTS, SLOTS, is_blocking_secondary, actual_slot

        slot  = actual_slot(wear_on)
        two_h = is_blocking_secondary(item)

        # ── Two-handed weapon ─────────────────────────────────────────────────
        if two_h:
            pri = char.equipment.get("primary_hand")
            sec = char.equipment.get("secondary_hand")
            if pri and sec:
                return ("&wYou must free both hands before wielding "
                        f"&N{item.name}&w.&N")
            if pri:
                return (f"&wYou must remove &N{pri.name}&w "
                        f"before wielding a two-handed weapon.&N")
            if sec:
                return (f"&wYou must remove &N{sec.name}&w from your off hand "
                        f"before wielding a two-handed weapon.&N")
            char.inventory.remove(item)
            char.equipment["primary_hand"] = item
            return f"&wYou wield &N{item.name}&w with both hands.&N"

        # ── Shield / off-hand held item ───────────────────────────────────────
        if slot == "secondary_hand":
            pri = char.equipment.get("primary_hand")
            if pri and is_blocking_secondary(pri):
                return (f"&wYour primary hand is occupied with the two-handed "
                        f"&N{pri.name}&w.&N")
            sec = char.equipment.get("secondary_hand")
            if sec:
                if getattr(sec, "is_shield", False):
                    return "&wYou are already wearing a shield.&N"
                return "&wYour off hand is already occupied.&N"
            char.inventory.remove(item)
            char.equipment["secondary_hand"] = item
            verb = "block with" if wear_on in ("shield", "secondary_hand") else "hold in your off hand"
            return f"&wYou {verb} &N{item.name}&w.&N"

        # ── One-handed weapon (primary hand; auto-routes to off-hand) ─────────
        if slot == "primary_hand":
            pri = char.equipment.get("primary_hand")
            if pri and is_blocking_secondary(pri):
                return "&wYou may wield no more weapons.&N"
            if pri:
                # Primary occupied by one-hander → try off-hand
                sec = char.equipment.get("secondary_hand")
                if sec:
                    return "&wYou may wield no more weapons.&N"
                char.inventory.remove(item)
                char.equipment["secondary_hand"] = item
                return f"&wYou wield &N{item.name}&w in your off hand.&N"
            char.inventory.remove(item)
            char.equipment["primary_hand"] = item
            return f"&wYou wield &N{item.name}&w.&N"

        # ── Dual slots (ring / neck / wrist / earring — up to 2 each) ─────────
        if slot in DUAL_SLOTS:
            current = char.equipment.get(slot, [])
            if not isinstance(current, list):
                current = [current]
            if len(current) >= 2:
                return _slot_full_msg(slot)
            char.inventory.remove(item)
            current.append(item)
            char.equipment[slot] = current
            return f"&wYou wear &N{item.name}&w on your {SLOTS.get(slot, slot).lower()}.&N"

        # ── All other single slots ────────────────────────────────────────────
        if slot in char.equipment:
            return _slot_full_msg(slot)
        char.inventory.remove(item)
        char.equipment[slot] = item
        return f"&wYou wear &N{item.name}&w.&N"

    # ── attributes / wimpy ────────────────────────────────────────────────────

    def _cmd_attributes(self, args) -> str:
        """
        Display the classic MUD character attribute sheet (command: att).

        Stat values shown are EFFECTIVE stats (base × racial multiplier).
        An Ogre with displayed STR 100 (×1.5) shows STR: 150 here.

        Hitroll  = DEX modifier + equipment hitroll bonuses
        Damroll  = STR modifier + equipment damroll bonuses

        Saving throws: PAR=CON  ROD=DEX  PET=STR  BRE=DEX  SPE=INT
          Plus save_mods from any equipped items.

        Load carried
          Weight capacity = effective_STR × 2 lbs
          Item capacity   = effective_DEX ÷ 5  (min 5)
          Worst of the two determines the overall message.
        """
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        from ..dnd.abilities import char_modifier
        from ..dnd.armor     import get_ac

        # Effective (post-racial) stats — what shows on this page
        str_eff = char.computed_stat("str")
        dex_eff = char.computed_stat("dex")
        con_eff = char.computed_stat("con")
        int_eff = char.computed_stat("int")
        wis_eff = char.computed_stat("wis")
        cha_eff = char.computed_stat("cha")

        # Modifiers from effective stats
        str_mod = char_modifier(char, "str")
        dex_mod = char_modifier(char, "dex")
        con_mod = char_modifier(char, "con")
        int_mod = char_modifier(char, "int")

        # Equipment hitroll / damroll / save bonuses
        equip_hit  = 0
        equip_dam  = 0
        equip_save = {}
        for item in char.equipment.values():
            if item is None:
                continue
            equip_hit += getattr(item, "hitroll", 0)
            equip_dam += getattr(item, "damroll", 0)
            for k, v in getattr(item, "save_mods", {}).items():
                equip_save[k] = equip_save.get(k, 0) + v

        # Hitroll = actual melee attack modifier (what goes into the d20 roll):
        #   STR modifier + proficiency bonus + equipment hitroll bonuses
        # Damroll = damage bonus: STR modifier + equipment damroll bonuses
        from ..dnd.abilities import proficiency_bonus
        prof    = proficiency_bonus(char.level)
        hitroll = str_mod + prof + equip_hit
        damroll = str_mod + equip_dam

        ac = get_ac(char)

        def _sv(n: int) -> str:
            return f"+{n}" if n > 0 else str(n)

        # Saving throws = stat modifier + proficiency (if proficient) + gear + effects
        from ..dnd.abilities import saving_throw

        effect_save: dict[str,int] = {}
        for eff in getattr(char, "active_effects", []):
            for k, v in eff.get("save_mods", {}).items():
                effect_save[k] = effect_save.get(k, 0) + v

        par = saving_throw(char, "par",
                           equip_bonus=equip_save.get("par", 0),
                           effect_bonus=effect_save.get("par", 0))
        rod = saving_throw(char, "rod",
                           equip_bonus=equip_save.get("rod", 0),
                           effect_bonus=effect_save.get("rod", 0))
        pet = saving_throw(char, "pet",
                           equip_bonus=equip_save.get("pet", 0),
                           effect_bonus=effect_save.get("pet", 0))
        bre = saving_throw(char, "bre",
                           equip_bonus=equip_save.get("bre", 0),
                           effect_bonus=effect_save.get("bre", 0))
        spe = saving_throw(char, "spe",
                           equip_bonus=equip_save.get("spe", 0),
                           effect_bonus=effect_save.get("spe", 0))

        race_obj  = char._races.get(char.race)
        size      = getattr(race_obj, "size", "Medium") if race_obj else "Medium"
        wimpy     = getattr(char, "wimpy", None)
        wimpy_str = f"&W{wimpy}&w hp&N" if wimpy else "not set"
        alignment = getattr(char, "alignment", "True Neutral")

        # Load carried
        inv_weight = sum(getattr(i, "weight", 0) for i in char.inventory)
        max_weight = max(1, str_eff * 2)
        inv_items  = len(char.inventory)
        max_items  = max(5, dex_eff // 5)

        wt_pct   = inv_weight / max_weight * 100
        it_pct   = inv_items  / max_items  * 100
        load_pct = max(wt_pct, it_pct)

        if load_pct <= 25:
            load_color, load_msg = "&+G", "Not a problem"
        elif load_pct <= 50:
            load_color, load_msg = "&G",  "Light"
        elif load_pct <= 75:
            load_color, load_msg = "&Y",  "Moderate"
        elif load_pct <= 90:
            load_color, load_msg = "&+Y", "Heavy"
        elif load_pct <= 100:
            load_color, load_msg = "&+R", "Staggering"
        else:
            load_color, load_msg = "&+R", "OVERLOADED!"

        load_detail = (f"&x  ({inv_weight:.1f}/{max_weight:.0f} lbs"
                       f" | {inv_items}/{max_items} items)&N")

        lines = [
            f"&+WCharacter attributes for &N{char.name}\n",
            f"&wLevel:&N {char.level:<5} &wRace:&N {char.race:<14} &wClass:&N {char.cclass}",
            f"&wSize:&N {size}",
            (f"&wSTR:&N {str_eff:>4}  "
             f"&wDEX:&N {dex_eff:>4}  "
             f"&wCON:&N {con_eff:>4}"),
            (f"&wINT:&N {int_eff:>4}  "
             f"&wWIS:&N {wis_eff:>4}  "
             f"&wCHA:&N {cha_eff:>4}"),
            f"&wArmor Class:&N {ac}  &x(0 - 100)&N",
            f"&wHitroll:&N {hitroll:+d}   &wDamroll:&N {damroll:+d}",
            f"&wAlignment:&N {alignment}",
            (f"&wSaving Throws:&N "
             f"PAR[{_sv(par)}]  "
             f"ROD[{_sv(rod)}]  "
             f"PET[{_sv(pet)}]  "
             f"BRE[{_sv(bre)}]  "
             f"SPE[{_sv(spe)}]"),
            f"   &wWimpy:&N {wimpy_str}",
            f"&wLoad carried:&N {load_color}{load_msg}&N{load_detail}",
        ]

        return "\n".join(lines)

    def _cmd_wimpy(self, args) -> str:
        """
        Set or clear the auto-flee HP threshold.

        wimpy 20    — flee when HP drops to or below 20
        wimpy off   — disable auto-flee
        wimpy       — show current setting
        """
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        if not args:
            w = getattr(char, "wimpy", None)
            if w:
                return f"&wYou will flee combat when your HP drops to &W{w}&w.&N"
            return "&wWimpy is not set. You will fight to the last breath.&N"

        val = args[0].lower()

        if val in ("off", "0", "none", "clear"):
            char.wimpy = None
            return "&wWimpy cleared. You will fight to the last breath.&N"

        try:
            hp = int(val)
        except ValueError:
            return "&wUsage: &Wwimpy <hp>&w  or  &Wwimpy off&N"

        if hp <= 0:
            char.wimpy = None
            return "&wWimpy cleared.&N"
        if hp >= char.max_hp:
            return f"&wWimpy must be less than your max HP (&W{char.max_hp}&w).&N"

        char.wimpy = hp
        return (f"&wYou will automatically flee combat "
                f"when your HP drops to &W{hp}&w.&N")

    def _cmd_offhand(self, args) -> str:
        """
        Wield a weapon explicitly in the off hand (secondary_hand slot).

        Normally 'wield' auto-routes to the off hand when primary is occupied,
        but use 'offhand' when you want to be explicit or override the auto
        behaviour — e.g. offhand dagger while primary holds a longsword.
        """
        if not args: return "&wWield what in your off hand?&N"
        char = self.characters.get(self.player)
        if not char: return "&RNo character found.&N"

        from ..world.objects   import Weapon
        from ..world.equipment import is_blocking_secondary

        item = _find_in_inventory(" ".join(args), char)
        if item is None:
            return f"&wYou're not carrying '&W{' '.join(args)}&w'.&N"
        if not isinstance(item, Weapon):
            return f"&w{item.name}&w can't be wielded in your off hand.&N"
        if getattr(item, "two_handed", False):
            return f"&w{item.name}&w requires both hands.&N"

        primary = char.equipment.get("primary_hand")
        if primary and is_blocking_secondary(primary):
            return (f"&wYour primary hand is busy with the two-handed "
                    f"&N{primary.name}&w.&N")

        msgs = []
        char.inventory.remove(item)

        if "secondary_hand" in char.equipment:
            bumped = char.equipment.pop("secondary_hand")
            char.inventory.append(bumped)
            msgs.append(f"&wYou move &N{bumped.name}&w back to your inventory.&N")

        char.equipment["secondary_hand"] = item
        msgs.append(f"&wYou wield &N{item.name}&w in your off hand.&N")

        # Dual-wield hint for D&D Warriors
        dnd = getattr(char, "dnd", {}) or {}
        if dnd.get("class") == "warrior":
            style = dnd.get("fighting_style", "")
            if style == "two_weapon":
                msgs.append("&x(Two-Weapon Fighting: off-hand damage includes your ability modifier.)&N")
            elif primary and not getattr(item, "light", False):
                msgs.append("&x(Note: for standard dual-wield both weapons should be Light, "
                            "or take the Two-Weapon Fighting style.)&N")

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
            # When looked at in a room, show brief position line.
            # 'detailed' (examine) → full character sheet.
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

    def _who(self):
        if not self.characters: return "&wNobody is here.&N"
        lines = [f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5} {'XP':>10}&N"]
        lines.append("&w" + "─"*58 + "&N")
        for char in self.characters.values():
            xp = getattr(char, "xp", 0)
            lines.append(f"{char.name:<15} {char.race:<12} {char.cclass:<10} "
                         f"{char.level:>5} {xp:>10,}")
        return "\n".join(lines)

    def character_list(self): return self._who()


# ── Slot-full refusal messages ────────────────────────────────────────────────

_SLOT_FULL: dict[str, str] = {
    "head":          "&wYou can wear nothing more on your head.&N",
    "face":          "&wYou can wear nothing more on your face.&N",
    "neck":          "&wYou can wear nothing more around your neck.&N",
    "on_body":       "&wYou can wear nothing more on your body.&N",
    "about_body":    "&wYou can wear nothing more about your body.&N",
    "back":          "&wYou can wear nothing more on your back.&N",
    "arms":          "&wYou can wear nothing more on your arms.&N",
    "hands":         "&wYou can wear nothing more on your hands.&N",
    "waist":         "&wYou can wear nothing more about your waist.&N",
    "legs":          "&wYou can wear nothing more on your legs.&N",
    "feet":          "&wYou can wear nothing more on your feet.&N",
    "wrist":         "&wYou can wear nothing more on your wrists.&N",
    "ring":          "&wYou can wear nothing more on your fingers.&N",
    "earring":       "&wYou can wear nothing more on your ears.&N",
    "light":         "&wYou are already holding a light source.&N",
    "floating":      "&wNothing more may float nearby.&N",
    "primary_hand":  "&wYou may wield no more weapons.&N",
    "secondary_hand":"&wYour off hand is already occupied.&N",
}

def _slot_full_msg(slot: str) -> str:
    return _SLOT_FULL.get(slot, "&wThat slot is already in use.&N")


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
