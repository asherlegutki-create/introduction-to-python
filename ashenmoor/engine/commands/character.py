"""
ashenmoor.engine.commands.character
─────────────────────────────────────
Character info commands: score, attributes, wimpy, position, powers, who, scan.
"""

from __future__ import annotations
import time as _time

from .helpers import max_inventory


def cmd_score(state) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...dnd.xp      import level_for_xp, XP_TABLE, MAX_LEVEL
    from ...world.effects import format_effects

    xp            = getattr(char, "xp", 0)
    level, xp_pct = level_for_xp(xp)
    if level != char.level and level <= MAX_LEVEL:
        char.level = level

    hp     = getattr(char, "hp",        char.max_hp)
    mhp    = getattr(char, "max_hp",    1)
    moves  = getattr(char, "moves",     100)
    mmoves = getattr(char, "max_moves", 100)

    def _coin_line(label, c):
        return (
            f"&w{label}&N&W{c.get('gold',0):>6}&w gold  "
            f"&W{c.get('silver',0):>6}&w silver  &W{c.get('copper',0):>6}&w copper&N"
        )

    coins      = getattr(char, "coins",      {"gold": 0, "silver": 0, "copper": 0})
    bank_coins = getattr(char, "bank_coins", {"gold": 0, "silver": 0, "copper": 0})

    total_secs = getattr(char, "play_time_seconds", 0) + int(_time.time() - state._session_start)
    days  = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    mins  = (total_secs % 3600) // 60

    detect  = "  ".join(getattr(char, "detect_flags",  []))
    protect = "  ".join(getattr(char, "protect_flags", []))
    enchant = "  ".join(getattr(char, "enchant_flags", []))

    resting  = state._resting.get(state._player)
    rest_str = ""
    if resting:
        t = resting["ticks"]
        if t < 4:
            rest_str = f"\n&wResting:&N  &W{4-t}&w tick{'s' if 4-t!=1 else ''} to short-rest abilities&N"
        elif t < 8:
            rest_str = f"\n&wResting:&N  &W{8-t}&w tick{'s' if 8-t!=1 else ''} to long-rest abilities&N"
        else:
            rest_str = "\n&wResting:&N  fully rested (type &Wstand&w to stop)&N"

    lines = [
        f"&+WScore information for &N{char.name}\n",
        f"&wLevel:&N {level:<5} &wRace:&N {char.race:<10} &wSex:&N {getattr(char,'sex','male').capitalize():<8} &wClass:&N {char.cclass}",
        f"&wHit points:&N &W{hp}&w(&W{mhp}&w)  &wMoves:&N &W{moves}&w(&W{mmoves}&w)",
        f"&wExperience Progress:&N &W{xp_pct}&w %  &x({xp:,} / {XP_TABLE.get(level+1, xp):,} xp)&N",
        _coin_line("Coins carried:   ", coins),
        _coin_line("Coins in bank:   ", bank_coins),
        f"&wPlaying time:&N {days} days / {hours} hours / {mins} minutes",
        f"&wTitle:&N {getattr(char,'title','')}",
        f"&wStatus:&N  {getattr(char,'position','standing').capitalize()}.",
        f"&wDetecting:&N       {detect}",
        f"&wProtected from:&N  {protect}",
        f"&wEnchantments:&N    {enchant}",
    ]
    if rest_str:
        lines.append(rest_str)

    effect_block = format_effects(char)
    if effect_block:
        lines.append("")
        lines.append(effect_block)

    return "\n".join(lines)


