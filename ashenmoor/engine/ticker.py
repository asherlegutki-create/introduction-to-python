"""
ashenmoor.engine.ticker
───────────────────────
Auto-combat REPL.

Uses select() on stdin so the combat tick fires every TICK_INTERVAL
seconds regardless of whether the player is typing.

Prompt behaviour
────────────────
  The prompt is only (re)printed when there is actually something to
  show the player:
    • The player typed a command  → show result, then prompt.
    • Combat tick produced output → show output, then prompt.
    • Idle timeout, no combat     → do nothing, no extra prompt printed.

This prevents the cursor line from being spammed with prompts while the
player is just standing around.
"""

import sys
import time
import select

from ..color import diku_to_ansi, cprint

TICK_INTERVAL = 4.0   # seconds between auto-attack rounds



# ── Login / character selection ───────────────────────────────────────────────

def _char_exists(conn, name: str) -> bool:
    """Return True if *name* is in the characters table."""
    row = conn.execute(
        "SELECT 1 FROM characters WHERE name = ?", (name,)
    ).fetchone()
    return row is not None


def _make_new_warrior(name: str, races: dict):
    """Create a fresh level-1 Human Warrior with the standard starter stats."""
    from ..core.character           import Character
    from ..dnd.classes.warrior      import new_warrior_dnd, WARRIOR_POWERS

    return Character({
        "name":      name,
        "race":      "Human",
        "class":     "Warrior",
        "level":     1,
        "stats":     [90, 90, 90, 70, 70, 70],   # STR DEX CON INT WIS CHA
        "dnd":       new_warrior_dnd(level=1, fighting_style="dueling"),
        "powers":    WARRIOR_POWERS,
        "alignment": "True Neutral",
        "position":  "standing",
    }, races=races)


def _make_shell_char(name: str, row, races: dict):
    """
    Build a Character shell matching the class/race stored in *row*,
    then let load_character() fill in the real stats from the DB.

    We need the dnd dict to match the saved class so that warrior
    features (Second Wind, Action Surge) work after loading.
    """
    from ..core.character           import Character
    from ..dnd.classes.warrior      import new_warrior_dnd, WARRIOR_POWERS

    cclass = row["class"]
    level  = row["level"]

    d: dict = {
        "name":   name,
        "race":   row["race"],
        "class":  cclass,
        "level":  level,
        "stats":  [75] * 6,   # overwritten by load_character
    }

    if cclass.lower() in ("warrior", "fighter"):
        d["dnd"]    = new_warrior_dnd(level=level)
        d["powers"] = WARRIOR_POWERS

    return Character(d, races=races)


def login_crepl(
    state,
    start_room: int,
    races:      dict,
    db_path:    str  = "ashenmoor.db",
) -> None:
    """
    Interactive login / character-creation flow.

    Prompts for a character name, checks the database, and either:
      • loads an existing character, or
      • offers to create a new level-1 Human Warrior.

    After a character is selected, sets state.player and
    state.locations[name], then returns so auto_crepl() can start.

    Parameters
    ----------
    state       : GameState (world already loaded via load_world).
    start_room  : Vnum of the default starting room for new characters.
    races       : RACES dict to pass into Character().
    db_path     : Path to the SQLite database file.
    """
    import sqlite3
    from ..engine.persist import open_db, save_character, load_character

    conn = open_db(db_path)

    cprint("\n&+W╔══════════════════════════════╗&N")
    cprint("&+W║      W e l c o m e  t o      ║&N")
    cprint("&+W║      R i v e r m o o r       ║&N")
    cprint("&+W╚══════════════════════════════╝&N\n")

    while True:
        name_raw = input("Who would you like to be known as? ").strip()
        if not name_raw:
            continue
        # Capitalise first letter, lowercase the rest
        name = name_raw[0].upper() + name_raw[1:].lower()

        if not _char_exists(conn, name):
            # ── New character ─────────────────────────────────────────────
            cprint(f"\n&wThat character does not exist.&N")
            cprint(f"&wWould you like to create &W{name}&w now?&N")
            answer = input("(yes/no) > ").strip().lower()
            if answer not in ("yes", "y"):
                cprint("&wVery well. Enter another name.&N\n")
                continue

            char = _make_new_warrior(name, races)
            save_character(conn, char, location=start_room, include_hp=True)

            state.characters[name]  = char
            state.locations[name]   = start_room
            state.player            = name

            cprint(f"\n&+WCharacter &N{name}&+W has been created!&N")
            cprint("&wYou are a level &W1&w Human Warrior.&N")
            cprint("&x(STR 90 / DEX 90 / CON 90 / INT 70 / WIS 70 / CHA 70)&N\n")
            break

        else:
            # ── Existing character ────────────────────────────────────────
            row = conn.execute(
                "SELECT race, class, level FROM characters WHERE name = ?",
                (name,),
            ).fetchone()

            char      = _make_shell_char(name, row, races)
            saved_room = load_character(conn, name, char)
            room_vnum  = saved_room if saved_room else start_room

            state.characters[name] = char
            state.locations[name]  = room_vnum
            state.player           = name

            cprint(f"\n&+WWelcome back, &N{name}&+W!&N")
            cprint(f"&x(Level {char.level} {char.race} {char.cclass})&N\n")
            break

    # Store the connection on state so GameState can use it for saves
    state._db = conn


