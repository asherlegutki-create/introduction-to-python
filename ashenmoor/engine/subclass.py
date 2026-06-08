"""
ashenmoor.engine.subclass
──────────────────────────
Shared subclass selection logic.

Both the local console (ticker.py) and network client (net/client.py)
call into this module.  The caller provides two async-compatible
callables:

    send(text)   — display text to the player
    recv()       — await a line of input from the player

This keeps the selection flow, help text, and validation in one place.
Adding a new subclass later is a one-line addition to SUBCLASSES.
"""

from __future__ import annotations
from ashenmoor.dnd.classes.fighter import (
    HELP_CHAMPION,
    HELP_BATTLEMASTER,
    apply_subclass,
)

# ── Subclass registry ──────────────────────────────────────────────────────────

SUBCLASSES: dict[str, dict] = {
    "1": {
        "key":   "champion",
        "label": "Champion",
        "blurb": (
            "&+WChampion&N — Superior combat instincts.\n"
            "  Improved parry roll (adds proficiency bonus).\n"
            "  1-in-4 chance to shrug any hit to zero damage.\n"
            "  Expanded crit range at higher levels.\n"
            "  &xNo extra resource pools — always on.&N"
        ),
        "help":  HELP_CHAMPION,
    },
    "2": {
        "key":   "battle_master",
        "label": "Battle Master",
        "blurb": (
            "&+WBattle Master&N — Tactical superiority through maneuvers.\n"
            "  Superiority Dice pool (4d8 → 5d10 → 6d12).\n"
            "  Six combat maneuvers: trip, disarm, precise,\n"
            "  menace, rally, and riposte.\n"
            "  &xRestores on short rest.&N"
        ),
        "help":  HELP_BATTLEMASTER,
    },
}

_BANNER = """
&+W╔══════════════════════════════════════════════════════╗
║          MARTIAL ARCHETYPE — Choose Your Path       ║
╚══════════════════════════════════════════════════════╝&N

&wYou have mastered the fundamentals of combat.
It is time to choose the path that defines you.
This choice is permanent.&N
"""

_PROMPT = (
    "\n&W  [1]  Champion\n"
    "  [2]  Battle Master\n"
    "  [h1] Help: Champion\n"
    "  [h2] Help: Battle Master\n\n"
    "&wEnter choice: &N"
)


async def run_subclass_selection(char, send, recv) -> None:
    """
    Drive the subclass selection flow to completion.

    send  — coroutine-compatible callable: await send(text)
    recv  — coroutine-compatible callable: line = await recv()

    Blocks until the player makes a valid choice.
    Calls apply_subclass() which mutates char in-place.
    """
    await send(_BANNER)

    # Show one-line blurbs
    for key, sub in SUBCLASSES.items():
        await send(f"  [{key}] {sub['blurb']}\n")

    while True:
        await send(_PROMPT)
        try:
            raw = (await recv()).strip().lower()
        except (EOFError, ConnectionResetError):
            # Connection dropped — default to Champion so char isn't stuck
            raw = "1"

        if raw in ("h1", "h2"):
            idx = raw[1]
            if idx in SUBCLASSES:
                await send(SUBCLASSES[idx]["help"])
                # Re-show blurbs after help
                for key, sub in SUBCLASSES.items():
                    await send(f"  [{key}] {sub['blurb']}\n")
            continue

        if raw in SUBCLASSES:
            sub = SUBCLASSES[raw]
            apply_subclass(char, sub["key"])
            await send(
                f"\n&+WYou have chosen the path of the &N{sub['label']}&+W!&N\n"
                f"&wYour training reshapes around your new focus.\n"
                f"Type &Wpowers&w to see your abilities.&N\n"
            )
            return

        await send("&RInvalid choice. Enter 1, 2, h1, or h2.&N\n")


def needs_subclass(char) -> bool:
    """
    Return True if this character needs to go through subclass selection.
    Covers:
      - Warriors migrated to Fighter with no subclass set
      - New fighters who have reached level 8
      - Characters whose dnd dict has subclass_pending = True
    """
    cclass = getattr(char, "cclass", "").lower()
    if cclass not in ("fighter", "warrior"):
        return False
    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("subclass_pending"):
        return True
    if dnd.get("subclass") is not None:
        return False
    # No subclass set at all — check level
    return char.level >= 8


def check_levelup_subclass(char) -> bool:
    """
    Called by apply_level_up after incrementing char.level.
    Sets subclass_pending if the character just hit level 8.
    Returns True if subclass selection should be triggered.
    """
    if char.level != 8:
        return False
    cclass = getattr(char, "cclass", "").lower()
    if cclass not in ("fighter", "warrior"):
        return False
    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("subclass") is not None:
        return False
    dnd["subclass_pending"] = True
    char.dnd = dnd
    return True
