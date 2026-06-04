"""
ashenmoor.world.effects
───────────────────────
Status effect system.

Every effect is a plain dict with a fixed schema.  Active effects are
stored on char.status_effects as a list of copies of these templates.
The engine calls tick_effects() every combat tick (4 seconds).

Effect schema
─────────────
{
    "id":        str   — unique id for stack/refresh lookup
    "name":      str   — display name shown in score
    "duration":  int   — ticks remaining; -1 = permanent
    "stat_mods": dict  — {stat: int} additive modifiers e.g. {"dex": 10}
    "ac_mod":    int   — flat AC bonus/penalty — stacks across all effects
    "dr_pct":    int   — damage reduction as % of max HP per hit (cap 75)
    "dot_dice":  str   — random damage per tick e.g. "1d6"
    "dot_flat":  int   — fixed damage per tick e.g. 10
    "hot_dice":  str   — random healing per tick e.g. "1d8"
    "hot_flat":  int   — fixed healing per tick e.g. 15
    "dot_type":  str   — flavour label used in messages and display
    "tick_msg":  str   — shown each tick while active (empty = silent)
    "apply_msg": str   — shown on application
    "expire_msg":str   — shown on expiry
    "flags":     set   — optional tags: "no_dispel", "hidden"
}

Stacking
────────
All ac_mod values are summed across active effects.
All stat_mods are summed per-stat across active effects.
dr_pct values are summed (capped at 75%).
dot_flat + dot_dice and hot_flat + hot_dice are each applied independently
per effect every tick — the net HP change is the sum of all of them.

Example:
  Barkskin  ac_mod=+15
  Armor     ac_mod=+10
  Broken    ac_mod=-10
  Net AC bonus = +15

  Bleeding  dot_flat=10  (loses 10 hp/tick)
  HealAura  hot_flat=15  (gains 15 hp/tick)
  Net per tick = +5 hp — when HealAura expires, back to -10/tick
"""

from __future__ import annotations
import random


# ── Dice helper ───────────────────────────────────────────────────────────────

def _roll(dice_str: str) -> int:
    """Roll NdS or NdS+K dice string."""
    s = dice_str.lower().strip()
    bonus = 0
    if "+" in s:
        s, b  = s.split("+", 1)
        bonus = int(b)
    elif "-" in s:
        s, b  = s.split("-", 1)
        bonus = -int(b)
    n, sides = s.split("d")
    return sum(random.randint(1, int(sides)) for _ in range(int(n))) + bonus


def _dot_per_tick(eff: dict) -> int:
    """Total damage this effect deals per tick (flat + dice roll)."""
    total = eff.get("dot_flat", 0)
    if eff.get("dot_dice"):
        total += _roll(eff["dot_dice"])
    return total


def _hot_per_tick(eff: dict) -> int:
    """Total healing this effect provides per tick (flat + dice roll)."""
    total = eff.get("hot_flat", 0)
    if eff.get("hot_dice"):
        total += _roll(eff["hot_dice"])
    return total


# ── Effect definitions ────────────────────────────────────────────────────────

POISON: dict = {
    "id":        "poisoned",
    "name":      "Poisoned",
    "duration":  10,
    "stat_mods": {},
    "ac_mod":    0,
    "dr_pct":    0,
    "dot_dice":  "1d6",
    "dot_flat":  0,
    "hot_dice":  "",
    "hot_flat":  0,
    "dot_type":  "poison",
    "tick_msg":    "&cYou feel a burning sensation in your blood.&N",
    "room_msg":"&c{name} shivers as the poison spreads through its veins.&N",
    "apply_msg": "&cYou feel a burning sensation — you have been poisoned!&N",
    "expire_msg":"&GThe poison works its way out of your system.&N",
    "flags":     set(),
}

BLEED: dict = {
    "id":        "bleeding",
    "name":      "Bleeding",
    "duration":  5,
    "stat_mods": {},
    "ac_mod":    0,
    "dr_pct":    0,
    "dot_dice":  "",
    "dot_flat":  10,
    "hot_dice":  "",
    "hot_flat":  0,
    "dot_type":  "bleed",
    "tick_msg":    "&cYou bleed profusely from your wounds.&N",
    "room_msg":"&c{name} bleeds from its wounds.&N",
    "apply_msg": "&cYou begin to bleed!&N",
    "expire_msg":"&wYour wounds stop bleeding.&N",
    "flags":     set(),
}

HEALING_AURA: dict = {
    "id":        "healing_aura",
    "name":      "Healing Aura",
    "duration":  8,
    "stat_mods": {},
    "ac_mod":    0,
    "dr_pct":    0,
    "dot_dice":  "",
    "dot_flat":  0,
    "hot_dice":  "",
    "hot_flat":  15,
    "dot_type":  "healing",
    "tick_msg":  "&GA warm glow surrounds you, mending your wounds.&N",
    "room_msg":  "&G{name} glows with healing energy.&N",
    "apply_msg": "&GA healing aura envelops you.&N",
    "expire_msg":"&wThe healing aura fades.&N",
    "flags":     set(),
}

