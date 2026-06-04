"""ashenmoor.world.room — from document index 37, _objects_str updated for stacking"""
TERRAIN = ("no ground", "water", "mountain", "plain", "stone", "forest",
           "desert", "swamp", "road", "inside")

_BLOCKED_STATES = {"closed", "locked"}


def _stack_room_objects(objects) -> list[str]:
    """Group objects by room_description; return display lines with [N] prefix."""
    order  = []
    counts = {}
    descs  = {}
    for obj in objects:
        key = obj.name   # stack by name; items of same template share a name
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
        if not self.objects: return ""
        return "\n".join(_stack_room_objects(self.objects))

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