def cmd_attributes(state) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ...dnd.abilities import char_modifier, proficiency_bonus, saving_throw
    from ...dnd.armor     import get_ac

    str_eff = char.computed_stat("str")
    dex_eff = char.computed_stat("dex")
    con_eff = char.computed_stat("con")
    int_eff = char.computed_stat("int")
    wis_eff = char.computed_stat("wis")
    cha_eff = char.computed_stat("cha")
    str_mod = char_modifier(char, "str")

    equip_hit  = 0
    equip_dam  = 0
    equip_save: dict[str, int] = {}
    for item in char.equipment.values():
        if item is None:
            continue
        equip_hit += getattr(item, "hitroll", 0)
        equip_dam += getattr(item, "damroll", 0)
        for k, v in getattr(item, "save_mods", {}).items():
            equip_save[k] = equip_save.get(k, 0) + v

    prof    = proficiency_bonus(char.level)
    hitroll = str_mod + prof + equip_hit
    damroll = str_mod + equip_dam
    ac      = get_ac(char)

    def _sv(n): return f"+{n}" if n > 0 else str(n)

    effect_save: dict[str, int] = {}
    for eff in getattr(char, "active_effects", []):
        for k, v in eff.get("save_mods", {}).items():
            effect_save[k] = effect_save.get(k, 0) + v

    par = saving_throw(char, "par", equip_bonus=equip_save.get("par", 0), effect_bonus=effect_save.get("par", 0))
    rod = saving_throw(char, "rod", equip_bonus=equip_save.get("rod", 0), effect_bonus=effect_save.get("rod", 0))
    pet = saving_throw(char, "pet", equip_bonus=equip_save.get("pet", 0), effect_bonus=effect_save.get("pet", 0))
    bre = saving_throw(char, "bre", equip_bonus=equip_save.get("bre", 0), effect_bonus=effect_save.get("bre", 0))
    spe = saving_throw(char, "spe", equip_bonus=equip_save.get("spe", 0), effect_bonus=effect_save.get("spe", 0))

    race_obj  = char._races.get(char.race)
    size      = getattr(race_obj, "size", "Medium") if race_obj else "Medium"
    wimpy     = getattr(char, "wimpy", None)
    wimpy_str = f"&W{wimpy}&w hp&N" if wimpy else "not set"

    inv_weight = sum(getattr(i, "weight", 0) for i in char.inventory)
    max_weight = max(1, str_eff * 2)
    inv_items  = len(char.inventory)
    max_items  = max_inventory(char)
    load_pct   = max(inv_weight / max_weight * 100, inv_items / max_items * 100)

    if   load_pct <= 25:  lc, lm = "&+G", "Not a problem"
    elif load_pct <= 50:  lc, lm = "&G",  "Light"
    elif load_pct <= 75:  lc, lm = "&Y",  "Moderate"
    elif load_pct <= 90:  lc, lm = "&+Y", "Heavy"
    elif load_pct <= 100: lc, lm = "&+R", "Staggering"
    else:                 lc, lm = "&+R", "OVERLOADED!"

    return "\n".join([
        f"&+WCharacter attributes for &N{char.name}\n",
        f"&wLevel:&N {char.level:<5} &wRace:&N {char.race:<10} &wSex:&N {getattr(char,'sex','male').capitalize():<8} &wClass:&N {char.cclass}",
        f"&wSize:&N {size}",
        f"&wSTR:&N {str_eff:>4}  &wDEX:&N {dex_eff:>4}  &wCON:&N {con_eff:>4}",
        f"&wINT:&N {int_eff:>4}  &wWIS:&N {wis_eff:>4}  &wCHA:&N {cha_eff:>4}",
        f"&wArmor Class:&N {ac}",
        f"&wHitroll:&N {hitroll:+d}   &wDamroll:&N {damroll:+d}",
        f"&wAlignment:&N {getattr(char,'alignment','True Neutral')}",
        f"&wSaving Throws:&N PAR[{_sv(par)}]  ROD[{_sv(rod)}]  PET[{_sv(pet)}]  BRE[{_sv(bre)}]  SPE[{_sv(spe)}]",
        f"   &wWimpy:&N {wimpy_str}",
        f"&wLoad carried:&N {lc}{lm}&N  &x({inv_weight:.1f}/{max_weight:.0f} lbs | {inv_items}/{max_items} items)&N",
    ])


