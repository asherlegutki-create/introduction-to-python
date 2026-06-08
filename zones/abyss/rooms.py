"""
zones.abyssal.rooms
────────────────────
The Abyssal Web — a spider lair with managed respawn populations.
Vnum range: 16001 – 16099
"""

from ashenmoor.world import Room
from . import objects as O
from . import mobs    as M

ROOMS: dict[int, Room] = {

    1: Room({
        "number":      1,
        "name":        "&LThe Abyssal Web — Entrance&N",
        "description": (
            "Thick sheets of &Lglowing silk&N hang from every surface, muffling sound\n"
            "and light alike. The air is damp and carries a faint chemical bite.\n"
            "The web grows thicker to the &cnorth&N and &ceast&N."
        ),
        "indoors": True,
        "terrain": "web",
        "exits": [
            {"direction": "north", "roomId": 2},
            {"direction": "east",  "roomId": 3},
            {"direction": "up", "roomId": 99001, "external": True},
        ],
        "objects": [
            O.spawn("spider_silk"),
            O.spawn("spider_silk"),
        ],
        "mob_spawns": [
            {
                "template": "abyssal_spider_1",
                "max":      3,
                "start":    1,
            },
        ],
    }),

    2: Room({
        "number":      2,
        "name":        "&LThe Abyssal Web — Silk Tunnels&N",
        "description": (
            "Narrow tunnels of compressed silk wind in every direction.\n"
            "Occasionally a leg-sized shape moves behind the walls.\n"
            "The &Lglowing filaments&N overhead provide just enough light to see."
        ),
        "indoors": True,
        "terrain": "web",
        "exits": [
            {"direction": "south", "roomId": 1},
            {"direction": "north", "roomId": 4},
            {"direction": "east",  "roomId": 5},
        ],
        "objects": [
            O.spawn("abyssal_egg_sac"),
        ],
        "mob_spawns": [
            {
                "template": "abyssal_spider_1",
                "max":      4,
                "start":    2,
            },
            {
                "template": "abyssal_spider_2",
                "max":      2,
                "start":    1,
            },
        ],
    }),

    3: Room({
        "number":      3,
        "name":        "&LThe Abyssal Web — Feeding Chamber&N",
        "description": (
            "Cocooned shapes hang from the ceiling — prey in various states\n"
            "of preservation. The floor is sticky underfoot.\n"
            "Larger spiders favour this room."
        ),
        "indoors": True,
        "terrain": "web",
        "exits": [
            {"direction": "west",  "roomId": 1},
            {"direction": "north", "roomId": 5},
        ],
        "objects": [
            O.spawn("venom_gland"),
        ],
        "mob_spawns": [
            {
                "template": "abyssal_spider_2",
                "max":      3,
                "start":    2,
            },
        ],
    }),

    4: Room({
        "number":      4,
        "name":        "&LThe Abyssal Web — Brood Chamber&N",
        "description": (
            "Dozens of &Megg sacs&N cover every wall, pulsing in unison.\n"
            "The air is thick and warm. This is the heart of the colony.\n"
            "Something very large watches from the far end of the chamber."
        ),
        "indoors": True,
        "terrain": "web",
        "exits": [
            {"direction": "south", "roomId": 2},
        ],
        "objects": [
            O.spawn("abyssal_egg_sac"),
            O.spawn("abyssal_egg_sac"),
            O.spawn("spider_silk"),
        ],
        "mob_spawns": [
            {
                "template":          "abyssal_spider_3",
                "max":               2,
                "start":             1,
                "respawn_ticks":     150,   # 10 minutes — boss-tier
                "repop_with_player": False,
            },
            {
                "template": "abyssal_spider_2",
                "max":      2,
                "start":    1,
            },
        ],
    }),

    5: Room({
        "number":      5,
        "name":        "&LThe Abyssal Web — Junction&N",
        "description": (
            "A wide junction where several silk tunnels converge.\n"
            "The walls here are thinner — you can see faint light through them\n"
            "though you cannot tell its source."
        ),
        "indoors": True,
        "terrain": "web",
        "exits": [
            {"direction": "west",  "roomId": 2},
            {"direction": "south", "roomId": 3},
        ],
        "objects": [
            O.spawn("spider_silk"),
            O.spawn("venom_gland"),
        ],
        "mob_spawns": [
            {
                "template": "abyssal_spider_1",
                "max":      2,
                "start":    1,
            },
            {
                "template": "abyssal_spider_2",
                "max":      2,
                "start":    1,
            },
        ],
    }),

}
