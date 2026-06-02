"""
ashenmoor.engine.persist
-
SQLite persistence for player character state.
"""

import json
import time
import sqlite3


_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS characters (
    name        TEXT    PRIMARY KEY,
    race        TEXT    NOT NULL,
    class       TEXT    NOT NULL,
    level       INTEGER NOT NULL DEFAULT 1,
    xp          INTEGER NOT NULL DEFAULT 0,
    stats       TEXT    NOT NULL,
    max_hp      INTEGER NOT NULL,
    hp          INTEGER NOT NULL,
    location    INTEGER NOT NULL,
    updated_at  REAL    NOT NULL,
    status_effects TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS inventory (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    position        INTEGER NOT NULL,
    item_data       TEXT    NOT NULL,
    PRIMARY KEY (character_name, position)
);

CREATE TABLE IF NOT EXISTS equipment (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    slot            TEXT    NOT NULL,
    item_index      INTEGER NOT NULL DEFAULT 0,
    item_data       TEXT    NOT NULL,
    PRIMARY KEY (character_name, slot, item_index)
);
"""

# Migrations -- run once at open_db time, ignored if column already exists
_MIGRATIONS = [
    "ALTER TABLE characters ADD COLUMN status_effects TEXT NOT NULL DEFAULT '[]'",
]


def open_db(path: str = "ashenmoor.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    # Run migrations -- ignore errors for columns that already exist
    for stmt in _MIGRATIONS:
        try:
            conn.execute(stmt)
            conn.commit()
        except sqlite3.OperationalError:
            pass   # column already exists
    return conn


def _item_to_dict(item) -> dict:
    """
    Convert any Object / Item / Weapon / Container to a plain dict
    for JSON serialization.  All fields needed to reconstruct the item
    are included -- including the proc key on weapons so procs survive
    save/load cycles.
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
            # proc and powers must be saved so they survive logout/login
            "proc":       item.proc,
            "powers":     item.powers,
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
    Container contents are deserialized recursively.
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


def save_character(
    conn:       sqlite3.Connection,
    char,
    location:   int,
    include_hp: bool = False,
) -> None:
    now = time.time()
    hp  = getattr(char, "hp", char.max_hp)

    with conn:
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
            1 if include_hp else 0,
        ))

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

        # Save active status effects (serializable dicts, strip non-JSON flags set)
        status_effects = getattr(char, "status_effects", [])
        serializable   = []
        for eff in status_effects:
            e = dict(eff)
            e["flags"] = list(e.get("flags", set()))   # set -> list for JSON
            serializable.append(e)
        conn.execute(
            "UPDATE characters SET status_effects = ? WHERE name = ?",
            (json.dumps(serializable), char.name),
        )


def load_character(
    conn: sqlite3.Connection,
    name: str,
    char,
) -> int | None:
    row = conn.execute(
        "SELECT * FROM characters WHERE name = ?", (name,)
    ).fetchone()

    if row is None:
        return None

    char.level  = row["level"]
    char.xp     = row["xp"]
    char.stats  = json.loads(row["stats"])
    char.max_hp = row["max_hp"]
    char.hp     = row["hp"]

    # Restore active status effects, converting flags back to set
    raw_effects = json.loads(row["status_effects"] or "[]")
    for eff in raw_effects:
        eff["flags"] = set(eff.get("flags", []))
    char.status_effects = raw_effects
    from ..world.effects import recalc_status
    recalc_status(char)

    inv_rows = conn.execute(
        "SELECT item_data FROM inventory "
        "WHERE character_name = ? ORDER BY position",
        (name,),
    ).fetchall()
    char.inventory = [
        _dict_to_item(json.loads(r["item_data"])) for r in inv_rows
    ]

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
