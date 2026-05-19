"""
main.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ashenmoor.color  import crepl, cprint
from ashenmoor.core   import Character, RACES
from ashenmoor.engine import GameState
from ashenmoor.world.powers import POWERS   # <-- import the registry

from zones.the_void  import ZONE as THE_VOID
from zones.archer    import ZONE as ARCHER
from zones.asher     import ZONE as ASHER
from zones.charlotte import ZONE as CHARLOTTE
from zones.damien    import ZONE as DAMIEN
from zones.drew      import ZONE as DREW
from zones.eva       import ZONE as EVA
from zones.gabe      import ZONE as GABE
from zones.isaac     import ZONE as ISAAC
from zones.jordan    import ZONE as JORDAN
from zones.joshua    import ZONE as JOSHUA
from zones.lindi     import ZONE as LINDI
from zones.new_zone  import ZONE as NEW_ZONE
from zones.reese     import ZONE as REESE
from zones.timothy   import ZONE as TIMOTHY
from zones.wilson    import ZONE as WILSON
from zones.wyatt     import ZONE as WYATT


def main():
    characters = {
        "Moted": Character({
            "name":   "Moted",
            "race":   "Dwarf",
            "class":  "Shaman",
            "level":  24,
            "stats":  [88, 80, 80, 80, 80, 80],
            "powers": [              # <-- assign powers here
                POWERS["heal"],
                POWERS["smite"],
                POWERS["meditate"],
                POWERS["shout"],
            ],
        }, races=RACES),

        "Aleolas": Character({
            "name":   "Aleolas",
            "race":   "Grey Elf",
            "class":  "Ranger",
            "level":  50,
            "stats":  [100, 80, 100, 80, 80, 80],
            "powers": [
                POWERS["entangle"],
                POWERS["barkskin"],
                POWERS["frost_bolt"],
            ],
        }, races=RACES),
    }

    locations = {"Moted": 1, "Aleolas": 1}

    state = GameState()
    state.load_world({}, characters, locations, player="Moted")

    state.load_zone(THE_VOID)
    state.load_zone(ARCHER)
    state.load_zone(ASHER)
    state.load_zone(CHARLOTTE)
    state.load_zone(DAMIEN)
    state.load_zone(DREW)
    state.load_zone(EVA)
    state.load_zone(GABE)
    state.load_zone(ISAAC)
    state.load_zone(JORDAN)
    state.load_zone(JOSHUA)
    state.load_zone(LINDI)
    state.load_zone(NEW_ZONE)
    state.load_zone(REESE)
    state.load_zone(TIMOTHY)
    state.load_zone(WILSON)
    state.load_zone(WYATT)

    cprint(f"&w{len(state.rooms)} rooms loaded across all zones.&N")

    crepl(
        handler  = state.handle,
        prompt   = "&g> &N",
        banner   = (
            "&WWelcome to &RRiverview &WChristian &BSchool&N SUD!&N\n"
            "&wType &Wlook&N&w, &Wn&N&w/&Ws&N&w/&We&N&w/&Ww&N&w, "
            "&Wwho&N&w, &Wstats&N&w, &Wpowers&N&w, &Wquit&N&w.&N"
        ),
        farewell = "&CGoodbye!&N",
    )


if __name__ == "__main__":
    main()
