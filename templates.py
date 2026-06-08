"""
ashenmoor.world.templates
─────────────────────────
Reference template dictionaries for all zone-definable objects.

Copy the relevant dict into your zone file and remove or fill
every field.  Fields marked REQUIRED must be present.
Fields marked OPTIONAL can be omitted; the default shown is used.

Usage
─────
from ashenmoor.world.templates import MOB, WEAPON, ARMOR   # etc.
import copy
my_mob = copy.deepcopy(MOB)
my_mob.update({"name": "a goblin", "level": 3, ...})

Color codes in strings
──────────────────────
&N  reset        &w  white     &W  bold white
&r  red          &R  bold red  &+R bright red
&g  green        &G  bold grn  &b  blue    &B  bold blue
&y  yellow       &Y  bold yel  &c  cyan    &C  bold cyan
&m  magenta      &M  bold mag  &x  dark grey
"""

# ══════════════════════════════════════════════════════════════════════════════
# ROOM
# ══════════════════════════════════════════════════════════════════════════════

ROOM: dict = {
    # ── Required ──────────────────────────────────────────────────────────────
    "name":        "&+LA Room Name&N",     # REQUIRED — shown in look header
    "description": "A description of the room.",  # REQUIRED — body of look

    # ── Exits ─────────────────────────────────────────────────────────────────
    # Keys: "n" "e" "s" "w" "u" "d"
    # dest     REQUIRED vnum of the destination room
    # desc     OPTIONAL brief exit description (shown in "look north")
    # door     OPTIONAL True → exit has a door that can be opened/closed
    # key_vnum OPTIONAL vnum of the key item (-1 = no key needed)
    "exits": {
        "n": {"dest": 0},
        # "e": {"dest": 0, "desc": "A path leads east.", "door": True, "key_vnum": -1},
    },

    # ── Extra descriptions ─────────────────────────────────────────────────────
    # Examined when player types "look <keyword>" in the room.
    "extra_descs": [
        # {"keywords": ["sign", "board"], "description": "A wooden sign reads..."},
    ],

    # ── Flags (optional) ──────────────────────────────────────────────────────
    # 0   = normal outdoor room
    # 1   = indoor (no weather)
    # 2   = safe (no combat)
    # 4   = no-magic
    # 8   = indoors + no-recall
    # 16  = wilderness/outdoor
    "flags":  0,

    # ── Sector type (optional) ────────────────────────────────────────────────
    # 0=inside  1=city  2=field  3=forest  4=hills  5=mountain
    # 6=water   7=deep_water  8=underwater  9=air  10=desert
    "sector": 0,
}


# ══════════════════════════════════════════════════════════════════════════════
# MOB  (Non-player character)
# ══════════════════════════════════════════════════════════════════════════════

MOB: dict = {
    # ── Identity ──────────────────────────────────────────────────────────────
    "name":             "&+wa mob&N",           # REQUIRED — combat / room name
    "room_description": "&+wA mob stands here.&N",  # What appears in room list
    "key_words":        ["mob"],                # Targeting keywords (lowercase)
    "description":      "A nondescript creature.",  # Seen when you look AT it

    # ── Character stats ───────────────────────────────────────────────────────
    "race":    "Human",    # Race key — unknown races treated as Human
    "cclass":  "Fighter",  # Class key — unknown classes treated as Fighter
    "level":   1,          # REQUIRED — drives HP, XP, combat scaling
    "stats":   [75, 75, 75, 75, 75, 75],   # STR DEX CON INT WIS CHA  (1-100)
    "alignment": 0,        # -1000 (evil) … 0 (neutral) … +1000 (good)
    "position":  "standing",  # standing | sitting | resting | kneeling | reclined

    # ── HP ────────────────────────────────────────────────────────────────────
    # Calculated automatically as level × 8 × 5.

    # ── AC ────────────────────────────────────────────────────────────────────
    # Omit to let the engine calculate from equipped gear (sum of ac_bonus).
    # Include to override with a flat value.
    # "ac": 40,

    # ── Combat ────────────────────────────────────────────────────────────────
    "damage_dice": "1d4+0",   # Melee damage per hit e.g. "2d6+3"

    # ── Loot ─────────────────────────────────────────────────────────────────
    "coins": {"gold": 0, "silver": 0, "copper": 0},

    # ── Behaviour ─────────────────────────────────────────────────────────────
    "aggro":           False,  # True → attacks any player in room on sight
    "killable":        True,   # False → cannot be targeted (quest NPCs, etc.)
    "perception_prof": False,  # True → Perception proficiency bonus added to PP
    "has_dialog":      False,  # True → mob has entries in the DIALOGS table
}


