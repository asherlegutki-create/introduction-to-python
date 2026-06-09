"""
ashenmoor.engine.persist
─────────────────────────
SQLite persistence — accounts, characters, inventory, equipment.

Schema
──────
  accounts      — login credentials and optional email
  characters    — one row per character, linked to account by account_id
  inventory     — per-character ordered item list
  equipment     — per-character slot/item rows

Password security
─────────────────
  Passwords are stored as  sha256(salt + password)  where salt is a
  random 32-byte hex string unique per account.  No external dependencies.

Account name rules (enforced by login layer)
─────────────────────────────────────────────
  [A-Za-z0-9_-]  stored lowercase

Character name rules (enforced by login layer)
───────────────────────────────────────────────
  [A-Za-z] only
"""

import hashlib
import json
import os
import re
import time
import sqlite3


_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS world_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    UNIQUE NOT NULL,
    password     TEXT    NOT NULL,
    salt         TEXT    NOT NULL,
    email        TEXT,
    created_at   REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    name           TEXT    PRIMARY KEY,
    account_id     INTEGER NOT NULL REFERENCES accounts(id),
    race           TEXT    NOT NULL,
    class          TEXT    NOT NULL,
    level          INTEGER NOT NULL DEFAULT 1,
    xp             INTEGER NOT NULL DEFAULT 0,
    stats          TEXT    NOT NULL,
    max_hp         INTEGER NOT NULL,
    hp             INTEGER NOT NULL,
    location       INTEGER NOT NULL,
    created_at     REAL    NOT NULL,
    updated_at     REAL    NOT NULL,
    status_effects TEXT    NOT NULL DEFAULT '[]',
    toggles        TEXT    NOT NULL DEFAULT '{}',
    potion_log     TEXT    NOT NULL DEFAULT '[]',
    sex            TEXT    NOT NULL DEFAULT 'male',
    dnd            TEXT    NOT NULL DEFAULT '{}'
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

_MIGRATIONS: list[str] = []


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


# ── Password helpers ──────────────────────────────────────────────────────────

def _make_salt() -> str:
    return os.urandom(32).hex()

def _hash_password(salt: str, password: str) -> str:
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_password(conn: sqlite3.Connection,
                    account_name: str, password: str) -> bool:
    row = conn.execute(
        "SELECT salt, password FROM accounts WHERE name = ?",
        (account_name.lower(),),
    ).fetchone()
    if row is None:
        return False
    return _hash_password(row["salt"], password) == row["password"]


# ── Account CRUD ──────────────────────────────────────────────────────────────

def account_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM accounts WHERE name = ?", (name.lower(),)
    ).fetchone() is not None


def create_account(conn: sqlite3.Connection,
                   name: str, password: str,
                   email: str | None = None) -> int:
    salt   = _make_salt()
    hashed = _hash_password(salt, password)
    with conn:
        cur = conn.execute(
            "INSERT INTO accounts (name, password, salt, email, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (name.lower(), hashed, salt, email or None, time.time()),
        )
    return cur.lastrowid


def get_account(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM accounts WHERE name = ?", (name.lower(),)
    ).fetchone()


def set_password(conn: sqlite3.Connection,
                 account_name: str, new_password: str) -> None:
    salt   = _make_salt()
    hashed = _hash_password(salt, new_password)
    with conn:
        conn.execute(
            "UPDATE accounts SET password=?, salt=? WHERE name=?",
            (hashed, salt, account_name.lower()),
        )


def set_email(conn: sqlite3.Connection,
              account_name: str, email: str | None) -> None:
    with conn:
        conn.execute(
            "UPDATE accounts SET email=? WHERE name=?",
            (email, account_name.lower()),
        )


