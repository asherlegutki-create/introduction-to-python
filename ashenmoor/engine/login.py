"""
ashenmoor.engine.login
───────────────────────
Shared account and character selection flow.

Both the network client (net/client.py) and local console (engine/ticker.py)
call run_login_flow().  The caller provides two async-compatible callables:

    send(text)   — display text to the player (no newline added)
    recv()       — await a line of input, returns stripped string

The flow:
  1. Enter account name  (validated [A-Za-z0-9_-])
  2. New account: choose password + confirm, optional email
     Existing account: enter password
  3. Character selection screen
  4. Choose character by number/name, create new, delete, change password,
     change email, or quit

Returns a (char, account_id, room_vnum) tuple on success, or None on quit/error.
"""

from __future__ import annotations
import time

from ashenmoor.colors import C, class_display, char_list_race

_SEP  = f"{C.SEP}-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-{C.RESET}"
_SEP2 = f"{C.SEP}-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-{C.RESET}"

# Width for character name column
_NAME_WIDTH = 28


def _char_list_line(idx: int, row) -> str:
    """Format one character list entry."""
    name     = row["name"]
    level    = row["level"]
    cclass   = row["class"]
    race     = row["race"]
    subclass = row.get("subclass") if isinstance(row, dict) else None

    # Try to get subclass from a joined query result
    if subclass is None:
        try:
            subclass = row["subclass"]
        except (KeyError, IndexError):
            subclass = None

    padded      = name.ljust(_NAME_WIDTH)
    class_str   = class_display(cclass, subclass)
    race_str    = char_list_race(race)

    return (
        f"  {C.NUMBER}{idx}){C.RESET} "
        f"{C.NAME}{padded}{C.RESET} "
        f"{C.LABEL}Level {C.VALUE}{level} "
        f"{class_str} {race_str}"
    )


async def run_login_flow(
    state,
    conn,
    send,
    recv,
    start_room: int,
    races:      dict,
) -> tuple | None:
    """
    Run the full account + character selection flow.

    Returns (char, account_id, room_vnum) on success.
    Returns None if the player quits or the connection drops.
    """
    from ..engine.persist import (
        account_exists, create_account, get_account,
        get_account_characters, verify_password,
        set_password, set_email, delete_character,
        valid_account_name, valid_char_name,
        save_character, load_character,
    )

    await send(
        "\r\n"
        "\033[1;37m╔══════════════════════════════╗\033[0m\r\n"
        "\033[1;37m║      W e l c o m e  t o      ║\033[0m\r\n"
        "\033[1;37m║      R i v e r m o o r       ║\033[0m\r\n"
        "\033[1;37m╚══════════════════════════════╝\033[0m\r\n\r\n"
    )

    from ..color import diku_to_ansi

    # ── Step 1: Account name ──────────────────────────────────────────────
    account = None
    account_id = None

    while account is None:
        await send("Account name (or 'new' to create one, 'quit' to exit): ")
        try:
            raw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None

        if not raw:
            continue

        if raw.lower() == "quit":
            await send("Goodbye!\r\n")
            return None

        if not valid_account_name(raw):
            await send(diku_to_ansi(
                f"{C.ERR}Account names may only contain letters, numbers, "
                f"underscores, and dashes.{C.RESET}\r\n"
            ))
            continue

        if raw.lower() == "new":
            result = await _create_account_flow(send, recv, conn)
            if result is None:
                return None
            account    = result
            account_id = account["id"]
        elif account_exists(conn, raw):
            account = get_account(conn, raw)
            await send(diku_to_ansi(f"{C.LABEL}Password: {C.RESET}"))
            try:
                pw = (await recv()).strip()
            except (EOFError, ConnectionResetError):
                return None
            if not verify_password(conn, raw, pw):
                await send(diku_to_ansi(f"{C.ERR}Incorrect password.{C.RESET}\r\n"))
                account = None
                continue
            account_id = account["id"]
            await send(diku_to_ansi(
                f"\r\n{C.HEADER}Welcome back, {C.NAME}{account['name']}{C.HEADER}!{C.RESET}\r\n\r\n"
            ))
        else:
            await send(diku_to_ansi(
                f"{C.LABEL}No account named '{C.NAME}{raw}{C.LABEL}' exists.\r\n"
                f"Type {C.VALUE}new{C.LABEL} to create one, "
                f"or try a different name.{C.RESET}\r\n"
            ))

    # ── Step 2: Character selection loop ──────────────────────────────────
    while True:
        chars = get_account_characters(conn, account_id)
        result = await _character_menu(
            send, recv, conn, state, account, account_id,
            chars, start_room, races,
        )
        if result is None:
            return None
        if result == "refresh":
            continue
        return result   # (char, account_id, room_vnum)


