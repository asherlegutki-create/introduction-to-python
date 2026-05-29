"""
ashenmoor.world.objects
───────────────────────
Object / Item / Weapon / Container hierarchy.

Weapon procs
────────────
Add "proc": "<name>" to any Weapon template to attach a special procedure.
The proc name must exist in ashenmoor.world.procs.PROCS.
Procs are called by combat_round() after each successful hit on the primary
hand weapon.  They receive (attacker, defender) and return a list of
diku-coloured message strings.

Stat bonuses on items
─────────────────────
Add a "stat_mods" dict to any item template to give it ability bonuses.

D&D 5.5e weapon properties
───────────────────────────
  light, finesse, versatile, thrown, reach, is_shield, armor_type
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
        self.weight:    float         = d.get("weight",    0)
        self.mod:       list          = d.get("mod",       [])
        self.take:      bool          = True
        self.wear_on:   str | None    = d.get("wear_on",   None)
        self.stat_mods: dict[str,int] = d.get("stat_mods", {})
        self.save_mods: dict[str,int] = d.get("save_mods", {})
        self.ac_bonus:  int           = d.get("ac_bonus",  0)
        self.armor_type: str | None   = d.get("armor_type", None)

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
        # ── Combat stats ──────────────────────────────────────────────────────
        self.dice:           str        = d.get("dice",           "1d6")
        self.hitroll:        int        = d.get("hitroll",        0)
        self.damroll:        int        = d.get("damroll",        0)
        self.two_handed:     bool       = d.get("two_handed",     False)
        # ── D&D 5.5e weapon properties ────────────────────────────────────────
        self.light:          bool       = d.get("light",          False)
        self.finesse:        bool       = d.get("finesse",        False)
        self.versatile:      bool       = d.get("versatile",      False)
        self.versatile_dice: str        = d.get("versatile_dice", self.dice)
        self.thrown:         bool       = d.get("thrown",         False)
        self.reach:          bool       = d.get("reach",          False)
        self.is_shield:      bool       = d.get("is_shield",      False)
        self.armor_type:     str | None = d.get("armor_type",     None)
        # ── Weapon proc ───────────────────────────────────────────────────────
        # Store as a string key; combat_round() resolves it via PROCS at runtime
        # to avoid circular imports between world.objects and engine.combat.
        self.proc:           str | None = d.get("proc",           None)
        # Weapon powers — list of power dicts; available to wielder while equipped
        self.powers:         list       = list(d.get("powers",    []))

    def __repr__(self):
        props = []
        if self.two_handed: props.append("2h")
        if self.light:      props.append("light")
        if self.finesse:    props.append("finesse")
        if self.proc:       props.append(f"proc={self.proc}")
        suffix = f", {', '.join(props)}" if props else ""
        return f"Weapon({self.name!r}, dice={self.dice!r}{suffix})"


class Container(Item):
    """An Item that holds other items."""

    def __init__(self, d: dict):
        super().__init__(d)
        self.capacity:            float = d.get("capacity",            0.0)
        self.weightless_capacity: float = d.get("weightless_capacity", 0.0)
        self.contents:            list  = list(d.get("contents",       []))
        self.is_open:             bool  = d.get("is_open",             True)
        self.is_shield:           bool  = False

    @property
    def contents_weight(self) -> float:
        return sum(getattr(i, "weight", 0) for i in self.contents)

    @property
    def available_capacity(self) -> float:
        return max(0.0, self.capacity - self.contents_weight)

    @property
    def available_weightless(self) -> float:
        used = min(self.contents_weight, self.weightless_capacity)
        return max(0.0, self.weightless_capacity - used)

    @property
    def effective_weight(self) -> float:
        cw       = self.contents_weight
        absorbed = min(cw, self.weightless_capacity)
        return self.weight + max(0.0, cw - absorbed)

    def can_fit(self, item) -> bool:
        return getattr(item, "weight", 0) <= self.available_capacity

    def __repr__(self):
        return (f"Container({self.name!r}, "
                f"{self.contents_weight:.1f}/{self.capacity:.1f} lbs, "
                f"open={self.is_open})")
