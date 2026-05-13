import pickle
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".pystack" / "pystack.db"


def open_db(path=None):
    db_path = Path(path) if path else DEFAULT_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS stack ("
        "position INTEGER PRIMARY KEY, value BLOB NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS slots ("
        "name TEXT PRIMARY KEY, value BLOB NOT NULL)"
    )
    conn.commit()
    return conn


def load_stack(conn):
    rows = conn.execute(
        "SELECT value FROM stack ORDER BY position ASC"
    ).fetchall()
    return [pickle.loads(row[0]) for row in rows]


def load_slots(conn):
    rows = conn.execute("SELECT name, value FROM slots").fetchall()
    return {name: pickle.loads(blob) for name, blob in rows}


def save_stack(conn, items):
    with conn:
        conn.execute("DELETE FROM stack")
        conn.executemany(
            "INSERT INTO stack (position, value) VALUES (?, ?)",
            [(i, pickle.dumps(v)) for i, v in enumerate(items)],
        )


def save_slots(conn, slots):
    existing = {row[0] for row in conn.execute("SELECT name FROM slots")}
    with conn:
        for name in existing - set(slots):
            conn.execute("DELETE FROM slots WHERE name = ?", (name,))
        for name, value in slots.items():
            conn.execute(
                "INSERT OR REPLACE INTO slots (name, value) " "VALUES (?, ?)",
                (name, pickle.dumps(value)),
            )


def reset_stack(conn):
    with conn:
        conn.execute("DELETE FROM stack")
