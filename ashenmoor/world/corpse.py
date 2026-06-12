"""
ashenmoor.world.corpse
───────────────────────
Corpse — left in the room when a mob dies.

Mob inventory/equipment templates support string keys that are resolved
against the zone's object_templates dict (same as room object contents).

Example mob template:
    "my_guard": {
        ...
        "inventory": ["bread_crust", "torch"],          # template key strings
        "equipment": {
            "primary_hand": "iron_sword",               # template key string
            "on_body":      "leather_jerkin",           # template key string
        },
        "coins": {"gold": 2, "silver": 0, "copper": 0},
    }

Raw dicts still work exactly as before — mixing is fine.
"""

from __future__ import annotations
import time

from .objects import Container, Item, Weapon, Object

DEFAULT_DECAY_TICKS = 75


def _make_item(d: dict):
    t = d.get("type", "Item")
    if t == "Weapon":
        return Weapon(d)
    if t == "Item":
        return Item(d)
    return Object(d)


def _resolve_item(entry, object_templates: dict | None):
    """
    Resolve one inventory/equipment entry to an item instance.

    entry may be:
      str  — template key looked up in object_templates
      dict — raw item template dict (legacy / inline)
    """
    if isinstance(entry, str):
        if object_templates and entry in object_templates:
            tmpl = dict(object_templates[entry])
            cls  = tmpl.pop("spawn_as", None)
            if cls is not None:
                obj = cls(tmpl)
                # Resolve nested container contents
                if isinstance(obj, Container) and obj.contents:
                    obj.contents = [
                        _resolve_item(c, object_templates) for c in obj.contents
                    ]
                return obj
            return _make_item(tmpl)
        # Unknown key — return a placeholder item so we don't crash
        import warnings
        warnings.warn(f"load_mob_gear: unknown object template key {entry!r}")
        return None
    elif isinstance(entry, dict):
        return _make_item(entry)
    return None


class CoinItem(Item):
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
        self.take      = True
        self._is_coins = True


class Corpse(Container):
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
            "capacity":            500.0,
            "weightless_capacity": 0.0,
            "is_open":          True,
            "weight":           0,
            "wear_on":          None,
        })

        self.take             = False
        self.is_corpse        = True
        self.mob_name         = mob.name
        self.ticks_remaining  = decay_ticks

        for item in list(getattr(mob, "inventory", [])):
            self.contents.append(item)

        for slot, equipped in list(getattr(mob, "equipment", {}).items()):
            items = equipped if isinstance(equipped, list) else [equipped]
            for item in items:
                if item is not None:
                    self.contents.append(item)

        coins = getattr(mob, "coins", {})
        total = sum(coins.get(k, 0) for k in ("gold", "silver", "copper"))
        if total > 0:
            self.contents.append(CoinItem(coins))

    def tick(self, room) -> bool:
        self.ticks_remaining -= 1
        if self.ticks_remaining <= 0:
            if self in room.objects:
                room.objects.remove(self)
            return True
        return False

    def examine(self) -> str:
        lines = [f"&wThe corpse of &N{self.mob_name}&w.&N", ""]
        if not self.contents:
            lines.append("&wIt has already been looted.&N")
        else:
            lines.append("&wYou search the body and find:&N")
            for item in self.contents:
                lines.append(f"  {item.name}")
        return "\n".join(lines)


def load_mob_gear(mob, template: dict,
                  object_templates: dict | None = None) -> None:
    """
    Populate a mob's inventory and equipment from its template.

    inventory entries may be:
      str  — key into object_templates (zone template reference)
      dict — raw item template dict

    equipment values may be:
      str  — key into object_templates
      dict — raw item template dict
    """
    for entry in template.get("inventory", []):
        item = _resolve_item(entry, object_templates)
        if item is not None:
            try:
                mob.inventory.append(item)
            except Exception as exc:
                print(f"[warn] mob {mob.name!r} inventory item error: {exc}")

    for slot, entry in template.get("equipment", {}).items():
        item = _resolve_item(entry, object_templates)
        if item is not None:
            try:
                mob.equipment[slot] = item
            except Exception as exc:
                print(f"[warn] mob {mob.name!r} equipment slot {slot!r} error: {exc}")


def _strip_color(text: str) -> str:
    import re
    text = re.sub(r"&&|&[Nn]|&\+?[a-zA-Z]",
                  lambda m: "&" if m.group() == "&&" else "", text)
    text = re.sub(r"\{\{|\{[a-zA-Z]",
                  lambda m: "{" if m.group() == "{{" else "", text)
    return text
