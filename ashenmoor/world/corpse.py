"""
ashenmoor.world.corpse
───────────────────────
Corpse — left in the room when a mob dies.

A Corpse is a specialised Container that:
  • Displays the mob's name in examine output
  • Lists everything that was in the mob's inventory and equipment
  • Holds any coins the mob was carrying as a takeable Coin item
  • Decays after a configurable number of ticks (default 10 ≈ 40 seconds)
  • Cannot be picked up (take = False) but its contents can be looted

Decay
─────
The server calls corpse.tick() every combat tick (4 seconds).
When ticks_remaining reaches 0 the corpse removes itself from the room
and returns True so the tick loop knows to clean up.

Coins
─────
If the mob had coins, a single Coin object is placed inside the corpse.
Players use  get coins corpse  or  get all corpse  to loot it.
The Coin object is takeable and goes straight into the player's inventory;
game.py's existing _cmd_get handles the container-loot path already.

Zone template — mob with gear
─────────────────────────────
Add "inventory" and/or "equipment" keys to the mob template dict.
Each value is a list of object template dicts (same format as Item/Weapon):

    "goblin_warrior": {
        "name":  "a goblin warrior",
        ...
        "inventory": [
            {"type": "Item", "name": "a bread crust", "key_words": ["bread","crust"],
             "room_description": "", "description": "Stale.", "weight": 0.1},
        ],
        "equipment": {
            "primary_hand": {
                "type": "Weapon", "name": "a rusty short sword",
                "key_words": ["rusty","sword","short"],
                "room_description": "", "description": "Pitted with rust.",
                "dice": "1d6", "hitroll": -1, "damroll": -1, "weight": 3,
            },
            "on_body": {
                "type": "Item", "name": "a tattered leather jerkin",
                "key_words": ["tattered","leather","jerkin"],
                "room_description": "", "description": "Barely holding together.",
                "wear_on": "on_body", "ac_bonus": 5, "weight": 4,
                "armor_type": "leather",
            },
        },
        "coins": {"gold": 2, "silver": 5, "copper": 0},
    }
"""

from __future__ import annotations
import time

from .objects import Container, Item, Weapon, Object

# How many 4-second ticks before a corpse vanishes (75 ticks = 300 s = 5 minutes)
DEFAULT_DECAY_TICKS = 75


def _make_item(d: dict):
    """Instantiate the right class from a plain template dict."""
    t = d.get("type", "Item")
    if t == "Weapon":
        return Weapon(d)
    if t == "Item":
        return Item(d)
    return Object(d)


class CoinItem(Item):
    """
    A bundle of coins that can be picked up and merged into the
    player's coin purse.  Handled specially by game.py on get.
    """

    def __init__(self, coins: dict):
        self.gold   = max(0, int(coins.get("gold",   0)))
        self.silver = max(0, int(coins.get("silver", 0)))
        self.copper = max(0, int(coins.get("copper", 0)))

        parts = []
        if self.gold:   parts.append(f"&W{self.gold}&w gold&N")
        if self.silver: parts.append(f"&W{self.silver}&w silver&N")
        if self.copper: parts.append(f"&W{self.copper}&w copper&N")
        label = ", ".join(parts) if parts else "some coins"

        super().__init__({
            "name":             label,
            "key_words":        ("coins", "coin", "gold", "silver", "copper",
                                 "money", "loot"),
            "room_description": f"{label} lies here.",
            "description":      f"A pile of coins: {label}.",
            "weight":           0.1 * (self.gold + self.silver + self.copper),
            "wear_on":          None,
        })
        # override take=True (set by Item.__init__ via wear_on=None check)
        self.take = True
        self._is_coins = True   # flag for game.py to detect

    # Bypass the wear_on validation in Item.__init__
    # We pass wear_on=None which is fine — coins aren't wearable.


class Corpse(Container):
    """
    A mob's remains.  Placed in the room by game.py on mob death.

    Parameters
    ----------
    mob         : Mob    the dead mob (stats/name read but not referenced after)
    decay_ticks : int    ticks until the corpse vanishes
    """

    def __init__(self, mob, decay_ticks: int = DEFAULT_DECAY_TICKS):
        mob_name_plain = _strip_color(mob.name)

        super().__init__({
            "name":             f"the corpse of {mob.name}",
            "key_words":        ("corpse", "body",
                                 *mob_name_plain.lower().split()),
            "room_description": f"The corpse of {mob.name} lies here.",
            "description":      (
                f"The lifeless body of {mob.name}.\n"
                f"You could search it for valuables."
            ),
            "capacity":         500.0,
            "weightless_capacity": 0.0,
            "is_open":          True,
            "weight":           0,
            "wear_on":          None,
        })

        # Corpses cannot be picked up
        self.take         = False
        self.is_corpse    = True
        self.mob_name     = mob.name
        self.ticks_remaining = decay_ticks

        # ── Transfer mob inventory into corpse ────────────────────────────────
        for item in list(getattr(mob, "inventory", [])):
            self.contents.append(item)

        # ── Transfer mob equipment into corpse ────────────────────────────────
        for slot, equipped in list(getattr(mob, "equipment", {}).items()):
            items = equipped if isinstance(equipped, list) else [equipped]
            for item in items:
                if item is not None:
                    self.contents.append(item)

        # ── Add coins ─────────────────────────────────────────────────────────
        coins = getattr(mob, "coins", {})
        total = sum(coins.get(k, 0) for k in ("gold", "silver", "copper"))
        if total > 0:
            self.contents.append(CoinItem(coins))

    # ── Tick ──────────────────────────────────────────────────────────────────

    def tick(self, room) -> bool:
        """
        Called every 4-second combat tick.
        Returns True when the corpse should be removed from the room.
        """
        self.ticks_remaining -= 1
        if self.ticks_remaining <= 0:
            if self in room.objects:
                room.objects.remove(self)
            return True
        return False

    # ── Display ───────────────────────────────────────────────────────────────

    def examine(self) -> str:
        """Rich description shown by 'exa corpse'."""
        lines = [
            f"&wThe corpse of &N{self.mob_name}&w.&N",
            "",
        ]
        if not self.contents:
            lines.append("&wIt has already been looted.&N")
        else:
            lines.append("&wYou search the body and find:&N")
            for item in self.contents:
                lines.append(f"  {item.name}")
        return "\n".join(lines)


# ── Mob template loader ───────────────────────────────────────────────────────

def load_mob_gear(mob, template: dict) -> None:
    """
    Called by Mob.__init__ (or the spawner) to populate a mob's
    inventory and equipment from its template dict.

    inventory key: list of item template dicts
    equipment key: dict of slot → item template dict

    Safe to call even if the keys are absent.
    """
    for item_data in template.get("inventory", []):
        try:
            mob.inventory.append(_make_item(item_data))
        except Exception as exc:
            print(f"[warn] mob {mob.name!r} inventory item error: {exc}")

    for slot, item_data in template.get("equipment", {}).items():
        try:
            item = _make_item(item_data)
            mob.equipment[slot] = item
        except Exception as exc:
            print(f"[warn] mob {mob.name!r} equipment slot {slot!r} error: {exc}")


# ── Utility ───────────────────────────────────────────────────────────────────

def _strip_color(text: str) -> str:
    """Remove Diku color codes for use in keywords."""
    import re
    text = re.sub(r"&&|&[Nn]|&\+?[a-zA-Z]", lambda m: "&" if m.group() == "&&" else "", text)
    text = re.sub(r"\{\{|\{[a-zA-Z]",        lambda m: "{" if m.group() == "{{" else "", text)
    return text