BARKSKIN: dict = {
    "id":        "barkskin",
    "name":      "Barkskin",
    "duration":  20,
    "stat_mods": {},
    "ac_mod":    15,
    "dr_pct":    0,
    "dot_dice":  "",
    "dot_flat":  0,
    "hot_dice":  "",
    "hot_flat":  0,
    "dot_type":  "",
    "tick_msg":  "",
    "room_msg":  "",
    "apply_msg": "&GYour skin hardens like bark.&N",
    "expire_msg":"&wYour skin softens back to normal.&N",
    "flags":     set(),
}

STONESKIN: dict = {
    "id":        "stoneskin",
    "name":      "Stoneskin",
    "duration":  20,
    "stat_mods": {},
    "ac_mod":    10,
    "dr_pct":    10,
    "dot_dice":  "",
    "dot_flat":  0,
    "hot_dice":  "",
    "hot_flat":  0,
    "dot_type":  "",
    "tick_msg":  "",
    "room_msg":  "",
    "apply_msg": "&WYour skin turns to stone.&N",
    "expire_msg":"&wYour skin returns to normal.&N",
    "flags":     set(),
}

# Registry — id → template dict
EFFECTS: dict[str, dict] = {
    "poisoned":     POISON,
    "bleeding":     BLEED,
    "healing_aura": HEALING_AURA,
    "barkskin":     BARKSKIN,
    "stoneskin":    STONESKIN,
}


# ── Application ───────────────────────────────────────────────────────────────

def apply_effect(char, effect: dict) -> str:
    """
    Apply or refresh a status effect on a character.
    Refreshes duration if already active.
    Returns the message to show the player.
    """
    effects  = _ensure(char)
    existing = next((e for e in effects if e["id"] == effect["id"]), None)
    if existing:
        existing["duration"] = max(existing["duration"], effect["duration"])
        return f"&c{effect['name']} refreshes its grip on you.&N"
    effects.append(dict(effect))
    recalc_status(char)
    return effect.get("apply_msg", "")


def remove_effect(char, effect_id: str) -> str | None:
    """
    Forcibly remove an effect by id (dispel, cure, etc).
    Returns expire_msg or None if not present.
    """
    effects  = _ensure(char)
    existing = next((e for e in effects if e["id"] == effect_id), None)
    if not existing:
        return None
    effects.remove(existing)
    recalc_status(char)
    return existing.get("expire_msg", "")


# ── Tick ──────────────────────────────────────────────────────────────────────

def tick_effects(char) -> tuple[list[str], list[str]]:
    """
    Called every combat tick (4 seconds) for any character -- PC or NPC.

    Returns (self_msgs, room_msgs):
      self_msgs  -- tick_msg strings shown to the affected character
      room_msgs  -- room_msg strings (with {name} formatted) shown to observers
    """
    effects = _ensure(char)
    if not effects:
        return [], []

    self_msgs:  list[str] = []
    room_msgs_: list[str] = []
    expired = []

    for eff in effects:
        dmg  = _dot_per_tick(eff)
        heal = _hot_per_tick(eff)

        if dmg > 0:
            char.hp = max(0, char.hp - dmg)
            tick = eff.get("tick_msg")
            if tick: self_msgs.append(tick)
            room = eff.get("room_msg", "")
            if room: room_msgs_.append(room.format(name=char.name))

        if heal > 0:
            char.hp = min(getattr(char, "max_hp", char.hp), char.hp + heal)
            if not dmg:
                tick = eff.get("tick_msg")
                if tick: self_msgs.append(tick)
                room = eff.get("room_msg", "")
                if room: room_msgs_.append(room.format(name=char.name))

        if eff["duration"] > 0:
            eff["duration"] -= 1
            if eff["duration"] == 0:
                expired.append(eff)

    for eff in expired:
        effects.remove(eff)
        msg = eff.get("expire_msg")
        if msg: self_msgs.append(msg)

    if expired:
        recalc_status(char)

    return self_msgs, room_msgs_


# ── Stat recalculation ────────────────────────────────────────────────────────

def recalc_status(char) -> None:
    """
    Sum all active effect modifiers and store on the character.
    Called after any effect is applied or expires.

    char.effect_stats  — dict of additive stat bonuses
    char.effect_ac     — total flat AC modifier from all effects
    char.effect_dr     — total damage reduction % (capped 75)
    """
    effects      = _ensure(char)
    effect_stats: dict[str, int] = {}
    effect_ac    = 0
    effect_dr    = 0

    for eff in effects:
        for stat, val in (eff.get("stat_mods") or {}).items():
            effect_stats[stat] = effect_stats.get(stat, 0) + val
        effect_ac += eff.get("ac_mod", 0)
        effect_dr += eff.get("dr_pct", 0)

    char.effect_stats = effect_stats
    char.effect_ac    = effect_ac
    char.effect_dr    = min(75, effect_dr)


