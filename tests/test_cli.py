import pytest

from pystack import cli
from pystack.storage import load_slots, load_stack, open_db


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "pst.db")


def run(db, *tokens, capsys):
    rc = cli.main(["--db", db, *tokens])
    captured = capsys.readouterr()
    return rc, captured.out, captured.err


def read_state(db):
    conn = open_db(db)
    try:
        return load_stack(conn), load_slots(conn)
    finally:
        conn.close()


# --- core arithmetic + display ------------------------------------------


def test_simple_addition_prints_result(db_path, capsys):
    rc, out, _ = run(db_path, "1", "2", "+", capsys=capsys)
    assert rc == 0
    assert out == "3\n"


def test_stack_persists_across_invocations(db_path, capsys):
    run(db_path, "1", "2", "+", capsys=capsys)
    rc, out, _ = run(db_path, "10", "+", capsys=capsys)
    assert rc == 0
    assert out == "13\n"


# --- the canonical example sequence from the spec -----------------------


def test_replay_example_sequence(db_path, capsys):
    # Step 1: `pst 1 2 +`        -> 3
    _, out, _ = run(db_path, "1", "2", "+", capsys=capsys)
    assert out == "3\n"

    # Step 2: `pst 1`            -> 3, 1
    _, out, _ = run(db_path, "1", capsys=capsys)
    assert out == "3\n1\n"

    # Step 3: `pst "'a'"`        -> 3, 1, "a"  (string must be quoted)
    _, out, _ = run(db_path, "'a'", capsys=capsys)
    assert out == '3\n1\n"a"\n'

    # Step 4: `pst swap`         -> 3, "a", 1
    _, out, _ = run(db_path, "swap", capsys=capsys)
    assert out == '3\n"a"\n1\n'

    # Step 5: `pst str +`        -> 3, "a1"
    _, out, _ = run(db_path, "str", "+", capsys=capsys)
    assert out == '3\n"a1"\n'


# --- unquoted strings now error ----------------------------------------


def test_unquoted_string_errors_and_rolls_back(db_path, capsys):
    # `pst A` with A not being a command: error, stack unchanged.
    run(db_path, "1", "2", capsys=capsys)
    rc, _, err = run(db_path, "A", capsys=capsys)
    assert rc == 1
    assert err
    stack, _ = read_state(db_path)
    assert stack == [1, 2]


# --- explicit coercion idiom -------------------------------------------


def test_explicit_str_coercion_for_plus(db_path, capsys):
    rc, out, _ = run(db_path, "'A'", "1", "str", "+", capsys=capsys)
    assert rc == 0
    assert out == '"A1"\n'


def test_mixed_plus_errors_and_rolls_back(db_path, capsys):
    run(db_path, "'a'", "1", capsys=capsys)
    rc, _, err = run(db_path, "+", capsys=capsys)
    assert rc == 1
    assert err
    # Atomic: stack unchanged after the failing invocation.
    stack, _ = read_state(db_path)
    assert stack == ["a", 1]


def test_b1a_compound_example(db_path, capsys):
    # Equivalent to typing `pst "'a'" "'b'" 1 str + swap +` in bash,
    # which leaves single-quoted python-string-literal tokens in argv.
    rc, out, _ = run(
        db_path,
        "'a'",
        "'b'",
        "1",
        "str",
        "+",
        "swap",
        "+",
        capsys=capsys,
    )
    assert rc == 0
    assert out == '"b1a"\n'


# --- slots --------------------------------------------------------------


def test_sto_persists_across_invocations(db_path, capsys):
    run(db_path, "42", "'x'", "sto", capsys=capsys)
    rc, out, _ = run(db_path, "'x'", "rcl", capsys=capsys)
    assert rc == 0
    assert out == "42\n"
    _, slots = read_state(db_path)
    assert slots == {"x": 42}


def test_purge_persists(db_path, capsys):
    run(db_path, "42", "'x'", "sto", capsys=capsys)
    run(db_path, "'x'", "purge", capsys=capsys)
    _, slots = read_state(db_path)
    assert slots == {}


# --- flags --------------------------------------------------------------


def test_reset_clears_stack_but_not_slots(db_path, capsys):
    run(db_path, "1", "2", "3", capsys=capsys)
    run(db_path, "9", "'k'", "sto", capsys=capsys)
    rc = cli.main(["--db", db_path, "--reset"])
    capsys.readouterr()
    assert rc == 0
    stack, slots = read_state(db_path)
    assert stack == []
    assert slots == {"k": 9}


def test_slots_flag_lists_slots(db_path, capsys):
    run(db_path, "1", "'a'", "sto", capsys=capsys)
    run(db_path, "2", "'b'", "sto", capsys=capsys)
    rc = cli.main(["--db", db_path, "--slots"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "a = 1" in captured.out
    assert "b = 2" in captured.out


# --- REPL ---------------------------------------------------------------


def test_repl_processes_lines_and_exits(db_path, capsys, monkeypatch):
    inputs = iter(["1 2 +", "swap", "exit"])

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    rc = cli.main(["--db", db_path])
    capsys.readouterr()
    assert rc == 0
    # `1 2 +` -> [3]; then `swap` errors on a 1-element stack and the
    # state rolls back. Final stack: [3].
    stack, _ = read_state(db_path)
    assert stack == [3]


def test_repl_atomic_rollback_per_line(db_path, capsys, monkeypatch):
    run(db_path, "'a'", "1", capsys=capsys)
    inputs = iter(["+", "exit"])
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(inputs),
    )
    cli.main(["--db", db_path])
    capsys.readouterr()
    stack, _ = read_state(db_path)
    assert stack == ["a", 1]


def test_repl_handles_eof(db_path, capsys, monkeypatch):
    def boom(prompt=""):
        raise EOFError

    monkeypatch.setattr("builtins.input", boom)
    rc = cli.main(["--db", db_path])
    capsys.readouterr()
    assert rc == 0
