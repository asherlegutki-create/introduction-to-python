"""
ashenmoor.world.objects
───────────────────────
Object / Item / Weapon hierarchy.

wear_on  str | None   value from VALID_WEAR_ON, or None (carry-only).
                      Weapons default to "primary_hand" if not set.
two_handed bool       Weapon-only. Blocks secondary_hand when equipped.
"""

from .equipment import VALID_WEAR_ON


class Object:
    def __init__(self, d: dict):
        self.name:             str   = d.get("name",             "something")
        self.room_description: str   = d.get("room_description", "")
        self.key_words:        tuple = d.get("key_words",        ())
        desc = d.get("description", "")
        self.description:      str   = "\n".join(desc) if isinstance(desc, (tuple, list)) else desc
        self.take:             bool  = False

    def matches(self, keyword: str) -> bool:
        return keyword.lower() in (k.lower() for k in self.key_words)

    def __str__(self):  return self.name
    def __repr__(self): return f"Object({self.name!r})"


class Item(Object):
    def __init__(self, d: dict):
        super().__init__(d)
        self.weight:  int      = d.get("weight",  0)
        self.mod:     list     = d.get("mod",     [])
        self.take:    bool     = True
        self.wear_on: str|None = d.get("wear_on", None)

        if self.wear_on is not None and self.wear_on not in VALID_WEAR_ON:
            raise ValueError(
                f"Item {self.name!r}: wear_on={self.wear_on!r} is not valid.\n"
                f"Valid values: {sorted(VALID_WEAR_ON)}"
            )

    def __repr__(self): return f"Item({self.name!r}, wear_on={self.wear_on!r})"


class Weapon(Item):
    """
    Wieldable item.

    wear_on defaults to "primary_hand" if not specified.
    two_handed=True blocks secondary_hand when equipped.
    """

    def __init__(self, d: dict):
        if "wear_on" not in d:
            d = {**d, "wear_on": "primary_hand"}
        super().__init__(d)
        self.dice:       str  = d.get("dice",       "1d6")
        self.hitroll:    int  = d.get("hitroll",    0)
        self.damroll:    int  = d.get("damroll",    0)
        self.two_handed: bool = d.get("two_handed", False)

    def __repr__(self):
        th = ", 2h" if self.two_handed else ""
        return f"Weapon({self.name!r}, dice={self.dice!r}{th})"
