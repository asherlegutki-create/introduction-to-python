"""
ashenmoor.world.zone
────────────────────
Zone class and vnum utilities.

Vnum scheme
───────────
Every zone has a number (from zones/<name>/zone.py).
Local room numbers in rooms.py use small integers (1, 2, 3 …).
apply_vnums() converts them to absolute vnums before the Zone is built:

    absolute_vnum = zone_number * 1000 + local_room_number

    zone 1,  room 1   →   1001
    zone 1,  room 999 →   1999
    zone 99, room 1   →  99001
    zone 99, room 999 →  99999

This gives each zone a private range of 999 rooms with no collisions.

External exits
──────────────
Exits that connect to a different zone carry  "external": True.
apply_vnums() leaves those roomIds untouched — they are already absolute.

    # rooms.py — connecting from zone 99 to zone 1, room 1
    {"direction": "west", "roomId": 1001, "external": True}

Zone template pattern
─────────────────────
Every zone package should follow this layout:

    zones/my_zone/
        zone.py      →  number = 7          # zone number, unique per zone
        objects.py   →  TEMPLATES, spawn
        mobs.py      →  TEMPLATES, spawn
        rooms.py     →  ROOMS  (local vnums 1-999)
        __init__.py  →  imports all, calls apply_vnums, builds ZONE
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .room import Room


# ── apply_vnums ───────────────────────────────────────────────────────────────

def apply_vnums(rooms: dict, zone_number: int) -> dict:
    """
    Convert a rooms dict using local vnums into one using absolute vnums.

    Parameters
    ----------
    rooms       : dict[int, Room]   keyed by local vnum (1, 2, 3 …)
    zone_number : int               from zones/<name>/zone.py

    zone_number = 0  (special)
        No prefix is applied.  Room numbers stay exactly as written.
        Use this for a default / limbo zone whose vnums are canonical.
        Exit roomIds are also left untouched (no offset added).
        Exits to prefixed zones still need  "external": True.

    zone_number > 0
        absolute_vnum = zone_number * 1000 + local_room_number
        Exit roomIds receive the same offset unless  "external": True.

    Returns
    -------
    dict[int, Room]   keyed by absolute vnum

    Side effects
    ------------
    Each Room's .number attribute is updated to the absolute vnum.
    Exit roomIds are updated in place UNLESS the exit has "external": True.
    """
    if zone_number < 0:
        raise ValueError(f"zone_number must be >= 0, got {zone_number!r}")

    # zone 0 — no prefix, rooms are their own absolute vnums
    if zone_number == 0:
        for local_num, room in rooms.items():
            room.number = local_num   # already absolute, just confirm
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
                        f"is missing 'roomId' (check for typos like 'roomid')"
                    )
                ex["roomId"] = base + ex["roomId"]

        new_dict[abs_vnum] = room

    return new_dict


# ── Zone ──────────────────────────────────────────────────────────────────────

class Zone:
    """
    A self-contained area of the world.

    Parameters
    ----------
    name             str
    rooms            dict[int, Room]   keyed by ABSOLUTE vnums (after apply_vnums)
    object_templates dict[str, dict]   optional
    mob_templates    dict[str, dict]   optional
    vnum_base        int               zone_number, stored for reference
    author           str               zone author name, available to game logic
    """

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


# ── Spawn machinery ───────────────────────────────────────────────────────────

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
    return cls(template)


def make_spawner(templates: dict, default_class_fn):
    """
    Return a spawn(key) function bound to *templates*.

    Use at the bottom of a zone's objects.py and mobs.py:

        from ashenmoor.world.zone import make_spawner
        spawn = make_spawner(TEMPLATES, lambda: Object)
    """
    def spawn(key: str):
        return _spawn(key, templates, default_class_fn)
    return spawn