# ── Combat helpers ────────────────────────────────────────────────────────────

def apply_dr(char, damage: int) -> int:
    """
    Reduce incoming damage by the character's total damage reduction.
    DR = sum of all active dr_pct values, capped at 75%.
    Expressed as percentage of max HP absorbed per hit.
    """
    dr = getattr(char, "effect_dr", 0)
    if dr <= 0:
        return damage
    absorbed = int(getattr(char, "max_hp", 100) * dr / 100)
    return max(0, damage - absorbed)


def effective_stat(char, stat: str) -> int:
    """Return a stat with all active effect modifiers applied, clamped 0-100."""
    base  = char.stats.get(stat, 10)
    bonus = getattr(char, "effect_stats", {}).get(stat, 0)
    return max(0, min(100, base + bonus))


# ── Score display ─────────────────────────────────────────────────────────────

def format_effects(char) -> str | None:
    """
    Format active effects for the score command.
    Shows each effect with its duration and modifiers.
    Shows net HP-per-tick when multiple DoT/HoT effects are active.
    Returns None if no active effects.
    """
    effects = _ensure(char)
    if not effects:
        return None

    lines = [
        "&wYou are affected by:&N",
        "&w" + "─" * 56 + "&N",
    ]

    total_dot = 0
    total_hot = 0

    for eff in effects:
        name  = eff.get("name", "?")
        dur   = eff.get("duration", 0)
        parts = []

        # DoT description
        dot_d = eff.get("dot_dice", "")
        dot_f = eff.get("dot_flat", 0)
        if dot_d and dot_f:
            parts.append(f"{dot_d}+{dot_f} {eff.get('dot_type','damage')}/tick")
        elif dot_d:
            parts.append(f"{dot_d} {eff.get('dot_type','damage')}/tick")
        elif dot_f:
            parts.append(f"{dot_f} {eff.get('dot_type','damage')}/tick")

        # HoT description
        hot_d = eff.get("hot_dice", "")
        hot_f = eff.get("hot_flat", 0)
        if hot_d and hot_f:
            parts.append(f"{hot_d}+{hot_f} healing/tick")
        elif hot_d:
            parts.append(f"{hot_d} healing/tick")
        elif hot_f:
            parts.append(f"{hot_f} healing/tick")

        for stat, val in (eff.get("stat_mods") or {}).items():
            sign = "+" if val >= 0 else ""
            parts.append(f"{sign}{val} {stat.upper()}")

        if eff.get("ac_mod"):
            sign = "+" if eff["ac_mod"] >= 0 else ""
            parts.append(f"{sign}{eff['ac_mod']} AC")

        if eff.get("dr_pct"):
            parts.append(f"{eff['dr_pct']}% DR")

        detail  = ", ".join(parts) if parts else ""
        dur_str = f"{dur} ticks" if dur > 0 else "permanent"
        color   = "&c" if not (dot_d or dot_f) else "&R"
        if hot_d or hot_f:
            color = "&G"
        lines.append(f"  {color}{name:<18}&N &w{dur_str:<16}&N {detail}")

        # Accumulate net tick totals (use average for dice)
        if dot_f:
            total_dot += dot_f
        if hot_f:
            total_hot += hot_f

    # Net HP summary when multiple tick effects are present
    net_effects = [e for e in effects if e.get("dot_flat") or e.get("hot_flat")
                   or e.get("dot_dice") or e.get("hot_dice")]
    if len(net_effects) > 1:
        net = total_hot - total_dot
        if net > 0:
            lines.append(f"\n  &GNet per tick (flat): +{net} hp&N")
        elif net < 0:
            lines.append(f"\n  &RNet per tick (flat): {net} hp&N")
        else:
            lines.append(f"\n  &wNet per tick (flat): balanced&N")

    # Net AC summary when multiple AC effects present
    ac_effects = [e for e in effects if e.get("ac_mod")]
    if len(ac_effects) > 1:
        net_ac = sum(e.get("ac_mod", 0) for e in effects)
        sign   = "+" if net_ac >= 0 else ""
        lines.append(f"  &wTotal AC from effects: {sign}{net_ac}&N")

    return "\n".join(lines)


# ── Internal ──────────────────────────────────────────────────────────────────

def _ensure(char) -> list:
    """Lazily initialise char.status_effects and return it."""
    if not hasattr(char, "status_effects") or char.status_effects is None:
        char.status_effects = []
    return char.status_effects
