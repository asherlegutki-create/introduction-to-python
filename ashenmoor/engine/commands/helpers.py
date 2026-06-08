"""
ashenmoor.engine.commands.helpers
──────────────────────────────────
Shared helper functions used across command submodules.
"""

from __future__ import annotations


# ── Slot-full messages ────────────────────────────────────────────────────────

_SLOT_FULL: dict[str, str] = {
    "head":           "&wYou can wear nothing more on your head.&N",
    "face":           "&wYou can wear nothing more on your face.&N",
    "neck":           "&wYou can wear nothing more around your neck.&N",
    "on_body":        "&wYou can wear nothing more on your body.&N",
    "about_body":     "&wYou can wear nothing more about your body.&N",
    "back":           "&wYou can wear nothing more on your back.&N",
    "arms":           "&wYou can wear nothing more on your arms.&N",
    "hands":          "&wYou can wear nothing more on your hands.&N",
    "waist":          "&wYou can wear nothing more about your waist.&N",
    "legs":           "&wYou can wear nothing more on your legs.&N",
    "feet":           "&wYou can wear nothing more on your feet.&N",
    "wrist":          "&wYou can wear nothing more on your wrists.&N",
    "ring":           "&wYou can wear nothing more on your fingers.&N",
    "earring":        "&wYou can wear nothing more on your ears.&N",
    "light":          "&wYou are already holding a light source.&N",
    "floating":       "&wNothing more may float nearby.&N",
    "primary_hand":   "&wYou may wield no more weapons.&N",
    "secondary_hand": "&wYour off hand is already occupied.&N",
}

def slot_full_msg(slot: str) -> str:
    return _SLOT_FULL.get(slot, "&wThat slot is already in use.&N")


# ── Combat message personalisation ───────────────────────────────────────────

_VERB_MAP: list[tuple[str, str]] = [
    ("fumbles and misses completely", "fumble and miss completely"),
    ("barely scratches",              "barely scratch"),
    ("hits very hard",                "hit very hard"),
    ("hits hard",                     "hit hard"),
    ("scratches",                     "scratch"),
    ("hits",                          "hit"),
    ("misses",                        "miss"),
    ("devastates",                    "devastate"),
    ("massacres",                     "massacre"),
    ("nearly slays",                  "nearly slay"),
    ("obliterates",                   "obliterate"),
]

def personalize_msg(msg: str, player_name: str) -> str:
    """Rewrite a combat message to second person when the player is the actor or target."""
    possessive = f"&w{player_name}&N's"
    if possessive in msg:
        return msg.replace(possessive, "&wYour&N", 1)

    subject = f"&w{player_name}&N"
    if subject in msg:
        msg = msg.replace(subject, "&wYou&N", 1)
        for third, second in _VERB_MAP:
            if third in msg:
                return msg.replace(third, second, 1)
        return msg

    defender_ref = f"&N{player_name}&w"
    if defender_ref in msg:
        return msg.replace(defender_ref, "&Nyou&w", 1)

    return msg


# ── Inventory helpers ─────────────────────────────────────────────────────────

def max_inventory(char) -> int:
    """
    Maximum items a character can carry, based on computed DEX.
    Formula: 8 + max(0, (dex - 41) // 10)
    """
    dex   = char.computed_stat("dex")
    bonus = max(0, (dex - 41) // 10)
    return 8 + bonus


def stack_items(items) -> list[str]:
    """Group items by name, returning display lines with [N] prefix for stacks > 1."""
    order  = []
    counts = {}
    for item in items:
        key = item.name
        if key not in counts:
            order.append(key)
            counts[key] = 0
        counts[key] += 1
    lines = []
    for key in order:
        n = counts[key]
        if n > 1:
            lines.append(f"&w[&W{n}&w]&N {key}")
        else:
            lines.append(key)
    return lines


def merge_coins(char, coin_item) -> None:
    """Add a CoinItem's values directly into the character's coin purse."""
    purse = getattr(char, "coins", None)
    if purse is None:
        char.coins = {"gold": 0, "silver": 0, "copper": 0}
        purse = char.coins
    purse["gold"]   = purse.get("gold",   0) + getattr(coin_item, "gold",   0)
    purse["silver"] = purse.get("silver", 0) + getattr(coin_item, "silver", 0)
    purse["copper"] = purse.get("copper", 0) + getattr(coin_item, "copper", 0)


# ── Item finders ──────────────────────────────────────────────────────────────

def item_matches(item, keyword: str) -> bool:
    if hasattr(item, "key_words"):
        if keyword in (k.lower() for k in item.key_words):
            return True
    return keyword in item.name.lower()


def find_container(target_str, char, room):
    from ...engine.targeting import parse_target
    idx, keyword = parse_target(target_str)
    matches = 0
    if char is not None:
        for item in reversed(char.inventory):
            if item_matches(item, keyword):
                matches += 1
                if matches == idx:
                    return item
    if room is not None:
        for obj in reversed(room.objects):
            if item_matches(obj, keyword):
                matches += 1
                if matches == idx:
                    return obj
    return None


def find_in_container(target_str, container):
    from ...engine.targeting import parse_target
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in reversed(container.contents):
        if item_matches(item, keyword):
            matches += 1
            if matches == idx:
                return item
    return None


def find_in_inventory(target_str, char):
    from ...engine.targeting import parse_target
    idx, keyword = parse_target(target_str)
    matches = 0
    for item in reversed(char.inventory):
        if item_matches(item, keyword):
            matches += 1
            if matches == idx:
                return item
    return None


def find_in_equipment(target_str, char):
    from ...world.equipment import DUAL_SLOTS
    from ...engine.targeting import parse_target
    _, keyword = parse_target(target_str)
    for slot, equipped in char.equipment.items():
        if slot in DUAL_SLOTS:
            for item in (equipped if isinstance(equipped, list) else [equipped]):
                if item_matches(item, keyword):
                    return item, slot
        else:
            if equipped and item_matches(equipped, keyword):
                return equipped, slot
    return None, None


# ── Container display ─────────────────────────────────────────────────────────

def look_in_container(c) -> str:
    if not c.is_open:
        return f"&N{c.name}&w is closed.&N"
    if not c.contents:
        return f"&wYou look in &N{c.name}&w, it is empty.&N"
    lines = stack_items(list(reversed(c.contents)))
    return "\n".join([f"&wYou look in &N{c.name}&w, it contains:&N"] + [f"  {l}" for l in lines])


def examine_container(c) -> str:
    lines = []
    if c.description:
        lines.append(c.description)
    lines.append(f"&wIt can hold about &W{int(c.available_capacity)}&w more lbs.&N")
    lines.append(look_in_container(c))
    return "\n".join(lines)


# ── Pronoun helper ────────────────────────────────────────────────────────────

def pronouns(char) -> dict[str, str]:
    if getattr(char, "sex", "male").lower() == "female":
        return {"subject": "she", "object": "her",
                "possessive": "her", "reflexive": "herself"}
    return {"subject": "he", "object": "him",
            "possessive": "his", "reflexive": "himself"}
