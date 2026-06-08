"""
ashenmoor.engine.targeting
──────────────────────────
Keyword-based targeting system — LIFO (last in, first out) order.

Newest mobs and objects in a room are matched first (1.mob = most recently
spawned).  Inventory items are also matched newest-first so that the most
recently picked-up item is 1.item.

Target string format
────────────────────
  "marker"      first (newest) thing whose keywords include "marker"
  "2.marker"    second newest such thing
  "1.marker"    same as "marker" — explicit index 1

Search order within the room (newest first in each category)
─────────────────────────────────────────────────────────────
  1. Mobs        (room.mobs reversed)
  2. Characters  (players currently in the room)
  3. Objects     (room.objects reversed)
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room     import Room
    from ..core.character import Character


def parse_target(s: str) -> tuple[int, str]:
    """
    Split a target string into (index, keyword).

    "marker"    -> (1, "marker")
    "2.marker"  -> (2, "marker")
    "1.guardian"-> (1, "guardian")

    Index is 1-based (1 = first / newest match).
    """
    s = s.strip().lower()
    if "." in s:
        prefix, _, keyword = s.partition(".")
        if prefix.isdigit():
            idx = int(prefix)
            return (max(1, idx), keyword.strip())
    return (1, s)


def find_target(
    target_str:  str,
    room:        "Room",
    locations:   dict[str, int]         | None = None,
    characters:  dict[str, "Character"] | None = None,
) -> object | None:
    """
    Resolve a target string to a live instance in the room.

    Searches newest-first (LIFO) within mobs and objects.
    Characters are not reversed since their presence order is not meaningful.
    """
    idx, keyword = parse_target(target_str)
    matches = 0

    # ── 1. Mobs — newest first ────────────────────────────────────────────────
    for mob in reversed(room.mobs):
        if _mob_matches(mob, keyword):
            matches += 1
            if matches == idx:
                return mob

    # ── 2. Characters (players in this room) ──────────────────────────────────
    if locations is not None and characters is not None:
        for name, room_id in locations.items():
            if room_id == room.number and name in characters:
                char = characters[name]
                if _char_matches(char, keyword):
                    matches += 1
                    if matches == idx:
                        return char

    # ── 3. Objects — newest first ─────────────────────────────────────────────
    for obj in reversed(room.objects):
        if _obj_matches(obj, keyword):
            matches += 1
            if matches == idx:
                return obj

    return None


def find_all_targets(
    keyword:    str,
    room:       "Room",
    locations:  dict[str, int]         | None = None,
    characters: dict[str, "Character"] | None = None,
) -> list:
    """
    Return every instance in the room that matches *keyword*, newest first.
    """
    _, kw = parse_target(keyword)
    results = []

    for mob in reversed(room.mobs):
        if _mob_matches(mob, kw):
            results.append(mob)

    if locations is not None and characters is not None:
        for name, room_id in locations.items():
            if room_id == room.number and name in characters:
                char = characters[name]
                if _char_matches(char, kw):
                    results.append(char)

    for obj in reversed(room.objects):
        if _obj_matches(obj, kw):
            results.append(obj)

    return results


def target_name(instance) -> str:
    return getattr(instance, "name", str(instance))


# ── Internal matchers ─────────────────────────────────────────────────────────

def _mob_matches(mob, keyword: str) -> bool:
    if hasattr(mob, "key_words"):
        if keyword in (k.lower() for k in mob.key_words):
            return True
    return keyword in mob.name.lower()


def _char_matches(char, keyword: str) -> bool:
    return keyword in char.name.lower()


def _obj_matches(obj, keyword: str) -> bool:
    if hasattr(obj, "key_words"):
        if keyword in (k.lower() for k in obj.key_words):
            return True
    return keyword in obj.name.lower()
