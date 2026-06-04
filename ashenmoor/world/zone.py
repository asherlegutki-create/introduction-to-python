"""
ashenmoor.world.zone  (copy from document index 39)
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .room import Room


def apply_vnums(rooms: dict, zone_number: int) -> dict:
    if zone_number < 0:
        raise ValueError(f"zone_number must be >= 0, got {zone_number!r}")
    if zone_number == 0:
        for local_num, room in rooms.items():
            room.number = local_num
        return dict(rooms)
    base     = zone_number * 1000
    new_dict = {}
    for local_num, room in rooms.items():
        abs_vnum    = base + local_num
        room.number = abs_vnum
        for ex in room.exits:
            if not ex.get("external", False):
                if "roomId" not in ex:
                    direction = ex.get("direction", "?")
                    raise KeyError(
                        f"Zone {zone_number}, room {local_num}: exit '{direction}' "
                        f"is missing 'roomId'"
                    )
                ex["roomId"] = base + ex["roomId"]
        new_dict[abs_vnum] = room
    return new_dict


class Zone:
    def __init__(
        self,
        name:             str,
        rooms:            dict,
        object_templates: dict | None = None,
        mob_templates:    dict | None = None,
        vnum_base:        int         = 0,
        author:           str         = "",
    ):
        self.name             = name
        self.rooms            = rooms
        self.object_templates = object_templates or {}
        self.mob_templates    = mob_templates    or {}
        self.vnum_base        = vnum_base
        self.author           = author

    def spawn_object(self, key: str):
        return _spawn(key, self.object_templates, _default_object_class)

    def spawn_mob(self, key: str):
        return _spawn(key, self.mob_templates, _default_mob_class)

    def __repr__(self) -> str:
        author = f", author={self.author!r}" if self.author else ""
        return (f"Zone({self.name!r}, vnum_base={self.vnum_base}, "
                f"{len(self.rooms)} rooms, "
                f"{len(self.object_templates)} obj templates, "
                f"{len(self.mob_templates)} mob templates{author})")


def _default_object_class():
    from .objects import Object
    return Object

def _default_mob_class():
    from .mob import Mob
    return Mob

def _spawn(key: str, templates: dict, default_class_fn):
    if key not in templates:
        raise KeyError(
            f"No template named {key!r}. Available: {list(templates)}"
        )
    template = dict(templates[key])
    cls      = template.pop("spawn_as", None) or default_class_fn()
    obj      = cls(template)

    # Recursively spawn container contents listed as template key strings
    from .objects import Container
    if isinstance(obj, Container) and obj.contents:
        spawned = []
        for item in obj.contents:
            if isinstance(item, str):
                spawned.append(_spawn(item, templates, default_class_fn))
            else:
                spawned.append(item)
        obj.contents = spawned

    return obj


def make_spawner(templates: dict, default_class_fn):
    def spawn(key: str):
        return _spawn(key, templates, default_class_fn)
    return spawn
