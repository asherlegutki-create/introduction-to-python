"""
ashenmoor.world.zone
─────────────────────
Zone container and respawn initialisation.

Zone-level respawn defaults are read from the zone module's attributes:
    respawn_ticks        int   default ticks before a mob respawns (4s each)
    repop_with_player    bool  default: whether mobs respawn with players present

These can be overridden per mob_spawn entry in each room.
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
        name:                str,
        rooms:               dict,
        object_templates:    dict | None = None,
        mob_templates:       dict | None = None,
        vnum_base:           int         = 0,
        author:              str         = "",
        respawn_ticks:       int         = 75,
        repop_with_player:   bool        = False,
    ):
        self.name               = name
        self.rooms              = rooms
        self.object_templates   = object_templates or {}
        self.mob_templates      = mob_templates    or {}
        self.vnum_base          = vnum_base
        self.author             = author
        self.respawn_ticks      = respawn_ticks
        self.repop_with_player  = repop_with_player

        # Wire up respawn for any room that has mob_spawns defined
        self._init_respawn()

    def _init_respawn(self) -> None:
        """
        For every room that was constructed with a "mob_spawns" key,
        resolve the spawn config (applying zone-level defaults for missing
        fields) and call room.init_respawn().

        The spawner is built once per zone so the closure correctly captures
        the final mob_templates reference rather than a loop variable.
        """
        from .mob import Mob

        # Single spawner shared by all rooms in this zone.
        # Captures mob_templates by reference — safe because the dict
        # is not mutated after Zone.__init__ completes.
        templates_ref = self.mob_templates

        def spawner(key: str):
            mob = Mob(dict(templates_ref[key]))
            mob._template_key = key
            return mob

        for room in self.rooms.values():
            raw_spawns = getattr(room, "_raw_mob_spawns", None)
            if not raw_spawns:
                continue

            resolved = []
            for entry in raw_spawns:
                template_key = entry["template"]
                if template_key not in self.mob_templates:
                    import warnings
                    warnings.warn(
                        f"Room {room.number}: mob_spawns template "
                        f"'{template_key}' not found in mob_templates",
                        stacklevel=2,
                    )
                    continue
                resolved.append({
                    "template":          template_key,
                    "max":               entry.get("max",               1),
                    "start":             entry.get("start",             1),
                    "respawn_ticks":     entry.get("respawn_ticks",     self.respawn_ticks),
                    "repop_with_player": entry.get("repop_with_player", self.repop_with_player),
                })

            if not resolved:
                continue

            room.init_respawn(resolved, spawner)

    def spawn_object(self, key: str):
        return _spawn(key, self.object_templates, _default_object_class)

    def spawn_mob(self, key: str):
        return _spawn(key, self.mob_templates, _default_mob_class)

    def __repr__(self) -> str:
        author = f", author={self.author!r}" if self.author else ""
        return (
            f"Zone({self.name!r}, vnum_base={self.vnum_base}, "
            f"{len(self.rooms)} rooms, "
            f"{len(self.object_templates)} obj templates, "
            f"{len(self.mob_templates)} mob templates{author})"
        )


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
