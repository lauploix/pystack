import pytest

from pystack import RpnStack, StackException

# --- string parsing (strings must be quoted) -----------------------------


def test_single_quoted_string_literal_parses():
    s = RpnStack()
    s.exec("'hello'")
    assert list(s) == ["hello"]


def test_double_quoted_string_literal_parses():
    s = RpnStack()
    s.exec('"hello"')
    assert list(s) == ["hello"]


def test_single_quoted_string_with_spaces_parses():
    # When the user types `pst "'a b'"`, the shell strips the outer
    # double quotes; argv carries the token "'a b'", which is a
    # valid Python string literal and should parse to "a b".
    s = RpnStack()
    s.exec("'a b'")
    assert list(s) == ["a b"]


def test_unquoted_unknown_token_errors():
    # `pst A` with A not being a command: strings must be quoted,
    # so this is an error rather than a bareword push.
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec("A")


# --- str / int / float conversions ---------------------------------------


def test_str_of_int():
    s = RpnStack()
    s.exec(tokens="42 str".split())
    assert list(s) == ["42"]


def test_str_of_float():
    s = RpnStack()
    s.exec(tokens="1.5 str".split())
    assert list(s) == ["1.5"]


def test_int_of_string():
    s = RpnStack()
    s.exec(tokens="'7' int".split())
    assert list(s) == [7]


def test_int_of_float():
    s = RpnStack()
    s.exec(tokens="3.7 int".split())
    assert list(s) == [3]


def test_float_of_string():
    s = RpnStack()
    s.exec(tokens="'2.5' float".split())
    assert list(s) == [2.5]


def test_float_of_int():
    s = RpnStack()
    s.exec(tokens="7 float".split())
    assert list(s) == [7.0]


def test_int_of_bad_string_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="'abc' int".split())


# --- the explicit-coercion idiom -----------------------------------------


def test_quoted_str_then_int_str_plus_concatenates():
    # User idiom: `pst "'A'" 1 str +` -> "A1". Strings are quoted;
    # `str` explicitly coerces the int for concatenation.
    s = RpnStack()
    s.exec(tokens=["'A'", "1", "str", "+"])
    assert list(s) == ["A1"]


def test_plus_string_and_int_raises():
    # Strict-Python `+`: mixed types error out.
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens=["'A'", "1", "+"])


def test_b1a_compound_example():
    # User example: "a" "b" 1 str + swap + -> "b1a"
    # (Tokens shown here are the python-literal form that survives the
    # shell when the user invokes `pst "'a'" "'b'" 1 str + swap +`.)
    s = RpnStack()
    s.exec(tokens=["'a'", "'b'", "1", "str", "+", "swap", "+"])
    assert list(s) == ["b1a"]


# --- sto / rcl / purge ---------------------------------------------------


def test_sto_stores_and_clears_stack():
    s = RpnStack()
    s.exec(tokens="42 'x' sto".split())
    assert list(s) == []
    assert s.slots == {"x": 42}


def test_rcl_pushes_stored_value():
    s = RpnStack()
    s.exec(tokens="42 'x' sto 'x' rcl".split())
    assert list(s) == [42]


def test_sto_overwrites_existing_slot():
    s = RpnStack()
    s.exec(tokens="1 'x' sto 2 'x' sto".split())
    assert s.slots == {"x": 2}


def test_purge_removes_slot():
    s = RpnStack()
    s.exec(tokens="42 'x' sto 'x' purge".split())
    assert s.slots == {}


def test_rcl_missing_slot_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="'nope' rcl".split())


def test_purge_missing_slot_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="'nope' purge".split())


def test_sto_with_non_string_name_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="42 7 sto".split())


def test_slots_preserved_across_constructor():
    s = RpnStack(slots={"y": 99})
    s.exec(tokens="'y' rcl".split())
    assert list(s) == [99]


# --- imaginary unit constant ---------------------------------------------


def test_imaginary_unit_pushes_1j():
    s = RpnStack()
    s.exec("i")
    assert list(s) == [1j]


def test_imaginary_unit_squared_is_minus_one():
    s = RpnStack()
    s.exec(tokens="i i *".split())
    assert list(s) == [-1 + 0j]


# --- logarithms (numpy convention) ---------------------------------------


def test_log_is_natural_log():
    s = RpnStack()
    s.exec(tokens="e log".split())
    assert list(s) == [1.0]


def test_log10_of_10_is_1():
    s = RpnStack()
    s.exec(tokens="10 log10".split())
    assert list(s) == [1.0]


def test_log10_of_100_is_2():
    s = RpnStack()
    s.exec(tokens="100 log10".split())
    assert list(s) == [2.0]


# --- tolist --------------------------------------------------------------


def test_tolist_builds_list_from_top_n():
    s = RpnStack()
    s.exec(tokens=["'a'", "'b'", "2", "tolist"])
    assert list(s) == [["a", "b"]]


def test_tolist_preserves_stack_order():
    s = RpnStack()
    s.exec(tokens="1 2 3 3 tolist".split())
    assert list(s) == [[1, 2, 3]]


def test_tolist_leaves_lower_items_on_stack():
    s = RpnStack()
    s.exec(tokens="99 1 2 2 tolist".split())
    assert list(s) == [99, [1, 2]]


def test_tolist_zero_pushes_empty_list():
    s = RpnStack()
    s.exec(tokens="0 tolist".split())
    assert list(s) == [[]]


def test_tolist_not_enough_items_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="1 5 tolist".split())


# --- len -----------------------------------------------------------------


def test_len_of_list():
    s = RpnStack()
    s.exec(tokens="1 2 3 3 tolist len".split())
    assert list(s) == [3]


def test_len_of_string():
    s = RpnStack()
    s.exec(tokens=["'hello'", "len"])
    assert list(s) == [5]


def test_len_of_empty_list():
    s = RpnStack()
    s.exec(tokens="0 tolist len".split())
    assert list(s) == [0]


def test_len_of_tuple_literal():
    s = RpnStack()
    s.exec(tokens=["'(1, 2, 3, 4)'", "eval", "len"])
    assert list(s) == [4]


def test_len_of_int_raises():
    s = RpnStack(raises=True)
    with pytest.raises(StackException):
        s.exec(tokens="42 len".split())
