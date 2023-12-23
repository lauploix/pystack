from pystack import RpnStack


def test_create_empty_stack():
    RpnStack()


def test_create_stack_from_list():
    s = RpnStack((1, 2, 4))
    assert len(s) == 3
    assert s.size() == 3
    assert s.top() == 4


def test_clear():
    s = RpnStack((1, 2, 4, "clear"))
    s.exec()
    assert len(s) == 0


def test_depth():
    s = RpnStack((1, 2, 4, "depth"))
    s.exec()
    assert list(s) == [1, 2, 4, 3]


def test_iter():
    s = RpnStack((1, 2, 4))
    assert list(s) == [1, 2, 4]


def test_operation_size_on_empty_stack():
    s = RpnStack(())
    s.exec("size")
    # Now contains one element: the size as computed
    assert len(s) == 1
    # the top element of the stack is 0 (it's size, when evaluated)
    assert s.top() == 0


def test_operation_size_with_elements():
    s = RpnStack((1, "abc", object()))
    s.exec("size")
    # Now contains 4 elements: the size as computed
    assert len(s) == 4
    # the top element of the stack is 3, ie the size of the stack when computed
    assert s.top() == 3
    s._exec_size()
    assert len(s) == 5
    assert s.top() == 4


def test_exec_adds_strings_to_stack():
    s = RpnStack()
    s.exec("'abc'")
    assert len(s) == 1
    assert s.top() == "abc"


def test_exec_adds_multiple_values_on_stack():
    s = RpnStack()
    s.exec("1 'abc'")
    assert len(s) == 2
    assert list(s) == [1, "abc"]


def test_exec_gets_exception_with_unclosed_str():
    s = RpnStack()
    s.exec("'abc")
    assert len(s) == 0


def test_pop():
    s = RpnStack((1, 2, 3))
    assert s.pop() == 3
    assert len(s) == 2
    assert s.top() == 2


def test_exec_parses_as_far_as_it_can():
    s = RpnStack()
    s.exec("1 'abc")
    assert list(s) == []
    assert s.msg == "Unclosed string"


def test_exec_parses_unknown_op():
    s = RpnStack()
    s.exec("1 abc")
    assert list(s) == [1]
    assert s.msg == "Operation not found: abc"


def test_scan_with_strings_and_space():
    s = RpnStack()
    s.exec("'a b' \"c d\"")
    assert list(s) == ["a b", "c d"]


# Test + on ints
def test_plus_int():
    s = RpnStack()
    s.exec("'a' 1 2 +")
    assert list(s) == ["a", 3]


# Test + on strings
def test_plus_str():
    s = RpnStack()
    s.exec("'a' 'b' 'c' +")
    assert list(s) == ["a", "bc"]


# Test -
def test_minus_on_ints():
    s = RpnStack()
    s.exec("'a' 5 7 -")
    assert list(s) == ["a", -2]


# Test / on ints
def test_div_on_ints():
    s = RpnStack()
    s.exec("'a' 5 2 /")
    assert list(s) == ["a", 2.5]


# Test / on ints
def test_divdiv_on_ints():
    s = RpnStack()
    s.exec("'a' 5 2 //")
    assert list(s) == ["a", 2]


# Test / on ints
def test_percent_on_ints():
    s = RpnStack()
    s.exec("'a' 5 2 %")
    assert list(s) == ["a", 1]


# Test * on ints
def test_mult_on_ints():
    s = RpnStack()
    s.exec("'a' 5 2 *")
    assert list(s) == ["a", 10]


# Test ** on ints
def test_power_on_ints():
    s = RpnStack()
    s.exec("'a' 5 2 **")
    assert list(s) == ["a", 25]


# test swap
def test_swap():
    s = RpnStack()
    s.exec("'a' 5 2 swap")
    assert list(s) == ["a", 2, 5]


# test drop
def test_drop():
    s = RpnStack()
    s.exec("'a' 5 2 drop")
    assert list(s) == ["a", 5]


# test drop2
def test_drop2():
    s = RpnStack()
    s.exec("'a' 5 2 1 drop2")
    assert list(s) == ["a", 5]


# test drpn
def test_drpn():
    s = RpnStack()
    s.exec("'a' 1 2 3 2 drpn")
    assert list(s) == ["a", 1]


# test dup
def test_dup():
    s = RpnStack()
    s.exec("'a' 1 dup")
    assert list(s) == ["a", 1, 1]


# test pick
def test_pick():
    s = RpnStack()
    s.exec("'a' 'b' 1 pick")
    assert list(s) == ["a", "b", "b"]
    s.exec("3 pick")
    assert list(s) == ["a", "b", "b", "a"]


# test over
def test_over():
    s = RpnStack()
    s.exec("'a' 'b' 1 over")
    assert list(s) == ["a", "b", 1, "b"]


# test rot
def test_rot():
    s = RpnStack()
    s.exec("1 2 3 rot")
    assert list(s) == [2, 3, 1]


# test roll as ROT
def test_roll_3_is_rot():
    s = RpnStack()
    s.exec("'a' 'b' 'c' 3 roll")
    assert list(s) == ["b", "c", "a"]


# test roll
def test_roll_n():
    s = RpnStack()
    s.exec("'a' 'b' 'c' 'd' 'e' 'f' 4 roll")
    assert list(s) == ["a", "b", "d", "e", "f", "c"]


# test roll as ROT
def test_rolld_3_is_not_rot():
    s = RpnStack()
    s.exec("'a' 'b' 'c' 3 rolld")
    assert list(s) == ["c", "a", "b"]


# test dup2
def test_dup2():
    s = RpnStack()
    s.exec("'a' 1 2 dup2")
    assert list(s) == ["a", 1, 2, 1, 2]


# test dupn
def test_dupn():
    s = RpnStack()
    s.exec("'a' 1 2 3 4 5 3 dupn")
    assert list(s) == ["a", 1, 2, 3, 4, 5, 3, 4, 5]
