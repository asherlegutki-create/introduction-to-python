"""
ashenmoor.engine.persist
─────────────────────────
SQLite persistence for player character state.

Migration notes
───────────────
  Warrior → Fighter: cclass field renamed seamlessly on load.
  temp_hp: initialised to 0 if not present (new field).
  dnd subclass_pending: set if Fighter at level 8+ with no subclass.
"""

import json
import time
import sqlite3


_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS world_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    name           TEXT    PRIMARY KEY,
    race           TEXT    NOT NULL,
    class          TEXT    NOT NULL,
    level          INTEGER NOT NULL DEFAULT 1,
    xp             INTEGER NOT NULL DEFAULT 0,
    stats          TEXT    NOT NULL,
    max_hp         INTEGER NOT NULL,
    hp             INTEGER NOT NULL,
    location       INTEGER NOT NULL,
    updated_at     REAL    NOT NULL,
    status_effects TEXT    NOT NULL DEFAULT '[]',
    toggles        TEXT    NOT NULL DEFAULT '{}',
    potion_log     TEXT    NOT NULL DEFAULT '[]',
    sex            TEXT    NOT NULL DEFAULT 'male'
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

_MIGRATIONS = [
    "ALTER TABLE characters ADD COLUMN status_effects TEXT NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN toggles TEXT NOT NULL DEFAULT '{}'",
    "ALTER TABLE characters ADD COLUMN potion_log TEXT NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN sex TEXT NOT NULL DEFAULT 'male'",
    "ALTER TABLE characters ADD COLUMN dnd TEXT NOT NULL DEFAULT '{}'",
]


def open_db(path: str = "ashenmoor.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    for stmt in _MIGRATIONS:
        try:
            conn.execute(stmt)
            conn.commit()
        except sqlite3.OperationalError:
            pass
    return conn


def _item_to_dict(item) -> dict:
    from ..world.objects import Weapon, Container, Item, Scroll, Potion

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
            "proc":       item.proc,
            "powers":     item.powers,
            "stat_mods":  getattr(item, "stat_mods", {}),
            "save_mods":  getattr(item, "save_mods", {}),
            "ac_bonus":   getattr(item, "ac_bonus",  0),
            "armor_type": getattr(item, "armor_type", None),
        })
    elif isinstance(item, Scroll):
        base.update({
            "weight":    item.weight,
            "mod":       item.mod,
            "wear_on":   item.wear_on,
            "effect":    item.effect,
            "apply_msg": item.apply_msg,
            "room_msg":  item.room_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name", "key_words", "room_description", "description", "type")},
        })
    elif isinstance(item, Potion):
        base.update({
            "weight":    item.weight,
            "mod":       item.mod,
            "wear_on":   item.wear_on,
            "effect":    item.effect,
            "apply_msg": item.apply_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name", "key_words", "room_description", "description", "type")},
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
            "weight":     item.weight,
            "mod":        item.mod,
            "wear_on":    item.wear_on,
            "stat_mods":  getattr(item, "stat_mods", {}),
            "save_mods":  getattr(item, "save_mods", {}),
            "ac_bonus":   getattr(item, "ac_bonus",  0),
            "armor_type": getattr(item, "armor_type", None),
            "is_key":     getattr(item, "is_key",    False),
            "key_name":   getattr(item, "key_name",  None),
        })

    return base


def _dict_to_item(data: dict):
    from ..world.objects import Weapon, Container, Item, Scroll, Potion, Object

    t = data.get("type", "Object")
    if t == "Weapon":   return Weapon(data)
    if t == "Scroll":   return Scroll(data)
    if t == "Potion":   return Potion(data)
    if t == "Item":     return Item(data)
    if t == "Container":
        d        = dict(data)
        contents = d.pop("contents", [])
        obj      = Container(d)
        obj.contents = [_dict_to_item(c) for c in contents]
        return obj
    return Object(data)


def save_world_time(conn: sqlite3.Connection, total_minutes: int) -> None:
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO world_state (key, value) VALUES ('total_minutes', ?)",
            (str(total_minutes),),
        )


