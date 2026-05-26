"""
main.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ashenmoor.color               import cprint
from ashenmoor.core                import RACES
from ashenmoor.engine              import GameState
from ashenmoor.engine.ticker       import login_crepl, auto_crepl

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

DB_PATH    = "ashenmoor.db"
START_ROOM = 99001   # Hub room in new_zone — where new characters spawn


def main():
    state = GameState()

    # ── Load all zones (no characters yet — login picks who plays) ──────────
    state.load_world({}, {}, {})

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

    cprint(f"&x{len(state.rooms)} rooms loaded.&N")

    # ── Login: picks/creates character, sets state.player ───────────────────
    login_crepl(
        state      = state,
        start_room = START_ROOM,
        races      = RACES,
        db_path    = DB_PATH,
    )

    # ── Start the game ───────────────────────────────────────────────────────
    char = state.characters[state.player]
    auto_crepl(
        state    = state,
        prompt   = "&g> &N",
        banner   = (
            f"&wYou are &W{char.name}&w, a level &W{char.level}&w "
            f"{char.race} {char.cclass}.&N\n"
            f"&xType &Wscore&N&x, &Watt&N&x, &Wlook&N&x, "
            f"&Wkill <mob>&N&x, &Wquit&N&x.&N"
        ),
        farewell = "&CGoodbye! Your progress has been saved.&N",
    )


if __name__ == "__main__":
    main()
