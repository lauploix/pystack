import numpy as np

from pystack.storage import (
    load_slots,
    load_stack,
    open_db,
    reset_stack,
    save_slots,
    save_stack,
)


def test_open_db_creates_schema(tmp_path):
    db = tmp_path / "x.db"
    conn = open_db(db)
    try:
        names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {"stack", "slots"} <= names
    finally:
        conn.close()


def test_open_db_creates_parent_directory(tmp_path):
    db = tmp_path / "a" / "b" / "x.db"
    conn = open_db(db)
    try:
        assert db.exists()
    finally:
        conn.close()


def test_stack_round_trip(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        items = [1, "a", 3.5, "a b", [1, 2, 3], {"k": "v"}]
        save_stack(conn, items)
        assert load_stack(conn) == items
    finally:
        conn.close()


def test_stack_order_preserved(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_stack(conn, ["bottom", 2, "top"])
        assert load_stack(conn) == ["bottom", 2, "top"]
    finally:
        conn.close()


def test_save_stack_overwrites(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_stack(conn, [1, 2, 3])
        save_stack(conn, [4, 5])
        assert load_stack(conn) == [4, 5]
    finally:
        conn.close()


def test_save_stack_empty(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_stack(conn, [1, 2, 3])
        save_stack(conn, [])
        assert load_stack(conn) == []
    finally:
        conn.close()


def test_reset_stack_clears(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_stack(conn, [1, 2, 3])
        reset_stack(conn)
        assert load_stack(conn) == []
    finally:
        conn.close()


def test_slots_round_trip(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        slots = {"x": 42, "y": "hello", "z": [1, 2]}
        save_slots(conn, slots)
        assert load_slots(conn) == slots
    finally:
        conn.close()


def test_save_slots_overwrites_existing_name(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_slots(conn, {"x": 1})
        save_slots(conn, {"x": 2})
        assert load_slots(conn) == {"x": 2}
    finally:
        conn.close()


def test_save_slots_drops_missing_names(tmp_path):
    conn = open_db(tmp_path / "x.db")
    try:
        save_slots(conn, {"x": 1, "y": 2})
        save_slots(conn, {"x": 1})
        assert load_slots(conn) == {"x": 1}
    finally:
        conn.close()


def test_storage_persists_across_connections(tmp_path):
    db = tmp_path / "x.db"
    conn = open_db(db)
    save_stack(conn, [1, "a", 2])
    save_slots(conn, {"x": 99})
    conn.close()

    conn = open_db(db)
    try:
        assert load_stack(conn) == [1, "a", 2]
        assert load_slots(conn) == {"x": 99}
    finally:
        conn.close()


def test_storage_round_trips_numpy_array(tmp_path):
    # pickle handles ndarrays; the engine pushes them, so the DB
    # must accept them.
    conn = open_db(tmp_path / "x.db")
    try:
        arr = np.array([1.0, 2.0, 3.0])
        save_stack(conn, [arr])
        out = load_stack(conn)
        assert len(out) == 1
        assert np.array_equal(out[0], arr)
    finally:
        conn.close()
