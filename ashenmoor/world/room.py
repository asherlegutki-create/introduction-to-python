"""
ashenmoor.world.room
─────────────────────
Room definitions and respawn mechanics.

Respawn system
──────────────
Rooms that define "mob_spawns" get managed population with respawn timers.
Rooms that define only "mobs" work exactly as before — static, no respawn.

mob_spawns format:
    "mob_spawns": [
        {
            "template":          "goblin_warrior",  # key in zone mob_templates
            "max":               3,                 # max alive at once
            "start":             1,                 # how many spawn at zone load
            "respawn_ticks":     75,                # override zone default
            "repop_with_player": False,             # override zone default
        },
    ]

Respawn behaviour:
    - When a managed mob dies, a respawn entry is queued with a countdown.
    - Each call to respawn_tick() decrements countdowns.
    - When a countdown reaches 0:
        * If current live count < max, spawn one mob and reset the timer
          (keeps ticking until max is reached).
        * Either repop_with_player is True, or no player is in the room.
    - If repop_with_player is False and a player is present, the countdown
      pauses (does not decrement) until the room is empty.
"""

from __future__ import annotations

TERRAIN = ("no ground", "water", "mountain", "plain", "stone", "forest",
           "desert", "swamp", "road", "inside")

_BLOCKED_STATES = {"closed", "locked"}


def _stack_room_objects(objects) -> list[str]:
    order  = []
    counts = {}
    descs  = {}
    for obj in objects:
        key = obj.name
        if key not in counts:
            order.append(key)
            counts[key] = 0
            descs[key]  = getattr(obj, "room_description", obj.name)
        counts[key] += 1
    lines = []
    for key in order:
        n    = counts[key]
        desc = descs[key]
        if n > 1:
            lines.append(f"&w[&W{n}&w]&N {desc}")
        else:
            lines.append(desc)
    return lines


