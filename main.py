"""
main.py
───────
Run from the introduction-to-python directory:

    python main.py

To add more zones, import them and call state.load_zone() before crepl().
Zone vnum ranges must not overlap.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ashenmoor.color import crepl, cprint
from ashenmoor.core import Character, RACES
from ashenmoor.engine import GameState

# ── Import zones ──────────────────────────────────────────────────────────────
# Each zone is a Python package under zones/.
# Add more here as you build them:
#   from zones.riverview import ZONE as RIVERVIEW
#   from zones.dungeon   import ZONE as DUNGEON

#from zones.the_void import ZONE as THE_VOID
from zones.wilson import ZONE as WILSON
from zones.damien import ZONE as DAMIEN
from zones.timothy import ZONE as TIMOTHY
from zones.asher import ZONE as ASHER
from zones.gabe import ZONE as GABE
from zones.the_void import ZONE as THE_VOID
from zones.charlotte import ZONE as CHARLOTTE
from zones.wyatt import ZONE as CRYSTAL_CAVERNS
from zones.joshua import ZONE as JOSHUA
from zones.eva import ZONE as EVA
from zones.lindi import ZONE as LINDI
from zones.drew import ZONE as DREW
from zones.archer import ZONE as ARCHER
from zones.isaac import ZONE as ISAAC
from zones.reese import ZONE as REESE
from zones.jordan import ZONE as JORDAN


def main():
    # ── Characters ────────────────────────────────────────────────────────────
    characters = {
        "Moted": Character(
            {
                "name": "Moted",
                "race": "Dwarf",
                "class": "Shaman",
                "level": 24,
                "stats": [88, 80, 80, 80, 80, 80],
            },
            races=RACES,
        ),
        "Aleolas": Character(
            {
                "name": "Aleolas",
                "race": "Grey Elf",
                "class": "Ranger",
                "level": 50,
                "stats": [100, 80, 100, 80, 80, 80],
            },
            races=RACES,
        ),
    }

    locations = {"Moted": 1, "Aleolas": 1}

    # ── Wire up world ─────────────────────────────────────────────────────────
    state = GameState()
    state.load_world({}, characters, locations, player="Moted")

    # Load zones — rooms, object templates, and mob templates all merge in
    #state.load_zone(THE_VOID)
    state.load_zone(WILSON)
    state.load_zone(DAMIEN)
    state.load_zone(TIMOTHY)
    state.load_zone(THE_VOID)
    state.load_zone(CHARLOTTE)
    state.load_zone(ASHER)
    state.load_zone(GABE)
    state.load_zone(JOSHUA)
    state.load_zone(CRYSTAL_CAVERNS)
    state.load_zone(EVA)
    state.load_zone(LINDI)
    state.load_zone(DREW)
    state.load_zone(ARCHER)
    #state.load_zone(ISAAC)
    state.load_zone(REESE)
    state.load_zone(JORDAN)

    # ── Run ───────────────────────────────────────────────────────────────────
    cprint(f"&w{len(state.rooms)} rooms loaded across all zones.&N")

    crepl(
        handler=state.handle,
        prompt="&g> &N",
        banner=(
            "&WWelcome to &RRiverview &WChristian &BSchool&N SUD!&N\n"
            "&wType &Wlook&N&w, &Wn&N&w/&Ws&N&w/&We&N&w/&Ww&N&w, "
            "&Wwho&N&w, &Wstats&N&w, &Wquit&N&w.&N"
        ),
        farewell="&CGoodbye!&N",
    )


if __name__ == "__main__":
    main()
