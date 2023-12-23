from pystack import RpnStack


def test_create_empty_stack():
    RpnStack()


def test_create_stack_from_list():
    s = RpnStack((1, 2, 4))
    assert len(s) == 3
    assert s.size() == 3
    assert s.top() == 4


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
    assert s.msg == "Syntax Error: 'abc"
    assert len(s) == 0


def test_pop():
    s = RpnStack((1, 2, 3))
    assert s.pop() == 3
    assert len(s) == 2
    assert s.top() == 2


def test_exec_parses_as_far_as_it_can():
    s = RpnStack()
    s.exec("1 'abc")
    assert list(s) == [1]


def test_exec_parses_unknown_op():
    s = RpnStack()
    s.exec("1 abc")
    assert list(s) == [1]
    assert s.msg == "Operation not found: abc"


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
