"""
ashenmoor.world.objects
───────────────────────
Object / Item / Weapon / Container hierarchy.

wear_on  str | None   slot from VALID_WEAR_ON, or None (carry-only).
                      Weapons default to "primary_hand".
two_handed bool       Weapon flag — blocks secondary_hand when equipped.

Container
─────────
Can live in a room or a player's inventory.
Interact with it wherever it is — no need to pick it up first.

    capacity            float   total weight it can hold (lbs)
    weightless_capacity float   of that, this many lbs don't add to carrier burden
    contents            list    Item instances inside
    is_open             bool    whether it can be accessed

Weight rules:
  - contents_weight  = sum of all item weights inside
  - effective_weight = container.weight + max(0, contents_weight - weightless_capacity)
    (weightless_capacity 'absorbs' the first N lbs of contents)
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
        self.weight:  float    = d.get("weight",  0)
        self.mod:     list     = d.get("mod",     [])
        self.take:    bool     = True
        self.wear_on: str|None = d.get("wear_on", None)

        if self.wear_on is not None and self.wear_on not in VALID_WEAR_ON:
            raise ValueError(
                f"Item {self.name!r}: wear_on={self.wear_on!r} is not valid.\n"
                f"Valid: {sorted(VALID_WEAR_ON)}"
            )

    def __repr__(self): return f"Item({self.name!r}, wear_on={self.wear_on!r})"


class Weapon(Item):
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


class Container(Item):
    """
    An Item that holds other items.

    Extra d keys
    ────────────
    capacity            float   max weight the container can hold (lbs)
    weightless_capacity float   lbs of contents that don't add to carrier's burden
    contents            list    pre-loaded Item instances (optional)
    is_open             bool    starts open unless set to False
    """

    def __init__(self, d: dict):
        super().__init__(d)
        self.capacity:            float = d.get("capacity",            0.0)
        self.weightless_capacity: float = d.get("weightless_capacity", 0.0)
        self.contents:            list  = list(d.get("contents",       []))
        self.is_open:             bool  = d.get("is_open",             True)

    @property
    def contents_weight(self) -> float:
        """Total weight of everything inside."""
        return sum(getattr(i, "weight", 0) for i in self.contents)

    @property
    def available_capacity(self) -> float:
        """How many more lbs can fit."""
        return max(0.0, self.capacity - self.contents_weight)

    @property
    def available_weightless(self) -> float:
        """How many more weightless lbs remain."""
        used = min(self.contents_weight, self.weightless_capacity)
        return max(0.0, self.weightless_capacity - used)

    @property
    def effective_weight(self) -> float:
        """
        Weight this container contributes to whoever is carrying it.
        Contents up to weightless_capacity are absorbed; the rest counts.
        """
        cw          = self.contents_weight
        absorbed    = min(cw, self.weightless_capacity)
        return self.weight + max(0.0, cw - absorbed)

    def can_fit(self, item) -> bool:
        """True if item fits by weight."""
        return getattr(item, "weight", 0) <= self.available_capacity

    def __repr__(self):
        return (f"Container({self.name!r}, "
                f"{self.contents_weight:.1f}/{self.capacity:.1f} lbs, "
                f"open={self.is_open})")