def get_account_characters(conn: sqlite3.Connection,
                            account_id: int) -> list[dict]:
    """Return all characters for an account in creation order with subclass."""
    rows = conn.execute(
        "SELECT name, race, class, level, dnd FROM characters "
        "WHERE account_id=? ORDER BY created_at ASC",
        (account_id,),
    ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        # Extract subclass from saved dnd dict
        try:
            dnd_data = json.loads(d.pop("dnd") or "{}")
            d["subclass"] = dnd_data.get("subclass")
        except (json.JSONDecodeError, TypeError):
            d["subclass"] = None
        result.append(d)
    return result


def delete_character(conn: sqlite3.Connection, char_name: str) -> None:
    with conn:
        conn.execute("DELETE FROM characters WHERE name=?", (char_name,))


# ── Validation ────────────────────────────────────────────────────────────────

_ACCOUNT_RE = re.compile(r'^[A-Za-z0-9_\-]+$')
_CHAR_RE    = re.compile(r'^[A-Za-z]+$')

def valid_account_name(name: str) -> bool:
    return bool(name) and bool(_ACCOUNT_RE.match(name))

def valid_char_name(name: str) -> bool:
    return bool(name) and bool(_CHAR_RE.match(name))


# ── Item serialization ────────────────────────────────────────────────────────

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
            "weight":     item.weight,  "mod":     item.mod,
            "wear_on":    item.wear_on, "dice":    item.dice,
            "hitroll":    item.hitroll, "damroll": item.damroll,
            "two_handed": item.two_handed,
            "proc":       item.proc,   "powers":  item.powers,
            "stat_mods":  getattr(item, "stat_mods", {}),
            "save_mods":  getattr(item, "save_mods", {}),
            "ac_bonus":   getattr(item, "ac_bonus",  0),
            "armor_type": getattr(item, "armor_type", None),
        })
    elif isinstance(item, Scroll):
        base.update({
            "weight": item.weight, "mod": item.mod, "wear_on": item.wear_on,
            "effect": item.effect, "apply_msg": item.apply_msg,
            "room_msg": item.room_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name","key_words","room_description","description","type")},
        })
    elif isinstance(item, Potion):
        base.update({
            "weight": item.weight, "mod": item.mod, "wear_on": item.wear_on,
            "effect": item.effect, "apply_msg": item.apply_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name","key_words","room_description","description","type")},
        })
    elif isinstance(item, Container):
        base.update({
            "weight": item.weight, "mod": item.mod, "wear_on": item.wear_on,
            "capacity": item.capacity,
            "weightless_capacity": item.weightless_capacity,
            "is_open": item.is_open,
            "contents": [_item_to_dict(c) for c in item.contents],
        })
    elif isinstance(item, Item):
        base.update({
            "weight": item.weight, "mod": item.mod, "wear_on": item.wear_on,
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
    if t == "Weapon":  return Weapon(data)
    if t == "Scroll":  return Scroll(data)
    if t == "Potion":  return Potion(data)
    if t == "Item":    return Item(data)
    if t == "Container":
        d = dict(data); contents = d.pop("contents", [])
        obj = Container(d); obj.contents = [_dict_to_item(c) for c in contents]
        return obj
    return Object(data)


# ── World time ────────────────────────────────────────────────────────────────

def save_world_time(conn: sqlite3.Connection, total_minutes: int) -> None:
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO world_state (key, value) VALUES ('total_minutes', ?)",
            (str(total_minutes),),
        )

def load_world_time(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT value FROM world_state WHERE key='total_minutes'"
    ).fetchone()
    return int(row["value"]) if row else 0


# ── Character save ────────────────────────────────────────────────────────────

def save_character(conn, char, location: int,
                   account_id: int = 0, include_hp: bool = False) -> None:
    now = time.time()
    hp  = getattr(char, "hp", char.max_hp)

    with conn:
        conn.execute("""
            INSERT INTO characters
                (name, account_id, race, class, level, xp, stats,
                 max_hp, hp, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                race=excluded.race, class=excluded.class,
                level=excluded.level, xp=excluded.xp,
                stats=excluded.stats, max_hp=excluded.max_hp,
                hp=CASE WHEN ? THEN excluded.hp ELSE hp END,
                location=excluded.location, updated_at=excluded.updated_at
        """, (
            char.name, account_id, char.race, char.cclass,
            char.level, getattr(char, "xp", 0), json.dumps(char.stats),
            char.max_hp, hp, location, now, now,
            1 if include_hp else 0,
        ))

        conn.execute("DELETE FROM inventory WHERE character_name=?", (char.name,))
        for pos, item in enumerate(char.inventory):
            conn.execute(
                "INSERT INTO inventory (character_name, position, item_data) "
                "VALUES (?,?,?)",
                (char.name, pos, json.dumps(_item_to_dict(item))),
            )

        conn.execute("DELETE FROM equipment WHERE character_name=?", (char.name,))
        from ..world.equipment import DUAL_SLOTS
        for slot, equipped in char.equipment.items():
            items = equipped if isinstance(equipped, list) else [equipped]
            for idx, item in enumerate(items):
                conn.execute(
                    "INSERT INTO equipment "
                    "(character_name, slot, item_index, item_data) VALUES (?,?,?,?)",
                    (char.name, slot, idx, json.dumps(_item_to_dict(item))),
                )

        status_effects = getattr(char, "status_effects", [])
        serializable   = []
        for eff in status_effects:
            e = dict(eff); e["flags"] = list(e.get("flags", set()))
            serializable.append(e)

        dnd = getattr(char, "dnd", None)
        conn.execute(
            "UPDATE characters SET "
            "status_effects=?, toggles=?, potion_log=?, sex=?, dnd=? "
            "WHERE name=?",
            (
                json.dumps(serializable),
                json.dumps(getattr(char, "toggles",    {})),
                json.dumps(getattr(char, "potion_log", [])),
                getattr(char, "sex", "male"),
                json.dumps(dnd) if dnd is not None else "{}",
                char.name,
            ),
        )


def update_location(conn, char_name: str, location: int) -> None:
    try:
        with conn:
            conn.execute(
                "UPDATE characters SET location=?, updated_at=? WHERE name=?",
                (location, time.time(), char_name),
            )
    except Exception:
        pass


# ── Character load ────────────────────────────────────────────────────────────

def load_character(conn, name: str, char) -> int | None:
    row = conn.execute(
        "SELECT * FROM characters WHERE name=?", (name,)
    ).fetchone()
    if row is None:
        return None

    char.level  = row["level"]
    char.xp     = row["xp"]
    char.stats  = json.loads(row["stats"])
    char.max_hp = row["max_hp"]
    char.hp     = row["hp"]

    # Restore dnd
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

    if not hasattr(char, "temp_hp"):
        char.temp_hp = 0

    raw_effects = json.loads(row["status_effects"] or "[]")
    for eff in raw_effects:
        eff["flags"] = set(eff.get("flags", []))
    char.status_effects = raw_effects
    from ..world.effects import recalc_status
    recalc_status(char)

    char.toggles    = json.loads(row["toggles"]    or "{}")
    char.potion_log = json.loads(row["potion_log"] or "[]")
    char.sex        = row["sex"] if row["sex"] else "male"

    inv_rows = conn.execute(
        "SELECT item_data FROM inventory WHERE character_name=? ORDER BY position",
        (name,),
    ).fetchall()
    char.inventory = [_dict_to_item(json.loads(r["item_data"])) for r in inv_rows]

    eq_rows = conn.execute(
        "SELECT slot, item_index, item_data FROM equipment "
        "WHERE character_name=? ORDER BY slot, item_index",
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

    if not getattr(char, "powers", []):
        cclass = getattr(char, "cclass", "").lower()
        if cclass in ("fighter", "warrior"):
            from ..dnd.classes.fighter import FIGHTER_POWERS, BATTLEMASTER_POWERS
            dnd = getattr(char, "dnd", {}) or {}
            char.powers = list(FIGHTER_POWERS)
            if dnd.get("subclass") == "battle_master":
                char.powers += BATTLEMASTER_POWERS

    cclass = getattr(char, "cclass", "").lower()
    if cclass in ("fighter", "warrior"):
        dnd = getattr(char, "dnd", {}) or {}
        if (dnd.get("subclass") is None
                and not dnd.get("subclass_pending")
                and char.level >= 8):
            dnd["subclass_pending"] = True
            char.dnd = dnd

    dnd = getattr(char, "dnd", {}) or {}
    if dnd.get("subclass") == "battle_master":
        from ..dnd.classes.fighter import new_battlemaster_state
        for k, v in new_battlemaster_state(char.level).items():
            dnd.setdefault(k, v)
        char.dnd = dnd

    return row["location"]


# ── Wiz helpers ───────────────────────────────────────────────────────────────

def wiz_list_accounts(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT a.id, a.name, a.email, a.created_at, "
        "COUNT(c.name) AS char_count "
        "FROM accounts a LEFT JOIN characters c ON c.account_id=a.id "
        "GROUP BY a.id ORDER BY a.created_at ASC"
    ).fetchall()
    return [dict(r) for r in rows]


def wiz_account_info(conn, account_name: str) -> dict | None:
    acc = get_account(conn, account_name)
    if acc is None:
        return None
    chars = get_account_characters(conn, acc["id"])
    return {"account": dict(acc), "characters": [dict(c) for c in chars]}


def wiz_reset_password(conn, account_name: str) -> str:
    import string, random as _r
    alphabet = string.ascii_letters + string.digits
    temp_pw  = "".join(_r.choices(alphabet, k=12))
    set_password(conn, account_name, temp_pw)
    return temp_pw
