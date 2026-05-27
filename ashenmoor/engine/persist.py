"""
ashenmoor.engine.persist
─────────────────────────
SQLite persistence for player character state.

What is saved and when
──────────────────────
  Semi-permanent  (written on every relevant change during play):
      level, xp, base stats, max_hp
      inventory  — every item the player is carrying
      equipment  — every item the player is wearing
      location   — current room vnum

  Memory-only  (written ONLY on a clean quit):
      hp  — current hit points

  Not persisted (reconstructed from zone files on each startup):
      room objects, mob state, power cooldowns

Schema
──────
  characters  — one row per saved player character
  inventory   — one row per carried item, ordered by position
  equipment   — one row per equipped item (dual slots use item_index 0/1)

Items are stored as self-contained JSON blobs so they can be
reconstructed without looking up zone templates.  This means custom-
named or modified items survive saves correctly.
"""

import json
import time
import sqlite3


# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS characters (
    name        TEXT    PRIMARY KEY,
    race        TEXT    NOT NULL,
    class       TEXT    NOT NULL,
    level       INTEGER NOT NULL DEFAULT 1,
    xp          INTEGER NOT NULL DEFAULT 0,
    stats       TEXT    NOT NULL,       -- JSON: [str, dex, con, int, wis, cha]
    max_hp      INTEGER NOT NULL,
    hp          INTEGER NOT NULL,       -- written only on clean quit
    location    INTEGER NOT NULL,       -- room vnum
    updated_at  REAL    NOT NULL        -- unix timestamp
);

CREATE TABLE IF NOT EXISTS inventory (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    position        INTEGER NOT NULL,   -- order items appear in inventory
    item_data       TEXT    NOT NULL,   -- full item state as JSON
    PRIMARY KEY (character_name, position)
);

CREATE TABLE IF NOT EXISTS equipment (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    slot            TEXT    NOT NULL,   -- e.g. primary_hand, head, earring
    item_index      INTEGER NOT NULL DEFAULT 0,  -- dual slots: 0 or 1
    item_data       TEXT    NOT NULL,
    PRIMARY KEY (character_name, slot, item_index)
);
"""


# ── Connection ────────────────────────────────────────────────────────────────

def open_db(path: str = "ashenmoor.db") -> sqlite3.Connection:
    """
    Open (or create) the SQLite database, initialize the schema, and
    return the open connection.

    Called once at startup from GameState.init_persistence().
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    return conn


# ── Item serialization ────────────────────────────────────────────────────────

def _item_to_dict(item) -> dict:
    """
    Convert any Object / Item / Weapon / Container to a plain dict
    suitable for JSON serialization.

    The "type" key lets _dict_to_item() reconstruct the right class.
    Container.contents are serialized recursively.
    """
    from ..world.objects import Weapon, Container, Item

    base = {
        "type":             type(item).__name__,
        "name":             item.name,
        "key_words":        list(item.key_words),
        "room_description": item.room_description,
        "description":      item.description,
    }

    if isinstance(item, Weapon):
        base.update({
            "weight":     item.weight,
            "mod":        item.mod,
            "wear_on":    item.wear_on,
            "dice":       item.dice,
            "hitroll":    item.hitroll,
            "damroll":    item.damroll,
            "two_handed": item.two_handed,
        })

    elif isinstance(item, Container):
        base.update({
            "weight":              item.weight,
            "mod":                 item.mod,
            "wear_on":             item.wear_on,
            "capacity":            item.capacity,
            "weightless_capacity": item.weightless_capacity,
            "is_open":             item.is_open,
            "contents":            [_item_to_dict(c) for c in item.contents],
        })

    elif isinstance(item, Item):
        base.update({
            "weight":  item.weight,
            "mod":     item.mod,
            "wear_on": item.wear_on,
        })

    return base