# ── Account creation ──────────────────────────────────────────────────────────

async def _create_account_flow(send, recv, conn):
    from ..engine.persist import (
        account_exists, create_account, get_account, valid_account_name,
    )
    from ..color import diku_to_ansi

    await send(diku_to_ansi(f"\r\n{C.HEADER}Create a new account{C.RESET}\r\n"))

    while True:
        await send(diku_to_ansi(
            f"{C.LABEL}Choose an account name {C.DIM}[A-Za-z0-9_-]{C.LABEL}: {C.RESET}"
        ))
        try:
            name = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None

        if not name:
            continue
        if name.lower() == "quit":
            return None
        if not valid_account_name(name):
            await send(diku_to_ansi(
                f"{C.ERR}Account names may only contain letters, numbers, "
                f"underscores, and dashes.{C.RESET}\r\n"
            ))
            continue
        if account_exists(conn, name):
            await send(diku_to_ansi(f"{C.ERR}That account name is already taken.{C.RESET}\r\n"))
            continue
        break

    while True:
        await send(diku_to_ansi(f"{C.LABEL}Choose a password: {C.RESET}"))
        try:
            pw1 = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        if not pw1:
            await send(diku_to_ansi(f"{C.ERR}Password cannot be empty.{C.RESET}\r\n"))
            continue
        await send(diku_to_ansi(f"{C.LABEL}Confirm password: {C.RESET}"))
        try:
            pw2 = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        if pw1 != pw2:
            await send(diku_to_ansi(f"{C.ERR}Passwords do not match. Try again.{C.RESET}\r\n"))
            continue
        break

    await send(diku_to_ansi(
        f"{C.LABEL}Email address {C.DIM}(optional, press Enter to skip){C.LABEL}: {C.RESET}"
    ))
    try:
        email_raw = (await recv()).strip()
    except (EOFError, ConnectionResetError):
        return None
    email = email_raw if email_raw else None

    account_id = create_account(conn, name, pw1, email)
    account    = get_account(conn, name)
    await send(diku_to_ansi(
        f"\r\n{C.OK}Account '{C.NAME}{name}{C.OK}' created!{C.RESET}\r\n"
        f"{C.LABEL}You can now create your first character.{C.RESET}\r\n\r\n"
    ))
    return account


# ── Character menu ────────────────────────────────────────────────────────────

