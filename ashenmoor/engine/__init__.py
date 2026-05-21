"""
ashenmoor.engine
────────────────
Game engine: state management, movement, targeting, command handling.

    from ashenmoor.engine import GameState, go, DIRECTIONS
    from ashenmoor.engine import find_target, find_all_targets, parse_target
"""

from .game      import GameState, go, DIRECTIONS
from .targeting import find_target, find_all_targets, parse_target, target_name

__all__ = [
    "GameState", "go", "DIRECTIONS",
    "find_target", "find_all_targets", "parse_target", "target_name",
]
