"""
ashenmoor.dnd.classes.fighter
──────────────────────────────
Fighter class — D&D 5.5e (2024).

Replaces the old Warrior class seamlessly. Any character saved as
"Warrior" is migrated to "Fighter" on login via persist.py.

Level mapping  (50-level scale, D&D level × 2.5 rounded up)
─────────────────────────────────────────────────────────────
  D&D  Game  Feature
    1     1  Fighting Style, Second Wind (2/short)
    2     3  Action Surge (1/short)
    3     8  Subclass choice (Champion or Battle Master)
    4    10  ASI
    5    13  Extra Attack ×2
    6    15  ASI
    7    18  Subclass feature
    8    20  ASI
    9    23  Indomitable (2/long) — +20 AC 7 ticks
   11    28  Extra Attack ×3
   12    30  ASI
   13    33  Indomitable (3/long)
   15    38  Subclass feature
   17    43  Action Surge (2/short)
   18    45  Subclass feature
   19    48  ASI / Epic Boon
   20    50  Extra Attack ×4

Subclasses
──────────
  Champion     — Passive combat mastery. Parry roll gets proficiency
                 bonus. 1-in-4 chance to shrug incoming damage to zero.
                 Improved Critical (19-20 at level 18, 18-20 at level 45).

  Battle Master — Superiority Dice (SD) pool fuels combat maneuvers.
                  Passive parry like all fighters.  Riposte arms a
                  counter-attack that fires on the next successful parry,
                  consuming 1 SD.  Pool restores on short rest.

Parry  (passive, all Fighters and Rangers)
───────────────────────────────────────────
  Resolves automatically on every incoming melee hit.
  Roll: (d20 + DEX_mod) × 5  vs  attacker's attack_score
  Champion adds proficiency_bonus to the roll.
  On success: damage reduced by max(0, 2d6 + DEX_mod)
  Champion shrug: on success roll d4; on 4 → zero damage.
  Shrug also triggers riposte if armed (free counter for shrugging it off).

Maneuvers  (Battle Master only)
────────────────────────────────
  One offensive maneuver may fire per combat tick.
  Riposte is pseudo-passive and bypasses the one-per-tick limit.
  Cooldowns are in ticks (4 s each).
  All maneuvers cost 1 SD except Riposte (charges on trigger).

  riposte / ri   — Arms riposte.  Next successful parry or shrug fires a
                   bonus attack with SD bonus damage.  If the battle ends
                   with no parry the SD is NOT consumed.  Resets after
                   triggering or battle end.
  trip           — Hit + SD damage + target -10 AC next tick  (cd 3)
  disarm / dis   — Hit + SD damage + target -hitroll next tick (cd 3)
  precise / pa   — Add SD roll to your attack roll this tick   (cd 2)
  menace / ma    — Hit + SD damage + target skip counter next tick (cd 3)
  rally          — Temp HP = SD + CHA mod, usable any time      (cd 4)
"""

from __future__ import annotations
import random

# ── Level → game level thresholds ─────────────────────────────────────────────

SUBCLASS_LEVEL   = 8    # game level where subclass is chosen
EXTRA_ATK2_LEVEL = 13
EXTRA_ATK3_LEVEL = 28
EXTRA_ATK4_LEVEL = 50
INDOMITABLE_LEVEL = 23
INDOMITABLE3_LEVEL = 33
ACTION_SURGE2_LEVEL = 43

# ── Proficiency bonus ──────────────────────────────────────────────────────────

