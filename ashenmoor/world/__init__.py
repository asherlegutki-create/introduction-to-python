"""
ashenmoor.world
───────────────
World objects, rooms, mobs, and zones.

    from ashenmoor.world import Object, Item, Weapon, Mob, Room, Zone, TERRAIN
"""

from .objects import Object, Item, Weapon, Container, Scroll, Potion
from .mob     import Mob
from .room    import Room, TERRAIN
from .zone    import Zone, make_spawner

__all__ = ["Object", "Item", "Weapon", "Container", "Scroll", "Potion", "Mob", "Room", "Zone", "TERRAIN", "make_spawner"]
