"""
ashenmoor.world.objects
───────────────────────
Object / Item / Weapon / Container hierarchy.

Stat bonuses on items
─────────────────────
Add a "stat_mods" dict to any item template to give it ability bonuses.
The bonus is summed across all equipped items in computed_stat(), then the
total (base + bonus) is capped at the character's racial maximum.

  {"stat_mods": {"str": 10}}            — +10 STR ring
  {"stat_mods": {"dex": 5, "cha": 3}}  — multi-stat item

Humans max at 100 per stat.  Ogres can reach 180 STR with enough +STR gear.

D&D 5.5e weapon properties
───────────────────────────
  light       Can be used for Two-Weapon Fighting without the style feat.
  finesse     Use STR or DEX modifier (whichever is higher) for attack and damage.
  versatile   Can be wielded one-handed (normal dice) or two-handed (versatile_dice).
  thrown      Can be thrown as a ranged attack.
  reach       Adds 5 ft to melee reach.
  is_shield   When in secondary_hand: grants +10 AC (0-100 scale).
  armor_type  Key into ARMOR_TABLE in dnd/armor.py (e.g. "chain_mail").
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
        self.mod:       list          = d.get("mod",       [])   # legacy compat
        self.take:      bool          = True
        self.wear_on:   str | None    = d.get("wear_on",   None)
        # Stat bonuses while equipped.
        # Regular keys  ("str", "int", …)      push toward the 100 display cap.
        # Max keys      ("max_str", "max_int")  extend the ceiling above 100.
        # Example: {"int": 10, "max_int": 56} — fills toward 100, then adds 56 beyond.
        self.stat_mods: dict[str,int] = d.get("stat_mods", {})
        # Saving throw bonuses: keys are "par", "rod", "pet", "bre", "spe"
        self.save_mods: dict[str,int] = d.get("save_mods", {})
        # Flat AC bonus added by get_ac() on top of armor_type base.
        # Any wearable item may carry this — not just body armor.
        self.ac_bonus:  int           = d.get("ac_bonus",  0)
        # Armor type key into ARMOR_TABLE (on_body items only; see dnd/armor.py)
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
        # armor_type: key into ARMOR_TABLE (e.g. "chain_mail")
        self.armor_type:     str | None = d.get("armor_type",     None)

    def __repr__(self):
        props = []
        if self.two_handed: props.append("2h")
        if self.light:      props.append("light")
        if self.finesse:    props.append("finesse")
        suffix = f", {', '.join(props)}" if props else ""
        return f"Weapon({self.name!r}, dice={self.dice!r}{suffix})"


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
        self.is_shield:           bool  = False   # containers are never shields

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