async def _character_menu(send, recv, conn, state, account,
                          account_id, chars, start_room, races):
    from ..engine.persist import (
        verify_password, delete_character, set_password, set_email,
        load_character, save_character,
    )
    from ..color import diku_to_ansi

    # Build and send the character list
    await send(diku_to_ansi(f"\r\n{C.HEADER}Characters:{C.RESET}\r\n"))
    await send(diku_to_ansi(_SEP + "\r\n"))

    if chars:
        for i, row in enumerate(chars, 1):
            await send(diku_to_ansi(_char_list_line(i, row) + "\r\n"))
    else:
        await send(diku_to_ansi(f"  {C.DIM}No characters yet.{C.RESET}\r\n"))

    await send(diku_to_ansi(_SEP2 + "\r\n"))
    await send(diku_to_ansi(
        f"{C.PLAIN}Type the # or name of a character above to login "
        f"or choose an action below.{C.RESET}\r\n"
    ))
    await send(diku_to_ansi(_SEP2 + "\r\n"))
    await send(diku_to_ansi(
        f"{C.SEP}({C.PLAIN}N{C.SEP}){C.PLAIN}ew character {C.SEP}|{C.RESET} "
        f"{C.SEP}({C.PLAIN}D{C.SEP}){C.PLAIN}elete character {C.SEP}|{C.RESET} "
        f"{C.SEP}({C.PLAIN}C{C.SEP}){C.PLAIN}hange password\r\n"
        f"{C.SEP}({C.PLAIN}M{C.SEP}){C.PLAIN}odify email address {C.SEP}|{C.RESET} "
        f"{C.SEP}({C.PLAIN}Q{C.SEP}){C.PLAIN}uit{C.RESET}\r\n"
    ))
    await send(diku_to_ansi(_SEP2 + "\r\n"))
    await send(diku_to_ansi(f"{C.SEP}>{C.RESET} "))

    try:
        raw = (await recv()).strip()
    except (EOFError, ConnectionResetError):
        return None

    choice = raw.lower()

    # ── Quit ──────────────────────────────────────────────────────────────
    if choice in ("q", "quit"):
        await send("Goodbye!\r\n")
        return None

    # ── New character ─────────────────────────────────────────────────────
    if choice in ("n", "new"):
        result = await _create_character_flow(
            send, recv, conn, state, account_id, start_room, races
        )
        if result is not None:
            return result
        return "refresh"

    # ── Delete character ──────────────────────────────────────────────────
    if choice in ("d", "delete"):
        if not chars:
            await send("&wYou have no characters to delete.&N\r\n")
            return "refresh"
        await send("Enter the name of the character to delete: ")
        try:
            del_name = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None

        # Verify it belongs to this account
        match = next(
            (r for r in chars if r["name"].lower() == del_name.lower()), None
        )
        if match is None:
            await send(f"&RNo character named '{del_name}' on this account.&N\r\n")
            return "refresh"

        await send(
            f"&RThis will permanently delete &W{match['name']}&R. "
            f"Enter your account password to confirm: &N"
        )
        try:
            pw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None

        if not verify_password(conn, account["name"], pw):
            await send("&RIncorrect password. Deletion cancelled.&N\r\n")
            return "refresh"

        # Remove from live state if somehow logged in
        state.characters.pop(match["name"], None)
        state.locations.pop(match["name"],  None)
        state.fighting.pop(match["name"],   None)
        delete_character(conn, match["name"])
        await send(f"&wCharacter &W{match['name']}&w has been deleted.&N\r\n")
        return "refresh"

    # ── Change password ───────────────────────────────────────────────────
    if choice in ("c", "change password"):
        await send("Current password: ")
        try:
            old_pw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        if not verify_password(conn, account["name"], old_pw):
            await send("&RIncorrect password.&N\r\n")
            return "refresh"

        while True:
            await send("New password: ")
            try:
                new1 = (await recv()).strip()
            except (EOFError, ConnectionResetError):
                return None
            if not new1:
                await send("&RPassword cannot be empty.&N\r\n")
                continue
            await send("Confirm new password: ")
            try:
                new2 = (await recv()).strip()
            except (EOFError, ConnectionResetError):
                return None
            if new1 != new2:
                await send("&RPasswords do not match.&N\r\n")
                continue
            break

        set_password(conn, account["name"], new1)
        await send("&GPassword changed successfully.&N\r\n")
        return "refresh"

    # ── Modify email ──────────────────────────────────────────────────────
    if choice in ("m", "modify email"):
        current = account["email"] or "(none)"
        await send(f"Current email: {current}\r\n")
        await send("New email address (or Enter to clear): ")
        try:
            new_email = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        set_email(conn, account["name"], new_email or None)
        await send("&GEmail updated.&N\r\n")
        return "refresh"

    # ── Select character by number ────────────────────────────────────────
    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(chars):
            return await _enter_world(
                send, recv, conn, state, chars[idx - 1]["name"],
                account_id, start_room, races,
            )
        await send("&RInvalid number.&N\r\n")
        return "refresh"

    # ── Select character by name ──────────────────────────────────────────
    match = next(
        (r for r in chars if r["name"].lower() == choice), None
    )
    if match:
        return await _enter_world(
            send, recv, conn, state, match["name"],
            account_id, start_room, races,
        )

    await send("&RUnrecognised choice. Try a number, character name, or menu option.&N\r\n")
    return "refresh"


# ── Character creation ────────────────────────────────────────────────────────

