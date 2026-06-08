"""
ashenmoor.engine.ticker
───────────────────────
Auto-combat REPL for local stdin/stdout play.

Uses select() on stdin so the combat tick fires every TICK_INTERVAL
seconds regardless of whether the player is typing.

Subclass selection uses the shared ashenmoor.engine.subclass module
so the flow is byte-for-byte identical to the network client — only
the send/recv primitives differ (stdout vs socket).
"""

import sys
import time
import select
import asyncio

from ..color import diku_to_ansi, cprint

TICK_INTERVAL = 4.0


# ── Login / character selection ───────────────────────────────────────────────

def _char_exists(conn, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM characters WHERE name = ?", (name,)
    ).fetchone()
    return row is not None


def _make_new_fighter(name: str, races: dict):
    from ..core.character           import Character
    from ..dnd.classes.fighter      import new_fighter_dnd, FIGHTER_POWERS

    return Character({
        "name":      name,
        "race":      "Human",
        "class":     "Fighter",
        "level":     1,
        "stats":     [90, 90, 90, 70, 70, 70],
        "dnd":       new_fighter_dnd(level=1, fighting_style="dueling"),
        "powers":    list(FIGHTER_POWERS),
        "alignment": "True Neutral",
        "position":  "standing",
    }, races=races)


def _make_shell_char(name: str, row, races: dict):
    from ..core.character      import Character
    from ..dnd.classes.fighter import new_fighter_dnd, FIGHTER_POWERS

    cclass = row["class"]
    level  = row["level"]

    # Migrate Warrior → Fighter
    display_class = "Fighter" if cclass.lower() == "warrior" else cclass

    d: dict = {
        "name":  name,
        "race":  row["race"],
        "class": display_class,
        "level": level,
        "stats": [75] * 6,
    }

    if display_class.lower() in ("fighter", "warrior"):
        d["dnd"]    = new_fighter_dnd(level=level)
        d["powers"] = list(FIGHTER_POWERS)

    return Character(d, races=races)


# ── Sync wrappers for the shared async subclass flow ─────────────────────────

def _sync_subclass_selection(char) -> None:
    """
    Run the shared subclass selection flow synchronously for the local
    console.  Bridges the async run_subclass_selection into a blocking
    call using a fresh event loop.
    """
    from ..engine.subclass import run_subclass_selection

    async def _send(text: str) -> None:
        sys.stdout.write(diku_to_ansi(text) + "\n")
        sys.stdout.flush()

    async def _recv() -> str:
        return input("").strip()

    async def _run():
        await run_subclass_selection(char, send=_send, recv=_recv)

    asyncio.run(_run())


def login_crepl(
    state,
    start_room: int,
    races:      dict,
    db_path:    str  = "ashenmoor.db",
) -> None:
    """
    Interactive login / character-creation flow for the local console.
    Blocks until the player has logged in and chosen a subclass if needed.
    """
    from ..engine.persist  import open_db, save_character, load_character
    from ..engine.subclass import needs_subclass

    conn = open_db(db_path)

    cprint("\n&+W╔══════════════════════════════╗&N")
    cprint("&+W║      W e l c o m e  t o      ║&N")
    cprint("&+W║      R i v e r m o o r       ║&N")
    cprint("&+W╚══════════════════════════════╝&N\n")

    while True:
        name_raw = input("Who would you like to be known as? ").strip()
        if not name_raw:
            continue
        name = name_raw[0].upper() + name_raw[1:].lower()

        if not _char_exists(conn, name):
            cprint(f"\n&wThat character does not exist.&N")
            cprint(f"&wWould you like to create &W{name}&w now?&N")
            answer = input("(yes/no) > ").strip().lower()
            if answer not in ("yes", "y"):
                cprint("&wVery well. Enter another name.&N\n")
                continue

            char = _make_new_fighter(name, races)
            save_character(conn, char, location=start_room, include_hp=True)

            state.characters[name] = char
            state.locations[name]  = start_room
            state.player           = name

            cprint(f"\n&+WCharacter &N{name}&+W has been created!&N")
            cprint("&wYou are a level &W1&w Human Fighter.&N")
            cprint("&x(STR 90 / DEX 90 / CON 90 / INT 70 / WIS 70 / CHA 70)&N\n")
            break

        else:
            row = conn.execute(
                "SELECT race, class, level FROM characters WHERE name = ?",
                (name,),
            ).fetchone()

            char       = _make_shell_char(name, row, races)
            saved_room = load_character(conn, name, char)
            room_vnum  = saved_room if saved_room else start_room

            state.characters[name] = char
            state.locations[name]  = room_vnum
            state.player           = name

            cprint(f"\n&+WWelcome back, &N{name}&+W!&N")
            cprint(f"&x(Level {char.level} {char.race} {char.cclass})&N\n")
            break

    state._db = conn

    # ── Subclass selection before entering the world ──────────────────────
    if needs_subclass(char):
        _sync_subclass_selection(char)
        save_character(conn, char, state.locations.get(name, start_room))


# ── Prompt builder ────────────────────────────────────────────────────────────

def _build_prompt(state) -> str:
    """
    Identical logic to MudClient._build_prompt — kept in sync manually.
    Local console renders via diku_to_ansi directly to stdout.
    """
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
    if swm:
        resources.append(f"SW:{sw}/{swm}")

    as_ = dnd.get("action_surge_uses", 0)
    asm = dnd.get("action_surge_max",  0)
    if asm:
        resources.append(f"AS:{as_}/{asm}")

    ind  = dnd.get("indomitable_uses", 0)
    indm = dnd.get("indomitable_max",  0)
    if indm:
        resources.append(f"IND:{ind}/{indm}")

    sd  = dnd.get("superiority_dice",     0)
    sdm = dnd.get("superiority_dice_max", 0)
    sds = dnd.get("superiority_die_size", 8)
    if sdm:
        if sd > 0:
            rip_state = "&Garmed&N" if dnd.get("riposte_armed") else "ready"
        else:
            rip_state = "&R0&N"
        resources.append(f"SD:{sd}d{sds} RIP:{rip_state}")

    res_str  = " ".join(resources)
    chevron  = "&R>&N" if name in state.fighting else "&g>&N"
    res_part = f" | {res_str}" if res_str else ""

    raw = (
        f"&w[{hp_color}{hp_display}&w/{mhp}hp "
        f"&W{mv}&w/{mmv}mv{res_part}&w] {chevron} &N"
    )
    return diku_to_ansi(raw)


# ── Main REPL ─────────────────────────────────────────────────────────────────

def auto_crepl(
    state,
    prompt:    str   = "&g> &N",
    quit_cmds: tuple = ("quit", "exit", "q"),
    banner:    str   = "",
    farewell:  str   = "",
) -> None:
    """
    Drop-in replacement for crepl() with automatic combat ticks and
    the new resource-aware prompt.
    """
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

        # ── Player typed something ────────────────────────────────────────
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

                # ── Subclass selection intercept ──────────────────────────
                char = state.characters.get(state.player)
                if char and needs_subclass(char):
                    sys.stdout.write("\n")
                    _sync_subclass_selection(char)
                    if state._db:
                        from ..engine.persist import save_character as _save
                        _save(state._db, char, state.locations.get(state.player, 0))
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

        # ── Tick ──────────────────────────────────────────────────────────
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
