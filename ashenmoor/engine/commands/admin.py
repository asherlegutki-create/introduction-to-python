"""
ashenmoor.engine.commands.admin
────────────────────────────────
Admin / wiz commands and game-time display.
"""

from __future__ import annotations


def cmd_time(state) -> str:
    return state.game_time.full_display()


def cmd_wiz(state, args: list) -> str:
    from ...world.effects import EFFECTS, apply_effect, remove_effect, recalc_status, format_effects

    if not args:
        return (
            "&wWiz commands:&N\n"
            "  &Wwiz goto &w<vnum>&N\n"
            "  &Wwiz xp &w<player> <amount>&N\n"
            "  &Wwiz apply_effect &w<id> [player]&N\n"
            "  &Wwiz remove_effect &w<id> [player]&N\n"
            "  &Wwiz clear_effects &w[player]&N\n"
            "  &Wwiz list_effects&N\n"
            "  &Wwiz effects &w[player]&N\n"
            "  &Wwiz heal &w[player]&N\n"
            "  &Wwiz poison &w[player]&N\n"
            "  &Wwiz change_sex &w[male|m|female|f] <player>&N\n"
            "  &Wwiz account list&N\n"
            "  &Wwiz account info &w<account>&N\n"
            "  &Wwiz account resetpassword &w<account>&N"
        )

    sub  = args[0].lower()
    rest = args[1:]

    def _get_target(name_args):
        if name_args:
            tname = name_args[0].lower()
            for pname, ch in state.characters.items():
                if pname.lower() == tname:
                    return ch, pname
            return None, tname
        return state.characters.get(state._player), state._player

    if sub == "goto":
        if not rest:
            return "&wUsage: wiz goto <vnum>&N"
        try:
            vnum = int(rest[0])
        except ValueError:
            return f"&w'{rest[0]}' is not a valid vnum.&N"
        if vnum not in state.rooms:
            return f"&wNo room with vnum &W{vnum}&w exists.&N"
        state.locations[state._player] = vnum
        state._save_location()
        from .movement import cmd_look, check_aggro
        parts = [cmd_look(state, [])]
        aggro = check_aggro(state)
        if aggro:
            parts.append(aggro)
        return "\n".join(parts)

    if sub == "xp":
        if len(rest) < 2:
            return "&wUsage: wiz xp <player> <amount>&N"
        tname = rest[0].lower()
        try:
            amount = int(rest[1])
        except ValueError:
            return f"&w'{rest[1]}' is not a valid number.&N"
        char = next(
            (ch for pn, ch in state.characters.items() if pn.lower() == tname),
            None,
        )
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        from ...dnd.xp import level_for_xp, apply_level_up, MAX_LEVEL
        old_level = char.level
        char.xp   = getattr(char, "xp", 0) + amount
        msgs      = [f"&W{char.name}&w receives &W{amount:,}&w experience points.&N"]
        msgs.extend(apply_level_up(char))
        if char.level != old_level:
            msgs.append(
                f"&W{char.name}&w advances from level &W{old_level}&w to level &W{char.level}&w!&N"
            )
        _, pct = level_for_xp(char.xp)
        msgs.append(
            f"&wTotal XP: &W{char.xp:,}&w  Level: &W{char.level}&w  Progress: &W{pct}&w%&N"
        )
        state._save_player()
        return "\n".join(msgs)

    if sub == "list_effects":
        lines = ["&wAvailable effect ids:&N"]
        for eid, eff in EFFECTS.items():
            lines.append(f"  &c{eid:<20}&N {eff.get('name','')}")
        return "\n".join(lines)

    if sub in ("apply_effect", "ae"):
        if not rest:
            return "&wUsage: wiz apply_effect <effect_id> [player]&N"
        eid         = rest[0].lower()
        char, tname = _get_target(rest[1:])
        if eid not in EFFECTS:
            return f"&wUnknown effect &W{eid}&w. Use &Wwiz list_effects&w to see options.&N"
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        import copy
        msg = apply_effect(char, copy.deepcopy(EFFECTS[eid]))
        return f"&wApplied &W{eid}&w to &W{tname}&w.&N\n{msg}"

    if sub in ("remove_effect", "re"):
        if not rest:
            return "&wUsage: wiz remove_effect <effect_id> [player]&N"
        eid         = rest[0].lower()
        char, tname = _get_target(rest[1:])
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        msg = remove_effect(char, eid)
        if msg is None:
            return f"&W{tname}&w does not have effect &W{eid}&w.&N"
        return f"&wRemoved &W{eid}&w from &W{tname}&w.&N\n{msg}"

    if sub in ("clear_effects", "ce"):
        char, tname = _get_target(rest)
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        char.status_effects = []
        recalc_status(char)
        return f"&wAll effects cleared from &W{tname}&w.&N"

    if sub in ("effects", "fx"):
        char, tname = _get_target(rest)
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        block = format_effects(char)
        return block if block else f"&W{tname}&w has no active effects.&N"

    if sub == "heal":
        char, tname = _get_target(rest)
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        char.hp = char.max_hp
        return f"&W{tname}&w restored to full hp (&W{char.max_hp}&w).&N"

    if sub == "poison":
        char, tname = _get_target(rest)
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        import copy
        msg = apply_effect(char, copy.deepcopy(EFFECTS["poisoned"]))
        return f"&wPoisoned &W{tname}&w.&N\n{msg}"

    if sub in ("change_sex", "sex"):
        if not rest:
            return "&wUsage: &Wwiz change_sex &w[male|m|female|f] <player>&N"
        sex_arg  = rest[0].lower()
        name_arg = rest[1:]
        if sex_arg in ("m", "male"):
            new_sex = "male"
        elif sex_arg in ("f", "female"):
            new_sex = "female"
        else:
            return f"&wUnknown sex '&W{sex_arg}&w'. Use &Wmale&w/&Wm&w or &Wfemale&w/&Wf&w.&N"
        char, tname = _get_target(name_arg)
        if char is None:
            return f"&wPlayer &W{tname}&w not found.&N"
        char.sex = new_sex
        state._save_player()
        return f"&W{tname}&w is now &W{new_sex}&w.&N"

    if sub == "account":
        return _cmd_wiz_account(state, rest)

    return f"&wUnknown wiz subcommand &W{sub}&w. Type &Wwiz&w for help.&N"