def cmd_wimpy(state, args: list) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    if not args:
        w = getattr(char, "wimpy", None)
        return (
            f"&wYou will flee combat when your HP drops to &W{w}&w.&N"
            if w else
            "&wWimpy is not set. You will fight to the last breath.&N"
        )
    val = args[0].lower()
    if val in ("off", "0", "none", "clear"):
        char.wimpy = None
        return "&wWimpy cleared. You will fight to the last breath.&N"
    try:
        hp = int(val)
    except ValueError:
        return "&wUsage: &Wwimpy <hp>&w  or  &Wwimpy off&N"
    if hp <= 0:
        char.wimpy = None
        return "&wWimpy cleared.&N"
    if hp >= char.max_hp:
        return f"&wWimpy must be less than your max HP (&W{char.max_hp}&w).&N"
    char.wimpy = hp
    return f"&wYou will automatically flee combat when your HP drops to &W{hp}&w.&N"


def cmd_position(state, new_pos: str) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    old_pos = getattr(char, "position", "standing")
    if new_pos == "standing":
        was_resting = state._resting.pop(state._player, None)
        if was_resting and old_pos == "standing":
            return "&wYou stop resting.&N"
    if old_pos == new_pos:
        return f"&wYou are already {new_pos}.&N"
    char.position = new_pos
    return {
        "standing": "&wYou stand up.&N",
        "sitting":  "&wYou sit down.&N",
        "resting":  "&wYou begin to rest.&N",
        "kneeling": "&wYou kneel.&N",
        "reclined": "&wYou lie down.&N",
    }.get(new_pos, f"&wYou are now {new_pos}.&N")


def cmd_powers(state) -> str:
    import time as _t
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    from ..game import _collect_tagged_powers, _power_key, _TICK_INTERVAL, _SLOT_LABELS

    all_powers = _collect_tagged_powers(char)
    if not all_powers:
        return "&wYou have no powers.&N"

    now   = _t.monotonic()
    lines = [
        f"&W{'Power':<28} {'Keywords':<22} Status&N",
        "&w" + "─" * 64 + "&N",
    ]
    for p in all_powers:
        raw_name = p.get("name", "?")
        slot     = p.get("_slot")
        label    = f" &x({_SLOT_LABELS.get(slot, slot)})&N" if slot else ""
        display  = f"{raw_name}{label}"
        keywords = ", ".join(p.get("keywords", ()))
        pkey     = _power_key(p)
        ready_at = state._power_cooldowns.get(pkey, 0)
        if now >= ready_at:
            status = "&Gready&N"
        else:
            rem    = (ready_at - now) / _TICK_INTERVAL
            status = f"&R{rem:.1f} ticks&N"
        lines.append(f"{display:<28} &c{keywords:<22}&N {status}")
    return "\n".join(lines)


def cmd_who(state) -> str:
    if not state.characters:
        return "&wNobody is here.&N"
    lines = [
        f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5} {'XP':>10}&N",
        "&w" + "─" * 58 + "&N",
    ]
    for char in state.characters.values():
        lines.append(
            f"{char.name:<15} {char.race:<12} {char.cclass:<10} "
            f"{char.level:>5} {getattr(char,'xp',0):>10,}"
        )
    return "\n".join(lines)


def cmd_toggle(state, args: list) -> str:
    KNOWN_TOGGLES = {
        "timeofday": (
            "time_announce",
            "Time-of-day announcements (dawn, dusk, midnight)",
        ),
    }
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"
    if not hasattr(char, "toggles") or char.toggles is None:
        char.toggles = {}

    if not args:
        lines = ["&wYour toggles:&N", "&w" + "-" * 44 + "&N"]
        for key, (field, desc) in KNOWN_TOGGLES.items():
            state   = char.toggles.get(field, True)
            color   = "&G" if state else "&R"
            setting = "ON " if state else "OFF"
            lines.append(f"  &w{key:<16}&N {color}{setting}&N  {desc}")
        return "\n".join(lines)

    key = args[0].lower()
    if key not in KNOWN_TOGGLES:
        opts = ", ".join(KNOWN_TOGGLES)
        return f"&wUnknown toggle &W{key}&w. Options: &W{opts}&N"

    field, desc     = KNOWN_TOGGLES[key]
    current         = char.toggles.get(field, True)
    char.toggles[field] = not current
    new_state       = char.toggles[field]
    color           = "&G" if new_state else "&R"
    state_str       = "ON" if new_state else "OFF"
    return f"&w{desc}: {color}{state_str}&N"