def _dict_to_item(data: dict):
    """
    Reconstruct an Object / Item / Weapon / Container from a plain dict.
    Container.contents are deserialized recursively.
    """
    from ..world.objects import Weapon, Container, Item, Object

    t = data.get("type", "Object")

    if t == "Weapon":
        return Weapon(data)

    if t == "Container":
        d        = dict(data)
        contents = d.pop("contents", [])
        obj      = Container(d)
        obj.contents = [_dict_to_item(c) for c in contents]
        return obj

    if t == "Item":
        return Item(data)

    return Object(data)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_character(
    conn:       sqlite3.Connection,
    char,
    location:   int,
    include_hp: bool = False,
) -> None:
    """
    Write the player character's persistent state to the database.

    All writes are wrapped in a single transaction so a crash mid-save
    leaves the database in its previous consistent state.

    Parameters
    ----------
    char        : Character instance to save.
    location    : Current room vnum (from state.locations[player]).
    include_hp  : False — skip hp (memory-only during play).
                  True  — write current hp (call this on clean quit).
    """
    now = time.time()
    hp  = getattr(char, "hp", char.max_hp)

    with conn:
        # Upsert the character row.
        # The CASE expression leaves hp unchanged unless include_hp is True.
        conn.execute("""
            INSERT INTO characters
                (name, race, class, level, xp, stats, max_hp, hp, location, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                race       = excluded.race,
                class      = excluded.class,
                level      = excluded.level,
                xp         = excluded.xp,
                stats      = excluded.stats,
                max_hp     = excluded.max_hp,
                hp         = CASE WHEN ? THEN excluded.hp ELSE hp END,
                location   = excluded.location,
                updated_at = excluded.updated_at
        """, (
            char.name, char.race, char.cclass,
            char.level, getattr(char, "xp", 0),
            json.dumps(char.stats),
            char.max_hp, hp, location, now,
            1 if include_hp else 0,   # CASE parameter
        ))

        # Replace inventory (delete-and-reinsert is simpler than diffing)
        conn.execute(
            "DELETE FROM inventory WHERE character_name = ?",
            (char.name,),
        )
        for pos, item in enumerate(char.inventory):
            conn.execute(
                "INSERT INTO inventory (character_name, position, item_data) "
                "VALUES (?, ?, ?)",
                (char.name, pos, json.dumps(_item_to_dict(item))),
            )

        # Replace equipment
        conn.execute(
            "DELETE FROM equipment WHERE character_name = ?",
            (char.name,),
        )
        from ..world.equipment import DUAL_SLOTS
        for slot, equipped in char.equipment.items():
            items = equipped if isinstance(equipped, list) else [equipped]
            for idx, item in enumerate(items):
                conn.execute(
                    "INSERT INTO equipment "
                    "(character_name, slot, item_index, item_data) "
                    "VALUES (?, ?, ?, ?)",
                    (char.name, slot, idx, json.dumps(_item_to_dict(item))),
                )


# ── Load ──────────────────────────────────────────────────────────────────────

def load_character(
    conn: sqlite3.Connection,
    name: str,
    char,
) -> int | None:
    """
    Restore a character's saved state into an existing Character object.

    Fields written into *char*:
        level, xp, stats, max_hp, hp, inventory, equipment

    Returns
    -------
    int   — the saved room vnum (use this as the starting location)
    None  — character not found in DB; leave defaults from main.py
    """
    row = conn.execute(
        "SELECT * FROM characters WHERE name = ?", (name,)
    ).fetchone()

    if row is None:
        return None

    # Restore character fields from DB
    char.level  = row["level"]
    char.xp     = row["xp"]
    char.stats  = json.loads(row["stats"])
    char.max_hp = row["max_hp"]
    char.hp     = row["hp"]

    # Restore inventory
    inv_rows = conn.execute(
        "SELECT item_data FROM inventory "
        "WHERE character_name = ? ORDER BY position",
        (name,),
    ).fetchall()
    char.inventory = [
        _dict_to_item(json.loads(r["item_data"])) for r in inv_rows
    ]

    # Restore equipment
    eq_rows = conn.execute(
        "SELECT slot, item_index, item_data FROM equipment "
        "WHERE character_name = ? ORDER BY slot, item_index",
        (name,),
    ).fetchall()

    from ..world.equipment import DUAL_SLOTS
    char.equipment = {}
    for r in eq_rows:
        slot = r["slot"]
        item = _dict_to_item(json.loads(r["item_data"]))
        if slot in DUAL_SLOTS:
            char.equipment.setdefault(slot, []).append(item)
        else:
            char.equipment[slot] = item

    return row["location"]
