import numpy as np
import pytest

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


def test_operation_size_on_empty_stack(stack):
    stack.exec("size")
    # Now contains one element: the size as computed
    assert len(stack) == 1
    # the top element of the stack is 0 (it's size, when evaluated)
    assert stack.top() == 0


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
    s.exec(tokens="1 'abc'".split())
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
    assert s.msg == "Syntax Error: 1 'abc"


def test_exec_parses_unknown_op():
    s = RpnStack()
    s.exec(tokens="1 abc".split())
    assert list(s) == [1]
    assert s.msg == "Operation not found: abc"


# Test + on ints
def test_plus_int():
    s = RpnStack()
    s.exec(tokens="'a' 1 2 +".split())
    assert list(s) == ["a", 3]


# Test + on strings
def test_plus_str():
    s = RpnStack()
    s.exec(tokens="'a' 'b' 'c' +".split())
    assert list(s) == ["a", "bc"]


# Test -
def test_minus_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 7 -".split())
    assert list(s) == ["a", -2]


# Test / on ints
def test_div_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 /".split())
    assert list(s) == ["a", 2.5]


# Test / on ints
def test_divdiv_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 //".split())
    assert list(s) == ["a", 2]


# Test / on ints
def test_percent_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 %".split())
    assert list(s) == ["a", 1]


# Test * on ints
def test_mult_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 *".split())
    assert list(s) == ["a", 10]


# Test ** on ints
def test_power_on_ints():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 **".split())
    assert list(s) == ["a", 25]


# test swap
def test_swap():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 swap".split())
    assert list(s) == ["a", 2, 5]


# test drop
def test_drop():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 drop".split())
    assert list(s) == ["a", 5]


# test drop2
def test_drop2():
    s = RpnStack()
    s.exec(tokens="'a' 5 2 1 drop2".split())
    assert list(s) == ["a", 5]


# test drpn
def test_drpn():
    s = RpnStack()
    s.exec(tokens="'a' 1 2 3 2 drpn".split())
    assert list(s) == ["a", 1]


# test dup
def test_dup():
    s = RpnStack()
    s.exec(tokens="'a' 1 dup".split())
    assert list(s) == ["a", 1, 1]


# test pick
def test_pick():
    s = RpnStack()
    s.exec(tokens="'a' 'b' 1 pick".split())
    assert list(s) == ["a", "b", "b"]
    s.exec(tokens="3 pick".split())
    assert list(s) == ["a", "b", "b", "a"]


# test over
def test_over():
    s = RpnStack()
    s.exec(tokens="'a' 'b' 1 over".split())
    assert list(s) == ["a", "b", 1, "b"]


# test rot
def test_rot():
    s = RpnStack()
    s.exec(tokens="1 2 3 rot".split())
    assert list(s) == [2, 3, 1]


# test roll as ROT
def test_roll_3_is_rot(stack):
    stack.exec(tokens="'a' 'b' 'c' 3 roll".split())
    assert list(stack) == ["b", "c", "a"]


# test roll
def test_roll_n(stack):
    stack.exec(tokens="'a' 'b' 'c' 'd' 'e' 'f' 4 roll".split())
    assert list(stack) == ["a", "b", "d", "e", "f", "c"]


# test roll as ROT
def test_rolld_3_is_not_rot(stack):
    stack.exec(tokens="'a' 'b' 'c' 3 rolld".split())
    assert list(stack) == ["c", "a", "b"]


# test dup2
def test_dup2(stack):
    stack.exec(tokens="'a' 1 2 dup2".split())
    assert list(stack) == ["a", 1, 2, 1, 2]


# test dupn
def test_dupn(stack):
    stack.exec(tokens="'a' 1 2 3 4 5 3 dupn".split())
    assert list(stack) == ["a", 1, 2, 3, 4, 5, 3, 4, 5]


def test_create_object_class(stack):
    stack.exec("'object'")
    stack.exec("eval")
    assert list(stack) == [object]


def test_create_object_instance(stack):
    stack.exec("'object'")
    stack.exec("eval")
    stack.exec("()")
    assert list(stack) == [object, tuple()]
    stack.exec("call")
    assert len(stack) == 1
    assert list(stack)[0].__class__ == object


def test_create_instance_with_params(stack):
    stack.exec("'list'")
    stack.exec("eval")
    stack.exec("((1, 'b'), )")
    assert list(stack) == [list, ((1, "b"),)]
    stack.exec("call")
    assert list(stack) == [[1, "b"]]


def test_parse_complex_structure(stack):
    stack.exec("{'a':123}, (2, 3, (4, 5, [], {}))")
    output = stack.pop()
    assert output == (dict(a=123), (2, 3, (4, 5, [], {})))


def test_constants(stack):
    stack.exec("e")
    assert stack.pop() == np.e
    stack.exec("pi")
    assert stack.pop() == np.pi


def test_exp_single_value(stack):
    stack.exec("3")
    stack.exec("exp")
    assert stack.pop() == np.exp(3)


def test_exp_array_value(stack):
    stack.exec("(2, 1)")
    stack.exec("exp")
    output = stack.pop()
    assert list(output == np.exp([2, 1])) == [True, True]
    assert type(output) is np.ndarray


def test_exp_complex(stack):
    stack.exec("pi")
    stack.exec("1.5j")
    stack.exec("*")
    stack.exec("exp")
    assert np.isclose(stack.pop(), -1j)


def test_sin_on_float(stack):
    stack.exec("0")
    stack.exec("sin")
    assert stack.pop() == 0
    stack.exec("pi")
    stack.exec("2")
    stack.exec("/")
    stack.exec("sin")
    assert stack.pop() == 1


def test_sin_on_array(stack):
    stack.exec("[0, 0.5, 1, 1.5, 2]")
    stack.exec("pi")
    stack.exec("multiply")
    stack.exec("sin")
    # close enough with 4 digits
    output = stack.pop()
    assert all(np.round(output, 4) == [0, 1, 0, -1, 0])
    assert type(output) is np.ndarray


def test_atan_on_float(stack):
    # This test serves as template for all triginometric functions
    stack.exec("(0, 1, -3)")
    stack.exec("arctan")
    output = stack.pop()
    assert len(output) == 3
    assert all(output == np.arctan([0, 1, -3]))
    assert output[0] == 0
    assert type(output) is np.ndarray


def test_to_ndarray_ints(stack):
    stack.exec("[0, 2, -3]")
    stack.exec("array")
    output = stack.pop()
    assert output[0] == 0
    assert output[1] == 2
    assert output[2] == -3
    assert type(output) is np.ndarray
    assert type(output[2]) is np.int64


def test_to_ndarray_floats_after_mutl(stack):
    stack.exec("[0, 2, -3]")
    stack.exec("array")
    stack.exec("1.5")
    stack.exec("*")
    output = stack.pop()
    assert output[2] == -4.5
    assert type(output[2]) is np.float64
    assert type(output[0]) is np.float64


def test_to_ndarray_floats_from_values(stack):
    stack.exec("[0.0, 2.1, -3]")
    stack.exec("array")
    output = stack.pop()
    assert output[1]
    assert type(output[0]) is np.float64


@pytest.fixture
def stack():
    return RpnStack(raises=True)
