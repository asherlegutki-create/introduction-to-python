"""
ashenmoor.engine.ticker
───────────────────────
Auto-combat REPL for local stdin/stdout play.
Login flow uses the shared ashenmoor.engine.login module.
"""

import sys
import time
import select
import asyncio

from ..color import diku_to_ansi, cprint

TICK_INTERVAL = 4.0


def _build_prompt(state) -> str:
    name = state.player
    char = state.characters.get(name)
    if not char:
        return diku_to_ansi("&g> &N")

    hp   = getattr(char, "hp",        0)
    mhp  = getattr(char, "max_hp",    1)
    temp = getattr(char, "temp_hp",   0)
    mv   = getattr(char, "moves",     0)
    mmv  = getattr(char, "max_moves", 1)

    if temp > 0:
        hp_color   = "&M"
        hp_display = hp + temp
    else:
        pct      = hp / max(1, mhp)
        hp_color = "&+G" if pct > 0.66 else ("&+Y" if pct > 0.33 else "&+R")
        hp_display = hp

    dnd       = getattr(char, "dnd", {}) or {}
    resources = []

    sw  = dnd.get("second_wind_uses", 0)
    swm = dnd.get("second_wind_max",  0)
    if swm: resources.append(f"SW:{sw}/{swm}")

    as_ = dnd.get("action_surge_uses", 0)
    asm = dnd.get("action_surge_max",  0)
    if asm: resources.append(f"AS:{as_}/{asm}")

    ind  = dnd.get("indomitable_uses", 0)
    indm = dnd.get("indomitable_max",  0)
    if indm: resources.append(f"IND:{ind}/{indm}")

    sd  = dnd.get("superiority_dice",     0)
    sdm = dnd.get("superiority_dice_max", 0)
    sds = dnd.get("superiority_die_size", 8)
    if sdm:
        rip_state = "&Garmed&N" if dnd.get("riposte_armed") else "ready"
        if sd == 0: rip_state = "&R0&N"
        resources.append(f"SD:{sd}d{sds} RIP:{rip_state}")

    res_str  = " ".join(resources)
    chevron  = "&R>&N" if name in state.fighting else "&g>&N"
    res_part = f" | {res_str}" if res_str else ""

    raw = (
        f"&w[{hp_color}{hp_display}&w/{mhp}hp "
        f"&W{mv}&w/{mmv}mv{res_part}&w] {chevron} &N"
    )
    return diku_to_ansi(raw)


def _sync_subclass_selection(char) -> None:
    from ..engine.subclass import run_subclass_selection

    async def _send(text: str) -> None:
        sys.stdout.write(diku_to_ansi(text) + "\n")
        sys.stdout.flush()

    async def _recv() -> str:
        return input("").strip()

    asyncio.run(run_subclass_selection(char, send=_send, recv=_recv))


def login_crepl(state, start_room: int, races: dict,
                db_path: str = "ashenmoor.db") -> None:
    """
    Interactive login for the local console.
    Uses the shared login flow from engine.login.
    """
    from ..engine.persist import open_db
    from ..engine.login   import run_login_flow

    conn = open_db(db_path)

    async def _send(text: str) -> None:
        sys.stdout.write(diku_to_ansi(text))
        sys.stdout.flush()

    async def _recv() -> str:
        return input("").strip()

    async def _run():
        return await run_login_flow(
            state      = state,
            conn       = conn,
            send       = _send,
            recv       = _recv,
            start_room = start_room,
            races      = races,
        )

    result = asyncio.run(_run())

    if result is None:
        sys.exit(0)

    char, account_id, room_vnum = result
    state.player = char.name
    state._db    = conn

    # Store account_id for save calls
    state._account_ids = getattr(state, "_account_ids", {})
    state._account_ids[char.name] = account_id

    # Subclass selection if needed
    from ..engine.subclass import needs_subclass
    if needs_subclass(char):
        _sync_subclass_selection(char)
        from ..engine.persist import save_character
        save_character(conn, char, room_vnum, account_id=account_id)


def auto_crepl(state, prompt: str = "&g> &N",
               quit_cmds: tuple = ("quit", "exit", "q"),
               banner: str = "", farewell: str = "") -> None:
    from ..engine.subclass import needs_subclass

    if banner:
        cprint(banner)

    last_tick = time.monotonic()
    sys.stdout.write(_build_prompt(state))
    sys.stdout.flush()

    while True:
        now          = time.monotonic()
        time_to_tick = max(0.05, TICK_INTERVAL - (now - last_tick))

        try:
            ready, _, _ = select.select([sys.stdin], [], [], time_to_tick)
        except (KeyboardInterrupt, EOFError):
            break

        need_prompt = False

        if ready:
            try:
                raw = sys.stdin.readline()
            except (KeyboardInterrupt, EOFError):
                break
            if not raw:
                break

            raw = raw.strip()
            if raw:
                if raw.lower() in quit_cmds:
                    break

                char = state.characters.get(state.player)
                if char and needs_subclass(char):
                    sys.stdout.write("\n")
                    _sync_subclass_selection(char)
                    if state._db:
                        from ..engine.persist import save_character
                        account_id = getattr(state, "_account_ids", {}).get(state.player, 0)
                        save_character(state._db, char,
                                       state.locations.get(state.player, 0),
                                       account_id=account_id)
                    need_prompt = True
                else:
                    result = state.handle(raw)
                    if result == "quit":
                        break
                    sys.stdout.write("\n")
                    if result:
                        cprint(result)
                    need_prompt = True
            else:
                sys.stdout.write("\n")
                need_prompt = True

        now = time.monotonic()
        if (now - last_tick) >= TICK_INTERVAL:
            last_tick += TICK_INTERVAL
            tick_output = None
            if state.fighting:
                tick_output = state.combat_tick()
            else:
                tick_output = state.mob_aggro_tick()

            if tick_output:
                sys.stdout.write("\r\033[K")
                cprint(tick_output)
                need_prompt = True

        if need_prompt:
            sys.stdout.write(_build_prompt(state))
            sys.stdout.flush()

    if farewell:
        cprint(farewell)
