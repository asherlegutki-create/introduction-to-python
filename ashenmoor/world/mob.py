"""
ashenmoor.world.mob
───────────────────
Mob — a non-player character.

Inherits everything from Character (stats, race, level, cclass, computed_stat,
character_sheet, etc.) and adds the fields that are only meaningful for NPCs:

  room_description   str        line shown in the room listing
  key_words          tuple      words players can use to target this mob
  description        str        full examine output
  aggro              bool       attacks players on sight (Phase 5)
  wander             bool       moves between rooms autonomously (Phase 5)

Template dict keys are the union of Character and Mob fields.  The "class"
key sets cclass (character class: Warrior, Guardian...) the same as for
player characters.  The zone spawner uses "spawn_as" (not "class") to select
the Python class, so there is no collision.
"""

from ..core.character import Character


class Mob(Character):
    """
    Non-player character.

    Parameters
    ----------
    d : dict
        All Character keys (name, stats, race, level, position, class) plus:

        room_description  str         shown in room listing
        key_words         tuple[str]  targeting keywords
        description       str         examine text
        aggro             bool        default False
        wander            bool        default False

    races : dict | None
        Passed through to Character.__init__.
    """

    def __init__(self, d: dict, races: dict | None = None):
        super().__init__(d, races)
        self.room_description: str = d.get("room_description", "")
        self.key_words: tuple = d.get("key_words", ())
        self.description: str = d.get("description", "")
        self.aggro: bool = d.get("aggro", False)
        self.wander: bool = d.get("wander", False)
        self.killable: bool = d.get("kill", True)
        # killable notes:
        #   True  (default) — normal mob, can be killed in combat.
        #   False — protected character (player-controlled, quest-critical,
        #           etc.). Will NOT appear in 'who'. The combat system MUST
        #           check target.killable and refuse the killing blow —
        #           this is not a pkill mud.

    def matches(self, keyword: str) -> bool:
        """True if keyword appears in the mob's name or key_words."""
        if keyword.lower() in self.name.lower():
            return True
        return keyword.lower() in (k.lower() for k in self.key_words)

    def examine(self) -> str:
        """Full examine text (may contain Diku color codes)."""
        return self.description or f"You see nothing special about {self.name}."

    def __repr__(self) -> str:
        kill = "" if self.killable else ", killable=False"
        return (
            f"Mob({self.name!r}, race={self.race!r}, "
            f"class={self.cclass!r}, level={self.level}, "
            f"aggro={self.aggro}{kill})"
        )


mr_mob = Mob(
    {
        "room_description": "the_void",
        "key_words": ("mob", "mr", "mr_mob"),
        "description": "A Mob Created For Homework",
        "aggro": False,
        "wander": True,
        "killable": True,
    }
)
