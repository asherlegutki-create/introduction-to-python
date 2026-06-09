"""
ashenmoor.engine.commands.style
────────────────────────────────
Fighting style management for Fighters.

Commands
────────
  style                       Show current style and charges
  style list                  Show all available styles with descriptions
  style choose <name>         Prompt for confirmation
  style choose <name> confirm Change immediately without prompt

Rules
─────
  Must have style_change_charges > 0
  Must have completed a long rest (style_long_rest_ready = True)
  Cannot change during combat
  Charges are earned: start with 3, gain 1 per level, max 3
"""

from __future__ import annotations


def cmd_style(state, args: list) -> str:
    char = state.characters.get(state._player)
    if not char:
        return "&RNo character found.&N"

    cclass = getattr(char, "cclass", "").lower()
    if cclass not in ("fighter", "warrior"):
        return "&wFighting styles are a Fighter feature.&N"

    from ...dnd.classes.fighter import FIGHTING_STYLES
    dnd = getattr(char, "dnd", {}) or {}

    # ── style (no args) ───────────────────────────────────────────────────
    if not args:
        style    = dnd.get("fighting_style", "none")
        charges  = dnd.get("style_change_charges", 0)
        max_chg  = dnd.get("style_change_max", 3)
        ready    = dnd.get("style_long_rest_ready", False)
        label    = style.replace("_", " ").title()
        desc     = FIGHTING_STYLES.get(style, "")

        lines = [
            f"&+WFighting Style: &N{label}&N",
            f"  &w{desc}&N",
            f"&wStyle change charges: &W{charges}&w/&W{max_chg}&N",
        ]
        if charges > 0 and not ready:
            lines.append(
                "&xYou need to complete a long rest before changing your style.&N"
            )
        elif charges > 0 and ready:
            lines.append(
                "&wYou may change your style. "
                "Use &Wstyle choose <name>&w to change.&N"
            )
        else:
            lines.append("&RNo charges remaining. Gain charges by leveling up.&N")
        return "\n".join(lines)

    # ── style list ────────────────────────────────────────────────────────
    if args[0].lower() == "list":
        current = dnd.get("fighting_style", "")
        lines   = ["&+WAvailable Fighting Styles:&N",
                   "&w" + "─" * 56 + "&N"]
        for sname, desc in FIGHTING_STYLES.items():
            label  = sname.replace("_", " ").title()
            marker = " &G(current)&N" if sname == current else ""
            lines.append(f"  &W{label}&N{marker}")
            lines.append(f"    &w{desc}&N")
        return "\n".join(lines)

    # ── style choose <name> [confirm] ─────────────────────────────────────
    if args[0].lower() == "choose":
        if len(args) < 2:
            return "&wUsage: &Wstyle choose <style name>&N"

        # Last arg might be "confirm"
        confirm = (args[-1].lower() == "confirm")
        name_parts = args[1:-1] if confirm else args[1:]
        style_input = "_".join(name_parts).lower()

        # Match style name
        match = next(
            (s for s in FIGHTING_STYLES
             if s.lower() == style_input or
                s.lower().replace("_", "") == style_input.replace("_", "")),
            None,
        )
        if match is None:
            opts = ", ".join(s.replace("_", " ").title() for s in FIGHTING_STYLES)
            return (
                f"&wUnknown style '&W{' '.join(name_parts)}&w'. "
                f"Available: &W{opts}&N"
            )

        current = dnd.get("fighting_style", "")
        if match == current:
            return f"&wYou already use the &W{match.replace('_',' ').title()}&w style.&N"

        # Check restrictions
        if state._player in state.fighting:
            return "&wYou cannot change your fighting style during combat.&N"

        charges = dnd.get("style_change_charges", 0)
        if charges <= 0:
            return (
                "&RYou have no style change charges remaining.\n"
                "Gain charges by leveling up (1 per level, max 3).&N"
            )

        ready = dnd.get("style_long_rest_ready", False)
        if not ready:
            return (
                "&wYou must complete a long rest before changing your style.\n"
                "Rest until fully restored, then try again.&N"
            )

        label = match.replace("_", " ").title()

        if not confirm:
            return (
                f"&wChange your fighting style to &W{label}&w?\n"
                f"This will consume 1 style change charge "
                f"(&W{charges}&w remaining).\n"
                f"Type &Wstyle choose {' '.join(name_parts)} confirm&w to proceed, "
                f"or just &Wstyle choose {' '.join(name_parts)}&w again.&N"
            )

        # Apply the change
        dnd["fighting_style"]        = match
        dnd["style_change_charges"]  = charges - 1
        dnd["style_long_rest_ready"] = False
        char.dnd = dnd

        return (
            f"&+WYour fighting style has changed to &N{label}&+W!&N\n"
            f"&wStyle change charges remaining: "
            f"&W{dnd['style_change_charges']}&w/&W{dnd['style_change_max']}&N"
        )

    return "&wUsage: &Wstyle&N | &Wstyle list&N | &Wstyle choose <name>&N"