def load_world_time(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT value FROM world_state WHERE key = 'total_minutes'"
    ).fetchone()
    return int(row["value"]) if row else 0


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

        conn.execute("DELETE FROM inventory WHERE character_name = ?", (char.name,))
        for pos, item in enumerate(char.inventory):
            conn.execute(
                "INSERT INTO inventory (character_name, position, item_data) VALUES (?, ?, ?)",
                (char.name, pos, json.dumps(_item_to_dict(item))),
            )

        conn.execute("DELETE FROM equipment WHERE character_name = ?", (char.name,))
        from ..world.equipment import DUAL_SLOTS
        for slot, equipped in char.equipment.items():
            items = equipped if isinstance(equipped, list) else [equipped]
            for idx, item in enumerate(items):
                conn.execute(
                    "INSERT INTO equipment (character_name, slot, item_index, item_data) "
                    "VALUES (?, ?, ?, ?)",
                    (char.name, slot, idx, json.dumps(_item_to_dict(item))),
                )

        status_effects = getattr(char, "status_effects", [])
        serializable   = []
        for eff in status_effects:
            e = dict(eff)
            e["flags"] = list(e.get("flags", set()))
            serializable.append(e)
        conn.execute(
            "UPDATE characters SET status_effects = ? WHERE name = ?",
            (json.dumps(serializable), char.name),
        )
        conn.execute(
            "UPDATE characters SET toggles = ? WHERE name = ?",
            (json.dumps(getattr(char, "toggles", {})), char.name),
        )
        conn.execute(
            "UPDATE characters SET potion_log = ? WHERE name = ?",
            (json.dumps(getattr(char, "potion_log", [])), char.name),
        )
        conn.execute(
            "UPDATE characters SET sex = ? WHERE name = ?",
            (getattr(char, "sex", "male"), char.name),
        )

        # Save dnd dict — this is what persists subclass choice, charges,
        # cooldowns, and all Fighter state between sessions.
        dnd = getattr(char, "dnd", None)
        if dnd is not None:
            conn.execute(
                "UPDATE characters SET dnd = ? WHERE name = ?",
                (json.dumps(dnd), char.name),
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

    # ── Restore dnd dict from DB ───────────────────────────────────────────
    # This must happen before migration logic so subclass choice survives login.
    saved_dnd_raw = row["dnd"] if "dnd" in row.keys() else None
    if saved_dnd_raw:
        try:
            saved_dnd = json.loads(saved_dnd_raw)
        except (json.JSONDecodeError, TypeError):
            saved_dnd = None
        if saved_dnd and isinstance(saved_dnd, dict):
            shell_dnd = getattr(char, "dnd", {}) or {}
            shell_dnd.update(saved_dnd)
            char.dnd = shell_dnd

    # ── Warrior → Fighter seamless migration ──────────────────────────────
    if char.cclass.lower() == "warrior":
        char.cclass = "Fighter"
        # dnd dict class field also needs updating
        dnd = getattr(char, "dnd", {}) or {}
        if dnd.get("class") == "warrior":
            dnd["class"] = "fighter"
        char.dnd = dnd

    # ── Ensure temp_hp exists ──────────────────────────────────────────────
    if not hasattr(char, "temp_hp"):
        char.temp_hp = 0

    # ── Restore status effects ─────────────────────────────────────────────
    raw_effects = json.loads(row["status_effects"] or "[]")
    for eff in raw_effects:
        eff["flags"] = set(eff.get("flags", []))
    char.status_effects = raw_effects
    from ..world.effects import recalc_status
    recalc_status(char)

    char.toggles    = json.loads(row["toggles"]    or "{}")
    char.potion_log = json.loads(row["potion_log"] or "[]")
    char.sex        = row["sex"] if row["sex"] else "male"

    # ── Inventory ──────────────────────────────────────────────────────────
    inv_rows = conn.execute(
        "SELECT item_data FROM inventory WHERE character_name = ? ORDER BY position",
        (name,),
    ).fetchall()
    char.inventory = [_dict_to_item(json.loads(r["item_data"])) for r in inv_rows]

    # ── Equipment ──────────────────────────────────────────────────────────
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

    # ── Restore class powers if missing ───────────────────────────────────
    # Covers characters saved before the powers system existed.
    if not getattr(char, "powers", []):
        cclass = getattr(char, "cclass", "").lower()
        if cclass in ("fighter", "warrior"):
            from ..dnd.classes.fighter import FIGHTER_POWERS, BATTLEMASTER_POWERS
            dnd      = getattr(char, "dnd", {}) or {}
            subclass = dnd.get("subclass")
            char.powers = list(FIGHTER_POWERS)
            if subclass == "battle_master":
                char.powers += BATTLEMASTER_POWERS

    # ── Ensure subclass_pending is set for eligible fighters ──────────────
    # Guard: only set pending if the saved dnd genuinely has no subclass.
    # If subclass was chosen during a previous session it will have been
    # loaded from the dnd column above and subclass will not be None here.
    cclass = getattr(char, "cclass", "").lower()
    if cclass in ("fighter", "warrior"):
        dnd = getattr(char, "dnd", {}) or {}
        if (dnd.get("subclass") is None
                and not dnd.get("subclass_pending")
                and char.level >= 8):
            dnd["subclass_pending"] = True
            char.dnd = dnd

    # ── Ensure Battle Master dnd fields are present if subclass set ───────
    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("subclass") == "battle_master":
        from ..dnd.classes.fighter import new_battlemaster_state
        bm_defaults = new_battlemaster_state(char.level)
        for k, v in bm_defaults.items():
            dnd.setdefault(k, v)
        char.dnd = dnd

    return row["location"]
