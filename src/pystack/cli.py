import argparse
import sys
from collections import deque

from pystack.display import format_stack, format_value
from pystack.engine import UNDO_MAX, RpnStack, StackException
from pystack.storage import (
    load_slots,
    load_stack,
    load_undo,
    open_db,
    reset_stack,
    save_slots,
    save_stack,
    save_undo,
)


def build_parser():
    p = argparse.ArgumentParser(
        prog="pst",
        description="RPN calculator with persistent stack and slots.",
    )
    p.add_argument(
        "--db",
        default=None,
        help="SQLite DB path (default ~/.pystack/pystack.db)",
    )
    p.add_argument(
        "--reset",
        action="store_true",
        help="Clear the persisted stack and exit",
    )
    p.add_argument(
        "--slots",
        action="store_true",
        help="List memory slots and exit",
    )
    p.add_argument(
        "tokens",
        nargs="*",
        help="RPN tokens to execute (omit to enter interactive mode)",
    )
    return p


def _execute_atomic(stack_items, slots, undo, tokens):
    rpn = RpnStack(
        tokens=list(stack_items),
        raises=True,
        slots=dict(slots),
        undo=deque(undo, maxlen=UNDO_MAX),
    )
    rpn.exec(tokens=list(tokens))
    return list(rpn), rpn.slots, rpn.undo


def _print_stack(items):
    out = format_stack(items)
    if out:
        print(out)


def _run_once(conn, tokens):
    stack_items = load_stack(conn)
    slots = load_slots(conn)
    undo = load_undo(conn)
    try:
        new_stack, new_slots, new_undo = _execute_atomic(
            stack_items, slots, undo, tokens
        )
    except StackException as e:
        print(e.msg, file=sys.stderr)
        return 1
    save_stack(conn, new_stack)
    save_slots(conn, new_slots)
    save_undo(conn, new_undo)
    _print_stack(new_stack)
    return 0


def _run_repl(conn):
    stack_items = load_stack(conn)
    slots = load_slots(conn)
    undo = load_undo(conn)
    _print_stack(stack_items)
    while True:
        try:
            line = input("pst> ")
        except EOFError:
            print()
            break
        line = line.strip()
        if not line:
            _print_stack(stack_items)
            continue
        if line == "exit":
            break
        tokens = line.split()
        try:
            stack_items, slots, undo = _execute_atomic(
                stack_items, slots, undo, tokens
            )
        except StackException as e:
            print(e.msg, file=sys.stderr)
            continue
        save_stack(conn, stack_items)
        save_slots(conn, slots)
        save_undo(conn, undo)
        _print_stack(stack_items)
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    conn = open_db(args.db)
    try:
        if args.reset:
            reset_stack(conn)
            return 0
        if args.slots:
            slots = load_slots(conn)
            for name in sorted(slots):
                print(f"{name} = {format_value(slots[name])}")
            return 0
        if args.tokens:
            return _run_once(conn, args.tokens)
        return _run_repl(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