# ══════════════════════════════════════════════════════════════════════════════
# SHARED ITEM FIELDS  (present on every item type)
# ══════════════════════════════════════════════════════════════════════════════

_ITEM_BASE: dict = {
    # ── Identity ──────────────────────────────────────────────────────────────
    "name":        "&wa thing&N",            # REQUIRED — inventory / look name
    "room_desc":   "&wA thing lies here.&N", # What appears on the floor
    "key_words":   ("thing",),               # Targeting keywords (tuple/list)
    "description": "A nondescript object.",  # Seen when you look AT it

    # ── Wear location ─────────────────────────────────────────────────────────
    # Set wear_on for wearable items.  Omit for inventory-only items.
    # Valid values:
    #   light           floats as a light source
    #   floating        floats near head (utility slot)
    #   head            helmet, hat, crown
    #   face            mask, goggles, visor
    #   neck            necklace, amulet, scarf        ← dual slot (2 items)
    #   on_body         chest armour, robe, tunic
    #   about_body      cloak, cape, tabard
    #   back            quiver, backpack
    #   arms            sleeves, vambraces
    #   hands           gloves, gauntlets
    #   waist           belt, sash
    #   legs            leggings, greaves, trousers
    #   feet            boots, shoes, sandals
    #   wrist           bracelet, bracer               ← dual slot (2 items)
    #   ring            ring, band                     ← dual slot (2 items)
    #   earring         earring, stud                  ← dual slot (2 items)
    #   primary_hand    main-hand weapon
    #   secondary_hand  off-hand weapon or shield
    #   held            held in off-hand (lamp, tome, wand)
    "wear_on": None,

    # ── Economy ───────────────────────────────────────────────────────────────
    "weight": 1.0,     # pounds
    "cost":   0,       # gold value

    # ── AC bonus ──────────────────────────────────────────────────────────────
    # Flat AC added while this item is equipped. Stacks with all other gear.
    # Unarmored AC is 0; all protection comes from ac_bonus values.
    "ac_bonus": 0,

    # ── Modifiers (stacks with others; displayed in att/score) ───────────────
    # stat_mods: flat bonus applied to displayed stat while worn
    "stat_mods": {},   # e.g. {"str": 5, "dex": -2}

    # save_mods: flat bonus to the relevant saving throw while worn
    "save_mods": {},   # e.g. {"par": 2, "spe": 1}
    #   Keys: par (paralysis/CON)  rod (rods/DEX)  pet (petri/CON)
    #         bre (breath/DEX)     spe (spells — class-dependent)
}


# ══════════════════════════════════════════════════════════════════════════════
# WEAPON
# ══════════════════════════════════════════════════════════════════════════════

