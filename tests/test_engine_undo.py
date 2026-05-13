import pytest

from pystack import RpnStack, StackException


def test_undo_reverts_last_op():
    # `1 2 +` -> [3]; undo reverts the `+` -> [1, 2].
    s = RpnStack()
    s.exec(tokens="1 2 +".split())
    assert list(s) == [3]
    s.exec("undo")
    assert list(s) == [1, 2]


def test_undo_chains_per_token():
    # Three pushes -> three snapshots; three undos peel them off.
    s = RpnStack()
    s.exec(tokens="1 2 3".split())
    assert list(s) == [1, 2, 3]
    s.exec("undo")
    assert list(s) == [1, 2]
    s.exec("undo")
    assert list(s) == [1]
    s.exec("undo")
    assert list(s) == []


def test_undo_doesnt_record_itself():
    # After `1 2`, the undo deque has snapshots [[], [1]].
    # First undo pops snapshot [1] -> stack = [1]. The undo op
    # must NOT push a snapshot for itself; otherwise the next
    # undo would return [1] again instead of [].
    s = RpnStack()
    s.exec(tokens="1 2".split())
    s.exec("undo")
    assert list(s) == [1]
    s.exec("undo")
    assert list(s) == []


def test_undo_on_empty_undo_stack_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec("undo")


def test_undo_capped_at_undo_max_snapshots():
    # UNDO_MAX + 1 non-undo ops produce UNDO_MAX + 1 snapshots,
    # but the deque drops the oldest. The pre-push-of-`0` snapshot
    # is gone, so we can only undo back to stack=[0].
    from pystack.engine import UNDO_MAX

    s = RpnStack()
    for i in range(UNDO_MAX + 1):
        s.exec(str(i))
    assert len(s.undo) == UNDO_MAX
    for _ in range(UNDO_MAX):
        s.exec("undo")
    assert list(s) == [0]


def test_undo_after_failed_op_returns_to_pre_op_state():
    # `+` on a 1-element stack fails (IndexError) but the snapshot
    # was already taken; undo restores [1].
    s = RpnStack()
    s.exec("1")
    s.exec("+")  # error, stack unchanged
    s.exec("undo")
    assert list(s) == [1]


def test_new_op_after_undo_records_a_fresh_snapshot():
    # No redo support — once undone, the snapshot is gone.
    # A new op records a fresh snapshot from the restored state.
    s = RpnStack()
    s.exec(tokens="1 2 +".split())  # -> [3]
    s.exec("undo")  # -> [1, 2]
    s.exec("*")  # -> [2], snapshot of [1, 2] saved
    assert list(s) == [2]
    s.exec("undo")  # -> [1, 2]
    assert list(s) == [1, 2]
