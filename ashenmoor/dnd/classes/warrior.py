"""
ashenmoor.dnd.classes.warrior
──────────────────────────────
Backwards-compatibility shim.

All Fighter/Warrior logic now lives in fighter.py.
Any code that imports from warrior.py continues to work unchanged.
"""

from .fighter import (
    # Core functions
    proficiency_bonus,
    attack_count,
    crit_range,
    active_features,
    great_weapon_reroll,
    # State constructors
    new_fighter_dnd,
    new_fighter_dnd as new_warrior_dnd,
    apply_subclass,
    new_battlemaster_state,
    # Power lists
    FIGHTER_POWERS,
    FIGHTER_POWERS as WARRIOR_POWERS,
    BATTLEMASTER_POWERS,
    # Constants
    FIGHTING_STYLES,
    SUBCLASS_LEVEL,
    # Help text
    HELP_CHAMPION,
    HELP_BATTLEMASTER,
)

__all__ = [
    "proficiency_bonus", "attack_count", "crit_range",
    "active_features", "great_weapon_reroll",
    "new_fighter_dnd", "new_warrior_dnd",
    "apply_subclass", "new_battlemaster_state",
    "FIGHTER_POWERS", "WARRIOR_POWERS", "BATTLEMASTER_POWERS",
    "FIGHTING_STYLES", "SUBCLASS_LEVEL",
    "HELP_CHAMPION", "HELP_BATTLEMASTER",
]