WEAPON: dict = {
    **_ITEM_BASE,
    "name":      "&wa sword&N",
    "room_desc": "&wA sword lies here.&N",
    "key_words": ("sword",),
    "wear_on":   "primary_hand",   # primary_hand | secondary_hand | held

    # ── Damage ────────────────────────────────────────────────────────────────
    "dice":    "1d6",   # REQUIRED damage dice e.g. "2d8" "1d12+3"

    # ── Enchantment bonuses ────────────────────────────────────────────────────
    "hitroll": 0,   # bonus to attack roll
    "damroll": 0,   # bonus to damage roll

    # ── Weapon properties ─────────────────────────────────────────────────────
    "two_handed": False,   # True → occupies both hands
    "finesse":    False,   # True → use higher of STR/DEX for attack + damage
    "light":      False,   # True → eligible for Two-Weapon Fighting
    "thrown":     False,   # True → can be thrown (ranged attack)
    "reach":      False,   # True → can attack from 10 ft

    # ── Versatile (one-handed OR two-handed) ──────────────────────────────────
    "versatile":       False,
    "versatile_dice":  "1d8",   # damage dice when wielded two-handed

    # ── Weapon is also a shield? ───────────────────────────────────────────────
    "is_shield": False,   # True → grants ac_bonus when in secondary_hand

    "weight":    2.0,
    "cost":      50,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# ARMOR  (wearable protection)
# ══════════════════════════════════════════════════════════════════════════════

ARMOR: dict = {
    **_ITEM_BASE,
    "name":      "&wan armour&N",
    "room_desc": "&wAn armour lies here.&N",
    "key_words": ("armour",),
    "wear_on":   "on_body",   # Usually on_body; can be any slot

    # ── AC ────────────────────────────────────────────────────────────────────
    # Set ac_bonus to however much protection this piece provides.
    # All equipped ac_bonus values stack; unarmored AC is 0.
    "ac_bonus":  20,

    "weight":    10.0,
    "cost":      200,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# SHIELD
# ══════════════════════════════════════════════════════════════════════════════

SHIELD: dict = {
    **_ITEM_BASE,
    "name":      "&wa shield&N",
    "room_desc": "&wA shield rests here.&N",
    "key_words": ("shield",),
    "wear_on":   "secondary_hand",

    "is_shield": True,   # marks it as a shield for display purposes
    "dice":      "1d4",  # bash damage if used as an improvised weapon
    "hitroll":   0,
    "damroll":   0,

    "ac_bonus":  10,     # flat AC while equipped
    "weight":    6.0,
    "cost":      80,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# CLOTHING / JEWELRY  (wearable, no AC — or small AC bonus)
# ══════════════════════════════════════════════════════════════════════════════

CLOTHING: dict = {
    **_ITEM_BASE,
    "name":      "&wa ring&N",
    "room_desc": "&wA ring glitters here.&N",
    "key_words": ("ring",),
    "wear_on":   "ring",   # Any wearable slot — see _ITEM_BASE for full list

    "ac_bonus":  0,
    "stat_mods": {"dex": 5},   # e.g. Ring of Agility
    "save_mods": {},

    "weight": 0.1,
    "cost":   100,
}


# ══════════════════════════════════════════════════════════════════════════════
# CONTAINER  (holds other items)
# ══════════════════════════════════════════════════════════════════════════════

CONTAINER: dict = {
    **_ITEM_BASE,
    "name":      "&wa sack&N",
    "room_desc": "&wA sack lies here.&N",
    "key_words": ("sack", "bag"),
    "wear_on":   "held",   # held | None (floor-only container)

    "capacity":           50.0,   # max total weight of contents (lbs)
    "weightless_capacity": 0.0,   # lbs of contents that don't add to burden
    "is_open":            True,   # False → must be opened before accessing

    "weight":    1.0,
    "cost":      30,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# FOOD
# ══════════════════════════════════════════════════════════════════════════════

FOOD: dict = {
    **_ITEM_BASE,
    "name":      "&wa piece of bread&N",
    "room_desc": "&wA piece of bread lies here.&N",
    "key_words": ("bread", "food"),
    "wear_on":   None,

    "hunger":   4,
    "poisoned": False,

    "weight":    0.2,
    "cost":      2,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# DRINK CONTAINER
# ══════════════════════════════════════════════════════════════════════════════

DRINK: dict = {
    **_ITEM_BASE,
    "name":      "&wa waterskin&N",
    "room_desc": "&wA waterskin lies here.&N",
    "key_words": ("waterskin", "skin"),
    "wear_on":   "held",

    "liquid":   "water",
    "capacity": 5,
    "current":  5,
    "poisoned": False,
    "thirst":   1,

    "weight":    0.5,
    "cost":      5,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# KEY
# ══════════════════════════════════════════════════════════════════════════════

KEY: dict = {
    **_ITEM_BASE,
    "name":      "&wa key&N",
    "room_desc": "&wA key lies here.&N",
    "key_words": ("key",),
    "wear_on":   None,

    "key_for": 0,

    "weight":    0.1,
    "cost":      5,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# LIGHT SOURCE
# ══════════════════════════════════════════════════════════════════════════════

LIGHT: dict = {
    **_ITEM_BASE,
    "name":      "&ya torch&N",
    "room_desc": "&yA torch has been dropped here.&N",
    "key_words": ("torch", "light"),
    "wear_on":   "light",

    "hours":    -1,

    "weight":    0.5,
    "cost":      1,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# TREASURE
# ══════════════════════════════════════════════════════════════════════════════

TREASURE: dict = {
    **_ITEM_BASE,
    "name":      "&Ya gem&N",
    "room_desc": "&YA gem sparkles here.&N",
    "key_words": ("gem",),
    "wear_on":   None,

    "weight":    0.1,
    "cost":      500,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}


# ══════════════════════════════════════════════════════════════════════════════
# MISC
# ══════════════════════════════════════════════════════════════════════════════

MISC: dict = {
    **_ITEM_BASE,
    "name":      "&wa thing&N",
    "room_desc": "&wA thing lies here.&N",
    "key_words": ("thing",),
    "wear_on":   None,

    "weight":    1.0,
    "cost":      0,
    "ac_bonus":  0,
    "stat_mods": {},
    "save_mods": {},
}
