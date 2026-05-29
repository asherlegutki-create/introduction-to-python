"""
Starter warrior gear — sturdy leather set.

Nine pieces covering every protection slot.  The full set adds a flat
ac_bonus to whatever the engine calculates from DEX + armor_type.

Color scheme  &Xa sturdy &N&yleather &X<item>&N
──────────────────────────────────────────────────────────────────────
Slot          Item              ac_bonus  STR  DEX  CON  save
head          cap                  4       —   +5    —
face          visor                1       —   +3   +2
on_body       armor (studded)     15      +3    —    —    par+1
about_body    cloak                4      +2    —   +3
waist         belt                 2      +5    —    —
arms          vambraces            3       —   +2   +2
hands         gloves               3      +3   +3    —
legs          leggings             5       —    —   +5
feet          boots                3      +2   +2   +3
──────────────────────────────────────────────────────────────────────
AC total      40  (15 body + 25 rest)
Stat totals   STR +15  DEX +15  CON +15   (+3 to each modifier)
"""

OBJECTS: dict = {

    # ── HEAD — 4 AC ──────────────────────────────────────────────────────────
    1: {
        "name":        "&Xa sturdy &N&yleather &Xcap&N",
        "room_desc":   "&XA sturdy &N&yleather &Xcap has been left here.&N",
        "key_words":   ("cap", "leather", "hat"),
        "description": (
            "A well-stitched leather cap with a short brim.  "
            "Simple, tough, and shaped to fit snugly without blocking your sight."
        ),
        "wear_on":   "head",
        "ac_bonus":  4,
        "weight":    1.0,
        "cost":      15,
        "stat_mods": {"dex": 5},
        "save_mods": {},
    },

    # ── FACE — 1 AC ──────────────────────────────────────────────────────────
    2: {
        "name":        "&Xa sturdy &N&yleather &Xvisor&N",
        "room_desc":   "&XA sturdy &N&yleather &Xvisor has been left here.&N",
        "key_words":   ("visor", "leather", "mask", "face"),
        "description": (
            "A narrow strip of hardened leather that guards the brow and cheeks.  "
            "Reinforced rivets run along the edge."
        ),
        "wear_on":   "face",
        "ac_bonus":  1,
        "weight":    0.5,
        "cost":      12,
        "stat_mods": {"dex": 3, "con": 2},
        "save_mods": {},
    },

    # ── ON_BODY — 15 AC ───────────────────────────────────────────────────────
    # armor_type gives the base AC from the armor table (studded = 40 + DEX).
    # ac_bonus is added on top of that.
    3: {
        "name":        "&Xa studded &N&yleather &Xarmour&N",
        "room_desc":   "&XA studded &N&yleather &Xarmour has been left here.&N",
        "key_words":   ("studded", "armor", "leather", "jacket"),
        "description": (
            "Thick hide stitched with close-set metal studs.  "
            "Heavier than plain leather but still light enough to move freely."
        ),
        "wear_on":    "on_body",
        "armor_type": "studded",
        "ac_bonus":   15,
        "weight":     13.0,
        "cost":       95,
        "stat_mods":  {"str": 3},
        "save_mods":  {"par": 1},
    },

    # ── ABOUT_BODY — 4 AC ─────────────────────────────────────────────────────
    4: {
        "name":        "&Xa sturdy &N&yleather &Xcloak&N",
        "room_desc":   "&XA sturdy &N&yleather &Xcloak has been left here.&N",
        "key_words":   ("cloak", "leather", "cape"),
        "description": (
            "A knee-length cloak of oiled leather.  "
            "Rolls off rain and wind alike, with a broad hood stitched firm."
        ),
        "wear_on":   "about_body",
        "ac_bonus":  4,
        "weight":    3.0,
        "cost":      40,
        "stat_mods": {"str": 2, "con": 3},
        "save_mods": {},
    },

    # ── WAIST — 2 AC ──────────────────────────────────────────────────────────
    5: {
        "name":        "&Xa sturdy &N&yleather &Xbelt&N",
        "room_desc":   "&XA sturdy &N&yleather &Xbelt has been left here.&N",
        "key_words":   ("belt", "leather", "girdle"),
        "description": (
            "A broad belt of double-layered leather with a heavy iron buckle.  "
            "Good for keeping your kit tight and your back supported."
        ),
        "wear_on":   "waist",
        "ac_bonus":  2,
        "weight":    1.0,
        "cost":      20,
        "stat_mods": {"str": 5},
        "save_mods": {},
    },

    # ── ARMS — 3 AC ───────────────────────────────────────────────────────────
    6: {
        "name":        "&Xsome sturdy &N&yleather &Xvambraces&N",
        "room_desc":   "&XSome sturdy &N&yleather &Xvambraces have been left here.&N",
        "key_words":   ("vambraces", "vambrace", "leather", "arms", "bracers"),
        "description": (
            "Paired leather guards lashed from wrist to elbow.  "
            "The inside is padded with soft linen to prevent chafing."
        ),
        "wear_on":   "arms",
        "ac_bonus":  3,
        "weight":    2.0,
        "cost":      25,
        "stat_mods": {"dex": 2, "con": 2},
        "save_mods": {},
    },

    # ── HANDS — 3 AC ─────────────────────────────────────────────────────────
    7: {
        "name":        "&Xa pair of sturdy &N&yleather &Xgloves&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xgloves have been left here.&N",
        "key_words":   ("gloves", "glove", "leather", "gauntlets", "hands"),
        "description": (
            "Close-fitting leather gloves with reinforced knuckles.  "
            "They improve your grip without dulling your feel for the weapon."
        ),
        "wear_on":   "hands",
        "ac_bonus":  3,
        "weight":    0.5,
        "cost":      18,
        "stat_mods": {"str": 3, "dex": 3},
        "save_mods": {},
    },

    # ── LEGS — 5 AC ───────────────────────────────────────────────────────────
    8: {
        "name":        "&Xa pair of sturdy &N&yleather &Xleggings&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xleggings have been left here.&N",
        "key_words":   ("leggings", "legging", "leather", "pants", "legs"),
        "description": (
            "Thick leather leggings reinforced at the knee and thigh.  "
            "They move with you and take a lot of punishment."
        ),
        "wear_on":   "legs",
        "ac_bonus":  5,
        "weight":    4.0,
        "cost":      45,
        "stat_mods": {"con": 5},
        "save_mods": {},
    },

    # ── FEET — 3 AC ───────────────────────────────────────────────────────────
    9: {
        "name":        "&Xa pair of sturdy &N&yleather &Xboots&N",
        "room_desc":   "&XA pair of sturdy &N&yleather &Xboots have been left here.&N",
        "key_words":   ("boots", "boot", "leather", "shoes", "feet"),
        "description": (
            "Ankle-high boots with thick soles and steel-capped toes.  "
            "Worn enough to be broken in, tough enough to last another year."
        ),
        "wear_on":   "feet",
        "ac_bonus":  3,
        "weight":    2.5,
        "cost":      35,
        "stat_mods": {"str": 2, "dex": 2, "con": 3},
        "save_mods": {},
    },
}

# ── Sanity check (runs when the module is imported) ───────────────────────────
_total_ac = sum(v["ac_bonus"] for v in OBJECTS.values())
assert _total_ac == 40, f"starter AC total is {_total_ac}, expected 40"
