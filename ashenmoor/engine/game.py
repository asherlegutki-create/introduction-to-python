"""
ashenmoor.engine.game
─────────────────────
Game state container and core engine functions.

The notebook had global dicts (locations, rooms, characters) threaded through
module-level code and referenced inside class methods.  This module replaces
that pattern with a GameState object that owns all runtime state and passes
itself to the functions that need it.

Usage
-----
    from ashenmoor.engine import GameState
    from ashenmoor.color  import crepl

    state = GameState()
    state.load_world(rooms, characters, locations)

    crepl(
        handler  = state.handle,
        prompt   = "&g>&N ",
        banner   = "&+WWelcome!&N",
        farewell = "&CGoodbye!&N",
    )
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room      import Room
    from ..core.character  import Character


# ── Movement directions ───────────────────────────────────────────────────────

DIRECTIONS = frozenset({
    "north", "south", "east", "west", "up", "down",
    "n", "s", "e", "w", "u", "d",
})

_DIR_EXPAND = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up",    "d": "down",
}


def _expand_direction(d: str) -> str:
    return _DIR_EXPAND.get(d.lower(), d.lower())


# ── go() — pure function, no global state ────────────────────────────────────

def go(character: str,
       locations: dict[str, int],
       rooms:     dict[int, "Room"],
       direction: str) -> object:
    """
    Move *character* in *direction*.

    Updates locations[character] in place.

    Returns
    -------
    Room   if the move succeeded (the destination room object)
    str    if the move failed (the 'alas' message)
    """
    direction = _expand_direction(direction)
    room = rooms[locations[character]]
    dest_id = room.exit_room_id(direction)
    if dest_id is not None and dest_id in rooms:
        locations[character] = dest_id
        return rooms[dest_id]
    # No exit — check if any exit failed or there were none at all
    return "&NAlas, you cannot go that way. . . ."


# ── GameState ─────────────────────────────────────────────────────────────────

class GameState:
    """
    Owns all runtime world state and exposes a handle() method suitable
    for passing directly to crepl().

    Attributes
    ----------
    rooms       dict[int, Room]
    characters  dict[str, Character]
    locations   dict[str, int]          character_name -> room_number
    player      str                     name of the player character
    """

    def __init__(self):
        self.rooms:            dict[int, "Room"]      = {}
        self.characters:       dict[str, "Character"] = {}
        self.locations:        dict[str, int]         = {}
        self.player:           str                    = ""
        self.object_templates: dict[str, dict]        = {}
        self.mob_templates:    dict[str, dict]        = {}

    def load_world(self,
                   rooms:      dict,
                   characters: dict,
                   locations:  dict,
                   player:     str = "") -> None:
        """Populate the game state from pre-built dicts."""
        self.rooms      = rooms
        self.characters = characters
        self.locations  = locations
        self.player     = player or (next(iter(characters)) if characters else "")

    def load_zone(self, zone) -> None:
        """
        Merge a Zone into the live world.

        Rooms are added to self.rooms (existing rooms with the same number
        are overwritten — zone designers should use non-overlapping vnum ranges).

        Object and mob templates are merged into the world template registries
        so the engine can spawn new instances of any template at runtime.

        Parameters
        ----------
        zone : ashenmoor.world.Zone
        """
        # Warn on room number collisions rather than silently overwriting
        collisions = set(zone.rooms) & set(self.rooms)
        if collisions:
            import warnings
            warnings.warn(
                f"Zone '{zone.name}' overwrites existing room numbers: {sorted(collisions)}",
                stacklevel=2,
            )
        self.rooms.update(zone.rooms)
        self.object_templates.update(zone.object_templates)
        self.mob_templates.update(zone.mob_templates)

    # ── Current room for player ───────────────────────────────────────────────

    @property
    def current_room(self) -> "Room | None":
        room_id = self.locations.get(self.player)
        return self.rooms.get(room_id) if room_id is not None else None

    # ── Command handler ───────────────────────────────────────────────────────

    def handle(self, raw: str) -> object:
        """
        Process one line of player input.

        Returns a string or object whose __str__ contains Diku color codes,
        which crepl() will pass to cprint().
        Returns None to produce no output.
        Returns the string 'quit' to signal crepl() to end the loop.
        """
        tokens    = raw.strip().lower().split()
        if not tokens:
            return None
        verb, *args = tokens

        # ── quit ──────────────────────────────────────────────────────────────
        if verb in ("quit", "exit", "leave", "q", "camp"):
            return "quit"

        # ── movement ─────────────────────────────────────────────────────────
        if verb in DIRECTIONS or verb == "go":
            direction = args[0] if verb == "go" and args else verb
            return go(self.player, self.locations, self.rooms, direction)

        # ── look ──────────────────────────────────────────────────────────────
        if verb in ("look", "l"):    ## fix this to look at objects/characters,
            room = self.current_room ## it should use a reusable targeting
            if room is None:         ## function
                return "&RYou are nowhere.&N"
            return room.render(self.locations, self.characters)

        # ── who ───────────────────────────────────────────────────────────────
        if verb == "who":
            return self._who()

        # ── score / stats ─────────────────────────────────────────────────────
        if verb in ("score", "stats", "stat"):
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"

        # ── unknown ───────────────────────────────────────────────────────────
        return "&NPardon?"

    # ── Utility ───────────────────────────────────────────────────────────────

    def _who(self) -> str:
        if not self.characters:
            return "&wNobody is here.&N"
        lines = [f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5}&N"]
        lines.append("&w" + "─" * 46 + "&N")
        for char in self.characters.values():
            lines.append(
                f"{char.name:<15} {char.race:<12} {char.cclass:<10} {char.level:>5}"
            )
        return "\n".join(lines)

    def character_list(self) -> str:
        """Formatted character table — same as _who() but public."""
        return self._who()