async def _create_character_flow(send, recv, conn, state,
                                  account_id, start_room, races):
    from ..engine.persist   import valid_char_name, save_character, load_character
    from ..core.character   import Character
    from ..dnd.classes.fighter import (
        new_fighter_dnd, FIGHTER_POWERS, FIGHTING_STYLES,
    )
    from ..color import diku_to_ansi

    await send(diku_to_ansi(f"\r\n{C.HEADER}Create a new character{C.RESET}\r\n"))

    # ── Name ──────────────────────────────────────────────────────────────
    while True:
        await send(diku_to_ansi(
            f"{C.LABEL}Character name {C.DIM}[A-Za-z only]{C.LABEL}: {C.RESET}"
        ))
        try:
            name_raw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None

        if not name_raw:
            continue
        if name_raw.lower() == "back":
            return None
        if not valid_char_name(name_raw):
            await send(diku_to_ansi(
                f"{C.ERR}Character names may only contain letters "
                f"(no numbers or symbols).{C.RESET}\r\n"
            ))
            continue

        name = name_raw[0].upper() + name_raw[1:].lower()
        existing = conn.execute(
            "SELECT 1 FROM characters WHERE name=?", (name,)
        ).fetchone()
        if existing:
            await send(diku_to_ansi(
                f"{C.ERR}The name '{name}' is already taken.{C.RESET}\r\n"
            ))
            continue
        break

    # ── Sex ───────────────────────────────────────────────────────────────
    sex = "male"
    while True:
        await send(diku_to_ansi(
            f"{C.LABEL}Are you Male or Female {C.PAREN}(M/F){C.LABEL}? {C.RESET}"
        ))
        try:
            s = (await recv()).strip().lower()
        except (EOFError, ConnectionResetError):
            return None
        if s in ("m", "male"):
            sex = "male"; break
        elif s in ("f", "female"):
            sex = "female"; break
        else:
            await send(diku_to_ansi(f"{C.ERR}Please enter M or F.{C.RESET}\r\n"))

    # ── Race ──────────────────────────────────────────────────────────────
    from ashenmoor.colors import race_color
    race_list  = list(races.keys())
    race_descs = _race_descriptions()

    await send(diku_to_ansi(f"\r\n{C.HEADER}Choose your race:{C.RESET}\r\n"))
    await send(diku_to_ansi(_SEP + "\r\n"))
    for i, rname in enumerate(race_list, 1):
        desc  = race_descs.get(rname, "A playable race.")
        rcode = race_color(rname)
        await send(diku_to_ansi(
            f"  {C.NUMBER}{i}){C.RESET} {rcode}{rname}{C.RESET}\r\n"
            f"     {C.LABEL}{desc}{C.RESET}\r\n"
        ))
    await send(diku_to_ansi(_SEP + "\r\n"))

    chosen_race = None
    while chosen_race is None:
        await send(diku_to_ansi(f"{C.LABEL}Enter race number or name: {C.RESET}"))
        try:
            raw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(race_list):
                chosen_race = race_list[idx - 1]
            else:
                await send(diku_to_ansi(f"{C.ERR}Invalid number.{C.RESET}\r\n"))
        else:
            match = next(
                (r for r in race_list if r.lower() == raw.lower()), None
            )
            if match:
                chosen_race = match
            else:
                await send(diku_to_ansi(
                    f"{C.ERR}Unknown race. Enter a number or the race name.{C.RESET}\r\n"
                ))

    # ── Fighting style ────────────────────────────────────────────────────
    style_list = list(FIGHTING_STYLES.keys())

    await send(diku_to_ansi(f"\r\n{C.HEADER}Choose your fighting style:{C.RESET}\r\n"))
    await send(diku_to_ansi(_SEP + "\r\n"))
    for i, sname in enumerate(style_list, 1):
        desc  = FIGHTING_STYLES[sname]
        label = sname.replace("_", " ").title()
        await send(diku_to_ansi(
            f"  {C.NUMBER}{i}){C.RESET} {C.VALUE}{label}{C.RESET}\r\n"
            f"     {C.LABEL}{desc}{C.RESET}\r\n"
        ))
    await send(diku_to_ansi(_SEP + "\r\n"))
    await send(diku_to_ansi(
        f"{C.DIM}You start with 3 style-change charges. "
        f"Gain 1 per level (max 3).\r\n"
        f"Use 'style choose <style>' after a long rest to change.{C.RESET}\r\n"
    ))

    chosen_style = None
    while chosen_style is None:
        await send(diku_to_ansi(
            f"{C.LABEL}Enter style number or name: {C.RESET}"
        ))
        try:
            raw = (await recv()).strip()
        except (EOFError, ConnectionResetError):
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(style_list):
                chosen_style = style_list[idx - 1]
            else:
                await send(diku_to_ansi(f"{C.ERR}Invalid number.{C.RESET}\r\n"))
        else:
            match = next(
                (s for s in style_list
                 if s.lower() == raw.lower().replace(" ", "_")),
                None,
            )
            if match:
                chosen_style = match
            else:
                await send(diku_to_ansi(
                    f"{C.ERR}Unknown style. Enter a number or the style name.{C.RESET}\r\n"
                ))

    # ── Build character ───────────────────────────────────────────────────
    dnd = new_fighter_dnd(level=1, fighting_style=chosen_style)
    dnd["style_change_charges"]  = 3
    dnd["style_change_max"]      = 3
    dnd["style_long_rest_ready"] = False

    char = Character({
        "name":      name,
        "race":      chosen_race,
        "class":     "Fighter",
        "level":     1,
        "stats":     [90, 90, 90, 70, 70, 70],
        "dnd":       dnd,
        "powers":    list(FIGHTER_POWERS),
        "alignment": "True Neutral",
        "position":  "standing",
        "sex":       sex,
    }, races=races)

    save_character(conn, char, location=start_room,
                   account_id=account_id, include_hp=True)

    state.characters[name] = char
    state.locations[name]  = start_room

    from ashenmoor.colors import class_display, char_list_race
    style_label = chosen_style.replace("_", " ").title()
    await send(diku_to_ansi(
        f"\r\n{C.OK}Character {C.NAME}{name}{C.OK} created!{C.RESET}\r\n"
        f"{C.LABEL}Level {C.VALUE}1{C.RESET} "
        f"{race_color(chosen_race)}{chosen_race}{C.RESET} "
        f"{class_display('Fighter')} "
        f"{C.DIM}— {style_label} style{C.RESET}\r\n\r\n"
    ))
    return (char, account_id, start_room)