class Room:
    def __init__(self, d: dict):
        self.number      = d["number"]
        self.name        = d["name"]
        desc = d.get("description", "")
        self.description: str = "\n".join(desc) if isinstance(desc, (tuple, list)) else desc
        self.indoors     = d.get("indoors", False)
        self.terrain     = d.get("terrain", "plain")
        self.exits       = d.get("exits",   [])
        self.objects     = d.get("objects", [])
        self.mobs        = list(d.get("mobs", []))

        # Stash raw mob_spawns config for Zone._init_respawn() to process.
        # If mob_spawns is present it overrides the static mobs list.
        self._raw_mob_spawns: list[dict] | None = d.get("mob_spawns", None)

        # ── Respawn system ────────────────────────────────────────────────────
        # _spawn_config  — resolved list of spawn entries (set by init_respawn)
        # _pending       — list of active respawn countdowns
        # _spawner       — callable(template_key) -> Mob
        self._spawn_config: list[dict] = []
        self._pending:      list[dict] = []
        self._spawner = None

    # ── Respawn initialisation (called by Zone._init_respawn) ─────────────────

    def init_respawn(self, spawn_config: list[dict], spawner) -> None:
        """
        Wire up the managed respawn system for this room.

        Replaces any statically placed mobs and populates the room up to
        each entry's 'start' count.

        spawn_config entries must have:
            template, max, start, respawn_ticks, repop_with_player
        """
        self._spawn_config = spawn_config
        self._spawner      = spawner

        # Replace static mobs with managed population
        self.mobs = []
        for entry in spawn_config:
            count = min(entry["start"], entry["max"])
            for _ in range(count):
                mob = spawner(entry["template"])
                self.mobs.append(mob)

    # ── Live count helper ─────────────────────────────────────────────────────

    def _live_count(self, template_key: str) -> int:
        """Count how many live mobs of this template are currently in the room."""
        return sum(
            1 for m in self.mobs
            if getattr(m, "_template_key", None) == template_key
        )

    # ── Notify respawn system of a mob death ──────────────────────────────────

    def notify_mob_death(self, mob) -> None:
        """
        Call when a managed mob dies to queue a respawn.
        No-op if this room uses static mobs.
        """
        if not self._spawn_config:
            return

        template_key = getattr(mob, "_template_key", None)
        if template_key is None:
            return

        entry = next(
            (e for e in self._spawn_config if e["template"] == template_key),
            None,
        )
        if entry is None:
            return

        # Only queue if we are below max (another player may have already
        # killed the same mob type and queued a respawn)
        pending_count = sum(
            1 for p in self._pending
            if p["template"] == template_key
        )
        live_count = self._live_count(template_key)

        if live_count + pending_count < entry["max"]:
            self._pending.append({
                "template":          entry["template"],
                "ticks_remaining":   entry["respawn_ticks"],
                "respawn_ticks":     entry["respawn_ticks"],
                "max":               entry["max"],
                "repop_with_player": entry["repop_with_player"],
            })

    # ── Per-tick respawn update ───────────────────────────────────────────────

    def respawn_tick(self, player_present: bool) -> None:
        """
        Called every combat tick (4 seconds) by the server tick loop.

        player_present: True if at least one player is currently in this room.

        For each pending respawn:
          - Pause timer if players are present and repop_with_player is False.
          - Decrement timer otherwise.
          - On expiry: spawn one mob if below max, then reset timer to keep
            filling until max is reached; discard entry if already at max.
        """
        if not self._spawn_config or self._spawner is None:
            return

        # Also check whether any template is below max with no pending entry
        # (handles the case where mobs were removed without going through
        # notify_mob_death, e.g. zone reloads or admin commands)
        self._fill_missing()

        still_pending = []
        for entry in self._pending:
            repop_with = entry["repop_with_player"]

            # Pause if players present and repop not allowed with players
            if not repop_with and player_present:
                still_pending.append(entry)
                continue

            entry["ticks_remaining"] -= 1

            if entry["ticks_remaining"] > 0:
                still_pending.append(entry)
                continue

            # Timer expired — spawn one if below max
            live = self._live_count(entry["template"])
            if live < entry["max"]:
                mob = self._spawner(entry["template"])
                self.mobs.append(mob)
                live += 1

            # If still below max after spawning, reset timer for next one
            if live < entry["max"]:
                entry["ticks_remaining"] = entry["respawn_ticks"]
                still_pending.append(entry)
            # else: at max — discard this pending entry

        self._pending = still_pending

    def _fill_missing(self) -> None:
        """
        Queue respawn entries for any template that is below max and has
        no existing pending entry. Catches gaps caused by anything other
        than normal combat death (e.g. first-time population after a
        zone reload where start < max).
        """
        for entry in self._spawn_config:
            key          = entry["template"]
            live         = self._live_count(key)
            pending      = sum(1 for p in self._pending if p["template"] == key)
            deficit      = entry["max"] - live - pending
            for _ in range(deficit):
                self._pending.append({
                    "template":          key,
                    "ticks_remaining":   entry["respawn_ticks"],
                    "respawn_ticks":     entry["respawn_ticks"],
                    "max":               entry["max"],
                    "repop_with_player": entry["repop_with_player"],
                })

    # ── Exit helpers ──────────────────────────────────────────────────────────

    def get_exit(self, direction):
        for ex in self.exits:
            if ex["direction"].lower() == direction.lower():
                return ex
        return None

    def exit_room_id(self, direction):
        ex = self.get_exit(direction)
        return ex["roomId"] if ex else None

    def exit_is_blocked(self, direction):
        ex = self.get_exit(direction)
        if ex is None:
            return False
        door = ex.get("door")
        return bool(door and door.get("state", "open") in _BLOCKED_STATES)

    def door_keyword(self, direction):
        ex = self.get_exit(direction)
        if ex is None:
            return None
        door = ex.get("door")
        return door.get("keyword") if door else None

    def door_is_pickable(self, direction) -> bool:
        ex = self.get_exit(direction)
        if ex is None:
            return False
        door = ex.get("door")
        if not door:
            return False
        if door.get("key_id") is None:
            return False
        return bool(door.get("pickable", True))

    def door_key_id(self, direction) -> str | None:
        ex = self.get_exit(direction)
        if ex is None:
            return None
        door = ex.get("door")
        return door.get("key_id") if door else None

    def peek(self, direction, rooms):
        ex = self.get_exit(direction)
        if ex is None:
            return None, False, "&wYou cannot see anything in that direction.&N"
        door = ex.get("door")
        if door and door.get("state", "open") in _BLOCKED_STATES:
            keyword = door.get("keyword", "door")
            return None, True, f"&wThe &W{keyword}&w is closed.&N"
        dest = rooms.get(ex["roomId"])
        if dest is None:
            return None, False, "&wYou cannot see anything in that direction.&N"
        return dest, False, None

    # ── Render helpers ────────────────────────────────────────────────────────

    def _exits_str(self):
        if not self.exits:
            return "&gExits:&N &RNone!&N"
        parts = ["&gExits:&N"]
        for i, ex in enumerate(self.exits):
            sep   = " &C-&N" if i > 0 else ""
            dname = ex["direction"].title()
            door  = ex.get("door")
            if door and door.get("state", "open") in _BLOCKED_STATES:
                parts.append(f"{sep} &r{dname}&N")
            else:
                parts.append(f"{sep} &c{dname}&N")
        return "".join(parts)

    def _objects_str(self):
        if not self.objects:
            return ""
        return "\n".join(_stack_room_objects(list(reversed(self.objects))))

    def _mobs_str(self, fighting: dict | None = None,
                  viewer: str | None = None) -> str:
        """
        Build the mob list for a room look.

        viewer  — the name of the player doing the looking, used to
                  show "fighting &RYOU!!&N" instead of their own name.

        Position verbs:
            standing  → stands
            sitting   → sits
            resting   → rests
            kneeling  → kneels
            reclined  → lies
        """
        if not self.mobs:
            return ""

        _POS_VERB = {
            "standing": "stands",
            "sitting":  "sits",
            "resting":  "rests",
            "kneeling": "kneels",
            "reclined": "lies",
        }

        lines = []
        for mob in reversed(self.mobs):
            pos_verb = _POS_VERB.get(getattr(mob, "position", "standing"), "stands")
            name     = mob.name

            # Find which player(s) are fighting this mob.
            # Union of: fighting[pname]==mob (player is targeting mob)
            # and mob.attackers (mob knows who it is fighting).
            fighters = []
            if fighting:
                for pname, target in fighting.items():
                    if target is mob:
                        fighters.append(pname)
            for pname in getattr(mob, "attackers", set()):
                if pname not in fighters:
                    fighters.append(pname)

            if fighters:
                # Determine how each fighter name is shown to the viewer
                shown = []
                for pname in fighters:
                    if pname == viewer:
                        shown.append("&RYOU!!&N")
                    else:
                        shown.append(f"&w{pname}&N")
                fight_str = "&w, &N".join(shown)
                lines.append(f"{name} {pos_verb} here fighting {fight_str}")
            else:
                lines.append(f"{name} {pos_verb} here.")

        return "\n".join(lines)

    def get_characters(self, locations, characters):
        return [
            characters[name]
            for name, room_id in locations.items()
            if room_id == self.number and name in characters
        ]

    def _characters_str(self, locations, characters,
                          fighting: dict | None = None,
                          viewer: str | None = None) -> str:
        _POS_STR = {
            "standing": "stands here",
            "sitting":  "is sitting here",
            "resting":  "is sitting here",   # others see resting as sitting
            "kneeling": "is kneeling here",
            "reclined": "is lying here",
        }
        chars = self.get_characters(locations, characters)
        if not chars:
            return ""
        lines = []
        for c in chars:
            if c.name == viewer:
                continue
            pos     = getattr(c, "position", "standing")
            pos_str = _POS_STR.get(pos, "is here")
            target  = fighting.get(c.name) if fighting else None
            if target is not None:
                target_name = getattr(target, "name", "something")
                lines.append(f"&w{c.name}&N {pos_str} fighting &R{target_name}&N.")
            else:
                lines.append(f"&w{c.name}&N {pos_str}.")
        return "\n".join(lines)

    def render(self, locations=None, characters=None, fighting=None, viewer=None):
        parts = [f"&+W{self.name}&N", f"  {self.description}"]
        parts.append(self._exits_str())
        mob_str = self._mobs_str(fighting=fighting, viewer=viewer)
        if mob_str:
            parts.append(mob_str)
        obj_str = self._objects_str()
        if obj_str:
            parts.append(obj_str)
        if locations is not None and characters is not None:
            char_str = self._characters_str(locations, characters, fighting=fighting, viewer=viewer)
            if char_str:
                parts.append(char_str)
        return "\n".join(parts)

    def __repr__(self): return self.render()
    def __str__(self):  return self.render()
