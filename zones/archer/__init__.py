"""
zones.the_void
──────────────
The Void — starter zone.  Vnums 1-99.

Usage:
    from zones.the_void import ZONE
    state.load_zone(ZONE)
"""

from ashenmoor.world import Zone
from .objects import TEMPLATES as OBJECT_TEMPLATES
from .mobs    import TEMPLATES as MOB_TEMPLATES
from .rooms   import ROOMS

ZONE = Zone(
    name             = "&xW&yo&xod&yl&xa&yn&xd&N Manor",
    rooms            = ROOMS,
    object_templates = OBJECT_TEMPLATES,
    mob_templates    = MOB_TEMPLATES,
)