def auto_crepl(
    state,
    prompt:    str   = "&g> &N",
    quit_cmds: tuple = ("quit", "exit", "q"),
    banner:    str   = "",
    farewell:  str   = "",
) -> None:
    """
    Drop-in replacement for crepl() with automatic combat ticks.

    While state.fighting is set:
      • An auto-attack round fires every TICK_INTERVAL seconds.
      • Powers fire immediately when typed, subject to their cooldown.
      • Movement is blocked (use 'flee' to escape).

    Outside combat the loop behaves like a normal REPL with no extra output.
    """
    if banner:
        cprint(banner)

    base_prompt = diku_to_ansi(prompt)

    def _build_prompt() -> str:
        """Show HP in the prompt while in combat."""
        if state.fighting:
            char = state.characters.get(state.player)
            if char:
                hp  = getattr(char, "hp",     "?")
                mhp = getattr(char, "max_hp",  "?")
                return diku_to_ansi(f"&w[&W{hp}&w/&W{mhp}&whp] &g>&N ")
        return base_prompt

    last_tick = time.monotonic()

    # Show the initial prompt once.
    sys.stdout.write(_build_prompt())
    sys.stdout.flush()

    while True:
        now          = time.monotonic()
        time_to_tick = max(0.05, TICK_INTERVAL - (now - last_tick))

        # Wait for input up to time_to_tick seconds.
        try:
            ready, _, _ = select.select([sys.stdin], [], [], time_to_tick)
        except (KeyboardInterrupt, EOFError):
            break

        # Track whether we have anything to show so we know whether to
        # reprint the prompt at the bottom of this iteration.
        need_prompt = False

        # ── Player typed something ────────────────────────────────────────
        if ready:
            try:
                raw = sys.stdin.readline()
            except (KeyboardInterrupt, EOFError):
                break

            if not raw:   # EOF — Ctrl-D
                break

            raw = raw.strip()

            if raw:
                if raw.lower() in quit_cmds:
                    break

                result = state.handle(raw)

                if result == "quit":
                    break

                sys.stdout.write("\n")
                if result:
                    cprint(result)
            else:
                # Player pressed Enter on a blank line — just drop to a
                # new line and give them a fresh prompt.
                sys.stdout.write("\n")

            # Always show a prompt after the player types something.
            need_prompt = True

        # ── Tick check ────────────────────────────────────────────────────
        now = time.monotonic()
        if (now - last_tick) >= TICK_INTERVAL:
            last_tick += TICK_INTERVAL   # advance by one interval, no drift

            if state.fighting:
                # Clear the current input line so output prints cleanly.
                sys.stdout.write("\r\033[K")
                output = state.combat_tick()
                if output:
                    cprint(output)
                    # Show a fresh prompt after combat output.
                    need_prompt = True

        # ── Reprint prompt only when needed ──────────────────────────────
        if need_prompt:
            sys.stdout.write(_build_prompt())
            sys.stdout.flush()

    if farewell:
        cprint(farewell)
