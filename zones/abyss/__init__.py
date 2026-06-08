from ashenmoor.world.zone import Zone, apply_vnums
from .zone    import number as ZONE_NUMBER, name as ZONE_NAME, author as ZONE_AUTHOR
from .zone    import respawn_ticks as RESPAWN_TICKS, repop_with_player as REPOP_WITH_PLAYER
from .objects import TEMPLATES as OBJECT_TEMPLATES
from .mobs    import TEMPLATES as MOB_TEMPLATES
from .rooms   import ROOMS

ZONE = Zone(
    name              = ZONE_NAME,
    rooms             = apply_vnums(ROOMS, ZONE_NUMBER),
    object_templates  = OBJECT_TEMPLATES,
    mob_templates     = MOB_TEMPLATES,
    vnum_base         = ZONE_NUMBER,
    author            = ZONE_AUTHOR,
    respawn_ticks     = RESPAWN_TICKS,
    repop_with_player = REPOP_WITH_PLAYER,
)
