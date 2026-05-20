"""
ashenmoor.world.room
────────────────────
Room class and terrain constants.

Exit format (backward compatible — door key is optional):

    {"direction": "east", "roomId": 2}                         # open passage

    {"direction": "east", "roomId": 2,
     "door": {
         "keyword":  "iron gate",   # word used with open/close/lock/unlock/pick
         "state":    "open",        # "open" | "closed" | "locked"
         "pickable": True,          # can a thief pick this lock?  default True
         "key_id":   "iron_key",    # object template key whose instance unlocks
     }}                             # this door.  None = no key required (bolt only)

Door field reference
────────────────────
keyword   str           Target word for open/close/lock/unlock/pick commands.
state     str           "open" | "closed" | "locked"
pickable  bool          True (default) — the lock can be picked.
                        False — only the correct key or a spell opens it.
key_id    str | None    Template key of the Item that acts as a key.
                        e.g. "iron_key" matches a zone object template.
                        None means the door can be bolted but has no keyed lock
                        (open/close work; lock/unlock/pick do not apply).

Door states
───────────
"open"    Passage is clear — look and move both work normally.
"closed"  Blocks sight and movement.  Use 'open <keyword>' to open.
"locked"  Blocks sight and movement.  Requires key or pick to unlock first.
"""

TERRAIN = ("no ground", "water", "mountain", "plain", "stone", "forest",
           "desert", "swamp", "road", "inside")

_BLOCKED_STATES = {"closed", "locked"}


class Room:
    def __init__(self, d):
        self.number      = d["number"]
        self.name        = d["name"]
        desc = d.get("description", "")
        self.description:      str   = "\n".join(desc) if isinstance(desc, (tuple, list)) else desc
        self.indoors     = d.get("indoors", False)
        self.terrain     = d.get("terrain", "plain")
        self.exits       = d.get("exits",   [])
        self.objects     = d.get("objects", [])
        self.mobs        = d.get("mobs",    [])

    # -- Exit helpers --

    def get_exit(self, direction):
        """Return the full exit dict for direction, or None."""
        for ex in self.exits:
            if ex["direction"].lower() == direction.lower():
                return ex
        return None

    def exit_room_id(self, direction):
        ex = self.get_exit(direction)
        return ex["roomId"] if ex else None

    def exit_is_blocked(self, direction):
        """True if a closed/locked door blocks this exit."""
        ex = self.get_exit(direction)
        if ex is None:
            return False
        door = ex.get("door")
        return bool(door and door.get("state", "open") in _BLOCKED_STATES)

    def door_keyword(self, direction):
        """Return the door keyword for direction, or None if no door."""
        ex = self.get_exit(direction)
        if ex is None:
            return None
        door = ex.get("door")
        return door.get("keyword") if door else None

    def door_is_pickable(self, direction) -> bool:
        """
        True if the door in *direction* can be picked by a thief.

        Returns False when there is no door, no lock, or pickable is
        explicitly set to False.  Defaults to True when a door exists
        and pickable is not specified (most doors can be picked).
        """
        ex = self.get_exit(direction)
        if ex is None:
            return False
        door = ex.get("door")
        if not door:
            return False
        # No key_id means no keyed lock — nothing to pick
        if door.get("key_id") is None:
            return False
        return bool(door.get("pickable", True))

    def door_key_id(self, direction) -> str | None:
        """
        Return the object template key whose instance unlocks this door,
        or None if the door has no keyed lock.

        The engine's unlock/key command should check whether the player
        is carrying an Item whose template key matches this value.
        """
        ex = self.get_exit(direction)
        if ex is None:
            return None
        door = ex.get("door")
        return door.get("key_id") if door else None

    def peek(self, direction, rooms):
        """
        Look in direction from this room.

        Returns (dest_room, blocked, message).
          dest_room  -- Room if visible, else None
          blocked    -- True when a door blocks the view
          message    -- ready-to-cprint string when dest_room is None,
                        else None (caller renders dest_room)
        """
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

    # -- Exits display --

    def _exits_str(self):
        if not self.exits:
            return "&gExits:&N &RNone!&N"
        parts = ["&gExits:&N"]
        for i, ex in enumerate(self.exits):
            sep   = " &C-&N" if i > 0 else ""
            dname = ex["direction"].title()
            door  = ex.get("door")
            if door and door.get("state", "open") in _BLOCKED_STATES:
                parts.append(f"{sep} &r{dname}&N")   # dark red = blocked
            else:
                parts.append(f"{sep} &c{dname}&N")   # cyan = open
        return "".join(parts)

    # -- Room content helpers --

    def _objects_str(self):
        if not self.objects: return ""
        return "\n".join(obj.room_description for obj in self.objects)

    def _mobs_str(self):
        if not self.mobs: return ""
        return "\n".join(
            mob.room_description if mob.room_description
            else f"{mob.name.capitalize()} is here."
            for mob in self.mobs
        )

    def get_characters(self, locations, characters):
        return [characters[name]
                for name, room_id in locations.items()
                if room_id == self.number and name in characters]

    def _characters_str(self, locations, characters):
        chars = self.get_characters(locations, characters)
        if not chars: return ""
        return "\n".join(f"{c.name.title()} stands here" for c in chars)

    # -- Render --

    def render(self, locations=None, characters=None):
        parts = [f"&+W{self.name}&N", f"  {self.description}"]
        parts.append(self._exits_str())
        mob_str = self._mobs_str()
        if mob_str: parts.append(mob_str)
        obj_str = self._objects_str()
        if obj_str: parts.append(obj_str)
        if locations is not None and characters is not None:
            char_str = self._characters_str(locations, characters)
            if char_str: parts.append(char_str)
        return "\n".join(parts)

    def __repr__(self): return self.render()
    def __str__(self):  return self.render()