def _cmd_wiz_account(state, args: list) -> str:
    """Wiz account management subcommands."""
    if not args:
        return (
            "&wWiz account commands:&N\n"
            "  &Wwiz account list&N\n"
            "  &Wwiz account info &w<account>&N\n"
            "  &Wwiz account resetpassword &w<account>&N"
        )

    if state._db is None:
        return "&RDatabase not available.&N"

    from ...engine.persist import (
        wiz_list_accounts, wiz_account_info, wiz_reset_password,
    )
    import time as _t

    sub = args[0].lower()

    if sub == "list":
        rows = wiz_list_accounts(state._db)
        if not rows:
            return "&wNo accounts found.&N"
        lines = [
            f"&W{'Account':<20} {'Email':<28} {'Chars':>5} {'Created'}&N",
            "&w" + "─" * 64 + "&N",
        ]
        for r in rows:
            created = _t.strftime("%Y-%m-%d", _t.localtime(r["created_at"]))
            email   = (r["email"] or "—")[:26]
            lines.append(
                f"{r['name']:<20} {email:<28} {r['char_count']:>5}  {created}"
            )
        return "\n".join(lines)

    if sub == "info":
        if len(args) < 2:
            return "&wUsage: wiz account info <account>&N"
        info = wiz_account_info(state._db, args[1])
        if info is None:
            return f"&wAccount '&W{args[1]}&w' not found.&N"
        acc   = info["account"]
        chars = info["characters"]
        lines = [
            f"&+WAccount: &N{acc['name']}&N",
            f"&wEmail:   &N{acc['email'] or '(none)'}&N",
            f"&wCreated: &N{_t.strftime('%Y-%m-%d %H:%M', _t.localtime(acc['created_at']))}&N",
            "",
            f"&wCharacters ({len(chars)}):&N",
        ]
        for i, c in enumerate(chars, 1):
            lines.append(
                f"  {i}) {c['name']:<28} Level {c['level']} {c['class']} ({c['race']})"
            )
        return "\n".join(lines)

    if sub == "resetpassword":
        if len(args) < 2:
            return "&wUsage: wiz account resetpassword <account>&N"
        temp_pw = wiz_reset_password(state._db, args[1])
        if temp_pw is None:
            return f"&wAccount '&W{args[1]}&w' not found.&N"
        return (
            f"&wPassword for &W{args[1]}&w has been reset.\n"
            f"Temporary password: &W{temp_pw}&N\n"
            f"&xRelay this to the player. Email delivery coming soon.&N"
        )

    return f"&wUnknown account subcommand '&W{sub}&w'. Type &Wwiz account&w for help.&N"
