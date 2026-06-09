"""
ashenmoor.colors
────────────────
Centralized color constants for the entire game.

Every command, menu, and display that shows a class name, race name,
or UI element imports from here.  Changing a color is a one-line edit.

Usage
─────
    from ashenmoor.colors import class_color, race_color, C

    cprint(f"{C.UI_HEADER}Characters:{C.RESET}")
    cprint(f"{class_color('Fighter')}Fighter{C.RESET}")
    cprint(f"{race_color('Dwarf')}Dwarf{C.RESET}")

    # Full class+subclass display string
    cprint(class_display("Fighter", "battle_master"))
    # → "&bFighter&w (&gBattle Master&w)&N"

Color code reference
────────────────────
    &N / &n   reset
    &r        dark red        &R  bold red
    &g        dark green      &G  bright green
    &b        dark blue       &B  bold blue
    &c        dark cyan       &C  bright cyan
    &y        dark yellow     &Y  bright yellow
    &m        dark magenta    &M  bright magenta
    &w        dark grey       &W  bright white
    &x        black/very dim  &X  dark grey
    &+W       bold bright white
"""

from __future__ import annotations


# ── UI constants ──────────────────────────────────────────────────────────────

class C:
    """UI color constants.  Import as `from ashenmoor.colors import C`."""

    # Structural
    RESET   = "&N"       # reset after any colored segment
    SEP     = "&w"       # separator lines  -=-=-=-
    DIM     = "&x"       # dim / secondary info
    PLAIN   = "&g"       # plain text for UI

    # Text roles
    HEADER  = "&g"      # section headers  e.g. "Characters:"
    NUMBER  = "&w"       # list numbers     e.g. "1)"
    NAME    = "&W"       # character / player names
    LABEL   = "&w"       # field labels     e.g. "Level"
    VALUE   = "&W"       # field values     e.g. the level number
    PAREN   = "&w"       # parentheses in  "(Race)"  "(Subclass)"

    # Subclass name (inside parentheses)
    SUBCLASS = "&g"

    # Feedback
    OK      = "&G"       # success messages
    WARN    = "&Y"       # warnings
    ERR     = "&R"       # errors / danger
    INFO    = "&c"       # informational


# ── Class colors ──────────────────────────────────────────────────────────────
#
# All Fighter subclasses (Champion, Battle Master, Eldritch Knight) share
# the Fighter color — the subclass is shown in C.SUBCLASS inside parens.

_CLASS_COLORS: dict[str, str] = {
    # Fighter family
    "fighter":         "&b",
    "warrior":         "&b",   # legacy name, same color
    "champion":        "&b",
    "battle master":   "&b",
    "battle_master":   "&b",
    "eldritch knight": "&b",
    "eldritch_knight": "&b",

    # Martial
    "barbarian":       "&C",
    "ranger":          "&G",
    "paladin":         "&Y",
    "monk":            "&W",

    # Arcane
    "wizard":          "&m",
    "mage":            "&m",
    "sorcerer":        "&M",
    "warlock":         "&M",

    # Divine / Nature
    "cleric":          "&W",
    "druid":           "&g",
    "shaman":          "&c",

    # Martial/Stealth
    "rogue":           "&r",
    "bard":            "&Y",
}

_DEFAULT_CLASS_COLOR = "&w"


def class_color(cclass: str) -> str:
    """Return the diku color code for a class name."""
    return _CLASS_COLORS.get(cclass.lower(), _DEFAULT_CLASS_COLOR)


def class_display(cclass: str, subclass: str | None = None) -> str:
    """
    Return a fully colored class+subclass string.

    Examples:
        class_display("Fighter")
            → "&bFighter&N"
        class_display("Fighter", "battle_master")
            → "&bFighter&w (&gBattle Master&w)&N"
        class_display("Wizard", "abjurer")
            → "&mWizard&w (&gAbjurer&w)&N"
    """
    cc    = class_color(cclass)
    label = cclass

    if not subclass:
        return f"{cc}{label}{C.RESET}"

    sub_label = subclass.replace("_", " ").title()
    return (
        f"{cc}{label}{C.PAREN} {C.PAREN}({C.SUBCLASS}{sub_label}"
        f"{C.PAREN}){C.RESET}"
    )


# ── Race colors ───────────────────────────────────────────────────────────────

_RACE_COLORS: dict[str, str] = {
    "human":     "&W",
    "dwarf":     "&y",
    "grey elf":  "&C",
    "half elf":  "&C",
    "elf":       "&C",
    "ogre":      "&r",
    # Placeholder entries for future races
    "halfling":  "&y",
    "gnome":     "&G",
    "half-orc":  "&r",
    "tiefling":  "&M",
    "dragonborn":"&R",
}

_DEFAULT_RACE_COLOR = "&w"


def race_color(race: str) -> str:
    """Return the diku color code for a race name."""
    return _RACE_COLORS.get(race.lower(), _DEFAULT_RACE_COLOR)


def race_display(race: str) -> str:
    """Return a colored race name string."""
    return f"{race_color(race)}{race}{C.RESET}"


# ── Combined helpers ──────────────────────────────────────────────────────────

def char_list_class(cclass: str, subclass: str | None = None) -> str:
    """
    Class display formatted for the character list column.
    Identical to class_display() — provided as a named alias for clarity
    at call sites that are specifically rendering the character list.
    """
    return class_display(cclass, subclass)


def char_list_race(race: str) -> str:
    """Race display formatted for the character list  (Race)  column."""
    return f"{C.PAREN}({race_color(race)}{race}{C.PAREN}){C.RESET}"