# ── Enter world ───────────────────────────────────────────────────────────────

async def _enter_world(send, recv, conn, state, char_name,
                        account_id, start_room, races):
    from ..engine.persist      import load_character
    from ..core.character      import Character
    from ..dnd.classes.fighter import new_fighter_dnd, FIGHTER_POWERS

    row = conn.execute(
        "SELECT race, class, level FROM characters WHERE name=?",
        (char_name,),
    ).fetchone()
    if row is None:
        await send(f"&RCharacter '{char_name}' not found.&N\r\n")
        return "refresh"

    cclass = row["class"]
    level  = row["level"]

    d = {
        "name":  char_name,
        "race":  row["race"],
        "class": "Fighter" if cclass.lower() == "warrior" else cclass,
        "level": level,
        "stats": [75] * 6,
    }
    if d["class"].lower() in ("fighter", "warrior"):
        d["dnd"]    = new_fighter_dnd(level=level)
        d["powers"] = list(FIGHTER_POWERS)

    char      = Character(d, races=races)
    saved_loc = load_character(conn, char_name, char)
    room_vnum = saved_loc if saved_loc else start_room

    state.characters[char_name] = char
    state.locations[char_name]  = room_vnum

    return (char, account_id, room_vnum)


# ── Race descriptions ─────────────────────────────────────────────────────────

def _race_descriptions() -> dict[str, str]:
    """
    Plain-language descriptions of each race's strengths and weaknesses.
    Add entries here as new races are defined in RACES.
    """
    return {
        "Human": (
            "&wBalanced in all attributes — no strengths, no weaknesses.\n"
            "     The most adaptable race, excelling in any class.&N"
        ),
        "Dwarf": (
            "&wBurly and incredibly tough. Exceptional constitution makes\n"
            "     Dwarves hard to kill. A bit slow-witted and gruff in company,\n"
            "     but their endurance is second to none.&N"
        ),
        "Grey Elf": (
            "&wSupernaturally quick and deeply intelligent. Fragile compared\n"
            "     to other races but unmatched in dexterity and arcane insight.\n"
            "     Poor choice for front-line fighters; excellent for rogues and mages.&N"
        ),
        "Ogre": (
            "&wMonstrous strength and near-indestructible constitution. Ogres\n"
            "     hit like siege weapons and shrug off punishment. Extremely dim,\n"
            "     slow, and poor in social situations. Not for beginners.&N"
        ),
    }