def proficiency_bonus(level: int) -> int:
    return max(2, (level - 1) // 4 + 2)

# ── Attack count ───────────────────────────────────────────────────────────────

def attack_count(level: int) -> int:
    if level >= EXTRA_ATK4_LEVEL: return 4
    if level >= EXTRA_ATK3_LEVEL: return 3
    if level >= EXTRA_ATK2_LEVEL: return 2
    return 1

# ── Critical hit range ─────────────────────────────────────────────────────────

def crit_range(char) -> int:
    """
    Minimum d20 roll that counts as a critical hit.
    Base: 20.  Champion: 19 at level 18, 18 at level 45.
    """
    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("subclass") != "champion":
        return 20
    if char.level >= 45:
        return 18
    if char.level >= 18:
        return 19
    return 20

# ── Fighting styles ────────────────────────────────────────────────────────────

FIGHTING_STYLES: dict[str, str] = {
    "archery":      "+2 to attack rolls with ranged weapons.",
    "defense":      "+1 AC while wearing armor.",
    "dueling":      "+2 damage when wielding one weapon with no other weapon.",
    "great_weapon": "Reroll 1s and 2s on two-handed weapon damage dice.",
    "protection":   "Use reaction to impose disadvantage on nearby attacks.",
    "two_weapon":   "Add ability modifier to the off-hand attack damage roll.",
}

# ── Features by game level ─────────────────────────────────────────────────────

_FEATURES: dict[int, list[str]] = {
    1:  ["Fighting Style", "Second Wind"],
    3:  ["Action Surge"],
    8:  ["Martial Archetype"],
    10: ["Ability Score Improvement"],
    13: ["Extra Attack (×2)"],
    15: ["Ability Score Improvement"],
    18: ["Archetype Feature"],
    20: ["Ability Score Improvement"],
    23: ["Indomitable"],
    28: ["Extra Attack (×3)"],
    30: ["Ability Score Improvement"],
    33: ["Indomitable (3 uses)"],
    38: ["Archetype Feature"],
    43: ["Action Surge (2 uses)"],
    45: ["Archetype Feature"],
    48: ["Ability Score Improvement / Epic Boon"],
    50: ["Extra Attack (×4)"],
}

def active_features(level: int) -> list[str]:
    feats = []
    for lvl in sorted(_FEATURES):
        if level >= lvl:
            feats.extend(_FEATURES[lvl])
    return feats

# ── Superiority Dice scaling ───────────────────────────────────────────────────

def sd_count(level: int) -> int:
    if level >= 45: return 6
    if level >= 28: return 5
    return 4

def sd_size(level: int) -> int:
    if level >= 45: return 12
    if level >= 28: return 10
    return 8

# ── Subclass help text ─────────────────────────────────────────────────────────

HELP_CHAMPION = """
&+W╔══════════════════════════════════════════════════════╗
║               THE CHAMPION                          ║
╚══════════════════════════════════════════════════════╝&N

&wThe Champion embodies physical perfection — honed to a
razor's edge through relentless training.  No spells,
no tricks.  Just steel and the will to use it.&N

&+WPassive Abilities&N
&w────────────────────────────────────────────────────────&N
  &YParry (Improved)&N
    Your parry roll adds your proficiency bonus on top of
    your DEX modifier.  You are simply harder to hit.

  &YShrug&N
    On every successful parry there is a 1-in-4 chance you
    deflect the blow so completely that you take zero damage.
    A shrug also triggers Riposte if you have it armed.

  &YImproved Critical&N
    &w· Level 18:&N Crits on a roll of 19 or 20.
    &w· Level 45:&N Crits on a roll of 18, 19, or 20.

&+WResources&N
&w────────────────────────────────────────────────────────&N
  No extra resource pools — the Champion's power is
  always on.  Manage your Second Wind, Action Surge,
  and Indomitable as a base Fighter.

&+WBest For&N
&w────────────────────────────────────────────────────────&N
  Players who want straightforward, reliable combat
  without tracking dice pools or maneuver cooldowns.
  The Champion rewards good positioning and timing over
  resource management.
"""

HELP_BATTLEMASTER = """
&+W╔══════════════════════════════════════════════════════╗
║             THE BATTLE MASTER                       ║
╚══════════════════════════════════════════════════════╝&N

&wThe Battle Master is a tactician who turns every
exchange into an opportunity.  Superiority Dice fuel
a set of combat maneuvers — debuffs, counters, and
finishers — that keep enemies off-balance.&N

&+WSuperiority Dice (SD)&N
&w────────────────────────────────────────────────────────&N
  A pool of dice that power your maneuvers.
  &w· Level  8–27:&N  4d8
  &w· Level 28–44:&N  5d10
  &w· Level 45–50:&N  6d12
  Restores fully on &Gshort rest&N.
  One offensive maneuver per combat tick (Riposte excepted).

&+WManeuvers&N
&w────────────────────────────────────────────────────────&N
  &Yriposte &x(ri)&N        &wArm a counter.  Next successful
                       parry or shrug fires a bonus attack
                       with +SD damage.  SD only consumed
                       on trigger.  Resets if battle ends
                       with no parry.&N

  &Ytrip               &wHit + SD damage.  Target loses
                       &W-10 AC&w for one tick.          &x(cd 3)&N

  &Ydisarm &x(dis)&N        &wHit + SD damage.  Target suffers
                       &W-hitroll&w penalty next tick.    &x(cd 3)&N

  &Yprecise &x(pa)&N        &wAdd SD roll to YOUR attack roll
                       this tick before resolution.     &x(cd 2)&N

  &Ymenace &x(ma)&N         &wHit + SD damage.  Target skips
                       their counter-attack this tick.  &x(cd 3)&N

  &Yrally               &wGain temp HP equal to SD + CHA mod.
                       Shown in &Mmagenta&N on your HP bar.   &x(cd 4)&N

&+WBest For&N
&w────────────────────────────────────────────────────────&N
  Players who enjoy active decision-making in combat.
  High ceiling — knowing when to trip vs menace vs
  riposte separates good Battle Masters from great ones.
"""

# ── DND state constructors ─────────────────────────────────────────────────────

def new_battlemaster_state(level: int) -> dict:
    """Battle Master additions merged into the base dnd dict."""
    return {
        "superiority_dice":     sd_count(level),
        "superiority_dice_max": sd_count(level),
        "superiority_die_size": sd_size(level),
        "maneuver_used":        False,
        "riposte_armed":        False,
        "maneuver_cooldowns": {
            "trip":    0,
            "disarm":  0,
            "precise": 0,
            "menace":  0,
            "rally":   0,
        },
        "target_debuffs": {
            "ac_penalty":  0,
            "hit_penalty": 0,
            "no_counter":  False,
        },
    }


def new_fighter_dnd(
    level:          int = 1,
    fighting_style: str = "dueling",
    subclass:       str | None = None,
) -> dict:
    """
    Build a fresh dnd state dict for a Fighter.

    subclass is None until the player chooses at level 8.
    Passing subclass here populates the appropriate extra state.
    """
    surge_uses  = 2 if level >= ACTION_SURGE2_LEVEL else (1 if level >= 3 else 0)
    indom_uses  = (3 if level >= INDOMITABLE3_LEVEL else 2) if level >= INDOMITABLE_LEVEL else 0

    # Flag so login flow knows to prompt for subclass
    subclass_pending = (subclass is None and level >= SUBCLASS_LEVEL)

    base: dict = {
        "class":    "fighter",
        "subclass": subclass,
        "subclass_pending": subclass_pending,

        # Hit dice
        "hit_die":            10,
        "hit_dice_remaining": level,

        # Fighting style
        "fighting_style": fighting_style,

        # Saving throw proficiencies
        "saving_throw_proficiencies": ["str", "con"],

        # Short-rest abilities
        "second_wind_uses": 2,
        "second_wind_max":  2,
        "action_surge_uses": surge_uses,
        "action_surge_max":  surge_uses,
        "action_surge_active": False,

        # Long-rest abilities
        "indomitable_uses": indom_uses,
        "indomitable_max":  indom_uses,
    }

    if subclass == "battle_master":
        base.update(new_battlemaster_state(level))

    return base


def apply_subclass(char, subclass: str) -> None:
    """
    Apply subclass choice to an existing character in-place.
    Called from the subclass selection flow.
    """
    dnd = getattr(char, "dnd", {}) or {}
    dnd["subclass"]         = subclass
    dnd["subclass_pending"] = False

    if subclass == "battle_master":
        bm = new_battlemaster_state(char.level)
        for k, v in bm.items():
            dnd.setdefault(k, v)   # don't overwrite existing charges

    char.dnd    = dnd
    char.cclass = "Fighter"

    # Rebuild powers list to include subclass powers
    from ashenmoor.dnd.classes.fighter import FIGHTER_POWERS, BATTLEMASTER_POWERS
    char.powers = list(FIGHTER_POWERS)
    if subclass == "battle_master":
        char.powers += BATTLEMASTER_POWERS


# ── Power definitions ──────────────────────────────────────────────────────────

FIGHTER_POWERS: list[dict] = [

    {
        "keywords":    ("secondwind", "sw"),
        "name":        "Second Wind",
        "charges_key": "second_wind_uses",
        "rest_type":   "short",
        "effect":      "second_wind",
        "user_msg":    "&+GYou draw on your fighting spirit to recover some health!&N",
        "room_msg":    "&+G{name} draws on inner strength and looks healthier!&N",
    },

    {
        "keywords":    ("actionsurge", "surge", "as"),
        "name":        "Action Surge",
        "charges_key": "action_surge_uses",
        "rest_type":   "short",
        "effect":      "action_surge",
        "user_msg":    "&+WYou surge with unstoppable energy — "
                       "your next round of attacks will be devastating!&N",
        "room_msg":    "&+W{name} surges with terrifying energy!&N",
    },

    {
        "keywords":    ("indomitable", "ind"),
        "name":        "Indomitable",
        "charges_key": "indomitable_uses",
        "rest_type":   "long",
        "effect":      "indomitable",
        "user_msg":    "&+YYour indomitable will hardens your defenses!&N",
        "room_msg":    "&+Y{name}'s form seems to harden, becoming harder to strike!&N",
    },

]

BATTLEMASTER_POWERS: list[dict] = [

    {
        "keywords":    ("riposte", "ri"),
        "name":        "Riposte",
        "effect":      "riposte_arm",
        # No charges_key — SD consumed on trigger, not on arming
        "cooldown_ticks": 0,   # no cooldown to arm, only one can be armed at a time
        "user_msg":    "&+WYou ready yourself to answer the next blow with steel!&N",
        "room_msg":    "&+W{name} shifts into a ready counter-stance!&N",
    },

    {
        "keywords":    ("trip",),
        "name":        "Trip Attack",
        "effect":      "maneuver_trip",
        "sd_cost":     1,
        "cooldown_ticks": 3,
        "user_msg":    "&+WYou drive your strike low, sweeping your foe off balance!&N",
        "room_msg":    "&+W{name} sweeps their foe off balance!&N",
    },

    {
        "keywords":    ("disarm", "dis"),
        "name":        "Disarming Strike",
        "effect":      "maneuver_disarm",
        "sd_cost":     1,
        "cooldown_ticks": 3,
        "user_msg":    "&+WYou knock at your foe's weapon hand!&N",
        "room_msg":    "&+W{name} strikes at their foe's weapon hand!&N",
    },

    {
        "keywords":    ("precise", "pa"),
        "name":        "Precision Attack",
        "effect":      "maneuver_precise",
        "sd_cost":     1,
        "cooldown_ticks": 2,
        "user_msg":    "&+WYou focus your strike, guiding your weapon with perfect accuracy!&N",
        "room_msg":    "&+W{name} lines up a precise, deliberate strike!&N",
    },

    {
        "keywords":    ("menace", "ma"),
        "name":        "Menacing Attack",
        "effect":      "maneuver_menace",
        "sd_cost":     1,
        "cooldown_ticks": 3,
        "user_msg":    "&+WYou strike with terrifying force, driving fear into your foe!&N",
        "room_msg":    "&+W{name} unleashes a terrifying strike!&N",
    },

    {
        "keywords":    ("rally",),
        "name":        "Rally",
        "effect":      "maneuver_rally",
        "sd_cost":     1,
        "cooldown_ticks": 4,
        "user_msg":    "&+GYou steel yourself, drawing on reserves of endurance!&N",
        "room_msg":    "&+G{name} rallies, steeling themselves against the fight!&N",
    },

]

# ── Great Weapon Fighting reroll ───────────────────────────────────────────────

def great_weapon_reroll(dice_results: list[int], die_size: int) -> list[int]:
    return [
        random.randint(1, die_size) if d <= 2 else d
        for d in dice_results
    ]

# ── Backwards-compat alias ─────────────────────────────────────────────────────
# Old code that imports WARRIOR_POWERS or new_warrior_dnd still works.

WARRIOR_POWERS = FIGHTER_POWERS

def new_warrior_dnd(level: int = 1, fighting_style: str = "dueling") -> dict:
    return new_fighter_dnd(level=level, fighting_style=fighting_style)
